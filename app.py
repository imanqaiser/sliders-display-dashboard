import os
from datetime import datetime
from flask import Flask, render_template, jsonify
from bson import ObjectId
from db import get_db

app = Flask(__name__)

NASA_TLX_FIELDS = ["mental", "temporal", "performance", "effort", "frustration"]
SUS_FIELDS = [f"sus{i}" for i in range(1, 11)]


def clean(doc):
    """
    Mongo documents contain ObjectId and datetime objects that don't
    serialize the way the frontend expects by default. This walks a doc
    (or list of docs) and:
      - converts ObjectId -> str
      - drops the internal _id field (not used by the frontend)
      - converts datetime -> ISO 8601 string, matching the format the
        old static JSON files used (e.g. "2026-06-15T15:03:34.703+00:00")
    """
    if isinstance(doc, list):
        return [clean(d) for d in doc]
    if isinstance(doc, dict):
        out = {}
        for k, v in doc.items():
            if k == "_id":
                continue
            if isinstance(v, ObjectId):
                out[k] = str(v)
            elif isinstance(v, datetime):
                out[k] = v.isoformat()
            elif isinstance(v, (dict, list)):
                out[k] = clean(v)
            else:
                out[k] = v
        return out
    return doc


def is_complete_survey(survey):
    """
    A survey counts as fully completed if every NASA-TLX subscale and
    every SUS item has a non-null, non-empty answer.
    """
    if not survey:
        return False
    workload = survey.get("workload") or {}
    usability = survey.get("usability") or {}

    for field in NASA_TLX_FIELDS:
        val = workload.get(field)
        if val is None or val == "":
            return False
    for field in SUS_FIELDS:
        val = usability.get(field)
        if val is None or val == "":
            return False
    return True


def get_real_session_ids(db):
    """
    A session counts as a real participant (not a test/dev session) if:
      1. session.user_type == "pilot"
      2. there's a matching survey for that session_id, fully completed
         (all NASA-TLX + SUS fields answered)
    Returns a set of qualifying session_ids.
    """
    pilot_session_ids = {
        s["session_id"]
        for s in db.sessions.find({"user_type": "pilot"}, {"session_id": 1})
    }
    if not pilot_session_ids:
        return set()

    surveys = db.surveys.find({"session_id": {"$in": list(pilot_session_ids)}})
    real_ids = {s["session_id"] for s in surveys if is_complete_survey(s)}
    return real_ids


@app.route("/")
def index():
    return render_template("index.html")


# -- Raw collection dumps -----------------------------------------------
# These mirror the old static/data/*.json files. The frontend's
# buildData() function in index.html does all the joining client-side,
# so we keep that logic untouched and just swap the data source.
#
# All four collections below are filtered down to real participants only:
# user_type == "pilot" AND a fully-completed survey exists for that session.


@app.route("/api/raw/sessions")
def raw_sessions():
    db = get_db()
    real_ids = get_real_session_ids(db)
    docs = list(db.sessions.find({"session_id": {"$in": list(real_ids)}}))
    return jsonify(clean(docs))


@app.route("/api/raw/tasks")
def raw_tasks():
    db = get_db()
    real_ids = get_real_session_ids(db)
    docs = list(db.tasks.find({"session_id": {"$in": list(real_ids)}}))
    return jsonify(clean(docs))


@app.route("/api/raw/searches")
def raw_searches():
    db = get_db()
    real_ids = get_real_session_ids(db)
    task_ids = {
        t["task_id"]
        for t in db.tasks.find({"session_id": {"$in": list(real_ids)}}, {"task_id": 1})
    }
    docs = list(db.searches.find({"task_id": {"$in": list(task_ids)}}))
    return jsonify(clean(docs))


@app.route("/api/raw/clicks")
def raw_clicks():
    db = get_db()
    real_ids = get_real_session_ids(db)
    task_ids = {
        t["task_id"]
        for t in db.tasks.find({"session_id": {"$in": list(real_ids)}}, {"task_id": 1})
    }
    search_ids = {
        s["search_id"]
        for s in db.searches.find(
            {"task_id": {"$in": list(task_ids)}}, {"search_id": 1}
        )
    }
    docs = list(db.clicks.find({"search_id": {"$in": list(search_ids)}}))
    return jsonify(clean(docs))


@app.route("/api/raw/surveys")
def raw_surveys():
    db = get_db()
    real_ids = get_real_session_ids(db)
    docs = list(db.surveys.find({"session_id": {"$in": list(real_ids)}}))
    return jsonify(clean(docs))


# -- Survey lookup by session --------------------------------------------
# Convenience endpoint: one survey response per session_id (per the data
# seen so far, sessions and surveys appear to be 1:1 via session_id).


@app.route("/api/survey/<session_id>")
def survey_for_session(session_id):
    db = get_db()
    doc = db.surveys.find_one({"session_id": session_id})
    if doc is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(clean(doc))


if __name__ == "__main__":
    print("Starting Sliders Dashboard at http://localhost:5000")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

import json
import os
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path) as f:
        return json.load(f)


def parse_date(val):
    if isinstance(val, dict) and "$date" in val:
        val = val["$date"]
    if val is None:
        return None
    if val.endswith("Z"):
        val = val[:-1] + "+00:00"
    return datetime.fromisoformat(val)


def build_session_data():
    sessions = load_json("sessions.json")
    tasks = load_json("tasks.json")
    searches = load_json("searches.json")
    clicks = load_json("clicks.json")

    # Index searches by task_id
    searches_by_task = {}
    for s in searches:
        tid = s["task_id"]
        searches_by_task.setdefault(tid, []).append(s)

    # Index clicks by search_id
    clicks_by_search = {}
    for c in clicks:
        sid = c["search_id"]
        clicks_by_search.setdefault(sid, []).append(c)

    result = []
    for session in sessions:
        session_id = session["session_id"]
        session_start = parse_date(session["start_time"])
        session_end = parse_date(session["end_time"])
        session_dur = round((session_end - session_start).total_seconds())

        session_tasks = [t for t in tasks if t["session_id"] == session_id]
        session_tasks.sort(key=lambda t: t["task_idx"])

        enriched_tasks = []
        for task in session_tasks:
            task_id = task["task_id"]
            task_start = parse_date(task["start_time"])
            task_end = parse_date(task["end_time"])
            task_dur = round((task_end - task_start).total_seconds())

            task_searches = searches_by_task.get(task_id, [])
            task_searches.sort(key=lambda s: parse_date(s["timestamp"]))

            enriched_searches = []
            for search in task_searches:
                search_id = search["search_id"]
                search_clicks = clicks_by_search.get(search_id, [])
                target_clicked = any(c["is_target"] for c in search_clicks)
                non_target_clicks = [c for c in search_clicks if not c["is_target"]]

                sliders = []
                names = search.get("slider_names", [])
                values = search.get("slider_values", [])
                for i, name in enumerate(names):
                    val = values[i] if i < len(values) else 0.0
                    sliders.append({"name": name, "value": round(val, 3)})

                enriched_searches.append(
                    {
                        "search_id": search_id,
                        "timestamp": search["timestamp"]["$date"]
                        if isinstance(search["timestamp"], dict)
                        else search["timestamp"],
                        "query_text": search.get("query_text", ""),
                        "sliders": sliders,
                        "has_sliders": len(values) > 0,
                        "target_rank": search.get("target_rank"),
                        "target_rank_status": search.get("target_rank_status"),
                        "target_clicked": target_clicked,
                        "non_target_click_count": len(non_target_clicks),
                        "result_count": len(search.get("results", [])),
                    }
                )

            # Rank trajectory across searches
            rank_trajectory = [
                s["target_rank"]
                for s in enriched_searches
                if s["target_rank"] is not None
            ]

            enriched_tasks.append(
                {
                    "task_id": task_id,
                    "task_idx": task["task_idx"],
                    "target_path": task["target_path"],
                    "status": task["status"],
                    "start_time": task["start_time"]["$date"]
                    if isinstance(task["start_time"], dict)
                    else task["start_time"],
                    "end_time": task["end_time"]["$date"]
                    if isinstance(task["end_time"], dict)
                    else task["end_time"],
                    "duration_sec": task_dur,
                    "searches": enriched_searches,
                    "search_count": len(enriched_searches),
                    "rank_trajectory": rank_trajectory,
                    "final_rank": rank_trajectory[-1] if rank_trajectory else None,
                    "best_rank": min(rank_trajectory) if rank_trajectory else None,
                }
            )

        result.append(
            {
                "session_id": session_id,
                "dataset": session.get("dataset", ""),
                # Pilot config fields (Pranavi's schema)
                "vocab": session.get("vocab", session.get("dataset", "")),
                "numTasks": session.get("tasks"),
                "numConcepts": session.get("concepts"),
                "setup": session.get("setup", ""),
                "start_time": session["start_time"]["$date"]
                if isinstance(session["start_time"], dict)
                else session["start_time"],
                "end_time": session["end_time"]["$date"]
                if isinstance(session["end_time"], dict)
                else session["end_time"],
                "duration_sec": session_dur,
                "task_count": len(enriched_tasks),
                "tasks": enriched_tasks,
                "success_count": sum(
                    1 for t in enriched_tasks if t["status"] == "success"
                ),
                "skip_count": sum(1 for t in enriched_tasks if t["status"] == "skip"),
            }
        )

    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/sessions")
def api_sessions():
    data = build_session_data()
    # Strip searches from summary to keep it light
    summary = []
    for s in data:
        s_copy = dict(s)
        s_copy["tasks"] = [
            {k: v for k, v in t.items() if k != "searches"} for t in s["tasks"]
        ]
        summary.append(s_copy)
    return jsonify(summary)


@app.route("/api/session/<session_id>")
def api_session(session_id):
    data = build_session_data()
    for s in data:
        if s["session_id"] == session_id:
            return jsonify(s)
    return jsonify({"error": "not found"}), 404


@app.route("/api/task/<task_id>")
def api_task(task_id):
    data = build_session_data()
    for session in data:
        for task in session["tasks"]:
            if task["task_id"] == task_id:
                return jsonify(task)
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    print("Starting Sliders Dashboard at http://localhost:5000")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

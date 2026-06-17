"""
MongoDB connection setup.

Reads connection info from a .env file (never hardcode credentials in app.py).
Exposes `get_db()` which returns the event-logs database, with collections
matching the old JSON filenames: sessions, tasks, searches, clicks, surveys.
"""
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()  # reads .env in the same directory

MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB = os.environ.get("MONGODB_DB", "event-logs")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI not set. Create a .env file with MONGODB_URI=mongodb+srv://..."
    )

_client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
_db = _client[MONGODB_DB]


def get_db():
    """Returns the event-logs database handle."""
    return _db


def check_connection():
    """Quick ping check, useful for debugging connection issues."""
    _client.admin.command("ping")
    return True

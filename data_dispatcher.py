"""
Streams synthetic event data to Firestore to simulate a real-time data feed.

This script reads events from `synthetic_data.json` and pushes them one by one
to a Firestore collection, pausing between each dispatch to mimic a live stream.
"""

import asyncio
import json
import firebase_admin
from firebase_admin import credentials, firestore
from validate_data import is_event_valid

# --- Firebase Initialization ---
KEY_PATH = "credentials/agent-one-465916-c61b8803d4b8.json"
try:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("DISPATCHER: Connected to Firestore.")
except Exception as e:
    print(f"DISPATCHER: Error connecting to Firestore: {e}")
    exit()
# -----------------------------


async def stream_data():
    """Reads events and streams them to the 'live_urban_events' collection."""
    try:
        with open("synthetic_data.json", "r") as f:
            events = json.load(f)
    except FileNotFoundError:
        print("DISPATCHER ERROR: synthetic_data.json not found. Run data_simulator.py first.")
        return

    print("\n--- STARTING DATA DISPATCHER ---")
    for event in events:
        if is_event_valid(event):
            try:
                doc_ref = db.collection("live_urban_events").document(event["eventId"])
                doc_ref.set(event)
                severity = event.get("severity", "N/A")
                print(
                    f"Dispatched Event: {event['eventId']} ({event['dataType']}) | Severity: {severity}"
                )
            except Exception as e:
                print(f"DISPATCHER ERROR: Failed to write to Firestore: {e}")
        else:
            print(f"Skipped Invalid Event: {event.get('eventId', 'Unknown ID')}")

        await asyncio.sleep(5)

    print("--- DATA DISPATCHER FINISHED ---")


if __name__ == "__main__":
    asyncio.run(stream_data())

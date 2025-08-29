"""
The main entry point for the agentic engine.

This script connects to Firestore, listens for new events in the
'live_urban_events' collection, and triggers the agent's cognitive loop
(perceive, reason, plan) when a significant new event is detected.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import requests
import time
import threading
import json

from model import perceive, reason, plan, adapt, REASONING_EXAMPLES, PLANNING_EXAMPLES
from validate_data import is_event_valid

# --- Firebase Initialization ---
KEY_PATH = "credentials/agent-one-465916-c61b8803d4b8.json"
try:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("MAIN: Connected to Firestore.")
except Exception as e:
    print(f"MAIN: Error connecting to Firestore: {e}")
    exit()
# -----------------------------

# --- Global State ---
current_plan = {}
stop_event = threading.Event()
# --------------------


def send_plan_to_protocol(plan_json: str, source_event: dict):
    """
    Sends the generated plan and its source event to the Flask API.

    Args:
        plan_json (str): The raw JSON string output from the LLM.
        source_event (dict): The event that triggered the plan generation.
    """
    protocol_url = "http://127.0.0.1:5000/recommend"
    try:
        cleaned_plan_str = plan_json.strip().replace("```json", "").replace("```", "")
        plan_dict = json.loads(cleaned_plan_str)

        payload = {"plan": plan_dict, "source_event": source_event}

        response = requests.post(protocol_url, json=payload)
        if response.status_code == 200:
            print("MAIN: Successfully sent new plan to protocol layer.")
        else:
            print(
                f"MAIN: Error sending plan. Status: {response.status_code}, Body: {response.text}"
            )
    except Exception as e:
        print(f"MAIN: Failed to send plan to protocol layer. Error: {e}")


def on_event_snapshot(doc_snapshot, changes, read_time):
    """
    A callback function that triggers whenever data changes in Firestore.

    This is the core of the real-time listener. It validates new events
    and runs the full agentic loop if necessary.
    """
    global current_plan
    for change in changes:
        if change.type.name in ["ADDED", "MODIFIED"]:
            event_data = change.document.to_dict()
            print(f"\nMAIN: New event received from Firestore: {event_data['eventId']}")

            if not is_event_valid(event_data):
                print("MAIN: Received invalid event, skipping.")
                continue

            needs_new_plan = adapt(json.dumps(current_plan), event_data)

            if not current_plan or needs_new_plan:
                print("MAIN: Change detected. Running agentic loop...")
                perceived_info = perceive(event_data)
                diagnosis = reason(perceived_info, REASONING_EXAMPLES)
                new_plan_raw_output = plan(diagnosis, PLANNING_EXAMPLES)

                # --- LLM Safeguard: Validate JSON output before proceeding ---
                try:
                    cleaned_plan_str = (
                        new_plan_raw_output.strip()
                        .replace("```json", "")
                        .replace("```", "")
                    )
                    plan_dict = json.loads(cleaned_plan_str)
                    current_plan = plan_dict
                    send_plan_to_protocol(new_plan_raw_output, event_data)

                except json.JSONDecodeError:
                    print("LLM SAFEGUARD: AI output was not valid JSON. Skipping this plan.")
                    print(f"--- AI Raw Output ---\n{new_plan_raw_output}\n--------------------")
            else:
                print("MAIN: Event received, but current plan is still sufficient.")


def main():
    """Sets up the Firestore listener and keeps the script running."""
    print("MAIN: Setting up Firestore listener...")
    event_collection_ref = db.collection("live_urban_events")
    query_watch = event_collection_ref.on_snapshot(on_event_snapshot)

    print("MAIN: System is live. Listening for events from the data dispatcher.")
    print("To stop, press Ctrl+C")

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMAIN: Shutting down...")
        stop_event.set()
        query_watch.unsubscribe()


if __name__ == "__main__":
    main()

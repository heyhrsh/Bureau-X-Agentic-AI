"""
A simple test script to verify the protocol layer's `/recommend` endpoint.

This sends a mock plan to the Flask server to ensure it is running and
can correctly receive data.
"""

import requests
import json

# A sample plan payload, mimicking the output of the agentic engine.
mock_payload = {
    "plan": {
        "plan_title": "TEST: Handle Mock Power Outage",
        "priority": "HIGH",
        "steps": [
            {"action_id": 1, "action": "Dispatch Crew", "details": "Send test crew to location A."},
            {"action_id": 2, "action": "Public Alert", "details": "Issue test alert on social media."},
        ],
    },
    "source_event": {
        "eventId": "test_event_001",
        "dataType": "power_outage",
        "severity": "HIGH",
    },
}

url = "http://127.0.0.1:5000/recommend"

try:
    response = requests.post(url, json=mock_payload)
    response.raise_for_status()  # Raise an exception for HTTP errors
    print("SUCCESS: Test plan sent successfully to the protocol layer.")
    print("Response from server:", response.json())
except requests.exceptions.RequestException as e:
    print(f"ERROR: Could not connect to the protocol layer: {e}")

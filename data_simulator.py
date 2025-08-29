"""
Generates a scripted, narrative-driven crisis scenario for simulation.

This script creates a `synthetic_data.json` file containing a sequence of
interrelated events, including anomalies, to test the agent's response
capabilities in a realistic, escalating situation.
"""

import json
import random
from datetime import datetime, timezone

from data_schema import SCHEMA_TEMPLATE
from locations import BENGALURU_LOCATIONS


def generate_event(data_type="traffic"):
    """
    Generates a single, randomized event based on the schema template.

    Args:
        data_type (str, optional): The type of event to create, e.g., "traffic".
                                   Defaults to "traffic".

    Returns:
        dict: A dictionary representing a single urban event.
    """
    event = SCHEMA_TEMPLATE.copy()
    now = datetime.now(timezone.utc)

    event["eventId"] = f"{data_type[:4]}_{now.strftime('%Y%m%d%H%M%S%f')}"
    event["dataType"] = data_type
    event["timestamp"] = now.isoformat()

    real_location = random.choice(BENGALURU_LOCATIONS)
    event["location"] = {
        "zone": real_location["name"],
        "coordinates": {"lat": real_location["lat"], "lon": real_location["lon"]},
        "granularity": "intersection",
    }
    event["metadata"] = {
        "confidence": round(random.uniform(0.85, 0.99), 2),
        "data_source": "synthetic_sensor",
    }

    if data_type == "traffic":
        congestion = round(random.uniform(0.2, 1.0), 2)
        event["data"] = {
            "congestion_level": congestion,
            "average_speed_kph": int(60 * (1 - congestion)),
        }
        if congestion > 0.9:
            event["severity"] = "HIGH"
        elif congestion > 0.7:
            event["severity"] = "MEDIUM"
        else:
            event["severity"] = "LOW"

    elif data_type == "weather":
        temp = round(random.uniform(22.0, 35.0), 1)
        event["data"] = {
            "temp_celsius": temp,
            "humidity_percent": random.randint(60, 95),
        }
        event["severity"] = "MEDIUM" if temp > 32 else "LOW"
        event["location"]["granularity"] = "city-wide"

    return event


if __name__ == "__main__":
    print("Generating a scripted 10-minute flood and traffic scenario...")
    all_events = []

    # --- Scenario Narrative ---
    rain_event = generate_event("weather")
    rain_event["data"]["description"] = "light rain"
    rain_event["severity"] = "LOW"
    all_events.append(rain_event)

    heavy_rain_event = generate_event("weather")
    heavy_rain_event["data"]["description"] = "heavy continuous rain"
    heavy_rain_event["severity"] = "MEDIUM"
    heavy_rain_event["interdependencies"].append(
        {"eventId": rain_event["eventId"], "relationship": "escalation_of"}
    )
    all_events.append(heavy_rain_event)

    flood_event = generate_event("water_quality")
    flood_event["dataType"] = "water_quality"
    flood_event["data"]["description"] = "severe waterlogging reported"
    flood_event["severity"] = "HIGH"
    flood_event["interdependencies"].append(
        {"eventId": heavy_rain_event["eventId"], "relationship": "caused_by"}
    )
    all_events.append(flood_event)

    for i in range(7):
        traffic_event = generate_event("traffic")
        traffic_event["data"]["congestion_level"] = round(0.8 + (i * 0.02), 2)
        traffic_event["severity"] = (
            "HIGH" if traffic_event["data"]["congestion_level"] > 0.9 else "MEDIUM"
        )
        traffic_event["interdependencies"].append(
            {"eventId": flood_event["eventId"], "relationship": "affected_by"}
        )
        all_events.append(traffic_event)

    # --- Inject Anomalies for Robustness Testing ---
    print("\nIntroducing anomalies (edge cases)...")
    if len(all_events) > 3:
        del all_events[3]["severity"]
        print("Anomaly 1: Removed 'severity' from the 4th event.")

    if len(all_events) > 6:
        all_events[6]["dataType"] = "unknown_disaster"
        print("Anomaly 2: Set an invalid 'dataType' on the 7th event.")

    with open("synthetic_data.json", "w") as f:
        json.dump(all_events, f, indent=2)

    print(
        f"\nSUCCESS: Generated scripted scenario with {len(all_events)} events."
    )
    print("Saved to synthetic_data.json")

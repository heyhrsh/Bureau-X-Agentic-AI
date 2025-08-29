"""
Defines the standard data structure (schema) for any event in the system.

This module acts as a single source of truth for event formats, ensuring
consistency across data simulation, validation, and processing.
"""

SCHEMA_TEMPLATE = {
    "eventId": "",
    "dataType": "",
    "timestamp": "",
    "validity_period_minutes": 15,
    "location": {
        "zone": "",
        "coordinates": {"lat": 0.0, "lon": 0.0},
        "granularity": "",
    },
    "data": {},
    "severity": "LOW",
    "metadata": {
        "confidence": 1.0,
        "data_source": "",
    },
    "interdependencies": [],
}

# --- Validation Constants ---

VALID_SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

VALID_DATA_TYPES = [
    "traffic",
    "public_transit_bus",
    "public_transit_metro",
    "ambulance_dispatch",
    "weather",
    "air_quality_index",
    "stock_market",
    "commodity_market",
    "water_quality",
    "fire_emergency",
    "power_outage",
    "public_event",
    "crime_report",
]

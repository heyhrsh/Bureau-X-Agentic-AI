"""
Provides a function to validate incoming urban event data against the defined schema.

This ensures data integrity before it is processed by the agentic engine.
"""

from data_schema import VALID_DATA_TYPES, VALID_SEVERITY_LEVELS


def is_event_valid(event: dict) -> bool:
    """
    Performs basic validation on a single event dictionary.

    Checks for the presence of required fields and validates the values for
    'dataType' and 'severity' against predefined lists.

    Args:
        event (dict): The event data dictionary to validate.

    Returns:
        bool: True if the event is valid, False otherwise.
    """
    required_fields = [
        "eventId",
        "dataType",
        "timestamp",
        "location",
        "data",
        "severity",
    ]
    for field in required_fields:
        if field not in event:
            print(
                f"VALIDATION FAILED: Missing required field '{field}' in event {event.get('eventId')}"
            )
            return False

    if event["dataType"] not in VALID_DATA_TYPES:
        print(
            f"VALIDATION FAILED: Invalid dataType '{event['dataType']}' in event {event.get('eventId')}"
        )
        return False

    if event["severity"] not in VALID_SEVERITY_LEVELS:
        print(
            f"VALIDATION FAILED: Invalid severity '{event['severity']}' in event {event.get('eventId')}"
        )
        return False

    return True

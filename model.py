"""
Defines the core agentic functions and initializes the connection to Vertex AI.

This module contains the agent's cognitive capabilities:
- perceive: Formats raw data for the LLM.
- reason: Analyzes data to diagnose the root cause of a crisis.
- plan: Generates a multi-step action plan based on the diagnosis.
- adapt: Decides if a new event requires a change to the current plan.
"""

import vertexai
import json
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

# --- Vertex AI Initialization ---
KEY_PATH = "credentials/agent-one-465916-c61b8803d4b8.json"
PROJECT_ID = "agent-one-465916"
LOCATION = "asia-south1"

try:
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
    gemini_pro_model = GenerativeModel("gemini-1.5-pro")
    print("MODEL: Connected to Vertex AI (Gemini 1.5 Pro).")
except Exception as e:
    print(f"MODEL: Error connecting to Vertex AI: {e}")
    exit()
# -----------------------------

CRISIS_KEYWORDS = {
    "traffic": ["traffic", "congestion", "jam", "accident"],
    "weather": ["weather", "rain", "storm", "heatwave", "flood"],
    "power": ["power", "outage", "electricity", "blackout"],
    "fire": ["fire", "smoke"],
    "medical": ["ambulance", "medical", "emergency"],
    "water": ["water", "quality", "supply", "leakage", "water_quality", "flood"],
    "air_quality": ["air", "quality", "aqi", "pollution", "smog"],
}

# ==============================================================================
# 1. AGENT COGNITIVE FUNCTIONS
# ==============================================================================


def perceive(raw_data: dict) -> str:
    """
    Takes a raw data dictionary and formats it into a string for the LLM.

    Args:
        raw_data (dict): The event data.

    Returns:
        str: A formatted string describing the current situation.
    """
    print("AGENT-PERCEIVE: Reading data...")
    return f"Current situation: {str(raw_data)}"


def reason(perceived_data: str, examples: list) -> str:
    """
    Analyzes the situation using Gemini to find the root cause and severity.

    Args:
        perceived_data (str): Formatted string from the perceive function.
        examples (list): A list of few-shot examples for the prompt.

    Returns:
        str: The LLM's diagnosis of the crisis.
    """
    print("AGENT-REASON: Analyzing root cause...")
    prompt = f"""
    You are an Urban Crisis Diagnosis AI. Based on the following data, what is the primary crisis and its severity (1-10)?
    Follow these examples:
    {examples}
    ---
    Data:
    {perceived_data}
    Diagnosis:
    """
    response = gemini_pro_model.generate_content(prompt)
    return response.text


def plan(diagnosis: str, examples: list) -> str:
    """
    Creates a multi-step action plan in JSON format based on the diagnosis.

    Args:
        diagnosis (str): The crisis diagnosis from the reason function.
        examples (list): A list of few-shot examples for the prompt.

    Returns:
        str: A raw string from the LLM, intended to be a valid JSON object.
    """
    print("AGENT-PLAN: Creating a step-by-step plan...")
    prompt = f"""
    You are an Urban Operations Planner AI. Based on the crisis diagnosis, create a clear, actionable, multi-step plan in JSON format.
    Follow these examples:
    {examples}
    ---
    Diagnosis:
    {diagnosis}
    Action Plan (JSON):
    """
    response = gemini_pro_model.generate_content(prompt)
    return response.text


def adapt(current_plan_json: str, new_event: dict) -> bool:
    """
    Decides if the current plan is sufficient to handle a new event.

    Compares the semantic category of the new event (e.g., 'traffic') with the
    category of the existing plan. An adaptation is needed if the categories
    do not match or if no plan currently exists.

    Args:
        current_plan_json (str): A JSON string of the current action plan.
        new_event (dict): The newly received event data.

    Returns:
        bool: True if a new plan is needed, False otherwise.
    """
    print("AGENT-ADAPT: Checking if plan needs to change...")
    try:
        cleaned_plan_str = (
            current_plan_json.strip().replace("```json", "").replace("```", "")
        )
        if not cleaned_plan_str or cleaned_plan_str == "{}":
            print("ADAPTATION NEEDED: No current plan exists.")
            return True

        plan_details = json.loads(cleaned_plan_str)
        plan_title = plan_details.get("plan_title", "").lower()
        new_crisis_type = new_event.get("dataType", "").lower()

        new_crisis_group = next(
            (group for group, kw in CRISIS_KEYWORDS.items() if new_crisis_type in kw),
            None,
        )
        if not new_crisis_group:
            print(f"ADAPTATION NEEDED: Unrecognized new crisis type '{new_crisis_type}'.")
            return True

        old_plan_group = next(
            (
                group
                for group, keywords in CRISIS_KEYWORDS.items()
                if any(keyword in plan_title for keyword in keywords)
            ),
            None,
        )

        if new_crisis_group == old_plan_group:
            print(
                f"ADAPTATION NOT NEEDED: New '{new_crisis_group}' event is covered by the existing '{old_plan_group}' plan."
            )
            return False
        else:
            print(
                f"ADAPTATION NEEDED: New '{new_crisis_group}' event is not covered by the existing '{old_plan_group}' plan."
            )
            return True

    except Exception as e:
        print(f"Error in adapt function: {e}. Re-planning to be safe.")
        return True


# ==============================================================================
# 2. FEW-SHOT PROMPTING EXAMPLES
# ==============================================================================

REASONING_EXAMPLES = [
    {
        "input": "Current situation: {'type': 'traffic', 'location': 'Silk Board', 'value': '95% congestion', 'event': 'waterlogging'}",
        "output": "Crisis: Severe traffic jam at Silk Board due to waterlogging. Severity: 9/10.",
    },
    {
        "input": "Current situation: {'type': 'air_quality', 'location': 'Indiranagar', 'value': 'AQI 350', 'event': 'post_diwali'}",
        "output": "Crisis: Hazardous air quality in Indiranagar, likely from festival fireworks. Severity: 8/10.",
    },
]

PLANNING_EXAMPLES = [
    {
        "input": "Crisis: Severe traffic jam at Silk Board due to waterlogging. Severity: 9/10.",
        "output": """
        {
          "plan_title": "Mitigate Silk Board Waterlogging & Congestion",
          "priority": "High",
          "steps": [
            {"action_id": 1, "action": "Dispatch Emergency Crew", "details": "Send BBMP water pumps and traffic police to Silk Board junction immediately."},
            {"action_id": 2, "action": "Divert Traffic", "details": "Reroute traffic from Outer Ring Road towards BTM Layout and HSR Layout."},
            {"action_id": 3, "action": "Public Alert", "details": "Issue real-time traffic advisory on social media and FM radio channels."}
          ]
        }
        """,
    }
]

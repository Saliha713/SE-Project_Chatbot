from collections import defaultdict
import re

# In-memory storage for session memory
chat_memory = defaultdict(dict)

# Required details to book a flight
REQUIRED_DETAILS = ["departure_city", "destination_city", "travel_dates", "passengers"]

# Simple regex patterns to extract user-provided details
DETAIL_PATTERNS = {
    "departure_city": r"(?:from|departure|leaving)\s+([A-Za-z ]+)",
    "destination_city": r"(?:to|destination|going to)\s+([A-Za-z ]+)",
    "travel_dates": r"(?:on|for|depart(?:ure)?)\s+([A-Za-z0-9, /-]+)",
    "passengers": r"(?:for|number of|travelling with)\s+(\d+)"
}

def get_memory(session_id: str):
    """
    Retrieve memory for a session. Initialize if not present.
    """
    if session_id not in chat_memory:
        chat_memory[session_id] = {
            "stage": "ask_details",
            "provided_details": {},
            "history": []
        }
    return chat_memory[session_id]

def extract_details_from_text(text: str, memory: dict):
    """
    Try to extract any required details from user text.
    Updates memory['provided_details'] automatically.
    """
    for key, pattern in DETAIL_PATTERNS.items():
        if key not in memory["provided_details"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                memory["provided_details"][key] = match.group(1).strip()

def update_memory(session_id: str, user_text: str, bot_text: str, memory=None):
    """
    Update session memory with the new user and bot messages.
    Optionally pass memory dict (used internally to avoid re-fetching).
    """
    if memory is None:
        memory = get_memory(session_id)

    # Append conversation history
    memory.setdefault("history", []).append({"user": user_text, "bot": bot_text})

    # Extract details automatically from user's message
    extract_details_from_text(user_text, memory)

    # Check if all details are provided to move to next stage
    missing_details = [d for d in REQUIRED_DETAILS if d not in memory["provided_details"]]
    if not missing_details:
        memory["stage"] = "provide_instructions"

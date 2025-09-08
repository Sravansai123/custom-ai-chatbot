SYSTEM_PROMPT = """You are a friendly travel planning assistant. The user wants a concise JSON itinerary and 2-3 hotel suggestions.
Return EXACTLY a JSON object with keys: hotels (array), itinerary (array of days), rationale (short string), sources (array).
Do NOT include additional markdown or commentary outside the JSON."""

# A short few-shot or example can be appended to user prompt to help format; we will ask the LLM to produce JSON.
def build_user_prompt(slots: PlanRequest, hotels_preview: List[Dict[str, Any]], poi_count: int):
    user_text = {
        "destination": slots.destination,
        "dates": {"start": slots.start_date, "end": slots.end_date},
        "budget_per_night": slots.budget_per_night,
        "interests": slots.interests,
        "party": slots.party,
        "pace": slots.pace,
        "hotels_preview": hotels_preview,
        "poi_count": poi_count
    }
    return "User request (json):\n" + json.dumps(user_text, indent=2) + "\n\nPlease output the structured JSON described in the system prompt."

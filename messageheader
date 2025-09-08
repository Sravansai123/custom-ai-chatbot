async def llm_chat(messages: List[Dict[str, str]], model: str = DEFAULT_MODEL, max_tokens: int = 800) -> Dict[str, Any]:
    """
    Simple async wrapper for OpenAI Chat Completions.
    Replace implementation with your provider's API.
    """
    if OPENAI_API_KEY is None:
        raise RuntimeError("OPENAI_API_KEY is not set")

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(OPENAI_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    # OpenAI v1 chat completion returns choices[0].message.content
    content = data["choices"][0]["message"]["content"]
    return {"raw": data, "content": content}

# -------------------------
# Retrieval stubs (replace with actual DB queries)
# -------------------------
def search_hotels_stub(city: str, budget: Optional[int], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Replace with actual DB retrieval using pgvector / SQL.
    This returns sample hotels with price_bucket 1..3 (1 cheapest).
    """
    sample = [
        {"id": "h1", "name": f"{city} Budget Inn", "price_bucket": 1, "lat": 0.0, "lng": 0.0, "amenities": ["wifi", "breakfast"], "rating": 4.0},
        {"id": "h2", "name": f"{city} Central Hotel", "price_bucket": 2, "lat": 0.01, "lng": 0.01, "amenities": ["wifi", "gym"], "rating": 4.2},
        {"id": "h3", "name": f"{city} Riverside Suites", "price_bucket": 3, "lat": 0.02, "lng": 0.0, "amenities": ["pool", "spa"], "rating": 4.6},
    ]
    # naive budget filter
    if budget:
        # map budget to bucket (example)
        if budget < 50:
            allowed = [h for h in sample if h["price_bucket"] <= 1]
        elif budget < 150:
            allowed = [h for h in sample if h["price_bucket"] <= 2]
        else:
            allowed = sample
    else:
        allowed = sample
    return allowed[:top_k]

def search_pois_stub(city: str, interests: List[str], top_k: int = 20) -> List[Dict[str, Any]]:
    """
    Replace with actual POI retrieval from DB/pgvector/OSM.
    Returns list of attractions with typical durations and opening hours.
    """
    base = []
    now = datetime.utcnow()
    for i in range(1, 21):
        base.append({
            "id": f"poi{i}",
            "name": f"{city} Attraction {i}",
            "category": "sightseeing" if i % 3 else "museum",
            "lat": 0.01 * i, "lng": 0.01 * i,
            "rating": 4.0 + (i % 5) * 0.1,
            "estimated_minutes": 90 if i % 3 == 0 else 60,
            "open_hours": {"mon":"09:00-18:00"},  # simplified
        })
    # simple filtering by interest presence in category/name
    if interests:
        filtered = [p for p in base if any(interest.lower() in (p["category"] + " " + p["name"]).lower() for interest in interests)]
        return filtered[:top_k] if filtered else base[:top_k]
    return base[:top_k]

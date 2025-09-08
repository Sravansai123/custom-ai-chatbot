@app.post("/plan", response_model=PlanResponse)
async def plan_trip(req: PlanRequest):
    # validate dates quickly
    try:
        _ = datetime.fromisoformat(req.start_date)
        _ = datetime.fromisoformat(req.end_date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format; expected YYYY-MM-DD")

    # 1) retrieve hotels + POIs (replace stubs with DB calls)
    hotels = search_hotels_stub(req.destination, req.budget_per_night, top_k=3)
    pois = search_pois_stub(req.destination, req.interests, top_k=30)

    # 2) compose itinerary locally (quick offline plan)
    try:
        itinerary_days = compose_itinerary(pois, req.start_date, req.end_date, pace=req.pace)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3) ask LLM to produce user-facing rationale + check format (LLM will produce JSON)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(req, hotels, len(pois))}
    ]

    # call LLM
    try:
        llm_out = await llm_chat(messages, max_tokens=800)
        llm_content = llm_out["content"]
    except Exception as e:
        # fallback: produce response using composer defaults
        llm_content = None

    # attempt to parse LLM JSON, otherwise fallback to our local format
    if llm_content:
        # extract first JSON object in response
        try:
            # naive JSON find: find first '{' and last '}' - robust enough for many model replies
            start = llm_content.find('{')
            end = llm_content.rfind('}')
            json_str = llm_content[start:end+1]
            parsed = json.loads(json_str)
            # validate keys exist
            hotels_out = parsed.get("hotels")
            itinerary_out = parsed.get("itinerary")
            rationale = parsed.get("rationale", "")
            sources = parsed.get("sources", [])
            if hotels_out and itinerary_out:
                # normalize to our Pydantic models (minimal)
                hotels_final = [HotelSuggestion(**h) for h in hotels_out]
                itinerary_final = []
                for d in itinerary_out:
                    blocks = [ItineraryBlock(**b) for b in d.get("blocks", [])]
                    itinerary_final.append(ItineraryDay(date=d.get("date"), blocks=blocks))
                return PlanResponse(hotels=hotels_final, itinerary=itinerary_final, rationale=rationale, sources=sources)
        except Exception:
            # parse error -> fallback below
            llm_content = None

    # Fallback deterministic response (if LLM failed or didn't return JSON)
    hotels_final = []
    for h in hotels:
        hs = HotelSuggestion(
            id=h["id"],
            name=h["name"],
            price_bucket=h["price_bucket"],
            pros=[f"{h.get('rating',4.0)}★ rating", "central location" if h["price_bucket"] <= 2 else "premium amenities"],
            cons=["smaller rooms" if h["price_bucket"] == 1 else "higher price" if h["price_bucket"] == 3 else "none"],
            why=f"Matches budget bucket {h['price_bucket']} and has good rating."
        )
        hotels_final.append(hs)

    rationale_text = f"Generated {len(itinerary_days)} day itinerary from {req.start_date} to {req.end_date} for {req.destination}. Hotels chosen by price fit and rating."
    sources = [{"type": "dataset", "name": "internal_stub", "last_updated": str(datetime.utcnow().date())}]

    return PlanResponse(hotels=hotels_final, itinerary=itinerary_days, rationale=rationale_text, sources=sources)
  
# Simple root
@app.get("/")
def root():
    return {"status": "ok", "info": "Travel Planner LLM backend - POST /plan to create a plan"}

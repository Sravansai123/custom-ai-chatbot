def compose_itinerary(pois: List[Dict[str, Any]], start_date: str, end_date: str, pace: str = "moderate") -> List[ItineraryDay]:
    """
    Greedy composer:
    - divides days
    - assigns 3-5 blocks per day depending on pace
    """
    sd = datetime.fromisoformat(start_date).date()
    ed = datetime.fromisoformat(end_date).date()
    days = (ed - sd).days + 1
    if days <= 0:
        raise ValueError("end_date must be >= start_date")
    # decide blocks per day by pace
    if pace == "slow":
        blocks_per_day = 2
    elif pace == "fast":
        blocks_per_day = 5
    else:
        blocks_per_day = 3

    result: List[ItineraryDay] = []
    poi_idx = 0
    for d in range(days):
        day_date = sd + timedelta(days=d)
        blocks = []
        # simple time windows: morning, afternoon, evening
        times = ["09:00-11:00", "12:00-15:00", "16:00-19:00", "20:00-21:30", "22:00-23:00"]
        assigned = 0
        while assigned < blocks_per_day and poi_idx < len(pois):
            p = pois[poi_idx]
            block = ItineraryBlock(time=times[assigned], place_id=p["id"], name=p["name"], note=f"Est. {p.get('estimated_minutes',60)} mins")
            blocks.append(block)
            assigned += 1
            poi_idx += 1
        # if we run out, wrap around
        if not blocks:
            blocks = [ItineraryBlock(time="09:00-11:00", place_id="none", name="Free time", note=None)]
        result.append(ItineraryDay(date=str(day_date), blocks=blocks))
    return result

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import httpx

# -------------------------
# Config / Environment
# -------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # or set PROVIDER_API_KEY
DEFAULT_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")  # swap as desired

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Travel Planner AI (minimal LLM backend)")

# -------------------------
# Pydantic request/response
# -------------------------
class PlanRequest(BaseModel):
    user_id: Optional[str] = None
    destination: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    budget_per_night: Optional[int] = None
    interests: Optional[List[str]] = Field(default_factory=list)
    party: Optional[Dict[str, Any]] = Field(default_factory=dict)  # e.g. {"adults":2,"kids":1}
    pace: Optional[str] = Field(default="moderate")  # slow/moderate/fast

class HotelSuggestion(BaseModel):
    id: str
    name: str
    price_bucket: int
    pros: List[str]
    cons: List[str]
    why: Optional[str]

class ItineraryBlock(BaseModel):
    time: str
    place_id: str
    name: str
    note: Optional[str] = None

class ItineraryDay(BaseModel):
    date: str
    blocks: List[ItineraryBlock]

class PlanResponse(BaseModel):
    hotels: List[HotelSuggestion]
    itinerary: List[ItineraryDay]
    rationale: str
    sources: List[Dict[str, Any]]

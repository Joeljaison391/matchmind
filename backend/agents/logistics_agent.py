import json
import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

ITINERARY_PROMPT = """You are a match day logistics planner for the 2026 FIFA World Cup.

Match details:
- Teams: {home_team} vs {away_team}
- Kickoff local time: {kickoff_local}
- Venue: {venue_name}, {city}
- Transport options: {transport}

Fan's starting location: {origin}

Create a practical match day itinerary with 4-6 steps covering:
departure from origin, arrival at venue area, pre-match activities, entry, and return.

Respond with valid JSON only:
{{"steps": [{{"time": "HH:MM", "activity": "...", "location": "...", "transport_mode": "...", "notes": null}}]}}"""


def get_transport_options(db, venue_id):
    venue = db.venues.find_one({"venue_id": venue_id})
    if not venue:
        return []
    return venue.get("transport_options", [])


def build_itinerary_step(time, activity, location, transport_mode, notes=None):
    return {
        "time": time,
        "activity": activity,
        "location": location,
        "transport_mode": transport_mode,
        "notes": notes,
    }


def plan_itinerary(db, match, origin):
    transport = get_transport_options(db, match["venue_id"])
    transport_str = ", ".join(
        t.get("description", t.get("mode", "")) for t in transport
    ) or "check official FIFA transport guide"

    venue = db.venues.find_one({"venue_id": match["venue_id"]}) or {}

    prompt = ITINERARY_PROMPT.format(
        home_team=match["home_team"],
        away_team=match["away_team"],
        kickoff_local=match.get("kickoff_local", "TBD"),
        venue_name=venue.get("stadium_name", match["venue_id"]),
        city=match.get("city", ""),
        transport=transport_str,
        origin=origin,
    )

    response = gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)

import json
import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

INTENTS = {"MATCH_LOOKUP", "ITINERARY", "LOCAL_DISCOVER", "TEAM_INFO", "GENERAL_FAQ", "MEMORY_READ"}

PROMPT = """You are a routing agent for a FIFA World Cup 2026 fan assistant.

Classify the user message into exactly one intent:
- MATCH_LOOKUP: match schedules, kickoff times, which teams play when/where
- ITINERARY: trip plans, daily schedules, what to do on match day
- LOCAL_DISCOVER: restaurants, food, bars, halal/vegan options, fan zones near a stadium
- TEAM_INFO: a specific team's group, players, history, stats
- GENERAL_FAQ: general World Cup questions — format, rules, tickets, travel tips, broadcasting
- MEMORY_READ: the fan's own saved preferences or past queries

Extract:
- language: detected language code (en, es, fr, ar, pt, de, ja, hi, ml, ko, etc.)
- teams: team names mentioned (empty list if none)
- city: city mentioned (null if none)
- date: date mentioned (null if none)
- dietary_flags: dietary restrictions mentioned (halal, vegan, vegetarian, kosher, gluten_free)

Respond with valid JSON only:
{{
  "language": "en",
  "intent": "MATCH_LOOKUP",
  "entities": {{
    "teams": [],
    "city": null,
    "date": null,
    "dietary_flags": []
  }}
}}

User message: {message}"""


def classify(message: str) -> dict:
    response = gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=PROMPT.format(message=message),
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)

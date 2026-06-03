"""
ADK agent definitions for MatchMind.
Wraps existing agent functions as FunctionTools and exposes LlmAgent instances
that the orchestrator uses via the ADK Runner.
"""
import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool

load_dotenv()

_gemini = Gemini(model="gemini-2.5-flash")


# ── Match Intelligence Agent ───────────────────────────────────────────────

def _describe_match_tools(db):
    def find_matches_tool(team: str = "", venue_id: str = "", round_type: str = "") -> dict:
        """Find World Cup matches. Filter by team name, venue_id, or round_type."""
        from agents.match_agent import find_matches, get_venue, build_match_card
        matches = find_matches(
            db,
            team=team or None,
            venue_id=venue_id or None,
            round_type=round_type or None,
            limit=5,
        )
        cards = []
        for m in matches:
            venue = get_venue(db, m["venue_id"]) if m.get("venue_id") else None
            cards.append(build_match_card(m, venue))
        return {"matches": cards, "count": len(cards)}

    def get_team_info_tool(team_name: str) -> dict:
        """Get FIFA team info by name or FIFA code (e.g. BRA, ARG)."""
        from agents.match_agent import get_team
        doc = get_team(db, team_name)
        return doc or {"error": f"No info found for {team_name}"}

    return [FunctionTool(find_matches_tool), FunctionTool(get_team_info_tool)]


def make_match_agent(db) -> LlmAgent:
    return LlmAgent(
        name="match_agent",
        model=_gemini,
        tools=_describe_match_tools(db),
        instruction=(
            "You are the Match Intelligence Agent for the 2026 FIFA World Cup. "
            "Use find_matches_tool to look up fixtures and get_team_info_tool for team data. "
            "Always return structured match details including kickoff time and venue."
        ),
    )


# ── Discovery Agent ────────────────────────────────────────────────────────

def _describe_discovery_tools(db, embed_fn):
    def search_faqs_tool(query: str) -> dict:
        """Search World Cup FAQ knowledge base using the user's question."""
        from agents.discovery_agent import vector_search_faqs, build_faq_answer
        embedding = embed_fn(query)
        results = vector_search_faqs(db, embedding, limit=3)
        faq = build_faq_answer(results)
        return faq or {"answer": "No FAQ found for that query."}

    def search_businesses_tool(query: str, venue_id: str, dietary: str = "") -> dict:
        """Find restaurants, bars, cafes near a World Cup venue. dietary can be 'halal', 'vegan', or empty."""
        from agents.discovery_agent import hybrid_search_businesses
        embedding = embed_fn(query)
        flags = [f.strip() for f in dietary.split(",") if f.strip()] if dietary else []
        results = hybrid_search_businesses(db, embedding, venue_id, flags, limit=8)
        return {"businesses": results, "count": len(results)}

    return [FunctionTool(search_faqs_tool), FunctionTool(search_businesses_tool)]


def make_discovery_agent(db, embed_fn) -> LlmAgent:
    return LlmAgent(
        name="discovery_agent",
        model=_gemini,
        tools=_describe_discovery_tools(db, embed_fn),
        instruction=(
            "You are the Discovery Agent for the 2026 FIFA World Cup. "
            "Use search_faqs_tool for general World Cup questions. "
            "Use search_businesses_tool to find food and drink near stadiums — "
            "always pass the venue_id and any dietary requirements."
        ),
    )


# ── Logistics Agent ────────────────────────────────────────────────────────

def _describe_logistics_tools(db):
    def plan_itinerary_tool(team: str, origin: str) -> dict:
        """Plan a match day itinerary. Finds the next match for the team and plans from origin."""
        from agents.match_agent import find_matches
        from agents.logistics_agent import plan_itinerary
        matches = find_matches(db, team=team, limit=1)
        if not matches:
            return {"error": f"No upcoming match found for {team}"}
        return plan_itinerary(db, matches[0], origin)

    return [FunctionTool(plan_itinerary_tool)]


def make_logistics_agent(db) -> LlmAgent:
    return LlmAgent(
        name="logistics_agent",
        model=_gemini,
        tools=_describe_logistics_tools(db),
        instruction=(
            "You are the Logistics Agent for the 2026 FIFA World Cup. "
            "Use plan_itinerary_tool to build a step-by-step match day plan. "
            "Include transport options, timing, and practical tips."
        ),
    )

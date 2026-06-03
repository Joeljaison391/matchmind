import asyncio
import hashlib
import time
import os

from google import genai
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.genai.types import Content, Part
from dotenv import load_dotenv

from agents.router import classify
from agents.match_agent import find_matches, get_venue, get_team, build_match_card
from agents.discovery_agent import vector_search_faqs, hybrid_search_businesses, build_faq_answer
from agents.logistics_agent import plan_itinerary
from agents.memory_agent import get_fan_profile, build_personalisation_context, append_query
from agents.adk_agents import make_match_agent, make_discovery_agent, make_logistics_agent
from api.evaluator import score_response, passes_threshold

load_dotenv()

gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _embed(text):
    result = gemini.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768),
    )
    return list(result.embeddings[0].values)


def _fan_id(session_id):
    return hashlib.sha256(session_id.encode()).hexdigest()[:16]


def _trace_step(agent, tool, query, t_start, score=None):
    return {
        "agent": agent,
        "tool": tool,
        "query": query,
        "duration_ms": int((time.time() - t_start) * 1000),
        "score": score,
    }


def _run_adk_agent(agent: LlmAgent, message: str, session_id: str) -> str:
    """Run an ADK LlmAgent synchronously and return the final text response."""
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="matchmind",
        session_service=session_service,
    )

    async def _run():
        session = await session_service.create_session(
            app_name="matchmind",
            user_id=session_id,
        )
        user_content = Content(role="user", parts=[Part(text=message)])
        final_text = ""
        async for event in runner.run_async(
            user_id=session_id,
            session_id=session.id,
            new_message=user_content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = event.content.parts[0].text or ""
        return final_text

    return asyncio.run(_run())


def handle(db, message, session_id, language_hint=None):
    t0 = time.time()
    steps = []
    agents_fired = []

    fan_id = _fan_id(session_id)

    # load fan profile
    t = time.time()
    profile = get_fan_profile(db, fan_id)
    ctx = build_personalisation_context(profile)
    steps.append(_trace_step("memory_agent", "get_fan_profile", fan_id, t))
    agents_fired.append("memory_agent")

    # classify intent
    t = time.time()
    classification = classify(message)
    intent = classification.get("intent", "GENERAL_FAQ")
    entities = classification.get("entities", {})
    steps.append(_trace_step("router", "classify", message, t))
    agents_fired.append("router")

    response_type = "faq_answer"
    response_data = {}
    response_text = ""

    if intent == "MATCH_LOOKUP":
        t = time.time()
        adk_agent = make_match_agent(db)
        teams = entities.get("teams", [])
        team = teams[0] if teams else ""
        adk_reply = _run_adk_agent(adk_agent, message, session_id)
        # also pull structured data for the card UI
        matches = find_matches(db, team=team or None, limit=5)
        cards = []
        for m in matches:
            venue = get_venue(db, m["venue_id"]) if m.get("venue_id") else None
            cards.append(build_match_card(m, venue))
        response_type = "match_card"
        response_data = {"matches": cards}
        response_text = adk_reply or f"Found {len(cards)} match(es){f' for {team}' if team else ''}."
        steps.append(_trace_step("match_agent", "adk:find_matches", team, t))
        agents_fired.append("match_agent")

    elif intent == "TEAM_INFO":
        t = time.time()
        adk_agent = make_match_agent(db)
        adk_reply = _run_adk_agent(adk_agent, message, session_id)
        teams = entities.get("teams", [])
        team_name = teams[0] if teams else ""
        team_doc = get_team(db, team_name) if team_name else None
        response_type = "team_info"
        response_data = team_doc or {}
        response_text = adk_reply or (f"Here's info on {team_name}." if team_doc else f"No data for {team_name}.")
        steps.append(_trace_step("match_agent", "adk:get_team", team_name, t))
        agents_fired.append("match_agent")

    elif intent == "LOCAL_DISCOVER":
        t = time.time()
        adk_agent = make_discovery_agent(db, _embed)
        city = entities.get("city") or ""
        venue_doc = (
            db.venues.find_one({"city": {"$regex": city, "$options": "i"}}, {"venue_id": 1})
            if city else None
        )
        venue_id = venue_doc["venue_id"] if venue_doc else "metlife_stadium"
        adk_reply = _run_adk_agent(adk_agent, message, session_id)
        # also pull structured data for cards
        embedding = _embed(message)
        businesses = hybrid_search_businesses(db, embedding, venue_id, ctx.get("dietary_flags"), limit=8)
        response_type = "business_list"
        response_data = {"businesses": businesses}
        response_text = adk_reply or f"Found {len(businesses)} place(s) near the venue."
        steps.append(_trace_step("discovery_agent", "adk:hybrid_search", message, t))
        agents_fired.append("discovery_agent")

    elif intent == "ITINERARY":
        t = time.time()
        adk_agent = make_logistics_agent(db)
        adk_reply = _run_adk_agent(adk_agent, message, session_id)
        # also pull structured itinerary data
        teams = entities.get("teams", [])
        team = teams[0] if teams else None
        matches = find_matches(db, team=team, limit=1)
        if matches:
            origin = entities.get("city") or "your hotel"
            itinerary = plan_itinerary(db, matches[0], origin)
            response_type = "itinerary"
            response_data = itinerary
            n = len(itinerary.get("steps", []))
            response_text = adk_reply or f"Here's your match day plan — {n} steps."
        else:
            response_text = adk_reply or "Couldn't find a fixture to plan around."
        steps.append(_trace_step("logistics_agent", "adk:plan_itinerary", message, t))
        agents_fired.append("logistics_agent")

    else:  # GENERAL_FAQ, MEMORY_READ, unknown
        t = time.time()
        adk_agent = make_discovery_agent(db, _embed)
        adk_reply = _run_adk_agent(adk_agent, message, session_id)
        embedding = _embed(message)
        faqs = vector_search_faqs(db, embedding, limit=3)
        faq = build_faq_answer(faqs)
        response_type = "faq_answer"
        response_data = faq or {}
        response_text = adk_reply or (faq["answer"] if faq else "I don't have specific info on that.")
        steps.append(_trace_step("discovery_agent", "adk:search_faqs", message, t))
        agents_fired.append("discovery_agent")

    # eval loop — max 2 attempts
    eval_scores = None
    retry_marker = "PASS"
    for attempt in range(2):
        eval_scores = score_response(message, response_text)
        steps[-1]["score"] = eval_scores["avg"]
        if passes_threshold(eval_scores):
            retry_marker = "PASS"
            break
        retry_marker = "RETRY"
        if intent in ("GENERAL_FAQ", "MEMORY_READ", None):
            embedding = _embed(message)
            faqs = vector_search_faqs(db, embedding, limit=5)
            faq = build_faq_answer(faqs)
            if faq:
                response_data = faq
                response_text = faq["answer"]

    append_query(db, fan_id, message)

    return {
        "response": {
            "type": response_type,
            "data": response_data,
            "text": response_text,
        },
        "trace": {
            "agents_fired": agents_fired,
            "total_ms": int((time.time() - t0) * 1000),
            "steps": steps,
            "eval": eval_scores,
            "retry_marker": retry_marker,
        },
        "session_id": session_id,
    }

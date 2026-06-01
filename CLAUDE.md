# MatchMind — Claude Code Context

## Project at a Glance

MatchMind is an autonomous multi-agent AI concierge for the 2026 FIFA World Cup.  
**Hackathon:** Google Cloud Rapid Agent Hackathon 2026, MongoDB Partner Track  
**Deadline:** June 11, 2026 (same day the World Cup kicks off)  
**Prize:** $5,000 (1st place, MongoDB track)

The one-sentence pitch: _Tell MatchMind you're going to the World Cup and it plans your entire experience — matches, food, transport, local secrets — in any language, in under five seconds._

---

## Tech Stack (must know)

| Layer | Technology | Notes |
|---|---|---|
| LLM | Gemini 3.5 Flash | Vertex AI. Handles 12+ languages natively. |
| Orchestration | Google Cloud Agent Builder | Multi-agent routing. Python ADK. |
| Database | MongoDB Atlas M0 | Free cluster. GCP us-east-1. All reads/writes via MongoDB MCP Server. |
| Vector search | Atlas Vector Search | Cosine, 768 dims. Gemini text-embedding-004. |
| Hybrid search | Atlas Hybrid Search | BM25 + vector on `local_businesses`. |
| Knowledge graph | MongoDB GraphRAG GA | `fan_graph` collection. LangChain integration. |
| MCP bridge | MongoDB MCP Server | Winter 2026 edition. ALL Atlas operations go through this. |
| Observability | Arize Phoenix (free cloud) | `openinference-instrumentation-mcp` + `openinference-instrumentation-google-adk`. |
| Evaluation | Arize LLM-as-judge | Gemini evaluator. Threshold 0.75. Auto-retry on fail. |
| API | FastAPI | 3 endpoints: `/api/chat`, `/api/health`, `/api/memory/{session_id}` |
| Backend hosting | Cloud Run | Free tier. Scales to zero. |
| Frontend | Next.js 14 | App Router. Vercel hobby tier. |

---

## Repository Layout

```
matchmind/
├── backend/
│   ├── agents/          # One file per agent
│   │   ├── router.py           # Router Agent — intent classification + entity extraction
│   │   ├── match_agent.py      # Match Intelligence Agent — schedule + venue + team data
│   │   ├── discovery_agent.py  # Discovery Agent — businesses + FAQs
│   │   ├── logistics_agent.py  # Logistics Agent — itinerary + transport + web search
│   │   └── memory_agent.py     # Memory Agent — fan_graph GraphRAG read/write
│   ├── api/
│   │   ├── main.py             # FastAPI app entrypoint
│   │   ├── routes/             # chat.py, health.py, memory.py
│   │   └── schemas.py          # Pydantic models for request/response
│   ├── data/
│   │   ├── seed/               # JSON seed files for matches, venues, FAQs, businesses
│   │   └── indexes.py          # Atlas index creation scripts
│   ├── scripts/
│   │   ├── data_loader.py      # Loads match + venue + FAQ seed data into Atlas
│   │   ├── embed_data.py       # Generates Gemini embeddings and upserts into Atlas
│   │   └── warm_up.py          # Pings Cloud Run health endpoint (used by GitHub Actions)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                    # Next.js App Router pages
│   ├── components/
│   │   ├── Chat/               # Chat input + message thread
│   │   ├── Cards/              # MatchCard, ItineraryTimeline, BusinessCard, FAQAnswer
│   │   └── TracePanel/         # Collapsible trace panel (agents fired, queries, scores)
│   └── package.json
├── docs/
│   ├── features.md             # Full feature spec (Win/Wow/Core/Coupling tiers)
│   ├── branching.md            # Branching strategy
│   └── architecture.md        # Detailed system design notes
├── .github/
│   └── workflows/
│       └── warm_up.yml         # Pings Cloud Run every 10 min during judging period
├── .env.example
├── .gitignore
├── CLAUDE.md
├── CONTRIBUTING.md
└── README.md
```

---

## The 5 Agents

### Router Agent (`backend/agents/router.py`)
- **Input:** raw fan message (any language)
- **Output:** `{language, intent, entities: {teams, city, date, dietary_flags}}`
- **Tools:** none — pure classifier, no Atlas calls
- **Intent enum:** `MATCH_LOOKUP | ITINERARY | LOCAL_DISCOVER | TEAM_INFO | GENERAL_FAQ | MEMORY_READ`
- **Latency target:** < 300ms

### Match Intelligence Agent (`backend/agents/match_agent.py`)
- **Tools:** `find_matches()`, `get_venue()`, `get_team_stats()`, `graphTraverse()`
- **Collections:** `matches`, `venues`, `teams`
- **Output format:** `MatchCard {match_id, home_team, away_team, kickoff_utc, kickoff_local, venue_name, city, group, round, broadcast[]}`
- **Latency target:** < 500ms

### Discovery Agent (`backend/agents/discovery_agent.py`)
- **Tools:** `hybrid_search_businesses()`, `vector_search_faqs()`, `get_fan_zones()`
- **Collections:** `local_businesses` (hybrid BM25+vector), `faq_embeddings` (vector)
- **Personalisation:** reads `fan_graph.dietary_flags` before search and appends as filter
- **Output format:** `BusinessCard[] {name, category, cuisine, halal_flag, rating, price_range, distance_meters, address}`
- **Latency target:** < 800ms

### Logistics Agent (`backend/agents/logistics_agent.py`)
- **Tools:** `get_venue_transport()`, `plan_itinerary()`, `web_search()` (Gemini tool)
- **Collections:** `venues.transport_options[]`
- **Output format:** `Itinerary {steps: [{time, activity, location, transport_mode, notes}]}`
- **Latency target:** < 1200ms

### Memory Agent (`backend/agents/memory_agent.py`)
- **Tools:** `get_fan_preferences()`, `upsert_fan_graph()`, `get_session_history()`, `listClusterSuggestedIndexes()` (dev only)
- **Collections:** `fan_graph`
- **GraphRAG:** reads entity relationships → passes `PersonalisationContext` to all other agents
- **Output:** `{team_preference, dietary_flags, visited_venues, trip_style, language}`
- **Latency target:** < 200ms

---

## MongoDB Collections — Quick Reference

| Collection | Key fields | Index |
|---|---|---|
| `matches` | `home_team`, `away_team`, `kickoff_utc`, `venue_id`, `group`, `round` | B-tree on `home_team, away_team, kickoff_utc` |
| `venues` | `venue_id`, `city`, `coords`, `transport_options[]`, `description_embedding` | Atlas Vector Search on `description_embedding` (cosine, 768) |
| `local_businesses` | `name`, `category`, `cuisine`, `halal_flag`, `vegan_flag`, `coords`, `distance_to_venue_m`, `description_embedding` | Atlas Hybrid (BM25+vector) |
| `faq_embeddings` | `question`, `answer`, `tags`, `embedding` | Atlas Vector Search on `embedding` (cosine, 768) |
| `fan_graph` | `fan_id`, `team_preference[]`, `dietary_flags[]`, `preferred_language`, `visited_venues[]`, `past_queries[]` | B-tree on `fan_id` |

---

## API Contracts

### `POST /api/chat`
```json
// Request
{"message": "string", "session_id": "string", "language_hint": "string (optional)"}

// Response
{
  "response": {
    "type": "match_card | itinerary | business_list | faq_answer | memory_summary",
    "data": {},
    "text": "string"
  },
  "trace": {
    "agents_fired": ["string"],
    "total_ms": 0,
    "steps": [{"agent": "", "tool": "", "query": "", "duration_ms": 0, "score": 0}]
  },
  "session_id": "string"
}
```

### `GET /api/health`
```json
{"status": "ok", "atlas_connected": true, "gemini_reachable": true, "phoenix_connected": true}
```

### `GET /api/memory/{session_id}`
Returns the raw `fan_graph` document for the session.

---

## Self-Evaluation Loop

```
Agent synthesises response
    → Arize LLM-as-judge scores: relevance + completeness + accuracy
    → avg score ≥ 0.75 → return to fan
    → avg score < 0.75 → retry with relaxed Atlas query (lower min_score, broader date range)
    → retry scored → return regardless (max 2 retries)
```

Trace panel shows both attempts with `RETRY` / `PASS` markers.

---

## Day 1 Checklist (June 1, 2026)

- [ ] 1.1 Create MongoDB Atlas M0 cluster on GCP us-east-1. Note connection string.
- [ ] 1.2 Enable Vertex AI, Agent Builder, Cloud Run in GCP Console.
- [ ] 1.3 Create Arize Phoenix account. Note `ARIZE_SPACE_ID` and `ARIZE_API_KEY`.
- [ ] 1.4 Repo is live on GitHub (this is done ✓).
- [ ] 1.5 Download FIFA 2026 match schedule JSON from public sources.
- [ ] 1.6 Write `backend/scripts/data_loader.py` — parse match JSON, insert to `matches` collection.
- [ ] 1.7 Create `venues` collection with 16 documents (manual from Wikipedia + FIFA).

**Checkpoint:** Atlas has `matches` + `venues` collections. Python connection confirmed.

---

## Critical Rules for This Project

- **All Atlas operations go through MongoDB MCP Server** — never use `pymongo` directly in agent code
- **Never commit `.env`** — all secrets live in `.env` only, which is gitignored
- **Gemini text-embedding-004 only** for all vector fields (768 dims) — do not mix embedding models
- **Arize Phoenix trace spans must be wired from day 4 onwards** — every agent call emits a span
- **LLM-as-judge threshold is 0.75** — do not change without testing
- **Fan ID = SHA256 of session token** — never store PII in `fan_graph`
- **Response latency P95 < 5000ms** — check trace panel `total_ms` after every major change
- **The hosted URL must work from a fresh browser with no login** — test this on every deploy

---

## Key Dates

| Date | Milestone |
|---|---|
| June 1 | Day 1 — Environment setup + data pipeline |
| June 2 | Day 2 — Vector indexes + embedding pipeline |
| June 3 | Day 3 — Business data + hybrid search |
| June 4 | Day 4 — Agent network (Match + Discovery) |
| June 5 | Day 5 — Logistics + Memory + self-correction |
| June 6 | Day 6 — API server + multilingual testing |
| June 7 | Day 7 — Frontend UI |
| June 8 | Day 8 — Cloud Run deploy + perf tuning |
| June 9–10 | Day 9–10 — Demo video + submission |
| **June 11** | **Submission deadline — 2:00pm PDT** |

---

## Judging Criteria (40pts each)

1. **Technological implementation** — depth of Gemini ADK + MongoDB MCP + Arize integration
2. **Design** — no-login UI, structured cards, live trace panel, query chips
3. **Potential impact** — 6M+ fans, multilingual, largest World Cup ever
4. **Quality of idea** — hackathon theme match, opening-day deadline, immediately experienceable

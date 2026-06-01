# MatchMind — Feature Specification

> Tied to the hackathon judging criteria: Technological Implementation (40pts) · Design (40pts) · Potential Impact (40pts) · Quality of Idea (40pts)

---

## Feature Tiers

Features are organised into four tiers by strategic value:

| Tier | Description | Count |
|---|---|---|
| **Win Feature** | The single capability that wins the MongoDB prize | 1 |
| **Wow Features** | Capabilities that make judges pause and say "how did they do that" | 4 |
| **Core Features** | Expected by judges — must work perfectly | 6 |
| **Coupling Features** | Combine two or more partner technologies for bonus depth | 4 |

---

## Tier 1 — Win Feature

### W-01: Fan Memory Graph with GraphRAG

**Why this wins:** MongoDB judge Daoud Farooqi (Partner Solutions Architect) published the GraphRAG + Atlas integration himself. Using a feature the judge shipped is the single highest-leverage move in this hackathon.

**What it does:**  
Every interaction the fan has is stored in MongoDB as a connected knowledge graph: team preference, city of origin, dietary restrictions, previous queries, match interests, travel companions. When the fan asks a follow-up question, the Memory Agent traverses this graph using MongoDB's GraphRAG GA feature to return answers that feel personalised — not retrieved.

**Example:**  
> "Since you said you prefer vegetarian food earlier, here are three vegetarian restaurants near MetLife Stadium."

**Technical details:**

| Detail | Value |
|---|---|
| Collection | `fan_graph` in MongoDB Atlas M0 |
| Fan ID | SHA256 of session token — no PII stored |
| Schema | `fan_id → team_preference[] → dietary_flags[] → visited_venues[] → past_query_embeddings[] → trip_companions` |
| GraphRAG traversal | Memory Agent retrieves fan subgraph, passes as context to Gemini before retrieval |
| Write path | Memory Agent upserts `fan_graph` after every query via MongoDB MCP `upsert()` |
| MongoDB feature version | GraphRAG with Atlas + LangChain, Generally Available (2025) |

**Agent:** Memory Agent  
**Status:** Day 5

---

## Tier 2 — Wow Features

### WW-01: Multilingual Agent — 12+ Languages

**What it does:**  
The fan types in any language. Gemini 3.5 Flash handles language detection and response generation natively — no separate detection step. The Router Agent extracts entities (team names, city names, dates) from any language using Gemini's multilingual function calling. Responses are always returned in the same language the fan used.

**Demo moment:** A judge types in Malayalam and receives a fully structured response in Malayalam within five seconds.

**Verified languages:** English · Spanish · French · Portuguese · Arabic · German · Italian · Japanese · Korean · Hindi · Malayalam · Mandarin Chinese

**Technical details:**
- Gemini 3.5 Flash handles detection implicitly via its system prompt
- Query chips in the UI include examples in three languages by default
- Entity extraction (`team_name`, `city`, `date`) works across all 12 languages via Gemini function calling
- No fallback translation service needed — Gemini is the fallback

**Agent:** Router Agent (detection + extraction) + all agents (response generation)  
**Status:** Day 6

---

### WW-02: Live Agent Trace Panel

**What it does:**  
Adjacent to every chat response, a collapsible trace panel shows:
1. Which agents fired (with latency per agent in ms)
2. The exact MongoDB query text that executed
3. How many documents were retrieved
4. Latency per step in milliseconds
5. The Arize Phoenix LLM-as-judge evaluation score

**Why this matters:** Turns observability into a UX feature. The judge can verify the system is not hallucinating — they see the real Atlas query and real retrieval results that produced the answer. This differentiates MatchMind from every other RAG demo that is a black box.

**Data source:** Arize Phoenix `openinference-instrumentation-mcp` captures every MongoDB MCP tool call as an OpenInference span, streamed back to the frontend as a separate JSON payload alongside the main response.

**Frontend component:** `TracePanel` — collapsible, renders agent steps as a vertical timeline with colour-coded pass/retry markers.

**Status:** Day 7 (frontend) — wired from Day 4 (agent instrumentation)

---

### WW-03: Full Match-Day Itinerary Generator

**What it does:**  
When a fan says "I am flying into Dallas for the Netherlands vs Japan match on June 14", the Logistics Agent autonomously generates a structured match-day plan:

- Suggested arrival time in the city
- Recommended hotel area
- Pre-match restaurant (personalised by dietary flags from `fan_graph`)
- Fan zone visit
- Stadium transport route with mode and duration
- Kickoff reminder
- Post-match exit strategy

**Output format:** Structured JSON rendered as a vertical timeline card in the UI — not a text paragraph.

```json
{
  "steps": [
    {"time": "14:00", "activity": "Arrive Dallas", "location": "DFW Airport", "transport_mode": "flight", "notes": ""},
    {"time": "15:30", "activity": "Pre-match meal", "location": "The Green Spot (vegan)", "transport_mode": "uber", "notes": "0.3 miles from AT&T Stadium"},
    {"time": "17:00", "activity": "Fan zone", "location": "AT&T Fan Zone Gate C", "transport_mode": "walk", "notes": "Opens 3 hours before kickoff"},
    {"time": "18:00", "activity": "Enter stadium", "location": "AT&T Stadium, Arlington TX", "transport_mode": "walk", "notes": ""},
    {"time": "21:00", "activity": "Kickoff: Netherlands vs Japan", "location": "AT&T Stadium", "transport_mode": null, "notes": "Group C"},
    {"time": "23:15", "activity": "Post-match exit", "location": "AT&T Stadium → Shuttle Stop 3", "transport_mode": "shuttle", "notes": "Last shuttle 01:00"}
  ]
}
```

**Agent:** Logistics Agent + Match Agent (coordinated by Agent Builder)  
**Status:** Day 5

---

### WW-04: Self-Evaluating Agent with Automatic Retry

**What it does:**  
After every response synthesis, a secondary Gemini call acts as an LLM-as-judge evaluator scoring the response on:

- **Relevance (0–1):** Does the response directly address what the fan asked?
- **Completeness (0–1):** Does it include all the information a fan would need to act?
- **Accuracy (0–1):** Does it correctly use the data retrieved from Atlas?

Combined score = simple average. If below **0.75**, the system automatically retries with a broader Atlas query before showing anything to the fan. The fan never sees a poor-quality response.

**Retry strategy:**
- Discovery Agent: retry with relaxed vector search (lower `min_score`) and `dietary_flags` as soft filter instead of hard filter
- Match Agent: retry with broader date range (±7 days from original date)
- Maximum 2 retries per query

**Trace panel shows:** both attempts, scores, RETRY/PASS markers  
**Framework:** Arize Phoenix LLM-as-judge (`openinference-instrumentation-google-adk`)  
**Status:** Day 5

---

## Tier 3 — Core Features

### C-01: Match Schedule Lookup

All 104 matches seeded into Atlas `matches` collection. Structured MatchCard response with team names, kickoff time (UTC + local), venue, city, group, round, broadcast info.

**MongoDB operation:** `find()` on `matches` collection  
**Response format:** `MatchCard {match_id, home_team, away_team, kickoff_utc, kickoff_local, venue_name, city, group, round, broadcast[]}`  
**Latency:** < 500ms  
**Status:** Day 1 (data) + Day 4 (agent)

---

### C-02: Venue & Stadium Information

16 stadiums with capacity, transport links, nearby fan zones, and coordinates. Vector search enables vibe-based queries ("stadium with the best atmosphere").

**MongoDB operation:** `vectorSearch()` on `venues` collection (cosine, 768 dims)  
**Index:** Atlas Vector Search on `description_embedding`  
**Status:** Day 2 (index) + Day 4 (agent)

---

### C-03: Local Food & Stay Finder

~2,500 business records across the top-5 venues (MetLife NJ, LA, Dallas, Atlanta, Houston). Hybrid BM25+vector search for dietary preference matching.

**MongoDB operation:** `hybrid_search()` on `local_businesses` — BM25 on `name + description` + vector on `description_embedding`  
**Filtering:** `halal_flag`, `vegan_flag`, `category`, `near_venue_id`  
**Status:** Day 3 (data + index) + Day 4 (agent)

---

### C-04: Team FAQ Knowledge Base

200+ FAQs with embeddings covering World Cup rules, team history, player info, tournament rules. Semantic search for natural language questions.

**MongoDB operation:** `vectorSearch()` on `faq_embeddings` collection  
**Embedding generation:** Gemini text-embedding-004 (768 dims), generated once at load time  
**Status:** Day 2

---

### C-05: Multi-Agent Routing

Router Agent classifies intent and dispatches to the correct specialist agent(s). Agent Builder handles orchestration including parallel agent firing.

**Intent types:** `MATCH_LOOKUP | ITINERARY | LOCAL_DISCOVER | TEAM_INFO | GENERAL_FAQ | MEMORY_READ`  
**Parallel dispatch:** ITINERARY intent fires Match + Discovery + Logistics in parallel  
**Status:** Day 4

---

### C-06: Fan Preference Persistence

Session-scoped memory stored in `fan_graph`. Personalisation improves with every query. Preferences persist for the full session and can be queried explicitly ("show me what you remember about me").

**MongoDB operation:** `upsert()` on `fan_graph`  
**Session scope:** SHA256 of session token (no PII)  
**Status:** Day 5

---

## Tier 4 — Coupling Features

### CP-01: Arize Phoenix Traces MongoDB MCP Calls

`openinference-instrumentation-mcp` captures every `vectorSearch()`, `find()`, and `aggregate()` call as an OpenInference span in Phoenix. The entire journey from fan query → Atlas → response is a single unified trace.

**Technologies combined:** MongoDB MCP Server + Arize Phoenix  
**Status:** Day 4 (wired), Day 7 (visible in UI)

---

### CP-02: Gemini Embeddings Stored Natively in Atlas

FAQ chunks and business descriptions are embedded using Gemini `text-embedding-004` and stored directly in Atlas Vector Search indexes. No external embedding service — Gemini and MongoDB are the complete pipeline.

**Technologies combined:** Gemini API + MongoDB Atlas Vector Search  
**Script:** `backend/scripts/embed_data.py`  
**Status:** Day 2

---

### CP-03: Performance Advisor Integration (MongoDB MCP Winter 2026)

The Memory Agent calls `listClusterSuggestedIndexes()` during development to automatically create Atlas-recommended indexes. This is the newest MongoDB MCP Server feature from Winter 2026.

**Judge signal:** Gaurab Aryal (Sr PM, MongoDB) is directly responsible for this feature.  
**Technologies combined:** MongoDB MCP Server Winter 2026 + Atlas Performance Advisor  
**Status:** Day 5 (agent) + Day 8 (apply suggested indexes)

---

### CP-04: Cloud Run One-Click Deploy from AI Studio

The agent backend deploys to Cloud Run from Google AI Studio with a single button click (announced May 2025). Fully reproducible deployment — documented in README.

**Technologies combined:** Google Cloud Run + Google AI Studio  
**Status:** Day 8

---

## Non-Functional Requirements

| Requirement | Target | How Measured |
|---|---|---|
| Response latency | P95 < 5000ms | Trace panel `total_ms` across 20 test queries |
| Availability | > 95% during judging (Jun 7–25) | Cloud Run `/api/health` returns 200 |
| Atlas connect time | < 100ms | `GET /api/health` response time |
| Eval score average | > 0.80 across 20 demo queries | Arize Phoenix dashboard |
| Monthly cost | $0.00 | All free tiers, no billing alerts |
| Cold start time | < 4s (with warm-up ping) | Cloud Run invocation log |
| No-login access | Full access from fresh browser | Test on every deploy |

---

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-001 | Return correct match info for any of the 48 teams within 2 seconds |
| FR-002 | Accept queries in 8+ languages, respond in the same language |
| FR-003 | Return 3+ relevant local businesses for any of the 5 seeded venue cities, filtered by dietary flags |
| FR-004 | Generate a complete match-day itinerary with 4+ timestamped steps |
| FR-005 | Persist fan preferences across queries within a session |
| FR-006 | Trigger automatic retry when LLM-as-judge score < 0.75, max 2 retries |
| FR-007 | Display trace panel with agents fired, MongoDB queries, per-step latency, Arize score |
| FR-008 | Hosted URL fully accessible with no login, no API key, no installation |
| FR-009 | Public GitHub repo with MIT license visible in About section + complete README |

---

## Feature Status Tracker

| Feature | Tier | Day | Status |
|---|---|---|---|
| Fan Memory Graph (GraphRAG) | Win | 5 | Pending |
| Multilingual Agent | Wow | 6 | Pending |
| Live Agent Trace Panel | Wow | 7 | Pending |
| Match-Day Itinerary Generator | Wow | 5 | Pending |
| Self-Evaluating Agent | Wow | 5 | Pending |
| Match Schedule Lookup | Core | 1+4 | In Progress |
| Venue & Stadium Info | Core | 2+4 | Pending |
| Local Food & Stay Finder | Core | 3+4 | Pending |
| Team FAQ Knowledge Base | Core | 2 | Pending |
| Multi-Agent Routing | Core | 4 | Pending |
| Fan Preference Persistence | Core | 5 | Pending |
| Arize ↔ MongoDB MCP Traces | Coupling | 4+7 | Pending |
| Gemini Embeddings in Atlas | Coupling | 2 | Pending |
| Performance Advisor MCP | Coupling | 5+8 | Pending |
| Cloud Run One-Click Deploy | Coupling | 8 | Pending |

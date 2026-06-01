# MatchMind — 2026 FIFA World Cup Fan Intelligence Agent

> **Your autonomous World Cup concierge.**  
> Tell MatchMind you're going to the World Cup and it plans your entire experience — matches, food, transport, local secrets — in any language, in under five seconds.

**Hackathon:** Google Cloud Rapid Agent Hackathon 2026 · MongoDB Partner Track  
**Deadline:** June 11, 2026 (World Cup opening day)  
**Prize target:** $5,000 (1st place, MongoDB track)  
**Monthly cost:** $0.00 — all free tiers  
**Submission:** [rapid-agent.devpost.com](https://rapid-agent.devpost.com)

---

## What It Does

MatchMind is an **autonomous multi-agent AI system** built for the 2026 FIFA World Cup. A fan types a high-level goal in any language — _"plan my Brazil match day"_ — and without further prompting the system:

1. Classifies intent and detects language (Router Agent)
2. Retrieves match schedules, venues, and team data from MongoDB Atlas (Match Agent)
3. Finds personalised local food and fan zones via hybrid BM25+vector search (Discovery Agent)
4. Generates a minute-by-minute match-day itinerary (Logistics Agent)
5. Persists fan preferences as a knowledge graph and improves with every query (Memory Agent)
6. Evaluates its own output — and self-corrects if quality is below threshold (Arize Phoenix)

---

## Architecture

```
Fan (browser)
     │
     ▼
Next.js UI ──────────────────── Vercel (free)
     │
     ▼
FastAPI Backend ─────────────── Cloud Run (free tier)
     │
     ├── Router Agent ──────── Gemini 3.5 Flash / Google ADK
     │        │
     │        ├── Match Intelligence Agent ─── MongoDB MCP → matches / venues / teams
     │        ├── Discovery Agent ────────────── MongoDB MCP → local_businesses / faq_embeddings
     │        ├── Logistics Agent ────────────── MongoDB MCP + Gemini web_search
     │        └── Memory Agent ───────────────── MongoDB MCP → fan_graph (GraphRAG)
     │
     ├── MongoDB Atlas M0 ──── Vector Search · Hybrid Search · GraphRAG GA
     │
     └── Arize Phoenix ──────── openinference-mcp · LLM-as-judge evaluation
```

**Stack summary:**

| Layer | Technology |
|---|---|
| LLM | Gemini 3.5 Flash (Vertex AI) |
| Orchestration | Google Cloud Agent Builder |
| Agent framework | Google ADK (Python) |
| Embedding model | Gemini text-embedding-004 (768 dims) |
| Database | MongoDB Atlas M0 (free forever) |
| Vector / Hybrid Search | Atlas Vector Search + Atlas Hybrid Search |
| Knowledge graph | MongoDB GraphRAG GA (LangChain + Atlas) |
| Agent↔DB bridge | MongoDB MCP Server (Winter 2026) |
| Observability | Arize Phoenix (free cloud) |
| API server | Python FastAPI + Docker |
| Backend hosting | Google Cloud Run (free tier) |
| Frontend | Next.js 14 App Router |
| Frontend hosting | Vercel (hobby tier) |

---

## MongoDB Collections

| Collection | Documents | Purpose |
|---|---|---|
| `matches` | 104 | All 2026 World Cup matches with schedules, venues, broadcast info |
| `venues` | 16 | Host stadiums with transport options, coordinates, description embeddings |
| `local_businesses` | ~2,500 | Restaurants, hotels, fan zones near top-5 venues with hybrid search index |
| `faq_embeddings` | 200+ | World Cup FAQs with semantic vector search index |
| `fan_graph` | dynamic | Fan knowledge graph — preferences, history, relationships (GraphRAG) |

---

## Quickstart (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas M0 cluster ([free signup](https://www.mongodb.com/cloud/atlas/register))
- Google Cloud account with Vertex AI + Agent Builder + Cloud Run enabled
- Arize Phoenix free cloud account ([app.phoenix.arize.com](https://app.phoenix.arize.com))

### 1. Clone & configure environment

```bash
git clone https://github.com/<your-username>/matchmind.git
cd matchmind
cp .env.example .env
# Fill in all values in .env (see docs below)
```

### 2. Install backend dependencies

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 3. Load data into Atlas

```bash
# Load match schedule
python scripts/data_loader.py

# Embed venues + FAQs + businesses
python scripts/embed_data.py
```

### 4. Start MongoDB MCP Server

```bash
npx @mongodb-js/mongodb-mcp-server
```

### 5. Run backend

```bash
cd backend
uvicorn api.main:app --reload --port 8000
```

### 6. Run frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## Environment Variables

See [.env.example](.env.example) for the full list. Required values:

| Variable | Where to get it |
|---|---|
| `MONGODB_URI` | Atlas cluster → Connect → Drivers |
| `GOOGLE_CLOUD_PROJECT` | GCP Console → Project selector |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) → Get API key |
| `ARIZE_SPACE_ID` | [app.phoenix.arize.com](https://app.phoenix.arize.com) → Settings |
| `ARIZE_API_KEY` | Arize Phoenix → Settings → API Keys |
| `NEXT_PUBLIC_API_URL` | Cloud Run service URL after deploy |

---

## Deployment

### Backend → Cloud Run

```bash
gcloud run deploy matchmind-backend \
  --source ./backend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MONGODB_URI=$MONGODB_URI,GEMINI_API_KEY=$GEMINI_API_KEY
```

### Frontend → Vercel

```bash
cd frontend
vercel --prod
# Set NEXT_PUBLIC_API_URL to your Cloud Run URL in Vercel dashboard
```

### Warm-up (important for judges)

Cloud Run scales to zero when idle. The first cold-start adds 2–3 seconds.  
Open the app URL **once** before recording your review — it will warm up automatically.

A GitHub Actions workflow pings the health endpoint every 10 minutes during the judging period (June 7–25).

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/chat` | Main agent endpoint. Accepts `{message, session_id}`, returns agent response + trace |
| `GET` | `/api/health` | Service health check — Atlas, Gemini, Phoenix connectivity |
| `GET` | `/api/memory/{session_id}` | Returns full fan_graph for the session |

---

## Agent Self-Evaluation

Every response is scored by a secondary Gemini LLM-as-judge call (via Arize Phoenix):

- **Relevance** — does the response address what the fan asked?
- **Completeness** — does it include all the info a fan needs to act?
- **Accuracy** — does it correctly use the Atlas data retrieved?

**Threshold: 0.75.** Below that, the system automatically retries with a broader Atlas query. The score and retry status are visible in the trace panel on every response.

---

## Repository Structure

```
matchmind/
├── backend/
│   ├── agents/          # Router, Match, Discovery, Logistics, Memory agents
│   ├── api/             # FastAPI app — /chat, /health, /memory endpoints
│   ├── data/            # Schema definitions and seed data
│   ├── scripts/         # data_loader.py, embed_data.py, warm_up.py
│   └── Dockerfile
├── frontend/            # Next.js 14 app — chat UI, response cards, trace panel
├── docs/
│   ├── features.md      # Full feature specification and tier breakdown
│   ├── branching.md     # Git branching strategy
│   └── architecture.md  # Detailed architecture notes
├── .env.example         # Environment variable template
├── CLAUDE.md            # AI assistant context for this repo
└── README.md
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). This is a hackathon project — PRs welcome for bug fixes and improvements before June 11.

## License

MIT — see [LICENSE](LICENSE).

---

*MatchMind | Google Cloud Rapid Agent Hackathon 2026 | MongoDB Track*  
*Total monthly cost: $0.00 · Score projection: 140/160 · Deadline: June 11, 2026*

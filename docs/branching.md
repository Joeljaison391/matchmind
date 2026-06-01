# MatchMind — Git Branching Strategy

## Overview

Given the 10-day hackathon timeline (June 1–11, 2026) with a solo or small-team workflow, this strategy prioritises **speed without chaos** — a clean `main` that always deploys, feature branches that stay short-lived, and a simple naming convention that maps directly to the 10-day plan.

---

## Branch Model

```
main
 └── dev
      ├── day1/data-pipeline
      ├── day2/vector-indexes
      ├── day3/business-data
      ├── day4/agent-network
      ├── day5/memory-self-correct
      ├── day6/api-server
      ├── day7/frontend-ui
      ├── day8/cloud-run-deploy
      └── day9/demo-polish
```

### `main`

- **Always deployable.** Every commit on `main` must pass the health check at `/api/health`.
- Directly maps to the live Vercel + Cloud Run deployment.
- **Never commit directly to `main`.** Merge only via PR from `dev`.
- Protected: require at least 1 review (or self-approve if solo) before merge.

### `dev`

- Integration branch. The day's work lands here first.
- Merged into `main` at the end of each day once the day's checkpoint passes.
- If a day's checkpoint fails, the branch stays at the previous `main` state — no broken deploys.

### Feature / Day Branches (`day{N}/description`)

- Cut from `dev` at the start of each workday.
- Scope: exactly one day's tasks from the implementation plan.
- Merged back into `dev` via PR once the checkpoint for that day passes.
- Deleted after merge.

---

## Branch Naming Convention

| Pattern | When to use | Example |
|---|---|---|
| `day{N}/{kebab-description}` | Primary day-scoped branches | `day4/agent-network` |
| `fix/{kebab-description}` | Bug fixes discovered mid-day | `fix/atlas-connection-pool` |
| `hotfix/{kebab-description}` | Critical bugs in `main` during judging | `hotfix/cold-start-timeout` |
| `chore/{kebab-description}` | Non-functional changes (docs, CI, config) | `chore/add-warm-up-action` |

- Use lowercase and hyphens only — no underscores, no slashes beyond the prefix.
- Keep names short (< 40 characters).

---

## Commit Message Format

```
<type>: <short summary in present tense>

[optional body — what and why, not how]
```

**Types:**
- `feat` — new capability
- `fix` — bug fix
- `data` — seed data, embeddings, Atlas index changes
- `agent` — agent logic changes
- `api` — FastAPI routes or schemas
- `ui` — frontend changes
- `infra` — Docker, Cloud Run, Vercel, GitHub Actions
- `docs` — documentation only
- `chore` — deps, config, non-functional

**Examples:**
```
feat: add hybrid search to Discovery Agent with dietary flag filters

data: seed local_businesses for MetLife NJ — 500 records, embeddings included

fix: cap Atlas connection pool to 10 to respect M0 100-connection limit

agent: implement LLM-as-judge eval loop with 0.75 threshold and retry

ui: add collapsible trace panel showing agent steps and Arize score
```

---

## Day-by-Day Workflow

### Start of day
```bash
git checkout dev
git pull origin dev
git checkout -b day{N}/description
```

### During the day
```bash
# Commit often — at minimum after each numbered task in the plan
git add <specific files>
git commit -m "feat: ..."
```

### End of day (checkpoint passes)
```bash
# Push day branch and open PR → dev
git push origin day{N}/description
# Create PR on GitHub: day{N}/description → dev
# Self-review, confirm checkpoint, merge

# If day is complete and checkpoint passes, also merge dev → main
git checkout dev && git pull
git checkout main && git pull
git merge dev --no-ff -m "chore: merge day{N} — <checkpoint description>"
git push origin main
```

### Hotfix during judging period
```bash
git checkout main
git pull origin main
git checkout -b hotfix/description
# Fix, commit, push
# PR hotfix → main (skip dev — urgent)
# After merge, backport to dev:
git checkout dev && git merge main
```

---

## Pull Request Rules

1. **Title:** mirrors the branch name — `day4/agent-network` → `Day 4: Agent Network`
2. **Description:** paste the day's checkpoint from the PRD as the acceptance criteria
3. **Checklist:** include the numbered task list from the implementation plan
4. **Labels:** use GitHub labels matching the day number (`day-1` … `day-10`) and type (`backend`, `frontend`, `data`, `infra`, `docs`)
5. **Merge method:** Squash and merge into `dev`; merge commit into `main` (to preserve history)

---

## Tags & Releases

Tag `main` at the end of each day with the format `v0.{N}.0`:

```bash
git tag -a v0.1.0 -m "Day 1 checkpoint: Atlas data pipeline"
git push origin v0.1.0
```

Final submission tag: `v1.0.0` (end of Day 10, before submission).

---

## CI / GitHub Actions

Workflows live in `.github/workflows/`:

| File | Trigger | What it does |
|---|---|---|
| `warm_up.yml` | Schedule: every 10 min (Jun 7–25) | Pings `/api/health` to keep Cloud Run warm |
| `lint.yml` | Push to any branch | Runs `ruff` (Python) and `eslint` (Next.js) |
| `deploy-backend.yml` | Push to `main` | `gcloud run deploy` to Cloud Run |
| `deploy-frontend.yml` | Push to `main` | Vercel production deployment |

---

## What Never Goes in Git

- `.env` — all secrets, including `MONGODB_URI`, `GEMINI_API_KEY`, `ARIZE_API_KEY`
- `backend/data/raw/` — raw data files downloaded from public sources
- `backend/data/embeddings_cache/` — locally cached embeddings

Use `.env.example` with placeholder values for all secrets (this file is committed).

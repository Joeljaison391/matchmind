"""
data_loader.py — MatchMind Day 1 seed script
Loads teams, venues, and matches into MongoDB Atlas.

Run from the backend/ directory:
    python scripts/data_loader.py

Requires MONGODB_URI in .env (project root).
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, errors

# ── Resolve paths ────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent           # backend/scripts/
BACKEND_DIR = SCRIPT_DIR.parent                          # backend/
PROJECT_DIR = BACKEND_DIR.parent                         # project root (D:\MatchMind)
SEED_DIR    = BACKEND_DIR / "data" / "seed"

load_dotenv(PROJECT_DIR / ".env")

# ── Atlas connection ─────────────────────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME     = os.getenv("MONGODB_DB_NAME", "matchmind")

if not MONGODB_URI:
    sys.exit("ERROR: MONGODB_URI not set. Fill in .env and retry.")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10_000)
db     = client[DB_NAME]

# ── Ground name → venue_id mapping ──────────────────────────────────────────
GROUND_TO_VENUE_ID = {
    "Vancouver":                                  "bc_place",
    "Seattle":                                    "lumen_field",
    "San Francisco Bay Area (Santa Clara)":       "levis_stadium",
    "Los Angeles (Inglewood)":                    "sofi_stadium",
    "Guadalajara (Zapopan)":                      "estadio_akron",
    "Mexico City":                                "estadio_azteca",
    "Monterrey (Guadalupe)":                      "estadio_bbva",
    "Houston":                                    "nrg_stadium",
    "Dallas (Arlington)":                         "att_stadium",
    "Kansas City":                                "arrowhead_stadium",
    "Atlanta":                                    "mercedes_benz_stadium",
    "Miami (Miami Gardens)":                      "hard_rock_stadium",
    "Toronto":                                    "bmo_field",
    "Boston (Foxborough)":                        "gillette_stadium",
    "Philadelphia":                               "lincoln_financial_field",
    "New York/New Jersey (East Rutherford)":      "metlife_stadium",
}

# ── Round label → internal round type ───────────────────────────────────────
def get_round_type(round_label: str) -> str:
    r = round_label.lower()
    if "matchday" in r or "group" in r:
        return "group_stage"
    if "round of 32" in r:
        return "r32"
    if "round of 16" in r:
        return "r16"
    if "quarter" in r:
        return "qf"
    if "semi" in r:
        return "sf"
    if "third" in r:
        return "3rd_place"
    if "final" in r:
        return "final"
    return "other"

# ── UTC time parser ──────────────────────────────────────────────────────────
def parse_utc(date_str: str, time_str: str) -> datetime:
    """
    Convert 'YYYY-MM-DD' + 'HH:MM UTC-N' → UTC datetime.
    E.g. '2026-06-11' + '13:00 UTC-6' → datetime(2026, 6, 11, 19, 0, tzinfo=UTC)
    """
    time_part, *tz_parts = time_str.split()
    hour, minute = map(int, time_part.split(":"))

    offset_hours = 0
    if tz_parts:
        tz = tz_parts[0]  # e.g. 'UTC-6', 'UTC-4', 'UTC+0'
        if tz.startswith("UTC"):
            remainder = tz[3:]
            if remainder:
                offset_hours = int(remainder)  # negative for west, positive for east

    year, month, day = map(int, date_str.split("-"))
    local_dt = datetime(year, month, day, hour, minute)
    # UTC = local_time − offset  (UTC-6 means local is 6 hrs behind UTC)
    utc_dt = local_dt - timedelta(hours=offset_hours)
    return utc_dt.replace(tzinfo=timezone.utc)


# ── Broadcast defaults by host country ───────────────────────────────────────
def get_broadcast(venue_id: str) -> list[str]:
    mexico_venues = {"estadio_azteca", "estadio_akron", "estadio_bbva"}
    canada_venues = {"bc_place", "bmo_field"}
    if venue_id in mexico_venues:
        return ["Televisa", "TV Azteca", "ViX"]
    if venue_id in canada_venues:
        return ["CBC", "TSN", "TVA Sports"]
    return ["FOX", "FS1", "Telemundo", "Peacock"]  # USA default


# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — Teams
# ════════════════════════════════════════════════════════════════════════════
def load_teams():
    print("\n── Teams ─────────────────────────────────────────────────────")
    raw = json.loads((SEED_DIR / "teams.json").read_text(encoding="utf-8"))

    docs = []
    for i, t in enumerate(raw, start=1):
        docs.append({
            "team_id":   t["fifa_code"].lower(),
            "name":      t["name"],
            "fifa_code": t["fifa_code"],
            "group":     t["group"],
            "confed":    t["confed"],
            "continent": t["continent"],
            "flag":      t.get("flag", ""),
            # description_embedding populated on Day 2
            "description_embedding": [],
        })

    col = db["teams"]
    col.drop()
    result = col.insert_many(docs)
    col.create_index([("team_id", ASCENDING)], unique=True, background=True)
    col.create_index([("name", ASCENDING)], background=True)
    col.create_index([("fifa_code", ASCENDING)], background=True)
    col.create_index([("group", ASCENDING)], background=True)
    print(f"  Inserted {len(result.inserted_ids)} teams  (expected 48)")


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — Venues
# ════════════════════════════════════════════════════════════════════════════
def load_venues():
    print("\n── Venues ────────────────────────────────────────────────────")
    raw = json.loads((SEED_DIR / "venues.json").read_text(encoding="utf-8"))

    col = db["venues"]
    col.drop()
    result = col.insert_many(raw)
    col.create_index([("venue_id", ASCENDING)], unique=True, background=True)
    col.create_index([("city", ASCENDING)], background=True)
    # Vector Search index on description_embedding created separately in Atlas UI (Day 2)
    print(f"  Inserted {len(result.inserted_ids)} venues  (expected 16)")


# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — Matches
# ════════════════════════════════════════════════════════════════════════════
def load_matches():
    print("\n── Matches ───────────────────────────────────────────────────")
    raw = json.loads((SEED_DIR / "matches_raw.json").read_text(encoding="utf-8"))

    docs = []
    for i, m in enumerate(raw, start=1):
        match_id  = f"WC2026_M{i:03d}"
        venue_id  = GROUND_TO_VENUE_ID.get(m["ground"], "unknown")
        round_type = get_round_type(m["round"])
        kickoff_utc = parse_utc(m["date"], m["time"])

        # Extract group letter only (e.g. "Group A" → "A")
        group_raw  = m.get("group") or ""
        group_val  = group_raw.replace("Group ", "").strip() or None

        docs.append({
            "match_id":      match_id,
            "match_num":     m.get("num", i),           # official FIFA match number for knockouts
            "home_team":     m["team1"],
            "away_team":     m["team2"],
            "kickoff_utc":   kickoff_utc,
            "kickoff_local": m["time"],                 # original local time string for display
            "date":          m["date"],
            "venue_id":      venue_id,
            "venue_name":    m["ground"],
            "group":         group_val,
            "round":         round_type,
            "round_label":   m["round"],                # human-readable (e.g. "Matchday 4")
            "broadcast":     get_broadcast(venue_id),
        })

    col = db["matches"]
    col.drop()
    result = col.insert_many(docs)

    # Indexes for fast lookups
    col.create_index([("match_id",    ASCENDING)], unique=True, background=True)
    col.create_index([("home_team",   ASCENDING)], background=True)
    col.create_index([("away_team",   ASCENDING)], background=True)
    col.create_index([("kickoff_utc", ASCENDING)], background=True)
    col.create_index([("group",       ASCENDING)], background=True)
    col.create_index([("round",       ASCENDING)], background=True)
    col.create_index([("venue_id",    ASCENDING)], background=True)
    # Compound index for the most common agent query: "team + date range"
    col.create_index(
        [("home_team", ASCENDING), ("kickoff_utc", ASCENDING)],
        background=True,
    )
    col.create_index(
        [("away_team", ASCENDING), ("kickoff_utc", ASCENDING)],
        background=True,
    )

    print(f"  Inserted {len(result.inserted_ids)} matches  (expected 104)")

    # Quick breakdown
    group_matches    = sum(1 for d in docs if d["round"] == "group_stage")
    knockout_matches = sum(1 for d in docs if d["round"] != "group_stage")
    print(f"    Group stage : {group_matches}")
    print(f"    Knockout    : {knockout_matches}")


# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — fan_graph collection (empty scaffold, populated at runtime)
# ════════════════════════════════════════════════════════════════════════════
def scaffold_fan_graph():
    print("\n── fan_graph ─────────────────────────────────────────────────")
    col = db["fan_graph"]
    col.create_index([("fan_id", ASCENDING)], unique=True, background=True)
    print("  fan_graph collection ready (index created, no seed docs needed)")


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"Connecting to Atlas — database: {DB_NAME}")
    try:
        # Quick ping to verify connection before doing any work
        client.admin.command("ping")
        print("  ✓ Atlas connection OK")
    except errors.ServerSelectionTimeoutError:
        sys.exit("ERROR: Could not reach Atlas. Check MONGODB_URI and network access.")

    load_teams()
    load_venues()
    load_matches()
    scaffold_fan_graph()

    print("\n── Summary ───────────────────────────────────────────────────")
    for col_name in ["teams", "venues", "matches", "fan_graph"]:
        count = db[col_name].count_documents({})
        print(f"  {col_name:<20} {count} documents")

    print("\n✅  Day 1 checkpoint: seed data loaded.\n")
    print("Next steps:")
    print("  Day 2 → run embed_data.py to generate Gemini embeddings")
    print("  Day 2 → create Atlas Vector Search indexes in the Atlas UI")
    client.close()

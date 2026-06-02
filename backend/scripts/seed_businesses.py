import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seed"


def load_and_insert(db):
    businesses = json.loads((SEED_DIR / "businesses.json").read_text(encoding="utf-8"))

    db.local_businesses.drop()
    db.local_businesses.insert_many(businesses)
    db.local_businesses.create_index("venue_id")
    db.local_businesses.create_index("category")
    db.local_businesses.create_index("halal_flag")
    db.local_businesses.create_index("vegan_flag")
    db.local_businesses.create_index([("city", 1), ("distance_to_venue_m", 1)])


if __name__ == "__main__":
    from pymongo import MongoClient

    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME", "matchmind")]

    print("seeding local_businesses...")
    load_and_insert(db)
    count = db.local_businesses.count_documents({})
    print(f"done — {count} documents inserted")

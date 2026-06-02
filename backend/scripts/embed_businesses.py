import os
import time
from pathlib import Path

from google import genai
from google.genai import types, errors
from dotenv import load_dotenv

load_dotenv()

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seed"

gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_embedding(text):
    for attempt in range(3):
        try:
            result = gemini.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
            return list(result.embeddings[0].values)
        except errors.ClientError as e:
            if e.status_code == 429 and attempt < 2:
                print("  rate limited, waiting 65s...")
                time.sleep(65)
            else:
                raise


def embed_businesses(db):
    cursor = db.local_businesses.find(
        {"description_embedding": []},
        {"_id": 1, "name": 1, "description": 1, "cuisine": 1, "category": 1}
    )
    docs = list(cursor)
    total = len(docs)
    print(f"  {total} businesses need embedding")

    for i, doc in enumerate(docs):
        text = f"{doc['category']} {doc['cuisine']} {doc['description']}"
        embedding = get_embedding(text)
        db.local_businesses.update_one(
            {"_id": doc["_id"]},
            {"$set": {"description_embedding": embedding}}
        )
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{total} done")
        time.sleep(0.65)


if __name__ == "__main__":
    from pymongo import MongoClient

    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME", "matchmind")]

    print("embedding businesses...")
    embed_businesses(db)
    print("done")

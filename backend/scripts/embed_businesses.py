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
    for attempt in range(5):
        try:
            result = gemini.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
            return list(result.embeddings[0].values)
        except errors.ClientError as e:
            if "429" in str(e) and attempt < 4:
                wait = 70 + attempt * 30  # 70s, 100s, 130s, 160s
                print(f"  rate limited (attempt {attempt + 1}), waiting {wait}s...")
                time.sleep(wait)
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
        time.sleep(0.8)


if __name__ == "__main__":
    from pymongo import MongoClient

    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME", "matchmind")]

    print("embedding businesses...")
    embed_businesses(db)
    print("done")

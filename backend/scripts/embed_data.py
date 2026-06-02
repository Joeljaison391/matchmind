import json
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


def embed_venues(db):
    venues = db.venues.find()
    for venue in venues:
        embedding = get_embedding(venue["description"])
        db.venues.update_one(
            {"venue_id": venue["venue_id"]},
            {"$set": {"description_embedding": embedding}}
        )


def build_faq_doc(faq, embedding):
    return {
        "question": faq["question"],
        "answer": faq["answer"],
        "tags": faq["tags"],
        "embedding": embedding,
    }


def embed_faqs(db):
    faq_file = SEED_DIR / "faqs.json"
    faqs = json.loads(faq_file.read_text(encoding="utf-8"))

    db.faq_embeddings.drop()

    docs = []
    for i, faq in enumerate(faqs):
        text = faq["question"] + " " + faq["answer"]
        embedding = get_embedding(text)
        docs.append(build_faq_doc(faq, embedding))
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(faqs)} done")
        time.sleep(0.65)  # ~92 req/min, stays under 100/min free tier

    db.faq_embeddings.insert_many(docs)


if __name__ == "__main__":
    from pymongo import MongoClient

    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME", "matchmind")]

    print("embedding venues...")
    embed_venues(db)
    print("done")

    print("embedding faqs...")
    embed_faqs(db)
    print("done")

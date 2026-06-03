import json
import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EVAL_PROMPT = """You are evaluating a FIFA World Cup AI assistant response.

Question: {question}
Answer: {answer}
{context_block}
Score each dimension from 0.0 to 1.0:
- relevance: does the answer address the question?
- completeness: is the answer sufficiently complete?
- accuracy: is the answer factually correct given the context?

Respond with JSON only:
{{"relevance": 0.0, "completeness": 0.0, "accuracy": 0.0}}"""


def score_response(question, answer, context=None):
    context_block = f"Context: {context}\n" if context else ""
    prompt = EVAL_PROMPT.format(
        question=question,
        answer=answer,
        context_block=context_block,
    )
    response = gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    scores = json.loads(response.text)
    scores["avg"] = round(
        (scores["relevance"] + scores["completeness"] + scores["accuracy"]) / 3, 4
    )
    return scores


def passes_threshold(scores, threshold=0.75):
    return scores["avg"] >= threshold

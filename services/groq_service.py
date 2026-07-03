import requests
import json
import time
from typing import Optional, Tuple
from config import GROQ_API_KEY

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

def _call_groq(prompt: str) -> Optional[str]:
    """Raw API call to Groq. Returns the text response or None on failure."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    try:
        response = requests.post(GROQ_URL, headers=headers, json=body, timeout=10)

        # Rate limit hit
        if response.status_code == 429:
            print("⚠️  Rate limit hit, waiting 60s...")
            time.sleep(60)
            response = requests.post(GROQ_URL, headers=headers, json=body, timeout=10)

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Groq API error: {e}")
        return None


def classify_and_summarize(article) -> Tuple[str, str]:
    """
    Takes an Article object.
    Returns (category, summary) tuple.
    Falls back gracefully if Groq fails.
    """

    # If article already has a category from the feed itself
    # we still ask Groq for a summary but trust the feed category
    known_category = article.category if article.category and article.category != "" else None

    prompt = f"""Classify this news article and write a summary.

    Title: {article.title}
    Description: {article.description[:400]}

    Respond with ONLY this JSON, no other text:
    {{"category": "Sports", "summary": "First sentence. Second sentence."}}

    Rules:
    - category must be exactly one of: Sports, Technology, Business, Entertainment, World, India, Environment, Regional
    - summary must be exactly 2 sentences, plain English, no special characters
    - do not include markdown, backticks, or explanation"""

    raw = _call_groq(prompt)

    if not raw:
        # Groq failed entirely — use feed category as fallback
        return (known_category or "General"), article.description[:120]

    try:
        # Strip any accidental markdown fences the model adds
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(clean)

        category = result.get("category", known_category or "General")
        summary = result.get("summary", article.description[:120])
        return category, summary

    except json.JSONDecodeError:
        # Model returned something but it wasn't valid JSON
        print(f"⚠️  JSON parse failed for: {article.title[:50]}")
        return (known_category or "General"), article.description[:120]


def process_articles(articles: list) -> list:
    """
    Runs classify_and_summarize on each article.
    Updates article.category and article.summary in place.
    Returns the updated list.
    """
    total = len(articles)

    for i, article in enumerate(articles):
        print(f"Processing {i+1}/{total}: {article.title[:50]}")

        category, summary = classify_and_summarize(article)
        article.category = category
        article.summary = summary

        # Small delay between calls to respect rate limits
        # 0.5s × 30 articles = ~15 seconds total, well within free tier
        time.sleep(0.5)

    return articles
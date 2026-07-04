import time
from services.rss_service import fetch_articles, TOPIC_FEEDS, CITY_FEEDS
from services.groq_service import classify_and_summarize
from database.db import (
    save_articles_to_cache, update_refresh_time,
    clear_stale_articles, cache_needs_refresh
)

ALL_TOPICS = list(TOPIC_FEEDS.keys())
# Only fetch regional for major cities that have feeds
ALL_CITIES = list(CITY_FEEDS.keys())

def refresh_cache():
    """
    Fetches ALL categories + ALL cities, processes via Groq,
    saves to shared cache. Called every 3 hours.
    """
    print("🔄 Starting cache refresh...")

    # Step 1 — clear articles older than 72 hours
    clear_stale_articles()
    print("🗑️  Cleared stale articles")

    # Step 2 — fetch all topic feeds (no city filter)
    print("📡 Fetching all topic feeds...")
    all_articles = fetch_articles(ALL_TOPICS, city=None)
    print(f"   Got {len(all_articles)} articles from topic feeds")

    # Step 3 — fetch each city feed separately
    # This gives each article the correct city tag
    for city in ALL_CITIES:
        city_articles = fetch_articles([], city=city)
        # Tag each article with its city
        for a in city_articles:
            a.city = city
        all_articles.extend(city_articles)
        print(f"   Got {len(city_articles)} articles from {city}")

    print(f"📰 Total articles to process: {len(all_articles)}")

    # Step 4 — classify + summarize each via Groq
    processed = []
    for i, article in enumerate(all_articles):
        print(f"✍️  Processing {i+1}/{len(all_articles)}: {article.title[:50]}")
        category, summary = classify_and_summarize(article)
        article.category = category
        article.summary = summary

        processed.append({
            "title": article.title,
            "summary": article.summary,
            "link": article.link,
            "source": article.source,
            "category": article.category,
            "is_regional": article.is_regional,
            "published": article.published,
            "city": getattr(article, "city", None)
        })

        time.sleep(0.5)  # respect Groq rate limit

    # Step 5 — save to shared cache
    save_articles_to_cache(processed)
    update_refresh_time()

    print(f"✅ Cache refresh complete — {len(processed)} articles cached")
    return len(processed)
import feedparser
import re
from dataclasses import dataclass

# ── Topic Feeds ──────────────────────────────────────────────────
TOPIC_FEEDS = {
    "Sports": {
        "TOI Sports":   "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
        "TOI Cricket":  "https://timesofindia.indiatimes.com/rssfeeds/54829575.cms",
    },
    "Technology": {
        "TOI Gadgets":  "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",
        "TOI Science":  "https://timesofindia.indiatimes.com/rssfeeds/-2128672765.cms",
    },
    "Business": {
        "TOI Business": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms?x=1",
    },
    "Entertainment": {
        "TOI Entertainment": "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms?x=1",
        "TOI Life & Style":  "https://timesofindia.indiatimes.com/rssfeeds/2886704.cms",
    },
    "World": {
        "TOI World":   "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    },
    "India": {
        "TOI India":   "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    },
    "Environment": {
        "TOI Environment": "https://timesofindia.indiatimes.com/rssfeeds/2647163.cms",
    },
}

# ── City Feeds ───────────────────────────────────────────────────
CITY_FEEDS = {
    "Mumbai": {
        "HT Mumbai":    "https://www.hindustantimes.com/feeds/rss/cities/mumbai-news/rssfeed.xml",
        "DNA Mumbai":   "https://www.dnaindia.com/feeds/mumbai.xml",
    },
    "Delhi": {
        "HT Delhi":     "https://www.hindustantimes.com/feeds/rss/cities/delhi-news/rssfeed.xml",
        "DNA Delhi":    "https://www.dnaindia.com/feeds/delhi.xml",
    },
    "Bangalore": {
        "HT Bengaluru": "https://www.hindustantimes.com/feeds/rss/cities/bengaluru-news/rssfeed.xml",
    },
    "Hyderabad": {
        "Siasat":        "https://www.siasat.com/feed/",
        "Telangana Today": "https://telanganatoday.com/feed",
    },
    "Chennai": {
        "The Hindu Chennai": "https://www.thehindu.com/news/cities/Chennai/feeder/default.rss",
    },
    "Lucknow": {
        "HT Lucknow":   "https://www.hindustantimes.com/feeds/rss/cities/lucknow-news/rssfeed.xml",
    },
}

# ── Article dataclass ────────────────────────────────────────────
@dataclass
class Article:
    title: str
    description: str
    link: str
    source: str
    category: str = ""
    summary: str = ""
    is_regional: bool = False   # flag so UI can show a 📍 badge

def clean_html(text):
    return re.sub('<.*?>', '', text or "").strip()

# ── Fetch by selected topics ─────────────────────────────────────
def fetch_articles(selected_topics: list[str], city: str = None) -> list[Article]:
    articles = []

    # 1. Topic feeds
    for topic in selected_topics:
        feeds = TOPIC_FEEDS.get(topic, {})
        for source_name, url in feeds.items():
            articles.extend(_parse_feed(url, source_name, category=topic))

    # 2. City feed (nested dict now)
    if city and city in CITY_FEEDS:
        city_feeds = CITY_FEEDS[city]
        for source_name, url in city_feeds.items():
            articles.extend(_parse_feed(
                url,
                source_name=source_name,
                category="Regional",
                is_regional=True,
                limit=5   # fewer per source for city news
            ))

    return articles[:40]


def _parse_feed(url, source_name, category="", is_regional=False, limit=8):
    results = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            title = clean_html(entry.get("title", ""))
            description = clean_html(entry.get("summary", ""))
            link = entry.get("link", "")
            if not title or not link:
                continue
            results.append(Article(
                title=title,
                description=description[:300],
                link=link,
                source=source_name,
                category=category,
                is_regional=is_regional
            ))
    except Exception as e:
        print(f"⚠️  Failed to fetch {source_name}: {e}")
    return results
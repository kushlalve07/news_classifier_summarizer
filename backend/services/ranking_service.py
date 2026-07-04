def rank_articles(articles: list, preferred_topics: list) -> list:
    """
    Puts articles matching user's preferred topics first.
    Within each group, preserves original order (most recent first from RSS).
    """
    preferred = [a for a in articles if a.category in preferred_topics]
    others = [a for a in articles if a.category not in preferred_topics]
    return preferred + others
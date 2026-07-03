import streamlit as st
from services.rss_service import fetch_articles
from services.groq_service import process_articles
from services.ranking_service import rank_articles
from components.article_card import show_article_card

def show_feed(prefs: dict):
    topics = prefs["topics"]
    city = prefs.get("city")

    # ── Sidebar ──────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['username']}")
        st.divider()

        st.markdown("**Your topics:**")
        for t in topics:
            st.markdown(f"• {t}")

        if city:
            st.markdown(f"**📍 City:** {city}")

        st.divider()

        if st.button("⚙️ Edit preferences", use_container_width=True):
            from database.db import save_preferences
            save_preferences(
                st.session_state["user_id"], [], [], None
            )
            st.session_state.pop("articles", None)
            st.session_state.pop("onboarded", None)
            st.rerun()

        if st.button("🔄 Refresh feed", use_container_width=True):
            st.session_state.pop("articles", None)
            st.rerun()

    # ── Fetch + process (cached in session) ──────────────
    if "articles" not in st.session_state:
        with st.spinner("📡 Fetching articles from RSS feeds..."):
            articles = fetch_articles(topics, city)

        if not articles:
            st.warning("Couldn't fetch any articles. Check your internet connection.")
            return

        progress = st.progress(0, text="✍️ Summarizing articles with Groq...")
        total = len(articles)

        # Process one by one so user sees progress
        for i, article in enumerate(articles):
            from services.groq_service import classify_and_summarize
            import time
            category, summary = classify_and_summarize(article)
            article.category = category
            article.summary = summary
            progress.progress(
                (i + 1) / total,
                text=f"✍️ Summarizing {i+1}/{total} articles..."
            )
            time.sleep(0.5)

        progress.empty()

        # Rank by user preferences
        articles = rank_articles(articles, topics)
        st.session_state["articles"] = articles

    articles = st.session_state["articles"]

    # ── Header ────────────────────────────────────────────
    st.title("📰 Your Daily Brief")
    st.caption(f"{len(articles)} articles · personalised for you")
    st.divider()

    # ── Build tab list ────────────────────────────────────
    # Always show All first, then each category that has articles
    categories_present = list(dict.fromkeys(
        [a.category for a in articles]
    ))  # preserves order, removes duplicates

    if city:
        tab_names = ["All"] + categories_present
    else:
        tab_names = ["All"] + categories_present

    tabs = st.tabs(tab_names)

    # All tab
    with tabs[0]:
        if not articles:
            st.info("No articles found.")
        for article in articles:
            show_article_card(article)

    # Per-category tabs
    for i, category in enumerate(categories_present):
        with tabs[i + 1]:
            filtered = [a for a in articles if a.category == category]
            if not filtered:
                st.info(f"No {category} articles found.")
            for article in filtered:
                show_article_card(article)
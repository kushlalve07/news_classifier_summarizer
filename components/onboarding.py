import streamlit as st
from database.db import save_preferences
from services.rss_service import TOPIC_FEEDS, CITY_FEEDS

def show_onboarding(user_id: int):
    st.title("👋 Welcome! Let's personalise your feed.")
    st.write("Pick your interests and we'll curate your daily brief.")

    st.subheader("📌 Topics you care about")
    available_topics = list(TOPIC_FEEDS.keys())
    selected_topics = []
    
    # Show topics as a clean grid of checkboxes
    cols = st.columns(3)
    for i, topic in enumerate(available_topics):
        with cols[i % 3]:
            if st.checkbox(topic, value=True):
                selected_topics.append(topic)

    st.subheader("🏙️ Your city (for local news)")
    city_options = ["None"] + list(CITY_FEEDS.keys())
    selected_city = st.selectbox(
        "Select your city",
        options=city_options,
        index=0
    )
    city = None if selected_city == "None" else selected_city

    st.divider()

    if st.button("🚀 Build my feed", type="primary", use_container_width=True):
        if not selected_topics:
            st.error("Please select at least one topic.")
            return

        save_preferences(
            user_id=user_id,
            topics=selected_topics,
            sources=[],   # reserved for future per-source filtering
            city=city
        )
        st.session_state["onboarded"] = True
        st.success("Preferences saved! Loading your feed...")
        st.rerun()
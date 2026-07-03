import streamlit as st
from database.db import create_tables, get_user, create_user, get_preferences

# ── Page config (must be first Streamlit call) ────────
st.set_page_config(
    page_title="My Daily Brief",
    page_icon="📰",
    layout="wide"
)

# ── Init DB ───────────────────────────────────────────
create_tables()

# ── Login screen ──────────────────────────────────────
if "user_id" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📰 My Daily Brief")
        st.write("Your personalised Indian news feed, powered by AI.")
        st.divider()

        username = st.text_input(
            "Enter your name to get started",
            placeholder="e.g. Kushal"
        )

        if st.button("Continue →", type="primary", use_container_width=True):
            if not username.strip():
                st.error("Please enter your name.")
            else:
                user = get_user(username.strip())
                if not user:
                    user_id = create_user(username.strip())
                else:
                    user_id = user[0]
                st.session_state["user_id"] = user_id
                st.session_state["username"] = username.strip()
                st.rerun()

# ── Main app ──────────────────────────────────────────
else:
    prefs = get_preferences(st.session_state["user_id"])

    if not prefs or not prefs.get("topics"):
        from components.onboarding import show_onboarding
        show_onboarding(st.session_state["user_id"])
    else:
        from components.feed import show_feed
        show_feed(prefs)
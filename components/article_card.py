import streamlit as st

def show_article_card(article):
    with st.container(border=True):
        # Top row: source badge + regional tag
        col1, col2 = st.columns([5, 1])
        with col1:
            badges = f"`{article.source}` &nbsp; `{article.category}`"
            if article.is_regional:
                badges += " &nbsp; 📍 Local"
            st.markdown(badges)
        with col2:
            st.link_button("Read →", article.link, use_container_width=True)

        # Title
        st.markdown(f"**{article.title}**")

        # Groq summary
        if article.summary:
            st.caption(article.summary)
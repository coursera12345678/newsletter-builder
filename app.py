import streamlit as st
from openai import OpenAI
from newspaper import Article

# --- Streamlit App Header ---
st.set_page_config(page_title="📰 Auto Newsletter Generator")
st.title("📰 Auto Newsletter Generator")
st.caption("Paste 2–3 article links from the same site to generate a newsletter")

# --- OpenAI Client ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Input ---
urls_input = st.text_area("Paste article URLs (one per line)")

if st.button("Generate Newsletter") and urls_input:
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
    summaries = []

    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()

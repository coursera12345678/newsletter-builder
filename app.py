import streamlit as st
import requests
from bs4 import BeautifulSoup

# Read Gemini API key from Streamlit secrets
API_KEY = st.secrets["GEMINI_API_KEY"]
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={API_KEY}"


def get_article_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text() for p in paragraphs)
        return text[:2000]  # Limit to 2000 chars
    except Exception:
        return None

def get_gemini_summary(text):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Summarize this article like it's a newsletter section. Make it clear and engaging: {text}"}
                ]
            }
        ]
    }
    try:
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"⚠️ Error generating summary: {str(e)}"

def main():
    st.title("📰 Auto Newsletter Generator with Gemini + Streamlit")
    st.write("Paste article URLs below (one per line), then click **Summarize**.")

    urls_text = st.text_area("Article URLs", height=150)

    if st.button("Summarize"):
        if not urls_text.strip():
            st.error("Please enter at least one URL.")
            return

        urls = [url.strip() for url in urls_text.strip().split("\n") if url.strip()]
        summaries = []

        for url in urls:
            st.write(f"🔍 Fetching article from: {url}")
            article_text = get_article_text(url)
            if not article_text:
                st.warning(f"⚠️ Could not fetch or parse the article: {url}")
                summaries.append("⚠️ Failed to fetch article text.")
                continue

            st.write("✍️ Generating summary...")
            summary = get_gemini_summary(article_text)
            summaries.append(summary)

        st.header("📄 Summaries")
        for i, summary in enumerate(summaries, start=1):
            st.subheader(f"Article {i}")
            st.write(summary)

if __name__ == "__main__":
    main()

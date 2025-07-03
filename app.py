import streamlit as st
import requests
from newspaper import Article

st.set_page_config(page_title="📰 Auto Newsletter Generator")
st.title("📰 Auto Newsletter Generator")
st.caption("Paste 2–3 article links from the same site to generate a newsletter")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# User input
urls_input = st.text_area("Paste article URLs (one per line)")

def generate_summary(text, title):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""Summarize this article like it's for a tech newsletter. Make it 2–4 sentences, clear and punchy.

Title: {title}

Text:
{text[:1500]}... (truncated)
"""

    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"❌ Gemini API Error: {response.json()}"

if st.button("Generate Newsletter") and urls_input:
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
    summaries = []

    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()

            summary = generate_summary(article.text, article.title)
            summaries.append(f"**{article.title}**\n\n{summary}\n\n🔗 [Read more]({url})")

        except Exception as e:
            st.warning(f"Could not process {url}: {e}")

    st.markdown("## 🧾 Final Newsletter")

    if summaries:
        st.subheader("Top Story")
        st.write(summaries[0])

        if len(summaries) > 1:
            st.subheader("Other Stories")
            for story in summaries[1:]:
                st.write(story)
    else:
        st.error("No stories could be generated. Please check your URLs.")

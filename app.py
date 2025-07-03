import os
import openai
import requests
from bs4 import BeautifulSoup
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Newsletter Builder", layout="centered")
st.title("📰 Auto Newsletter Generator")
st.write("Paste 2–3 article links from the same site to generate a newsletter")

urls = st.text_area("Paste article URLs (one per line)").strip().split("\n")

def extract_text_from_url(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text() for p in paragraphs])
        return soup.title.string if soup.title else "Untitled", text
    except Exception as e:
        return "Error", f"Failed to extract from {url}: {e}"

if st.button("Generate Newsletter") and urls:
    stories = []

    for url in urls:
        title, content = extract_text_from_url(url)
        if content.startswith("Failed"):
            st.error(content)
            continue

        prompt = f"Summarize this article in 3–4 sentences, keeping the tone neutral and professional:\n\n{content}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )
            summary = response.choices[0].message.content.strip()
        except Exception as e:
            summary = f"Error calling OpenAI: {e}"

        stories.append({"title": title, "summary": summary, "url": url})

    if stories:
        st.subheader("🧾 Final Newsletter")

        main_story = stories[0]
        other

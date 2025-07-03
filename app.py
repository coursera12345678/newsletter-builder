import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="📰 Auto Newsletter Generator")
st.title("📰 Auto Newsletter Generator")
st.caption("Paste 2–3 article links from the same site to generate a newsletter")

# Use new OpenAI SDK
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extract_article_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text() for p in paragraphs)
        return text[:3000]  # Truncate to avoid token limit
    except Exception as e:
        return None

urls_input = st.text_area("Paste article URLs (one per line)")

if st.button("Generate Newsletter") and urls_input:
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
    summaries = []

    for url in urls:
        article_text = extract_article_text(url)
        if not article_text:
            st.warning(f"❌ Couldn't extract text from {url}")
            continue

        prompt = f"""
You're writing for a tech newsletter. Summarize the following article clearly and concisely in 2–4 sentences. Make it snappy, smart, and useful to a reader who skims.

Article:
{article_text}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You're a newsletter writer."},
                    {"role": "user", "content": prompt}
                ]
            )
            summary = f"🔹 **Summary** for [{url}]({url}):\n\n{response.choices[0].message.content.strip()}"
            summaries.append(summary)

        except Exception as e:
            st.warning(f"⚠️ OpenAI failed on {url}:\n{e}")

    if summaries:
        st.markdown("## 🧾 Final Newsletter")
        for s in summaries:
            st.markdown(s)
    else:
        st.error("No summaries generated. Please check your URLs and try again.")

import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="📰 Auto Newsletter Generator", layout="centered")
st.title("📰 Auto Newsletter Generator")
st.caption("Paste 2–3 article links from the same site to generate a styled newsletter.")

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Input
urls_input = st.text_area("Paste article URLs (one per line)")

def fetch_article_text(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        paragraphs = soup.find_all('p')
        return ' '.join([p.get_text() for p in paragraphs])
    except Exception as e:
        return f"Error fetching article: {e}"

def summarize_with_groq(title, content):
    prompt = f"""
You are a copywriter writing a newsletter. Summarize this article in 2–4 sentences in a clear, engaging, and informative tone.

Title: {title}

Content:
{content[:1500]}...(truncated)
"""
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "system", "content": "You write concise tech newsletter summaries."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
    )

    data = response.json()
    return data['choices'][0]['message']['content'].strip()

if st.button("Generate Newsletter") and urls_input:
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
    summaries = []

    for url in urls:
        article_text = fetch_article_text(url)
        title = url.split("/")[-1].replace("-", " ").title()
        summary = summarize_with_groq(title, article_text)
        summaries.append((title, summary, url))

    # Output like MailerLite style
    st.markdown("---")
    st.markdown("<h2 style='font-family:sans-serif;color:#111;'>🧾 Weekly Digest</h2>", unsafe_allow_html=True)

    for title, summary, link in summaries:
        st.markdown(f"""
        <div style='background-color:#f9f9f9;padding:20px;border-radius:10px;margin-bottom:20px;'>
            <h3 style='color:#222;margin-bottom:10px;'>{title}</h3>
            <p style='color:#444;font-size:16px;line-height:1.6;'>{summary}</p>
            <a href='{link}' style='color:#0066cc;text-decoration:none;'>Read more →</a>
        </div>
        """, unsafe_allow_html=True)

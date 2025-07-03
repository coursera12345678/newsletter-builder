import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="📰 Auto Newsletter Generator")
st.title("📰 Auto Newsletter Generator")
st.caption("Paste 2–3 article links from the same site to generate a newsletter")

openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to extract meaningful text
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
        else:
            paragraphs = soup.find_all('p')

        text = ' '.join([p.get_text() for p in paragraphs])
        return text.strip()
    except Exception as e:
        return f"Error fetching {url}: {e}"

urls_input = st.text_area("Paste article URLs (one per line)")

if st.button("Generate Newsletter") and urls_input:
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
    summaries = []

    for url in urls:
        content = extract_text_from_url(url)
        if content.startswith("Error"):
            st.warning(content)
            continue

        prompt = f"""
You're an assistant helping write a newsletter. Summarize the following article in a clear, engaging, and concise way as if it's a section in a tech newsletter. Make it informative but punchy, in 2–4 sentences:

Article text:
{content[:2000]}... (truncated)
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write newsletter content."},
                    {"role": "user", "content": prompt},
                ]
            )
            summary = response['choices'][0]['message']['content'].strip()
            summaries.append(f"**{url}**\n\n{summary}\n\n🔗 [Read more]({url})")
        except Exception as e:
            st.error(f"OpenAI failed on {url}: {e}")

    # Show newsletter
    st.markdown("## 🧾 Final Newsletter")
    if summaries:
        st.subheader("Top Story")
        st.write(summaries[0])

        if len(summaries) > 1:
            st.subheader("Other Stories")
            for story in summaries[1:]:
                st.write(story)

        st.subheader("⚡ Quick Reads")
        st.write("- Add a few one-liner updates here.")

        st.subheader("📚 Recommended Reads")
        st.write("- Add some deep dives or essays here.")
    else:
        st.error("No summaries generated. Please try again.")

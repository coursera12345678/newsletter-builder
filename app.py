import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

# Set up page
st.set_page_config(page_title="📰 Auto Newsletter Generator")
st.title("📰 Auto Newsletter Generator")
st.caption("Paste 2–3 article links from the same site to generate a newsletter")

# Load OpenAI key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Input
urls_input = st.text_area("Paste article URLs (one per line)")

def fetch_article_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title and paragraphs
        title = soup.title.string if soup.title else "Untitled"
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text() for p in paragraphs])
        return title.strip(), content.strip()
    except Exception as e:
        return None, f"Error fetching article: {e}"

if st.button("Generate Newsletter") and urls_input:
    urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
    summaries = []

    for url in urls:
        title, article_text = fetch_article_text(url)

        if not title or not article_text or "Error" in article_text:
            st.warning(f"Could not process {url}: {article_text}")
            continue

        prompt = f"""
You are an assistant helping write a newsletter. Summarize the following article in a clear, engaging, and concise way as if it's a section in a tech newsletter. Make it informative but punchy, in 2–4 sentences.

Title: {title}

Text: {article_text[:1500]}... (truncated)
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You write newsletter content."},
                    {"role": "user", "content": prompt}
                ]
            )

            summary = f"**{title}**\n\n{response.choices[0].message.content.strip()}\n\n🔗 [Read more]({url})"
            summaries.append(summary)
        except Exception as e:
            st.error(f"OpenAI failed on {url}: {e}")

    # Render newsletter
    st.markdown("## 🧾 Final Newsletter")

    if summaries:
        st.subheader("Top Story")
        st.write(summaries[0])

        if len(summaries) > 1:
            st.subheader("Other Stories")
            for story in summaries[1:]:
                st.write(story)

        st.subheader("⚡ Quick Reads")
        st.write("- Add a few one-liner news bits or updates here.")

        st.subheader("📚 Recommended Reads")
        st.write("- Link out to opinion pieces or deep dives relevant to your audience.")
    else:
        st.error("No summaries generated. Please try again.")

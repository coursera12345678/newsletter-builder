import os
import openai
import streamlit as st
from newspaper import Article

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Newsletter Builder", layout="centered")
st.title("📰 Auto Newsletter Generator")
st.write("Paste 2–3 article links from the same site to generate a newsletter")

urls = st.text_area("Paste article URLs (one per line)").strip().split("\n")

if st.button("Generate Newsletter") and urls:
    stories = []

    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            content = article.text

            prompt = f"Summarize this article in 3–4 sentences, keeping the tone neutral and professional:\n\n{content}"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )
            summary = response.choices[0].message.content.strip()

            stories.append({"title": article.title, "summary": summary, "url": url})

        except Exception as e:
            st.error(f"Error processing {url}: {e}")

    if stories:
        st.subheader("🧾 Final Newsletter")

        main_story = stories[0]
        other_stories = stories[1:]

        newsletter = f"## 📰 Main Story\n**{main_story['title']}**\n{main_story['summary']}\n[Read more]({main_story['url']})\n\n"

        if other_stories:
            newsletter += "## ✨ Other Stories\n"
            for s in other_stories:
                newsletter += f"- **{s['title']}**: {s['summary']} [Read]({s['url']})\n"

        newsletter += "\n## ⚡ Quick Reads\n(Add short links or headlines here.)\n\n"
        newsletter += "## 📚 Recommended Reads\n(Add evergreen/editorial picks.)"

        st.code(newsletter, language="markdown")

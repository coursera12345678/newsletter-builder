import streamlit as st
import openai
from newspaper import Article

st.set_page_config(page_title="📰 Auto Newsletter Generator")
st.title("📰 Auto Newsletter Generator")
st.caption("Paste 2–3 article links from the same site to generate a newsletter")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# User input
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

            prompt = f"""
You are an assistant helping write a newsletter. Summarize the following article in a clear, engaging, and concise way as if it's a section in a tech newsletter. Make it informative but punchy, in 2–4 sentences:

Title: {article.title}

Text:
{article.text[:1500]}... (truncated)
"""
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You write newsletter content."},
                    {"role": "user", "content": prompt},
                ]
            )

            summary = f"**{article.title}**\n\n{response['choices'][0]['message']['content'].strip()}\n\n🔗 [Read more]({url})"
            summaries.append(summary)

        except Exception as e:
            st.warning(f"Could not process {url}: {e}")

    # Render Newsletter
    st.markdown("## 🧾 Final Newsletter")

    if summaries:
        main = summaries[0]
        st.subheader("Top Story")
        st.write(main)

        if len(summaries) > 1:
            other = summaries[1:]
            st.subheader("Other Stories")
            for story in other:
                st.write(story)

        st.subheader("⚡ Quick Reads")
        st.write("- Add a few one-liner news bits or updates here.")

        st.subheader("📚 Recommended Reads")
        st.write("- Link out to opinion pieces or deep dives relevant to your audience.")
    else:
        st.error("No stories could be generated. Please check your URLs.")

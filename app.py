import streamlit as st
from google import genai

st.set_page_config(page_title="Parul Uni Comment Generator", page_icon="🎓")

st.title("🎓 Parul University Comment Generator")

# Initialize Gemini Client
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("⚠️ Please add your GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# Caption Input
caption = st.text_area("Paste Instagram Post Caption Here:", height=150, placeholder="Paste caption from the Instagram Reel/Post...")

# Tone Selector
tone = st.selectbox("Select Page Vibe:", [
    "General Parul Uni Student Mix (Hyped, Curious, Funny, Proud)",
    "Outreach / Gen-Z (Casual, Slang, Tagging Friends)",
    "Radio Live / Event Stream (Interactive Questions & Hype)",
    "Official Campus Highlight (Proud & Supportive)"
])

if st.button("⚡ Generate 30 Comments", type="primary", use_container_width=True):
    if not caption.strip():
        st.warning("Please paste a caption first!")
    else:
        with st.spinner("Generating 30 phone-typed student comments..."):
            prompt = f"""
            You are generating 30 realistic Instagram comments from real college students at Parul University.
            
            Vibe/Tone Context: {tone}
            Post Caption: {caption}

            Generate exactly 30 Instagram comments.

            STRICT REQUIREMENTS:
            1. Make comments feel completely human, casual, and typed quickly on a phone.
            2. Use lowercase starts, light slang, and natural imperfections.
            3. Mix perspectives: hyped/excited, proud, curious, funny/sarcastic, wholesome, alumni nostalgic, and low-energy.
            4. Vary lengths: 1-3 words, single lines, and 2-line maximums.
            5. Occasionally tag casual friends (e.g., @rohit, @priya, @amit).
            6. Use emojis naturally without overdoing them.

            Output strictly a numbered list from 1 to 30.
            """
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                st.subheader("🎉 Generated Comments")
                st.write(response.text)
            except Exception as err:
                st.error(f"Error: {err}")

import streamlit as st
import instaloader
from google import genai

# Page Config
st.set_page_config(
    page_title="Parul Uni Comment Generator",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Parul University Instagram Comment Generator")
st.caption("Automatically pull public captions from @paruluniversity or paste them manually to generate 30 distinct student comments.")

# Initialize Gemini Client from Streamlit Secrets
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("⚠️ Please configure your GEMINI_API_KEY in Streamlit Cloud Secrets.")
    st.stop()

# Mode Selection
mode = st.radio("Choose Caption Source:", ["Fetch Public Page (@paruluniversity)", "Paste Caption Manually"], horizontal=True)

selected_caption = ""

# Mode A: Fetch Public IG Feed
if mode == "Fetch Public Page (@paruluniversity)":
    col1, col2 = st.columns([3, 1])
    with col1:
        target_handle = st.text_input("Instagram Handle:", value="paruluniversity")
    with col2:
        st.write(" ")
        fetch_btn = st.button("🔍 Fetch Recent Posts")

    if fetch_btn and target_handle:
        with st.spinner(f"Scraping latest posts from @{target_handle}..."):
            try:
                L = instaloader.Instaloader(
                    download_pictures=False,
                    download_videos=False,
                    download_comments=False,
                    save_metadata=False
                )
                profile = instaloader.Profile.from_username(L.context, target_handle)
                
                posts_data = []
                for idx, post in enumerate(profile.get_posts()):
                    if idx >= 5: # Fetch top 5 recent posts
                        break
                    posts_data.append({
                        "caption": post.caption or "No caption provided",
                        "date": str(post.date_utc)[:10],
                        "url": f"https://www.instagram.com/p/{post.shortcode}/"
                    })
                
                st.session_state["pulled_posts"] = posts_data
                st.success(f"Fetched 5 latest posts from @{target_handle}!")
            except Exception as e:
                st.error("Instagram rate-limited or blocked direct scraping. Please use the 'Paste Caption Manually' tab above.")

    if "pulled_posts" in st.session_state:
        st.write("### Select a Post:")
        for idx, post in enumerate(st.session_state["pulled_posts"]):
            with st.container(border=True):
                st.markdown(f"**Posted on:** {post['date']} | [View Post on Instagram]({post['url']})")
                st.text_area("Caption:", value=post['caption'], height=80, key=f"cap_{idx}", disabled=True)
                if st.button("Use This Caption", key=f"btn_{idx}"):
                    st.session_state["active_cap"] = post['caption']

    if "active_cap" in st.session_state:
        selected_caption = st.session_state["active_cap"]
        st.info(f"**Selected Caption:** {selected_caption[:120]}...")

# Mode B: Manual Paste
else:
    selected_caption = st.text_area("Paste Post Caption Here:", height=150, placeholder="Paste the caption from the Instagram Reel/Post here...")

# Tone Selection & Generation
st.divider()

col_tone, col_out = st.columns([2, 1])
with col_tone:
    tone_preset = st.selectbox("Select Page Vibe / Tone:", [
        "General Parul Uni Student Mix (Hyped, Curious, Funny, Proud)",
        "Outreach / Gen-Z (Casual, Slang, Tagging Friends, High Energy)",
        "Radio Live / Event Stream (Interactive Questions & Hype)",
        "Official Campus Highlight (Proud & Supportive)"
    ])

if st.button("⚡ Generate 30 Comments", type="primary", use_container_width=True):
    if not selected_caption.strip():
        st.warning("Please fetch/select a post or paste a caption first!")
    else:
        with st.spinner("Generating 30 realistic phone-typed student comments..."):
            prompt = f"""
            You are generating 30 realistic Instagram comments from real college students at Parul University.
            
            Vibe/Tone Context: {tone_preset}
            Post Caption: {selected_caption}

            Generate exactly 30 Instagram comments.

            STRICT REQUIREMENTS:
            1. Make comments feel completely human, casual, and typed quickly on a phone.
            2. Use lowercase starts, light slang, and natural imperfections.
            3. Mix perspectives: hyped/excited, proud, curious, funny/sarcastic, wholesome, alumni nostalgic, and low-energy reactions.
            4. Vary lengths: 1-3 words, single lines, and 2-line maximums.
            5. Occasionally tag casual friends (e.g., @rohit, @priya, @amit).
            6. Use emojis naturally without overdoing them.
            7. Avoid formal language, promotional tones, or AI clichés.

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
                st.error(f"Error generating comments: {err}")

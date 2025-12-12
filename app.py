import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

st.set_page_config(page_title="Gemini YouTube Summarizer", page_icon="♊")

st.title("♊ Gemini YouTube Summarizer")
st.write("Paste a YouTube link below to get a concise summary.")

# --- NEW SECTION: GET THE SECRET KEY ---
try:
    # This looks for the key in the "Secrets" safe we just set up
    api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    # If running locally (on your PC) without a secrets file, asking manually
    api_key = st.sidebar.text_input("Enter your Google Gemini API Key", type="password")
# ---------------------------------------

def get_transcript(youtube_url):
    try:
        video_id = youtube_url.split("v=")[1].split("&")[0]
        # This is the line that was breaking. 
        # By ensuring requirements.txt is correct, this should work now.
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        return f"Error: {str(e)}"

def summarize_with_gemini(text, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "Summarize this YouTube video transcript into 5 bullet points:\n\n" + text
    response = model.generate_content(prompt)
    return response.text

youtube_link = st.text_input("YouTube Video URL:")

if st.button("Get Summary"):
    if youtube_link:
        with st.spinner("Loading..."):
            transcript = get_transcript(youtube_link)
            
            if "Error:" in transcript:
                st.error(transcript)
            else:
                summary = summarize_with_gemini(transcript, api_key)
                st.subheader("Summary:")
                st.write(summary)

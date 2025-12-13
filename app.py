import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

st.set_page_config(page_title="Gemini YouTube Summarizer", page_icon="♊")

st.title("♊ Gemini YouTube Summarizer")
st.write("Paste a YouTube link below to get a concise summary.")

# Securely get the API key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("🚨 API Key is missing! Please set GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

def get_transcript(youtube_url):
    try:
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in youtube_url:
            video_id = youtube_url.split("/")[-1]
        else:
            return "Error: Invalid YouTube URL"
            
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        return f"Error: {str(e)}"

def summarize_with_gemini(text, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = "Summarize this YouTube video transcript into 5 concise bullet points:\n\n" + text
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"

youtube_link = st.text_input("YouTube Video URL:")

if st.button("Get Summary"):
    if youtube_link:
        with st.spinner("⏳ Downloading transcript & thinking..."):
            transcript = get_transcript(youtube_link)
            
            if "Error:" in transcript:
                st.error(transcript)
            else:
                summary = summarize_with_gemini(transcript, api_key)
                st.subheader("Summary:")
                st.markdown(summary)

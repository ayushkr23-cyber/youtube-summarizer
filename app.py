import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# 1. SETUP PAGE CONFIGURATION
st.set_page_config(page_title="Gemini YouTube Summarizer", page_icon="♊")

# 2. TITLE AND HEADER
st.title("♊ Gemini YouTube Summarizer")
st.write("Paste a YouTube link below to get a concise summary using Google Gemini.")

# 3. SIDEBAR FOR API KEY
api_key = st.sidebar.text_input("Enter your Google Gemini API Key", type="password")

# 4. FUNCTION TO EXTRACT TRANSCRIPT
def get_transcript(youtube_url):
    try:
        if "v=" not in youtube_url:
            return "Error: Invalid YouTube URL format."
            
        video_id = youtube_url.split("v=")[1].split("&")[0]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        return f"Error: Could not retrieve transcript. ({str(e)})"

# 5. FUNCTION TO SUMMARIZE TEXT (USING GEMINI)
def summarize_with_gemini(text, api_key):
    if not api_key:
        return "Please enter your API Key in the sidebar."
    
    # Configure the Gemini API
    genai.configure(api_key=AIzaSyAPTlbFkXLOzSA-x58n-EeYp5K33iKadDM)
    
    try:
        # Use Gemini 1.5 Flash (Fast and efficient for text)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create the prompt
        prompt = (
            "You are a helpful assistant. Summarize the following YouTube video transcript "
            "into 5 concise bullet points with a brief intro sentence:\n\n" + text
        )
        
        # Generate content
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to Google Gemini: {str(e)}"

# 6. THE USER INTERFACE LOGIC
youtube_link = st.text_input("YouTube Video URL:")

if st.button("Get Summary"):
    if youtube_link and "youtube.com" in youtube_link:
        with st.spinner("Extracting transcript..."):
            transcript = get_transcript(youtube_link)
        
        if "Error" in transcript:
            st.error(transcript)
        else:
            with st.spinner("Asking Gemini to summarize..."):
                summary = summarize_with_gemini(transcript, api_key)
                
                st.subheader("📝 Summary:")
                st.markdown(summary)
                
                with st.expander("View Full Transcript"):
                    st.write(transcript)
    else:
        st.warning("Please enter a valid YouTube URL (must contain 'youtube.com').")
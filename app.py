import streamlit as st
import yt_dlp
import os
import time
from faster_whisper import WhisperModel

st.set_page_config(page_title="Ultimate Turbo Transcriber", page_icon="⚡")

# --- SIDEBAR: TURBO SETTINGS ---
st.sidebar.header("⚡ Turbo Engine Settings")
model_size = st.sidebar.select_slider(
    "AI Brain Size (for Plan B)",
    options=["tiny", "base", "small", "medium"],
    value="tiny"
)
st.sidebar.info("Tip: 'tiny' is fastest. 'small' is smarter.")

# --- 1. SETUP: LOAD TURBO MODEL ---
@st.cache_resource
def load_turbo_model(size):
    print(f"⏳ Loading {size} Turbo Model...")
    # int8 quantization makes it run 4x faster on CPU
    return WhisperModel(size, device="cpu", compute_type="int8")

# --- 2. PLAN A: THE SMART WAY (Scraping) ---
def download_captions_smart(url):
    output_filename = "smart_subs"
    ydl_opts = {
        'skip_download': True,
        'writeautomaticsub': True,
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'outtmpl': output_filename,
        'quiet': True,
        'nocheckcertificate': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        for file in os.listdir("."):
            if file.startswith("smart_subs") and file.endswith(".vtt"):
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Clean VTT format
                lines = content.splitlines()
                clean_text = []
                for line in lines:
                    if "-->" not in line and line.strip() and not line.startswith("WEBVTT"):
                        clean_text.append(line)
                
                os.remove(file)
                # Remove duplicates nicely
                final_text = " ".join(dict.fromkeys(clean_text)) 
                return final_text
                
    except Exception as e:
        print(f"Smart fetch failed: {e}")
        return None
    return None

# --- 3. PLAN B: THE TURBO WAY (Local AI) ---
def download_audio_hq(url):
    output_filename = "temp_audio"
    # We use High Quality (192kbps) because we don't have file size limits locally
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'outtmpl': output_filename,
        'quiet': True,
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_filename + ".mp3"

# --- MAIN APP ---
st.title("⚡ Ultimate Turbo Transcriber")
st.markdown("Attempts **Plan A** (Instant Fetch). If that fails, uses **Plan B** (Local Turbo AI).")

url = st.text_input("Paste YouTube Link:")

if url:
    if st.button("Get Transcript", type="primary"):
        status = st.empty()
        
        # --- EXECUTE PLAN A ---
        status.info("⚡ Plan A: Checking for official captions...")
        transcript = download_captions_smart(url)
        
        if transcript:
            status.success("✅ Plan A Success! (Instant Fetch)")
            st.text_area("Transcript:", transcript, height=350)
            st.download_button("Download", transcript, file_name="transcript_smart.txt")
        else:
            # --- EXECUTE PLAN B ---
            status.warning("⚠️ Plan A failed (No captions). Switching to Plan B: Turbo AI...")
            time.sleep(1)
            
            try:
                # 1. Download
                status.info("⬇️ Plan B: Downloading Audio...")
                audio_file = download_audio_hq(url)
                
                # 2. Load Model
                status.info(f"🧠 Plan B: Revving up '{model_size}' engine...")
                model = load_turbo_model(model_size)
                
                # 3. Transcribe
                status.info("⚡ Plan B: Transcribing (This runs locally)...")
                segments, info = model.transcribe(audio_file, beam_size=5)
                
                # Loop to show progress
                full_text = ""
                count = 0
                progress_bar = st.progress(0)
                
                for segment in segments:
                    full_text += segment.text + " "
                    count += 1
                    if count % 10 == 0:
                        status.text(f"⚡ Transcribed {int(segment.end)} seconds of audio...")
                
                progress_bar.progress(100)
                
                status.success(f"✅ Plan B Success! (Language: {info.language.upper()})")
                st.text_area("Transcript:", full_text, height=350)
                st.download_button("Download", full_text, file_name="transcript_turbo.txt")
                
                os.remove(audio_file)
                
            except Exception as e:
                status.error(f"❌ Error: {e}")

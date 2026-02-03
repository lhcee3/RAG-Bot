import streamlit as st
import google.generativeai as genai
import os
import time
from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Google Veo 3 Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'api_key_validated' not in st.session_state:
    st.session_state.api_key_validated = False
if 'generated_videos' not in st.session_state:
    st.session_state.generated_videos = []

# Create output directory
OUTPUT_DIR = Path("generated_videos")
OUTPUT_DIR.mkdir(exist_ok=True)

def validate_api_key(api_key):
    """Validate the Google API key"""
    try:
        genai.configure(api_key=api_key)
        # Try to list models to verify the key works
        models = genai.list_models()
        return True
    except Exception as e:
        return False

def generate_video(prompt, api_key, aspect_ratio="16:9", duration=5):
    """Generate video using Veo 3"""
    try:
        genai.configure(api_key=api_key)
        
        # Generate video
        model = genai.GenerativeModel('veo-001')
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'aspect_ratio': aspect_ratio,
                'duration': duration
            }
        )
        
        # Save video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = OUTPUT_DIR / f"video_{timestamp}.mp4"
        
        with open(video_path, 'wb') as f:
            f.write(response.video_data)
        
        return str(video_path), None
    except Exception as e:
        return None, str(e)

# Main UI
st.title("Google Veo 3 Video Generator")
st.write("Generate AI videos using Google's Veo 3 model")

# Sidebar for API key and settings
with st.sidebar:
    st.header("Configuration")
    
    # API Key input
    api_key = st.text_input("Google API Key", type="password", 
                            help="Enter your Google API key with Veo 3 access")
    
    if st.button("Validate API Key"):
        if api_key:
            with st.spinner("Validating..."):
                if validate_api_key(api_key):
                    st.session_state.api_key_validated = True
                    st.success("API Key validated successfully")
                else:
                    st.session_state.api_key_validated = False
                    st.error("Invalid API Key or no Veo 3 access")
        else:
            st.warning("Please enter an API key")
    
    if st.session_state.api_key_validated:
        st.success("API Key is valid")
    
    st.divider()
    
    # Video settings
    st.header("Video Settings")
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["16:9", "9:16", "1:1"],
        help="Select the aspect ratio for your video"
    )
    
    duration = st.slider(
        "Duration (seconds)",
        min_value=2,
        max_value=10,
        value=5,
        help="Video duration in seconds"
    )

# Main content area
if not st.session_state.api_key_validated:
    st.info("Please enter and validate your API key in the sidebar to get started")
else:
    # Video generation interface
    st.header("Generate Video")
    
    prompt = st.text_area(
        "Video Prompt",
        height=100,
        placeholder="Describe the video you want to generate...\nExample: A serene sunset over a calm ocean, with gentle waves reflecting golden light, cinematic quality",
        help="Be descriptive about scene elements, style, lighting, camera movement, and mood"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        generate_btn = st.button("Generate Video", type="primary", use_container_width=True)
    
    if generate_btn:
        if not prompt:
            st.warning("Please enter a prompt")
        else:
            with st.spinner("Generating video... This may take a few minutes"):
                video_path, error = generate_video(prompt, api_key, aspect_ratio, duration)
                
                if video_path:
                    st.success("Video generated successfully")
                    st.session_state.generated_videos.append({
                        'path': video_path,
                        'prompt': prompt,
                        'timestamp': datetime.now()
                    })
                    
                    # Display video
                    st.video(video_path)
                    
                    # Download button
                    with open(video_path, 'rb') as f:
                        st.download_button(
                            label="Download Video",
                            data=f,
                            file_name=Path(video_path).name,
                            mime="video/mp4"
                        )
                else:
                    st.error(f"Failed to generate video: {error}")
    
    # Display previously generated videos
    if st.session_state.generated_videos:
        st.divider()
        st.header("Generated Videos")
        
        for idx, video in enumerate(reversed(st.session_state.generated_videos)):
            with st.expander(f"Video {len(st.session_state.generated_videos) - idx} - {video['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"**Prompt:** {video['prompt']}")
                st.video(video['path'])
                with open(video['path'], 'rb') as f:
                    st.download_button(
                        label="Download",
                        data=f,
                        file_name=Path(video['path']).name,
                        mime="video/mp4",
                        key=f"download_{idx}"
                    )

# Footer
st.divider()
st.markdown("""
### Tips for Better Videos
- Be descriptive with your prompts
- Include details about scene elements, style, lighting, camera movement, and mood
- Try different aspect ratios and durations
- Review example prompts in the README

### Example Prompts
- "A serene sunset over a calm ocean, with gentle waves reflecting golden light, cinematic quality"
- "Underwater scene of colorful coral reef with tropical fish swimming, 4K quality"
- "Time-lapse of a flower blooming in a garden, soft natural lighting"
""")

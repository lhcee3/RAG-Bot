import streamlit as st
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Google GenAI
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Veo 3 Video Generator",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .status-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_validated' not in st.session_state:
    st.session_state.api_validated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('GOOGLE_API_KEY', '')
if 'client' not in st.session_state:
    st.session_state.client = None
if 'generated_videos' not in st.session_state:
    st.session_state.generated_videos = []
if 'available_models' not in st.session_state:
    st.session_state.available_models = []
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = None


def validate_api_key(api_key: str) -> tuple[bool, str, list]:
    """Validate the Google API key by attempting to initialize the client."""
    if not api_key or len(api_key) < 10:
        return False, "API key is too short or empty.", []
    
    if not GENAI_AVAILABLE:
        return False, "Google GenAI library not installed. Run: pip install google-genai", []
    
    try:
        # Initialize the client with the API key
        client = genai.Client(api_key=api_key)
        
        # Try to list models to verify the API key works
        models = list(client.models.list())
        model_names = [m.name for m in models]
        
        # Look for Veo/video models
        video_models = [m for m in model_names if 'veo' in m.lower() or 'video' in m.lower()]
        
        st.session_state.client = client
        st.session_state.available_models = model_names
        
        if video_models:
            return True, f"API key validated! Found video models: {', '.join(video_models)}", video_models
        else:
            # Return all models for debugging
            return True, "API key validated! No Veo models found. You may need Veo access.", model_names
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            return False, "Invalid API key. Please check and try again.", []
        elif "permission" in error_msg.lower() or "denied" in error_msg.lower():
            return False, "API key doesn't have permission. Ensure you have access.", []
        else:
            return False, f"Validation error: {error_msg}", []


def generate_video(prompt: str, model_name: str, duration: int = 8, aspect_ratio: str = "16:9", resolution: str = "720p", negative_prompt: str = "") -> dict:
    """Generate a video using Google Veo API."""
    if not st.session_state.client:
        return {"success": False, "error": "Client not initialized"}
    
    try:
        client = st.session_state.client
        
        # Create output directory
        output_dir = Path("generated_videos")
        output_dir.mkdir(exist_ok=True)
        
        # Build config
        config_params = {
            "aspect_ratio": aspect_ratio,
            "duration_seconds": duration,
            "number_of_videos": 1,
        }
        
        # Add resolution for Veo 3.1
        if "3.1" in model_name:
            config_params["resolution"] = resolution
        
        # Add negative prompt if provided
        if negative_prompt:
            config_params["negative_prompt"] = negative_prompt
        
        config = types.GenerateVideosConfig(**config_params)
        
        # Try the video generation API
        try:
            operation = client.models.generate_videos(
                model=model_name,
                prompt=prompt,
                config=config,
            )
            
            # Poll for completion (video generation takes time)
            max_wait = 600  # 10 minutes max for video
            waited = 0
            while not operation.done and waited < max_wait:
                time.sleep(10)
                waited += 10
                operation = client.operations.get(operation)
            
            if not operation.done:
                return {"success": False, "error": "Video generation timed out after 10 minutes. Try again."}
            
            # Get the generated video
            if operation.response and operation.response.generated_videos:
                video = operation.response.generated_videos[0]
                
                timestamp = int(time.time())
                video_path = output_dir / f"video_{timestamp}.mp4"
                
                # Download and save the video
                client.files.download(file=video.video)
                video.video.save(str(video_path))
                
                return {
                    "success": True,
                    "video_path": str(video_path),
                    "prompt": prompt
                }
            else:
                return {"success": False, "error": "No video in response. Check your quota/credits."}
                
        except Exception as api_error:
            error_str = str(api_error)
            
            # Parse different error types
            if "NOT_FOUND" in error_str or "not found" in error_str.lower():
                return {
                    "success": False, 
                    "error": f"❌ Model '{model_name}' not found.\n\n"
                             f"**Your API key may not have Veo access yet.**\n"
                             f"Ask your manager to confirm Veo is enabled.\n\n"
                             f"**Raw error:** {error_str[:300]}"
                }
            elif "PERMISSION_DENIED" in error_str or "permission" in error_str.lower():
                return {
                    "success": False,
                    "error": f"❌ Permission denied for '{model_name}'.\n\n"
                             f"Your API key may not have Veo access.\n"
                             f"Ask your manager to verify the key has video generation enabled.\n\n"
                             f"**Raw error:** {error_str[:300]}"
                }
            elif "QUOTA" in error_str or "quota" in error_str.lower():
                return {
                    "success": False,
                    "error": f"❌ Quota exceeded.\n\nYour account has run out of video generation credits.\n\n"
                             f"**Raw error:** {error_str[:300]}"
                }
            elif "INVALID_ARGUMENT" in error_str:
                return {
                    "success": False,
                    "error": f"❌ Invalid request.\n\n"
                             f"The prompt or settings may be invalid.\n"
                             f"Try a simpler prompt.\n\n"
                             f"**Raw error:** {error_str[:300]}"
                }
            elif "SAFETY" in error_str or "safety" in error_str.lower() or "blocked" in error_str.lower():
                return {
                    "success": False,
                    "error": f"❌ Content blocked by safety filters.\n\n"
                             f"Try a different prompt that doesn't violate content policies.\n\n"
                             f"**Raw error:** {error_str[:300]}"
                }
            else:
                return {"success": False, "error": f"API Error: {error_str}"}
            
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def get_available_video_models() -> list:
    """Get list of available video generation models."""
    if not st.session_state.client:
        return []
    
    try:
        models = list(st.session_state.client.models.list())
        video_models = [m.name for m in models if 'veo' in m.name.lower() or 'video' in m.name.lower()]
        return video_models
    except:
        return []


def main():
    # Header
    st.markdown("<h1 class='main-header'>🎬 Google Veo 3 Video Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Generate AI videos using Google's Veo 3 model</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Check if GenAI is available
    if not GENAI_AVAILABLE:
        st.error("⚠️ Google GenAI library is not installed!")
        st.code("pip install google-genai", language="bash")
        st.stop()
    
    # Step 1: API Key Validation
    if not st.session_state.api_validated:
        st.markdown("### 🔑 Step 1: Enter Your API Key")
        st.markdown("Enter your Google AI API key to get started. You can get one from [Google AI Studio](https://aistudio.google.com/apikey).")
        
        with st.form("api_key_form"):
            api_key = st.text_input(
                "Google API Key",
                type="password",
                value=st.session_state.api_key,
                placeholder="Enter your Google API key...",
                help="Your API key will be stored in session only"
            )
            
            submitted = st.form_submit_button("🔍 Validate API Key", type="primary")
            
            if submitted:
                if not api_key:
                    st.error("Please enter an API key.")
                else:
                    with st.spinner("Validating API key..."):
                        is_valid, message, models = validate_api_key(api_key)
                        
                        if is_valid:
                            st.session_state.api_validated = True
                            st.session_state.api_key = api_key
                            st.success(f"✅ {message}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        
        # Info box
        st.info("💡 **Tip:** Make sure your API key has access to the Veo 3 model. You may need to enable it in your Google Cloud Console.")
    
    else:
        # Show validated status
        st.success("✅ API Key Validated Successfully!")
        
        # Option to change API key
        with st.expander("🔄 Change API Key"):
            if st.button("Use a different API key"):
                st.session_state.api_validated = False
                st.session_state.client = None
                st.rerun()
        
        st.divider()
        
        # Step 2: Video Generation Interface
        st.markdown("### 🎥 Step 2: Generate Your Video")
        
        st.success("💡 **Using Google AI Studio key with Veo 3.1**")
        
        # Correct model names based on Google documentation
        veo_models = [
            "veo-3.1-generate-preview",      # Latest Veo 3.1
            "veo-3.1-fast-generate-preview", # Veo 3.1 Fast (optimized for speed)
            "veo-2",                          # Veo 2 stable
        ]
        
        selected_model = st.selectbox(
            "Select Video Model",
            options=veo_models,
            index=0,
            help="veo-3.1-generate-preview is the latest model with audio support"
        )
        
        # Show model info
        with st.expander("ℹ️ Model Information"):
            st.markdown("""
            **Veo 3.1 Preview** - Latest model with:
            - 🎬 8 second videos (720p, 1080p, or 4K)
            - 🔊 Native audio generation (dialogue, sound effects, ambient)
            - 🖼️ Image-to-video support
            - 📐 16:9 or 9:16 aspect ratios
            
            **Veo 3.1 Fast Preview** - Optimized for speed:
            - Faster generation times
            - Good for rapid prototyping
            
            **Veo 2** - Stable release:
            - 720p/1080p output
            - No audio generation
            """)
        
        # Prompt input
        prompt = st.text_area(
            "Video Prompt",
            placeholder="Describe the video you want to generate...\n\nExample: A serene sunset over a calm ocean, with gentle waves reflecting golden light, cinematic quality",
            height=150,
            help="Be descriptive! Include details about scene, style, mood, camera movement, etc."
        )
        
        # Optional: Negative prompt
        negative_prompt = st.text_input(
            "Negative Prompt (optional)",
            placeholder="e.g., cartoon, drawing, low quality, blurry",
            help="Describe what you DON'T want in the video"
        )
        
        # Video settings
        col1, col2, col3 = st.columns(3)
        
        with col1:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                options=["16:9", "9:16"],
                index=0,
                help="16:9 for landscape, 9:16 for portrait"
            )
        
        with col2:
            duration = st.selectbox(
                "Duration (seconds)",
                options=[8, 6, 4],
                index=0,
                help="Video length - 8s for 1080p/4K"
            )
        
        with col3:
            resolution = st.selectbox(
                "Resolution",
                options=["720p", "1080p", "4k"],
                index=0,
                help="Higher res = longer wait & higher cost"
            )
        
        # Generate button
        if st.button("🎬 Generate Video", type="primary", disabled=not prompt):
            if not prompt:
                st.warning("Please enter a prompt to generate a video.")
            else:
                with st.spinner("🎥 Generating your video... This may take several minutes."):
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text(f"Starting video generation with {selected_model}...")
                    progress_bar.progress(10)
                    
                    # Actually generate the video
                    result = generate_video(
                        prompt=prompt, 
                        model_name=selected_model, 
                        duration=duration, 
                        aspect_ratio=aspect_ratio,
                        resolution=resolution,
                        negative_prompt=negative_prompt
                    )
                    
                    progress_bar.progress(100)
                    progress_bar.empty()
                    status_text.empty()
                    
                    if result["success"]:
                        st.success("✅ Video generated successfully!")
                        
                        # Store in session
                        st.session_state.generated_videos.append(result)
                        
                        # Display video
                        st.video(result["video_path"])
                        
                        # Download button
                        with open(result["video_path"], "rb") as f:
                            st.download_button(
                                label="⬇️ Download Video",
                                data=f.read(),
                                file_name=Path(result["video_path"]).name,
                                mime="video/mp4"
                            )
                    else:
                        st.error(f"❌ Failed to generate video: {result['error']}")
        
        # Prompt suggestions
        with st.expander("💡 Need inspiration? Try these prompts:"):
            suggestions = [
                "A majestic eagle soaring through mountain peaks at golden hour, cinematic drone shot",
                "Underwater scene of colorful coral reef with tropical fish swimming, 4K quality",
                "Time-lapse of a flower blooming in a garden, soft natural lighting",
                "Futuristic city skyline at night with flying cars, cyberpunk style",
                "A cozy coffee shop interior with rain on the windows, warm ambient lighting"
            ]
            for suggestion in suggestions:
                if st.button(f"📝 {suggestion[:50]}...", key=suggestion):
                    st.session_state.selected_prompt = suggestion
                    st.rerun()
        
        # Previously generated videos
        if st.session_state.generated_videos:
            st.divider()
            st.markdown("### 📚 Previously Generated Videos")
            
            for i, video in enumerate(reversed(st.session_state.generated_videos)):
                with st.expander(f"Video {len(st.session_state.generated_videos) - i}: {video['prompt'][:50]}..."):
                    if Path(video["video_path"]).exists():
                        st.video(video["video_path"])
                    else:
                        st.warning("Video file not found.")


# Footer
def show_footer():
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #888; padding: 1rem;'>
        <p>Built with ❤️ using Streamlit & Google Veo 3</p>
        <p style='font-size: 0.8rem;'>Make sure you have proper API access and credits for video generation.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
    show_footer()

# 🎬 Google Veo 3 Video Generator

A Streamlit-based application for generating AI videos using Google's Veo 3 model.

## Features

- ✅ API Key validation
- 🎥 Video generation with customizable settings
- 📐 Multiple aspect ratios (16:9, 9:16, 1:1)
- ⏱️ Configurable video duration
- 💾 Download generated videos
- 📚 View previously generated videos

## Prerequisites

1. Python 3.9 or higher
2. Google API key with Veo 3 access
3. Internet connection

## Installation

1. Navigate to the veo folder:
   ```bash
   cd veo
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Getting Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Make sure you have access to Veo 3 (may require waitlist or specific account type)

## Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Enter API Key**: Paste your Google API key in the input field
2. **Validate**: Click "Validate API Key" to verify access
3. **Create Prompt**: Enter a descriptive prompt for your video
4. **Configure Settings**: Choose aspect ratio and duration
5. **Generate**: Click "Generate Video" and wait for processing
6. **Download**: Save your generated video

## Tips for Better Videos

- Be descriptive with your prompts
- Include details about:
  - Scene elements (objects, people, environment)
  - Style (cinematic, anime, realistic)
  - Lighting (golden hour, dramatic, soft)
  - Camera movement (pan, zoom, tracking shot)
  - Mood (serene, energetic, mysterious)

## Example Prompts

- "A serene sunset over a calm ocean, with gentle waves reflecting golden light, cinematic quality"
- "Underwater scene of colorful coral reef with tropical fish swimming, 4K quality"
- "Time-lapse of a flower blooming in a garden, soft natural lighting"

## Troubleshooting

### API Key Invalid
- Ensure your API key is copied correctly
- Check if the key has Veo 3 access enabled
- Verify your Google Cloud billing is set up

### Video Generation Failed
- Check your API quota and credits
- Try a simpler prompt
- Ensure stable internet connection

### Import Errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Make sure you're using Python 3.9+

## File Structure

```
veo/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment file
├── README.md           # This file
└── generated_videos/   # Generated videos (created automatically)
```

## Environment Variables

You can optionally set your API key in a `.env` file:

```env
GOOGLE_API_KEY=your_api_key_here
```

## License

MIT License

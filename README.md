# PDF RAG Chatbot

A production-ready chatbot that ingests PDF documents, creates vector embeddings, and answers questions using LangGraph-powered RAG pipeline with Ollama.

# LIVE DEMO WITH G-DRIVE LINK
https://drive.google.com/file/d/1FZAK9k2nB_dZANVjc4R6UPTMYievQiUf/view?usp=sharing

## Features

- Upload and process PDF documents
- Intelligent text chunking with overlap
- Vector embeddings using sentence-transformers
- ChromaDB for efficient similarity search
- LangGraph-powered RAG pipeline
- Ollama integration for local LLM inference
- FastAPI backend with REST API
- Streamlit web interface

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install and run Ollama
# Download from: https://ollama.ai
ollama run llama2

# 4. In another terminal, run the app
streamlit run app.py
```

The app will open at **http://localhost:8501**

## Ollama Setup (Local LLM)

The system uses **Ollama** for local LLM inference - no API keys needed!

### Quick Setup:
```bash
# 1. Install Ollama from https://ollama.ai

# 2. Pull a model (choose one):
ollama pull llama2       # Recommended for general use
ollama pull llama3       # Better quality, larger
ollama pull mistral      # Fast and efficient
ollama pull phi          # Lightweight

# 3. Run your chosen model:
ollama run llama2
```

### Configuration (.env):
```bash
OLLAMA_MODEL=llama2
OLLAMA_URL=http://localhost:11434
```

That's it! The app will automatically connect to your local Ollama instance.

## Installation Steps

### 1. Install Python 3.9+
Download from [python.org](https://www.python.org/downloads/)

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)
```bash
# Copy the example file
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# Edit to change Ollama model if needed
# OLLAMA_MODEL=llama2
```

### 5. Run Ollama
```bash
ollama run llama2
```

### 6. Run the Application
```bash
streamlit run app.py
```

## Usage

### 1. Upload PDF
- Click **"Upload Documents"** in sidebar
- Select your PDF file(s)
- Click **"Process PDF"**

### 2. Ask Questions
```
"What is this document about?"
"Summarize the key findings"
"What does it say about [topic]?"
```

### 3. Get Answers with Sources
- View AI-generated answers
- Check source citations
- See exact page numbers

## Advanced Usage

### Run API Separately

```bash
# Terminal 1: Start API
python main.py
# API docs at http://localhost:8000/docs

# Terminal 2: Start UI
streamlit run app.py
```

### Using API Programmatically

```python
import requests

# Upload PDF
files = {"file": open("document.pdf", "rb")}
requests.post("http://localhost:8000/upload-pdf", files=files)

# Ask question
response = requests.post(
    "http://localhost:8000/chat",
    json={"question": "What is this about?"}
)
print(response.json()["answer"])
```

## Project Structure

```
Pipe/
├── app.py                 # Streamlit UI
├── main.py                # FastAPI backend
├── pdf_processor.py       # PDF loading & chunking
├── vector_store.py        # Embeddings + ChromaDB
├── rag_pipeline.py        # LangGraph RAG pipeline
├── requirements.txt       # Dependencies
├── .env                   # Your configuration
├── .env.example           # Configuration template
└── README.md              # This file
```

## Configuration (.env)

```bash
# Ollama Configuration
OLLAMA_MODEL=llama2
OLLAMA_URL=http://localhost:11434

# Embeddings (no API key needed - runs locally)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Text Processing
CHUNK_SIZE=1000          # Characters per chunk
CHUNK_OVERLAP=200        # Overlap between chunks
TOP_K_RESULTS=4          # Number of chunks to retrieve
```

## How It Works

1. **Upload PDF** - System extracts and chunks text
2. **Create Embeddings** - Local model converts text to vectors
3. **Store in ChromaDB** - Vectors saved locally for fast search
4. **Ask Question** - System finds relevant chunks
5. **Generate Answer** - LLM creates response using Ollama
6. **Show Sources** - See which PDF sections were used

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| API won't start | Run `python main.py` |
| Ollama not connecting | Make sure it's running: `ollama run llama2` |
| Slow responses | Use smaller model: `ollama pull phi` |
| Port 8000 in use | Change `API_PORT=8001` in `.env` |
| Out of memory | Reduce `CHUNK_SIZE=500` in `.env` |

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Embeddings:** Sentence Transformers (local, free)
- **Vector DB:** ChromaDB (local, free)
- **RAG:** LangGraph
- **PDF Parser:** PyPDF
- **LLM:** Ollama (local, free)

## License

MIT License - free to use for any project!

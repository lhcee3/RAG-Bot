# 📚 PDF RAG Chatbot

A production-ready chatbot that ingests PDF documents, creates vector embeddings, and answers questions using LangGraph-powered RAG pipeline.

---

## ✨ Features

- Upload and process PDF documents
- Intelligent text chunking with overlap
- Vector embeddings using sentence-transformers
- ChromaDB for efficient similarity search
- LangGraph-powered RAG pipeline
- Multiple LLM support (OpenAI, Groq, or local)
- FastAPI backend with REST API
- Streamlit web interface

---

## 🚀 Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (copy from .env.example)
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# 4. Run the app
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## 🔑 API Keys (Optional but Recommended)

The system works **without any API keys** using local embeddings and fallback responses.

For **better quality answers**, add one of these to your `.env` file:

### Option 1: Groq (Free & Fast) ⭐ Recommended
```bash
GROQ_API_KEY=gsk_your_key_here
```
- Get free key at: [console.groq.com](https://console.groq.com)
- Fast inference
- Generous free tier
- Best for production

### Option 2: OpenAI (Paid)
```bash
OPENAI_API_KEY=sk_your_key_here
```
- Get key at: [platform.openai.com](https://platform.openai.com)
- Pay-as-you-go pricing
- GPT-3.5-turbo is cheap (~$0.002 per request)
- Highest quality responses

### Option 3: Local (Free but slower)
No API key needed - install Ollama:
```bash
# Install from ollama.ai
ollama pull llama2
```

---

## 📖 Installation Steps

## 📖 Installation Steps

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

### 4. Configure Environment
```bash
# Copy the example file
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# Edit .env and add API keys (optional)
# GROQ_API_KEY=your_key_here
```

### 5. Run the Application
```bash
streamlit run app.py
```

---

## 🎯 Usage

### 1️⃣ Upload PDF
- Click **"📤 Upload Documents"** in sidebar
- Select your PDF file(s)
- Click **"🚀 Process PDF"**

### 2️⃣ Ask Questions
```
"What is this document about?"
"Summarize the key findings"
"What does it say about [topic]?"
```

### 3️⃣ Get Answers with Sources
- View AI-generated answers
- Check source citations
- See exact page numbers

---

## 💡 Advanced Usage

### Run API Separately

```bash
# Terminal 1: Start API
python main.py
# API docs at http://localhost:8000/docs

# Terminal 2: Start UI
streamlit run app.py
```

### Test System

```bash
# Run diagnostic test
python test_system.py
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

---

## 📁 Project Structure

```
📦 Pipe/
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

---

## ⚙️ Configuration (.env)

## ⚙️ Configuration (.env)

```bash
# Embeddings (no API key needed - runs locally)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Text Processing
CHUNK_SIZE=1000          # Characters per chunk
CHUNK_OVERLAP=200        # Overlap between chunks
TOP_K_RESULTS=4          # Number of chunks to retrieve

# LLM API Keys (OPTIONAL - system works without these)
# For better answers, add ONE of these:

# Option 1: Groq (Free, recommended)
# GROQ_API_KEY=gsk_your_key_here

# Option 2: OpenAI (Paid)
# OPENAI_API_KEY=sk_your_key_here
```

---

## 🎯 How It Works

1. **Upload PDF** → System extracts and chunks text
2. **Create Embeddings** → Local model converts text to vectors
3. **Store in ChromaDB** → Vectors saved locally for fast search
4. **Ask Question** → System finds relevant chunks
5. **Generate Answer** → LLM (or fallback) creates response
6. **Show Sources** → See which PDF sections were used

---

## 🔧 Advanced Usage

### Run API Separately
```bash
# Terminal 1: API
python main.py
# API docs: http://localhost:8000/docs

# Terminal 2: UI
streamlit run app.py
```

### Using API Directly
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

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| API won't start | Run `python main.py` |
| Slow responses | Reduce `TOP_K_RESULTS=2` in `.env` |
| Port 8000 in use | Change `API_PORT=8001` in `.env` |
| Out of memory | Reduce `CHUNK_SIZE=500` in `.env` |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Embeddings:** Sentence Transformers (local, free)
- **Vector DB:** ChromaDB (local, free)
- **RAG:** LangGraph
- **PDF Parser:** PyPDF
- **LLM:** OpenAI / Groq / Local (all optional)

---

## 📄 License

MIT License - free to use for any project!

---

## ⭐ Support

If this helped you, please star the repo!

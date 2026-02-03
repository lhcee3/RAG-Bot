# ML Pipeline Projects

This repository contains multiple machine learning projects.

## Projects

### 1. [PDF RAG Chatbot](./pdf-rag-chatbot/)
A production-ready chatbot that ingests PDF documents, creates vector embeddings, and answers questions using LangGraph-powered RAG pipeline with Ollama.

**Key Features:**
- PDF document processing with intelligent chunking
- Vector embeddings using sentence-transformers
- ChromaDB for similarity search
- LangGraph-powered RAG pipeline
- Local LLM inference with Ollama
- Streamlit web interface

[View Project →](./pdf-rag-chatbot/README.md)

---

## Repository Structure

```
ML/Pipe/
├── pdf-rag-chatbot/          # PDF RAG Chatbot project
│   ├── app.py
│   ├── main.py
│   ├── pdf_processor.py
│   ├── rag_pipeline.py
│   ├── vector_store.py
│   ├── requirements.txt
│   └── README.md
├── [future-project-2]/       # Your next project goes here
└── README.md                 # This file
```

## Getting Started

Navigate to the specific project folder and follow its README for setup instructions.

## Contributing

Each project has its own setup and requirements. Please refer to individual project READMEs for details.

import streamlit as st
import requests
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="PDF RAG Chatbot",
    page_icon="file-text",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stAlert { margin-top: 1rem; }
    .source-box { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
    .chat-message { padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; }
    .user-message { background-color: #e3f2fd; }
    .bot-message { background-color: #f5f5f5; }
    </style>
""", unsafe_allow_html=True)

def check_api_status():
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return {
            "ok": response.status_code == 200,
            "status_code": response.status_code,
            "latency_ms": round(response.elapsed.total_seconds() * 1000, 1),
            "error": None,
        }
    except Exception as exc:
        return {"ok": False, "status_code": None, "latency_ms": None, "error": str(exc)}

def get_system_status():
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def upload_pdf(file):
    try:
        files = {"file": (file.name, file, "application/pdf")}
        response = requests.post(f"{API_URL}/upload-pdf", files=files, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": response.json().get("detail", "Upload failed")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def upload_multiple_pdfs(files):
    try:
        file_list = [("files", (file.name, file, "application/pdf")) for file in files]
        response = requests.post(f"{API_URL}/upload-multiple-pdfs", files=file_list, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": response.json().get("detail", "Upload failed")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ask_question(question: str, top_k: int = None):
    try:
        payload = {"question": question}
        if top_k:
            payload["top_k"] = top_k
        
        response = requests.post(f"{API_URL}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("detail", "Unknown error")
            return {"error": error}
    except Exception as e:
        return {"error": str(e)}

def clear_database():
    try:
        response = requests.delete(f"{API_URL}/clear", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": "Failed to clear database"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False

st.title("PDF RAG Chatbot")
st.markdown("Upload PDFs and ask questions about their content using local Ollama LLM")

with st.sidebar:
    st.header("System Status")
    
    api_status = check_api_status()
    if api_status["ok"]:
        st.success("API Running")
        
        status = get_system_status()
        if status:
            st.info(f"Documents: {status['details'].get('document_count', 0)}")
    else:
        st.error("API Not Running")
        st.warning("Start the API with: `uvicorn main:app --reload`")
        with st.expander("API debug steps"):
            st.markdown(
                """
                1. Confirm the backend is running: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
                2. Check if port 8000 is already in use (Windows): `netstat -ano | findstr :8000`
                3. Try a direct call: `curl http://localhost:8000/status`
                4. Make sure Ollama is running: `ollama run llama2`
                5. Inspect terminal logs for tracebacks; restart the backend after fixing them.
                """
            )
            if api_status.get("error"):
                st.info(f"Last check error: {api_status['error']}")
        st.stop()
    
    st.markdown("---")
    
    st.subheader("Upload Documents")
    
    upload_mode = st.radio("Upload mode:", ["Single PDF", "Multiple PDFs"])
    
    if upload_mode == "Single PDF":
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to add to the knowledge base"
        )
        
        if uploaded_file:
            if st.button("Process PDF", type="primary"):
                with st.spinner("Processing PDF..."):
                    result = upload_pdf(uploaded_file)
                    
                    if result["status"] == "success":
                        st.success(f"{result['message']}")
                        st.json(result["details"])
                        st.session_state.documents_loaded = True
                        st.rerun()
                    else:
                        st.error(f"{result['message']}")
    
    else:
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Upload multiple PDF documents"
        )
        
        if uploaded_files:
            if st.button("Process All PDFs", type="primary"):
                with st.spinner(f"Processing {len(uploaded_files)} PDFs..."):
                    result = upload_multiple_pdfs(uploaded_files)
                    
                    if result["status"] == "success":
                        st.success(f"{result['message']}")
                        st.json(result["details"])
                        st.session_state.documents_loaded = True
                        st.rerun()
                    else:
                        st.error(f"{result['message']}")
    
    st.markdown("---")
    
    st.subheader("Advanced")
    
    top_k = st.slider(
        "Number of chunks to retrieve",
        min_value=1,
        max_value=10,
        value=4,
        help="More chunks = more context but slower"
    )
    
    if st.button("Clear Database", type="secondary"):
        with st.spinner("Clearing database..."):
            result = clear_database()
            if result["status"] == "success":
                st.success("Database cleared")
                st.session_state.chat_history = []
                st.session_state.documents_loaded = False
                st.rerun()
            else:
                st.error(f"Error: {result['message']}")

st.header("Chat with your documents")

for chat in st.session_state.chat_history:
    with st.container():
        st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {chat["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-message bot-message"><strong>Bot:</strong> {chat["answer"]}</div>', unsafe_allow_html=True)
        
        if chat.get("sources"):
            with st.expander("View Sources"):
                for i, source in enumerate(chat["sources"], 1):
                    st.markdown(f"**Source {i}:**")
                    st.text(source["content"])
                    st.caption(f"Page: {source['metadata'].get('page', 'N/A')}, File: {source['metadata'].get('source_file', 'N/A')}")
                    st.markdown("---")

question_input = st.text_input(
    "Ask a question about your documents:",
    placeholder="What is this document about?",
    key="question_input"
)

col1, col2 = st.columns([1, 5])
with col1:
    ask_button = st.button("Ask", type="primary", use_container_width=True)

if ask_button and question_input:
    with st.spinner("Thinking..."):
        result = ask_question(question_input, top_k=top_k)
        
        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.session_state.chat_history.append(result)
            st.rerun()

if not st.session_state.documents_loaded:
    st.info("Upload a PDF document to start chatting")

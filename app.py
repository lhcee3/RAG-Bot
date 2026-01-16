"""
Streamlit UI
Interactive web interface for the PDF RAG Chatbot
"""

import streamlit as st
import requests
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

# API configuration
API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="PDF RAG Chatbot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stAlert {
        margin-top: 1rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .bot-message {
        background-color: #f5f5f5;
    }
    </style>
""", unsafe_allow_html=True)


def check_api_status():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_system_status():
    """Get system status from API"""
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def upload_pdf(file):
    """Upload a PDF file to the API"""
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
    """Upload multiple PDF files to the API"""
    try:
        file_list = [("files", (file.name, file, "application/pdf")) for file in files]
        response = requests.post(f"{API_URL}/upload-multiple-pdfs", files=file_list, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": response.json().get("detail", "Upload failed")}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def ask_question(question: str):
    """Send a question to the chatbot"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"question": question},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "Query failed")}
    except Exception as e:
        return {"error": str(e)}


def clear_vectorstore():
    """Clear all documents from the vector store"""
    try:
        response = requests.delete(f"{API_URL}/clear", timeout=10)
        return response.status_code == 200
    except:
        return False


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False


# Sidebar
with st.sidebar:
    st.title("📚 PDF RAG Chatbot")
    st.markdown("---")
    
    # API status check
    api_status = check_api_status()
    if api_status:
        st.success("✓ API Connected")
        
        # System status
        status = get_system_status()
        if status:
            st.info(f"📊 Documents: {status['details'].get('document_count', 0)}")
    else:
        st.error("✗ API Not Running")
        st.warning("Start the API with: `uvicorn main:app --reload`")
        st.stop()
    
    st.markdown("---")
    
    # File upload section
    st.subheader("📤 Upload Documents")
    
    upload_mode = st.radio("Upload mode:", ["Single PDF", "Multiple PDFs"])
    
    if upload_mode == "Single PDF":
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to add to the knowledge base"
        )
        
        if uploaded_file:
            if st.button("🚀 Process PDF", type="primary"):
                with st.spinner("Processing PDF..."):
                    result = upload_pdf(uploaded_file)
                    
                    if result["status"] == "success":
                        st.success(f"✓ {result['message']}")
                        st.json(result["details"])
                        st.session_state.documents_loaded = True
                        st.rerun()
                    else:
                        st.error(f"✗ {result['message']}")
    
    else:
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Upload multiple PDF documents"
        )
        
        if uploaded_files:
            if st.button("🚀 Process All PDFs", type="primary"):
                with st.spinner(f"Processing {len(uploaded_files)} PDFs..."):
                    result = upload_multiple_pdfs(uploaded_files)
                    
                    if result["status"] == "success":
                        st.success(f"✓ {result['message']}")
                        st.json(result["details"])
                        st.session_state.documents_loaded = True
                        st.rerun()
                    else:
                        st.error(f"✗ {result['message']}")
    
    st.markdown("---")
    
    # Clear button
    if st.button("🗑️ Clear All Documents", type="secondary"):
        if clear_vectorstore():
            st.success("✓ Documents cleared")
            st.session_state.messages = []
            st.session_state.documents_loaded = False
            st.rerun()
        else:
            st.error("✗ Failed to clear documents")
    
    st.markdown("---")
    st.caption("Built with LangChain, LangGraph & Streamlit")


# Main content
st.title("💬 Chat with Your Documents")

# Check if documents are loaded
status = get_system_status()
if status and status["details"].get("document_count", 0) == 0:
    st.info("👈 Upload a PDF document to get started!")
    st.markdown("""
    ### How to use:
    1. **Upload PDFs** using the sidebar
    2. **Ask questions** about your documents
    3. **Get answers** with source references
    
    ### Features:
    - 📄 Multiple PDF support
    - 🔍 Intelligent retrieval
    - 🤖 Context-aware responses
    - 📚 Source citations
    """)
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**Source {i}:**")
                        st.text(source["content"])
                        st.caption(f"From: {source['metadata'].get('source_file', 'Unknown')}, Page: {source['metadata'].get('page', 'N/A')}")
                        st.markdown("---")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_question(prompt)
                
                if "error" in response:
                    st.error(f"Error: {response['error']}")
                else:
                    st.markdown(response["answer"])
                    
                    # Store assistant message with sources
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response.get("sources", [])
                    })
                    
                    # Show sources
                    if response.get("sources"):
                        with st.expander("📚 View Sources"):
                            for i, source in enumerate(response["sources"], 1):
                                st.markdown(f"**Source {i}:**")
                                st.text(source["content"])
                                st.caption(f"From: {source['metadata'].get('source_file', 'Unknown')}, Page: {source['metadata'].get('page', 'N/A')}")
                                st.markdown("---")
    
    # Clear chat button
    if st.session_state.messages:
        if st.button("🔄 Clear Chat History"):
            st.session_state.messages = []
            st.rerun()


# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🤖 Powered by LangChain")
with col2:
    st.caption("🔗 LangGraph RAG Pipeline")
with col3:
    st.caption("🎯 ChromaDB Vector Store")

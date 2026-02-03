import os
import shutil
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from pdf_processor import PDFProcessor
from vector_store import VectorStore
from rag_pipeline import RAGPipeline

load_dotenv()

app = FastAPI(
    title="PDF RAG Chatbot API",
    description="API for PDF-based Retrieval-Augmented Generation chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pdf_processor = PDFProcessor()
vector_store = VectorStore()
rag_pipeline: Optional[RAGPipeline] = None

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    question: str
    top_k: Optional[int] = None

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list

class StatusResponse(BaseModel):
    status: str
    message: str
    details: dict

@app.get("/", response_model=StatusResponse)
async def root():
    store_info = vector_store.get_store_info()
    
    return {
        "status": "online",
        "message": "PDF RAG Chatbot API is running",
        "details": {
            "vectorstore_status": store_info.get("status"),
            "document_count": store_info.get("document_count", 0)
        }
    }

@app.post("/upload-pdf", response_model=StatusResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing: {file.filename}")
        
        chunks = pdf_processor.load_pdf(file_path)
        chunk_info = pdf_processor.get_chunk_info(chunks)
        
        vector_store.add_documents(chunks)
        
        global rag_pipeline
        if rag_pipeline is None:
            rag_pipeline = RAGPipeline(vectorstore=vector_store.vectorstore)
        
        return {
            "status": "success",
            "message": f"PDF '{file.filename}' processed successfully",
            "details": {
                "filename": file.filename,
                "chunks_created": chunk_info["total_chunks"],
                "total_characters": chunk_info["total_chars"],
                "avg_chunk_size": chunk_info["avg_chunk_size"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
    finally:
        await file.close()

@app.post("/upload-multiple-pdfs", response_model=StatusResponse)
async def upload_multiple_pdfs(files: list[UploadFile] = File(...)):
    processed_files = []
    total_chunks = 0
    
    try:
        for file in files:
            if not file.filename.endswith('.pdf'):
                continue
            
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            chunks = pdf_processor.load_pdf(file_path)
            vector_store.add_documents(chunks)
            
            processed_files.append(file.filename)
            total_chunks += len(chunks)
            
            await file.close()
        
        global rag_pipeline
        if rag_pipeline is None:
            rag_pipeline = RAGPipeline(vectorstore=vector_store.vectorstore)
        
        return {
            "status": "success",
            "message": f"Processed {len(processed_files)} PDF files",
            "details": {
                "files": processed_files,
                "total_chunks": total_chunks
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDFs: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if rag_pipeline is None:
        raise HTTPException(
            status_code=400,
            detail="No documents loaded. Please upload a PDF first."
        )
    
    try:
        result = rag_pipeline.query(request.question)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

@app.get("/status", response_model=StatusResponse)
async def get_status():
    store_info = vector_store.get_store_info()
    
    return {
        "status": "ready" if rag_pipeline else "no_documents",
        "message": "System ready" if rag_pipeline else "Upload documents to start",
        "details": store_info
    }

@app.delete("/clear", response_model=StatusResponse)
async def clear_vectorstore():
    try:
        vector_store.clear_store()
        
        global rag_pipeline
        rag_pipeline = None
        
        for file in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        return {
            "status": "success",
            "message": "Vector store and uploads cleared",
            "details": {}
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing store: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"Starting PDF RAG Chatbot API on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

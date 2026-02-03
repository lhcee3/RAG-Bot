import os
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    def __init__(self, embedding_model: str = None, persist_directory: str = None):
        self.embedding_model_name = embedding_model or os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.persist_directory = persist_directory or os.getenv(
            "VECTOR_DB_PATH",
            "./chroma_db"
        )
        
        print(f"Loading embedding model: {self.embedding_model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vectorstore: Optional[Chroma] = None
        
        if os.path.exists(self.persist_directory):
            self._load_existing_store()
    
    def _load_existing_store(self):
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print(f"Loaded existing vector store from {self.persist_directory}")
        except Exception as e:
            print(f"Could not load existing store: {str(e)}")
            self.vectorstore = None
    
    def create_store(self, documents: List[Document]) -> Chroma:
        if not documents:
            raise ValueError("No documents provided to create store")
        
        print(f"Creating vector store with {len(documents)} documents...")
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        print(f"Vector store created and persisted to {self.persist_directory}")
        return self.vectorstore
    
    def add_documents(self, documents: List[Document]):
        if not self.vectorstore:
            return self.create_store(documents)
        
        print(f"Adding {len(documents)} documents to vector store...")
        self.vectorstore.add_documents(documents)
        print("Documents added successfully")
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Add documents first.")
        
        k = k or int(os.getenv("TOP_K_RESULTS", "4"))
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, query: str, k: int = None) -> List[tuple[Document, float]]:
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Add documents first.")
        
        k = k or int(os.getenv("TOP_K_RESULTS", "4"))
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results
    
    def clear_store(self):
        if self.vectorstore:
            self.vectorstore.delete_collection()
            self.vectorstore = None
            print("Vector store cleared")
    
    def get_store_info(self) -> dict:
        if not self.vectorstore:
            return {"status": "empty", "document_count": 0}
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                "status": "ready",
                "document_count": count,
                "persist_directory": self.persist_directory,
                "embedding_model": self.embedding_model_name
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

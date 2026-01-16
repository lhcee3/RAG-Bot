"""
PDF Processing Module
Handles PDF loading and intelligent text chunking with overlap
"""

import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()


class PDFProcessor:
    """Process PDF documents for RAG pipeline"""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize PDF processor with configurable chunking parameters
        
        Args:
            chunk_size: Size of each text chunk (default from env or 1000)
            chunk_overlap: Overlap between chunks (default from env or 200)
        """
        self.chunk_size = chunk_size or int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = chunk_overlap or int(os.getenv("CHUNK_OVERLAP", "200"))
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Load and process a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of Document objects with chunked text
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Load PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Chunk documents
        chunks = self.text_splitter.split_documents(documents)
        
        # Add metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["source_file"] = os.path.basename(file_path)
        
        return chunks
    
    def load_multiple_pdfs(self, file_paths: List[str]) -> List[Document]:
        """
        Load and process multiple PDF files
        
        Args:
            file_paths: List of paths to PDF files
            
        Returns:
            Combined list of Document objects from all PDFs
        """
        all_chunks = []
        
        for file_path in file_paths:
            try:
                chunks = self.load_pdf(file_path)
                all_chunks.extend(chunks)
                print(f"✓ Processed {file_path}: {len(chunks)} chunks")
            except Exception as e:
                print(f"✗ Error processing {file_path}: {str(e)}")
        
        return all_chunks
    
    def get_chunk_info(self, chunks: List[Document]) -> dict:
        """
        Get statistics about the processed chunks
        
        Args:
            chunks: List of Document chunks
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {"total_chunks": 0, "total_chars": 0, "avg_chunk_size": 0}
        
        total_chars = sum(len(chunk.page_content) for chunk in chunks)
        
        return {
            "total_chunks": len(chunks),
            "total_chars": total_chars,
            "avg_chunk_size": total_chars // len(chunks),
            "sources": list(set(chunk.metadata.get("source_file") for chunk in chunks))
        }


# Example usage
if __name__ == "__main__":
    processor = PDFProcessor()
    
    # Test with a sample PDF (replace with your PDF path)
    # chunks = processor.load_pdf("sample.pdf")
    # info = processor.get_chunk_info(chunks)
    # print(f"Processed {info['total_chunks']} chunks from {info['sources']}")

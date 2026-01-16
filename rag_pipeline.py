"""
RAG Pipeline Module
LangGraph-powered Retrieval-Augmented Generation pipeline
"""

import os
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()


class GraphState(TypedDict):
    """State object for the RAG pipeline graph"""
    question: str
    context: List[str]
    answer: str
    retrieved_docs: List[Document]
    vectorstore: object


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline using LangGraph"""
    
    def __init__(self, vectorstore, llm=None):
        """
        Initialize RAG pipeline
        
        Args:
            vectorstore: VectorStore instance for retrieval
            llm: Language model for generation (optional, uses fallback)
        """
        self.vectorstore = vectorstore
        self.llm = llm or self._get_default_llm()
        self.graph = self._build_graph()
    
    def _get_default_llm(self):
        """Get a default LLM - tries Groq first, then falls back to local model"""
        # Option 1: Try Groq if API key available
        if os.getenv("GROQ_API_KEY"):
            try:
                from langchain_groq import ChatGroq
                print("Using Groq Llama 3")
                return ChatGroq(model="llama3-8b-8192", temperature=0)
            except ImportError:
                print("Warning: langchain_groq not installed. Install with: pip install langchain-groq")
            except Exception as e:
                print(f"Warning: Could not load Groq: {e}")
        
        # Option 2: Use HuggingFace pipeline (local, free)
        try:
            from langchain_community.llms import HuggingFacePipeline
            from transformers import pipeline
            print("Using local HuggingFace model (this may take a moment...)")
            
            pipe = pipeline(
                "text-generation",
                model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                max_new_tokens=256,
                temperature=0.7
            )
            return HuggingFacePipeline(pipeline=pipe)
        except Exception as e:
            print(f"Warning: Could not load HuggingFace model: {e}")
        
        # Fallback: Simple template-based response
        print("⚠️ No LLM available. Using template-based responses.")
        return None
    
    def _retrieve_node(self, state: GraphState) -> GraphState:
        """
        Retrieval node: Search vector store for relevant documents
        """
        print(f"🔍 Retrieving context for: {state['question'][:50]}...")
        
        k = int(os.getenv("TOP_K_RESULTS", "4"))
        docs = self.vectorstore.similarity_search(state['question'], k=k)
        
        state['retrieved_docs'] = docs
        state['context'] = [doc.page_content for doc in docs]
        
        print(f"✓ Retrieved {len(docs)} relevant chunks")
        return state
    
    def _generate_node(self, state: GraphState) -> GraphState:
        """
        Generation node: Generate answer using retrieved context
        """
        print("💭 Generating answer...")
        
        context = "\n\n".join(state['context'])
        question = state['question']
        
        if self.llm is None:
            # Fallback response without LLM
            state['answer'] = self._template_response(context, question)
        else:
            # Use LLM for generation
            prompt = self._create_prompt(context, question)
            
            try:
                if hasattr(self.llm, 'invoke'):
                    response = self.llm.invoke(prompt)
                    if hasattr(response, 'content'):
                        state['answer'] = response.content
                    else:
                        state['answer'] = str(response)
                else:
                    state['answer'] = self.llm(prompt)
            except Exception as e:
                print(f"⚠️ LLM error: {e}")
                state['answer'] = self._template_response(context, question)
        
        print("✓ Answer generated")
        return state
    
    def _create_prompt(self, context: str, question: str) -> str:
        """Create a prompt for the LLM"""
        return f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Answer the question based solely on the context provided above. If the context doesn't contain enough information to answer the question, say so. Be concise and accurate.

Answer:"""
    
    def _template_response(self, context: str, question: str) -> str:
        """Generate a simple template-based response (fallback)"""
        if not context:
            return "I couldn't find relevant information in the documents to answer your question."
        
        return f"""Based on the available documents, here are the relevant excerpts:

{context[:500]}...

[Note: Using local processing. For better answers, configure an LLM API key in .env]"""
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph RAG pipeline"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)
        
        # Add edges
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        # Set entry point
        workflow.set_entry_point("retrieve")
        
        return workflow.compile()
    
    def query(self, question: str) -> dict:
        """
        Run a query through the RAG pipeline
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer and source documents
        """
        initial_state = {
            "question": question,
            "context": [],
            "answer": "",
            "retrieved_docs": [],
            "vectorstore": self.vectorstore
        }
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "question": question,
            "answer": result["answer"],
            "sources": [
                {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }
                for doc in result["retrieved_docs"]
            ]
        }


# Example usage
if __name__ == "__main__":
    from vector_store import VectorStore
    from pdf_processor import PDFProcessor
    
    # Initialize components
    processor = PDFProcessor()
    vector_store = VectorStore()
    
    # Load PDFs (replace with your PDF path)
    # chunks = processor.load_pdf("sample.pdf")
    # vector_store.create_store(chunks)
    
    # Create RAG pipeline
    # rag = RAGPipeline(vectorstore=vector_store.vectorstore)
    
    # Query
    # result = rag.query("What is this document about?")
    # print(f"Answer: {result['answer']}")

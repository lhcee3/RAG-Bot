import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

class GraphState(TypedDict):
    question: str
    context: List[str]
    answer: str
    retrieved_docs: List[Document]
    vectorstore: object

class RAGPipeline:
    def __init__(self, vectorstore, llm=None):
        self.vectorstore = vectorstore
        self.llm = llm or self._get_default_llm()
        self.graph = self._build_graph()
    
    def _get_default_llm(self):
        try:
            from langchain_community.llms import Ollama
            
            model_name = os.getenv("OLLAMA_MODEL", "llama2")
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            
            print(f"Connecting to Ollama model: {model_name} at {ollama_url}")
            
            llm = Ollama(
                model=model_name,
                base_url=ollama_url,
                temperature=0.7
            )
            
            print("Ollama connected successfully")
            return llm
            
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")
            print("Make sure Ollama is running with: ollama run <model-name>")
        
        print("No LLM available. Using template-based responses.")
        return None
    
    def _retrieve_node(self, state: GraphState) -> GraphState:
        print(f"Retrieving context for: {state['question'][:50]}...")
        
        k = int(os.getenv("TOP_K_RESULTS", "4"))
        docs = self.vectorstore.similarity_search(state['question'], k=k)
        
        state['retrieved_docs'] = docs
        state['context'] = [doc.page_content for doc in docs]
        
        print(f"Retrieved {len(docs)} relevant chunks")
        return state
    
    def _generate_node(self, state: GraphState) -> GraphState:
        print("Generating answer...")
        
        context = "\n\n".join(state['context'])
        question = state['question']
        
        if self.llm is None:
            state['answer'] = self._template_response(context, question)
        else:
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
                print(f"LLM error: {e}")
                state['answer'] = self._template_response(context, question)
        
        print("Answer generated")
        return state
    
    def _create_prompt(self, context: str, question: str) -> str:
        return f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Answer the question based solely on the context provided above. If the context doesn't contain enough information to answer the question, say so. Be concise and accurate.

Answer:"""
    
    def _template_response(self, context: str, question: str) -> str:
        if not context:
            return "I couldn't find relevant information in the documents to answer your question."
        
        return f"""Based on the available documents, here are the relevant excerpts:

{context[:500]}...

[Note: Using local processing. For better answers, configure Ollama with: ollama run llama2]"""
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(GraphState)
        
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)
        
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        workflow.set_entry_point("retrieve")
        
        return workflow.compile()
    
    def query(self, question: str) -> dict:
        initial_state = {
            "question": question,
            "context": [],
            "answer": "",
            "retrieved_docs": [],
            "vectorstore": self.vectorstore
        }
        
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

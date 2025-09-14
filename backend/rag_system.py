"""
RAG Pipeline Implementation
Handles document processing, embedding, retrieval, and generation with memory.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# LangChain imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader, 
    TextLoader, 
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Environment setup
from dotenv import load_dotenv
load_dotenv()


class PersonalKnowledgeVault:
    """
    Main RAG system with memory capabilities.
    """
    
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Check API key availability
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Initialize components
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
        
        # Vector store
        self.vector_store = Chroma(
            persist_directory=str(self.storage_path / "chroma_db"),
            embedding_function=self.embeddings
        )
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
        
        # Chat history
        self.chat_history_file = self.storage_path / "chat_history.json"
        self.chat_history = self._load_chat_history()
        
        # RAG prompt template
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant for question-answering tasks. 
            Use the following pieces of retrieved context to answer the question. 
            If you don't know the answer, just say that you don't know. 
            Use three sentences maximum and keep the answer concise.
            
            Always cite your sources by mentioning the document name when providing information.
            
            Previous conversation context: {chat_context}
            
            Retrieved context: {context}"""),
            ("human", "{question}")
        ])
        
        # Build RAG chain
        self.rag_chain = self._build_rag_chain()
    
    def _load_chat_history(self) -> List[Dict[str, Any]]:
        """Load chat history from JSON file."""
        if self.chat_history_file.exists():
            try:
                with open(self.chat_history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_chat_history(self):
        """Save chat history to JSON file."""
        with open(self.chat_history_file, 'w') as f:
            json.dump(self.chat_history, f, indent=2, default=str)
    
    def _format_chat_context(self, max_messages: int = 5) -> str:
        """Format recent chat history for context."""
        if not self.chat_history:
            return "No previous conversation."
        
        recent_messages = self.chat_history[-max_messages:]
        context_parts = []
        
        for msg in recent_messages:
            context_parts.append(f"Q: {msg['question']}")
            context_parts.append(f"A: {msg['answer']}")
        
        return "\n".join(context_parts)
    
    def _build_rag_chain(self):
        """Build the RAG processing chain."""
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )
        
        rag_chain = (
            {
                "context": retriever | format_docs,
                "chat_context": lambda x: self._format_chat_context(),
                "question": RunnablePassthrough()
            }
            | self.rag_prompt
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain
    
    def add_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Add documents to the knowledge base.
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            Processing results with success/failure counts
        """
        results = {
            "processed": 0,
            "failed": 0,
            "errors": []
        }
        
        for file_path in file_paths:
            try:
                # Load document based on file type
                file_path = Path(file_path)
                
                if file_path.suffix.lower() == '.pdf':
                    loader = PyPDFLoader(str(file_path))
                elif file_path.suffix.lower() == '.txt':
                    loader = TextLoader(str(file_path))
                elif file_path.suffix.lower() in ['.docx', '.doc']:
                    loader = Docx2txtLoader(str(file_path))
                elif file_path.suffix.lower() == '.md':
                    loader = TextLoader(str(file_path))
                else:
                    results["errors"].append(f"Unsupported file type: {file_path}")
                    results["failed"] += 1
                    continue
                
                # Load and split documents
                documents = loader.load()
                
                # Add metadata
                for doc in documents:
                    doc.metadata.update({
                        "source": str(file_path.name),
                        "added_date": datetime.now().isoformat(),
                        "file_type": file_path.suffix
                    })
                
                # Split documents
                splits = self.text_splitter.split_documents(documents)
                
                # Add to vector store
                self.vector_store.add_documents(splits)
                
                results["processed"] += 1
                
            except Exception as e:
                results["errors"].append(f"Error processing {file_path}: {str(e)}")
                results["failed"] += 1
        
        return results
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the knowledge base with memory.
        
        Args:
            question: User's question
            
        Returns:
            Response with answer, sources, and metadata
        """
        try:
            # Get retrieved documents for source citation
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
            retrieved_docs = retriever.invoke(question)
            
            # Generate answer using RAG chain
            answer = self.rag_chain.invoke(question)
            
            # Prepare sources
            sources = []
            for doc in retrieved_docs:
                sources.append({
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", None)
                })
            
            # Create chat entry
            chat_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "answer": answer,
                "sources": sources
            }
            
            # Add to chat history
            self.chat_history.append(chat_entry)
            self._save_chat_history()
            
            return {
                "answer": answer,
                "sources": sources,
                "chat_id": chat_entry["id"],
                "success": True
            }
            
        except Exception as e:
            return {
                "answer": f"I encountered an error: {str(e)}",
                "sources": [],
                "chat_id": None,
                "success": False,
                "error": str(e)
            }
    
    def get_chat_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get chat history, optionally limited to recent messages."""
        if limit:
            return self.chat_history[-limit:]
        return self.chat_history
    
    def clear_chat_history(self):
        """Clear all chat history."""
        self.chat_history = []
        self._save_chat_history()
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store."""
        try:
            collection = self.vector_store._collection
            return collection.count()
        except:
            return 0
    
    def list_sources(self) -> List[str]:
        """List all unique document sources in the knowledge base."""
        try:
            # Get all documents with metadata
            results = self.vector_store.get()
            sources = set()
            
            if results and 'metadatas' in results:
                for metadata in results['metadatas']:
                    if metadata and 'source' in metadata:
                        sources.add(metadata['source'])
            
            return sorted(list(sources))
        except:
            return []


def test_rag_system():
    """Test function for the RAG system."""
    print("Testing Personal Knowledge Vault...")
    
    # Initialize system
    vault = PersonalKnowledgeVault()
    
    # Test query (should work even with empty knowledge base)
    result = vault.query("What is artificial intelligence?")
    print(f"Query result: {result}")
    
    print("RAG system test completed!")


if __name__ == "__main__":
    test_rag_system()

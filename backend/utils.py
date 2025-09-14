"""
Document processing utilities for the RAG system.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document upload and validation."""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.doc', '.md'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def is_supported_file(cls, filename: str) -> bool:
        """Check if file type is supported."""
        return Path(filename).suffix.lower() in cls.SUPPORTED_EXTENSIONS
    
    @classmethod
    def validate_file_size(cls, file_path: str) -> bool:
        """Check if file size is within limits."""
        try:
            return os.path.getsize(file_path) <= cls.MAX_FILE_SIZE
        except OSError:
            return False
    
    @classmethod
    def save_uploaded_file(cls, uploaded_file, upload_dir: str) -> str:
        """
        Save uploaded file to disk and return the file path.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            upload_dir: Directory to save the file
            
        Returns:
            Path to the saved file
        """
        upload_path = Path(upload_dir)
        upload_path.mkdir(exist_ok=True)
        
        # Create safe filename
        safe_filename = "".join(c for c in uploaded_file.name if c.isalnum() or c in '._- ')
        file_path = upload_path / safe_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return str(file_path)
    
    @classmethod
    def get_file_info(cls, file_path: str) -> Dict[str, Any]:
        """Get file metadata."""
        path = Path(file_path)
        
        try:
            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "extension": path.suffix.lower(),
                "modified": stat.st_mtime
            }
        except OSError:
            return {"error": "Could not read file info"}


class ChatHistoryManager:
    """Manages chat history operations."""
    
    @staticmethod
    def format_chat_for_display(chat_history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format chat history for Streamlit display."""
        formatted = []
        
        for entry in chat_history:
            formatted.append({
                "role": "user", 
                "content": entry["question"],
                "timestamp": entry.get("timestamp", "")
            })
            formatted.append({
                "role": "assistant", 
                "content": entry["answer"],
                "sources": entry.get("sources", [])
            })
        
        return formatted
    
    @staticmethod
    def export_chat_history(chat_history: List[Dict[str, Any]], format: str = "txt") -> str:
        """Export chat history to text format."""
        if format == "txt":
            lines = []
            for entry in chat_history:
                lines.append(f"Q: {entry['question']}")
                lines.append(f"A: {entry['answer']}")
                if entry.get('sources'):
                    lines.append("Sources:")
                    for source in entry['sources']:
                        lines.append(f"  - {source.get('source', 'Unknown')}")
                lines.append("-" * 50)
            return "\n".join(lines)
        
        return "Unsupported export format"


def create_sample_document():
    """Create a sample document for testing."""
    sample_content = """
# Sample Knowledge Document

This is a sample document for testing the Personal Knowledge Vault.

## What is Artificial Intelligence?

Artificial Intelligence (AI) refers to the simulation of human intelligence in machines 
that are programmed to think and learn like humans. The term may also be applied to any 
machine that exhibits traits associated with a human mind such as learning and problem-solving.

## Key Features of AI:

1. **Machine Learning**: The ability to automatically learn and improve from experience
2. **Natural Language Processing**: Understanding and generating human language
3. **Computer Vision**: Interpreting and understanding visual information
4. **Robotics**: Physical interaction with the environment

## Applications:

- Healthcare diagnosis and treatment
- Autonomous vehicles
- Financial trading
- Personal assistants
- Search engines

This document serves as a basic knowledge base entry for testing retrieval capabilities.
"""
    
    return sample_content


if __name__ == "__main__":
    # Test document processor
    print("Testing Document Processor...")
    
    # Test file type validation
    test_files = ["test.pdf", "document.txt", "image.jpg", "data.docx"]
    for file in test_files:
        supported = DocumentProcessor.is_supported_file(file)
        print(f"{file}: {'Supported' if supported else 'Not supported'}")
    
    print("Document processor test completed!")

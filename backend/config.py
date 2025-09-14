"""
Configuration and setup for the Personal Knowledge Vault.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the RAG system."""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    
    # Model settings
    EMBEDDING_MODEL = "models/embedding-001"
    LLM_MODEL = "gemini-1.5-flash"
    LLM_TEMPERATURE = 0.1
    
    # Chunking settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Retrieval settings
    RETRIEVAL_K = 4
    
    # File limits
    MAX_FILE_SIZE_MB = 10
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.doc', '.md'}
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    STORAGE_DIR = PROJECT_ROOT / "storage"
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.STORAGE_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_api_keys(cls):
        """Validate required API keys."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "Google API key is required. Set GOOGLE_API_KEY environment variable."
            )
    
    @classmethod
    def get_storage_path(cls) -> str:
        """Get the storage directory path."""
        return str(cls.STORAGE_DIR)


def check_dependencies():
    """Check if all required dependencies are installed."""
    missing_deps = []
    
    try:
        import langchain
    except ImportError:
        missing_deps.append("langchain")
    
    try:
        import streamlit
    except ImportError:
        missing_deps.append("streamlit")
    
    try:
        import chromadb
    except ImportError:
        missing_deps.append("chromadb")
    
    if missing_deps:
        raise ImportError(f"Missing dependencies: {', '.join(missing_deps)}")
    
    return True


def setup_environment():
    """Setup the environment for the application."""
    # Create directories
    Config.setup_directories()
    
    # Check dependencies
    check_dependencies()
    
    # Validate API keys (warn but don't fail)
    try:
        Config.validate_api_keys()
        return True
    except ValueError as e:
        print(f"Warning: {e}")
        return False
if __name__ == "__main__":
    print("🔧 Checking environment setup...")
    
    try:
        has_api_key = setup_environment()
        print("✅ Environment setup complete!")
        
        if has_api_key:
            print("✅ API keys configured")
        else:
            print("⚠️ API keys need to be configured")
            print("📝 Please set GOOGLE_API_KEY in your environment or .env file")
            print("🔗 Get your API key from: https://aistudio.google.com/app/apikey")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("💡 Try running: pip install -r requirements.txt")

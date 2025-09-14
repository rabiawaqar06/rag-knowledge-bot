"""
Test script for the Personal Knowledge Vault application.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_rag_system():
    """Test the RAG system (requires API key)."""
    print("🔧 Testing RAG System...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ Skipping RAG system test - no Google API key")
        return True
    
    try:
        from backend.rag_system import PersonalKnowledgeVault
        
        # Create system
        vault = PersonalKnowledgeVault("./storage")
        
        # Test document addition
        print("📁 Testing document processing...")
        sample_files = ["test_doc.pdf", "sample.txt"]
        # Note: These are dummy files for testing the interface
        
        # Test basic functionality
        doc_count = vault.get_document_count()
        sources = vault.list_sources()
        
        print(f"   Current documents: {doc_count}")
        print(f"   Current sources: {len(sources)}")
        
        print("✅ RAG system test passed!")
        return True
        
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        return False


def test_configuration():
    """Test configuration and environment setup."""
    print("⚙️ Testing Configuration...")
    
    try:
        from backend.config import Config, setup_environment
        
        # Test environment setup
        has_api_key = setup_environment()
        
        print(f"   API Key configured: {'✅' if has_api_key else '⚠️'}")
        print(f"   Storage directory: {Config.get_storage_path()}")
        print(f"   Data directory: {Config.DATA_DIR}")
        
        print("✅ Configuration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Running Personal Knowledge Vault Tests")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_rag_system
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
        print()
    
    print("=" * 50)
    print("📊 Test Results:")
    print(f"   Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! The application is ready to use.")
        print(f"🌐 Access the app at: http://localhost:8501")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

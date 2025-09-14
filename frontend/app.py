"""
Personal Knowledge Vault - Streamlit Frontend
A RAG application with memory for personal knowledge management using Google Gemini.
"""

import streamlit as st
import sys
import os
from pathlib import Path
import tempfile
import json
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

# Configure page
st.set_page_config(
    page_title="Personal Knowledge Vault",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #28a745;
    }
    .assistant-message {
        background-color: #ffffff;
        border-left-color: #1f77b4;
    }
    .source-box {
        background-color: #f8f9fa;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 0.25rem;
        border: 1px solid #dee2e6;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def initialize_rag_system():
    """Initialize the RAG system with error handling."""
    try:
        from rag_system import PersonalKnowledgeVault
        
        if st.session_state.rag_system is None:
            with st.spinner("Initializing Knowledge Vault..."):
                st.session_state.rag_system = PersonalKnowledgeVault(
                    storage_path="./storage"
                )
        return True
    except Exception as e:
        st.error(f"Failed to initialize RAG system: {str(e)}")
        return False


def render_sidebar():
    """Render the sidebar with document upload and system info."""
    st.sidebar.markdown("## 📚 Knowledge Management")
    
    # Document upload section
    st.sidebar.markdown("### Upload Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Choose files to add to your knowledge base",
        type=['pdf', 'txt', 'docx', 'md'],
        accept_multiple_files=True,
        help="Supported formats: PDF, TXT, DOCX, MD"
    )
    
    if uploaded_files:
        if st.sidebar.button("Process Documents", type="primary"):
            process_uploaded_files(uploaded_files)
    
    # Knowledge base info
    st.sidebar.markdown("### 📊 Knowledge Base Stats")
    if st.session_state.rag_system:
        doc_count = st.session_state.rag_system.get_document_count()
        sources = st.session_state.rag_system.list_sources()
        
        st.sidebar.metric("Documents", doc_count)
        st.sidebar.metric("Sources", len(sources))
        
        if sources:
            st.sidebar.markdown("**Sources:**")
            for source in sources[:10]:  # Show max 10 sources
                st.sidebar.text(f"• {source}")
            if len(sources) > 10:
                st.sidebar.text(f"... and {len(sources) - 10} more")
    
    # Chat management
    st.sidebar.markdown("### 💬 Chat Management")
    
    if st.sidebar.button("Clear Chat History"):
        if st.session_state.rag_system:
            st.session_state.rag_system.clear_chat_history()
        st.session_state.chat_history = []
        st.rerun()
    
    if st.sidebar.button("Export Chat History"):
        export_chat_history()
    
    # System settings
    st.sidebar.markdown("### ⚙️ Settings")
    
    # API key check
    api_key_status = "✅ Set" if os.getenv("GOOGLE_API_KEY") else "❌ Missing"
    st.sidebar.text(f"Google API Key: {api_key_status}")


def process_uploaded_files(uploaded_files):
    """Process uploaded files and add them to the knowledge base."""
    if not st.session_state.rag_system:
        st.error("RAG system not initialized")
        return
    
    # Create temporary directory for uploaded files
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    try:
        # Save uploaded files
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)
        
        # Process files
        with st.spinner(f"Processing {len(file_paths)} documents..."):
            results = st.session_state.rag_system.add_documents(file_paths)
        
        # Show results
        if results["processed"] > 0:
            st.success(f"Successfully processed {results['processed']} documents!")
        
        if results["failed"] > 0:
            st.warning(f"Failed to process {results['failed']} documents")
            for error in results["errors"]:
                st.error(error)
    
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
    
    finally:
        # Cleanup temporary files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def render_chat_interface():
    """Render the main chat interface."""
    st.markdown('<div class="main-header">📚 Personal Knowledge Vault</div>', 
                unsafe_allow_html=True)
    
    # Chat input
    user_question = st.chat_input("Ask me anything about your documents...")
    
    if user_question:
        handle_user_question(user_question)
    
    # Display chat history
    display_chat_history()


def handle_user_question(question: str):
    """Handle user question and generate response."""
    if not st.session_state.rag_system:
        st.error("Please wait for the system to initialize.")
        return
    
    # Get response from RAG system
    with st.spinner("Thinking..."):
        response = st.session_state.rag_system.query(question)
    
    # Update session state
    st.session_state.chat_history = st.session_state.rag_system.get_chat_history()
    
    # Show error if query failed
    if not response.get("success", True):
        st.error(f"Query failed: {response.get('error', 'Unknown error')}")
    
    st.rerun()


def display_chat_history():
    """Display the chat history."""
    if not st.session_state.chat_history:
        st.info("👋 Welcome! Upload some documents and start asking questions about them.")
        
        # Show sample questions if no history
        st.markdown("### 💡 Sample Questions")
        sample_questions = [
            "What are the main topics in my documents?",
            "Can you summarize the key points?",
            "What does the document say about [specific topic]?",
            "Compare different viewpoints mentioned in the documents"
        ]
        
        for question in sample_questions:
            if st.button(question, key=f"sample_{question}"):
                handle_user_question(question)
        
        return
    
    # Display chat messages
    for entry in st.session_state.chat_history:
        # User message
        with st.chat_message("user"):
            st.write(entry["question"])
            st.caption(f"🕒 {format_timestamp(entry.get('timestamp'))}")
        
        # Assistant message
        with st.chat_message("assistant"):
            st.write(entry["answer"])
            
            # Show sources if available
            if entry.get("sources"):
                with st.expander(f"📖 Sources ({len(entry['sources'])})", expanded=False):
                    for i, source in enumerate(entry["sources"], 1):
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>Source {i}:</strong> {source.get('source', 'Unknown')}<br>
                            <em>Content:</em> {source.get('content', '')[:200]}...
                        </div>
                        """, unsafe_allow_html=True)


def export_chat_history():
    """Export chat history as downloadable file."""
    if not st.session_state.chat_history:
        st.warning("No chat history to export")
        return
    
    # Format chat history for export
    export_data = []
    for entry in st.session_state.chat_history:
        export_data.append({
            "timestamp": entry.get("timestamp"),
            "question": entry["question"],
            "answer": entry["answer"],
            "sources": [s.get("source", "Unknown") for s in entry.get("sources", [])]
        })
    
    # Create downloadable file
    export_text = json.dumps(export_data, indent=2)
    
    st.download_button(
        label="📥 Download Chat History",
        data=export_text,
        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str


def create_sample_environment():
    """Create sample documents for testing."""
    sample_content = """
# Personal Knowledge Base - Getting Started

Welcome to your Personal Knowledge Vault! This is a sample document to help you get started.

## What is this system?

This is a Retrieval-Augmented Generation (RAG) system that allows you to:
- Upload your personal documents (PDFs, text files, etc.)
- Ask questions about the content
- Get answers with source citations
- Maintain conversation history

## How to use:

1. **Upload Documents**: Use the sidebar to upload PDF, TXT, DOCX, or Markdown files
2. **Ask Questions**: Type questions in the chat interface
3. **Review Sources**: Expand the sources section to see where answers came from
4. **Continue Conversations**: The system remembers context from previous questions

## Example Questions:

- "What are the main topics covered?"
- "Can you summarize the key points?"
- "Tell me about [specific topic]"

## Tips:

- Upload multiple related documents for comprehensive knowledge
- Ask follow-up questions for deeper insights
- Use the export feature to save your conversations

Happy learning!
"""
    
    # Create sample file
    sample_dir = Path("./data")
    sample_dir.mkdir(exist_ok=True)
    
    sample_file = sample_dir / "getting_started.md"
    with open(sample_file, 'w') as f:
        f.write(sample_content)
    
    return str(sample_file)


def main():
    """Main application function."""
    initialize_session_state()
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("""
        🔑 **Google API Key Required**
        
        Please set your Google API key as an environment variable:
        ```bash
        export GOOGLE_API_KEY="your-api-key-here"
        ```
        
        Or create a `.env` file in the project root with:
        ```
        GOOGLE_API_KEY=your-api-key-here
        ```
        
        🔗 Get your API key from: https://aistudio.google.com/app/apikey
        """)
        st.stop()
    
    # Initialize RAG system
    if not initialize_rag_system():
        st.stop()
    
    # Render interface
    render_sidebar()
    render_chat_interface()
    
    # Add sample document if knowledge base is empty
    if st.session_state.rag_system.get_document_count() == 0:
        with st.sidebar:
            if st.button("📝 Add Sample Document", help="Add a sample document to get started"):
                sample_file = create_sample_environment()
                results = st.session_state.rag_system.add_documents([sample_file])
                if results["processed"] > 0:
                    st.success("Sample document added! Try asking a question.")
                    st.rerun()


if __name__ == "__main__":
    main()

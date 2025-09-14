#!/bin/bash

# Startup script for Personal Knowledge Vault
# This sets up a demo environment and starts the application

echo "🚀 Starting Personal Knowledge Vault..."

# Navigate to project directory
cd /home/rabia/Documents/RAG

# Check if .env exists and has an API key
if [ ! -f ".env" ] || ! grep -q "GOOGLE_API_KEY=" .env || grep -q "your-api-key-here" .env; then
    echo "⚠️ No valid Google API key found in .env file"
    echo "📝 Please edit .env file and add your Google API key"
    echo "   Example: GOOGLE_API_KEY=your-key-here"
    echo ""
    echo "🔗 Get your API key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Install any missing packages
echo "📦 Checking dependencies..."
.venv/bin/python -c "
import sys
try:
    import streamlit, langchain, chromadb
    print('✅ All dependencies available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    print('💡 Run: pip install -r requirements.txt')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

echo "🌐 Starting Streamlit application..."
echo "📍 Access the app at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Start the application
.venv/bin/python -m streamlit run frontend/app.py --server.port 8501 --server.address localhost

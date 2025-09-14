#!/bin/bash

# Setup script for Personal Knowledge Vault

echo "🚀 Setting up Personal Knowledge Vault..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data storage

# Check for environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env file and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=your-api-key-here"
    echo ""
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the application:"
echo "   1. Activate the virtual environment: source venv/bin/activate"
echo "   2. Set your OpenAI API key in .env file"
echo "   3. Run: streamlit run frontend/app.py"
echo ""
echo "🌐 The app will open in your browser at http://localhost:8501"

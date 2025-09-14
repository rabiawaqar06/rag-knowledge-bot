# 📚 Personal Knowledge Vault

A RAG (Retrieval-Augmented Generation) application for building a personal knowledge vault with persistent chat memory using Google Gemini.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![Gemini](https://img.shields.io/badge/Powered%20by-Google%20Gemini-blue) ![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

## ✨ Features

- **📚 Document Upload**: PDF, DOCX, TXT, MD support
- **🔍 Smart Search**: AI-powered retrieval with source citations
- **💾 Chat Memory**: Persistent conversation history
- **🎨 Clean UI**: Modern Streamlit interface
- **� Source Citations**: Always shows document references

## 🚀 Quick Start

### 1. Setup
```bash
git clone https://github.com/rabiawaqar06/rag-knowledge-bot.git
cd rag-knowledge-bot
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env and add: GOOGLE_API_KEY=your-api-key-here
```
🔗 Get your API key: https://aistudio.google.com/app/apikey

### 3. Run
```bash
streamlit run frontend/app.py
```
Access at: **http://localhost:8501**

## 🏗️ Architecture

```
├── backend/           # RAG pipeline (Google Gemini + ChromaDB)
├── frontend/          # Streamlit web interface  
├── data/             # Document storage
└── storage/          # Vector database & chat history
```

## 🎯 Usage

1. **Upload**: Add your documents via sidebar
2. **Ask**: Type questions about your content
3. **Explore**: View AI responses with source citations
4. **Export**: Download chat history

## 🔧 Tech Stack

- **AI**: Google Gemini 1.5 Flash + Embeddings
- **Framework**: LangChain + Streamlit
- **Database**: ChromaDB
- **Processing**: PyPDF, python-docx

## � Requirements

- Python 3.8+
- Google API key
- 2GB RAM minimum

---

**Built with ❤️ for intelligent document exploration**

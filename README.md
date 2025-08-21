# 📄 AI Document Organizer

A modern, full-stack intelligent document organization system with advanced AI capabilities for Ethiopian languages (Amharic, Afaan Oromo) and English. Built with React frontend and FastAPI backend, this application helps you organize, search, and manage your documents using AI-powered classification and OCR.

## 🌟 Features

### 🌐 Modern Full-Stack Architecture
- **React Frontend**: Modern, responsive web interface with Tailwind CSS
- **FastAPI Backend**: High-performance Python API with automatic documentation
- **RESTful API**: Clean, well-documented API endpoints

### 📚 Multilingual Document Processing
- **Ethiopian Languages**: Native support for Amharic (ፊደል) and Afaan Oromo
- **Advanced OCR**: Tesseract integration with multiple language packs
- **Format Support**: PDF, DOCX, XLSX, PPTX, and image files (PNG, JPG, TIFF, BMP)
- **Automatic Language Detection**: Smart detection of document languages

### 🤖 AI-Powered Intelligence
- **Hybrid Classification**: Combines rule-based and ML approaches
- **Semantic Search**: Vector-based similarity search with FAISS
- **Ethiopian NLP**: Specialized tokenization for Geez script
- **Confidence Scoring**: Transparent AI decision making

### 🔍 Advanced Search Capabilities
- **Dual-Mode Search**: Keyword and semantic search
- **Rich Filtering**: Category, tags, date ranges, and more
- **Real-time Results**: Fast, responsive search interface
- **Search Suggestions**: Intelligent autocomplete

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Tesseract OCR with language packs:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install tesseract-ocr tesseract-ocr-amh tesseract-ocr-eng
  
  # macOS (using Homebrew)
  brew install tesseract tesseract-lang
  ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-document-organizer.git
   cd ai-document-organizer
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

4. **Configuration** (Optional):
   ```bash
   # Create .env file in backend directory
   echo "DATABASE_URL=sqlite:///./data/documents.db" > backend/.env
   echo "SECRET_KEY=your-secret-key-here" >> backend/.env
   ```

### Running the Application

1. **Start the Backend** (from `backend/` directory):
   ```bash
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Start the Frontend** (from `frontend/` directory):
   ```bash
   npm start
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
ai-document-organizer/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── documents.py   # Document management
│   │   │   ├── search.py      # Search functionality
│   │   │   ├── upload.py      # File upload
│   │   │   └── health.py      # Health checks
│   │   ├── core/              # Core configuration
│   │   │   └── config.py      # Settings
│   │   ├── models/            # Data models
│   │   │   ├── document.py    # Document entities
│   │   │   └── schemas.py     # API schemas
│   │   ├── services/          # Business logic
│   │   │   ├── ai/            # AI/ML services
│   │   │   ├── processing/    # Document processing
│   │   │   ├── database/      # Database operations
│   │   │   └── nlp/           # Ethiopian language NLP
│   │   └── main.py           # FastAPI app entry
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React Frontend
│   ├── public/               # Static files
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── pages/           # Page components
│   │   ├── utils/           # API client
│   │   ├── App.js           # Main React app
│   │   └── index.js         # Entry point
│   └── package.json         # Node dependencies
├── WARP.md                  # WARP development guide
└── README.md               # This file
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Tesseract OCR for text recognition
- Streamlit for the web interface
- spaCy and scikit-learn for natural language processing
- The Ethiopian AI community for language support

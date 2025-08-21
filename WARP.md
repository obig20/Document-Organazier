# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AI Document Organizer is a modern, full-stack multilingual document management system with advanced AI capabilities for Ethiopian languages (Amharic, Afaan Oromo) and English. The system provides document processing, OCR, classification, and semantic search with a React frontend and FastAPI backend.

## Quick Start Commands

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install backend dependencies
pip install -r requirements.txt
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

### Running the Application
```bash
# Start backend server (from backend directory)
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Start frontend development server (from frontend directory)
cd frontend
npm start
```

### Development Commands
```bash
# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_classifier.py -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Run pre-commit hooks
pre-commit run --all-files
```

### Training and Testing
```bash
# Train Amharic classifier
python amharic_train_and_test.py

# Run individual test for classifier
python -m pytest tests/test_classifier.py::TestDocumentClassifier::test_train_and_ml_classification -v
```

## Architecture Overview

### Core Components

**Document Processing Pipeline:**
- `processing/document_processor.py` - Basic OCR and text extraction
- `processing/advanced_processor.py` - Enhanced processing with format conversion
- Supports PDF, DOCX, XLSX, PPTX, and images with multilingual OCR

**AI/ML Layer:**
- `ai/classifier.py` - Hybrid rule-based + ML document classification
- `ai/search_service.py` - Semantic and keyword search using FAISS + Whoosh
- `nlp/amharic_embeddings.py` - Specialized embeddings for low-resource Ethiopian languages
- `nlp/amharic_tokenizer.py` - Geez script tokenization and normalization

**Data Layer:**
- `database/database.py` - SQLite-based document storage with search indexing
- `models/document.py` - Document data models with metadata support

**Configuration:**
- `config/settings.py` - Basic application settings
- `config/enhanced_settings.py` - Advanced configuration with Pydantic models

### Key Architectural Patterns

**Multilingual Support:**
- Specialized handling for Amharic (Geez script), Oromo, and English
- Unicode normalization for Ethiopian character sets
- Cross-lingual embeddings with fallback to hash-based representations

**Hybrid Classification:**
- Rule-based classification using keyword matching
- ML-based classification with confidence scoring
- Automatic fallback between approaches based on confidence thresholds

**Search Architecture:**
- Dual-mode search: keyword (Whoosh) + semantic (FAISS + sentence-transformers)
- Document embeddings cached for fast similarity search
- Configurable similarity thresholds and result ranking

**Processing Strategy:**
- Document type detection via file extension and MIME analysis
- OCR fallback for scanned PDFs and images
- Tesseract integration with multiple language packs

## Development Patterns

### Adding New Document Categories
1. Update `DOCUMENT_CATEGORIES` in `config/settings.py`
2. Add relevant keywords for both rule-based and ML classification
3. Retrain classifier with `DocumentClassifier.train()` method

### Testing Document Processing
```python
from processing.document_processor import document_processor
from pathlib import Path

doc, content = document_processor.process_document(Path("test_file.pdf"))
```

### Training Custom Classifiers
```python
from ai.classifier import document_classifier

# Prepare training data
texts = ["document content 1", "document content 2"]
labels = ["category1", "category2"]

# Train and save model
document_classifier.train(texts, labels)
```

### Working with Ethiopian Languages
```python
from nlp.amharic_tokenizer import amharic_tokenizer
from nlp.amharic_embeddings import amharic_embeddings

# Tokenize Amharic text
tokens = amharic_tokenizer.extract_meaningful_words("አማርኛ ጽሑፍ")

# Generate embeddings
embedding = amharic_embeddings.get_sentence_embedding("አማርኛ ጽሑፍ")
```

## Critical Configuration

### Tesseract OCR Setup
- Install Tesseract with Ethiopian language packs: `tesseract-ocr-amh`, `tesseract-ocr-eng`
- Configure path in environment or system PATH
- Languages configured in `TESSERACT_CONFIG`: `['amh', 'orm', 'eng']`

### Database Configuration
- Default: SQLite at `data/documents.db`
- Enhanced config supports PostgreSQL via `DATABASE_URL` environment variable
- Automatic table creation with proper indexing for search performance

### ML Models
- Default sentence transformer: `all-MiniLM-L6-v2`
- Multilingual fallbacks for Ethiopian languages
- Model caching in `models/` directory

## File Structure Significance

```
backend/                    # FastAPI backend application
├── app/
│   ├── api/               # API route handlers
│   │   ├── documents.py   # Document CRUD operations
│   │   ├── search.py      # Search endpoints
│   │   ├── upload.py      # File upload handling
│   │   └── health.py      # Health checks
│   ├── core/              # Core configuration
│   │   └── config.py      # Application settings
│   ├── models/            # Data models
│   │   ├── document.py    # Document entity model
│   │   └── schemas.py     # Pydantic request/response schemas
│   ├── services/          # Business logic services
│   │   ├── ai/            # AI/ML components
│   │   ├── processing/    # Document processing
│   │   ├── database/      # Database operations
│   │   └── nlp/           # Ethiopian language processing
│   └── main.py           # FastAPI application entry point
├── requirements.txt       # Python dependencies

frontend/                  # React frontend application
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/            # Page components
│   ├── utils/            # Utility functions (API client)
│   ├── App.js            # Main React component
│   └── index.js          # Application entry point
├── public/               # Static files
└── package.json          # Node.js dependencies
```

## Important Implementation Details

**Document Classification Logic:**
- Rule-based classification runs first with configurable confidence threshold (0.8)
- ML classification used when rule-based confidence is low
- Automatic model persistence and loading via joblib

**Search Implementation:**
- FAISS index for semantic similarity with L2 distance
- Whoosh for keyword search with stemming analyzer
- Result fusion based on configurable similarity thresholds

**Ethiopian Language Support:**
- Geez Unicode ranges: 0x1200-0x137F, 0x1380-0x139F, 0x2D80-0x2DDF
- Custom punctuation and numeral normalization
- Language detection based on character script analysis

**Processing Error Handling:**
- Graceful degradation from direct text extraction to OCR
- Document status tracking: pending → processing → completed/error
- Error messages stored in document metadata

## Performance Considerations

- Document embeddings are cached in FAISS index for fast retrieval
- SQLite with proper indexing on category, tags, and dates
- Batch processing support for multiple document upload
- Configurable similarity thresholds to balance precision/recall

# 🚀 Development Guide

## Overview

This project has been restructured into a modern, full-stack application with clear separation between frontend and backend components. The structure is now more maintainable, scalable, and human-friendly.

## 🏗️ Project Architecture

### Backend (FastAPI)
- **Location**: `backend/`
- **Framework**: FastAPI with automatic OpenAPI documentation
- **Database**: SQLite with SQLAlchemy (configurable for PostgreSQL)
- **AI/ML**: Scikit-learn, sentence-transformers, FAISS
- **OCR**: Tesseract with Ethiopian language support

### Frontend (React)
- **Location**: `frontend/`
- **Framework**: React with React Router
- **Styling**: Tailwind CSS
- **State Management**: React Query for server state
- **UI Components**: Headless UI with Heroicons

## 🔧 Development Commands

### Backend Development

```bash
# Navigate to backend
cd backend

# Start development server
python -m uvicorn app.main:app --reload

# Install new dependencies
pip install package-name
pip freeze > requirements.txt

# Run tests (when test directory is added)
pytest tests/ -v

# Format code
black app/
```

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Start development server
npm start

# Install new dependencies
npm install package-name

# Build for production
npm run build

# Run tests (when tests are added)
npm test
```

## 📂 Key Components

### Backend Services

1. **Document Service** (`app/services/document_service.py`)
   - Handles document CRUD operations
   - Manages file processing workflows
   - Integrates with AI classification

2. **Search Service** (`app/services/search_service.py`)
   - Provides semantic and keyword search
   - Manages search indexing
   - Handles query processing

3. **AI Services** (`app/services/ai/`)
   - Document classification (hybrid approach)
   - Ethiopian language processing
   - Embedding generation

### Frontend Components

1. **Layout** (`src/components/Layout.js`)
   - Main application shell
   - Navigation sidebar
   - Responsive design

2. **Dashboard** (`src/pages/Dashboard.js`)
   - System statistics
   - Recent documents
   - Quick actions

3. **API Client** (`src/utils/api.js`)
   - Centralized API communication
   - Request/response handling
   - Error management

## 🛠️ Adding New Features

### Backend API Endpoint

1. Create route handler in `backend/app/api/`
2. Add Pydantic schemas in `backend/app/models/schemas.py`
3. Implement business logic in `backend/app/services/`
4. Update main router in `backend/app/main.py`

### Frontend Page/Component

1. Create component in `frontend/src/components/` or `frontend/src/pages/`
2. Add routing in `frontend/src/App.js`
3. Integrate API calls using the client in `frontend/src/utils/api.js`
4. Style with Tailwind CSS classes

## 🔍 Ethiopian Language Support

The system includes specialized support for Ethiopian languages:

- **Geez Script Processing**: Unicode normalization for Amharic text
- **Tokenization**: Custom tokenizer for Ethiopian languages
- **OCR Integration**: Tesseract with Amharic language packs
- **Search**: Semantic search works with multilingual content

## 🧪 Testing Strategy

### Backend Testing
- Unit tests for services and utilities
- Integration tests for API endpoints
- Database tests with test fixtures

### Frontend Testing
- Component tests with React Testing Library
- Integration tests for user workflows
- E2E tests with testing framework

## 📱 UI/UX Considerations

- **Responsive Design**: Works on desktop and mobile
- **Accessibility**: ARIA labels and keyboard navigation
- **Ethiopian Languages**: Proper display of Geez script
- **Performance**: Lazy loading and optimized bundles

## 🚀 Deployment

### Backend Deployment
```bash
# Build Docker image
docker build -t ai-doc-organizer-backend ./backend

# Or use pip for direct deployment
pip install -r backend/requirements.txt
```

### Frontend Deployment
```bash
# Build production assets
cd frontend && npm run build

# Serve static files or deploy to CDN
```

## 🔐 Security Considerations

- API authentication and authorization
- File upload validation and sanitization  
- Input sanitization for search queries
- Secure storage of sensitive configuration

## 📈 Performance Optimization

- Database indexing for search operations
- Caching of AI model predictions
- Frontend code splitting and lazy loading
- Optimized image and document processing

## 🤝 Contributing

1. Follow the established project structure
2. Add tests for new features
3. Update documentation
4. Use consistent code formatting (Black for Python, Prettier for JavaScript)
5. Create meaningful commit messages

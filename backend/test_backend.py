#!/usr/bin/env python3
"""
Simple backend test script
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing imports...")
    
    try:
        from app.core.config import settings
        print("✓ Config imported")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from app.models.document import Document, DocumentMetadata
        print("✓ Document models imported")
    except Exception as e:
        print(f"✗ Document models import failed: {e}")
        return False
    
    try:
        from app.services.database.database import Database
        print("✓ Database imported")
    except Exception as e:
        print(f"✗ Database import failed: {e}")
        return False
    
    try:
        from app.services.processing.document_processor import DocumentProcessor
        print("✓ Document processor imported")
    except Exception as e:
        print(f"✗ Document processor import failed: {e}")
        return False
    
    try:
        from app.services.ai.classifier import DocumentClassifier
        print("✓ Classifier imported")
    except Exception as e:
        print(f"✗ Classifier import failed: {e}")
        return False
    
    try:
        from app.services.nlp.language import detect_language
        print("✓ Language detection imported")
    except Exception as e:
        print(f"✗ Language detection import failed: {e}")
        return False
    
    try:
        from app.services.nlp.keyphrases import extract_key_phrases
        print("✓ Keyphrase extraction imported")
    except Exception as e:
        print(f"✗ Keyphrase extraction import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from app.core.config import settings
        print(f"✓ Data directory: {settings.DATA_DIR}")
        print(f"✓ Upload directory: {settings.UPLOAD_DIR}")
        print(f"✓ Storage directory: {settings.STORAGE_DIR}")
        print(f"✓ Supported extensions: {settings.SUPPORTED_EXTENSIONS}")
        print(f"✓ Categories: {list(settings.DOCUMENT_CATEGORIES.keys())}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_database():
    """Test database operations"""
    print("\nTesting database...")
    
    try:
        from app.services.database.database import Database
        from app.models.document import Document
        
        db = Database()
        print("✓ Database initialized")
        
        # Test creating a document
        doc = Document(
            filename="test.txt",
            original_path="/tmp/test.txt",
            content="This is a test document about housing lease.",
            category="housing",
            confidence_score=0.8
        )
        
        doc_id = db.add_document(doc)
        print(f"✓ Document added with ID: {doc_id}")
        
        # Test retrieving the document
        retrieved_doc = db.get_document(doc_id)
        if retrieved_doc and retrieved_doc.filename == "test.txt":
            print("✓ Document retrieved successfully")
        else:
            print("✗ Document retrieval failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_classifier():
    """Test document classification"""
    print("\nTesting classifier...")
    
    try:
        from app.services.ai.classifier import DocumentClassifier
        from app.models.document import Document
        
        classifier = DocumentClassifier()
        
        # Test rule-based classification
        test_doc = Document(
            filename="lease.txt",
            content="This is a housing lease agreement between tenant and landlord.",
            category="other"
        )
        
        category, confidence = classifier.classify_document(test_doc)
        print(f"✓ Classification result: {category} (confidence: {confidence:.3f})")
        
        return True
    except Exception as e:
        print(f"✗ Classifier test failed: {e}")
        return False

def test_nlp():
    """Test NLP features"""
    print("\nTesting NLP features...")
    
    try:
        from app.services.nlp.language import detect_language
        from app.services.nlp.keyphrases import extract_key_phrases
        
        test_text = "This is a test document about housing lease and tenant details."
        
        # Test language detection
        lang, conf = detect_language(test_text)
        print(f"✓ Language detection: {lang} (confidence: {conf:.3f})")
        
        # Test keyphrase extraction
        phrases = extract_key_phrases(test_text, top_k=5)
        print(f"✓ Key phrases: {phrases}")
        
        return True
    except Exception as e:
        print(f"✗ NLP test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Backend Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_classifier,
        test_nlp
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Backend is ready.")
        return 0
    else:
        print("✗ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

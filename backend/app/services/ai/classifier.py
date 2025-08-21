"""
Document Classifier for AI Document Organizer
Uses both rule-based and ML-based approaches for document categorization
"""
import os
import re
import logging
from typing import Dict, List, Tuple

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import LinearSVC
    from sklearn.pipeline import Pipeline
    from sklearn.calibration import CalibratedClassifierCV
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    np = None
    TfidfVectorizer = None
    LinearSVC = None
    Pipeline = None
    CalibratedClassifierCV = None
    joblib = None

from app.core.config import settings
from app.models.document import Document

logger = logging.getLogger(__name__)

class DocumentClassifier:
    def __init__(self, model_path: str = None):
        """Initialize the document classifier"""
        self.categories = list(settings.DOCUMENT_CATEGORIES.keys())
        self.rule_based_threshold = 0.8  # Confidence threshold to trust rule-based classification
        self.model_path = model_path or os.path.join('models', 'classifier.joblib')
        self.vectorizer = None
        self.classifier = None
        if SKLEARN_AVAILABLE:
            self._initialize_ml_model()
    
    def _initialize_ml_model(self):
        """Initialize the ML model for classification"""
        if not SKLEARN_AVAILABLE:
            return
            
        try:
            if os.path.exists(self.model_path):
                self.vectorizer, self.classifier = joblib.load(self.model_path)
            else:
                # Initialize a new model if none exists
                self.vectorizer = TfidfVectorizer(
                    max_features=5000,
                    ngram_range=(1, 2),
                    stop_words=None,  # Important for multilingual support
                    min_df=2
                )
                self.classifier = Pipeline([
                    ('tfidf', self.vectorizer),
                    ('clf', CalibratedClassifierCV(
                        LinearSVC(dual=False, max_iter=10000),
                        cv=3,
                        n_jobs=-1
                    ))
                ])
        except Exception as e:
            logger.error(f"Error initializing ML model: {e}")
            self.vectorizer = None
            self.classifier = None
    
    def classify_document(self, document: Document) -> Tuple[str, float]:
        """
        Classify a document using both rule-based and ML approaches
        
        Args:
            document: Document object containing text content
            
        Returns:
            Tuple of (category, confidence_score)
        """
        if not document.content:
            return "other", 0.0
        
        # First try rule-based classification
        rule_based_category, rule_confidence = self._rule_based_classification(document.content)
        
        # If rule-based confidence is high, use it
        if rule_confidence >= self.rule_based_threshold:
            return rule_based_category, rule_confidence
        
        # Otherwise, use ML-based classification if available
        if self.classifier is not None and SKLEARN_AVAILABLE:
            try:
                ml_category, ml_confidence = self._ml_classification(document.content)
                
                # If ML confidence is higher than rule-based, use it
                if ml_confidence > rule_confidence:
                    return ml_category, ml_confidence
            except Exception as e:
                logger.warning(f"ML classification failed: {e}")
        
        # Fall back to rule-based or 'other'
        return rule_based_category, rule_confidence
    
    def _rule_based_classification(self, text: str) -> Tuple[str, float]:
        """
        Classify document using rule-based approach with keywords
        
        Returns:
            Tuple of (category, confidence_score)
        """
        if not text:
            return "other", 0.0
        
        text_lower = text.lower()
        scores = {category: 0.0 for category in self.categories}
        
        # Score each category based on keyword matches
        for category, config in settings.DOCUMENT_CATEGORIES.items():
            keywords = config.get('keywords', [])
            if not keywords:
                continue
                
            # Count keyword matches
            matches = sum(1 for keyword in keywords if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower))
            
            # Simple scoring: percentage of keywords matched
            if matches > 0:
                scores[category] = min(1.0, matches / len(keywords) * 2)  # Cap at 1.0
        
        # Get the best matching category
        best_category = max(scores.items(), key=lambda x: x[1])
        
        # If no good matches, default to 'other'
        if best_category[1] < 0.1:  # Threshold for minimum confidence
            return "other", 0.0
            
        return best_category
    
    def _ml_classification(self, text: str) -> Tuple[str, float]:
        """
        Classify document using the trained ML model
        
        Returns:
            Tuple of (category, confidence_score)
        """
        if not text or not self.classifier or not SKLEARN_AVAILABLE:
            return "other", 0.0
        
        try:
            # Get probabilities for each class
            probas = self.classifier.predict_proba([text])[0]
            
            # Get the class with highest probability
            max_idx = np.argmax(probas)
            confidence = float(probas[max_idx])
            category = self.classifier.classes_[max_idx]
            
            return category, confidence
            
        except Exception as e:
            logger.error(f"Error in ML classification: {e}")
            return "other", 0.0
    
    def train(self, texts: List[str], labels: List[str]):
        """
        Train or update the ML model with new data
        
        Args:
            texts: List of document texts
            labels: List of corresponding category labels
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("Sklearn not available - cannot train ML model")
            return
            
        if not texts or not labels or len(texts) != len(labels):
            raise ValueError("Texts and labels must be non-empty and of equal length")
        
        try:
            # Initialize model if needed
            if self.classifier is None:
                self._initialize_ml_model()
            
            # Train the model
            self.classifier.fit(texts, labels)
            
            # Save the trained model
            os.makedirs(os.path.dirname(self.model_path) or '.', exist_ok=True)
            joblib.dump((self.vectorizer, self.classifier), self.model_path)
            
            logger.info(f"Model trained and saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def evaluate(self, texts: List[str], labels: List[str]) -> Dict[str, float]:
        """
        Evaluate the classifier on test data
        
        Returns:
            Dictionary of evaluation metrics
        """
        if not self.classifier or not SKLEARN_AVAILABLE:
            return {"error": "No trained model available"}
        
        try:
            from sklearn.metrics import accuracy_score, classification_report
            
            predictions = self.classifier.predict(texts)
            accuracy = accuracy_score(labels, predictions)
            report = classification_report(labels, predictions, output_dict=True)
            
            return {
                "accuracy": accuracy,
                **report
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {"error": str(e)}

# Singleton instance
document_classifier = DocumentClassifier()

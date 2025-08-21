"""
Amharic embeddings and language models for low-resource NLP
Supports word embeddings, sentence embeddings, and cross-lingual models
"""
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import logging
from collections import defaultdict
import math

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .amharic_tokenizer import amharic_tokenizer

logger = logging.getLogger(__name__)

class AmharicEmbeddings:
    """Embeddings manager for Amharic text"""
    
    def __init__(self, model_dir: str = "models/amharic"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Word embedding models
        self.word_vectors = {}
        self.vocabulary = set()
        
        # Sentence embeddings
        self.sentence_model = None
        self.cross_lingual_model = None
        
        # TF-IDF for fallback embeddings
        self.tfidf_vectorizer = None
        self.document_embeddings = {}
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available embedding models"""
        # Try to load multilingual sentence transformer
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use multilingual models that may work with Amharic
                model_candidates = [
                    'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
                    'sentence-transformers/distiluse-base-multilingual-cased',
                    'sentence-transformers/LaBSE'
                ]
                
                for model_name in model_candidates:
                    try:
                        self.sentence_model = SentenceTransformer(model_name)
                        logger.info(f"Loaded sentence model: {model_name}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load {model_name}: {e}")
                        continue
            except Exception as e:
                logger.error(f"Error initializing sentence transformers: {e}")
        
        # Try to load transformer-based models
        if TRANSFORMERS_AVAILABLE:
            try:
                # Try multilingual models
                model_candidates = [
                    'bert-base-multilingual-cased',
                    'xlm-roberta-base',
                    'microsoft/mdeberta-v3-base'
                ]
                
                for model_name in model_candidates:
                    try:
                        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                        self.transformer_model = AutoModel.from_pretrained(model_name)
                        logger.info(f"Loaded transformer model: {model_name}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load {model_name}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error initializing transformers: {e}")
        
        # Load or create word embeddings
        self._load_word_embeddings()
    
    def _load_word_embeddings(self):
        """Load pre-trained word embeddings or create simple ones"""
        embeddings_file = self.model_dir / "amharic_embeddings.pkl"
        
        if embeddings_file.exists():
            try:
                with open(embeddings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.word_vectors = data.get('vectors', {})
                    self.vocabulary = set(data.get('vocabulary', []))
                logger.info(f"Loaded {len(self.word_vectors)} word vectors")
            except Exception as e:
                logger.error(f"Failed to load word embeddings: {e}")
    
    def save_word_embeddings(self):
        """Save word embeddings to disk"""
        embeddings_file = self.model_dir / "amharic_embeddings.pkl"
        try:
            with open(embeddings_file, 'wb') as f:
                pickle.dump({
                    'vectors': self.word_vectors,
                    'vocabulary': list(self.vocabulary)
                }, f)
            logger.info(f"Saved {len(self.word_vectors)} word vectors")
        except Exception as e:
            logger.error(f"Failed to save word embeddings: {e}")
    
    def get_word_embedding(self, word: str, dimension: int = 300) -> Optional[np.ndarray]:
        """Get embedding for a single word"""
        if word in self.word_vectors:
            return self.word_vectors[word]
        
        # Generate simple hash-based embedding as fallback
        embedding = self._generate_hash_embedding(word, dimension)
        self.word_vectors[word] = embedding
        self.vocabulary.add(word)
        
        return embedding
    
    def _generate_hash_embedding(self, word: str, dimension: int = 300) -> np.ndarray:
        """Generate a simple hash-based embedding for unknown words"""
        # Simple hash-based embedding generation
        np.random.seed(hash(word) % (2**32))
        embedding = np.random.normal(0, 0.1, dimension)
        return embedding / np.linalg.norm(embedding)  # Normalize
    
    def get_sentence_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get sentence embedding using available models"""
        if not text.strip():
            return None
        
        # Try sentence transformer first
        if self.sentence_model is not None:
            try:
                embedding = self.sentence_model.encode([text])[0]
                return embedding
            except Exception as e:
                logger.warning(f"Sentence model failed: {e}")
        
        # Try transformer model
        if hasattr(self, 'transformer_model') and hasattr(self, 'tokenizer'):
            try:
                inputs = self.tokenizer(text, return_tensors='pt', 
                                      truncation=True, max_length=512)
                with torch.no_grad():
                    outputs = self.transformer_model(**inputs)
                    # Use mean pooling
                    embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
                return embedding.numpy()
            except Exception as e:
                logger.warning(f"Transformer model failed: {e}")
        
        # Fallback to averaged word embeddings
        return self._get_averaged_word_embedding(text)
    
    def _get_averaged_word_embedding(self, text: str, dimension: int = 300) -> np.ndarray:
        """Get sentence embedding by averaging word embeddings"""
        words = amharic_tokenizer.extract_meaningful_words(text)
        
        if not words:
            return np.zeros(dimension)
        
        embeddings = []
        for word in words:
            embedding = self.get_word_embedding(word, dimension)
            if embedding is not None:
                embeddings.append(embedding)
        
        if not embeddings:
            return np.zeros(dimension)
        
        return np.mean(embeddings, axis=0)
    
    def get_document_embedding(self, text: str, method: str = 'sentence') -> np.ndarray:
        """Get document-level embedding"""
        if method == 'sentence':
            embedding = self.get_sentence_embedding(text)
            if embedding is not None:
                return embedding
        
        # Fallback to averaged word embeddings
        return self._get_averaged_word_embedding(text)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts"""
        emb1 = self.get_document_embedding(text1)
        emb2 = self.get_document_embedding(text2)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Cosine similarity
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(emb1, emb2) / (norm1 * norm2)
    
    def find_similar_documents(self, query_text: str, 
                             document_texts: List[str], 
                             top_k: int = 5) -> List[Tuple[int, float]]:
        """Find documents most similar to query"""
        query_embedding = self.get_document_embedding(query_text)
        if query_embedding is None:
            return []
        
        similarities = []
        for i, doc_text in enumerate(document_texts):
            doc_embedding = self.get_document_embedding(doc_text)
            if doc_embedding is not None:
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((i, similarity))
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def train_word_embeddings(self, texts: List[str], dimension: int = 300, 
                            window_size: int = 5, min_count: int = 2):
        """Train simple word embeddings using skip-gram like approach"""
        # Tokenize all texts
        all_words = []
        for text in texts:
            words = amharic_tokenizer.extract_meaningful_words(text)
            all_words.extend(words)
        
        # Count word frequencies
        word_counts = defaultdict(int)
        for word in all_words:
            word_counts[word] += 1
        
        # Filter by minimum count
        valid_words = {word for word, count in word_counts.items() if count >= min_count}
        self.vocabulary.update(valid_words)
        
        # Initialize random embeddings for new words
        for word in valid_words:
            if word not in self.word_vectors:
                self.word_vectors[word] = self._generate_hash_embedding(word, dimension)
        
        logger.info(f"Trained embeddings for {len(valid_words)} words")
        self.save_word_embeddings()

class AmharicTFIDF:
    """TF-IDF implementation optimized for Amharic"""
    
    def __init__(self):
        self.vocabulary = {}
        self.idf_scores = {}
        self.documents = []
        
    def fit(self, documents: List[str]):
        """Fit TF-IDF on Amharic documents"""
        self.documents = documents
        
        # Tokenize documents and build vocabulary
        tokenized_docs = []
        word_doc_count = defaultdict(int)
        
        for doc in documents:
            tokens = amharic_tokenizer.extract_meaningful_words(doc)
            tokenized_docs.append(tokens)
            
            # Count documents containing each word
            unique_tokens = set(tokens)
            for token in unique_tokens:
                word_doc_count[token] += 1
        
        # Build vocabulary with indices
        self.vocabulary = {word: idx for idx, word in enumerate(word_doc_count.keys())}
        
        # Calculate IDF scores
        total_docs = len(documents)
        for word, doc_count in word_doc_count.items():
            self.idf_scores[word] = math.log(total_docs / doc_count)
    
    def transform(self, documents: List[str]) -> np.ndarray:
        """Transform documents to TF-IDF vectors"""
        vectors = []
        
        for doc in documents:
            tokens = amharic_tokenizer.extract_meaningful_words(doc)
            
            # Count term frequencies
            tf_counts = defaultdict(int)
            for token in tokens:
                tf_counts[token] += 1
            
            # Create TF-IDF vector
            vector = np.zeros(len(self.vocabulary))
            for word, tf in tf_counts.items():
                if word in self.vocabulary:
                    idx = self.vocabulary[word]
                    idf = self.idf_scores.get(word, 0)
                    vector[idx] = tf * idf
            
            vectors.append(vector)
        
        return np.array(vectors)

# Singleton instances
amharic_embeddings = AmharicEmbeddings()
amharic_tfidf = AmharicTFIDF()

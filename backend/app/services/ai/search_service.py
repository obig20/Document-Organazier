"""
Search Service
Provides both keyword and semantic search capabilities
"""
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import sqlite3
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from whoosh import index
    from whoosh.fields import Schema, TEXT, ID, DATETIME, NUMERIC, STORED
    from whoosh.analysis import StemmingAnalyzer, StandardAnalyzer
    from whoosh.qparser import QueryParser, MultifieldParser
    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False

from app.core.config import settings
from app.models.document import Document, SearchResult

logger = logging.getLogger(__name__)

class SearchService:
    """Handles both keyword and semantic search operations"""
    
    def __init__(self, index_dir: Optional[Path] = None):
        self.index_dir = index_dir or settings.DATA_DIR / "search_index"
        self.embedding_model = None
        self.embedding_dim = 384
        self.faiss_index = None
        self.doc_ids = []
        
        # Initialize only if dependencies are available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}")
        
        if WHOOSH_AVAILABLE:
            self._init_search_index()
        else:
            logger.warning("Whoosh not available - search functionality limited")
    
    def _init_search_index(self):
        """Initialize or load the search index"""
        if not WHOOSH_AVAILABLE:
            return
            
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Define schema for Whoosh index
        analyzer = StandardAnalyzer() | StemmingAnalyzer()
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            title=TEXT(analyzer=analyzer, stored=True),
            content=TEXT(analyzer=analyzer, stored=True),
            category=TEXT(stored=True),
            tags=STORED,  # Store as JSON string
            created_date=DATETIME(stored=True, sortable=True),
            updated_date=DATETIME(stored=True, sortable=True),
            embedding=STORED  # Store binary FAISS index separately
        )
        
        # Create or open the index
        if not index.exists_in(str(self.index_dir)):
            self.ix = index.create_in(str(self.index_dir), self.schema)
            logger.info("Created new search index")
        else:
            self.ix = index.open_dir(str(self.index_dir))
            logger.info("Opened existing search index")
        
        # Initialize FAISS index for semantic search
        if FAISS_AVAILABLE:
            self._init_faiss_index()
    
    def _init_faiss_index(self):
        """Initialize or load FAISS index for semantic search"""
        if not FAISS_AVAILABLE:
            return
            
        faiss_index_path = self.index_dir / "faiss_index.bin"
        doc_ids_path = self.index_dir / "doc_ids.json"
        
        if faiss_index_path.exists() and doc_ids_path.exists():
            # Load existing index
            self.faiss_index = faiss.read_index(str(faiss_index_path))
            with open(doc_ids_path, 'r') as f:
                self.doc_ids = json.load(f)
            logger.info(f"Loaded FAISS index with {len(self.doc_ids)} documents")
        else:
            # Create new index
            self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
            self.doc_ids = []
            logger.info("Created new FAISS index")
    
    def _save_faiss_index(self):
        """Save FAISS index to disk"""
        if not FAISS_AVAILABLE or self.faiss_index is None:
            return
            
        faiss.write_index(self.faiss_index, str(self.index_dir / "faiss_index.bin"))
        with open(self.index_dir / "doc_ids.json", 'w') as f:
            json.dump(self.doc_ids, f)
    
    def index_document(self, doc: Document) -> bool:
        """Index a single document"""
        if not WHOOSH_AVAILABLE:
            return False
            
        writer = self.ix.writer()
        
        try:
            # Add to Whoosh index
            writer.update_document(
                id=str(doc.id),
                title=doc.title or doc.filename,
                content=doc.content,
                category=doc.category,
                tags=json.dumps(doc.tags) if doc.tags else '[]',
                created_date=doc.created_date,
                updated_date=doc.updated_date or datetime.now()
            )
            
            # Add to FAISS index for semantic search
            if doc.content and FAISS_AVAILABLE and self.embedding_model:
                try:
                    # Generate embedding
                    embedding = self.embedding_model.encode(
                        doc.content,
                        convert_to_numpy=True,
                        show_progress_bar=False,
                        batch_size=32
                    )
                    
                    # Ensure 2D array (even for single document)
                    if len(embedding.shape) == 1:
                        embedding = embedding.reshape(1, -1)
                    
                    # Add to FAISS index
                    if self.faiss_index is None:
                        self._init_faiss_index()
                    
                    # Add to FAISS index
                    self.faiss_index.add(embedding.astype('float32'))
                    self.doc_ids.append(str(doc.id))
                except Exception as e:
                    logger.warning(f"Failed to add document to FAISS index: {e}")
            
            writer.commit()
            self._save_faiss_index()
            return True
            
        except Exception as e:
            logger.error(f"Error indexing document {doc.id}: {e}")
            writer.cancel()
            return False
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
        use_semantic: bool = True,
        similarity_threshold: float = 0.5
    ) -> List[SearchResult]:
        """
        Search documents using both keyword and semantic search
        
        Args:
            query: Search query string
            category: Filter by category
            tags: Filter by tags
            start_date: Filter by creation date (inclusive)
            end_date: Filter by creation date (inclusive)
            limit: Maximum number of results to return
            use_semantic: Whether to use semantic search
            similarity_threshold: Minimum similarity score for semantic search (0-1)
            
        Returns:
            List of SearchResult objects
        """
        if not WHOOSH_AVAILABLE:
            return []
            
        if not query.strip() and not (category or tags or start_date or end_date):
            # If no search criteria, return recent documents
            return self.get_recent_documents(limit=limit)
        
        if use_semantic and query.strip() and FAISS_AVAILABLE:
            # Use semantic search
            results = self._semantic_search(
                query=query,
                category=category,
                tags=tags,
                start_date=start_date,
                end_date=end_date,
                k=limit,
                similarity_threshold=similarity_threshold
            )
        else:
            # Fall back to keyword search
            results = self._keyword_search(
                query=query,
                category=category,
                tags=tags,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
        
        return results
    
    def _keyword_search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Perform keyword search using Whoosh"""
        if not WHOOSH_AVAILABLE:
            return []
            
        results = []
        
        try:
            with self.ix.searcher() as searcher:
                # Build query
                query_parts = []
                
                if query.strip():
                    # Search in both title and content
                    query_parser = MultifieldParser(["title", "content"], schema=self.schema)
                    query_parts.append(query_parser.parse(query))
                
                # Add filters
                if category:
                    query_parts.append(QueryParser("category", self.schema).parse(f'category:{category}'))
                
                if tags:
                    for tag in tags:
                        query_parts.append(QueryParser("tags", self.schema).parse(f'tags:{tag}'))
                
                if start_date or end_date:
                    date_filter = ""
                    if start_date:
                        date_filter += f'[{start_date.isoformat()} TO '
                    else:
                        date_filter += '[* TO '
                    
                    if end_date:
                        date_filter += f'{end_date.isoformat()}]'
                    else:
                        date_filter += ']'
                    
                    query_parts.append(QueryParser("created_date", self.schema).parse(f'created_date:{date_filter}'))
                
                # Combine queries
                if not query_parts:
                    # If no search criteria, return recent documents
                    return self.get_recent_documents(limit=limit)
                
                # Execute search
                search_results = searcher.search(query_parts[0], limit=limit)
                
                # Convert to SearchResult objects
                for hit in search_results:
                    results.append(SearchResult(
                        document_id=hit['id'],
                        score=hit.score,
                        highlights=hit.highlights("content") or "",
                        title=hit['title'],
                        snippet=self._create_snippet(hit['content'], query) if query.strip() else hit['content'][:200] + '...',
                        category=hit['category'],
                        created_date=hit['created_date']
                    ))
                
        except Exception as e:
            logger.error(f"Error performing keyword search: {e}")
        
        return results
    
    def _semantic_search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        k: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[SearchResult]:
        """Perform semantic search using FAISS and sentence transformers"""
        if not FAISS_AVAILABLE or not WHOOSH_AVAILABLE or self.faiss_index is None or not self.doc_ids:
            return []
        
        try:
            # Encode query
            query_embedding = self.embedding_model.encode(
                query,
                convert_to_numpy=True,
                show_progress_bar=False
            ).reshape(1, -1).astype('float32')
            
            # Search in FAISS index
            distances, indices = self.faiss_index.search(query_embedding, k=min(k * 2, len(self.doc_ids)))
            
            # Convert distances to similarities (1 - normalized distance)
            max_distance = np.max(distances) if np.max(distances) > 0 else 1.0
            similarities = 1.0 - (distances / max_distance)
            
            # Get document IDs and filter by similarity
            results = []
            with self.ix.searcher() as searcher:
                for idx, (doc_idx, similarity) in enumerate(zip(indices[0], similarities[0])):
                    if similarity < similarity_threshold:
                        continue
                    
                    if doc_idx < 0 or doc_idx >= len(self.doc_ids):
                        continue
                    
                    doc_id = self.doc_ids[doc_idx]
                    hit = searcher.document(id=doc_id)
                    
                    if not hit:
                        continue
                    
                    # Apply filters
                    if category and hit['category'] != category:
                        continue
                    
                    if tags:
                        doc_tags = json.loads(hit['tags'] or '[]')
                        if not any(tag in doc_tags for tag in tags):
                            continue
                    
                    if start_date and hit['created_date'] < start_date:
                        continue
                    
                    if end_date and hit['created_date'] > end_date:
                        continue
                    
                    # Add to results
                    results.append(SearchResult(
                        document_id=doc_id,
                        score=float(similarity),
                        highlights=self._highlight_query_terms(hit['content'], query),
                        title=hit['title'],
                        snippet=self._create_snippet(hit['content'], query),
                        category=hit['category'],
                        created_date=hit['created_date']
                    ))
                    
                    if len(results) >= k:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            return []
    
    def get_recent_documents(self, limit: int = 10) -> List[SearchResult]:
        """Get most recently added/updated documents"""
        if not WHOOSH_AVAILABLE:
            return []
            
        results = []
        
        try:
            with self.ix.searcher() as searcher:
                # Sort by updated_date descending, then by created_date descending
                results = searcher.search(
                    QueryParser("id", self.schema).parse('*'),
                    limit=limit,
                    sortedby=["-updated_date", "-created_date"]
                )
                
                return [
                    SearchResult(
                        document_id=hit['id'],
                        score=hit.score,
                        highlights="",
                        title=hit['title'],
                        snippet=hit['content'][:200] + '...',
                        category=hit['category'],
                        created_date=hit['created_date']
                    )
                    for hit in results
                ]
                
        except Exception as e:
            logger.error(f"Error fetching recent documents: {e}")
            return []
    
    def _create_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Create a text snippet with query terms highlighted"""
        if not query.strip():
            return text[:max_length] + ('...' if len(text) > max_length else '')
        
        # Simple implementation - find first occurrence of any query term
        query_terms = set(term.lower() for term in query.split() if len(term) > 2)
        
        if not query_terms:
            return text[:max_length] + ('...' if len(text) > max_length else '')
        
        # Find the first occurrence of any query term
        text_lower = text.lower()
        first_pos = len(text)
        
        for term in query_terms:
            pos = text_lower.find(term)
            if 0 <= pos < first_pos:
                first_pos = pos
        
        if first_pos == len(text):
            return text[:max_length] + ('...' if len(text) > max_length else '')
        
        # Create snippet around the first occurrence
        start = max(0, first_pos - max_length // 2)
        end = min(len(text), first_pos + max_length // 2)
        
        snippet = ''
        if start > 0:
            snippet += '...'
        
        snippet += text[start:end]
        
        if end < len(text):
            snippet += '...'
        
        return snippet
    
    def _highlight_query_terms(self, text: str, query: str) -> str:
        """Highlight query terms in text"""
        if not query.strip():
            return text
        
        # Simple implementation - wrap query terms in <mark> tags
        query_terms = set(term for term in query.split() if len(term) > 2)
        
        for term in query_terms:
            # Case-insensitive replacement
            text = text.replace(term, f'<mark>{term}</mark>')
            
            # Also try with first letter capitalized
            term_cap = term[0].upper() + term[1:]
            text = text.replace(term_cap, f'<mark>{term_cap}</mark>')
        
        return text

# Singleton instance
search_service = SearchService()

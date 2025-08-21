"""
Database module for AI Document Organizer
Handles all database operations using SQLite
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

from app.models.document import Document, DocumentMetadata, SearchResult
from app.core.config import settings

DATABASE_PATH = settings.DATABASE_URL.replace("sqlite:///", "")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or DATABASE_PATH
        self._create_tables()
    
    def _get_connection(self):
        """Create a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Documents table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_path TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                title TEXT,
                content TEXT,
                category TEXT,
                confidence_score REAL,
                tags TEXT,  -- JSON array of tags
                metadata TEXT,  -- JSON string of metadata
                created_date TIMESTAMP,
                updated_date TIMESTAMP,
                is_processed BOOLEAN,
                processing_status TEXT,
                error_message TEXT
            )
            ''')
            
            # Document versions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                version_number INTEGER,
                content TEXT,
                metadata TEXT,
                created_date TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
            ''')
            
            # Create indexes for better search performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_tags ON documents(tags)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_date)')
            
            # Feedback table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                was_correct BOOLEAN NOT NULL,
                correct_category TEXT,
                notes TEXT,
                created_date TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
            ''')
            
            conn.commit()
    
    def add_document(self, document: Document) -> int:
        """Add a new document to the database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert document to database format
            doc_dict = document.to_dict()
            
            cursor.execute('''
            INSERT INTO documents (
                filename, original_path, stored_path, title, content, 
                category, confidence_score, tags, metadata, 
                created_date, updated_date, is_processed, processing_status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_dict['filename'],
                doc_dict['original_path'],
                doc_dict['stored_path'],
                doc_dict['title'],
                doc_dict['content'],
                doc_dict['category'],
                doc_dict['confidence_score'],
                doc_dict['tags'],
                doc_dict['metadata'],
                doc_dict['created_date'],
                doc_dict['updated_date'],
                doc_dict['is_processed'],
                doc_dict['processing_status'],
                doc_dict['error_message']
            ))
            
            document_id = cursor.lastrowid
            conn.commit()
            return document_id
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """Retrieve a document by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return self._row_to_document(dict(row))
    
    def update_document(self, document: Document) -> bool:
        """Update an existing document"""
        if not document.id:
            raise ValueError("Document ID is required for update")
            
        doc_dict = document.to_dict()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE documents SET
                filename = ?,
                original_path = ?,
                stored_path = ?,
                title = ?,
                content = ?,
                category = ?,
                confidence_score = ?,
                tags = ?,
                metadata = ?,
                updated_date = ?,
                is_processed = ?,
                processing_status = ?,
                error_message = ?
            WHERE id = ?
            ''', (
                doc_dict['filename'],
                doc_dict['original_path'],
                doc_dict['stored_path'],
                doc_dict['title'],
                doc_dict['content'],
                doc_dict['category'],
                doc_dict['confidence_score'],
                doc_dict['tags'],
                doc_dict['metadata'],
                doc_dict['updated_date'],
                doc_dict['is_processed'],
                doc_dict['processing_status'],
                doc_dict['error_message'],
                document.id
            ))
            
            conn.commit()
            return cursor.rowcount > 0

    # Feedback operations
    def add_feedback(self, document_id: int, was_correct: bool, correct_category: Optional[str], notes: Optional[str]) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (document_id, was_correct, correct_category, notes, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (document_id, int(was_correct), correct_category, notes, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def get_feedback_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            stats: Dict[str, Any] = {}
            cursor.execute('SELECT COUNT(*) as total, SUM(was_correct) as correct FROM feedback')
            row = cursor.fetchone()
            total = row['total'] if row and row['total'] is not None else 0
            correct = row['correct'] if row and row['correct'] is not None else 0
            stats['total_feedback'] = total
            stats['accuracy'] = (correct / total) if total > 0 else 0.0

            # By-category accuracy
            cursor.execute('''
                SELECT d.category as category, COUNT(f.id) as total, SUM(f.was_correct) as correct
                FROM feedback f JOIN documents d ON d.id = f.document_id
                GROUP BY d.category
            ''')
            by_cat: Dict[str, float] = {}
            for r in cursor.fetchall():
                t = r['total'] if r['total'] is not None else 0
                c = r['correct'] if r['correct'] is not None else 0
                by_cat[r['category']] = (c / t) if t > 0 else 0.0
            stats['by_category_accuracy'] = by_cat
            return stats
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_documents(self, query: str, category: str = None, tags: List[str] = None, 
                        limit: int = 20, offset: int = 0) -> Tuple[List[SearchResult], int]:
        """Search documents with optional filters"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Base query
            sql = 'SELECT * FROM documents WHERE 1=1'
            params = []
            
            # Add filters
            if category:
                sql += ' AND category = ?'
                params.append(category)
                
            if tags:
                for tag in tags:
                    sql += ' AND tags LIKE ?'
                    params.append(f'%"{tag}"%')
            
            # Add full-text search if query is provided
            if query:
                # Simple LIKE search for now - can be enhanced with FTS5
                sql += ' AND (content LIKE ? OR title LIKE ? OR filename LIKE ?)'
                search_term = f'%{query}%'
                params.extend([search_term] * 3)
            
            # Add sorting and pagination
            sql += ' ORDER BY created_date DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            # Execute query
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert to Document objects
            documents = [self._row_to_document(dict(row)) for row in rows]
            
            # Get total count for pagination
            count_sql = 'SELECT COUNT(*) as count FROM documents WHERE 1=1'
            if category:
                count_sql += ' AND category = ?'
            if tags:
                for _ in tags:
                    count_sql += ' AND tags LIKE ?'
            if query:
                count_sql += ' AND (content LIKE ? OR title LIKE ? OR filename LIKE ?)'
                
            count_params = [p for p in params if not isinstance(p, int)]
            cursor.execute(count_sql, count_params)
            total_count = cursor.fetchone()[0]
            
            # Create search results (for now, simple results without relevance scoring)
            results = [
                SearchResult(
                    document=doc,
                    relevance_score=1.0,  # Placeholder - implement real scoring
                    matched_fields=['content', 'title', 'filename'],
                    snippet=self._generate_snippet(doc.content, query) if query else doc.content[:200] + '...'
                )
                for doc in documents
            ]
            
            return results, total_count
    
    def _row_to_document(self, row: Dict[str, Any]) -> Document:
        """Convert a database row to a Document object"""
        return Document.from_dict(row)
    
    def _generate_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Generate a text snippet around the query match"""
        if not query or not content:
            return content[:max_length] + '...' if len(content) > max_length else content
            
        # Simple implementation - find first occurrence of query
        query = query.lower()
        content_lower = content.lower()
        pos = content_lower.find(query)
        
        if pos == -1:
            return content[:max_length] + '...' if len(content) > max_length else content
        
        # Get surrounding text
        start = max(0, pos - (max_length // 2))
        end = min(len(content), pos + len(query) + (max_length // 2))
        
        snippet = content[start:end]
        if start > 0:
            snippet = '...' + snippet
        if end < len(content):
            snippet = snippet + '...'
            
        return snippet
    
    def get_document_categories(self) -> List[Dict[str, Any]]:
        """Get list of categories with document counts"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM documents 
                GROUP BY category
                ORDER BY count DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_document_tags(self) -> List[Dict[str, Any]]:
        """Get list of tags with document counts"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tag, COUNT(*) as count 
                FROM (
                    SELECT json_each.value as tag
                    FROM documents, json_each(documents.tags)
                    WHERE json_valid(documents.tags)
                )
                GROUP BY tag
                ORDER BY count DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_all_documents(self) -> List[Document]:
        """Get all documents from database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents ORDER BY created_date DESC')
            rows = cursor.fetchall()
            return [self._row_to_document(dict(row)) for row in rows]

# Singleton database instance
db = Database()

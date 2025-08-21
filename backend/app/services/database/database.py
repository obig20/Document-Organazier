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

from app.models.document import Document, DocumentMetadata
from app.models.schemas import SearchResult, DocumentResponse
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
    
    def search_documents(self, query: str = None, category: str = None, status: str = None, tags: List[str] = None, 
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
                
            if status:
                sql += ' AND processing_status = ?'
                params.append(status)
                
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
            if status:
                count_sql += ' AND processing_status = ?'
            if tags:
                for _ in tags:
                    count_sql += ' AND tags LIKE ?'
            if query:
                count_sql += ' AND (content LIKE ? OR title LIKE ? OR filename LIKE ?)'
                
            count_params = [p for p in params if not isinstance(p, int)]
            cursor.execute(count_sql, count_params)
            total_count = cursor.fetchone()[0]
            
            # Create search results (for now, simple results without relevance scoring)
            results = []
            for doc in documents:
                # Convert Document to DocumentResponse
                doc_response = DocumentResponse(
                    id=doc.id,
                    filename=doc.filename,
                    title=doc.title or doc.filename,
                    category=doc.category or "other",
                    confidence_score=doc.confidence_score or 0.0,
                    tags=doc.tags or [],
                    created_date=doc.created_date or datetime.now(),
                    updated_date=doc.updated_date or datetime.now(),
                    is_processed=doc.is_processed or False,
                    processing_status=doc.processing_status or "pending",
                    content_preview=doc.content[:200] + "..." if doc.content and len(doc.content) > 200 else doc.content,
                    metadata=doc.metadata,
                    key_phrases=doc.tags,  # Use tags as key phrases for now
                    language_detected=doc.metadata.language_detected if doc.metadata else None
                )
                
                result = SearchResult(
                    document=doc_response,
                    relevance_score=1.0,  # Placeholder - implement real scoring
                    matched_fields=['content', 'title', 'filename'],
                    snippet=self._generate_snippet(doc.content, query) if query and doc.content else (doc.content[:200] + '...' if doc.content and len(doc.content) > 200 else doc.content or '')
                )
                results.append(result)
            
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
    
    def get_document_count(self, category: Optional[str] = None, status: Optional[str] = None, search: Optional[str] = None) -> int:
        """Get total count of documents with optional filtering"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM documents WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if status:
                query += " AND processing_status = ?"
                params.append(status)
            
            if search:
                query += " AND (filename LIKE ? OR title LIKE ? OR content LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    
    def add_feedback(self, document_id: int, was_correct: bool, correct_category: Optional[str] = None, notes: Optional[str] = None):
        """Add user feedback for a document"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (document_id, was_correct, correct_category, notes, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (document_id, was_correct, correct_category, notes, datetime.now()))
            conn.commit()
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics for analytics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total feedback count
            cursor.execute('SELECT COUNT(*) FROM feedback')
            total_feedback = cursor.fetchone()[0]
            
            if total_feedback == 0:
                return {
                    "total_feedback": 0,
                    "accuracy": 0.0,
                    "by_category_accuracy": {},
                    "learning_potential": 0.0,
                    "recent_performance": [],
                    "feedback_analysis": {
                        "correct_classifications": 0,
                        "incorrect_classifications": 0,
                        "feedback_rate": 0.0
                    }
                }
            
            # Get accuracy
            cursor.execute('SELECT COUNT(*) FROM feedback WHERE was_correct = 1')
            correct_feedback = cursor.fetchone()[0]
            accuracy = correct_feedback / total_feedback
            
            # Get accuracy by category
            cursor.execute('''
                SELECT d.category, 
                       COUNT(*) as total,
                       SUM(CASE WHEN f.was_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM feedback f
                JOIN documents d ON f.document_id = d.id
                GROUP BY d.category
            ''')
            
            by_category_accuracy = {}
            for row in cursor.fetchall():
                category, total, correct = row
                by_category_accuracy[category] = correct / total if total > 0 else 0.0
            
            # Get recent performance (last 7 days)
            cursor.execute('''
                SELECT DATE(f.created_date) as date,
                       COUNT(*) as total,
                       SUM(CASE WHEN f.was_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM feedback f
                WHERE f.created_date >= datetime('now', '-7 days')
                GROUP BY DATE(f.created_date)
                ORDER BY date DESC
            ''')
            
            recent_performance = []
            for row in cursor.fetchall():
                date, total, correct = row
                recent_performance.append({
                    "date": date,
                    "documents_processed": total,
                    "accuracy": correct / total if total > 0 else 0.0
                })
            
            # Calculate learning potential (percentage of incorrect classifications)
            learning_potential = (total_feedback - correct_feedback) / total_feedback
            
            # Feedback analysis
            feedback_analysis = {
                "correct_classifications": correct_feedback,
                "incorrect_classifications": total_feedback - correct_feedback,
                "feedback_rate": (total_feedback / max(1, self.get_document_count())) * 100
            }
            
            return {
                "total_feedback": total_feedback,
                "accuracy": accuracy,
                "by_category_accuracy": by_category_accuracy,
                "learning_potential": learning_potential,
                "recent_performance": recent_performance,
                "feedback_analysis": feedback_analysis
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total documents
            cursor.execute('SELECT COUNT(*) FROM documents')
            total_documents = cursor.fetchone()[0]
            
            # Documents by category
            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM documents 
                GROUP BY category
            ''')
            documents_by_category = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Documents by status
            cursor.execute('''
                SELECT processing_status, COUNT(*) as count 
                FROM documents 
                GROUP BY processing_status
            ''')
            documents_by_status = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Recent uploads (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) 
                FROM documents 
                WHERE created_date >= datetime('now', '-7 days')
            ''')
            recent_uploads = cursor.fetchone()[0]
            
            # Calculate storage used (estimate)
            cursor.execute('''
                SELECT SUM(LENGTH(content)) as total_size
                FROM documents
                WHERE content IS NOT NULL
            ''')
            content_size = cursor.fetchone()[0] or 0
            storage_used_mb = round(content_size / (1024 * 1024), 2)
            
            return {
                "total_documents": total_documents,
                "documents_by_category": documents_by_category,
                "documents_by_status": documents_by_status,
                "storage_used_mb": storage_used_mb,
                "recent_uploads": recent_uploads
            }

# Singleton database instance
db = Database()

"""
Database Manager for Scientific Paper Citations
Handles PostgreSQL operations for storing and retrieving paper citations and analyses.
"""

import psycopg2
import psycopg2.extras
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PaperRecord:
    """Data class for paper records"""
    title: str
    authors: List[str]
    journal: Optional[str] = None
    year: Optional[int] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    pdf_path: Optional[str] = None
    citations: Optional[Dict] = None
    extraction_confidence: Optional[float] = None


class CitationDatabaseManager:
    """Manages PostgreSQL database operations for scientific paper citations"""
    
    def __init__(self, database_url: str = None, **kwargs):
        """
        Initialize database connection
        
        Args:
            database_url: PostgreSQL connection string
            **kwargs: Individual connection parameters (host, database, user, password, port)
        """
        self.database_url = database_url
        self.connection_params = kwargs
        self.connection = None
        
        # Default connection parameters
        if not database_url and not kwargs:
            self.connection_params = {
                'host': 'localhost',
                'database': 'scientific_papers',
                'user': 'postgres',
                'password': 'password',
                'port': 5432
            }
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            if self.database_url:
                self.connection = psycopg2.connect(self.database_url)
            else:
                self.connection = psycopg2.connect(**self.connection_params)
            
            self.connection.autocommit = False
            logger.info("✅ Connected to PostgreSQL database")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("🔌 Database connection closed")
    
    def create_tables(self) -> bool:
        """Create database tables using the schema file"""
        try:
            with open('database_setup.sql', 'r') as f:
                schema_sql = f.read()
            
            with self.connection.cursor() as cur:
                cur.execute(schema_sql)
                self.connection.commit()
                logger.info("✅ Database tables created successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            self.connection.rollback()
            return False
    
    def store_paper(self, paper: PaperRecord) -> Optional[int]:
        """
        Store a paper citation in the database
        
        Args:
            paper: PaperRecord object with citation data
            
        Returns:
            Paper ID if successful, None if failed
        """
        try:
            with self.connection.cursor() as cur:
                insert_sql = """
                    INSERT INTO papers (
                        title, authors, journal, year, volume, pages, doi, 
                        pdf_path, citations, extraction_confidence
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """
                
                cur.execute(insert_sql, (
                    paper.title,
                    paper.authors,
                    paper.journal,
                    paper.year,
                    paper.volume,
                    paper.pages,
                    paper.doi,
                    paper.pdf_path,
                    json.dumps(paper.citations) if paper.citations else None,
                    paper.extraction_confidence
                ))
                
                paper_id = cur.fetchone()[0]
                self.connection.commit()
                
                logger.info(f"✅ Stored paper: {paper.title} (ID: {paper_id})")
                return paper_id
                
        except psycopg2.IntegrityError as e:
            logger.warning(f"⚠️ Paper already exists (DOI conflict): {paper.doi}")
            self.connection.rollback()
            return self.get_paper_by_doi(paper.doi)['id'] if paper.doi else None
            
        except Exception as e:
            logger.error(f"❌ Failed to store paper: {e}")
            self.connection.rollback()
            return None
    
    def store_analysis(self, paper_id: int, analysis_type: str, content: str, 
                      model_used: str = None, context_tokens: int = None) -> Optional[int]:
        """
        Store paper analysis in the database
        
        Args:
            paper_id: ID of the paper
            analysis_type: Type of analysis ('comprehensive', 'summary', etc.)
            content: Analysis content
            model_used: LLM model used for analysis
            context_tokens: Number of tokens used
            
        Returns:
            Analysis ID if successful, None if failed
        """
        try:
            with self.connection.cursor() as cur:
                insert_sql = """
                    INSERT INTO paper_analyses (
                        paper_id, analysis_type, analysis_content, model_used, context_tokens
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """
                
                cur.execute(insert_sql, (
                    paper_id, analysis_type, content, model_used, context_tokens
                ))
                
                analysis_id = cur.fetchone()[0]
                self.connection.commit()
                
                logger.info(f"✅ Stored analysis for paper ID {paper_id} (Analysis ID: {analysis_id})")
                return analysis_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store analysis: {e}")
            self.connection.rollback()
            return None
    
    def get_paper_by_doi(self, doi: str) -> Optional[Dict]:
        """Get paper by DOI"""
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM papers WHERE doi = %s", (doi,))
                result = cur.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ Failed to get paper by DOI: {e}")
            return None
    
    def search_papers(self, query: str = None, author: str = None, 
                     journal: str = None, year_from: int = None, 
                     year_to: int = None, limit: int = 50) -> List[Dict]:
        """
        Search papers with various filters
        
        Args:
            query: Full-text search in title
            author: Author name to search for
            journal: Journal name (partial match)
            year_from: Start year for range
            year_to: End year for range
            limit: Maximum results to return
            
        Returns:
            List of paper dictionaries
        """
        try:
            conditions = []
            params = []
            
            # Build WHERE clause based on provided filters
            if query:
                conditions.append("to_tsvector('english', title) @@ plainto_tsquery(%s)")
                params.append(query)
            
            if author:
                conditions.append("%s = ANY(authors)")
                params.append(author)
            
            if journal:
                conditions.append("journal ILIKE %s")
                params.append(f"%{journal}%")
            
            if year_from:
                conditions.append("year >= %s")
                params.append(year_from)
            
            if year_to:
                conditions.append("year <= %s")
                params.append(year_to)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            
            sql = f"""
                SELECT id, title, authors, journal, year, doi, 
                       citations->>'ACS' as acs_citation,
                       created_at
                FROM papers 
                WHERE {where_clause}
                ORDER BY created_at DESC 
                LIMIT %s
            """
            params.append(limit)
            
            with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                results = cur.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ Failed to search papers: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            with self.connection.cursor() as cur:
                # Get paper counts
                cur.execute("SELECT COUNT(*) FROM papers")
                total_papers = cur.fetchone()[0]
                
                # Get papers by year
                cur.execute("""
                    SELECT year, COUNT(*) as count 
                    FROM papers 
                    WHERE year IS NOT NULL 
                    GROUP BY year 
                    ORDER BY year DESC 
                    LIMIT 10
                """)
                papers_by_year = cur.fetchall()
                
                # Get top journals
                cur.execute("""
                    SELECT journal, COUNT(*) as count 
                    FROM papers 
                    WHERE journal IS NOT NULL 
                    GROUP BY journal 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                top_journals = cur.fetchall()
                
                # Get analysis count
                cur.execute("SELECT COUNT(*) FROM paper_analyses")
                total_analyses = cur.fetchone()[0]
                
                return {
                    'total_papers': total_papers,
                    'total_analyses': total_analyses,
                    'papers_by_year': papers_by_year,
                    'top_journals': top_journals
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get statistics: {e}")
            return {}
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Convenience functions for integration with citation extractor
def store_citation_data(citation_info: Dict, formatted_citations: Dict, 
                       pdf_path: str = None, extraction_confidence: float = None) -> Optional[int]:
    """
    Store citation data extracted from citation_extractor
    
    Args:
        citation_info: Raw citation info from extract_citation_info()
        formatted_citations: Formatted citations from format_citations()
        pdf_path: Path to the PDF file
        extraction_confidence: Confidence score for extraction
        
    Returns:
        Paper ID if successful
    """
    paper = PaperRecord(
        title=citation_info.get('title', 'Unknown Title'),
        authors=citation_info.get('authors', []),
        journal=citation_info.get('journal'),
        year=int(citation_info.get('year')) if citation_info.get('year') else None,
        volume=citation_info.get('volume'),
        pages=citation_info.get('pages'),
        doi=citation_info.get('doi'),
        pdf_path=pdf_path,
        citations=formatted_citations,
        extraction_confidence=extraction_confidence
    )
    
    with CitationDatabaseManager() as db:
        return db.store_paper(paper)


if __name__ == "__main__":
    # Example usage and testing
    print("🧪 Testing Database Manager...")
    
    with CitationDatabaseManager() as db:
        # Create tables
        db.create_tables()
        
        # Test data
        test_paper = PaperRecord(
            title="Test Paper: AI in Chemistry",
            authors=["John Doe", "Jane Smith"],
            journal="Test Journal",
            year=2024,
            doi="10.1234/test",
            citations={
                "ACS": "Doe, J.; Smith, J. Test Paper: AI in Chemistry. Test Journal 2024.",
                "APA": "John Doe and Jane Smith (2024). Test Paper: AI in Chemistry. Test Journal."
            }
        )
        
        # Store test paper
        paper_id = db.store_paper(test_paper)
        if paper_id:
            print(f"✅ Test paper stored with ID: {paper_id}")
            
            # Store test analysis
            analysis_id = db.store_analysis(
                paper_id=paper_id,
                analysis_type="test",
                content="This is a test analysis of the paper.",
                model_used="llama3.1:8b"
            )
            
            if analysis_id:
                print(f"✅ Test analysis stored with ID: {analysis_id}")
        
        # Get statistics
        stats = db.get_statistics()
        print(f"📊 Database stats: {stats}")
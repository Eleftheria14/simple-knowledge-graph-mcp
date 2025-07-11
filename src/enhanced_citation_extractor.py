"""
Enhanced Citation Extractor with Database Integration
Extends the original citation extractor to automatically store results in PostgreSQL
"""

from citation_extractor import extract_citation_info, format_citations, display_citation_info
from database_manager import store_citation_data, CitationDatabaseManager
import logging
from typing import Dict, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_and_store_citation(pdf_path: str, store_in_db: bool = True, 
                              extraction_confidence: float = None) -> Tuple[Dict, Dict, Optional[int]]:
    """
    Extract citation information and optionally store in database
    
    Args:
        pdf_path: Path to the PDF file
        store_in_db: Whether to store results in database
        extraction_confidence: Manual confidence score (0.0-1.0)
        
    Returns:
        Tuple of (citation_info, formatted_citations, paper_id)
    """
    logger.info(f"🔍 Extracting citation from: {pdf_path}")
    
    # Extract citation using existing extractor
    citation_info = extract_citation_info(pdf_path)
    formatted_citations = format_citations(citation_info)
    
    # Calculate confidence score if not provided
    if extraction_confidence is None:
        extraction_confidence = calculate_extraction_confidence(citation_info)
    
    paper_id = None
    if store_in_db:
        try:
            paper_id = store_citation_data(
                citation_info=citation_info,
                formatted_citations=formatted_citations,
                pdf_path=pdf_path,
                extraction_confidence=extraction_confidence
            )
            
            if paper_id:
                logger.info(f"✅ Citation stored in database with ID: {paper_id}")
            else:
                logger.warning("⚠️ Failed to store citation in database")
                
        except Exception as e:
            logger.error(f"❌ Database storage failed: {e}")
    
    return citation_info, formatted_citations, paper_id


def calculate_extraction_confidence(citation_info: Dict) -> float:
    """
    Calculate confidence score based on extracted citation completeness
    
    Args:
        citation_info: Dictionary with extracted citation data
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    score = 0.0
    max_score = 6.0  # Maximum possible score
    
    # Title (most important)
    if citation_info.get('title') and len(citation_info['title']) > 10:
        score += 2.0
    elif citation_info.get('title'):
        score += 1.0
    
    # Authors
    authors = citation_info.get('authors', [])
    if authors and len(authors) >= 3:
        score += 1.5
    elif authors and len(authors) >= 1:
        score += 1.0
    
    # Journal
    if citation_info.get('journal'):
        score += 1.0
    
    # Year
    if citation_info.get('year'):
        score += 1.0
    
    # DOI
    if citation_info.get('doi'):
        score += 0.5
    
    return round(score / max_score, 2)


def display_and_store_citation(pdf_path: str, show_metadata: bool = True, 
                              show_all_formats: bool = False) -> Dict:
    """
    Enhanced version of display_citation_info that also stores in database
    
    Args:
        pdf_path: Path to the PDF file
        show_metadata: Whether to show extracted metadata
        show_all_formats: Whether to show all citation formats
        
    Returns:
        Dictionary with citation info, formatted citations, and database ID
    """
    print("📚 Extracting citation information and storing in database...")
    
    # Extract and store
    citation_info, formatted_citations, paper_id = extract_and_store_citation(pdf_path)
    
    # Display results (similar to original but with database info)
    print("\n📖 PAPER CITATION INFORMATION")
    print("=" * 70)
    
    if paper_id:
        print(f"🗄️ Database ID: {paper_id}")
        print(f"📊 Extraction Confidence: {calculate_extraction_confidence(citation_info):.2f}")
    
    if show_metadata:
        print("\n🔍 EXTRACTED METADATA:")
        for key, value in citation_info.items():
            if isinstance(value, list):
                display_value = ', '.join(value[:3]) + (' et al.' if len(value) > 3 else '') if value else 'Not found'
            else:
                display_value = value if value else 'Not found'
            print(f"📌 {key.capitalize()}: {display_value}")
    
    print("\n📝 FORMATTED CITATIONS:")
    print("-" * 50)
    
    # Always show ACS style (prioritized)
    print("\n🧪 ACS Style (American Chemical Society):")
    print("   " + "\n   ".join([line for line in formatted_citations['ACS'].split('\n')]))
    
    if show_all_formats:
        other_formats = ['APA', 'BibTeX', 'Simple']
        for format_name in other_formats:
            print(f"\n📄 {format_name} Style:")
            if format_name == 'BibTeX':
                print("   " + formatted_citations[format_name].replace('\n', '\n   '))
            else:
                print("   " + "\n   ".join([line for line in formatted_citations[format_name].split('\n')]))
    
    print("\n" + "=" * 70)
    
    return {
        'citation_info': citation_info,
        'formatted_citations': formatted_citations,
        'paper_id': paper_id,
        'extraction_confidence': calculate_extraction_confidence(citation_info)
    }


def search_stored_citations(query: str = None, author: str = None, 
                           journal: str = None, year_from: int = None, 
                           year_to: int = None) -> None:
    """
    Search and display stored citations from database
    
    Args:
        query: Search term for paper titles
        author: Author name to search for
        journal: Journal name (partial match)
        year_from: Start year for range
        year_to: End year for range
    """
    print("🔍 SEARCHING STORED CITATIONS")
    print("=" * 50)
    
    with CitationDatabaseManager() as db:
        results = db.search_papers(
            query=query,
            author=author,
            journal=journal,
            year_from=year_from,
            year_to=year_to
        )
        
        if not results:
            print("❌ No papers found matching your criteria")
            return
        
        print(f"📚 Found {len(results)} paper(s):")
        print()
        
        for i, paper in enumerate(results, 1):
            print(f"{i}. **{paper['title']}**")
            authors_str = ', '.join(paper['authors']) if paper['authors'] else 'Unknown authors'
            print(f"   👥 Authors: {authors_str}")
            
            if paper['journal']:
                print(f"   📖 Journal: {paper['journal']}")
            if paper['year']:
                print(f"   📅 Year: {paper['year']}")
            if paper['doi']:
                print(f"   🔗 DOI: {paper['doi']}")
            
            # Show ACS citation if available
            if paper.get('acs_citation'):
                print(f"   📝 Citation: {paper['acs_citation']}")
            
            print(f"   🗄️ Database ID: {paper['id']}")
            print()


def get_database_statistics() -> None:
    """Display database statistics"""
    print("📊 DATABASE STATISTICS")
    print("=" * 30)
    
    with CitationDatabaseManager() as db:
        stats = db.get_statistics()
        
        print(f"📚 Total Papers: {stats.get('total_papers', 0)}")
        print(f"🔬 Total Analyses: {stats.get('total_analyses', 0)}")
        
        if stats.get('papers_by_year'):
            print(f"\n📅 Papers by Year:")
            for year, count in stats['papers_by_year']:
                print(f"   {year}: {count} papers")
        
        if stats.get('top_journals'):
            print(f"\n📖 Top Journals:")
            for journal, count in stats['top_journals']:
                print(f"   {journal}: {count} papers")


if __name__ == "__main__":
    # Test the enhanced citation extractor
    import sys
    
    pdf_path = "/Users/aimiegarces/Agents/d4sc03921a.pdf"
    
    print("🧪 Testing Enhanced Citation Extractor with Database Integration")
    print("=" * 70)
    
    # Test extraction and storage
    result = display_and_store_citation(pdf_path, show_all_formats=True)
    
    print(f"\n✅ Test completed. Paper stored with ID: {result.get('paper_id')}")
    
    # Show database statistics
    print("\n")
    get_database_statistics()
    
    # Test search functionality
    print("\n")
    search_stored_citations(author="Andrew D. White")
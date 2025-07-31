"""Citation extraction tool for LangGraph"""
from typing import Dict, Any, List
from langchain_core.tools import tool
import re
import json

@tool
def extract_citations(content: str) -> Dict[str, Any]:
    """
    Extract bibliographic information and citations from document content.
    
    Args:
        content: Document text content
        
    Returns:
        Dictionary with extracted citations and metadata
    """
    try:
        if not content or len(content.strip()) < 100:
            return {"success": False, "error": "Content too short for citation extraction"}
        
        print("📚 Extracting citations from document content...")
        
        # For now, use regex-based extraction (will be enhanced with LLM later)
        citations = []
        
        # Look for year patterns like (2023) or [2023]
        year_pattern = r'[\(\[]\d{4}[\)\]]'
        years = re.findall(year_pattern, content)
        
        # Simple author pattern (Last, First)
        author_pattern = r'[A-Z][a-z]+,\s+[A-Z]\.'
        authors = re.findall(author_pattern, content)
        
        # DOI pattern
        doi_pattern = r'10\.\d{4,}/[^\s]+'
        dois = re.findall(doi_pattern, content)
        
        # Look for References section
        references_match = re.search(r'References\s*\n(.*?)(?:\n\n|\Z)', content, re.DOTALL | re.IGNORECASE)
        references_section = references_match.group(1) if references_match else ""
        
        # Create basic citation entries
        if years or authors or dois:
            citations.append({
                "type": "pattern_extraction",
                "years_found": list(set(years))[:10],  # Limit to 10
                "authors_found": list(set(authors))[:10],
                "dois_found": list(set(dois))[:5],
                "references_section_length": len(references_section),
                "extraction_method": "regex_patterns"
            })
        
        # Try to extract specific citation formats
        # Format: Author (Year). Title. Journal.
        citation_pattern = r'([A-Z][a-z]+(?:\s+[A-Z]\.)*)\s+\((\d{4})\)\.\s+([^.]+)\.\s+([^.]+)\.'
        structured_citations = re.findall(citation_pattern, content)
        
        for match in structured_citations[:5]:  # Limit to 5
            author, year, title, journal = match
            citations.append({
                "type": "structured_citation",
                "author": author,
                "year": int(year),
                "title": title.strip(),
                "journal": journal.strip(),
                "extraction_method": "regex_structured"
            })
        
        return {
            "success": True,
            "citations": citations,
            "citations_count": len(citations),
            "content_length": len(content),
            "has_references_section": bool(references_section),
            "references_section": references_section[:500] if references_section else "",
            "extraction_method": "regex_with_patterns"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Exception in extract_citations: {str(e)}"}

# Test function
def test_citation_tool():
    """Test the citation extraction tool"""
    test_content = """
    This paper builds on the work of Smith, J. (2022) and Jones, A. (2023).
    
    References:
    Smith, J. (2022). Machine Learning Approaches. Journal of AI, 15(3), 123-145.
    Jones, A. (2023). Deep Learning Methods. Nature, 456, 789-801.
    DOI: 10.1038/nature12345
    """
    
    print("Citation tool created successfully")
    print("Tool name:", extract_citations.name)
    print("Tool description:", extract_citations.description)
    
    # Test with sample content
    result = extract_citations(test_content)
    print("Test result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    test_citation_tool()
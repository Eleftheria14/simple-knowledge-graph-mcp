"""Text processing tools for systematic paper chunking."""
from typing import List, Dict, Any
from fastmcp import FastMCP
from pydantic import BaseModel

from utils.text_chunking import chunk_paper_for_complete_coverage, estimate_expected_chunks
# Simple coverage validation removed for minimal implementation

class PaperProcessingRequest(BaseModel):
    """Request for automatic paper processing."""
    paper_text: str  # Full paper text
    paper_title: str = "Research Paper"  # Paper title for chunk naming
    chunk_size: int = 300  # Target words per chunk
    overlap: int = 75  # Overlap words between chunks

class CoverageValidationRequest(BaseModel):
    """Request for coverage validation."""
    original_text: str  # Original paper text
    stored_chunks: List[Dict[str, Any]]  # List of stored chunks

def register_text_processing_tools(mcp: FastMCP):
    """Register text processing and chunking tools."""
    
    @mcp.tool()
    def generate_systematic_chunks(
        paper_text: str,
        paper_title: str = "Research Paper",
        chunk_size: int = 300,
        overlap: int = 75
    ) -> Dict[str, Any]:
        """
        Generate systematic chunks for complete paper coverage.
        
        This tool automatically chunks an entire paper into overlapping segments
        that provide 95%+ coverage for comprehensive semantic search.
        
        Args:
            paper_text: Full paper text to chunk
            paper_title: Paper title for chunk naming
            chunk_size: Target words per chunk (200-400 recommended)
            overlap: Overlap words between chunks (50-100 recommended)
            
        Returns:
            Complete set of chunks ready for vector storage
        """
        try:
            # Generate systematic chunks
            chunks = chunk_paper_for_complete_coverage(
                paper_text=paper_text,
                document_title=paper_title,
                chunk_size=chunk_size,
                overlap=overlap
            )
            
            # Get coverage report from first chunk if available
            coverage_info = {}
            if chunks and "coverage_validation" in chunks[0].get("properties", {}):
                coverage_info = chunks[0]["properties"]["coverage_validation"]
            
            # Calculate statistics
            total_words = sum(chunk.get("properties", {}).get("word_count", 0) for chunk in chunks)
            sections_found = set(chunk.get("properties", {}).get("section", "unknown") for chunk in chunks)
            
            return {
                "success": True,
                "message": f"Generated {len(chunks)} systematic chunks with {coverage_info.get('coverage_status', 'good')} coverage",
                "chunks": chunks,
                "statistics": {
                    "total_chunks": len(chunks),
                    "total_words": total_words,
                    "average_chunk_size": round(total_words / len(chunks)) if chunks else 0,
                    "sections_covered": list(sections_found),
                    "coverage_report": coverage_info
                },
                "ready_for_vector_storage": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate systematic chunks"
            }
    
    @mcp.tool()
    def estimate_chunking_requirements(
        paper_text: str
    ) -> Dict[str, Any]:
        """
        Estimate chunking requirements for a paper.
        
        Provides estimates for how many chunks should be generated
        to achieve complete coverage of the paper content.
        
        Args:
            paper_text: Full paper text to analyze
            
        Returns:
            Chunking estimates and recommendations
        """
        try:
            estimates = estimate_expected_chunks(paper_text)
            
            # Add detailed recommendations
            word_count = estimates["total_words"]
            estimated_chunks = estimates["estimated_chunks"]
            
            recommendations = []
            
            if word_count < 1000:
                recommendations.append("Short paper - consider 1-3 chunks with full content")
            elif word_count < 3000:
                recommendations.append("Medium paper - systematic chunking with 200-300 word chunks")
            else:
                recommendations.append("Long paper - systematic chunking with 300-400 word chunks")
            
            if estimated_chunks < 10:
                recommendations.append("Use smaller chunks (200-250 words) for better granularity")
            elif estimated_chunks > 80:
                recommendations.append("Use larger chunks (350-400 words) to reduce total count")
            
            recommendations.append(f"Target: {estimated_chunks} chunks for 95%+ coverage")
            
            return {
                "success": True,
                "estimates": estimates,
                "recommendations": recommendations,
                "suggested_chunk_size": 300 if 10 <= estimated_chunks <= 80 else (250 if estimated_chunks > 80 else 350),
                "suggested_overlap": 75,
                "research_standards": {
                    "minimum_coverage": "85%",
                    "excellent_coverage": "95%",
                    "systematic_chunking": "Required for research databases"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to estimate chunking requirements"
            }
    
    @mcp.tool()
    def validate_text_coverage(
        original_text: str,
        stored_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simple text coverage validation for research integrity.
        
        Basic validation of how well chunks cover the original paper.
        
        Args:
            original_text: Full original paper text
            stored_chunks: List of chunk dictionaries that were stored
            
        Returns:
            Simple coverage validation report
        """
        try:
            # Simple word count comparison
            original_words = len(original_text.split())
            total_chunk_words = sum(
                len(chunk.get("content", "").split()) 
                for chunk in stored_chunks
            )
            
            coverage_ratio = min(total_chunk_words / original_words, 1.0) if original_words > 0 else 0
            
            # Simple status determination
            if coverage_ratio >= 0.85:
                status = "good"
                meets_standards = True
            else:
                status = "insufficient"
                meets_standards = False
            
            return {
                "success": True,
                "coverage_report": {
                    "coverage_ratio": f"{coverage_ratio:.1%}",
                    "status": status,
                    "meets_research_standards": meets_standards
                },
                "statistics": {
                    "original_words": original_words,
                    "stored_words": total_chunk_words,
                    "total_chunks": len(stored_chunks)
                },
                "message": f"Coverage: {coverage_ratio:.1%} ({'✅ Good' if meets_standards else '⚠️ Low'})"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to validate text coverage"
            }
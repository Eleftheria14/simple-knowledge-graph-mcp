"""Complete text coverage utilities for systematic paper chunking."""
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ChunkMetadata:
    """Metadata for a text chunk."""
    page: int
    section: str
    chunk_sequence: int
    word_count: int
    overlap_with_previous: bool
    content_type: str = "main_text"
    figure_number: Optional[int] = None
    table_number: Optional[int] = None

class PaperChunker:
    """Systematic paper chunking for complete text coverage."""
    
    def __init__(self, chunk_size: int = 300, overlap: int = 75):
        """
        Initialize paper chunker.
        
        Args:
            chunk_size: Target words per chunk (200-400 optimal)
            overlap: Overlapping words between chunks (50-100 optimal)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Section detection patterns
        self.section_patterns = {
            'abstract': [r'\babstract\b', r'\bsummary\b'],
            'introduction': [r'\bintroduction\b', r'\bbackground\b'],
            'methods': [r'\bmethods?\b', r'\bmethodology\b', r'\bprocedure\b', r'\bexperimental\b'],
            'results': [r'\bresults?\b', r'\bfindings?\b', r'\bperformance\b'],
            'discussion': [r'\bdiscussion\b', r'\banalysis\b'],
            'conclusion': [r'\bconclusion\b', r'\bsummary\b', r'\bfuture work\b'],
            'figure': [r'\bfigure\s+\d+\b', r'\bfig\.?\s+\d+\b'],
            'table': [r'\btable\s+\d+\b']
        }
    
    def chunk_complete_paper(self, paper_text: str, document_title: str = "Unknown") -> List[Dict[str, Any]]:
        """
        Systematically chunk entire paper for complete vector coverage.
        
        Args:
            paper_text: Full paper text
            document_title: Paper title for chunk naming
            
        Returns:
            List of chunk dictionaries for vector storage with 95%+ coverage
        """
        # Clean and prepare text
        cleaned_text = self._clean_paper_text(paper_text)
        
        # Split into words for systematic processing
        words = cleaned_text.split()
        
        if len(words) < self.chunk_size:
            # Short paper - single chunk
            return self._create_single_chunk(cleaned_text, document_title)
        
        chunks = []
        chunk_sequence = 1
        
        # Process text sequentially with overlap
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # Skip if chunk too small (end of document)
            if len(chunk_words) < 50:  # Minimum viable chunk
                continue
            
            # Generate metadata
            metadata = self._generate_chunk_metadata(
                chunk_text, chunk_sequence, i, words, len(chunk_words)
            )
            
            # Create chunk dictionary
            chunk = {
                "id": f"page{metadata.page}_chunk{chunk_sequence}_{metadata.section}",
                "content": chunk_text.strip(),
                "type": "text_chunk",
                "properties": {
                    "page": metadata.page,
                    "section": metadata.section,
                    "chunk_sequence": chunk_sequence,
                    "word_count": metadata.word_count,
                    "overlap_with_previous": metadata.overlap_with_previous,
                    "content_type": metadata.content_type
                }
            }
            
            # Add figure/table numbers if detected
            if metadata.figure_number:
                chunk["properties"]["figure_number"] = metadata.figure_number
            if metadata.table_number:
                chunk["properties"]["table_number"] = metadata.table_number
            
            chunks.append(chunk)
            chunk_sequence += 1
        
        # Validate coverage
        coverage_report = self._validate_coverage(paper_text, chunks)
        
        # Add coverage metadata to first chunk
        if chunks:
            chunks[0]["properties"]["coverage_validation"] = coverage_report
        
        return chunks
    
    def _clean_paper_text(self, text: str) -> str:
        """Clean paper text for systematic chunking."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page headers/footers (common patterns)
        text = re.sub(r'\b\d+\s+of\s+\d+\b', '', text)
        text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
        
        # Clean up citation markers [1], [2,3] etc.
        text = re.sub(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', '', text)
        
        return text.strip()
    
    def _create_single_chunk(self, text: str, title: str) -> List[Dict[str, Any]]:
        """Create single chunk for short papers."""
        return [{
            "id": "page1_chunk1_complete",
            "content": text,
            "type": "text_chunk",
            "properties": {
                "page": 1,
                "section": "complete",
                "chunk_sequence": 1,
                "word_count": len(text.split()),
                "overlap_with_previous": False,
                "content_type": "complete_paper"
            }
        }]
    
    def _generate_chunk_metadata(self, chunk_text: str, sequence: int, 
                               word_position: int, total_words: List[str], 
                               word_count: int) -> ChunkMetadata:
        """Generate comprehensive metadata for chunk."""
        
        # Estimate page number (assuming ~300 words per page)
        page = max(1, word_position // 300 + 1)
        
        # Detect section
        section = self._detect_section(chunk_text)
        
        # Check for figures/tables
        figure_num = self._extract_figure_number(chunk_text)
        table_num = self._extract_table_number(chunk_text)
        
        # Determine content type
        content_type = "main_text"
        if figure_num:
            content_type = "figure_caption"
        elif table_num:
            content_type = "table_content"
        elif any(keyword in chunk_text.lower() for keyword in ['equation', 'formula']):
            content_type = "equation"
        
        return ChunkMetadata(
            page=page,
            section=section,
            chunk_sequence=sequence,
            word_count=word_count,
            overlap_with_previous=sequence > 1,
            content_type=content_type,
            figure_number=figure_num,
            table_number=table_num
        )
    
    def _detect_section(self, text: str) -> str:
        """Detect paper section from chunk content."""
        text_lower = text.lower()
        
        # Score each section based on keyword matches
        section_scores = {}
        for section, patterns in self.section_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            section_scores[section] = score
        
        # Return section with highest score, default to 'content'
        if max(section_scores.values()) > 0:
            return max(section_scores, key=section_scores.get)
        
        # Fallback: analyze position and content
        if 'abstract' in text_lower[:100]:
            return 'abstract'
        elif any(word in text_lower for word in ['we propose', 'this paper', 'introduction']):
            return 'introduction'
        elif any(word in text_lower for word in ['we found', 'results show', 'performance']):
            return 'results'
        elif any(word in text_lower for word in ['in conclusion', 'to summarize']):
            return 'conclusion'
        else:
            return 'content'
    
    def _extract_figure_number(self, text: str) -> Optional[int]:
        """Extract figure number from text."""
        patterns = [r'\bfigure\s+(\d+)\b', r'\bfig\.?\s+(\d+)\b']
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_table_number(self, text: str) -> Optional[int]:
        """Extract table number from text."""
        match = re.search(r'\btable\s+(\d+)\b', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def _validate_coverage(self, original_text: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that chunks provide comprehensive coverage."""
        
        # Reconstruct text from chunks
        chunk_contents = [chunk['content'] for chunk in chunks]
        reconstructed_text = ' '.join(chunk_contents)
        
        # Calculate word-level coverage
        original_words = set(word.lower() for word in original_text.split())
        reconstructed_words = set(word.lower() for word in reconstructed_text.split())
        
        # Remove common stop words for more meaningful coverage calculation
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        original_content_words = original_words - stop_words
        reconstructed_content_words = reconstructed_words - stop_words
        
        if len(original_content_words) > 0:
            content_coverage = len(reconstructed_content_words & original_content_words) / len(original_content_words)
        else:
            content_coverage = 1.0
        
        # Overall statistics
        total_coverage = len(reconstructed_words & original_words) / len(original_words) if original_words else 1.0
        
        coverage_report = {
            "total_coverage": round(total_coverage, 3),
            "content_coverage": round(content_coverage, 3),
            "original_word_count": len(original_text.split()),
            "reconstructed_word_count": len(reconstructed_text.split()),
            "total_chunks": len(chunks),
            "coverage_status": "excellent" if content_coverage >= 0.95 else "good" if content_coverage >= 0.85 else "insufficient",
            "meets_requirements": content_coverage >= 0.85
        }
        
        return coverage_report

def chunk_paper_for_complete_coverage(paper_text: str, 
                                    document_title: str = "Research Paper",
                                    chunk_size: int = 300, 
                                    overlap: int = 75) -> List[Dict[str, Any]]:
    """
    Convenience function for complete paper chunking.
    
    Args:
        paper_text: Full paper text
        document_title: Paper title for naming
        chunk_size: Words per chunk (200-400 recommended)
        overlap: Overlap words (50-100 recommended)
    
    Returns:
        List of chunks with 95%+ coverage validation
    """
    chunker = PaperChunker(chunk_size=chunk_size, overlap=overlap)
    return chunker.chunk_complete_paper(paper_text, document_title)

def validate_research_coverage(original_paper: str, stored_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate that stored chunks provide comprehensive research coverage.
    
    Args:
        original_paper: Full original paper text
        stored_chunks: List of chunk dictionaries
    
    Returns:
        Coverage validation report
    """
    chunker = PaperChunker()
    return chunker._validate_coverage(original_paper, stored_chunks)

def estimate_expected_chunks(paper_text: str) -> Dict[str, int]:
    """
    Estimate expected number of chunks for a paper.
    
    Args:
        paper_text: Full paper text
    
    Returns:
        Dictionary with chunk estimates
    """
    word_count = len(paper_text.split())
    
    # Standard chunking parameters
    chunk_size = 300
    overlap = 75
    effective_chunk_size = chunk_size - overlap
    
    estimated_chunks = max(1, word_count // effective_chunk_size)
    
    return {
        "total_words": word_count,
        "estimated_chunks": estimated_chunks,
        "recommended_range": f"{max(1, estimated_chunks - 5)}-{estimated_chunks + 10}",
        "expected_coverage": "95%+",
        "chunking_strategy": f"{chunk_size} words per chunk with {overlap} word overlap"
    }
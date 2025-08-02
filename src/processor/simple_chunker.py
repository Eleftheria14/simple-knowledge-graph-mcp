"""
Simple document chunking for entity extraction.
Focused, lightweight, and easy to test.
"""
import re
from typing import List, Dict, Any

def chunk_text(content: str, strategy: str = "hierarchical", chunk_size: int = 4000) -> List[Dict[str, Any]]:
    """
    Split text into chunks using the specified strategy.
    
    Args:
        content: Full document text
        strategy: Chunking strategy ('simple_truncate', 'hierarchical', 'paragraph', 'sliding_window')
        chunk_size: Target size for each chunk
        
    Returns:
        List of chunk dictionaries with content and metadata
    """
    if not content or len(content.strip()) < 50:
        return []
    
    if strategy == "simple_truncate":
        return _simple_truncate(content, chunk_size)
    elif strategy == "hierarchical":
        return _hierarchical_chunks(content, chunk_size)
    elif strategy == "paragraph_based":
        return _paragraph_chunks(content, chunk_size)
    elif strategy == "sliding_window":
        return _sliding_window_chunks(content, chunk_size)
    else:
        # Default to hierarchical for unknown strategies
        return _hierarchical_chunks(content, chunk_size)

def _simple_truncate(content: str, chunk_size: int) -> List[Dict[str, Any]]:
    """Just take the first N characters"""
    truncated = content[:chunk_size]
    return [{
        "content": truncated,
        "start_pos": 0,
        "end_pos": len(truncated),
        "chunk_number": 1,
        "section_type": "truncated",
        "strategy": "simple_truncate"
    }]

def _hierarchical_chunks(content: str, chunk_size: int) -> List[Dict[str, Any]]:
    """Split by academic paper sections (Abstract, Introduction, etc.)"""
    # Find section headers
    section_patterns = [
        (r'\n\s*(Abstract|ABSTRACT)\s*\n', 'abstract'),
        (r'\n\s*(Introduction|INTRODUCTION)\s*\n', 'introduction'),
        (r'\n\s*(Methods?|METHODS?|Methodology|METHODOLOGY)\s*\n', 'methods'),
        (r'\n\s*(Results?|RESULTS?)\s*\n', 'results'),
        (r'\n\s*(Discussion|DISCUSSION)\s*\n', 'discussion'),
        (r'\n\s*(Conclusion|CONCLUSION|Conclusions|CONCLUSIONS)\s*\n', 'conclusion')
    ]
    
    sections = []
    last_end = 0
    
    # Find all section boundaries
    for pattern, section_type in section_patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for match in matches:
            # Add content before this section
            if last_end < match.start():
                prev_content = content[last_end:match.start()].strip()
                if prev_content:
                    sections.append((prev_content, last_end, match.start(), 'unknown'))
            
            # Find end of current section
            section_start = match.start()
            section_end = len(content)
            
            # Look for next section
            for next_pattern, _ in section_patterns:
                next_matches = list(re.finditer(next_pattern, content[match.end():], re.IGNORECASE))
                if next_matches:
                    section_end = match.end() + next_matches[0].start()
                    break
            
            section_content = content[section_start:section_end].strip()
            if section_content:
                sections.append((section_content, section_start, section_end, section_type))
            last_end = section_end
    
    # Add remaining content
    if last_end < len(content):
        remaining = content[last_end:].strip()
        if remaining:
            sections.append((remaining, last_end, len(content), 'unknown'))
    
    # Convert sections to chunks, split large sections if needed
    chunks = []
    chunk_number = 1
    
    for section_content, start_pos, end_pos, section_type in sections:
        if len(section_content) <= chunk_size:
            # Section fits in one chunk
            chunks.append({
                "content": section_content,
                "start_pos": start_pos,
                "end_pos": end_pos,
                "chunk_number": chunk_number,
                "section_type": section_type,
                "strategy": "hierarchical"
            })
            chunk_number += 1
        else:
            # Split large section into smaller chunks
            _split_large_section(section_content, chunk_size, section_type, chunks, chunk_number)
            chunk_number = len(chunks) + 1
    
    return chunks

def _split_large_section(content: str, chunk_size: int, section_type: str, chunks: List, start_chunk_num: int):
    """Split a large section into smaller chunks"""
    start = 0
    chunk_num = start_chunk_num
    
    while start < len(content):
        end = min(start + chunk_size, len(content))
        
        # Try to break at sentence boundary
        if end < len(content):
            sentence_end = content.rfind('.', start, end + 100)
            if sentence_end > start:
                end = sentence_end + 1
        
        chunk_content = content[start:end].strip()
        if chunk_content:
            chunks.append({
                "content": chunk_content,
                "start_pos": start,
                "end_pos": end,
                "chunk_number": chunk_num,
                "section_type": f"{section_type}_part_{chunk_num - start_chunk_num + 1}",
                "strategy": "hierarchical"
            })
            chunk_num += 1
        
        start = end

def _paragraph_chunks(content: str, chunk_size: int) -> List[Dict[str, Any]]:
    """Split on paragraph boundaries"""
    paragraphs = content.split('\n\n')
    chunks = []
    current_chunk = ""
    chunk_number = 1
    start_pos = 0
    
    for paragraph in paragraphs:
        # Check if adding this paragraph would exceed chunk size
        if len(current_chunk + paragraph) > chunk_size and current_chunk:
            # Create chunk from current content
            chunks.append({
                "content": current_chunk.strip(),
                "start_pos": start_pos,
                "end_pos": start_pos + len(current_chunk),
                "chunk_number": chunk_number,
                "section_type": "paragraph",
                "strategy": "paragraph_based"
            })
            chunk_number += 1
            
            # Start new chunk
            current_chunk = paragraph
            start_pos = content.find(paragraph, start_pos)
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
                start_pos = content.find(paragraph)
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),
            "start_pos": start_pos,
            "end_pos": start_pos + len(current_chunk),
            "chunk_number": chunk_number,
            "section_type": "paragraph",
            "strategy": "paragraph_based"
        })
    
    return chunks

def _sliding_window_chunks(content: str, chunk_size: int) -> List[Dict[str, Any]]:
    """Sliding window with overlap"""
    chunks = []
    overlap = 200
    step = chunk_size - overlap
    start = 0
    chunk_number = 1
    
    while start < len(content):
        end = min(start + chunk_size, len(content))
        
        # Try to break at word boundary
        if end < len(content):
            space_pos = content.rfind(' ', end - 50, end + 50)
            if space_pos > start:
                end = space_pos
        
        chunk_content = content[start:end].strip()
        if chunk_content and len(chunk_content) >= 100:  # Minimum chunk size
            chunks.append({
                "content": chunk_content,
                "start_pos": start,
                "end_pos": end,
                "chunk_number": chunk_number,
                "section_type": "sliding_window",
                "strategy": "sliding_window"
            })
            chunk_number += 1
        
        start += step
        
        # Prevent infinite loops
        if chunk_number > 20:
            break
    
    return chunks

def get_chunking_info(strategy: str) -> Dict[str, str]:
    """Get information about a chunking strategy"""
    strategies = {
        "simple_truncate": {
            "name": "Simple Truncate",
            "description": "Take first 4000 characters only",
            "speed": "⚡⚡⚡",
            "quality": "⭐",
            "best_for": "Quick testing, short documents"
        },
        "hierarchical": {
            "name": "Hierarchical",
            "description": "Respect paper sections (Abstract, Methods, Results, etc.)",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "best_for": "Academic papers with clear structure"
        },
        "paragraph_based": {
            "name": "Paragraph Based",
            "description": "Split on paragraph boundaries",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐",
            "best_for": "Documents with clear paragraph structure"
        },
        "sliding_window": {
            "name": "Sliding Window",
            "description": "Overlapping chunks ensure no content is lost",
            "speed": "⚡",
            "quality": "⭐⭐⭐",
            "best_for": "When entities might span chunk boundaries"
        }
    }
    
    return strategies.get(strategy, {
        "name": "Unknown",
        "description": "Unknown chunking strategy",
        "speed": "?",
        "quality": "?",
        "best_for": "Unknown"
    })
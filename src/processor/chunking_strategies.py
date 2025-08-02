"""
Comprehensive text chunking strategies for document processing.
Implements multiple chunking approaches with user-selectable strategies.
"""
import re
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    SpacyTextSplitter,
    NLTKTextSplitter,
    CharacterTextSplitter
)

class ChunkingStrategy(Enum):
    """Available chunking strategies"""
    SIMPLE_TRUNCATE = "simple_truncate"           # Just take first N characters
    RECURSIVE_CHARACTER = "recursive_character"   # LangChain recursive splitter
    TOKEN_AWARE = "token_aware"                   # Token-based splitting
    SENTENCE_AWARE = "sentence_aware"             # NLTK sentence splitting
    HIERARCHICAL = "hierarchical"                 # Section-based chunking
    SLIDING_WINDOW = "sliding_window"             # Overlapping windows
    SEMANTIC_TOPIC = "semantic_topic"             # Topic change detection
    MULTI_LEVEL = "multi_level"                   # Multiple granularities
    PARAGRAPH_BASED = "paragraph_based"           # Paragraph boundaries
    CONTENT_AWARE = "content_aware"               # Structure-aware splitting

@dataclass
class ChunkingConfig:
    """Configuration for chunking strategies"""
    strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE_CHARACTER
    chunk_size: int = 4000
    chunk_overlap: int = 200
    max_chunks: int = 10  # Limit total chunks processed
    preserve_structure: bool = True
    min_chunk_size: int = 100
    
    # Advanced options
    semantic_threshold: float = 0.5
    hierarchical_levels: List[str] = None
    sliding_window_step: int = 200
    
    def __post_init__(self):
        if self.hierarchical_levels is None:
            self.hierarchical_levels = ["Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion"]

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata"""
    content: str
    start_pos: int
    end_pos: int
    chunk_id: str
    chunk_number: int
    metadata: Dict[str, Any] = None
    section_type: str = "unknown"
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class DocumentChunker:
    """Main chunking orchestrator that implements all strategies"""
    
    def __init__(self, config: ChunkingConfig = None):
        self.config = config or ChunkingConfig()
        self._init_splitters()
    
    def _init_splitters(self):
        """Initialize LangChain text splitters"""
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )
        
        self.token_splitter = TokenTextSplitter(
            chunk_size=self.config.chunk_size // 4,  # Rough char to token conversion
            chunk_overlap=self.config.chunk_overlap // 4
        )
        
        try:
            self.sentence_splitter = NLTKTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
        except:
            # Fallback if NLTK not available
            self.sentence_splitter = self.recursive_splitter
        
        self.paragraph_splitter = CharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separator="\n\n"
        )
    
    def chunk_document(self, content: str, document_info: Dict[str, Any] = None) -> List[TextChunk]:
        """
        Main chunking method that dispatches to specific strategy
        
        Args:
            content: Full document text
            document_info: Document metadata
            
        Returns:
            List of TextChunk objects
        """
        if not content or len(content.strip()) < self.config.min_chunk_size:
            return []
        
        strategy_map = {
            ChunkingStrategy.SIMPLE_TRUNCATE: self._simple_truncate,
            ChunkingStrategy.RECURSIVE_CHARACTER: self._recursive_character_chunking,
            ChunkingStrategy.TOKEN_AWARE: self._token_aware_chunking,
            ChunkingStrategy.SENTENCE_AWARE: self._sentence_aware_chunking,
            ChunkingStrategy.HIERARCHICAL: self._hierarchical_chunking,
            ChunkingStrategy.SLIDING_WINDOW: self._sliding_window_chunking,
            ChunkingStrategy.SEMANTIC_TOPIC: self._semantic_topic_chunking,
            ChunkingStrategy.MULTI_LEVEL: self._multi_level_chunking,
            ChunkingStrategy.PARAGRAPH_BASED: self._paragraph_based_chunking,
            ChunkingStrategy.CONTENT_AWARE: self._content_aware_chunking
        }
        
        chunking_func = strategy_map.get(self.config.strategy, self._recursive_character_chunking)
        chunks = chunking_func(content, document_info or {})
        
        # Limit chunks if specified
        if self.config.max_chunks > 0:
            chunks = chunks[:self.config.max_chunks]
        
        return chunks
    
    def _simple_truncate(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """Simple truncation - just take first N characters"""
        truncated = content[:self.config.chunk_size]
        return [TextChunk(
            content=truncated,
            start_pos=0,
            end_pos=len(truncated),
            chunk_id="chunk_1",
            chunk_number=1,
            section_type="truncated",
            metadata={"strategy": "simple_truncate", "original_length": len(content)}
        )]
    
    def _recursive_character_chunking(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """LangChain recursive character splitting"""
        splits = self.recursive_splitter.split_text(content)
        chunks = []
        
        current_pos = 0
        for i, split in enumerate(splits):
            # Find position in original text
            start_pos = content.find(split, current_pos)
            if start_pos == -1:
                start_pos = current_pos
            
            chunk = TextChunk(
                content=split,
                start_pos=start_pos,
                end_pos=start_pos + len(split),
                chunk_id=f"recursive_{i+1}",
                chunk_number=i + 1,
                section_type="recursive",
                metadata={"strategy": "recursive_character"}
            )
            chunks.append(chunk)
            current_pos = start_pos + len(split)
        
        return chunks
    
    def _token_aware_chunking(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """Token-aware splitting for precise LLM token control"""
        splits = self.token_splitter.split_text(content)
        chunks = []
        
        current_pos = 0
        for i, split in enumerate(splits):
            start_pos = content.find(split, current_pos)
            if start_pos == -1:
                start_pos = current_pos
                
            chunk = TextChunk(
                content=split,
                start_pos=start_pos,
                end_pos=start_pos + len(split),
                chunk_id=f"token_{i+1}",
                chunk_number=i + 1,
                section_type="token_aware",
                metadata={"strategy": "token_aware"}
            )
            chunks.append(chunk)
            current_pos = start_pos + len(split)
        
        return chunks
    
    def _sentence_aware_chunking(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """NLTK sentence-boundary aware splitting"""
        splits = self.sentence_splitter.split_text(content)
        chunks = []
        
        current_pos = 0
        for i, split in enumerate(splits):
            start_pos = content.find(split, current_pos)
            if start_pos == -1:
                start_pos = current_pos
                
            chunk = TextChunk(
                content=split,
                start_pos=start_pos,
                end_pos=start_pos + len(split),
                chunk_id=f"sentence_{i+1}",
                chunk_number=i + 1,
                section_type="sentence_aware",
                metadata={"strategy": "sentence_aware"}
            )
            chunks.append(chunk)
            current_pos = start_pos + len(split)
        
        return chunks
    
    def _hierarchical_chunking(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """Section-based hierarchical chunking for academic papers"""
        # Find section headers
        section_patterns = [
            (r'\n\s*(Abstract|ABSTRACT)\s*\n', 'abstract'),
            (r'\n\s*(Introduction|INTRODUCTION)\s*\n', 'introduction'),
            (r'\n\s*(Methods?|METHODS?|Methodology|METHODOLOGY)\s*\n', 'methods'),
            (r'\n\s*(Results?|RESULTS?)\s*\n', 'results'),
            (r'\n\s*(Discussion|DISCUSSION)\s*\n', 'discussion'),
            (r'\n\s*(Conclusion|CONCLUSION|Conclusions|CONCLUSIONS)\s*\n', 'conclusion'),
            (r'\n\s*(References?|REFERENCES?|Bibliography|BIBLIOGRAPHY)\s*\n', 'references')
        ]
        
        sections = []
        last_end = 0
        
        for pattern, section_type in section_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                # Add previous section if exists
                if last_end < match.start():
                    section_content = content[last_end:match.start()].strip()
                    if section_content:
                        sections.append((section_content, last_end, match.start(), 'unknown'))
                
                # Find end of current section (next header or end of document)
                section_start = match.start()
                section_end = len(content)
                
                # Look for next section header
                for next_pattern, _ in section_patterns:
                    next_matches = list(re.finditer(next_pattern, content[match.end():], re.IGNORECASE))
                    if next_matches:
                        section_end = match.end() + next_matches[0].start()
                        break
                
                section_content = content[section_start:section_end].strip()
                if section_content:
                    sections.append((section_content, section_start, section_end, section_type))
                last_end = section_end
        
        # Add remaining content if any
        if last_end < len(content):
            remaining = content[last_end:].strip()
            if remaining:
                sections.append((remaining, last_end, len(content), 'unknown'))
        
        # Convert sections to chunks, splitting large sections if needed
        chunks = []
        chunk_counter = 1
        
        for section_content, start_pos, end_pos, section_type in sections:
            if len(section_content) <= self.config.chunk_size:
                # Section fits in one chunk
                chunk = TextChunk(
                    content=section_content,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    chunk_id=f"hierarchical_{chunk_counter}",
                    chunk_number=chunk_counter,
                    section_type=section_type,
                    metadata={"strategy": "hierarchical", "section": section_type}
                )
                chunks.append(chunk)
                chunk_counter += 1
            else:
                # Split large section
                subsections = self.recursive_splitter.split_text(section_content)
                for i, subsection in enumerate(subsections):
                    chunk = TextChunk(
                        content=subsection,
                        start_pos=start_pos,  # Approximate position
                        end_pos=start_pos + len(subsection),
                        chunk_id=f"hierarchical_{chunk_counter}",
                        chunk_number=chunk_counter,
                        section_type=f"{section_type}_part_{i+1}",
                        metadata={"strategy": "hierarchical", "section": section_type, "subsection": i+1}
                    )
                    chunks.append(chunk)
                    chunk_counter += 1
        
        return chunks
    
    def _sliding_window_chunking(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """Sliding window with configurable step size"""
        chunks = []
        step = self.config.sliding_window_step
        chunk_size = self.config.chunk_size
        
        start = 0
        chunk_counter = 1
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            
            # Try to break at word boundary
            if end < len(content):
                space_pos = content.rfind(' ', end - 100, end + 50)
                if space_pos > start:
                    end = space_pos
            
            chunk_content = content[start:end].strip()
            if chunk_content and len(chunk_content) >= self.config.min_chunk_size:
                chunk = TextChunk(
                    content=chunk_content,
                    start_pos=start,
                    end_pos=end,
                    chunk_id=f"sliding_{chunk_counter}",
                    chunk_number=chunk_counter,
                    section_type="sliding_window",
                    metadata={"strategy": "sliding_window", "step_size": step}
                )
                chunks.append(chunk)
                chunk_counter += 1
            
            start += step
            
            # Prevent infinite loops
            if chunk_counter > 50:
                break
        
        return chunks
    
    def _semantic_topic_chunking(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """Topic change detection using simple heuristics (placeholder for embedding-based)"""
        # Simplified version - in practice would use embeddings
        # For now, use paragraph breaks as proxy for topic changes
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_counter = 1
        
        for paragraph in paragraphs:
            # Check if adding this paragraph would exceed chunk size
            if len(current_chunk + paragraph) > self.config.chunk_size and current_chunk:
                # Create chunk from accumulated content
                chunk = TextChunk(
                    content=current_chunk.strip(),
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk),
                    chunk_id=f"semantic_{chunk_counter}",
                    chunk_number=chunk_counter,
                    section_type="semantic_topic",
                    metadata={"strategy": "semantic_topic"}
                )
                chunks.append(chunk)
                chunk_counter += 1
                
                # Start new chunk
                current_chunk = paragraph
                current_start = content.find(paragraph, current_start)
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                    current_start = content.find(paragraph)
        
        # Add final chunk
        if current_chunk.strip():
            chunk = TextChunk(
                content=current_chunk.strip(),
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                chunk_id=f"semantic_{chunk_counter}",
                chunk_number=chunk_counter,
                section_type="semantic_topic",
                metadata={"strategy": "semantic_topic"}
            )
            chunks.append(chunk)
        
        return chunks
    
    def _multi_level_chunking(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """Multi-level chunking with different granularities"""
        # Create chunks at different levels
        chunks = []
        
        # Level 1: Large sections (for context)
        large_config = ChunkingConfig(
            strategy=ChunkingStrategy.HIERARCHICAL,
            chunk_size=self.config.chunk_size * 2,
            chunk_overlap=self.config.chunk_overlap
        )
        large_chunker = DocumentChunker(large_config)
        large_chunks = large_chunker._hierarchical_chunking(content, doc_info)
        
        # Level 2: Medium paragraphs (for detailed extraction)
        medium_chunks = self._paragraph_based_chunking(content, doc_info)
        
        # Combine and prioritize medium chunks with large chunk context
        for i, medium_chunk in enumerate(medium_chunks):
            # Add context from large chunks
            context_chunks = [lc for lc in large_chunks 
                            if lc.start_pos <= medium_chunk.start_pos <= lc.end_pos]
            
            medium_chunk.metadata.update({
                "strategy": "multi_level",
                "level": "medium",
                "context_available": len(context_chunks) > 0
            })
            chunks.append(medium_chunk)
        
        return chunks
    
    def _paragraph_based_chunking(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """Paragraph-boundary aware chunking"""
        splits = self.paragraph_splitter.split_text(content)
        chunks = []
        
        current_pos = 0
        for i, split in enumerate(splits):
            start_pos = content.find(split, current_pos)
            if start_pos == -1:
                start_pos = current_pos
                
            chunk = TextChunk(
                content=split,
                start_pos=start_pos,
                end_pos=start_pos + len(split),
                chunk_id=f"paragraph_{i+1}",
                chunk_number=i + 1,
                section_type="paragraph",
                metadata={"strategy": "paragraph_based"}
            )
            chunks.append(chunk)
            current_pos = start_pos + len(split)
        
        return chunks
    
    def _content_aware_chunking(self, content: str, doc_info: Dict) -> List[TextChunk]:
        """Structure-aware chunking that preserves document elements"""
        # Detect and preserve key structures
        chunks = []
        
        # Look for figures, tables, equations
        figure_pattern = r'(Figure \d+|Fig\. \d+|Table \d+)[^\n]*'
        equation_pattern = r'\$[^$]+\$|\$\$[^$]+\$\$'
        citation_pattern = r'\[[^\]]+\]|\([^)]*\d{4}[^)]*\)'
        
        # Split on major breaks while preserving structures
        major_breaks = ['\n\n\n', '\n\n']  # Triple and double line breaks
        
        current_content = content
        current_pos = 0
        chunk_counter = 1
        
        # Simple implementation - split on paragraph breaks but keep structures intact
        paragraphs = content.split('\n\n')
        current_chunk = ""
        chunk_start = 0
        
        for paragraph in paragraphs:
            # Check for special content
            has_figure = bool(re.search(figure_pattern, paragraph, re.IGNORECASE))
            has_equation = bool(re.search(equation_pattern, paragraph))
            has_citations = bool(re.search(citation_pattern, paragraph))
            
            # If adding this paragraph exceeds size or it contains special content
            if (len(current_chunk + paragraph) > self.config.chunk_size and current_chunk) or \
               (has_figure or has_equation) and current_chunk:
                
                # Create chunk
                chunk = TextChunk(
                    content=current_chunk.strip(),
                    start_pos=chunk_start,
                    end_pos=chunk_start + len(current_chunk),
                    chunk_id=f"content_aware_{chunk_counter}",
                    chunk_number=chunk_counter,
                    section_type="content_aware",
                    metadata={
                        "strategy": "content_aware",
                        "has_special_content": has_figure or has_equation or has_citations
                    }
                )
                chunks.append(chunk)
                chunk_counter += 1
                
                # Start new chunk
                current_chunk = paragraph
                chunk_start = content.find(paragraph, chunk_start if chunk_start > 0 else 0)
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                    chunk_start = content.find(paragraph)
        
        # Add final chunk
        if current_chunk.strip():
            chunk = TextChunk(
                content=current_chunk.strip(),
                start_pos=chunk_start,
                end_pos=chunk_start + len(current_chunk),
                chunk_id=f"content_aware_{chunk_counter}",
                chunk_number=chunk_counter,
                section_type="content_aware",
                metadata={"strategy": "content_aware"}
            )
            chunks.append(chunk)
        
        return chunks

# Helper functions for getting strategy info
def get_chunking_strategies() -> Dict[str, Dict[str, str]]:
    """Get all available chunking strategies with descriptions"""
    return {
        "simple_truncate": {
            "name": "Simple Truncate",
            "description": "Just take first 4000 characters - fastest but loses content",
            "best_for": "Quick testing, short documents",
            "speed": "⚡⚡⚡",
            "quality": "⭐"
        },
        "recursive_character": {
            "name": "Recursive Character",
            "description": "Smart splitting on paragraphs, sentences, then words",
            "best_for": "General use, balanced approach",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐"
        },
        "token_aware": {
            "name": "Token Aware",
            "description": "Splits by exact token count for precise LLM control",
            "best_for": "When you need exact token limits",
            "speed": "⚡⚡",
            "quality": "⭐⭐"
        },
        "sentence_aware": {
            "name": "Sentence Aware",
            "description": "Never breaks sentences, preserves linguistic structure",
            "best_for": "Complex academic text with citations",
            "speed": "⚡",
            "quality": "⭐⭐⭐⭐"
        },
        "hierarchical": {
            "name": "Hierarchical",
            "description": "Respects document sections (Abstract, Methods, Results, etc.)",
            "best_for": "Academic papers with clear structure",
            "speed": "⚡",
            "quality": "⭐⭐⭐⭐⭐"
        },
        "sliding_window": {
            "name": "Sliding Window",
            "description": "Overlapping chunks ensure no content is lost at boundaries",
            "best_for": "When entities might span chunk boundaries",
            "speed": "⚡",
            "quality": "⭐⭐⭐"
        },
        "semantic_topic": {
            "name": "Semantic Topic",
            "description": "Splits when topics change, keeps related content together",
            "best_for": "Papers with distinct topics/sections",
            "speed": "⚡",
            "quality": "⭐⭐⭐⭐"
        },
        "multi_level": {
            "name": "Multi-Level",
            "description": "Processes at multiple granularities for comprehensive extraction",
            "best_for": "Maximum coverage, complex documents",
            "speed": "💀",
            "quality": "⭐⭐⭐⭐⭐"
        },
        "paragraph_based": {
            "name": "Paragraph Based",
            "description": "Splits on paragraph boundaries, preserves paragraph integrity",
            "best_for": "Documents with clear paragraph structure",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐"
        },
        "content_aware": {
            "name": "Content Aware",
            "description": "Preserves figures, tables, equations, and citations",
            "best_for": "Papers with lots of figures, tables, and equations",
            "speed": "⚡",
            "quality": "⭐⭐⭐⭐"
        }
    }

def get_recommended_strategy(document_info: Dict[str, Any]) -> str:
    """Recommend a chunking strategy based on document characteristics"""
    content_length = document_info.get('content_length', 0)
    has_sections = any(keyword in document_info.get('title', '').lower() 
                      for keyword in ['abstract', 'introduction', 'method', 'result', 'discussion'])
    
    if content_length < 5000:
        return "simple_truncate"
    elif content_length < 15000:
        return "recursive_character"
    elif has_sections:
        return "hierarchical"
    else:
        return "paragraph_based"
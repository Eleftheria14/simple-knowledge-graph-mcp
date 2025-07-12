"""
Enhanced Paper Analyzer for Literature Review System
Extends the existing paper analysis to output GraphRAG-compatible documents with rich metadata.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .simple_paper_rag import SimplePaperRAG
from .simple_knowledge_graph import SimpleKnowledgeGraph

logger = logging.getLogger(__name__)


class EnhancedPaperAnalyzer:
    """
    Enhanced paper analyzer that produces GraphRAG-compatible documents
    with rich metadata for cross-paper analysis and literature reviews.
    """
    
    def __init__(self, embedding_model: str = "nomic-embed-text", 
                 llm_model: str = "llama3.1:8b"):
        """Initialize the enhanced analyzer"""
        self.rag = SimplePaperRAG(embedding_model, llm_model)
        self.kg = SimpleKnowledgeGraph(llm_model)
        
        logger.info("🔬 EnhancedPaperAnalyzer initialized")
    
    def analyze_for_corpus(self, pdf_path: str) -> Dict:
        """
        Analyze paper and return GraphRAG-compatible document format
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with content, metadata, and analysis data
        """
        logger.info(f"📄 Analyzing paper for corpus: {Path(pdf_path).name}")
        
        # Load paper with existing system
        paper_info = self.rag.load_paper(pdf_path)
        
        # Extract entities and relationships
        kg_result = self.kg.extract_entities_and_relationships(
            self.rag.paper_data['content'],
            self.rag.paper_data['title']
        )
        
        # Enhanced metadata extraction
        metadata = self._extract_enhanced_metadata(
            self.rag.paper_data, kg_result
        )
        
        # Build citation map
        citation_map = self._build_citation_map(self.rag.paper_data['content'])
        
        # Section analysis
        sections = self._extract_sections(self.rag.paper_data['content'])
        
        result = {
            "content": self.rag.paper_data['content'],
            "metadata": metadata,
            "full_analysis": {
                "paper_info": paper_info,
                "entities": kg_result['entities'],
                "relationships": kg_result['relationships'],
                "graph_stats": kg_result['graph_stats']
            },
            "citation_map": citation_map,
            "sections": sections,
            "document_id": self._generate_document_id(pdf_path, metadata)
        }
        
        logger.info(f"✅ Analysis complete: {metadata['title'][:50]}...")
        return result
    
    def _extract_enhanced_metadata(self, paper_data: Dict, kg_result: Dict) -> Dict:
        """Extract comprehensive metadata for GraphRAG"""
        
        content = paper_data['content']
        entities = kg_result['entities']
        
        metadata = {
            # Basic paper information
            "title": paper_data['title'],
            "file_path": paper_data.get('file_path', ''),
            "processed_date": datetime.now().isoformat(),
            
            # Extracted entities (for GraphRAG edges)
            "authors": entities.get('authors', []),
            "institutions": entities.get('institutions', []),
            "methods": entities.get('methods', []),
            "concepts": entities.get('concepts', []),
            "technologies": entities.get('technologies', []),
            "metrics": entities.get('metrics', []),
            "datasets": entities.get('datasets', []),
            
            # Publication details
            "year": self._extract_year(content),
            "abstract": self._extract_abstract(content),
            "keywords": self._extract_keywords(content),
            
            # Content statistics
            "word_count": len(content.split()),
            "section_count": len(self._extract_sections(content)),
            "citation_count": len(self._extract_reference_citations(content)),
            
            # Research categorization
            "research_type": self._classify_research_type(content),
            "domain": self._identify_domain(content, entities),
            "methodology": self._identify_methodology(entities.get('methods', [])),
            
            # Quality indicators
            "has_abstract": bool(self._extract_abstract(content)),
            "has_conclusion": self._has_conclusion_section(content),
            "has_methodology": self._has_methodology_section(content),
        }
        
        return metadata
    
    def _extract_year(self, content: str) -> Optional[int]:
        """Extract publication year from content"""
        # Look for common year patterns
        year_patterns = [
            r'\b(19|20)\d{2}\b',  # 4-digit years
            r'©\s*(19|20)\d{2}',   # Copyright years
            r'Published.*?(19|20)\d{2}',  # Published dates
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, content[:2000])  # Search in first 2000 chars
            if matches:
                years = [int(match if isinstance(match, str) else match[0] + match[1]) 
                        for match in matches]
                # Return most recent plausible year
                valid_years = [y for y in years if 1990 <= y <= datetime.now().year]
                if valid_years:
                    return max(valid_years)
        
        return None
    
    def _extract_abstract(self, content: str) -> str:
        """Extract abstract from paper content"""
        # Look for abstract section
        abstract_patterns = [
            r'(?i)abstract\s*:?\s*(.*?)(?=\n\s*(?:introduction|keywords|1\.|background))',
            r'(?i)abstract\s*\n\s*(.*?)(?=\n\s*(?:[A-Z][a-z]+|Keywords|1\.))',
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, content[:3000], re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                # Clean up the abstract
                abstract = re.sub(r'\s+', ' ', abstract)
                abstract = re.sub(r'\n+', ' ', abstract)
                if len(abstract) > 50:  # Minimum reasonable abstract length
                    return abstract[:500]  # Limit length
        
        return ""
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from paper"""
        # Look for keywords section
        keyword_patterns = [
            r'(?i)keywords?\s*:?\s*(.*?)(?=\n\s*(?:introduction|abstract|1\.))',
            r'(?i)key\s*words?\s*:?\s*(.*?)(?=\n\s*(?:introduction|abstract|1\.))',
        ]
        
        for pattern in keyword_patterns:
            match = re.search(pattern, content[:3000], re.DOTALL)
            if match:
                keyword_text = match.group(1).strip()
                # Split by common delimiters
                keywords = re.split(r'[,;·•]', keyword_text)
                keywords = [kw.strip() for kw in keywords if kw.strip()]
                keywords = [kw for kw in keywords if len(kw) < 50]  # Filter long items
                return keywords[:10]  # Limit to 10 keywords
        
        return []
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract section structure with line numbers"""
        sections = []
        
        # Common section patterns
        section_patterns = [
            r'^\s*(\d+\.?\s*[A-Z][A-Za-z\s]+)\s*$',  # "1. Introduction"
            r'^\s*([A-Z][A-Z\s]+)\s*$',              # "INTRODUCTION"
            r'^\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$',  # "Introduction"
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            for pattern in section_patterns:
                match = re.match(pattern, line.strip())
                if match and len(line.strip()) < 100:  # Reasonable section title length
                    section_title = match.group(1).strip()
                    sections.append({
                        "title": section_title,
                        "line_number": i + 1,
                        "character_position": len('\n'.join(lines[:i]))
                    })
                    break
        
        return sections
    
    def _build_citation_map(self, content: str) -> Dict:
        """Build map of citations with precise locations"""
        citation_map = {
            "inline_citations": self._extract_inline_citations(content),
            "reference_citations": self._extract_reference_citations(content),
            "sections": self._map_sections_to_content(content)
        }
        
        return citation_map
    
    def _extract_inline_citations(self, content: str) -> List[Dict]:
        """Extract inline citations like [1], (Smith, 2020), etc."""
        citations = []
        
        # Common citation patterns
        patterns = [
            r'\[(\d+(?:,\s*\d+)*)\]',  # [1], [1,2,3]
            r'\(([A-Za-z]+(?:\s+et\s+al\.)?(?:,\s*\d{4})?)\)',  # (Smith, 2020), (Smith et al.)
            r'([A-Za-z]+\s+et\s+al\.\s*\(\d{4}\))',  # Smith et al. (2020)
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                citations.append({
                    "text": match.group(0),
                    "citation_key": match.group(1),
                    "start_pos": match.start(),
                    "end_pos": match.end(),
                    "line_number": content[:match.start()].count('\n') + 1
                })
        
        return citations
    
    def _extract_reference_citations(self, content: str) -> List[Dict]:
        """Extract reference list citations"""
        references = []
        
        # Look for references section
        ref_match = re.search(r'(?i)(references|bibliography)\s*\n(.*?)(?=\n\s*(?:appendix|acknowledgment|\Z))', 
                             content, re.DOTALL)
        
        if ref_match:
            ref_text = ref_match.group(2)
            # Split by numbered references
            ref_items = re.split(r'\n\s*(\d+\.)', ref_text)
            
            for i in range(1, len(ref_items), 2):
                if i + 1 < len(ref_items):
                    ref_number = ref_items[i].strip('.')
                    ref_content = ref_items[i + 1].strip()
                    
                    references.append({
                        "number": ref_number,
                        "content": ref_content,
                        "authors": self._extract_authors_from_reference(ref_content),
                        "year": self._extract_year_from_reference(ref_content),
                        "title": self._extract_title_from_reference(ref_content)
                    })
        
        return references
    
    def _map_sections_to_content(self, content: str) -> Dict:
        """Map sections to their content ranges"""
        sections = self._extract_sections(content)
        section_map = {}
        
        for i, section in enumerate(sections):
            start_pos = section['character_position']
            end_pos = sections[i + 1]['character_position'] if i + 1 < len(sections) else len(content)
            
            section_content = content[start_pos:end_pos].strip()
            section_map[section['title']] = {
                "start_line": section['line_number'],
                "start_char": start_pos,
                "end_char": end_pos,
                "content": section_content[:500],  # First 500 chars
                "word_count": len(section_content.split())
            }
        
        return section_map
    
    def _classify_research_type(self, content: str) -> str:
        """Classify the type of research"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['review', 'survey', 'systematic review']):
            return 'review'
        elif any(word in content_lower for word in ['experiment', 'experimental', 'methodology']):
            return 'experimental'
        elif any(word in content_lower for word in ['theoretical', 'theory', 'model']):
            return 'theoretical'
        elif any(word in content_lower for word in ['simulation', 'computational', 'modeling']):
            return 'computational'
        else:
            return 'empirical'
    
    def _identify_domain(self, content: str, entities: Dict) -> str:
        """Identify research domain"""
        content_lower = content.lower()
        
        # Check for domain keywords
        domains = {
            'chemistry': ['chemistry', 'chemical', 'molecule', 'catalyst', 'reaction'],
            'biology': ['biology', 'biological', 'protein', 'gene', 'cell'],
            'physics': ['physics', 'quantum', 'particle', 'energy', 'mechanics'],
            'computer_science': ['algorithm', 'computational', 'machine learning', 'ai', 'neural'],
            'materials': ['material', 'crystal', 'polymer', 'synthesis'],
            'medicine': ['medical', 'clinical', 'patient', 'treatment', 'drug']
        }
        
        for domain, keywords in domains.items():
            if sum(1 for keyword in keywords if keyword in content_lower) >= 2:
                return domain
        
        return 'multidisciplinary'
    
    def _identify_methodology(self, methods: List[str]) -> str:
        """Identify primary methodology"""
        if not methods:
            return 'unknown'
        
        method_categories = {
            'machine_learning': ['neural', 'learning', 'ai', 'model', 'training'],
            'experimental': ['experiment', 'synthesis', 'measurement', 'analysis'],
            'computational': ['simulation', 'calculation', 'modeling', 'computation'],
            'theoretical': ['theory', 'theoretical', 'mathematical', 'analytical']
        }
        
        methods_text = ' '.join(methods).lower()
        
        for category, keywords in method_categories.items():
            if any(keyword in methods_text for keyword in keywords):
                return category
        
        return 'empirical'
    
    def _has_conclusion_section(self, content: str) -> bool:
        """Check if paper has conclusion section"""
        return bool(re.search(r'(?i)\b(conclusion|summary|discussion)\b', content))
    
    def _has_methodology_section(self, content: str) -> bool:
        """Check if paper has methodology section"""
        return bool(re.search(r'(?i)\b(method|methodology|approach|procedure)\b', content))
    
    def _extract_authors_from_reference(self, ref_content: str) -> List[str]:
        """Extract authors from reference text"""
        # Simple author extraction - look for Last, F. patterns
        author_pattern = r'([A-Z][a-z]+,\s*[A-Z]\.(?:\s*[A-Z]\.)*)'
        authors = re.findall(author_pattern, ref_content)
        return authors[:5]  # Limit to 5 authors
    
    def _extract_year_from_reference(self, ref_content: str) -> Optional[int]:
        """Extract year from reference"""
        year_match = re.search(r'\b(19|20)\d{2}\b', ref_content)
        return int(year_match.group(0)) if year_match else None
    
    def _extract_title_from_reference(self, ref_content: str) -> str:
        """Extract title from reference"""
        # Look for quoted title or title after author/year
        title_patterns = [
            r'"([^"]+)"',  # Quoted title
            r'\.([^.]+)\.',  # Text between periods
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, ref_content)
            if match:
                title = match.group(1).strip()
                if 10 < len(title) < 200:  # Reasonable title length
                    return title
        
        return ""
    
    def _generate_document_id(self, pdf_path: str, metadata: Dict) -> str:
        """Generate unique document ID"""
        filename = Path(pdf_path).stem
        title_hash = hash(metadata['title']) % 10000
        return f"{filename}_{title_hash}"


# Convenience function for quick analysis
def analyze_paper_for_corpus(pdf_path: str) -> Dict:
    """
    Quick analysis of a paper for corpus inclusion
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        GraphRAG-compatible document
    """
    analyzer = EnhancedPaperAnalyzer()
    return analyzer.analyze_for_corpus(pdf_path)


if __name__ == "__main__":
    # Test the enhanced analyzer
    test_pdf = "../examples/d4sc03921a.pdf"
    
    if Path(test_pdf).exists():
        print("🧪 Testing EnhancedPaperAnalyzer...")
        result = analyze_paper_for_corpus(test_pdf)
        
        print(f"✅ Analysis complete!")
        print(f"📊 Title: {result['metadata']['title']}")
        print(f"📊 Authors: {result['metadata']['authors']}")
        print(f"📊 Year: {result['metadata']['year']}")
        print(f"📊 Domain: {result['metadata']['domain']}")
        print(f"📊 Sections: {len(result['sections'])}")
        print(f"📊 Citations: {result['metadata']['citation_count']}")
    else:
        print("❌ Test PDF not found")
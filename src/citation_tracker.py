"""
Citation Tracking System
Provides precise citation location mapping and verification for literature reviews.
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CitationTracker:
    """
    Advanced citation tracking system that maps every citation to its exact location
    in the source document for precise literature review writing.
    """
    
    def __init__(self):
        """Initialize citation tracker"""
        self.citation_patterns = self._build_citation_patterns()
        logger.info("📝 CitationTracker initialized")
    
    def build_citation_map(self, content: str, paper_metadata: Dict) -> Dict:
        """
        Build comprehensive citation map for a paper
        
        Args:
            content: Full paper text
            paper_metadata: Paper metadata including title, authors, etc.
            
        Returns:
            Complete citation mapping
        """
        logger.info("🗺️ Building citation map...")
        
        citation_map = {
            "paper_info": {
                "title": paper_metadata.get('title', ''),
                "authors": paper_metadata.get('authors', []),
                "year": paper_metadata.get('year'),
                "document_id": paper_metadata.get('document_id', '')
            },
            "inline_citations": self._extract_inline_citations(content),
            "reference_list": self._extract_reference_list(content),
            "section_citations": self._map_citations_to_sections(content),
            "citation_contexts": self._extract_citation_contexts(content),
            "key_claims": self._identify_key_claims_with_citations(content),
            "citation_density": self._calculate_citation_density(content)
        }
        
        # Link inline citations to reference list
        citation_map["citation_links"] = self._link_inline_to_references(
            citation_map["inline_citations"], 
            citation_map["reference_list"]
        )
        
        logger.info(f"✅ Citation map built: {len(citation_map['inline_citations'])} inline, "
                   f"{len(citation_map['reference_list'])} references")
        
        return citation_map
    
    def _build_citation_patterns(self) -> Dict:
        """Build comprehensive citation pattern library"""
        return {
            # Numbered citations: [1], [1,2,3], [1-3]
            "numbered": [
                r'\[(\d+(?:[-,]\s*\d+)*)\]',
                r'\((\d+(?:[-,]\s*\d+)*)\)'
            ],
            
            # Author-year citations: (Smith, 2020), (Smith et al., 2020)
            "author_year": [
                r'\(([A-Za-z]+(?:\s+et\s+al\.)?(?:,\s*\d{4})?)\)',
                r'([A-Za-z]+\s+et\s+al\.\s*\(\d{4}\))',
                r'([A-Za-z]+(?:,\s*\d{4})?)'
            ],
            
            # Superscript citations: text^1, text^1,2,3
            "superscript": [
                r'\^(\d+(?:[-,]\s*\d+)*)',
                r'(\d+(?:[-,]\s*\d+)*)\s*(?=\.|,|\s)'
            ],
            
            # Full author citations: Smith (2020), According to Smith (2020)
            "full_author": [
                r'([A-Za-z]+(?:\s+et\s+al\.)?)\s*\((\d{4})\)',
                r'(?:According\s+to|As\s+shown\s+by)\s+([A-Za-z]+(?:\s+et\s+al\.)?)\s*\((\d{4})\)'
            ]
        }
    
    def _extract_inline_citations(self, content: str) -> List[Dict]:
        """Extract all inline citations with precise locations"""
        citations = []
        
        for citation_type, patterns in self.citation_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    citation_info = {
                        "type": citation_type,
                        "text": match.group(0),
                        "citation_key": match.group(1) if match.groups() else match.group(0),
                        "start_position": match.start(),
                        "end_position": match.end(),
                        "line_number": content[:match.start()].count('\n') + 1,
                        "context": self._get_citation_context(content, match.start(), match.end()),
                        "section": self._identify_section_for_position(content, match.start())
                    }
                    
                    # Add additional groups for complex patterns
                    if len(match.groups()) > 1:
                        citation_info["author"] = match.group(1) if citation_type == "full_author" else None
                        citation_info["year"] = match.group(2) if citation_type == "full_author" else None
                    
                    citations.append(citation_info)
        
        # Sort by position
        citations.sort(key=lambda x: x['start_position'])
        
        # Remove duplicates (same position)
        unique_citations = []
        seen_positions = set()
        for citation in citations:
            pos_key = (citation['start_position'], citation['end_position'])
            if pos_key not in seen_positions:
                unique_citations.append(citation)
                seen_positions.add(pos_key)
        
        return unique_citations
    
    def _extract_reference_list(self, content: str) -> List[Dict]:
        """Extract and parse reference list"""
        references = []
        
        # Find references section
        ref_patterns = [
            r'(?i)(references|bibliography|works\s+cited)\s*\n(.*?)(?=\n\s*(?:appendix|acknowledgment|figure|\Z))',
            r'(?i)(references|bibliography)\s*\n(.*?)(?=\Z)'
        ]
        
        ref_section = None
        for pattern in ref_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                ref_section = match.group(2)
                break
        
        if not ref_section:
            return references
        
        # Parse individual references
        # Try different reference formats
        ref_formats = [
            r'\n\s*(\d+)\.\s*([^\n]+(?:\n(?!\s*\d+\.)[^\n]+)*)',  # Numbered: "1. Author..."
            r'\n\s*\[(\d+)\]\s*([^\n]+(?:\n(?!\s*\[\d+\])[^\n]+)*)',  # Bracketed: "[1] Author..."
            r'\n\s*([A-Za-z]+,?\s*[A-Za-z]*\.?.*?)(?=\n\s*(?:[A-Za-z]+,|$))'  # Author-based
        ]
        
        for format_pattern in ref_formats:
            matches = re.findall(format_pattern, ref_section, re.MULTILINE | re.DOTALL)
            if matches:
                for match in matches:
                    if isinstance(match, tuple) and len(match) == 2:
                        ref_number, ref_text = match
                        ref_info = self._parse_reference_text(ref_text.strip(), ref_number)
                        references.append(ref_info)
                break
        
        return references
    
    def _parse_reference_text(self, ref_text: str, ref_number: str = "") -> Dict:
        """Parse individual reference text"""
        ref_info = {
            "number": ref_number,
            "full_text": ref_text,
            "authors": [],
            "title": "",
            "journal": "",
            "year": None,
            "volume": "",
            "pages": "",
            "doi": "",
            "url": ""
        }
        
        # Extract DOI
        doi_match = re.search(r'(?:doi|DOI)[:\s]*([^\s]+)', ref_text)
        if doi_match:
            ref_info["doi"] = doi_match.group(1)
        
        # Extract URL
        url_match = re.search(r'(https?://[^\s]+)', ref_text)
        if url_match:
            ref_info["url"] = url_match.group(1)
        
        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', ref_text)
        if year_match:
            ref_info["year"] = int(year_match.group(0))
        
        # Extract title (usually in quotes or after authors)
        title_patterns = [
            r'"([^"]+)"',  # Quoted title
            r'\'([^\']+)\'',  # Single quoted
            r'\.([^.]+\.)\s*[A-Z]',  # Between periods before journal
        ]
        
        for pattern in title_patterns:
            title_match = re.search(pattern, ref_text)
            if title_match:
                title = title_match.group(1).strip()
                if 10 < len(title) < 200:  # Reasonable title length
                    ref_info["title"] = title
                    break
        
        # Extract authors (simplified - first few words before year or title)
        author_part = ref_text.split(str(ref_info["year"]))[0] if ref_info["year"] else ref_text[:100]
        author_patterns = [
            r'([A-Z][a-z]+,\s*[A-Z]\.(?:\s*[A-Z]\.)*)',  # Last, F. M.
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # First Last
        ]
        
        for pattern in author_patterns:
            authors = re.findall(pattern, author_part)
            if authors:
                ref_info["authors"] = authors[:5]  # Limit to 5 authors
                break
        
        # Extract journal/venue (heuristic)
        if ref_info["title"]:
            # Text after title might be journal
            title_pos = ref_text.find(ref_info["title"])
            if title_pos != -1:
                after_title = ref_text[title_pos + len(ref_info["title"]):]
                journal_match = re.search(r'\.?\s*([A-Za-z\s&]+(?:Journal|Proceedings|Conference|Review))', after_title)
                if journal_match:
                    ref_info["journal"] = journal_match.group(1).strip()
        
        return ref_info
    
    def _get_citation_context(self, content: str, start_pos: int, end_pos: int, 
                            context_chars: int = 200) -> Dict:
        """Get context around a citation"""
        # Get text before and after citation
        before_start = max(0, start_pos - context_chars)
        after_end = min(len(content), end_pos + context_chars)
        
        before_text = content[before_start:start_pos]
        after_text = content[end_pos:after_end]
        citation_text = content[start_pos:end_pos]
        
        # Find sentence boundaries
        before_sentence = self._extract_sentence_containing_position(content, start_pos, "before")
        after_sentence = self._extract_sentence_containing_position(content, end_pos, "after")
        
        return {
            "before": before_text,
            "after": after_text,
            "citation": citation_text,
            "sentence": before_sentence + citation_text + after_sentence,
            "paragraph": self._extract_paragraph_containing_position(content, start_pos)
        }
    
    def _extract_sentence_containing_position(self, content: str, position: int, 
                                            direction: str = "both") -> str:
        """Extract sentence containing a specific position"""
        # Find sentence boundaries (. ! ?)
        sentences = re.split(r'[.!?]+', content)
        
        char_count = 0
        for sentence in sentences:
            sentence_start = char_count
            sentence_end = char_count + len(sentence)
            
            if sentence_start <= position <= sentence_end:
                return sentence.strip()
            
            char_count = sentence_end + 1  # +1 for the delimiter
        
        return ""
    
    def _extract_paragraph_containing_position(self, content: str, position: int) -> str:
        """Extract paragraph containing a specific position"""
        paragraphs = content.split('\n\n')
        
        char_count = 0
        for paragraph in paragraphs:
            para_start = char_count
            para_end = char_count + len(paragraph)
            
            if para_start <= position <= para_end:
                return paragraph.strip()
            
            char_count = para_end + 2  # +2 for \n\n
        
        return ""
    
    def _identify_section_for_position(self, content: str, position: int) -> str:
        """Identify which section a position belongs to"""
        # Simple section detection
        section_pattern = r'^\s*(?:\d+\.?\s*)?([A-Z][A-Za-z\s]+)\s*$'
        
        lines = content[:position].split('\n')
        current_section = "Introduction"  # Default
        
        for line in reversed(lines):
            if re.match(section_pattern, line.strip()) and len(line.strip()) < 100:
                current_section = line.strip()
                break
        
        return current_section
    
    def _map_citations_to_sections(self, content: str) -> Dict:
        """Map citation distribution across sections"""
        sections = self._extract_sections_with_positions(content)
        inline_citations = self._extract_inline_citations(content)
        
        section_citations = {}
        
        for section in sections:
            section_name = section['title']
            section_start = section['start_position']
            section_end = section['end_position']
            
            # Find citations in this section
            section_cites = [
                cite for cite in inline_citations 
                if section_start <= cite['start_position'] < section_end
            ]
            
            section_citations[section_name] = {
                "citation_count": len(section_cites),
                "citations": section_cites,
                "citation_density": len(section_cites) / max(1, (section_end - section_start) / 1000)  # per 1000 chars
            }
        
        return section_citations
    
    def _extract_sections_with_positions(self, content: str) -> List[Dict]:
        """Extract sections with their character positions"""
        sections = []
        section_pattern = r'^\s*(?:\d+\.?\s*)?([A-Z][A-Za-z\s]+)\s*$'
        
        lines = content.split('\n')
        char_position = 0
        
        for i, line in enumerate(lines):
            if re.match(section_pattern, line.strip()) and len(line.strip()) < 100:
                sections.append({
                    "title": line.strip(),
                    "line_number": i + 1,
                    "start_position": char_position
                })
            
            char_position += len(line) + 1  # +1 for newline
        
        # Set end positions
        for i in range(len(sections)):
            if i + 1 < len(sections):
                sections[i]["end_position"] = sections[i + 1]["start_position"]
            else:
                sections[i]["end_position"] = len(content)
        
        return sections
    
    def _extract_citation_contexts(self, content: str) -> List[Dict]:
        """Extract key citation contexts for literature review writing"""
        inline_citations = self._extract_inline_citations(content)
        contexts = []
        
        for citation in inline_citations:
            context = citation["context"]
            
            # Identify if this is a key claim or finding
            sentence = context["sentence"].lower()
            
            is_key_claim = any(indicator in sentence for indicator in [
                'show', 'demonstrate', 'find', 'result', 'conclude', 'report',
                'achieve', 'improve', 'increase', 'decrease', 'significant'
            ])
            
            if is_key_claim:
                contexts.append({
                    "citation": citation,
                    "claim_type": self._classify_claim_type(sentence),
                    "evidence_strength": self._assess_evidence_strength(sentence),
                    "section": citation["section"],
                    "quotable_text": context["sentence"]
                })
        
        return contexts
    
    def _classify_claim_type(self, sentence: str) -> str:
        """Classify the type of claim being made"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['result', 'find', 'show']):
            return 'finding'
        elif any(word in sentence_lower for word in ['method', 'approach', 'technique']):
            return 'methodology'
        elif any(word in sentence_lower for word in ['improve', 'better', 'enhance']):
            return 'improvement'
        elif any(word in sentence_lower for word in ['compare', 'versus', 'than']):
            return 'comparison'
        else:
            return 'general'
    
    def _assess_evidence_strength(self, sentence: str) -> str:
        """Assess the strength of evidence in a sentence"""
        sentence_lower = sentence.lower()
        
        strong_indicators = ['significant', 'clearly', 'demonstrate', 'prove', 'confirm']
        moderate_indicators = ['suggest', 'indicate', 'show', 'reveal']
        weak_indicators = ['may', 'might', 'could', 'possibly', 'potentially']
        
        if any(indicator in sentence_lower for indicator in strong_indicators):
            return 'strong'
        elif any(indicator in sentence_lower for indicator in moderate_indicators):
            return 'moderate'
        elif any(indicator in sentence_lower for indicator in weak_indicators):
            return 'weak'
        else:
            return 'neutral'
    
    def _identify_key_claims_with_citations(self, content: str) -> List[Dict]:
        """Identify key claims that are well-cited"""
        inline_citations = self._extract_inline_citations(content)
        key_claims = []
        
        for citation in inline_citations:
            context = citation["context"]
            sentence = context["sentence"]
            
            # Look for quantitative claims
            if re.search(r'\d+%|\d+\.\d+|\d+\s*±|\d+\s*times', sentence):
                key_claims.append({
                    "type": "quantitative",
                    "claim": sentence,
                    "citation": citation,
                    "section": citation["section"],
                    "evidence_type": "numerical"
                })
            
            # Look for comparative claims
            elif any(word in sentence.lower() for word in ['better', 'higher', 'lower', 'faster', 'improved']):
                key_claims.append({
                    "type": "comparative",
                    "claim": sentence,
                    "citation": citation,
                    "section": citation["section"],
                    "evidence_type": "comparative"
                })
        
        return key_claims
    
    def _calculate_citation_density(self, content: str) -> Dict:
        """Calculate citation density statistics"""
        inline_citations = self._extract_inline_citations(content)
        word_count = len(content.split())
        
        return {
            "total_citations": len(inline_citations),
            "citations_per_1000_words": (len(inline_citations) / word_count) * 1000 if word_count > 0 else 0,
            "sections_with_citations": len(set(cite["section"] for cite in inline_citations)),
            "avg_citations_per_section": len(inline_citations) / max(1, len(set(cite["section"] for cite in inline_citations)))
        }
    
    def _link_inline_to_references(self, inline_citations: List[Dict], 
                                  reference_list: List[Dict]) -> List[Dict]:
        """Link inline citations to reference list entries"""
        links = []
        
        for inline_cite in inline_citations:
            citation_key = inline_cite["citation_key"]
            
            # Try to match by number
            if citation_key.isdigit():
                ref_number = int(citation_key)
                matching_refs = [ref for ref in reference_list if ref["number"] == str(ref_number)]
                
                if matching_refs:
                    links.append({
                        "inline_citation": inline_cite,
                        "reference": matching_refs[0],
                        "match_confidence": "high"
                    })
            
            # Try to match by author
            elif inline_cite.get("author"):
                author = inline_cite["author"]
                matching_refs = [ref for ref in reference_list 
                               if any(author.lower() in auth.lower() for auth in ref["authors"])]
                
                if matching_refs:
                    links.append({
                        "inline_citation": inline_cite,
                        "reference": matching_refs[0],
                        "match_confidence": "medium"
                    })
        
        return links


# Helper functions for external use
def track_citations_in_paper(content: str, paper_metadata: Dict) -> Dict:
    """
    Track all citations in a paper
    
    Args:
        content: Paper text
        paper_metadata: Paper metadata
        
    Returns:
        Complete citation tracking data
    """
    tracker = CitationTracker()
    return tracker.build_citation_map(content, paper_metadata)


def verify_citation_accuracy(section_content: str, evidence_sources: List[Dict]) -> Dict:
    """
    Verify that citations in written content are accurate
    
    Args:
        section_content: Written literature review section
        evidence_sources: Available evidence sources
        
    Returns:
        Citation verification report
    """
    tracker = CitationTracker()
    
    # Extract citations from written content
    cited_papers = tracker._extract_inline_citations(section_content)
    
    # Check against available evidence
    verification = {
        "total_citations": len(cited_papers),
        "verified_citations": 0,
        "unverified_citations": [],
        "missing_evidence": [],
        "accuracy_score": 0.0
    }
    
    for citation in cited_papers:
        citation_key = citation["citation_key"]
        
        # Check if this citation has corresponding evidence
        has_evidence = any(
            citation_key in str(source.get("citation", "")) or 
            citation_key in str(source.get("paper", {}).get("title", ""))
            for source in evidence_sources
        )
        
        if has_evidence:
            verification["verified_citations"] += 1
        else:
            verification["unverified_citations"].append(citation)
    
    verification["accuracy_score"] = (
        verification["verified_citations"] / max(1, verification["total_citations"])
    )
    
    return verification


if __name__ == "__main__":
    # Test citation tracking
    print("🧪 Testing CitationTracker...")
    
    sample_text = """
    Machine learning has shown great promise in chemistry [1,2]. 
    Smith et al. (2020) demonstrated significant improvements in molecular property prediction.
    The results show 89% accuracy compared to traditional methods [3].
    """
    
    sample_metadata = {
        "title": "Test Paper",
        "authors": ["Test Author"],
        "year": 2024
    }
    
    tracker = CitationTracker()
    citation_map = tracker.build_citation_map(sample_text, sample_metadata)
    
    print(f"✅ Found {len(citation_map['inline_citations'])} inline citations")
    print(f"✅ Citation tracking test complete!")
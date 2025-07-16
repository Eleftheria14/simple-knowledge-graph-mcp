"""
ChromaDB-Persistent Citation Manager

Replaces the in-memory citation manager with ChromaDB persistence.
Integrates with knowledge graph for provenance tracking.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings
from pydantic import BaseModel, Field

from ..utils.error_handling import ValidationError, ProcessingError

logger = logging.getLogger(__name__)


class CitationRecord(BaseModel):
    """Citation record for ChromaDB storage"""
    citation_key: str
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    document_path: Optional[str] = None
    abstract: Optional[str] = None
    
    # Citation usage tracking
    citation_count: int = 0
    first_cited: datetime = Field(default_factory=datetime.now)
    last_cited: Optional[datetime] = None
    
    # Knowledge graph integration
    linked_entities: List[str] = Field(default_factory=list, description="Entity IDs this citation supports")
    entity_contexts: Dict[str, str] = Field(default_factory=dict, description="Context for each linked entity")
    
    # Provenance tracking
    source_chunks: List[str] = Field(default_factory=list, description="Chunk IDs where citation was found")
    confidence_score: float = Field(default=1.0, description="Confidence in citation extraction")
    
    def to_chromadb_document(self) -> Dict[str, Any]:
        """Convert to ChromaDB document format"""
        return {
            "citation_key": self.citation_key,
            "title": self.title,
            "authors_json": json.dumps(self.authors),
            "year": self.year or 0,
            "journal": self.journal or "",
            "doi": self.doi or "",
            "url": self.url or "",
            "document_path": self.document_path or "",
            "abstract": self.abstract or "",
            "citation_count": self.citation_count,
            "first_cited": self.first_cited.isoformat(),
            "last_cited": self.last_cited.isoformat() if self.last_cited else "",
            "linked_entities_json": json.dumps(self.linked_entities),
            "entity_contexts_json": json.dumps(self.entity_contexts),
            "source_chunks_json": json.dumps(self.source_chunks),
            "confidence_score": self.confidence_score,
            "full_text": f"{self.title} {' '.join(self.authors)} {self.abstract or ''}"
        }
    
    @classmethod
    def from_chromadb_document(cls, doc_data: Dict[str, Any]) -> "CitationRecord":
        """Create from ChromaDB document"""
        return cls(
            citation_key=doc_data["citation_key"],
            title=doc_data["title"],
            authors=json.loads(doc_data["authors_json"]) if doc_data["authors_json"] else [],
            year=doc_data["year"] if doc_data["year"] > 0 else None,
            journal=doc_data["journal"] if doc_data["journal"] else None,
            doi=doc_data["doi"] if doc_data["doi"] else None,
            url=doc_data["url"] if doc_data["url"] else None,
            document_path=doc_data["document_path"] if doc_data["document_path"] else None,
            abstract=doc_data["abstract"] if doc_data["abstract"] else None,
            citation_count=doc_data["citation_count"],
            first_cited=datetime.fromisoformat(doc_data["first_cited"]),
            last_cited=datetime.fromisoformat(doc_data["last_cited"]) if doc_data["last_cited"] else None,
            linked_entities=json.loads(doc_data["linked_entities_json"]) if doc_data["linked_entities_json"] else [],
            entity_contexts=json.loads(doc_data["entity_contexts_json"]) if doc_data["entity_contexts_json"] else {},
            source_chunks=json.loads(doc_data["source_chunks_json"]) if doc_data["source_chunks_json"] else [],
            confidence_score=doc_data["confidence_score"]
        )


class ChromaDBCitationManager:
    """
    ChromaDB-persistent citation manager with knowledge graph integration.
    
    Features:
    - Persistent citation storage in ChromaDB
    - Entity-citation linking for provenance tracking
    - Citation usage tracking across sessions
    - Multiple academic citation formats
    - Semantic search over citations
    """
    
    def __init__(self, 
                 collection_name: str = "citations",
                 persist_directory: str = "chroma_citations_db"):
        """
        Initialize ChromaDB citation manager.
        
        Args:
            collection_name: Name of ChromaDB collection
            persist_directory: Directory for persistent storage
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"📚 Connected to existing citation collection: {collection_name}")
        except Exception:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Citation storage with knowledge graph links"}
            )
            logger.info(f"📚 Created new citation collection: {collection_name}")
        
        # Citation styles
        self.citation_styles = {
            "APA": self._format_apa,
            "IEEE": self._format_ieee,
            "Nature": self._format_nature,
            "MLA": self._format_mla
        }
        
        logger.info(f"📚 ChromaDB Citation Manager initialized")
        logger.info(f"   💾 Storage: {self.persist_directory}")
        logger.info(f"   📊 Collection: {collection_name}")
    
    def add_citation(self, 
                    title: str,
                    authors: List[str] = None,
                    year: int = None,
                    linked_entities: List[str] = None,
                    entity_contexts: Dict[str, str] = None,
                    source_chunks: List[str] = None,
                    **kwargs) -> str:
        """
        Add citation with knowledge graph links.
        
        Args:
            title: Citation title
            authors: List of authors
            year: Publication year
            linked_entities: Entity IDs this citation supports
            entity_contexts: Context for each linked entity
            source_chunks: Source chunk IDs
            **kwargs: Additional metadata
            
        Returns:
            Citation key
        """
        # Generate citation key
        citation_key = self._generate_citation_key(title, authors or [], year)
        
        # Create citation record
        citation_record = CitationRecord(
            citation_key=citation_key,
            title=title,
            authors=authors or [],
            year=year,
            linked_entities=linked_entities or [],
            entity_contexts=entity_contexts or {},
            source_chunks=source_chunks or [],
            **kwargs
        )
        
        # Check if citation already exists
        existing = self._get_citation_by_key(citation_key)
        if existing:
            # Update existing citation
            existing.citation_count += 1
            existing.last_cited = datetime.now()
            existing.linked_entities = list(set(existing.linked_entities + citation_record.linked_entities))
            existing.entity_contexts.update(citation_record.entity_contexts)
            existing.source_chunks = list(set(existing.source_chunks + citation_record.source_chunks))
            
            self._update_citation_in_chromadb(existing)
            logger.info(f"📚 Updated existing citation: {citation_key}")
        else:
            # Add new citation
            self._add_citation_to_chromadb(citation_record)
            logger.info(f"📚 Added new citation: {citation_key}")
            logger.info(f"   🔗 Linked to {len(citation_record.linked_entities)} entities")
        
        return citation_key
    
    def link_citation_to_entity(self, 
                               citation_key: str,
                               entity_id: str,
                               context: str = "") -> bool:
        """
        Link citation to knowledge graph entity.
        
        Args:
            citation_key: Citation identifier
            entity_id: Entity identifier from knowledge graph
            context: Context of the link
            
        Returns:
            Success status
        """
        citation = self._get_citation_by_key(citation_key)
        if not citation:
            logger.error(f"Citation not found: {citation_key}")
            return False
        
        # Add entity link
        if entity_id not in citation.linked_entities:
            citation.linked_entities.append(entity_id)
        
        # Add context
        if context:
            citation.entity_contexts[entity_id] = context
        
        # Update citation count and timestamp
        citation.citation_count += 1
        citation.last_cited = datetime.now()
        
        # Update in ChromaDB
        self._update_citation_in_chromadb(citation)
        
        logger.info(f"🔗 Linked citation {citation_key} to entity {entity_id}")
        return True
    
    def get_citations_for_entity(self, entity_id: str) -> List[CitationRecord]:
        """
        Get all citations supporting a specific entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            List of citation records
        """
        try:
            # Query ChromaDB for citations containing this entity
            results = self.collection.query(
                query_texts=[entity_id],
                n_results=100,
                where={"linked_entities_json": {"$contains": entity_id}}
            )
            
            citations = []
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                if metadata and entity_id in json.loads(metadata.get("linked_entities_json", "[]")):
                    citation = CitationRecord.from_chromadb_document(metadata)
                    citations.append(citation)
            
            return citations
            
        except Exception as e:
            logger.error(f"Failed to get citations for entity {entity_id}: {e}")
            return []
    
    def search_citations(self, 
                        query: str,
                        limit: int = 10,
                        filter_by_entities: List[str] = None) -> List[CitationRecord]:
        """
        Semantic search over citations.
        
        Args:
            query: Search query
            limit: Maximum results
            filter_by_entities: Filter by linked entities
            
        Returns:
            List of relevant citations
        """
        try:
            where_clause = {}
            if filter_by_entities:
                # Filter by entities (simplified - would need better query logic)
                pass
            
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            citations = []
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                if metadata:
                    citation = CitationRecord.from_chromadb_document(metadata)
                    citations.append(citation)
            
            return citations
            
        except Exception as e:
            logger.error(f"Citation search failed: {e}")
            return []
    
    def generate_bibliography(self, 
                            style: str = "APA",
                            entity_filter: List[str] = None,
                            used_only: bool = False) -> str:
        """
        Generate bibliography in specified style.
        
        Args:
            style: Citation style (APA, IEEE, Nature, MLA)
            entity_filter: Only include citations for these entities
            used_only: Only include citations that have been used/tracked
            
        Returns:
            Formatted bibliography
        """
        if style not in self.citation_styles:
            raise ValueError(f"Unsupported citation style: {style}")
        
        # Get all citations or filtered ones
        if entity_filter:
            citations = []
            for entity_id in entity_filter:
                citations.extend(self.get_citations_for_entity(entity_id))
            # Remove duplicates
            citations = list({c.citation_key: c for c in citations}.values())
        else:
            citations = self._get_all_citations()
        
        # Filter to used citations only if requested
        if used_only:
            citations = [c for c in citations if c.citation_count > 0]
        
        # Sort by author, year, title
        citations.sort(key=lambda c: (c.authors[0] if c.authors else "", c.year or 0, c.title))
        
        # Format bibliography
        formatter = self.citation_styles[style]
        bibliography_entries = []
        
        for citation in citations:
            formatted = formatter(citation)
            bibliography_entries.append(formatted)
        
        return "\\n".join(bibliography_entries)
    
    def track_citation(self, 
                      citation_key: str,
                      context_text: str = "",
                      section: str = "",
                      confidence: float = 1.0) -> bool:
        """
        Track usage of a citation.
        
        Args:
            citation_key: Citation identifier
            context_text: Context where citation is used
            section: Section of document where used
            confidence: Confidence in citation relevance
            
        Returns:
            Success status
        """
        try:
            citation = self._get_citation_by_key(citation_key)
            if not citation:
                logger.warning(f"Citation not found for tracking: {citation_key}")
                return False
            
            # Update citation usage
            citation.citation_count += 1
            citation.last_cited = datetime.now()
            
            # Track context if provided
            if context_text:
                # Store usage context in entity_contexts (repurposing for usage tracking)
                usage_key = f"usage_{len(citation.entity_contexts) + 1}"
                citation.entity_contexts[usage_key] = f"{section}: {context_text}"
            
            # Update confidence score (weighted average)
            if citation.citation_count > 1:
                citation.confidence_score = (citation.confidence_score + confidence) / 2
            else:
                citation.confidence_score = confidence
            
            # Update in ChromaDB
            self._update_citation_in_chromadb(citation)
            
            logger.info(f"📚 Tracked citation usage: {citation_key} (count: {citation.citation_count})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track citation {citation_key}: {e}")
            return False
    
    def get_citation_usage(self, citation_key: str) -> Dict[str, Any]:
        """
        Get usage statistics for a specific citation.
        
        Args:
            citation_key: Citation identifier
            
        Returns:
            Usage statistics
        """
        try:
            citation = self._get_citation_by_key(citation_key)
            if not citation:
                return {"error": f"Citation not found: {citation_key}"}
            
            return {
                "citation_key": citation_key,
                "usage_count": citation.citation_count,
                "first_cited": citation.first_cited.isoformat(),
                "last_cited": citation.last_cited.isoformat() if citation.last_cited else None,
                "confidence_score": citation.confidence_score,
                "contexts": citation.entity_contexts,
                "linked_entities": citation.linked_entities
            }
            
        except Exception as e:
            logger.error(f"Failed to get citation usage for {citation_key}: {e}")
            return {"error": str(e)}
    
    def get_used_citations(self) -> List[CitationRecord]:
        """Get all citations that have been used (citation_count > 0)"""
        try:
            all_citations = self._get_all_citations()
            return [c for c in all_citations if c.citation_count > 0]
        except Exception as e:
            logger.error(f"Failed to get used citations: {e}")
            return []
    
    def get_unused_citations(self) -> List[CitationRecord]:
        """Get all citations that have not been used (citation_count = 0)"""
        try:
            all_citations = self._get_all_citations()
            return [c for c in all_citations if c.citation_count == 0]
        except Exception as e:
            logger.error(f"Failed to get unused citations: {e}")
            return []
    
    def generate_in_text_citation(self, citation_key: str, style: str = "APA") -> str:
        """
        Generate in-text citation for a specific citation.
        
        Args:
            citation_key: Citation identifier
            style: Citation style (APA, IEEE, Nature, MLA)
            
        Returns:
            Formatted in-text citation
        """
        try:
            citation = self._get_citation_by_key(citation_key)
            if not citation:
                return f"[{citation_key}]"
            
            if style == "APA":
                if citation.authors:
                    author = citation.authors[0].split()[-1]  # Last name
                    return f"({author}, {citation.year or 'n.d.'})"
                else:
                    return f"({citation.year or 'n.d.'})"
            elif style == "IEEE":
                return f"[{citation_key}]"
            elif style == "Nature":
                return f"^{citation_key}"
            elif style == "MLA":
                if citation.authors:
                    author = citation.authors[0].split()[-1]  # Last name
                    return f"({author})"
                else:
                    return f"({citation.title[:20]}...)"
            else:
                return f"[{citation_key}]"
                
        except Exception as e:
            logger.error(f"Failed to generate in-text citation for {citation_key}: {e}")
            return f"[{citation_key}]"

    def get_citation_stats(self) -> Dict[str, Any]:
        """Get citation statistics"""
        try:
            # Get collection count
            collection_count = self.collection.count()
            
            # Get all citations for detailed stats
            all_citations = self._get_all_citations()
            
            # Calculate statistics
            total_citations = len(all_citations)
            used_citations = len([c for c in all_citations if c.citation_count > 0])
            total_entities_linked = sum(len(c.linked_entities) for c in all_citations)
            
            # Year distribution
            years = [c.year for c in all_citations if c.year]
            year_range = (min(years), max(years)) if years else (None, None)
            
            return {
                "total_citations": total_citations,
                "used_citations": used_citations,
                "unused_citations": total_citations - used_citations,
                "total_entity_links": total_entities_linked,
                "year_range": year_range,
                "collection_count": collection_count,
                "storage_directory": str(self.persist_directory),
                "supported_styles": list(self.citation_styles.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to get citation stats: {e}")
            return {"error": str(e)}
    
    def _generate_citation_key(self, title: str, authors: List[str], year: int = None) -> str:
        """Generate unique citation key"""
        # Use first author's last name
        if authors:
            first_author = authors[0].split()[-1].lower()  # Get last name
        else:
            first_author = "unknown"
        
        # Use year or "unknown"
        year_str = str(year) if year else "unknown"
        
        # Use first significant word from title
        title_words = [word for word in title.lower().split() if len(word) > 3]
        title_word = title_words[0] if title_words else "untitled"
        
        return f"{first_author}{year_str}{title_word}"
    
    def _get_citation_by_key(self, citation_key: str) -> Optional[CitationRecord]:
        """Get citation by key from ChromaDB"""
        try:
            results = self.collection.query(
                query_texts=[citation_key],
                n_results=1,
                where={"citation_key": citation_key}
            )
            
            if results["ids"][0]:
                metadata = results["metadatas"][0][0]
                return CitationRecord.from_chromadb_document(metadata)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get citation by key {citation_key}: {e}")
            return None
    
    def _get_all_citations(self) -> List[CitationRecord]:
        """Get all citations from ChromaDB"""
        try:
            results = self.collection.query(
                query_texts=[""],
                n_results=1000  # Adjust as needed
            )
            
            citations = []
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                if metadata:
                    citation = CitationRecord.from_chromadb_document(metadata)
                    citations.append(citation)
            
            return citations
            
        except Exception as e:
            logger.error(f"Failed to get all citations: {e}")
            return []
    
    def _add_citation_to_chromadb(self, citation: CitationRecord):
        """Add citation to ChromaDB"""
        doc_data = citation.to_chromadb_document()
        
        self.collection.add(
            documents=[doc_data["full_text"]],
            metadatas=[doc_data],
            ids=[citation.citation_key]
        )
    
    def _update_citation_in_chromadb(self, citation: CitationRecord):
        """Update citation in ChromaDB"""
        doc_data = citation.to_chromadb_document()
        
        self.collection.update(
            ids=[citation.citation_key],
            documents=[doc_data["full_text"]],
            metadatas=[doc_data]
        )
    
    # Citation formatting methods
    def _format_apa(self, citation: CitationRecord) -> str:
        """Format citation in APA style"""
        authors_str = ", ".join(citation.authors) if citation.authors else "Unknown Author"
        year_str = f"({citation.year})" if citation.year else "(n.d.)"
        title_str = citation.title
        
        formatted = f"{authors_str} {year_str}. {title_str}"
        
        if citation.journal:
            formatted += f". {citation.journal}"
        
        if citation.doi:
            formatted += f". https://doi.org/{citation.doi}"
        
        return formatted
    
    def _format_ieee(self, citation: CitationRecord) -> str:
        """Format citation in IEEE style"""
        authors_str = ", ".join(citation.authors) if citation.authors else "Unknown Author"
        title_str = f'"{citation.title}"'
        year_str = citation.year if citation.year else "n.d."
        
        formatted = f"{authors_str}, {title_str}, {year_str}"
        
        if citation.journal:
            formatted += f", {citation.journal}"
        
        if citation.doi:
            formatted += f", doi: {citation.doi}"
        
        return formatted
    
    def _format_nature(self, citation: CitationRecord) -> str:
        """Format citation in Nature style"""
        authors_str = ", ".join(citation.authors) if citation.authors else "Unknown Author"
        title_str = citation.title
        year_str = citation.year if citation.year else "n.d."
        
        formatted = f"{authors_str}. {title_str}. {year_str}"
        
        if citation.journal:
            formatted += f" {citation.journal}"
        
        if citation.doi:
            formatted += f" https://doi.org/{citation.doi}"
        
        return formatted
    
    def _format_mla(self, citation: CitationRecord) -> str:
        """Format citation in MLA style"""
        if citation.authors:
            authors_str = citation.authors[0]
            if len(citation.authors) > 1:
                authors_str += ", et al."
        else:
            authors_str = "Unknown Author"
        
        title_str = f'"{citation.title}"'
        year_str = citation.year if citation.year else "n.d."
        
        formatted = f"{authors_str}. {title_str}. {year_str}"
        
        if citation.journal:
            formatted += f". {citation.journal}"
        
        if citation.doi:
            formatted += f". Web. doi:{citation.doi}"
        
        return formatted
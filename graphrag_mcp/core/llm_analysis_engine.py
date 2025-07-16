"""
LLM Analysis Engine for Comprehensive Sequential Processing

Performs comprehensive analysis of text chunks using llama3.1:8b to extract:
- Entities with types and properties
- Citations with context and metadata
- Relationships between entities
- Enhanced chunks with entity enrichment

This is the core component that replaces parallel processing with
sequential accuracy-first analysis.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from ..utils.error_handling import ProcessingError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Entity extracted from text with provenance"""
    entity_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source_context: str = ""
    source_location: str = ""
    related_citations: List[str] = field(default_factory=list)


@dataclass
class ExtractedCitation:
    """Citation extracted from text with full context"""
    citation_key: str
    citation_text: str
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_type: str = "reference"  # inline, reference, footnote
    context: str = ""
    location: str = ""
    confidence: float = 1.0
    supporting_entities: List[str] = field(default_factory=list)


@dataclass
class ExtractedRelationship:
    """Relationship between entities with provenance"""
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float = 1.0
    context: str = ""
    supporting_citations: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedChunk:
    """Text chunk enhanced with entity and citation metadata"""
    chunk_id: str
    original_text: str
    enhanced_text: str
    entities: List[ExtractedEntity] = field(default_factory=list)
    citations: List[ExtractedCitation] = field(default_factory=list)
    relationships: List[ExtractedRelationship] = field(default_factory=list)
    importance_score: float = 0.5
    processing_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Complete analysis result from LLM processing"""
    entities: List[ExtractedEntity]
    citations: List[ExtractedCitation]
    relationships: List[ExtractedRelationship]
    enhanced_chunks: List[EnhancedChunk]
    processing_stats: Dict[str, Any]
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)


class LLMAnalysisEngine:
    """
    Comprehensive LLM analysis engine for sequential processing.
    
    This engine replaces parallel processing with a single comprehensive
    analysis pass that extracts entities, citations, and relationships
    in a coordinated manner for maximum accuracy.
    """
    
    def __init__(self, 
                 llm_model: str = "llama3.1:8b",
                 temperature: float = 0.1,
                 max_context: int = 32768,
                 max_predict: int = 4096):
        """
        Initialize LLM analysis engine.
        
        Args:
            llm_model: Ollama model identifier
            temperature: LLM temperature setting
            max_context: Maximum context length
            max_predict: Maximum prediction length
        """
        self.llm_model = llm_model
        self.temperature = temperature
        self.max_context = max_context
        self.max_predict = max_predict
        
        # Initialize LLM
        try:
            self.llm = ChatOllama(
                model=llm_model,
                temperature=temperature,
                num_ctx=max_context,
                num_predict=max_predict
            )
            logger.info(f"🧠 LLM Analysis Engine initialized with {llm_model}")
        except Exception as e:
            raise ProcessingError(f"Failed to initialize LLM: {e}")
        
        # Analysis templates
        self.comprehensive_analysis_template = self._create_comprehensive_template()
        self.entity_enhancement_template = self._create_entity_enhancement_template()
        self.citation_extraction_template = self._create_citation_extraction_template()
        
        # Processing statistics
        self.processing_stats = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "average_processing_time": 0.0,
            "total_entities_extracted": 0,
            "total_citations_extracted": 0,
            "total_relationships_extracted": 0
        }
    
    def analyze_document_comprehensive(self, 
                                     text_chunks: List[str],
                                     document_title: str = "",
                                     document_path: str = "") -> AnalysisResult:
        """
        Perform comprehensive analysis of document chunks.
        
        Args:
            text_chunks: List of text chunks to analyze
            document_title: Document title for context
            document_path: Document path for provenance
            
        Returns:
            Complete analysis result
        """
        logger.info(f"🔍 Starting comprehensive document analysis")
        logger.info(f"   📄 Document: {document_title}")
        logger.info(f"   📊 Chunks: {len(text_chunks)}")
        
        start_time = time.time()
        
        try:
            # Step 1: Comprehensive analysis of substantial content
            analysis_content = self._prepare_analysis_content(text_chunks)
            comprehensive_result = self._run_comprehensive_analysis(analysis_content, document_title)
            
            # Step 2: Create enhanced chunks with entity enrichment
            enhanced_chunks = self._create_enhanced_chunks(
                text_chunks, 
                comprehensive_result['entities'],
                comprehensive_result['citations'],
                comprehensive_result['relationships']
            )
            
            # Step 3: Extract structured data
            entities = self._process_entities(comprehensive_result['entities'], document_path)
            citations = self._process_citations(comprehensive_result['citations'], document_path)
            relationships = self._process_relationships(comprehensive_result['relationships'])
            
            # Step 4: Create analysis result
            processing_time = time.time() - start_time
            
            result = AnalysisResult(
                entities=entities,
                citations=citations,
                relationships=relationships,
                enhanced_chunks=enhanced_chunks,
                processing_stats={
                    "processing_time": processing_time,
                    "chunks_analyzed": len(text_chunks),
                    "entities_extracted": len(entities),
                    "citations_extracted": len(citations),
                    "relationships_extracted": len(relationships),
                    "enhanced_chunks_created": len(enhanced_chunks),
                    "analysis_method": "comprehensive_sequential"
                },
                analysis_metadata={
                    "document_title": document_title,
                    "document_path": document_path,
                    "llm_model": self.llm_model,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            )
            
            # Update statistics
            self._update_processing_stats(result, processing_time)
            
            logger.info(f"✅ Comprehensive analysis completed in {processing_time:.2f}s")
            logger.info(f"   👥 Entities: {len(entities)}")
            logger.info(f"   📚 Citations: {len(citations)}")
            logger.info(f"   🔗 Relationships: {len(relationships)}")
            logger.info(f"   ✨ Enhanced chunks: {len(enhanced_chunks)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Comprehensive analysis failed: {e}")
            self.processing_stats["failed_analyses"] += 1
            raise ProcessingError(f"Analysis failed: {e}")
    
    def _prepare_analysis_content(self, text_chunks: List[str]) -> str:
        """
        Prepare content for analysis by combining chunks intelligently.
        
        Args:
            text_chunks: List of text chunks
            
        Returns:
            Combined content for analysis
        """
        # Use substantial content for analysis (first 12k characters)
        combined_text = " ".join(text_chunks)
        
        # Take first 12k characters but try to break at sentence boundaries
        if len(combined_text) > 12000:
            content = combined_text[:12000]
            # Try to end at a sentence
            last_period = content.rfind('.')
            if last_period > 8000:  # Only truncate if we have substantial content
                content = content[:last_period + 1]
        else:
            content = combined_text
        
        logger.info(f"📝 Prepared {len(content)} characters for analysis")
        return content
    
    def _run_comprehensive_analysis(self, content: str, document_title: str) -> Dict[str, Any]:
        """
        Run comprehensive LLM analysis to extract all information.
        
        Args:
            content: Text content to analyze
            document_title: Document title for context
            
        Returns:
            Comprehensive analysis result
        """
        chain = self.comprehensive_analysis_template | self.llm | StrOutputParser()
        
        try:
            logger.info("🧠 Running comprehensive LLM analysis...")
            result = chain.invoke({
                "content": content,
                "document_title": document_title
            })
            
            # Parse JSON response
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start == -1 or json_end == -1:
                raise ValueError("No valid JSON found in LLM response")
            
            json_str = result[json_start:json_end]
            analysis_data = json.loads(json_str)
            
            # Validate analysis data
            if not isinstance(analysis_data, dict):
                raise ValueError("Invalid analysis data format")
            
            # Ensure required keys
            analysis_data.setdefault("entities", [])
            analysis_data.setdefault("citations", [])
            analysis_data.setdefault("relationships", [])
            
            logger.info("✅ Comprehensive analysis completed successfully")
            return analysis_data
            
        except Exception as e:
            logger.error(f"❌ Comprehensive analysis failed: {e}")
            # Return fallback analysis
            return {
                "entities": [],
                "citations": [],
                "relationships": [],
                "analysis_error": str(e)
            }
    
    def _create_enhanced_chunks(self, 
                              original_chunks: List[str],
                              entities: List[Dict[str, Any]],
                              citations: List[Dict[str, Any]],
                              relationships: List[Dict[str, Any]]) -> List[EnhancedChunk]:
        """
        Create enhanced chunks with entity and citation enrichment.
        
        Args:
            original_chunks: Original text chunks
            entities: Extracted entities
            citations: Extracted citations
            relationships: Extracted relationships
            
        Returns:
            List of enhanced chunks
        """
        logger.info("✨ Creating enhanced chunks with entity enrichment...")
        
        enhanced_chunks = []
        
        for i, chunk in enumerate(original_chunks):
            # Find entities mentioned in this chunk
            chunk_entities = []
            for entity in entities:
                entity_name = entity.get("name", "")
                if entity_name.lower() in chunk.lower():
                    chunk_entities.append(ExtractedEntity(
                        entity_id=entity.get("id", f"entity_{i}_{len(chunk_entities)}"),
                        entity_type=entity.get("type", "unknown"),
                        name=entity_name,
                        properties=entity.get("properties", {}),
                        confidence=entity.get("confidence", 1.0),
                        source_context=chunk[:200],
                        source_location=f"chunk_{i}"
                    ))
            
            # Find citations mentioned in this chunk
            chunk_citations = []
            for citation in citations:
                citation_text = citation.get("text", "")
                if citation_text and citation_text.lower() in chunk.lower():
                    chunk_citations.append(ExtractedCitation(
                        citation_key=citation.get("key", f"citation_{i}_{len(chunk_citations)}"),
                        citation_text=citation_text,
                        title=citation.get("title"),
                        authors=citation.get("authors", []),
                        year=citation.get("year"),
                        context=chunk[:300],
                        location=f"chunk_{i}",
                        confidence=citation.get("confidence", 1.0)
                    ))
            
            # Find relationships involving entities in this chunk
            chunk_relationships = []
            chunk_entity_ids = [e.entity_id for e in chunk_entities]
            for relationship in relationships:
                if (relationship.get("source") in chunk_entity_ids or 
                    relationship.get("target") in chunk_entity_ids):
                    chunk_relationships.append(ExtractedRelationship(
                        source_entity_id=relationship.get("source", ""),
                        target_entity_id=relationship.get("target", ""),
                        relationship_type=relationship.get("type", "related_to"),
                        confidence=relationship.get("confidence", 1.0),
                        context=relationship.get("context", "")
                    ))
            
            # Calculate importance score
            importance_score = self._calculate_chunk_importance(
                chunk, chunk_entities, chunk_citations, chunk_relationships
            )
            
            # Create enhanced text
            enhanced_text = self._create_enhanced_text(
                chunk, chunk_entities, chunk_citations
            )
            
            # Create enhanced chunk
            enhanced_chunk = EnhancedChunk(
                chunk_id=f"chunk_{i}",
                original_text=chunk,
                enhanced_text=enhanced_text,
                entities=chunk_entities,
                citations=chunk_citations,
                relationships=chunk_relationships,
                importance_score=importance_score,
                processing_metadata={
                    "entity_count": len(chunk_entities),
                    "citation_count": len(chunk_citations),
                    "relationship_count": len(chunk_relationships),
                    "enhancement_method": "comprehensive_analysis"
                }
            )
            
            enhanced_chunks.append(enhanced_chunk)
        
        logger.info(f"✨ Created {len(enhanced_chunks)} enhanced chunks")
        return enhanced_chunks
    
    def _calculate_chunk_importance(self, 
                                  chunk: str,
                                  entities: List[ExtractedEntity],
                                  citations: List[ExtractedCitation],
                                  relationships: List[ExtractedRelationship]) -> float:
        """Calculate importance score for a chunk"""
        base_score = 0.3
        
        # Entity importance
        entity_bonus = min(0.4, len(entities) * 0.1)
        
        # Citation importance
        citation_bonus = min(0.3, len(citations) * 0.15)
        
        # Relationship importance
        relationship_bonus = min(0.2, len(relationships) * 0.1)
        
        # Length bonus (prefer substantial chunks)
        length_bonus = min(0.1, len(chunk) / 2000)
        
        return min(1.0, base_score + entity_bonus + citation_bonus + relationship_bonus + length_bonus)
    
    def _create_enhanced_text(self, 
                            chunk: str,
                            entities: List[ExtractedEntity],
                            citations: List[ExtractedCitation]) -> str:
        """
        Create enhanced text with entity and citation context.
        
        This enhanced text will produce better embeddings because
        it includes explicit entity and citation information.
        """
        enhanced_text = chunk
        
        # Add entity context
        if entities:
            entity_context = []
            for entity in entities[:5]:  # Limit to top 5
                entity_context.append(f"{entity.entity_type}:{entity.name}")
            
            if entity_context:
                context_prefix = f"[Entities: {', '.join(entity_context)}] "
                enhanced_text = context_prefix + enhanced_text
        
        # Add citation context
        if citations:
            citation_count = len(citations)
            citation_context = f"[{citation_count} citations] "
            enhanced_text = citation_context + enhanced_text
        
        return enhanced_text
    
    def _process_entities(self, 
                         raw_entities: List[Dict[str, Any]],
                         document_path: str) -> List[ExtractedEntity]:
        """Process raw entities into structured format"""
        entities = []
        
        for i, entity_data in enumerate(raw_entities):
            if not isinstance(entity_data, dict):
                continue
                
            entity = ExtractedEntity(
                entity_id=entity_data.get("id", f"entity_{i}"),
                entity_type=entity_data.get("type", "unknown"),
                name=entity_data.get("name", ""),
                properties=entity_data.get("properties", {}),
                confidence=entity_data.get("confidence", 1.0),
                source_context=entity_data.get("context", ""),
                source_location=document_path
            )
            
            entities.append(entity)
        
        return entities
    
    def _process_citations(self, 
                          raw_citations: List[Dict[str, Any]],
                          document_path: str) -> List[ExtractedCitation]:
        """Process raw citations into structured format"""
        citations = []
        
        for i, citation_data in enumerate(raw_citations):
            if not isinstance(citation_data, dict):
                continue
            
            # Generate citation key
            citation_key = self._generate_citation_key(citation_data, i)
            
            citation = ExtractedCitation(
                citation_key=citation_key,
                citation_text=citation_data.get("text", ""),
                title=citation_data.get("title"),
                authors=citation_data.get("authors", []),
                year=citation_data.get("year"),
                journal=citation_data.get("journal"),
                doi=citation_data.get("doi"),
                url=citation_data.get("url"),
                citation_type=citation_data.get("type", "reference"),
                context=citation_data.get("context", ""),
                location=document_path,
                confidence=citation_data.get("confidence", 1.0)
            )
            
            citations.append(citation)
        
        return citations
    
    def _process_relationships(self, 
                             raw_relationships: List[Dict[str, Any]]) -> List[ExtractedRelationship]:
        """Process raw relationships into structured format"""
        relationships = []
        
        for relationship_data in raw_relationships:
            if not isinstance(relationship_data, dict):
                continue
            
            relationship = ExtractedRelationship(
                source_entity_id=relationship_data.get("source", ""),
                target_entity_id=relationship_data.get("target", ""),
                relationship_type=relationship_data.get("type", "related_to"),
                confidence=relationship_data.get("confidence", 1.0),
                context=relationship_data.get("context", ""),
                properties=relationship_data.get("properties", {})
            )
            
            relationships.append(relationship)
        
        return relationships
    
    def _generate_citation_key(self, citation_data: Dict[str, Any], index: int) -> str:
        """Generate unique citation key"""
        if citation_data.get("authors") and citation_data.get("year"):
            first_author = citation_data["authors"][0].split()[-1].lower()
            year = citation_data["year"]
            title_word = citation_data.get("title", "").split()[0].lower() if citation_data.get("title") else "paper"
            return f"{first_author}{year}{title_word}"
        else:
            return f"citation_{index}"
    
    def _update_processing_stats(self, result: AnalysisResult, processing_time: float):
        """Update processing statistics"""
        self.processing_stats["total_analyses"] += 1
        self.processing_stats["successful_analyses"] += 1
        self.processing_stats["total_entities_extracted"] += len(result.entities)
        self.processing_stats["total_citations_extracted"] += len(result.citations)
        self.processing_stats["total_relationships_extracted"] += len(result.relationships)
        
        # Update average processing time
        total_time = (self.processing_stats["average_processing_time"] * 
                     (self.processing_stats["total_analyses"] - 1) + processing_time)
        self.processing_stats["average_processing_time"] = total_time / self.processing_stats["total_analyses"]
    
    def _create_comprehensive_template(self) -> ChatPromptTemplate:
        """Create comprehensive analysis prompt template"""
        return ChatPromptTemplate.from_template("""
You are an expert research analyst. Analyze this document comprehensively and extract ALL important information.

Document: {document_title}

Content to analyze:
{content}

Extract the following information in a single JSON response:

1. ENTITIES: All important entities with their types, properties, and confidence scores
2. CITATIONS: All citations with full metadata and context
3. RELATIONSHIPS: How entities relate to each other with supporting evidence

Return a JSON object with this EXACT structure:
{{
  "entities": [
    {{
      "id": "unique_entity_id",
      "type": "author|organization|concept|method|technology|dataset|metric|location|publication|other",
      "name": "Entity name",
      "properties": {{"key": "value"}},
      "confidence": 0.95,
      "context": "Context where entity was found"
    }}
  ],
  "citations": [
    {{
      "key": "unique_citation_key",
      "text": "Exact citation text as it appears",
      "title": "Paper title if identifiable",
      "authors": ["Author names"],
      "year": 2023,
      "journal": "Journal name",
      "doi": "DOI if available",
      "url": "URL if available",
      "type": "inline|reference|footnote",
      "context": "Surrounding text for context",
      "confidence": 0.9
    }}
  ],
  "relationships": [
    {{
      "source": "source_entity_id",
      "target": "target_entity_id",
      "type": "uses|improves|implements|collaborates_with|cites|builds_on|evaluates|compares_to",
      "confidence": 0.85,
      "context": "Context explaining the relationship",
      "properties": {{"key": "value"}}
    }}
  ]
}}

BE THOROUGH AND ACCURATE. Extract ALL entities, citations, and relationships you can identify.

JSON:""")
    
    def _create_entity_enhancement_template(self) -> ChatPromptTemplate:
        """Create entity enhancement prompt template"""
        return ChatPromptTemplate.from_template("""
Enhance the following entities with additional context and properties:

Entities: {entities}
Text context: {context}

Return enhanced entities with additional properties and refined confidence scores.

JSON:""")
    
    def _create_citation_extraction_template(self) -> ChatPromptTemplate:
        """Create citation extraction prompt template"""
        return ChatPromptTemplate.from_template("""
Extract ALL citations from this text with full metadata and context:

Text: {text}

Return a JSON array of citations with complete information.

JSON:""")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.processing_stats,
            "model_info": {
                "llm_model": self.llm_model,
                "temperature": self.temperature,
                "max_context": self.max_context,
                "max_predict": self.max_predict
            }
        }
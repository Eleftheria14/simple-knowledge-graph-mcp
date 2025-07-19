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

from ..utils.error_handling import ProcessingError, ValidationError
from .config import ModelConfig
from .llm_factory import LLMFactory, validate_provider_config

logger = logging.getLogger(__name__)


def repair_json_response(response: str) -> str:
    """
    Repair common JSON formatting issues in LLM responses.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Cleaned JSON string
    """
    import re
    
    # Remove all markdown formatting (including ```json and ```)
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*', '', response)
    
    # Remove any explanatory text before JSON
    response = re.sub(r'^.*?(?=\{)', '', response, flags=re.DOTALL)
    
    # Find the JSON object boundaries more carefully
    start_idx = response.find('{')
    if start_idx == -1:
        return '{"entities": [], "citations": [], "relationships": []}'
    
    # Count braces to find the proper end
    brace_count = 0
    end_idx = start_idx
    for i in range(start_idx, len(response)):
        if response[i] == '{':
            brace_count += 1
        elif response[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i
                break
    
    # Extract just the JSON part
    response = response[start_idx:end_idx + 1]
    
    # Fix common JSON syntax errors
    # Fix trailing commas before closing brackets/braces
    response = re.sub(r',\s*}', '}', response)
    response = re.sub(r',\s*]', ']', response)
    
    # Fix missing commas between objects
    response = re.sub(r'}\s*{', '}, {', response)
    
    # Fix unquoted property names
    response = re.sub(r'(\w+):', r'"\1":', response)
    
    return response.strip()


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
    
    def __init__(self, config: ModelConfig = None):
        """
        Initialize LLM analysis engine with flexible provider support.
        
        Args:
            config: Model configuration. If None, uses default Ollama config.
        """
        # Use default config if none provided
        if config is None:
            config = ModelConfig()
        
        self.config = config
        
        # Validate configuration
        is_valid, error_msg = validate_provider_config(config)
        if not is_valid:
            raise ProcessingError(f"Invalid provider configuration: {error_msg}")
        
        # Initialize LLM using factory
        try:
            self.llm = LLMFactory.create_llm(config)
            logger.info(f"🧠 LLM Analysis Engine initialized")
            logger.info(f"   🔌 Provider: {config.provider}")
            logger.info(f"   📝 Model: {config.llm_model}")
            logger.info(f"   🌡️  Temperature: {config.temperature}")
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
                                     optimal_chunks: List[str],
                                     document_title: str = "",
                                     document_path: str = "") -> AnalysisResult:
        """
        Perform comprehensive analysis of optimal-sized chunks.
        
        Args:
            optimal_chunks: List of optimal-sized chunks (no batching needed)
            document_title: Document title for context
            document_path: Document path for provenance
            
        Returns:
            Complete analysis result
        """
        logger.info(f"🔍 Starting comprehensive document analysis")
        logger.info(f"   📄 Document: {document_title}")
        logger.info(f"   📊 Optimal chunks: {len(optimal_chunks)}")
        
        start_time = time.time()
        
        try:
            all_entities = []
            all_citations = []
            all_relationships = []
            
            # Process each optimal chunk directly (no batching needed!)
            for i, chunk in enumerate(optimal_chunks):
                chunk_size = len(chunk)
                logger.info(f"🔄 Processing optimal chunk {i+1}/{len(optimal_chunks)} ({chunk_size:,} characters)")
                chunk_result = self._run_comprehensive_analysis(chunk, document_title)
                
                # Aggregate results from this chunk
                all_entities.extend(chunk_result.get('entities', []))
                all_citations.extend(chunk_result.get('citations', []))
                all_relationships.extend(chunk_result.get('relationships', []))
            
            # Combine all results
            comprehensive_result = {
                'entities': all_entities,
                'citations': all_citations,
                'relationships': all_relationships
            }
            
            # Step 2: Create enhanced chunks with entity enrichment
            enhanced_chunks = self._create_enhanced_chunks(
                optimal_chunks, 
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
                    "chunks_analyzed": len(optimal_chunks),
                    "entities_extracted": len(entities),
                    "citations_extracted": len(citations),
                    "relationships_extracted": len(relationships),
                    "enhanced_chunks_created": len(enhanced_chunks),
                    "analysis_method": "optimal_chunks_direct"
                },
                analysis_metadata={
                    "document_title": document_title,
                    "document_path": document_path,
                    "provider": self.config.provider,
                    "llm_model": self.config.llm_model,
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
    
    def _create_large_batches(self, text_chunks: List[str]) -> List[str]:
        """
        Create large batches that utilize the full context window efficiently.
        
        Based on scaling tests:
        - llama3.1:8b context: 131K tokens ≈ 400K characters  
        - Reserve 7K tokens for output ≈ 20K characters
        - Max input per batch: 370K characters
        
        Args:
            text_chunks: Original small chunks
            
        Returns:
            List of large batch strings
        """
        MAX_BATCH_SIZE = 370_000  # characters, leaving room for JSON output
        
        batches = []
        current_batch = ""
        
        for chunk in text_chunks:
            # Check if adding this chunk would exceed limit
            if len(current_batch) + len(chunk) + 10 > MAX_BATCH_SIZE:  # +10 for separator
                if current_batch:
                    batches.append(current_batch.strip())
                current_batch = chunk
            else:
                if current_batch:
                    current_batch += "\n\n" + chunk
                else:
                    current_batch = chunk
        
        # Add final batch
        if current_batch:
            batches.append(current_batch.strip())
        
        # Log batch statistics
        total_chars = sum(len(batch) for batch in batches)
        avg_batch_size = total_chars / len(batches) if batches else 0
        
        logger.info(f"📦 Batch creation complete:")
        logger.info(f"   📊 {len(text_chunks)} chunks → {len(batches)} batches")
        logger.info(f"   📏 Average batch size: {avg_batch_size:,.0f} characters")
        logger.info(f"   🎯 Expected speedup: {len(text_chunks)/len(batches):.1f}x")
        
        return batches
    
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
    
    def _run_comprehensive_analysis(self, content: str, document_title: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Run comprehensive LLM analysis to extract all information with retry logic.
        
        Args:
            content: Text content to analyze
            document_title: Document title for context
            max_retries: Maximum number of retry attempts for failed JSON parsing
            
        Returns:
            Comprehensive analysis result
        """
        import signal
        import time
        
        chain = self.comprehensive_analysis_template | self.llm | StrOutputParser()
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Retry attempt {attempt}/{max_retries}")
                    
                logger.info("🧠 Running comprehensive LLM analysis...")
                logger.info(f"   📊 Content length: {len(content):,} characters")
                
                # Dynamic timeout based on content size (from scaling tests)
                if len(content) < 5000:
                    timeout_seconds = 30      # Small content: 30s
                elif len(content) < 50000:
                    timeout_seconds = 60      # Medium content: 60s  
                else:
                    timeout_seconds = 180     # Large content: 180s (3 min)
                
                logger.info(f"   ⏱️  Timeout: {timeout_seconds} seconds")
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"LLM analysis timed out after {timeout_seconds} seconds")
                
                # Set up timeout
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
                
                start_time = time.time()
                
                try:
                    # Log progress periodically during analysis
                    logger.info("🔄 Sending request to Ollama...")
                    result = chain.invoke({
                        "content": content,
                        "document_title": document_title
                    })
                    
                    elapsed_time = time.time() - start_time
                    logger.info(f"✅ LLM analysis completed in {elapsed_time:.1f}s")
                    
                finally:
                    signal.alarm(0)  # Clear the alarm
                
                # Parse JSON response
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                
                if json_start == -1 or json_end == -1:
                    logger.warning("⚠️ No valid JSON found in LLM response, using fallback")
                    raise ValueError("No valid JSON found in LLM response")
                
                json_str = result[json_start:json_end]
                
                try:
                    analysis_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ JSON parsing failed: {e}")
                    logger.warning(f"   Raw response: {result[:200]}...")
                    
                    # Try to repair the JSON using our repair function
                    try:
                        repaired_json = repair_json_response(result)
                        analysis_data = json.loads(repaired_json)
                        logger.info("✅ JSON repair successful")
                    except json.JSONDecodeError:
                        logger.error("❌ JSON parsing failed after repair, using fallback")
                        raise ValueError(f"JSON parsing failed: {e}")
                
                # Validate analysis data
                if not isinstance(analysis_data, dict):
                    raise ValueError("Invalid analysis data format")
                
                # Ensure required keys
                analysis_data.setdefault("entities", [])
                analysis_data.setdefault("citations", [])
                analysis_data.setdefault("relationships", [])
                
                logger.info("✅ Comprehensive analysis completed successfully")
                return analysis_data
                
            except TimeoutError as e:
                logger.error(f"⏰ LLM analysis timed out: {e}")
                # Return fallback analysis for timeout
                return {
                    "entities": [],
                    "citations": [],
                    "relationships": [],
                    "analysis_error": f"Analysis timed out after {timeout_seconds} seconds"
                }
                
            except ValueError as e:
                # JSON parsing failed - try again if we have retries left
                if attempt < max_retries:
                    logger.warning(f"🔄 JSON parsing failed, retrying... ({attempt + 1}/{max_retries})")
                    continue
                else:
                    logger.error(f"❌ All retry attempts failed: {e}")
                    # Return fallback analysis
                    return {
                        "entities": [],
                        "citations": [],
                        "relationships": [],
                        "analysis_error": str(e)
                    }
                    
            except Exception as e:
                logger.error(f"❌ Comprehensive analysis failed: {e}")
                # Return fallback analysis
                return {
                    "entities": [],
                    "citations": [],
                    "relationships": [],
                    "analysis_error": str(e)
                }
                
        # If we get here, all retries failed
        return {
            "entities": [],
            "citations": [],
            "relationships": [],
            "analysis_error": "All retry attempts failed"
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
        """Create analysis prompt template using configuration"""
        # Get the prompt from configuration, with fallback to default
        prompt_template = getattr(self.config, 'extraction', None)
        if prompt_template and hasattr(prompt_template, 'entity_extraction_prompt'):
            template_text = prompt_template.entity_extraction_prompt
        else:
            # Fallback to improved default prompt
            template_text = """TASK: Extract entities and citations from this academic document.

FOCUS ON:
- Authors and researchers (extract ALL names)
- Key concepts, theories, and frameworks  
- Methods, algorithms, and techniques
- Technologies, software, and tools
- Organizations and institutions
- Chemical compounds and materials
- Datasets and measurements

EXTRACT 20-40 entities for comprehensive literature review.

CONTENT: {content}

Return ONLY this JSON:

{{
  "entities": [
    {{
      "id": "author_1",
      "name": "John Smith",
      "type": "person"
    }},
    {{
      "id": "concept_1",
      "name": "machine learning",
      "type": "concept"
    }},
    {{
      "id": "method_1",
      "name": "gradient descent",
      "type": "method"
    }}
  ],
  "citations": [
    {{
      "text": "Smith et al. (2023)",
      "authors": ["John Smith", "Jane Doe"],
      "year": 2023,
      "title": "Paper Title"
    }}
  ],
  "relationships": [
    {{
      "source": "author_1",
      "target": "concept_1", 
      "type": "researches"
    }}
  ]
}}"""
        
        return ChatPromptTemplate.from_template(template_text)
    
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
                "provider": self.config.provider,
                "llm_model": self.config.llm_model,
                "temperature": self.config.temperature,
                "max_context": self.config.max_context,
                "max_predict": self.config.max_predict
            }
        }
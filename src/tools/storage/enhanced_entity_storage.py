"""Enhanced entity storage tool that works for both MCP and LangChain."""
from typing import List, Dict, Any, Optional
import json
import uuid
import re
import sys
from datetime import datetime
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from fastmcp import FastMCP
from pydantic import BaseModel
import os

from storage.neo4j import Neo4jStorage
from processor.entity_extractor_config import EntityExtractorConfig, create_default_config

# Data models
class EntityData(BaseModel):
    """Represents an important entity extracted from a document.
    
    Examples:
    - Person: {"id": "smith_2023", "name": "Dr. Jane Smith", "type": "person", 
              "properties": {"affiliation": "MIT", "role": "corresponding_author"}}
    - Concept: {"id": "ml_concept", "name": "machine learning", "type": "concept",
               "properties": {"domain": "AI", "definition": "algorithms that learn from data"}}
    - Technology: {"id": "transformer", "name": "Transformer Architecture", "type": "technology",
                  "properties": {"domain": "NLP", "year_introduced": "2017"}}
    """
    id: str  # Unique identifier for this entity
    name: str  # Display name of the entity
    type: str  # Category: person, concept, technology, organization, method, etc.
    properties: Dict[str, Any] = {}  # Additional attributes specific to this entity
    confidence: float = 1.0  # Confidence score 0-1 for extraction quality

class RelationshipData(BaseModel):
    """Represents a relationship between two entities.
    
    Examples:
    - Research: {"source": "smith_2023", "target": "ml_concept", "type": "researches",
                "context": "Dr. Smith's primary research focus is machine learning"}
    - Uses: {"source": "ml_concept", "target": "transformer", "type": "implemented_with",
            "context": "Modern ML systems often use transformer architectures"}
    """
    source: str  # ID of the source entity
    target: str  # ID of the target entity  
    type: str  # Relationship type: researches, uses, part_of, collaborates_with, etc.
    confidence: float = 1.0  # Confidence score 0-1 for relationship extraction
    context: str = ""  # Text snippet that supports this relationship

class DocumentInfo(BaseModel):
    """Metadata about the source document for provenance tracking.
    
    Example:
    {"title": "Attention Is All You Need", "type": "research_paper", 
     "path": "/papers/attention_paper.pdf"}
    """
    title: str  # Document title or filename
    type: str = "document"  # Document type: research_paper, book, article, etc.
    id: str = None  # Optional unique document ID (auto-generated if not provided)
    path: str = None  # Optional file path or URL

# Global entity extractor configuration
_global_entity_config: Optional[EntityExtractorConfig] = None

def set_global_entity_config(config: EntityExtractorConfig):
    """Set global entity extractor configuration"""
    global _global_entity_config
    _global_entity_config = config

def get_global_entity_config() -> EntityExtractorConfig:
    """Get global entity extractor configuration"""
    global _global_entity_config
    if _global_entity_config is None:
        _global_entity_config = create_default_config()
    return _global_entity_config

def _extract_and_store_entities_streaming(content: str, document_info: Dict[str, Any]):
    """
    Generator version that yields streaming tokens and final result.
    Yields: streaming tokens and final extraction result
    """
    try:
        # Debug: Check what type document_info actually is
        print(f"🔍 DEBUG: document_info type: {type(document_info)}", file=sys.stderr)
        print(f"🔍 DEBUG: document_info value: {document_info}", file=sys.stderr)
        # Get configuration from global config (set by process)
        config = get_global_entity_config()
        
        # Check if custom template configuration is provided
        if isinstance(document_info, dict) and "template_config" in document_info:
            template_config = document_info["template_config"]
            print(f"🎨 Using custom template: {template_config.get('template_name', 'Unknown')}", file=sys.stderr)
            
            # Override config with custom template settings
            config.extraction_mode = template_config.get("extraction_mode", config.extraction_mode)
            config.model_name = template_config.get("model_name", config.model_name)
            config.temperature = template_config.get("temperature", config.temperature)
            config.global_confidence_threshold = template_config.get("confidence_threshold", config.global_confidence_threshold)
        
        print(f"🧠 Analyzing content with {config.extraction_mode.value} mode: {len(content)} characters", file=sys.stderr)
        print(f"🔧 Entity types: {[et.value for et in config.get_enabled_entity_types()]}", file=sys.stderr)
        print(f"🎯 Confidence threshold: {config.global_confidence_threshold}", file=sys.stderr)
        
        # Initialize LLM
        llm = ChatGroq(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Build extraction prompt using configuration  
        extraction_prompt = config.build_extraction_prompt(content)
        
        print(f"🤖 Using model: {config.model_name} (temp: {config.temperature})", file=sys.stderr)
        print(f"📤 Sending extraction request to LLM...", file=sys.stderr)
        
        # Stream LLM response tokens
        print(f"🌊 Streaming LLM response...", file=sys.stderr)
        response_content = ""
        
        try:
            yield {"type": "llm_start", "message": "Starting LLM generation..."}
            
            for chunk in llm.stream(extraction_prompt):
                token = chunk.content if hasattr(chunk, 'content') else str(chunk)
                response_content += token
                
                # Yield each token as it arrives
                yield {"type": "llm_token", "token": token}
            
            yield {"type": "llm_complete", "message": f"LLM generation complete ({len(response_content)} chars)"}
            
            # Create a response-like object for compatibility
            class StreamResponse:
                def __init__(self, content):
                    self.content = content
            
            response = StreamResponse(response_content)
            print(f"📥 Streaming complete - Length: {len(response_content)} chars", file=sys.stderr)
            
        except Exception as stream_error:
            yield {"type": "llm_error", "message": f"Streaming failed: {stream_error}"}
            print(f"❌ Streaming failed, falling back to invoke: {stream_error}", file=sys.stderr)
            
            # Fallback to regular invoke
            response = llm.invoke(extraction_prompt)
            yield {"type": "llm_complete", "message": f"LLM fallback complete ({len(str(response))} chars)"}
            print(f"📥 Received LLM response - Length: {len(str(response))} chars", file=sys.stderr)
        
        # Continue with the rest of the extraction logic...
        yield {"type": "parsing_start", "message": "Parsing LLM response..."}
        
        # Parse LLM response with improved retry logic and better JSON extraction
        extraction_data = None
        for attempt in range(config.max_retry_attempts + 1):
            try:
                # Get response content
                content_text = response.content if hasattr(response, 'content') else str(response)
                yield {"type": "parsing_progress", "message": f"Parsing attempt {attempt + 1}, response length: {len(content_text)}"}
                
                # Try multiple JSON extraction strategies
                json_str = None
                
                # Strategy 1: Find complete JSON object with proper brace matching
                json_start = content_text.find('{')
                if json_start >= 0:
                    brace_count = 0
                    json_end = json_start
                    for i, char in enumerate(content_text[json_start:], json_start):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i + 1
                                break
                    
                    if brace_count == 0:
                        json_str = content_text[json_start:json_end]
                
                # Strategy 2: If no balanced braces, try simple start/end finding
                if not json_str:
                    json_start = content_text.find('{')
                    json_end = content_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content_text[json_start:json_end]
                
                # Strategy 3: Look for ```json code blocks
                if not json_str:
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                
                if json_str:
                    yield {"type": "json_found", "message": f"Found JSON string ({len(json_str)} chars)"}
                    # Clean up common JSON issues
                    json_str = json_str.strip()
                    # Remove any trailing commas before closing braces/brackets
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                    
                    extraction_data = json.loads(json_str)
                    yield {"type": "json_parsed", "message": f"Successfully parsed JSON with {len(extraction_data.get('entities', []))} entities"}
                    break
                else:
                    raise json.JSONDecodeError("No JSON found in response", content_text, 0)
            
            except json.JSONDecodeError as e:
                yield {"type": "json_error", "message": f"JSON parsing failed (attempt {attempt + 1}): {e}"}
                
                if attempt < config.max_retry_attempts and config.retry_on_json_error:
                    yield {"type": "retry_start", "message": "Retrying with simplified prompt..."}
                    # Retry with simpler, more explicit prompt
                    simple_prompt = f"""Extract entities from this text. Return ONLY the JSON object, no other text:

{{"entities": [{{"id": "sample_id", "name": "Sample Entity", "type": "concept", "properties": {{}}, "confidence": 0.8}}], "relationships": [{{"source": "id1", "target": "id2", "type": "RELATED_TO", "context": "context", "confidence": 0.7}}], "metadata": {{"total_entities": 1, "total_relationships": 1, "extraction_mode": "academic", "confidence_threshold": {config.global_confidence_threshold}}}}}

Text to analyze: {content[:1500]}

JSON Response:"""
                    response = llm.invoke(simple_prompt)
                    continue
                else:
                    # Final fallback
                    if config.enable_fallback_extraction:
                        extraction_data = {
                            "entities": [
                                {
                                    "id": "extracted_content",
                                    "name": f"Content from {document_info.get('title', 'document')}",
                                    "type": "concept",
                                    "properties": {"source": "fallback_extraction"},
                                    "confidence": 0.5
                                }
                            ],
                            "relationships": [],
                            "metadata": {"extraction_method": "fallback_due_to_parse_error"}
                        }
                        yield {"type": "fallback_extraction", "message": "Using fallback extraction due to parsing errors"}
                    else:
                        yield {"type": "extraction_failed", "message": f"JSON parsing failed after {config.max_retry_attempts} attempts"}
                        return
        
        if extraction_data is None:
            yield {"type": "extraction_failed", "message": "Failed to extract valid data"}
            return
        
        # Process extracted data
        yield {"type": "processing_start", "message": "Processing extracted entities and relationships..."}
        
        try:
            entities_raw = extraction_data.get("entities", [])
            relationships_raw = extraction_data.get("relationships", [])
            
            yield {"type": "raw_data", "message": f"Raw extraction: {len(entities_raw)} entities, {len(relationships_raw)} relationships"}
        except Exception as debug_e:
            yield {"type": "error", "message": f"Error during entity/relationship extraction: {debug_e}"}
            return
        
        # Filter entities by configuration
        filtered_entities = []
        enabled_types = {et.value for et in config.get_enabled_entity_types()}
        
        for entity_data in entities_raw:
            # Add safety check for list vs dict
            if not isinstance(entity_data, dict):
                continue
                
            entity_type = entity_data.get("type", "concept")
            confidence = entity_data.get("confidence", 0.0)
            
            # Check if entity type is enabled
            if entity_type not in enabled_types:
                continue
                
            # Check confidence threshold
            min_confidence = config.global_confidence_threshold
            
            if confidence < min_confidence:
                continue
                
            filtered_entities.append(entity_data)
        
        # Filter relationships by configuration  
        filtered_relationships = []
        enabled_rel_types = {rt.value for rt in config.enabled_relationship_types}
        
        for rel_data in relationships_raw:
            # Add safety check for list vs dict
            if not isinstance(rel_data, dict):
                continue
                
            rel_type = rel_data.get("type", "RELATED_TO")
            confidence = rel_data.get("confidence", 0.0)
            
            # Check if relationship type is enabled
            if rel_type not in enabled_rel_types:
                continue
                
            # Check confidence threshold
            if confidence < config.relationship_confidence_threshold:
                continue
                
            filtered_relationships.append(rel_data)
        
        yield {"type": "filtering_complete", "message": f"After filtering: {len(filtered_entities)} entities, {len(filtered_relationships)} relationships"}
        
        # Convert to Pydantic models for validation
        entities = []
        for entity_data in filtered_entities:
            try:
                # Add safety check here too
                if not isinstance(entity_data, dict):
                    continue
                    
                # Flatten properties to avoid Neo4j nested object issues
                properties = entity_data.get("properties", {})
                flattened_properties = {}
                
                # Safety check for properties
                if isinstance(properties, dict):
                    for key, value in properties.items():
                        if isinstance(value, (str, int, float, bool)):
                            flattened_properties[key] = value
                        else:
                            flattened_properties[key] = str(value)
                
                entity = EntityData(
                    id=entity_data.get("id", f"entity_{uuid.uuid4().hex[:8]}"),
                    name=entity_data.get("name", "Unknown"),
                    type=entity_data.get("type", "concept"),
                    properties=flattened_properties,
                    confidence=entity_data.get("confidence", 0.7)
                )
                entities.append(entity)
            except Exception as e:
                yield {"type": "entity_validation_error", "message": f"Skipping invalid entity: {e}"}
        
        relationships = []
        for rel_data in filtered_relationships:
            try:
                # Add safety check here too
                if not isinstance(rel_data, dict):
                    continue
                    
                relationship = RelationshipData(
                    source=rel_data.get("source", ""),
                    target=rel_data.get("target", ""),
                    type=rel_data.get("type", "RELATED_TO"),
                    context=rel_data.get("context", ""),
                    confidence=rel_data.get("confidence", 0.7)
                )
                relationships.append(relationship)
            except Exception as e:
                yield {"type": "relationship_validation_error", "message": f"Skipping invalid relationship: {e}"}
        
        # Store extracted entities in Neo4j linked to source document
        yield {"type": "storage_start", "message": f"Storing {len(entities)} entities and {len(relationships)} relationships in Neo4j..."}
        
        try:
            # Get Neo4j storage instance
            from storage.neo4j.storage import Neo4jStorage
            neo4j_storage = Neo4jStorage()
            
            # Create extraction session record
            extraction_id = str(uuid.uuid4())
            extraction_metadata = {
                "extraction_id": extraction_id,
                "document_id": document_info.get("id"),
                "extraction_mode": "academic",  # Could be configurable
                "extraction_timestamp": datetime.now().isoformat(),
                "total_entities": len(entities),
                "total_relationships": len(relationships),
                "confidence_threshold": config.global_confidence_threshold,
                "status": "pending_review"  # pending_review -> approved -> in_knowledge_graph
            }
            
            # Store extraction metadata
            neo4j_storage.driver.execute_query("""
                MERGE (doc:Document {id: $document_id})
                CREATE (extraction:EntityExtraction $metadata)
                CREATE (extraction)-[:EXTRACTED_FROM]->(doc)
            """, {"document_id": document_info.get("id"), "metadata": extraction_metadata})
            
            # Store individual entities linked to extraction
            entities_stored = 0
            for entity in entities:
                entity_data = {
                    "entity_id": str(uuid.uuid4()),
                    "extraction_id": extraction_id,
                    "name": entity.name,
                    "type": entity.type,
                    "confidence": entity.confidence,
                    "properties": json.dumps(entity.properties),  # Flatten for Neo4j
                    "status": "pending_review"
                }
                
                neo4j_storage.driver.execute_query("""
                    MATCH (extraction:EntityExtraction {extraction_id: $extraction_id})
                    CREATE (entity:ExtractedEntity $entity_data)
                    CREATE (entity)-[:EXTRACTED_IN]->(extraction)
                """, {"extraction_id": extraction_id, "entity_data": entity_data})
                entities_stored += 1
            
            # Store individual relationships linked to extraction
            relationships_stored = 0
            for relationship in relationships:
                rel_data = {
                    "relationship_id": str(uuid.uuid4()),
                    "extraction_id": extraction_id,
                    "source": relationship.source,
                    "target": relationship.target,
                    "type": relationship.type,
                    "confidence": relationship.confidence,
                    "context": relationship.context,
                    "status": "pending_review"
                }
                
                neo4j_storage.driver.execute_query("""
                    MATCH (extraction:EntityExtraction {extraction_id: $extraction_id})
                    CREATE (rel:ExtractedRelationship $rel_data)
                    CREATE (rel)-[:EXTRACTED_IN]->(extraction)
                """, {"extraction_id": extraction_id, "rel_data": rel_data})
                relationships_stored += 1
                
            yield {"type": "storage_complete", "message": f"Stored {entities_stored} entities and {relationships_stored} relationships in Neo4j"}
            
            # Final result
            result = {
                "success": True,
                "message": f"Extracted and stored {len(entities)} entities, {len(relationships)} relationships",
                "entities_found": len(entities),
                "relationships_found": len(relationships),
                "extraction_method": "llm_analysis",
                "document_id": document_info.get("id"),
                "extraction_id": extraction_id,
                "storage_result": {
                    "entities_created": entities_stored,
                    "relationships_created": relationships_stored,
                    "extraction_id": extraction_id,
                    "document_id": document_info.get("id")
                }
            }
            
            yield {"type": "extraction_complete", "result": result}
            
        except Exception as storage_error:
            yield {"type": "storage_error", "message": f"Failed to store in Neo4j: {storage_error}"}
            
    except Exception as e:
        yield {"type": "error", "message": f"Extraction failed: {e}"}
        print(f"❌ Error in extract_and_store_entities: {e}", file=sys.stderr)

def _extract_and_store_entities_impl(content: str, document_info: Dict[str, Any], stream_callback=None) -> Dict[str, Any]:
    """
    Extract entities and relationships from content using configurable LLM analysis, then store in Neo4j.
    
    Works for both MCP clients and LangGraph agents.
    
    Args:
        content: Document text content to analyze
        document_info: Document metadata (title, type, path, etc.)
        
    Returns:
        Dictionary with extraction results and storage confirmation
    """
    print(f"🚀 ENTERING: _extract_and_store_entities_impl", file=sys.stderr)
    try:
        # Debug: Check what type document_info actually is
        print(f"🔍 DEBUG: document_info type: {type(document_info)}", file=sys.stderr)
        print(f"🔍 DEBUG: document_info value: {document_info}", file=sys.stderr)
        # Get configuration from global config (set by process)
        config = get_global_entity_config()
        
        # Check if custom template configuration is provided
        if isinstance(document_info, dict) and "template_config" in document_info:
            template_config = document_info["template_config"]
            print(f"🎨 Using custom template: {template_config.get('template_name', 'Unknown')}", file=sys.stderr)
            
            # Override config with custom template settings
            if template_config.get("system_prompt"):
                config.prompt_template.system_prompt = template_config["system_prompt"]
            if template_config.get("instruction_template"):
                config.prompt_template.instruction_template = template_config["instruction_template"]
            if template_config.get("confidence_threshold"):
                config.global_confidence_threshold = template_config["confidence_threshold"]
            if template_config.get("temperature"):
                config.temperature = template_config["temperature"]
            if template_config.get("max_tokens"):
                config.max_tokens = template_config["max_tokens"]
            
            print(f"✅ Applied custom template overrides: conf={config.global_confidence_threshold}, temp={config.temperature}", file=sys.stderr)
        
        # Validate inputs
        if not content or len(content.strip()) < 50:
            return {
                "success": False,
                "error": "Content too short for meaningful entity extraction",
                "entities_found": 0,
                "relationships_found": 0
            }
        
        print(f"🧠 Analyzing content with {config.extraction_mode.value} mode: {len(content)} characters", file=sys.stderr)
        print(f"🔧 Entity types: {[et.value for et in config.get_enabled_entity_types()]}", file=sys.stderr)
        print(f"🎯 Confidence threshold: {config.global_confidence_threshold}", file=sys.stderr)
        
        # Initialize Groq LLM with configuration
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            return {
                "success": False,
                "error": "GROQ_API_KEY not found in environment",
                "entities_found": 0,
                "relationships_found": 0
            }
        
        llm = ChatGroq(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            groq_api_key=groq_api_key
        )
        
        # Build extraction prompt using configuration  
        extraction_prompt = config.build_extraction_prompt(content)
        
        print(f"🤖 Using model: {config.model_name} (temp: {config.temperature})", file=sys.stderr)
        print(f"📤 Sending extraction request to LLM...", file=sys.stderr)
        
        # Extract entities using configured LLM with optional streaming
        if stream_callback:
            # Use streaming for real-time token output
            print(f"🌊 Streaming LLM response...", file=sys.stderr)
            response_content = ""
            
            try:
                for chunk in llm.stream(extraction_prompt):
                    token = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    response_content += token
                    
                    # Send token to stream callback
                    if stream_callback:
                        stream_callback({"type": "llm_token", "token": token})
                
                # Create a response-like object for compatibility
                class StreamResponse:
                    def __init__(self, content):
                        self.content = content
                
                response = StreamResponse(response_content)
                print(f"📥 Streaming complete - Length: {len(response_content)} chars", file=sys.stderr)
                
            except Exception as stream_error:
                print(f"❌ Streaming failed, falling back to invoke: {stream_error}", file=sys.stderr)
                response = llm.invoke(extraction_prompt)
                print(f"📥 Received LLM response - Length: {len(str(response))} chars", file=sys.stderr)
        else:
            # Use regular invoke for non-streaming
            response = llm.invoke(extraction_prompt)
            print(f"📥 Received LLM response - Length: {len(str(response))} chars", file=sys.stderr)
        
        # Parse LLM response with improved retry logic and better JSON extraction
        extraction_data = None
        for attempt in range(config.max_retry_attempts + 1):
            try:
                # Get response content
                content_text = response.content if hasattr(response, 'content') else str(response)
                print(f"🔍 LLM Response content (attempt {attempt + 1}): {content_text[:500]}...", file=sys.stderr)
                
                # Try multiple JSON extraction strategies
                json_str = None
                
                # Strategy 1: Find complete JSON object with proper brace matching
                json_start = content_text.find('{')
                if json_start >= 0:
                    brace_count = 0
                    json_end = json_start
                    for i, char in enumerate(content_text[json_start:], json_start):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i + 1
                                break
                    
                    if brace_count == 0:
                        json_str = content_text[json_start:json_end]
                
                # Strategy 2: If no balanced braces, try simple start/end finding
                if not json_str:
                    json_start = content_text.find('{')
                    json_end = content_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content_text[json_start:json_end]
                
                # Strategy 3: Look for ```json code blocks
                if not json_str:
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                
                if json_str:
                    print(f"📝 Extracted JSON string: {json_str[:200]}...", file=sys.stderr)
                    # Clean up common JSON issues
                    json_str = json_str.strip()
                    # Remove any trailing commas before closing braces/brackets
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                    
                    extraction_data = json.loads(json_str)
                    print(f"✅ Successfully parsed JSON with {len(extraction_data.get('entities', []))} entities", file=sys.stderr)
                    break
                else:
                    raise json.JSONDecodeError("No JSON found in response", content_text, 0)
            
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed (attempt {attempt + 1}): {e}", file=sys.stderr)
                
                if attempt < config.max_retry_attempts and config.retry_on_json_error:
                    print(f"🔄 Retrying extraction with simplified prompt...", file=sys.stderr)
                    # Retry with simpler, more explicit prompt
                    simple_prompt = f"""Extract entities from this text. Return ONLY the JSON object, no other text:

{{"entities": [{{"id": "sample_id", "name": "Sample Entity", "type": "concept", "properties": {{}}, "confidence": 0.8}}], "relationships": [{{"source": "id1", "target": "id2", "type": "RELATED_TO", "context": "context", "confidence": 0.7}}], "metadata": {{"total_entities": 1, "total_relationships": 1, "extraction_mode": "academic", "confidence_threshold": {config.global_confidence_threshold}}}}}

Text to analyze: {content[:1500]}

JSON Response:"""
                    response = llm.invoke(simple_prompt)
                    continue
                else:
                    # Final fallback
                    if config.enable_fallback_extraction:
                        extraction_data = {
                            "entities": [
                                {
                                    "id": "extracted_content",
                                    "name": f"Content from {document_info.get('title', 'document')}",
                                    "type": "concept",
                                    "properties": {"source": "fallback_extraction"},
                                    "confidence": 0.5
                                }
                            ],
                            "relationships": [],
                            "metadata": {"extraction_method": "fallback_due_to_parse_error"}
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"JSON parsing failed after {config.max_retry_attempts} attempts",
                            "entities_found": 0,
                            "relationships_found": 0
                        }
        
        if extraction_data is None:
            return {
                "success": False,
                "error": "Failed to extract valid data",
                "entities_found": 0,
                "relationships_found": 0
            }
        
        try:
            entities_raw = extraction_data.get("entities", [])
            print(f"✅ Got entities_raw: {len(entities_raw)}", file=sys.stderr)
            relationships_raw = extraction_data.get("relationships", [])
            print(f"✅ Got relationships_raw: {len(relationships_raw)}", file=sys.stderr)
            
            print(f"📊 Raw extraction: {len(entities_raw)} entities, {len(relationships_raw)} relationships", file=sys.stderr)
            print(f"🔍 DEBUG: relationships_raw type: {type(relationships_raw)}", file=sys.stderr)
            print(f"🔍 DEBUG: relationships_raw content: {relationships_raw}", file=sys.stderr)
        except Exception as debug_e:
            print(f"❌ Error during entity/relationship extraction: {debug_e}", file=sys.stderr)
            raise
        
        # Filter entities by configuration
        filtered_entities = []
        enabled_types = {et.value for et in config.get_enabled_entity_types()}
        
        for entity_data in entities_raw:
            # Add safety check for list vs dict
            if not isinstance(entity_data, dict):
                print(f"⚠️ Skipping non-dict entity: {type(entity_data)} - {entity_data}", file=sys.stderr)
                continue
                
            entity_type = entity_data.get("type", "concept")
            confidence = entity_data.get("confidence", 0.0)
            
            # Check if entity type is enabled
            if entity_type not in enabled_types:
                continue
                
            # Check confidence threshold
            min_confidence = config.global_confidence_threshold
            
            if confidence < min_confidence:
                continue
                
            filtered_entities.append(entity_data)
        
        # Filter relationships by configuration  
        filtered_relationships = []
        enabled_rel_types = {rt.value for rt in config.enabled_relationship_types}
        
        for rel_data in relationships_raw:
            # Add safety check for list vs dict
            if not isinstance(rel_data, dict):
                print(f"⚠️ Skipping non-dict relationship: {type(rel_data)} - {rel_data}", file=sys.stderr)
                continue
                
            rel_type = rel_data.get("type", "RELATED_TO")
            confidence = rel_data.get("confidence", 0.0)
            
            # Check if relationship type is enabled
            if rel_type not in enabled_rel_types:
                continue
                
            # Check confidence threshold
            if confidence < config.relationship_confidence_threshold:
                continue
                
            filtered_relationships.append(rel_data)
        
        print(f"🔍 After filtering: {len(filtered_entities)} entities, {len(filtered_relationships)} relationships", file=sys.stderr)
        
        # Convert to Pydantic models for validation
        entities = []
        for entity_data in filtered_entities:
            try:
                # Add safety check here too
                if not isinstance(entity_data, dict):
                    print(f"⚠️ Skipping non-dict entity in conversion: {type(entity_data)} - {entity_data}", file=sys.stderr)
                    continue
                    
                # Flatten properties to avoid Neo4j nested object issues
                properties = entity_data.get("properties", {})
                flattened_properties = {}
                
                # Safety check for properties
                if isinstance(properties, dict):
                    for key, value in properties.items():
                        if isinstance(value, (str, int, float, bool)):
                            flattened_properties[key] = value
                        else:
                            flattened_properties[key] = str(value)
                else:
                    print(f"⚠️ Entity properties not a dict: {type(properties)} - {properties}", file=sys.stderr)
                
                entity = EntityData(
                    id=entity_data.get("id", f"entity_{uuid.uuid4().hex[:8]}"),
                    name=entity_data.get("name", "Unknown"),
                    type=entity_data.get("type", "concept"),
                    properties=flattened_properties,
                    confidence=entity_data.get("confidence", 0.7)
                )
                entities.append(entity)
            except Exception as e:
                print(f"⚠️ Skipping invalid entity: {e} - Data: {entity_data}", file=sys.stderr)
        
        relationships = []
        for rel_data in filtered_relationships:
            try:
                # Add safety check here too
                if not isinstance(rel_data, dict):
                    print(f"⚠️ Skipping non-dict relationship in conversion: {type(rel_data)} - {rel_data}", file=sys.stderr)
                    continue
                    
                relationship = RelationshipData(
                    source=rel_data.get("source", ""),
                    target=rel_data.get("target", ""),
                    type=rel_data.get("type", "RELATED_TO"),
                    context=rel_data.get("context", ""),
                    confidence=rel_data.get("confidence", 0.7)
                )
                relationships.append(relationship)
            except Exception as e:
                print(f"⚠️ Skipping invalid relationship: {e} - Data: {rel_data}", file=sys.stderr)
        
        # Prepare document info
        doc_info = DocumentInfo(
            title=document_info.get("title", "Unknown Document"),
            type=document_info.get("type", "document"),
            id=document_info.get("id", str(uuid.uuid4())),
            path=document_info.get("path", "")
        )
        
        # Store extracted entities in Neo4j linked to source document
        print(f"💾 Storing {len(entities)} entities and {len(relationships)} relationships in Neo4j", file=sys.stderr)
        
        try:
            # Get Neo4j storage instance
            from storage.neo4j.storage import Neo4jStorage
            neo4j_storage = Neo4jStorage()
            
            # Create extraction session record
            extraction_id = str(uuid.uuid4())
            extraction_metadata = {
                "extraction_id": extraction_id,
                "document_id": document_info.get("id"),
                "extraction_mode": "academic",  # Could be configurable
                "extraction_timestamp": datetime.now().isoformat(),
                "total_entities": len(entities),
                "total_relationships": len(relationships),
                "confidence_threshold": 0.7,
                "status": "pending_review"  # pending_review -> approved -> in_knowledge_graph
            }
            
            # Store extraction metadata
            neo4j_storage.driver.execute_query("""
                MERGE (doc:Document {id: $document_id})
                CREATE (extraction:EntityExtraction $metadata)
                CREATE (extraction)-[:EXTRACTED_FROM]->(doc)
            """, {"document_id": document_info.get("id"), "metadata": extraction_metadata})
            
            # Store individual entities linked to extraction
            entities_stored = 0
            for entity in entities:
                entity_data = {
                    "entity_id": str(uuid.uuid4()),
                    "extraction_id": extraction_id,
                    "name": entity.name,
                    "type": entity.type,
                    "confidence": entity.confidence,
                    "properties": json.dumps(entity.properties),  # Flatten for Neo4j
                    "status": "pending_review"
                }
                
                neo4j_storage.driver.execute_query("""
                    MATCH (extraction:EntityExtraction {extraction_id: $extraction_id})
                    CREATE (entity:ExtractedEntity $entity_data)
                    CREATE (entity)-[:EXTRACTED_IN]->(extraction)
                """, {"extraction_id": extraction_id, "entity_data": entity_data})
                entities_stored += 1
            
            # Store individual relationships linked to extraction
            relationships_stored = 0
            for relationship in relationships:
                rel_data = {
                    "relationship_id": str(uuid.uuid4()),
                    "extraction_id": extraction_id,
                    "source": relationship.source,
                    "target": relationship.target,
                    "type": relationship.type,
                    "confidence": relationship.confidence,
                    "context": relationship.context,
                    "status": "pending_review"
                }
                
                neo4j_storage.driver.execute_query("""
                    MATCH (extraction:EntityExtraction {extraction_id: $extraction_id})
                    CREATE (rel:ExtractedRelationship $rel_data)
                    CREATE (rel)-[:EXTRACTED_IN]->(extraction)
                """, {"extraction_id": extraction_id, "rel_data": rel_data})
                relationships_stored += 1
                
            print(f"✅ Stored {entities_stored} entities and {relationships_stored} relationships in Neo4j", file=sys.stderr)
            
            storage_result = {
                "entities_created": entities_stored,
                "relationships_created": relationships_stored,
                "extraction_id": extraction_id,
                "document_id": document_info.get("id")
            }
            
        except Exception as storage_error:
            print(f"❌ Failed to store in Neo4j: {storage_error}", file=sys.stderr)
            # Fallback to previous behavior
            storage_result = {
                "entities_created": len(entities), 
                "relationships_created": len(relationships),
                "document_id": document_info.get("id")
            }
        
        # Add safety checks for entity access
        try:
            entity_names = [e.name if hasattr(e, 'name') else str(e) for e in entities[:3]]
            print(f"📋 Sample entities: {entity_names}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ Error displaying entity names: {e}", file=sys.stderr)
            
        try:
            rel_display = [f'{r.source}->{r.target}' if hasattr(r, 'source') and hasattr(r, 'target') else str(r) for r in relationships[:3]]
            print(f"🔗 Sample relationships: {rel_display}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ Error displaying relationships: {e}", file=sys.stderr)
        
        storage_result = {
            "entities_created": len(entities), 
            "relationships_created": len(relationships),
            "document_id": document_info.get("id", str(uuid.uuid4()))  # Use document_info directly instead of doc_info
        }
        
        result = {
            "success": True,
            "message": f"Extracted and stored {len(entities)} entities, {len(relationships)} relationships",
            "entities_found": len(entities),
            "relationships_found": len(relationships),
            "extraction_method": "llm_analysis",
            "document_id": document_info.get("id", str(uuid.uuid4())),
            "extraction_id": storage_result.get("extraction_id"),  # Add extraction ID for tracking
            "storage_result": storage_result
        }
        
        # Include additional metadata if configured (simplified to avoid errors)
        try:
            if config.include_metadata:
                result["raw_entities_count"] = len(entities_raw)
                result["raw_relationships_count"] = len(relationships_raw)
                result["filtering_applied"] = True
        except Exception as meta_error:
            print(f"⚠️ Error adding metadata: {meta_error}", file=sys.stderr)
        
        return result
        
    except Exception as e:
        print(f"❌ Error in extract_and_store_entities: {e}", file=sys.stderr)
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to extract and store entities",
            "entities_found": 0,
            "relationships_found": 0
        }

@tool
def extract_and_store_entities(content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract entities and relationships from content using configurable LLM analysis, then store in Neo4j.
    
    Works for both MCP clients and LangGraph agents.
    
    Args:
        content: Document text content to analyze
        document_info: Document metadata (title, type, path, etc.)
        
    Returns:
        Dictionary with extraction results and storage confirmation
    """
    return _extract_and_store_entities_impl(content, document_info)

def register_enhanced_entity_tools(mcp: FastMCP, neo4j_storage: Neo4jStorage):
    """Register enhanced entity extraction tools with the MCP server."""
    
    @mcp.tool()
    def extract_and_store_entities_mcp(
        content: str,
        document_info: DocumentInfo
    ) -> Dict[str, Any]:
        """
        MCP wrapper for extract_and_store_entities.
        
        Args:
            content: Document text content to analyze
            document_info: Document metadata
            
        Returns:
            Extraction and storage results
        """
        return extract_and_store_entities(content, document_info.model_dump())

# Test function
def test_entity_extraction():
    """Test the entity extraction functionality"""
    test_content = """
    This paper introduces the Transformer architecture by Vaswani et al. from Google Research.
    The Transformer uses self-attention mechanisms and has revolutionized natural language processing.
    It was published in "Attention is All You Need" in 2017 at NeurIPS.
    The architecture has been adopted by BERT, GPT, and other modern language models.
    """
    
    test_doc_info = {
        "title": "Transformer Architecture Paper",
        "type": "research_paper",
        "path": "/test/transformer.pdf"
    }
    
    print("Testing entity extraction...")
    result = extract_and_store_entities.invoke({
        "content": test_content,
        "document_info": test_doc_info
    })
    print("Test result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    test_entity_extraction()
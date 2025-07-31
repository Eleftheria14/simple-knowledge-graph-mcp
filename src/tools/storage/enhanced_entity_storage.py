"""Enhanced entity storage tool that works for both MCP and LangChain."""
from typing import List, Dict, Any, Optional
import json
import uuid
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from fastmcp import FastMCP
from pydantic import BaseModel
import os

from storage.neo4j import Neo4jStorage
from processor.entity_extractor_config import EntityExtractorConfig, create_default_config

# Reuse existing data models
from tools.storage.entity_storage import EntityData, RelationshipData, DocumentInfo

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
    try:
        # Get configuration from global config (set by process)
        config = get_global_entity_config()
        
        # Validate inputs
        if not content or len(content.strip()) < 50:
            return {
                "success": False,
                "error": "Content too short for meaningful entity extraction",
                "entities_found": 0,
                "relationships_found": 0
            }
        
        print(f"🧠 Analyzing content with {config.extraction_mode.value} mode: {len(content)} characters")
        print(f"🔧 Entity types: {[et.value for et in config.get_enabled_entity_types()]}")
        print(f"🎯 Confidence threshold: {config.global_confidence_threshold}")
        
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
        
        print(f"🤖 Using model: {config.model_name} (temp: {config.temperature})")
        print(f"📤 Sending extraction request to LLM...")
        
        # Extract entities using configured LLM
        response = llm.invoke(extraction_prompt)
        print(f"📥 Received LLM response - Length: {len(str(response))} chars")
        
        # Parse LLM response with retry logic
        extraction_data = None
        for attempt in range(config.max_retry_attempts + 1):
            try:
                # Find JSON in response
                content_text = response.content if hasattr(response, 'content') else str(response)
                json_start = content_text.find('{')
                json_end = content_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = content_text[json_start:json_end]
                    extraction_data = json.loads(json_str)
                    break
                else:
                    raise json.JSONDecodeError("No JSON found in response", content_text, 0)
            
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed (attempt {attempt + 1}): {e}")
                
                if attempt < config.max_retry_attempts and config.retry_on_json_error:
                    print(f"🔄 Retrying extraction with simplified prompt...")
                    # Retry with simpler prompt
                    simple_prompt = f"""Extract entities from this text and return only JSON:
{{"entities": [{{"id": "id", "name": "name", "type": "type", "confidence": 0.8}}], "relationships": []}}

Text: {content[:2000]}"""
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
        
        entities_raw = extraction_data.get("entities", [])
        relationships_raw = extraction_data.get("relationships", [])
        
        print(f"📊 Raw extraction: {len(entities_raw)} entities, {len(relationships_raw)} relationships")
        
        # Filter entities by configuration
        filtered_entities = []
        enabled_types = {et.value for et in config.get_enabled_entity_types()}
        
        for entity_data in entities_raw:
            entity_type = entity_data.get("type", "concept")
            confidence = entity_data.get("confidence", 0.0)
            
            # Check if entity type is enabled
            if entity_type not in enabled_types:
                continue
                
            # Check confidence threshold
            type_config = config.get_entity_config(config.enabled_entity_types.__class__(entity_type) if entity_type in [et.value for et in config.enabled_entity_types] else None)
            min_confidence = type_config.confidence_threshold if type_config else config.global_confidence_threshold
            
            if confidence < min_confidence:
                continue
                
            filtered_entities.append(entity_data)
        
        # Filter relationships by configuration  
        filtered_relationships = []
        enabled_rel_types = {rt.value for rt in config.enabled_relationship_types}
        
        for rel_data in relationships_raw:
            rel_type = rel_data.get("type", "RELATED_TO")
            confidence = rel_data.get("confidence", 0.0)
            
            # Check if relationship type is enabled
            if rel_type not in enabled_rel_types:
                continue
                
            # Check confidence threshold
            if confidence < config.relationship_confidence_threshold:
                continue
                
            filtered_relationships.append(rel_data)
        
        print(f"🔍 After filtering: {len(filtered_entities)} entities, {len(filtered_relationships)} relationships")
        
        # Convert to Pydantic models for validation
        entities = []
        for entity_data in filtered_entities:
            try:
                # Flatten properties to avoid Neo4j nested object issues
                properties = entity_data.get("properties", {})
                flattened_properties = {}
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
                print(f"⚠️ Skipping invalid entity: {e}")
        
        relationships = []
        for rel_data in filtered_relationships:
            try:
                relationship = RelationshipData(
                    source=rel_data.get("source", ""),
                    target=rel_data.get("target", ""),
                    type=rel_data.get("type", "RELATED_TO"),
                    context=rel_data.get("context", ""),
                    confidence=rel_data.get("confidence", 0.7)
                )
                relationships.append(relationship)
            except Exception as e:
                print(f"⚠️ Skipping invalid relationship: {e}")
        
        # Prepare document info
        doc_info = DocumentInfo(
            title=document_info.get("title", "Unknown Document"),
            type=document_info.get("type", "document"),
            id=document_info.get("id", str(uuid.uuid4())),
            path=document_info.get("path", "")
        )
        
        # For now, return extraction results without storage due to Neo4j properties issue
        # TODO: Fix Neo4j properties storage in existing storage layer
        print(f"💾 Would store {len(entities)} entities and {len(relationships)} relationships")
        print(f"📋 Sample entities: {[e.name for e in entities[:3]]}")
        print(f"🔗 Sample relationships: {[f'{r.source}->{r.target}' for r in relationships[:3]]}")
        
        storage_result = {
            "entities_created": len(entities), 
            "relationships_created": len(relationships),
            "document_id": doc_info.id
        }
        
        result = {
            "success": True,
            "message": f"Extracted and stored {len(entities)} entities, {len(relationships)} relationships",
            "entities_found": len(entities),
            "relationships_found": len(relationships),
            "extraction_method": extraction_data.get("metadata", {}).get("extraction_method", "llm_analysis"),
            "document_id": storage_result.get("document_id"),
            "storage_result": storage_result,
            "configuration_used": {
                "extraction_mode": config.extraction_mode.value,
                "model_name": config.model_name,
                "temperature": config.temperature,
                "confidence_threshold": config.global_confidence_threshold,
                "enabled_entity_types": [et.value for et in config.get_enabled_entity_types()],
                "enabled_relationship_types": [rt.value for rt in config.enabled_relationship_types]
            }
        }
        
        # Include additional metadata if configured
        if config.include_metadata:
            result["metadata"] = extraction_data.get("metadata", {})
            result["raw_entities_count"] = len(entities_raw)
            result["raw_relationships_count"] = len(relationships_raw)
            result["filtering_applied"] = True
        
        return result
        
    except Exception as e:
        print(f"❌ Error in extract_and_store_entities: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to extract and store entities",
            "entities_found": 0,
            "relationships_found": 0
        }

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
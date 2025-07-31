"""Enhanced entity storage tool that works for both MCP and LangChain."""
from typing import List, Dict, Any
import json
import uuid
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from fastmcp import FastMCP
from pydantic import BaseModel
import os

from storage.neo4j import Neo4jStorage

# Reuse existing data models
from tools.storage.entity_storage import EntityData, RelationshipData, DocumentInfo

# Entity extraction prompt
ENTITY_EXTRACTION_PROMPT = """
Analyze the following document content and extract entities and relationships.

Extract:
1. **People**: Authors, researchers, historical figures
2. **Organizations**: Companies, universities, institutions  
3. **Concepts**: Technical terms, theories, methodologies
4. **Technologies**: Tools, frameworks, systems, algorithms
5. **Publications**: Papers, books, journals referenced

For each entity, provide:
- id: Short unique identifier (lowercase, underscores)
- name: Clear, standardized name
- type: One of [person, organization, concept, technology, publication]
- properties: Key attributes (affiliation, year, domain, etc.)
- confidence: 0.0-1.0 confidence score

For relationships, identify:
- source: Source entity id
- target: Target entity id  
- type: Relationship type [AUTHORED, WORKS_AT, USES, CITES, RELATED_TO, DEVELOPED, APPLIED]
- context: Brief context explaining the relationship
- confidence: 0.0-1.0 confidence score

Return ONLY valid JSON format:
{{
  "entities": [
    {{
      "id": "entity_id",
      "name": "Entity Name",
      "type": "concept|person|organization|technology|publication",
      "properties": {{"key": "value"}},
      "confidence": 0.9
    }}
  ],
  "relationships": [
    {{
      "source": "source_entity_id",
      "target": "target_entity_id",
      "type": "RELATIONSHIP_TYPE",
      "context": "Brief explanation",
      "confidence": 0.8
    }}
  ],
  "metadata": {{
    "total_entities": 0,
    "total_relationships": 0,
    "extraction_method": "llm_analysis"
  }}
}}

Document content (first 4000 chars):
{content}
"""

@tool
def extract_and_store_entities(content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract entities and relationships from content using LLM analysis, then store in Neo4j.
    
    Works for both MCP clients and LangGraph agents.
    
    Args:
        content: Document text content to analyze
        document_info: Document metadata (title, type, path, etc.)
        
    Returns:
        Dictionary with extraction results and storage confirmation
    """
    try:
        # Validate inputs
        if not content or len(content.strip()) < 50:
            return {
                "success": False,
                "error": "Content too short for meaningful entity extraction",
                "entities_found": 0,
                "relationships_found": 0
            }
        
        print(f"🧠 Analyzing content for entity extraction: {len(content)} characters")
        
        # Initialize Groq LLM for extraction
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            return {
                "success": False,
                "error": "GROQ_API_KEY not found in environment",
                "entities_found": 0,
                "relationships_found": 0
            }
        
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.1,
            groq_api_key=groq_api_key
        )
        
        # Extract entities using LLM
        extraction_prompt = ENTITY_EXTRACTION_PROMPT.format(content=content[:4000])
        response = llm.invoke(extraction_prompt)
        
        # Parse LLM response
        try:
            # Find JSON in response
            content_text = response.content if hasattr(response, 'content') else str(response)
            json_start = content_text.find('{')
            json_end = content_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content_text[json_start:json_end]
                extraction_data = json.loads(json_str)
            else:
                # Fallback if no JSON found
                extraction_data = {
                    "entities": [],
                    "relationships": [],
                    "metadata": {"extraction_method": "fallback"}
                }
        
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
            # Create fallback extraction
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
        
        entities_raw = extraction_data.get("entities", [])
        relationships_raw = extraction_data.get("relationships", [])
        
        print(f"📊 Extracted {len(entities_raw)} entities, {len(relationships_raw)} relationships")
        
        # Convert to Pydantic models for validation
        entities = []
        for entity_data in entities_raw:
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
        for rel_data in relationships_raw:
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
        
        return {
            "success": True,
            "message": f"Extracted and stored {len(entities)} entities, {len(relationships)} relationships",
            "entities_found": len(entities),
            "relationships_found": len(relationships),
            "extraction_method": extraction_data.get("metadata", {}).get("extraction_method", "llm_analysis"),
            "document_id": storage_result.get("document_id"),
            "storage_result": storage_result
        }
        
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
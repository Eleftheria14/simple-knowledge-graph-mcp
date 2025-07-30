"""
Enhanced Entity Storage Tools for LlamaParse Integration

This module provides MCP tools for storing entities with structured content support
from LlamaParse including tables, figures, and formulas with precise location tracking.
"""

from typing import List, Dict, Any, Optional
import logging
from fastmcp import FastMCP

from storage.neo4j.enhanced_storage import EnhancedNeo4jStorage
from storage.chroma.enhanced_storage import EnhancedChromaDBStorage
from .entity_storage import EntityData, RelationshipData
from .structured_data_models import StructuredDocument, DocumentInfo

logger = logging.getLogger(__name__)


def register_enhanced_entity_tools(mcp: FastMCP, neo4j_storage, chromadb_storage):
    """Register enhanced entity storage tools with structured content support."""
    
    # Initialize enhanced storage classes
    enhanced_neo4j = EnhancedNeo4jStorage()
    enhanced_chromadb = EnhancedChromaDBStorage()
    
    @mcp.tool()
    def store_entities_with_structure(
        entities: List[EntityData],
        relationships: List[RelationshipData],
        document_info: DocumentInfo,
        structured_content: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhanced entity storage with tables, figures, and formulas from LlamaParse.
        
        This tool extends the basic entity storage to handle structured content
        from LlamaParse including tables, figures, and mathematical formulas with
        precise location tracking for academic literature analysis.
        
        Args:
            entities: List of extracted entities (concepts, people, methods, etc.)
            relationships: List of relationships between entities
            document_info: Enhanced document metadata with bibliographic information
            structured_content: Optional structured data from LlamaParse including:
                - tables: Table data with markdown/HTML and location info
                - figures: Figure data with captions, OCR text, and images
                - formulas: Mathematical formulas in LaTeX with context
                - metadata: Processing information and document statistics
        
        Returns:
            Storage results including counts of all stored elements and any errors
        
        Example:
            result = store_entities_with_structure(
                entities=[
                    {"id": "transformer_2017", "name": "Transformer Architecture", 
                     "type": "concept", "confidence": 0.95}
                ],
                relationships=[
                    {"source": "transformer_2017", "target": "attention_mechanism", 
                     "type": "uses", "confidence": 0.9}
                ],
                document_info={
                    "id": "vaswani_2017", "title": "Attention Is All You Need",
                    "authors": ["Ashish Vaswani", "Noam Shazeer"], "year": 2017
                },
                structured_content={
                    "tables": [{"id": "table_1", "caption": "Results", ...}],
                    "figures": [{"id": "figure_1", "caption": "Architecture", ...}],
                    "formulas": [{"id": "formula_1", "latex": "Attention(Q,K,V) = ...", ...}]
                }
            )
        """
        
        result = {
            "entities_created": 0,
            "relationships_created": 0,
            "tables_stored": 0,
            "figures_stored": 0,
            "formulas_stored": 0,
            "total_elements": 0,
            "errors": []
        }
        
        try:
            # Store basic entities using existing method (preserves backward compatibility)
            if entities or relationships:
                basic_result = neo4j_storage.store_entities(
                    entities, relationships, document_info.dict()
                )
                result.update({
                    "entities_created": basic_result.get("entities_created", 0),
                    "relationships_created": basic_result.get("relationships_created", 0)
                })
            
            # Store structured content if provided
            if structured_content:
                try:
                    # Parse structured content into our data models
                    structured_doc = StructuredDocument(**structured_content)
                    
                    # Store in Neo4j as entities with relationships
                    neo4j_result = enhanced_neo4j.store_structured_entities(
                        structured_doc, document_info
                    )
                    
                    # Store in ChromaDB as searchable vectors
                    chromadb_result = enhanced_chromadb.store_structured_vectors(
                        structured_doc, document_info
                    )
                    
                    # Merge results
                    result.update({
                        "tables_stored": neo4j_result.get("tables_stored", 0),
                        "figures_stored": neo4j_result.get("figures_stored", 0),
                        "formulas_stored": neo4j_result.get("formulas_stored", 0)
                    })
                    
                    # Add any errors from structured storage
                    if neo4j_result.get("errors"):
                        result["errors"].extend(neo4j_result["errors"])
                    
                    if chromadb_result.get("error"):
                        result["errors"].append(f"ChromaDB error: {chromadb_result['error']}")
                    
                    logger.info(f"Stored structured content: {result['tables_stored']} tables, "
                               f"{result['figures_stored']} figures, {result['formulas_stored']} formulas")
                    
                except Exception as e:
                    error_msg = f"Error processing structured content: {e}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
            
            # Calculate totals
            result["total_elements"] = (
                result["entities_created"] + 
                result["tables_stored"] + 
                result["figures_stored"] + 
                result["formulas_stored"]
            )
            
            # Success status
            result["success"] = len(result["errors"]) == 0
            result["document_id"] = document_info.id
            
            if result["success"]:
                logger.info(f"Successfully stored all content for document {document_info.id}: "
                           f"{result['total_elements']} total elements")
            else:
                logger.warning(f"Stored content with {len(result['errors'])} errors for document {document_info.id}")
            
            return result
            
        except Exception as e:
            error_msg = f"Critical error in enhanced entity storage: {e}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            result["success"] = False
            return result
    
    @mcp.tool()
    def query_structured_content(
        query: str,
        content_types: Optional[List[str]] = None,
        limit: int = 10,
        include_location: bool = True
    ) -> Dict[str, Any]:
        """
        Query structured content (tables, figures, formulas) with location information.
        
        This tool searches across tables, figures, and mathematical formulas stored
        from LlamaParse processing, returning results with precise location data
        for citation and reference purposes.
        
        Args:
            query: Search query for structured content
            content_types: Filter by content types. Options:
                - "table": Search tables and tabular data
                - "figure": Search figures, charts, and images  
                - "formula": Search mathematical formulas and equations
                - Default: searches all types
            limit: Maximum number of results to return (default: 10)
            include_location: Whether to include precise location data (page, line, bbox)
        
        Returns:
            Organized results with content from both Neo4j and ChromaDB including:
            - results: List of matching content with metadata
            - results_by_type: Results organized by content type
            - location_info: Precise document locations for citations
            - display_info: Ready-to-render display data for UI
        
        Example:
            results = query_structured_content(
                query="experimental results accuracy comparison",
                content_types=["table", "figure"],
                limit=5
            )
            # Returns tables and figures related to experimental results
        """
        
        try:
            # Default to all content types if not specified
            if not content_types:
                content_types = ["table", "figure", "formula"]
            
            # Map content types to ChromaDB types
            chromadb_types = []
            neo4j_types = []
            
            for content_type in content_types:
                if content_type == "table":
                    chromadb_types.append("structured_table")
                    neo4j_types.append("table")
                elif content_type == "figure":
                    chromadb_types.append("figure_content")
                    neo4j_types.append("figure")
                elif content_type == "formula":
                    chromadb_types.append("mathematical_formula")
                    neo4j_types.append("formula")
            
            # Query ChromaDB for semantic matches
            chromadb_results = enhanced_chromadb.query_structured_content_combined(
                query, chromadb_types, limit
            )
            
            # Query Neo4j for structured relationships and location data
            neo4j_results = enhanced_neo4j.query_structured_content(
                query, neo4j_types, limit
            )
            
            # Combine and enhance results
            combined_results = []
            
            # Process ChromaDB results (better for semantic search)
            for result in chromadb_results.get("combined_results", []):
                enhanced_result = _enhance_structured_result(result, include_location)
                combined_results.append(enhanced_result)
            
            # Add any unique Neo4j results not found in ChromaDB
            for neo4j_result in neo4j_results:
                if not _result_already_included(neo4j_result, combined_results):
                    enhanced_result = _enhance_neo4j_result(neo4j_result, include_location)
                    combined_results.append(enhanced_result)
            
            # Sort by relevance and limit
            combined_results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            combined_results = combined_results[:limit]
            
            # Organize results by type
            results_by_type = {}
            for content_type in content_types:
                type_results = [r for r in combined_results if r.get("content_type") == content_type]
                results_by_type[content_type] = type_results
            
            return {
                "query": query,
                "content_types_searched": content_types,
                "results": combined_results,
                "results_by_type": results_by_type,
                "total_found": len(combined_results),
                "include_location": include_location,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error querying structured content: {e}")
            return {
                "query": query,
                "results": [],
                "results_by_type": {},
                "total_found": 0,
                "error": str(e),
                "success": False
            }
    
    @mcp.tool()
    def get_document_structure_analysis(
        document_id: str,
        include_content_preview: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive structural analysis of a processed document.
        
        This tool provides a complete overview of a document's structured content
        including counts, locations, and content previews for all tables, figures,
        and formulas extracted by LlamaParse.
        
        Args:
            document_id: Unique identifier of the document to analyze
            include_content_preview: Whether to include content previews (default: True)
        
        Returns:
            Comprehensive document analysis including:
            - structure: Element counts and distribution
            - elements_by_page: Page-by-page breakdown
            - elements_by_section: Section-wise organization
            - content_previews: Sample content from each element type
            - processing_metadata: Information about LlamaParse processing
        
        Example:
            analysis = get_document_structure_analysis("smith_2025_transformers")
            # Returns complete structural breakdown of the document
        """
        
        try:
            # Get basic structure from Neo4j
            structure = enhanced_neo4j.get_document_structure(document_id)
            
            if structure.get("error"):
                return structure
            
            # Enhance with detailed analysis
            enhanced_analysis = {
                "document_id": document_id,
                "document_info": {
                    "title": structure.get("title"),
                    "type": structure.get("type"),
                    "path": structure.get("path")
                },
                "structure_summary": structure.get("structure", {}),
                "elements_by_type": {},
                "processing_info": {}
            }
            
            # Get detailed element information if requested
            if include_content_preview:
                with enhanced_neo4j.driver.session() as session:
                    # Get table previews
                    table_query = """
                        MATCH (t:Table)-[:APPEARS_IN]->(d:Document {id: $doc_id})
                        RETURN t.id as id, t.caption as caption, t.page as page, 
                               t.section as section, t.row_count as row_count,
                               t.columns as columns
                        ORDER BY t.page, t.id
                        LIMIT 10
                    """
                    table_results = session.run(table_query, doc_id=document_id)
                    enhanced_analysis["elements_by_type"]["tables"] = [
                        dict(record) for record in table_results
                    ]
                    
                    # Get figure previews
                    figure_query = """
                        MATCH (f:Figure)-[:APPEARS_IN]->(d:Document {id: $doc_id})
                        RETURN f.id as id, f.caption as caption, f.page as page,
                               f.section as section, f.figure_type as figure_type,
                               f.has_image_data as has_image_data
                        ORDER BY f.page, f.id
                        LIMIT 10
                    """
                    figure_results = session.run(figure_query, doc_id=document_id)
                    enhanced_analysis["elements_by_type"]["figures"] = [
                        dict(record) for record in figure_results
                    ]
                    
                    # Get formula previews
                    formula_query = """
                        MATCH (m:Formula)-[:APPEARS_IN]->(d:Document {id: $doc_id})
                        RETURN m.id as id, m.latex as latex, m.page as page,
                               m.section as section, m.domain as domain,
                               m.equation_number as equation_number
                        ORDER BY m.page, m.id
                        LIMIT 10
                    """
                    formula_results = session.run(formula_query, doc_id=document_id)
                    enhanced_analysis["elements_by_type"]["formulas"] = [
                        dict(record) for record in formula_results
                    ]
            
            enhanced_analysis["success"] = True
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing document structure: {e}")
            return {
                "document_id": document_id,
                "error": str(e),
                "success": False
            }


def _enhance_structured_result(result: Dict[str, Any], include_location: bool) -> Dict[str, Any]:
    """Enhance ChromaDB result with display and location information."""
    
    metadata = result.get("metadata", {})
    
    enhanced = {
        "id": metadata.get("element_id", ""),
        "content": result.get("content", ""),
        "content_type": metadata.get("element_type", ""),
        "confidence": result.get("confidence", 0),
        "document_id": metadata.get("document_id", ""),
        "document_title": metadata.get("document_title", "")
    }
    
    # Add location information if requested
    if include_location:
        enhanced["location"] = {
            "page": metadata.get("page"),
            "section": metadata.get("section", ""),
            "line_start": metadata.get("line_start"),
            "line_end": metadata.get("line_end"),
            "bbox": metadata.get("bbox", [])
        }
    
    # Add display information based on content type
    content_type = metadata.get("element_type", "")
    
    if content_type == "table":
        enhanced["display"] = {
            "type": "table",
            "caption": metadata.get("caption", ""),
            "columns": metadata.get("columns", []),
            "row_count": metadata.get("row_count", 0),
            "markdown": metadata.get("markdown_content", "")
        }
        
    elif content_type == "figure":
        enhanced["display"] = {
            "type": "image",
            "caption": metadata.get("caption", ""),
            "figure_type": metadata.get("figure_type", ""),
            "image_path": metadata.get("local_path", ""),
            "ocr_text": metadata.get("ocr_text", ""),
            "has_image": metadata.get("image_available", False)
        }
        
    elif content_type == "formula":
        enhanced["display"] = {
            "type": "formula",
            "latex": metadata.get("latex", ""),
            "context": metadata.get("context", ""),
            "domain": metadata.get("domain", ""),
            "equation_number": metadata.get("equation_number", "")
        }
    
    return enhanced


def _enhance_neo4j_result(result: Dict[str, Any], include_location: bool) -> Dict[str, Any]:
    """Enhance Neo4j result with consistent format."""
    
    enhanced = {
        "id": result.get("id", ""),
        "content": result.get("name", ""),
        "content_type": result.get("type", "").replace("data_", "").replace("mathematical_", ""),
        "confidence": 0.8,  # Default confidence for Neo4j exact matches
        "document_id": result.get("source_document", ""),
        "document_title": ""  # Would need additional query to get this
    }
    
    # Add location information
    if include_location:
        enhanced["location"] = {
            "page": result.get("page"),
            "section": result.get("section", ""),
            "line_start": result.get("line_start"),
            "line_end": result.get("line_end"),
            "bbox": result.get("bbox", [])
        }
    
    # Add type-specific display information
    result_type = result.get("type", "")
    
    if "table" in result_type:
        enhanced["display"] = {
            "type": "table",
            "caption": result.get("caption", ""),
            "markdown": result.get("markdown", "")
        }
    elif "figure" in result_type:
        enhanced["display"] = {
            "type": "image",
            "caption": result.get("caption", ""),
            "figure_type": result.get("figure_type", ""),
            "image_path": result.get("local_path", "")
        }
    elif "formula" in result_type:
        enhanced["display"] = {
            "type": "formula",
            "latex": result.get("latex", ""),
            "context": result.get("context", ""),
            "domain": result.get("domain", "")
        }
    
    return enhanced


def _result_already_included(neo4j_result: Dict[str, Any], existing_results: List[Dict[str, Any]]) -> bool:
    """Check if a Neo4j result is already included in the existing results."""
    
    neo4j_id = neo4j_result.get("id", "")
    
    for existing in existing_results:
        if existing.get("id") == neo4j_id:
            return True
    
    return False
"""
Enhanced ChromaDB Storage for Structured Content

This module extends the base ChromaDB storage to handle structured content from LlamaParse
with enhanced searchability and metadata for tables, figures, and formulas.
"""

import logging
from typing import List, Dict, Any, Optional

from .storage import ChromaDBStorage
from tools.storage.structured_data_models import (
    StructuredDocument, TableData, FigureData, FormulaData, DocumentInfo
)

logger = logging.getLogger(__name__)


class EnhancedChromaDBStorage(ChromaDBStorage):
    """Enhanced ChromaDB storage with support for structured content vectors."""
    
    def __init__(self):
        """Initialize enhanced ChromaDB storage."""
        super().__init__()
        logger.info("Enhanced ChromaDB storage initialized")
    
    def store_structured_vectors(
        self, 
        structured_doc: StructuredDocument, 
        document_info: DocumentInfo
    ) -> Dict[str, Any]:
        """
        Store structured content as searchable vectors with enhanced metadata.
        
        Args:
            structured_doc: Structured document with tables, figures, formulas
            document_info: Document metadata
            
        Returns:
            Dict with storage results and statistics
        """
        
        vectors = []
        
        try:
            # Store table content for semantic search
            for table in structured_doc.tables:
                table_vector = self._create_table_vector(table, document_info)
                vectors.append(table_vector)
            
            # Store figure descriptions for search
            for figure in structured_doc.figures:
                figure_vector = self._create_figure_vector(figure, document_info)
                vectors.append(figure_vector)
            
            # Store formulas with context
            for formula in structured_doc.formulas:
                formula_vector = self._create_formula_vector(formula, document_info)
                vectors.append(formula_vector)
            
            # Store using parent class method
            if vectors:
                result = self.store_vectors(vectors, document_info.dict())
                
                # Add structured content statistics
                result.update({
                    "structured_elements_stored": len(vectors),
                    "tables_vectorized": len(structured_doc.tables),
                    "figures_vectorized": len(structured_doc.figures),
                    "formulas_vectorized": len(structured_doc.formulas)
                })
                
                logger.info(f"Stored {len(vectors)} structured vectors for document {document_info.id}")
                return result
            else:
                return {
                    "vectors_stored": 0,
                    "structured_elements_stored": 0,
                    "message": "No structured content to vectorize"
                }
                
        except Exception as e:
            logger.error(f"Error storing structured vectors: {e}")
            return {
                "error": str(e),
                "vectors_stored": 0,
                "structured_elements_stored": 0
            }
    
    def _create_table_vector(
        self, 
        table: TableData, 
        document_info: DocumentInfo
    ) -> Dict[str, Any]:
        """Create searchable vector content from table data."""
        
        # Create comprehensive searchable content
        content_parts = [
            f"Table: {table.caption}",
            "",
            f"This table appears on page {table.location.page} in the {table.location.section} section.",
            "",
            "Table content:",
            table.markdown if table.markdown else "Table data not available in markdown format",
            "",
            f"Table structure: {len(table.columns)} columns × {table.row_count} rows"
        ]
        
        # Add column information
        if table.columns:
            content_parts.extend([
                "",
                f"Columns: {', '.join(table.columns)}"
            ])
        
        # Add context information
        if table.location.paragraph_context:
            content_parts.extend([
                "",
                f"Context: {table.location.paragraph_context}"
            ])
        
        # Join all content
        searchable_content = "\n".join(content_parts)
        
        return {
            "content": searchable_content,
            "type": "structured_table",
            "metadata": {
                # Core identification
                "element_id": table.id,
                "element_type": "table",
                "document_id": document_info.id,
                "document_title": document_info.title,
                
                # Table-specific metadata
                "caption": table.caption,
                "table_type": table.table_type,
                "columns": table.columns,
                "column_count": len(table.columns),
                "row_count": table.row_count,
                "has_headers": table.has_headers,
                
                # Location metadata
                "page": table.location.page,
                "section": table.location.section,
                "line_start": table.location.line_start,
                "line_end": table.location.line_end,
                "bbox": table.location.bbox,
                
                # Content formats
                "has_markdown": bool(table.markdown),
                "has_html": bool(table.html),
                "markdown_content": table.markdown,
                
                # Searchability flags
                "searchable": True,
                "display_ready": True,
                "content_category": "tabular_data"
            }
        }
    
    def _create_figure_vector(
        self, 
        figure: FigureData, 
        document_info: DocumentInfo
    ) -> Dict[str, Any]:
        """Create searchable vector content from figure data."""
        
        # Create comprehensive searchable content
        content_parts = [
            f"Figure: {figure.caption}",
            "",
            f"This {figure.figure_type} appears on page {figure.location.page} in the {figure.location.section} section."
        ]
        
        # Add OCR text if available
        if figure.ocr_text:
            content_parts.extend([
                "",
                "Text extracted from figure:",
                figure.ocr_text
            ])
        
        # Add surrounding context
        if figure.surrounding_text:
            content_parts.extend([
                "",
                f"Surrounding context: {figure.surrounding_text}"
            ])
        
        # Add references
        if figure.referenced_in_text:
            content_parts.extend([
                "",
                f"Referenced in text as: {', '.join(figure.referenced_in_text)}"
            ])
        
        # Add paragraph context
        if figure.location.paragraph_context:
            content_parts.extend([
                "",
                f"Paragraph context: {figure.location.paragraph_context}"
            ])
        
        searchable_content = "\n".join(content_parts)
        
        return {
            "content": searchable_content,
            "type": "figure_content",
            "metadata": {
                # Core identification
                "element_id": figure.id,
                "element_type": "figure",
                "document_id": document_info.id,
                "document_title": document_info.title,
                
                # Figure-specific metadata
                "caption": figure.caption,
                "figure_type": figure.figure_type,
                "has_ocr": bool(figure.ocr_text),
                "ocr_text": figure.ocr_text,
                "local_path": figure.local_path,
                
                # Location metadata
                "page": figure.location.page,
                "section": figure.location.section,
                "bbox": figure.location.bbox,
                
                # Context metadata
                "surrounding_text": figure.surrounding_text,
                "referenced_in_text": figure.referenced_in_text,
                
                # Visual metadata
                "has_image": bool(figure.image_data or figure.local_path),
                "image_available": bool(figure.local_path),
                
                # Searchability flags
                "searchable": True,
                "display_ready": True,
                "content_category": "visual_content"
            }
        }
    
    def _create_formula_vector(
        self, 
        formula: FormulaData, 
        document_info: DocumentInfo
    ) -> Dict[str, Any]:
        """Create searchable vector content from formula data."""
        
        # Create comprehensive searchable content
        content_parts = [
            f"Mathematical Formula: {formula.latex}",
            ""
        ]
        
        # Add equation number if available
        if formula.equation_number:
            content_parts.append(f"Equation number: {formula.equation_number}")
            content_parts.append("")
        
        # Add context
        content_parts.extend([
            f"Context: {formula.context}",
            ""
        ])
        
        # Add domain information
        if formula.domain:
            content_parts.extend([
                f"Mathematical domain: {formula.domain}",
                ""
            ])
        
        # Add variable definitions
        if formula.variables_defined:
            content_parts.extend([
                f"Variables defined: {', '.join(formula.variables_defined)}",
                ""
            ])
        
        # Add references
        if formula.referenced_in_text:
            content_parts.extend([
                f"Referenced in text as: {', '.join(formula.referenced_in_text)}",
            ])
        
        # Add location context
        content_parts.append(f"This formula appears on page {formula.location.page} in the {formula.location.section} section.")
        
        if formula.location.paragraph_context:
            content_parts.extend([
                "",
                f"Paragraph context: {formula.location.paragraph_context}"
            ])
        
        searchable_content = "\n".join(content_parts)
        
        return {
            "content": searchable_content,
            "type": "mathematical_formula",
            "metadata": {
                # Core identification
                "element_id": formula.id,
                "element_type": "formula",
                "document_id": document_info.id,
                "document_title": document_info.title,
                
                # Formula-specific metadata
                "latex": formula.latex,
                "context": formula.context,
                "domain": formula.domain,
                "equation_number": formula.equation_number,
                "variables_defined": formula.variables_defined,
                
                # Location metadata
                "page": formula.location.page,
                "section": formula.location.section,
                "line_number": formula.location.line_start,
                
                # Reference metadata
                "referenced_in_text": formula.referenced_in_text,
                
                # Mathematical metadata
                "has_equation_number": bool(formula.equation_number),
                "has_variables": bool(formula.variables_defined),
                "mathematical_domain": formula.domain or "general",
                
                # Searchability flags
                "searchable": True,
                "display_ready": True,
                "content_category": "mathematical_content"
            }
        }
    
    def query_by_content_type(
        self, 
        query: str, 
        content_type: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query structured content by specific type.
        
        Args:
            query: Search query
            content_type: Type filter (structured_table, figure_content, mathematical_formula)
            limit: Maximum results
            
        Returns:
            List of matching structured content with metadata
        """
        
        try:
            # Use the base class query method with type filtering
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where={"type": content_type}
            )
            
            enhanced_results = []
            
            if results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        "distance": results['distances'][0][i] if results['distances'] and results['distances'][0] else 0,
                        "confidence": 1 - (results['distances'][0][i] if results['distances'] and results['distances'][0] else 0)
                    }
                    
                    # Enhance with display information
                    result = self._enhance_result_for_display(result)
                    enhanced_results.append(result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error querying by content type {content_type}: {e}")
            return []
    
    def query_structured_content_combined(
        self, 
        query: str, 
        content_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Query multiple types of structured content and return organized results.
        
        Args:
            query: Search query
            content_types: List of content types to search
            limit: Maximum results per type
            
        Returns:
            Dict with organized results by content type
        """
        
        if not content_types:
            content_types = ["structured_table", "figure_content", "mathematical_formula"]
        
        results = {
            "query": query,
            "results_by_type": {},
            "combined_results": [],
            "total_found": 0
        }
        
        try:
            for content_type in content_types:
                type_results = self.query_by_content_type(query, content_type, limit)
                
                # Store by type
                results["results_by_type"][content_type] = type_results
                
                # Add to combined results with type indicator
                for result in type_results:
                    result["source_type"] = content_type
                    results["combined_results"].append(result)
            
            # Sort combined results by confidence/relevance
            results["combined_results"].sort(key=lambda x: x.get("confidence", 0), reverse=True)
            
            # Limit combined results
            results["combined_results"] = results["combined_results"][:limit]
            results["total_found"] = len(results["combined_results"])
            
            return results
            
        except Exception as e:
            logger.error(f"Error in combined structured content query: {e}")
            results["error"] = str(e)
            return results
    
    def _enhance_result_for_display(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Add display information for structured content."""
        
        metadata = result.get("metadata", {})
        element_type = metadata.get("element_type", "")
        
        if element_type == "table":
            result["display"] = {
                "type": "table",
                "caption": metadata.get("caption", ""),
                "columns": metadata.get("columns", []),
                "row_count": metadata.get("row_count", 0),
                "markdown": metadata.get("markdown_content", ""),
                "page": metadata.get("page"),
                "section": metadata.get("section", "")
            }
            
        elif element_type == "figure":
            result["display"] = {
                "type": "image",
                "caption": metadata.get("caption", ""),
                "figure_type": metadata.get("figure_type", ""),
                "image_path": metadata.get("local_path", ""),
                "ocr_text": metadata.get("ocr_text", ""),
                "page": metadata.get("page"),
                "section": metadata.get("section", ""),
                "has_image": metadata.get("image_available", False)
            }
            
        elif element_type == "formula":
            result["display"] = {
                "type": "formula",
                "latex": metadata.get("latex", ""),
                "context": metadata.get("context", ""),
                "domain": metadata.get("domain", ""),
                "equation_number": metadata.get("equation_number", ""),
                "page": metadata.get("page"),
                "section": metadata.get("section", "")
            }
        
        return result
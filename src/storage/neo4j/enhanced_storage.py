"""
Enhanced Neo4j Storage for Structured Content

This module extends the base Neo4j storage to handle tables, figures, and formulas
from LlamaParse with precise location tracking and rich metadata.
"""

import os
import base64
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .storage import Neo4jStorage
from tools.storage.structured_data_models import (
    StructuredDocument, TableData, FigureData, FormulaData, DocumentInfo, LocationInfo
)

logger = logging.getLogger(__name__)


class EnhancedNeo4jStorage(Neo4jStorage):
    """Enhanced Neo4j storage with support for tables, figures, and formulas."""
    
    def __init__(self):
        """Initialize enhanced storage with figure storage directory."""
        super().__init__()
        
        # Create figures storage directory
        project_root = Path(__file__).parent.parent.parent.parent
        self.figures_dir = project_root / "storage" / "figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Enhanced Neo4j storage initialized. Figures directory: {self.figures_dir}")
    
    def store_structured_entities(
        self, 
        structured_doc: StructuredDocument, 
        document_info: DocumentInfo
    ) -> Dict[str, Any]:
        """
        Store tables, figures, formulas as entities with relationships and location data.
        
        Args:
            structured_doc: Structured document with tables, figures, formulas
            document_info: Document metadata
            
        Returns:
            Dict with counts of stored elements and any errors
        """
        
        with self.driver.session() as session:
            results = {
                "tables_stored": 0,
                "figures_stored": 0,
                "formulas_stored": 0,
                "errors": []
            }
            
            try:
                # Store table entities
                for table in structured_doc.tables:
                    try:
                        self._store_table_entity(session, table, document_info)
                        results["tables_stored"] += 1
                    except Exception as e:
                        error_msg = f"Error storing table {table.id}: {e}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                
                # Store figure entities
                for figure in structured_doc.figures:
                    try:
                        # Save figure file locally first
                        if figure.image_data and not figure.local_path:
                            figure.local_path = self._save_figure_file(figure, document_info.id)
                        
                        self._store_figure_entity(session, figure, document_info)
                        results["figures_stored"] += 1
                    except Exception as e:
                        error_msg = f"Error storing figure {figure.id}: {e}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                
                # Store formula entities
                for formula in structured_doc.formulas:
                    try:
                        self._store_formula_entity(session, formula, document_info)
                        results["formulas_stored"] += 1
                    except Exception as e:
                        error_msg = f"Error storing formula {formula.id}: {e}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                
                logger.info(f"Stored structured content: {results['tables_stored']} tables, "
                           f"{results['figures_stored']} figures, {results['formulas_stored']} formulas")
                
            except Exception as e:
                error_msg = f"Error in structured entity storage: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
            
            return results
    
    def _store_table_entity(
        self, 
        session, 
        table: TableData, 
        document_info: DocumentInfo
    ) -> None:
        """Store a table as a Neo4j entity with location and content metadata."""
        
        entity_id = f"table_{document_info.id}_{table.id}"
        
        # Prepare table properties
        table_props = {
            "entity_id": entity_id,
            "name": f"Table: {table.caption}",
            "type": "data_table",
            "caption": table.caption,
            "markdown": table.markdown,
            "html": table.html,
            "columns": table.columns,
            "row_count": table.row_count,
            "table_type": table.table_type,
            "has_headers": table.has_headers,
            
            # Location information
            "page": table.location.page,
            "bbox": table.location.bbox,
            "line_start": table.location.line_start,
            "line_end": table.location.line_end,
            "section": table.location.section,
            "paragraph_context": table.location.paragraph_context,
            
            # Metadata
            "created": "datetime()",
            "source_document": document_info.id
        }
        
        # Create table entity
        session.run("""
            MERGE (t:Table:StructuredContent {id: $entity_id})
            SET t.name = $name,
                t.type = $type,
                t.caption = $caption,
                t.markdown = $markdown,
                t.html = $html,
                t.columns = $columns,
                t.row_count = $row_count,
                t.table_type = $table_type,
                t.has_headers = $has_headers,
                t.page = $page,
                t.bbox = $bbox,
                t.line_start = $line_start,
                t.line_end = $line_end,
                t.section = $section,
                t.paragraph_context = $paragraph_context,
                t.created = datetime(),
                t.source_document = $source_document
        """, **table_props)
        
        # Create relationship to document
        session.run("""
            MATCH (t:Table {id: $entity_id})
            MATCH (d:Document {id: $doc_id})
            MERGE (t)-[:APPEARS_IN {page: $page, section: $section}]->(d)
        """, entity_id=entity_id, doc_id=document_info.id, 
            page=table.location.page, section=table.location.section)
        
        # Create relationships to sections if section info is available
        if table.location.section:
            session.run("""
                MERGE (s:Section {name: $section, document_id: $doc_id})
                SET s.document_id = $doc_id
                WITH s
                MATCH (t:Table {id: $entity_id})
                MERGE (t)-[:IN_SECTION]->(s)
            """, section=table.location.section, doc_id=document_info.id, entity_id=entity_id)
    
    def _store_figure_entity(
        self, 
        session, 
        figure: FigureData, 
        document_info: DocumentInfo
    ) -> None:
        """Store a figure as a Neo4j entity with location and visual metadata."""
        
        entity_id = f"figure_{document_info.id}_{figure.id}"
        
        # Prepare figure properties
        figure_props = {
            "entity_id": entity_id,
            "name": f"Figure: {figure.caption}",
            "type": "figure",
            "caption": figure.caption,
            "figure_type": figure.figure_type,
            "ocr_text": figure.ocr_text,
            "local_path": figure.local_path,
            "surrounding_text": figure.surrounding_text,
            "referenced_in_text": figure.referenced_in_text,
            
            # Location information
            "page": figure.location.page,
            "bbox": figure.location.bbox,
            "section": figure.location.section,
            "paragraph_context": figure.location.paragraph_context,
            
            # Metadata
            "created": "datetime()",
            "source_document": document_info.id,
            "has_image_data": bool(figure.image_data or figure.local_path)
        }
        
        # Create figure entity
        session.run("""
            MERGE (f:Figure:StructuredContent {id: $entity_id})
            SET f.name = $name,
                f.type = $type,
                f.caption = $caption,
                f.figure_type = $figure_type,
                f.ocr_text = $ocr_text,
                f.local_path = $local_path,
                f.surrounding_text = $surrounding_text,
                f.referenced_in_text = $referenced_in_text,
                f.page = $page,
                f.bbox = $bbox,
                f.section = $section,
                f.paragraph_context = $paragraph_context,
                f.created = datetime(),
                f.source_document = $source_document,
                f.has_image_data = $has_image_data
        """, **figure_props)
        
        # Create relationship to document
        session.run("""
            MATCH (f:Figure {id: $entity_id})
            MATCH (d:Document {id: $doc_id})
            MERGE (f)-[:APPEARS_IN {page: $page, section: $section}]->(d)
        """, entity_id=entity_id, doc_id=document_info.id, 
            page=figure.location.page, section=figure.location.section)
        
        # Create relationships to sections
        if figure.location.section:
            session.run("""
                MERGE (s:Section {name: $section, document_id: $doc_id})
                SET s.document_id = $doc_id
                WITH s
                MATCH (f:Figure {id: $entity_id})
                MERGE (f)-[:IN_SECTION]->(s)
            """, section=figure.location.section, doc_id=document_info.id, entity_id=entity_id)
    
    def _store_formula_entity(
        self, 
        session, 
        formula: FormulaData, 
        document_info: DocumentInfo
    ) -> None:
        """Store a formula as a Neo4j entity with LaTeX and domain metadata."""
        
        entity_id = f"formula_{document_info.id}_{formula.id}"
        
        # Prepare formula properties
        formula_props = {
            "entity_id": entity_id,
            "name": f"Formula: {formula.latex[:50]}{'...' if len(formula.latex) > 50 else ''}",
            "type": "mathematical_formula",
            "latex": formula.latex,
            "context": formula.context,
            "domain": formula.domain,
            "equation_number": formula.equation_number,
            "variables_defined": formula.variables_defined,
            "referenced_in_text": formula.referenced_in_text,
            
            # Location information
            "page": formula.location.page,
            "line_number": formula.location.line_start or formula.location.line_end,
            "section": formula.location.section,
            "paragraph_context": formula.location.paragraph_context,
            
            # Metadata
            "created": "datetime()",
            "source_document": document_info.id
        }
        
        # Create formula entity
        session.run("""
            MERGE (m:Formula:StructuredContent {id: $entity_id})
            SET m.name = $name,
                m.type = $type,
                m.latex = $latex,
                m.context = $context,
                m.domain = $domain,
                m.equation_number = $equation_number,
                m.variables_defined = $variables_defined,
                m.referenced_in_text = $referenced_in_text,
                m.page = $page,
                m.line_number = $line_number,
                m.section = $section,
                m.paragraph_context = $paragraph_context,
                m.created = datetime(),
                m.source_document = $source_document
        """, **formula_props)
        
        # Create relationship to document
        session.run("""
            MATCH (m:Formula {id: $entity_id})
            MATCH (d:Document {id: $doc_id})
            MERGE (m)-[:APPEARS_IN {page: $page, section: $section}]->(d)
        """, entity_id=entity_id, doc_id=document_info.id, 
            page=formula.location.page, section=formula.location.section)
        
        # Create relationships to mathematical domains
        if formula.domain:
            session.run("""
                MERGE (domain:MathematicalDomain {name: $domain})
                WITH domain
                MATCH (m:Formula {id: $entity_id})
                MERGE (m)-[:BELONGS_TO_DOMAIN]->(domain)
            """, domain=formula.domain, entity_id=entity_id)
        
        # Create relationships to sections
        if formula.location.section:
            session.run("""
                MERGE (s:Section {name: $section, document_id: $doc_id})
                SET s.document_id = $doc_id
                WITH s
                MATCH (m:Formula {id: $entity_id})
                MERGE (m)-[:IN_SECTION]->(s)
            """, section=formula.location.section, doc_id=document_info.id, entity_id=entity_id)
    
    def _save_figure_file(self, figure: FigureData, document_id: str) -> str:
        """
        Save figure image data to local file.
        
        Args:
            figure: Figure data with image_data
            document_id: Document identifier
            
        Returns:
            Local file path where image was saved
        """
        if not figure.image_data:
            return ""
        
        try:
            # Generate filename
            figure_filename = f"{document_id}_{figure.id}.png"
            figure_path = self.figures_dir / figure_filename
            
            # Decode and save image data
            if isinstance(figure.image_data, str):
                # Base64 encoded string
                image_bytes = base64.b64decode(figure.image_data)
            else:
                # Raw bytes
                image_bytes = figure.image_data
            
            with open(figure_path, "wb") as f:
                f.write(image_bytes)
            
            logger.info(f"Saved figure to: {figure_path}")
            return str(figure_path)
            
        except Exception as e:
            logger.error(f"Error saving figure {figure.id}: {e}")
            return ""
    
    def query_structured_content(
        self, 
        query: str, 
        content_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query structured content (tables, figures, formulas) in Neo4j.
        
        Args:
            query: Search query text
            content_types: Filter by content types (table, figure, formula)
            limit: Maximum results to return
            
        Returns:
            List of structured content matches with metadata
        """
        
        if not content_types:
            content_types = ["table", "figure", "formula"]
        
        results = []
        
        with self.driver.session() as session:
            try:
                # Query tables
                if "table" in content_types:
                    table_query = """
                        MATCH (t:Table)
                        WHERE t.caption CONTAINS $query 
                           OR t.markdown CONTAINS $query
                           OR t.section CONTAINS $query
                           OR t.paragraph_context CONTAINS $query
                        RETURN t.id as id, t.name as name, t.type as type,
                               t.caption as caption, t.markdown as markdown,
                               t.page as page, t.section as section,
                               t.bbox as bbox, t.line_start as line_start,
                               t.line_end as line_end, t.source_document as source_document
                        LIMIT $limit
                    """
                    
                    table_results = session.run(table_query, query=query, limit=limit)
                    for record in table_results:
                        result = dict(record)
                        result["content_type"] = "table"
                        result["display_type"] = "table"
                        results.append(result)
                
                # Query figures
                if "figure" in content_types:
                    figure_query = """
                        MATCH (f:Figure)
                        WHERE f.caption CONTAINS $query
                           OR f.ocr_text CONTAINS $query
                           OR f.section CONTAINS $query
                           OR f.surrounding_text CONTAINS $query
                        RETURN f.id as id, f.name as name, f.type as type,
                               f.caption as caption, f.figure_type as figure_type,
                               f.ocr_text as ocr_text, f.local_path as local_path,
                               f.page as page, f.section as section,
                               f.bbox as bbox, f.source_document as source_document
                        LIMIT $limit
                    """
                    
                    figure_results = session.run(figure_query, query=query, limit=limit)
                    for record in figure_results:
                        result = dict(record)
                        result["content_type"] = "figure"
                        result["display_type"] = "image"
                        results.append(result)
                
                # Query formulas
                if "formula" in content_types:
                    formula_query = """
                        MATCH (m:Formula)
                        WHERE m.latex CONTAINS $query
                           OR m.context CONTAINS $query
                           OR m.domain CONTAINS $query
                           OR m.section CONTAINS $query
                        RETURN m.id as id, m.name as name, m.type as type,
                               m.latex as latex, m.context as context,
                               m.domain as domain, m.equation_number as equation_number,
                               m.page as page, m.section as section,
                               m.line_number as line_number, m.source_document as source_document
                        LIMIT $limit
                    """
                    
                    formula_results = session.run(formula_query, query=query, limit=limit)
                    for record in formula_results:
                        result = dict(record)
                        result["content_type"] = "formula"
                        result["display_type"] = "formula"
                        results.append(result)
                
            except Exception as e:
                logger.error(f"Error querying structured content: {e}")
        
        return results[:limit]
    
    def get_document_structure(self, document_id: str) -> Dict[str, Any]:
        """
        Get the complete structure of a document including all structured elements.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Dict with document structure and element counts
        """
        
        with self.driver.session() as session:
            try:
                # Get document info
                doc_query = """
                    MATCH (d:Document {id: $doc_id})
                    RETURN d.title as title, d.type as type, d.path as path
                """
                doc_result = session.run(doc_query, doc_id=document_id).single()
                
                if not doc_result:
                    return {"error": f"Document {document_id} not found"}
                
                # Get structured elements counts
                structure_query = """
                    MATCH (d:Document {id: $doc_id})
                    OPTIONAL MATCH (t:Table)-[:APPEARS_IN]->(d)
                    OPTIONAL MATCH (f:Figure)-[:APPEARS_IN]->(d)
                    OPTIONAL MATCH (m:Formula)-[:APPEARS_IN]->(d)
                    RETURN count(DISTINCT t) as table_count,
                           count(DISTINCT f) as figure_count,
                           count(DISTINCT m) as formula_count
                """
                structure_result = session.run(structure_query, doc_id=document_id).single()
                
                return {
                    "document_id": document_id,
                    "title": doc_result["title"],
                    "type": doc_result["type"],
                    "path": doc_result["path"],
                    "structure": {
                        "tables": structure_result["table_count"],
                        "figures": structure_result["figure_count"],
                        "formulas": structure_result["formula_count"],
                        "total_elements": (structure_result["table_count"] + 
                                         structure_result["figure_count"] + 
                                         structure_result["formula_count"])
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting document structure: {e}")
                return {"error": str(e)}
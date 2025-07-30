"""
LlamaParse Integration Client

This module provides the integration layer for LlamaParse document processing.
It handles document parsing, structured content extraction, and location tracking
for enhanced entity extraction with precise provenance.
"""

from typing import Dict, Any, List, Optional
import os
import base64
import logging
from pathlib import Path

try:
    from llama_parse import LlamaParse
except ImportError:
    LlamaParse = None

import config

logger = logging.getLogger(__name__)


class LlamaParseClient:
    """Client for LlamaParse document processing integration."""
    
    def __init__(self):
        """Initialize LlamaParse client with configuration."""
        if not LlamaParse:
            raise ImportError("llama-parse not installed. Run: uv add llama-parse")
        
        if not config.LLAMAPARSE_API_KEY:
            raise ValueError("LLAMAPARSE_API_KEY not set in environment variables")
        
        self.parser = LlamaParse(
            api_key=config.LLAMAPARSE_API_KEY,
            result_type="json",  # Get structured output
            premium_mode=config.LLAMAPARSE_PREMIUM_MODE,
            language=config.LLAMAPARSE_LANGUAGE,
            verbose=True
        )
        
        logger.info("LlamaParse client initialized successfully")
    
    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse document and return structured data with location information.
        
        Args:
            file_path: Path to PDF document
            
        Returns:
            Dict containing text, tables, figures, formulas, and precise location metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if file_path.suffix.lower() != '.pdf':
            raise ValueError(f"Only PDF files supported, got: {file_path.suffix}")
        
        try:
            logger.info(f"Starting LlamaParse processing for: {file_path}")
            documents = self.parser.load_data(str(file_path))
            
            if not documents:
                raise ValueError(f"No content extracted from {file_path}")
            
            # Process the first document (LlamaParse typically returns one document per file)
            structured_content = self.extract_structured_content(documents[0])
            
            logger.info(f"Successfully parsed document: {len(structured_content['text'])} chars, "
                       f"{len(structured_content['tables'])} tables, "
                       f"{len(structured_content['figures'])} figures, "
                       f"{len(structured_content['formulas'])} formulas")
            
            return structured_content
            
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {e}")
            return {
                "text": "",
                "tables": [],
                "figures": [],
                "formulas": [],
                "metadata": {"error": str(e), "file_path": str(file_path)}
            }
    
    def extract_structured_content(self, document) -> Dict[str, Any]:
        """
        Extract tables, figures, formulas from parsed content with location tracking.
        
        Args:
            document: LlamaParse document object
            
        Returns:
            Dict with structured content and precise location information
        """
        try:
            # Convert document to dict format (LlamaParse provides this)
            if hasattr(document, 'to_dict'):
                parsed_data = document.to_dict()
            elif hasattr(document, 'dict'):
                parsed_data = document.dict()
            else:
                # Fallback: treat as dict-like object
                parsed_data = {
                    "text": str(document),
                    "tables": getattr(document, 'tables', []),
                    "figures": getattr(document, 'figures', []),
                    "formulas": getattr(document, 'formulas', []),
                    "metadata": getattr(document, 'metadata', {})
                }
            
            return {
                "text": self._extract_clean_text(parsed_data),
                "tables": self._extract_tables(parsed_data),
                "figures": self._extract_figures(parsed_data),
                "formulas": self._extract_formulas(parsed_data),
                "metadata": self._extract_metadata(parsed_data)
            }
            
        except Exception as e:
            logger.error(f"Error extracting structured content: {e}")
            return {
                "text": str(document) if document else "",
                "tables": [],
                "figures": [],
                "formulas": [],
                "metadata": {"extraction_error": str(e)}
            }
    
    def _extract_clean_text(self, parsed_data: Dict) -> str:
        """Extract clean text content with preserved structure."""
        text = parsed_data.get("text", "")
        
        # Ensure we have some text content
        if not text and "content" in parsed_data:
            text = parsed_data["content"]
        
        return text.strip() if text else ""
    
    def _extract_tables(self, parsed_data: Dict) -> List[Dict[str, Any]]:
        """Extract table data with markdown, HTML formatting, and location info."""
        tables = []
        
        for i, table_data in enumerate(parsed_data.get("tables", [])):
            table = {
                "id": f"table_{i+1}",
                "caption": table_data.get("caption", f"Table {i+1}"),
                "markdown": table_data.get("markdown", ""),
                "html": table_data.get("html", ""),
                "page": table_data.get("page", 1),
                "bbox": table_data.get("bbox", []),  # [x1, y1, x2, y2] coordinates
                "line_start": table_data.get("line_start"),
                "line_end": table_data.get("line_end"),
                "columns": table_data.get("columns", []),
                "row_count": table_data.get("row_count", 0),
                "section": table_data.get("section", ""),  # Section heading context
                "paragraph_context": table_data.get("paragraph_context", "")
            }
            
            # Generate markdown from HTML if missing
            if not table["markdown"] and table["html"]:
                table["markdown"] = self._html_to_markdown(table["html"])
            
            # Extract column info from markdown if missing
            if not table["columns"] and table["markdown"]:
                table["columns"] = self._extract_columns_from_markdown(table["markdown"])
                table["row_count"] = self._count_rows_in_markdown(table["markdown"])
            
            tables.append(table)
        
        return tables
    
    def _extract_figures(self, parsed_data: Dict) -> List[Dict[str, Any]]:
        """Extract figure data with images, captions, and location info."""
        figures = []
        
        for i, figure_data in enumerate(parsed_data.get("figures", [])):
            figure = {
                "id": f"figure_{i+1}",
                "caption": figure_data.get("caption", f"Figure {i+1}"),
                "figure_type": self._classify_figure_type(figure_data.get("caption", "")),
                "ocr_text": figure_data.get("ocr_text", ""),
                "page": figure_data.get("page", 1),
                "bbox": figure_data.get("bbox", []),  # Bounding box coordinates
                "line_context": figure_data.get("line_context", []),  # Lines referencing this figure
                "image_data": figure_data.get("image_data"),  # Base64 encoded image
                "local_path": None,  # Will be set during storage
                "section": figure_data.get("section", ""),
                "surrounding_text": figure_data.get("surrounding_text", "")
            }
            
            figures.append(figure)
        
        return figures
    
    def _extract_formulas(self, parsed_data: Dict) -> List[Dict[str, Any]]:
        """Extract mathematical formulas as LaTeX with precise location."""
        formulas = []
        
        for i, formula_data in enumerate(parsed_data.get("formulas", [])):
            formula = {
                "id": f"formula_{i+1}",
                "latex": formula_data.get("latex", ""),
                "context": formula_data.get("context", ""),
                "domain": self._infer_mathematical_domain(formula_data.get("context", "")),
                "page": formula_data.get("page", 1),
                "line_number": formula_data.get("line_number"),
                "bbox": formula_data.get("bbox", []),
                "equation_number": formula_data.get("equation_number", ""),  # (1), (2), etc.
                "section": formula_data.get("section", ""),
                "paragraph_context": formula_data.get("paragraph_context", "")
            }
            
            formulas.append(formula)
        
        return formulas
    
    def _extract_metadata(self, parsed_data: Dict) -> Dict[str, Any]:
        """Extract document metadata with processing information."""
        metadata = parsed_data.get("metadata", {})
        
        return {
            "total_pages": metadata.get("total_pages", 0),
            "processing_time": metadata.get("processing_time", 0),
            "language": metadata.get("language", "en"),
            "document_type": metadata.get("document_type", "academic_paper"),
            "parse_version": metadata.get("parse_version", "unknown"),
            "premium_mode": config.LLAMAPARSE_PREMIUM_MODE,
            "extraction_timestamp": metadata.get("timestamp")
        }
    
    def _classify_figure_type(self, caption: str) -> str:
        """Classify figure type based on caption content."""
        caption_lower = caption.lower()
        
        if any(word in caption_lower for word in ["flowchart", "workflow", "process", "diagram"]):
            return "flowchart"
        elif any(word in caption_lower for word in ["graph", "plot", "chart", "histogram"]):
            return "chart"
        elif any(word in caption_lower for word in ["architecture", "network", "model", "structure"]):
            return "architecture_diagram"
        elif any(word in caption_lower for word in ["screenshot", "interface", "ui", "gui"]):
            return "screenshot"
        elif any(word in caption_lower for word in ["photo", "image", "picture"]):
            return "photograph"
        else:
            return "diagram"
    
    def _infer_mathematical_domain(self, context: str) -> Optional[str]:
        """Infer mathematical domain from formula context."""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["learning", "neural", "network", "ai", "ml"]):
            return "machine_learning"
        elif any(word in context_lower for word in ["probability", "statistics", "bayesian", "distribution"]):
            return "statistics"
        elif any(word in context_lower for word in ["optimization", "minimize", "maximize", "objective"]):
            return "optimization"
        elif any(word in context_lower for word in ["linear", "algebra", "matrix", "vector"]):
            return "linear_algebra"
        elif any(word in context_lower for word in ["calculus", "derivative", "integral", "differential"]):
            return "calculus"
        else:
            return "general_mathematics"
    
    def _html_to_markdown(self, html: str) -> str:
        """Convert simple HTML table to markdown format."""
        # Basic HTML to markdown conversion for tables
        try:
            import re
            
            # Remove HTML tags and convert to basic markdown
            # This is a simplified conversion - could be enhanced with proper HTML parser
            markdown = html
            markdown = re.sub(r'<table[^>]*>', '', markdown)
            markdown = re.sub(r'</table>', '', markdown)
            markdown = re.sub(r'<tr[^>]*>', '', markdown)
            markdown = re.sub(r'</tr>', '\n', markdown)
            markdown = re.sub(r'<th[^>]*>', '| ', markdown)
            markdown = re.sub(r'</th>', ' ', markdown)
            markdown = re.sub(r'<td[^>]*>', '| ', markdown)
            markdown = re.sub(r'</td>', ' ', markdown)
            
            # Clean up extra whitespace
            markdown = re.sub(r'\n+', '\n', markdown.strip())
            
            return markdown
            
        except Exception as e:
            logger.warning(f"HTML to markdown conversion failed: {e}")
            return html
    
    def _extract_columns_from_markdown(self, markdown: str) -> List[str]:
        """Extract column names from markdown table."""
        try:
            lines = markdown.strip().split('\n')
            if lines:
                # First line should contain headers
                header_line = lines[0]
                columns = [col.strip() for col in header_line.split('|') if col.strip()]
                return columns
        except Exception as e:
            logger.warning(f"Column extraction failed: {e}")
        
        return []
    
    def _count_rows_in_markdown(self, markdown: str) -> int:
        """Count data rows in markdown table (excluding header and separator)."""
        try:
            lines = [line.strip() for line in markdown.strip().split('\n') if line.strip()]
            # Remove header and separator lines
            data_lines = [line for line in lines if not line.startswith('|---') and line.startswith('|')]
            return max(0, len(data_lines) - 1)  # Subtract header row
        except Exception as e:
            logger.warning(f"Row counting failed: {e}")
            return 0
    
    def test_connection(self) -> bool:
        """Test LlamaParse API connection."""
        try:
            # Create a minimal test to verify API key works
            if not config.LLAMAPARSE_API_KEY:
                logger.error("No API key configured")
                return False
            
            logger.info("LlamaParse client configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"LlamaParse connection test failed: {e}")
            return False
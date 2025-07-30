"""
Structured Data Models for LlamaParse Integration

This module defines Pydantic models for handling structured content from LlamaParse
including tables, figures, and formulas with precise location information.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class LocationInfo(BaseModel):
    """Location information for any content element."""
    page: int = Field(default=1, description="Page number where element appears")
    bbox: List[float] = Field(default_factory=list, description="Bounding box coordinates [x1, y1, x2, y2]")
    line_start: Optional[int] = Field(default=None, description="Starting line number")
    line_end: Optional[int] = Field(default=None, description="Ending line number")
    section: str = Field(default="", description="Section heading context")
    paragraph_context: str = Field(default="", description="Surrounding paragraph text")


class TableData(BaseModel):
    """Represents a table extracted from a document with location tracking."""
    
    id: str = Field(description="Unique identifier for this table")
    caption: str = Field(description="Table caption or title")
    markdown: str = Field(default="", description="Table content in markdown format")
    html: str = Field(default="", description="Table content in HTML format")
    columns: List[str] = Field(default_factory=list, description="Column headers")
    row_count: int = Field(default=0, description="Number of data rows")
    
    # Location information
    location: LocationInfo = Field(default_factory=LocationInfo)
    
    # Metadata
    table_type: str = Field(default="data", description="Type: data, comparison, results, etc.")
    has_headers: bool = Field(default=True, description="Whether table has header row")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "table_1",
                "caption": "Experimental Results Comparison",
                "markdown": "| Method | Accuracy | Precision |\n|--------|----------|----------|\n| A | 85.2% | 0.89 |\n| B | 92.1% | 0.94 |",
                "html": "<table><tr><th>Method</th><th>Accuracy</th><th>Precision</th></tr><tr><td>A</td><td>85.2%</td><td>0.89</td></tr><tr><td>B</td><td>92.1%</td><td>0.94</td></tr></table>",
                "columns": ["Method", "Accuracy", "Precision"],
                "row_count": 2,
                "location": {
                    "page": 3,
                    "bbox": [100, 200, 400, 300],
                    "line_start": 45,
                    "line_end": 52,
                    "section": "Results",
                    "paragraph_context": "Table 1 shows the comparison of different methods..."
                },
                "table_type": "comparison"
            }
        }


class FigureData(BaseModel):
    """Represents a figure/image extracted from a document with location tracking."""
    
    id: str = Field(description="Unique identifier for this figure")
    caption: str = Field(description="Figure caption or title")
    figure_type: str = Field(default="diagram", description="Type: chart, diagram, photo, flowchart, etc.")
    ocr_text: str = Field(default="", description="Text extracted from the image via OCR")
    
    # Image data
    image_data: Optional[bytes] = Field(default=None, description="Base64 encoded image data")
    local_path: Optional[str] = Field(default=None, description="Local file path where image is stored")
    
    # Location information
    location: LocationInfo = Field(default_factory=LocationInfo)
    
    # Context
    surrounding_text: str = Field(default="", description="Text surrounding the figure reference")
    referenced_in_text: List[str] = Field(default_factory=list, description="Text snippets that reference this figure")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "figure_1",
                "caption": "Neural Network Architecture Overview",
                "figure_type": "architecture_diagram",
                "ocr_text": "Input Layer -> Hidden Layer -> Output Layer",
                "local_path": "storage/figures/paper_2025_figure_1.png",
                "location": {
                    "page": 2,
                    "bbox": [50, 100, 300, 250],
                    "section": "Methodology",
                    "paragraph_context": "The proposed architecture is shown in Figure 1..."
                },
                "surrounding_text": "As illustrated in the diagram, our approach uses...",
                "referenced_in_text": ["see Figure 1", "shown in Figure 1", "Figure 1 illustrates"]
            }
        }


class FormulaData(BaseModel):
    """Represents a mathematical formula extracted from a document with location tracking."""
    
    id: str = Field(description="Unique identifier for this formula")
    latex: str = Field(description="LaTeX representation of the formula")
    context: str = Field(description="Surrounding text that explains the formula")
    domain: Optional[str] = Field(default=None, description="Mathematical domain: ml, statistics, etc.")
    
    # Formula metadata
    equation_number: str = Field(default="", description="Equation number if present (e.g., '(1)', '(2)')")
    variables_defined: List[str] = Field(default_factory=list, description="Variables defined in surrounding text")
    
    # Location information
    location: LocationInfo = Field(default_factory=LocationInfo)
    
    # References
    referenced_in_text: List[str] = Field(default_factory=list, description="Text snippets that reference this formula")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "formula_1",
                "latex": "\\sum_{i=1}^{n} x_i \\cdot w_i + b",
                "context": "The linear transformation is computed as shown in equation (1), where x_i represents input features and w_i are the learned weights.",
                "domain": "machine_learning",
                "equation_number": "(1)",
                "variables_defined": ["x_i", "w_i", "b", "n"],
                "location": {
                    "page": 1,
                    "line_number": 67,
                    "section": "Methodology",
                    "paragraph_context": "Our model computes the weighted sum of inputs..."
                },
                "referenced_in_text": ["equation (1)", "as shown in (1)", "using formula 1"]
            }
        }


class StructuredDocument(BaseModel):
    """Complete structured document with all extracted elements and metadata."""
    
    # Core content
    text: str = Field(description="Clean extracted text from the document")
    
    # Structured elements
    tables: List[TableData] = Field(default_factory=list, description="Extracted tables")
    figures: List[FigureData] = Field(default_factory=list, description="Extracted figures")
    formulas: List[FormulaData] = Field(default_factory=list, description="Extracted formulas")
    
    # Document metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document processing metadata")
    
    # Processing statistics
    processing_stats: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total_pages": 0,
            "processing_time": 0,
            "extraction_quality": "unknown",
            "elements_found": 0
        },
        description="Statistics about the parsing process"
    )
    
    def get_element_count(self) -> Dict[str, int]:
        """Get count of all structured elements."""
        return {
            "tables": len(self.tables),
            "figures": len(self.figures),
            "formulas": len(self.formulas),
            "total_elements": len(self.tables) + len(self.figures) + len(self.formulas)
        }
    
    def get_elements_by_page(self, page_number: int) -> Dict[str, List]:
        """Get all elements from a specific page."""
        return {
            "tables": [t for t in self.tables if t.location.page == page_number],
            "figures": [f for f in self.figures if f.location.page == page_number],
            "formulas": [f for f in self.formulas if f.location.page == page_number]
        }
    
    def get_elements_by_section(self, section_name: str) -> Dict[str, List]:
        """Get all elements from a specific section."""
        section_lower = section_name.lower()
        return {
            "tables": [t for t in self.tables if section_lower in t.location.section.lower()],
            "figures": [f for f in self.figures if section_lower in f.location.section.lower()],
            "formulas": [f for f in self.formulas if section_lower in f.location.section.lower()]
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This paper presents a novel approach to machine learning...",
                "tables": [
                    {
                        "id": "table_1",
                        "caption": "Performance Comparison",
                        "markdown": "| Method | Accuracy |\n|--------|----------|\n| Ours | 95.2% |",
                        "location": {"page": 3, "section": "Results"}
                    }
                ],
                "figures": [
                    {
                        "id": "figure_1", 
                        "caption": "System Architecture",
                        "figure_type": "diagram",
                        "location": {"page": 2, "section": "Methodology"}
                    }
                ],
                "formulas": [
                    {
                        "id": "formula_1",
                        "latex": "y = wx + b",
                        "context": "Linear transformation",
                        "location": {"page": 1, "section": "Introduction"}
                    }
                ],
                "metadata": {
                    "total_pages": 8,
                    "processing_time": 45.2,
                    "document_type": "academic_paper"
                }
            }
        }


class DocumentInfo(BaseModel):
    """Enhanced document information with additional metadata."""
    
    id: str = Field(description="Unique document identifier")
    title: str = Field(description="Document title")
    type: str = Field(default="academic_paper", description="Document type")
    path: Optional[str] = Field(default=None, description="File path")
    
    # Enhanced metadata
    authors: List[str] = Field(default_factory=list, description="Document authors")
    doi: Optional[str] = Field(default=None, description="DOI if available")
    journal: Optional[str] = Field(default=None, description="Journal name")
    year: Optional[int] = Field(default=None, description="Publication year")
    abstract: Optional[str] = Field(default=None, description="Document abstract")
    keywords: List[str] = Field(default_factory=list, description="Document keywords")
    
    # Processing metadata
    processed_with_llamaparse: bool = Field(default=False, description="Whether processed with LlamaParse")
    processing_timestamp: Optional[str] = Field(default=None, description="When document was processed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "smith_2025_transformers",
                "title": "Attention Is All You Need: A Comprehensive Review",
                "type": "academic_paper",
                "path": "/papers/smith_2025.pdf",
                "authors": ["Jane Smith", "John Doe"],
                "doi": "10.1000/example.doi",
                "journal": "Journal of Machine Learning Research",
                "year": 2025,
                "abstract": "This paper reviews the transformer architecture...",
                "keywords": ["transformers", "attention", "neural networks"],
                "processed_with_llamaparse": True,
                "processing_timestamp": "2025-01-15T10:30:00Z"
            }
        }
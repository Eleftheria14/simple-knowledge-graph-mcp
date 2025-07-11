# API Reference

## Citation Extraction

### `extract_citation_info(pdf_path: str)`
Extract citation information from a PDF research paper.

**Parameters:**
- `pdf_path` (str): Path to the PDF file

**Returns:**
- Dict with keys: title, authors, journal, year, volume, pages, doi

**Example:**
```python
from src.citation_extractor import extract_citation_info

citation_info = extract_citation_info("paper.pdf")
print(citation_info['title'])
```

### `format_citations(citation_info: Dict)`
Format citation information in multiple academic styles.

**Parameters:**
- `citation_info` (Dict): Citation information from extract_citation_info

**Returns:**
- Dict with formatted citations: ACS, APA, BibTeX, Simple

**Example:**
```python
from src.citation_extractor import format_citations

citations = format_citations(citation_info)
print(citations['ACS'])
```

### `get_acs_citation(pdf_path: str)`
Quick function to get just the ACS formatted citation.

**Parameters:**
- `pdf_path` (str): Path to the PDF file

**Returns:**
- String with ACS formatted citation

## Database Operations

### `CitationDatabaseManager`
Main class for database operations.

**Methods:**
- `connect()`: Establish database connection
- `store_paper(paper: PaperRecord)`: Store paper in database
- `search_papers(**kwargs)`: Search stored papers
- `get_statistics()`: Get database statistics

**Example:**
```python
from src.database_manager import CitationDatabaseManager

with CitationDatabaseManager() as db:
    papers = db.search_papers(author="John Doe")
```

### `extract_and_store_citation(pdf_path: str)`
Extract citation and store in database.

**Parameters:**
- `pdf_path` (str): Path to PDF file
- `store_in_db` (bool): Whether to store in database (default: True)

**Returns:**
- Tuple of (citation_info, formatted_citations, paper_id)

## Search Functions

### `search_stored_citations(**kwargs)`
Search stored citations with various filters.

**Parameters:**
- `query` (str): Full-text search in titles
- `author` (str): Author name to search for
- `journal` (str): Journal name (partial match)
- `year_from` (int): Start year for range
- `year_to` (int): End year for range

**Example:**
```python
from src.enhanced_citation_extractor import search_stored_citations

search_stored_citations(author="Andrew White", year_from=2020)
```

## Configuration

### `get_database_config()`
Get database configuration from environment variables.

**Returns:**
- Dict with database connection parameters

**Example:**
```python
from config import get_database_config

config = get_database_config()
```
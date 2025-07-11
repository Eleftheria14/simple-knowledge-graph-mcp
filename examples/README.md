# Examples

This directory contains example files and scripts for the Scientific Paper Analyzer.

## Files

### `d4sc03921a.pdf`
Example research paper: "A review of large language models and autonomous agents in chemistry" 
- **Authors**: Mayk Caldas Ramos, Christopher J. Collison, Andrew D. White
- **Journal**: Chemical Science
- **Year**: 2024
- **DOI**: 10.1039/d4sc03921a

This paper is used for testing citation extraction and analysis functionality.

### `improved_citation_extractor.py`
Earlier version of the citation extractor with detailed debugging and analysis capabilities.

### `working_regex_patterns.py`
Collection of regex patterns that were developed and tested for citation extraction.

## Usage Examples

### Basic Citation Extraction
```python
from src import get_acs_citation

# Extract ACS citation from example paper
citation = get_acs_citation("examples/d4sc03921a.pdf")
print(citation)
```

### Database Storage
```python
from src import extract_and_store_citation

# Extract and store in database
citation_info, formatted_citations, paper_id = extract_and_store_citation(
    "examples/d4sc03921a.pdf"
)
print(f"Paper stored with ID: {paper_id}")
```

### Search Stored Papers
```python
from src import search_stored_citations

# Search by author
search_stored_citations(author="Andrew D. White")

# Search by journal
search_stored_citations(journal="Chemical Science")
```

## Testing Your Own Papers

1. Place your PDF files in this directory
2. Update the file path in the examples
3. Run the citation extraction:

```python
from src import display_and_store_citation

result = display_and_store_citation("examples/your_paper.pdf")
```

## Expected Output

When running citation extraction on the example paper, you should see:

```
📚 Extracting citation information from research paper...

📖 PAPER CITATION INFORMATION
======================================================================
🗄️ Database ID: 1
📊 Extraction Confidence: 1.00

🔍 EXTRACTED METADATA:
📌 Title: A review of large language models and autonomous agents in chemistry
📌 Authors: Mayk Caldas Ramos, Christopher J. Collison, Andrew D. White
📌 Journal: Chemical Science
📌 Year: 2024
📌 Doi: 10.1039/d4sc03921a

📝 FORMATTED CITATIONS:
--------------------------------------------------

🧪 ACS Style (American Chemical Society):
   Ramos, M. C.; Collison, C. J.; White, A. D. A review of large
   language models and autonomous agents in chemistry. Chemical
   Science 2024. DOI: 10.1039/d4sc03921a.
```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Ollama Setup (Required)
```bash
# Install required models for local LLM processing
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve
```

### Database Setup
```bash
# Start PostgreSQL with Docker (recommended)
docker run --name citations-db \
  -e POSTGRES_DB=scientific_papers \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Initialize database schema
psql -h localhost -U postgres -d scientific_papers -f database/database_setup.sql
```

### Running and Testing
```bash
# Start Jupyter notebooks for analysis
jupyter notebook

# Test citation extraction functionality
python -c "from src import get_acs_citation; print(get_acs_citation('examples/d4sc03921a.pdf'))"

# Verify database connection
python -c "from src import CitationDatabaseManager; CitationDatabaseManager().connect()"
```

## Code Architecture

### Core Components
- **`src/citation_extractor.py`**: Regex-based citation extraction engine optimized for academic papers
- **`src/enhanced_citation_extractor.py`**: Database-integrated extractor with confidence scoring and storage
- **`src/database_manager.py`**: PostgreSQL operations with full-text search and citation management
- **`config/database_config.py`**: Environment-based database configuration with fallback support

### Technical Stack
- **LangChain + Ollama**: Local LLM processing for privacy and offline capability
- **PostgreSQL**: Citation storage with JSONB formats and full-text search indexes
- **Context Preservation Strategy**: Optimized for Ollama's 32,768 token limit

### Database Schema
- **papers table**: Citation metadata with JSONB storage for multiple citation formats (ACS, APA, BibTeX)
- **paper_analyses table**: LLM analysis results with model tracking and timestamps
- **Full-text search**: PostgreSQL GIN indexes for efficient searching across titles and content

### Notebook Architecture
- **Maximum_Context_Scientific_Analyzer.ipynb**: Production analysis with database integration
- **Tutorial.ipynb**: Beginner introduction to LangChain and Ollama concepts
- **Scientific_Paper_Analyzer.ipynb**: Intermediate multi-stage processing pipeline

## Key Development Patterns

### Citation Processing Flow
1. PDF loading through PyPDFLoader with first 5000 characters extracted
2. Regex pattern matching for title, authors, journal, DOI extraction
3. Multi-format citation generation (ACS, APA, BibTeX, Simple)
4. Database storage with confidence scoring and duplicate detection

### Database Integration Pattern
Uses context managers for all database operations:
```python
with CitationDatabaseManager() as db:
    paper_id = db.store_paper(paper_record)
```

### LLM Analysis Strategy
- Maximum context preservation within token limits
- Section-based analysis for comprehensive coverage
- R&D-focused analysis prompts for scientific applications
- Model usage tracking and analysis metadata storage

## External Dependencies

### Required Services
- **Ollama server** must be running locally with llama3.1:8b and nomic-embed-text models
- **PostgreSQL database** (Docker setup provided in docs/database_setup_instructions.md)

### Model Configuration
- Primary model: llama3.1:8b (32,768 token context window)
- Embedding model: nomic-embed-text
- Temperature: 0.1 for analytical consistency
- Max prediction: 4,096 tokens

## Important Notes

### No Automated Testing
This codebase lacks formal test suites. Testing is performed manually through:
- Jupyter notebook execution with example papers
- Manual verification of citation extraction accuracy
- Database connection testing in module `__main__` blocks

### Performance Considerations
- Token limit optimization for Ollama processing
- Efficient database indexing for citation collections
- Context preservation strategies for long research papers
- JSONB storage for flexible citation format handling

### Citation Format Support
The system generates citations in multiple academic formats with regex patterns optimized for:
- Multi-line titles and complex author lists with superscripts
- Journal detection and DOI extraction
- Publication date prioritization over random years in text
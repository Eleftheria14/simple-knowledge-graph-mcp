# Installation Guide

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Eleftheria14/scientific-paper-analyzer.git
cd scientific-paper-analyzer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Database (Optional)
```bash
# Using Docker (recommended)
docker run --name citations-db \
  -e POSTGRES_DB=scientific_papers \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Create database schema
psql -h localhost -U postgres -d scientific_papers -f database/database_setup.sql
```

### 4. Set Up Ollama
```bash
# Install Ollama (visit https://ollama.ai)
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve
```

## Detailed Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, for citation storage)
- Ollama (for LLM analysis)

### Python Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Setup Options

**Option 1: Docker (Easiest)**
```bash
docker run --name citations-db \
  -e POSTGRES_DB=scientific_papers \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15
```

**Option 2: Local PostgreSQL**
```bash
# macOS
brew install postgresql
brew services start postgresql
createdb scientific_papers

# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb scientific_papers
```

### Environment Variables
Create a `.env` file (optional):
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/scientific_papers
```

### Verification
```bash
# Test citation extraction
python -c "from src import get_acs_citation; print(get_acs_citation('examples/d4sc03921a.pdf'))"

# Test database connection (if set up)
python -c "from src import CitationDatabaseManager; CitationDatabaseManager().connect()"
```

## Troubleshooting

### Import Errors
If you get import errors, add the project root to Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/scientific-paper-analyzer"
```

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps  # For Docker
brew services list | grep postgresql  # For macOS
sudo systemctl status postgresql  # For Linux
```

### Ollama Issues
```bash
# Check if Ollama is running
ollama list
ollama serve
```
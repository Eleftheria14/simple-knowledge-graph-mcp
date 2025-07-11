# PostgreSQL Database Setup for Citation Storage

This guide will help you set up a PostgreSQL database to store your extracted citations.

## 🛠️ Installation Options

### Option 1: Docker (Recommended - Easiest)

```bash
# Pull PostgreSQL image and run container
docker run --name citations-db \
  -e POSTGRES_DB=scientific_papers \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Verify it's running
docker ps
```

### Option 2: Local Installation

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
createdb scientific_papers
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb scientific_papers
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

## 🗄️ Database Setup

### 1. Install Python Dependencies

```bash
pip install psycopg2-binary sqlalchemy
```

### 2. Create Database Schema

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d scientific_papers

# Or run the schema file directly
psql -h localhost -U postgres -d scientific_papers -f database_setup.sql
```

### 3. Test Connection

```python
# Test the database connection
python database_manager.py
```

## 🔧 Configuration

### Default Connection Settings

The database manager uses these default settings:
```python
{
    'host': 'localhost',
    'database': 'scientific_papers',
    'user': 'postgres',
    'password': 'password',
    'port': 5432
}
```

### Custom Configuration

Create a `.env` file (optional):
```bash
# .env file
DATABASE_URL=postgresql://postgres:password@localhost:5432/scientific_papers

# Or individual settings
DB_HOST=localhost
DB_NAME=scientific_papers
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432
```

## 🚀 Usage Examples

### Basic Citation Storage

```python
from enhanced_citation_extractor import extract_and_store_citation

# Extract and store citation
pdf_path = "your_paper.pdf"
citation_info, formatted_citations, paper_id = extract_and_store_citation(pdf_path)

print(f"Paper stored with ID: {paper_id}")
```

### Search Stored Citations

```python
from enhanced_citation_extractor import search_stored_citations

# Search by author
search_stored_citations(author="Andrew D. White")

# Search by journal and year range
search_stored_citations(journal="Chemical Science", year_from=2020, year_to=2024)

# Full-text search in titles
search_stored_citations(query="machine learning")
```

### Database Statistics

```python
from enhanced_citation_extractor import get_database_statistics

get_database_statistics()
```

## 📊 Database Schema

### Papers Table
- `id`: Primary key
- `title`: Paper title
- `authors`: Array of author names
- `journal`: Journal name
- `year`: Publication year
- `volume`, `pages`: Publication details
- `doi`: Digital Object Identifier
- `citations`: JSONB with formatted citations (ACS, APA, BibTeX)
- `extraction_confidence`: Confidence score (0.0-1.0)
- `created_at`, `updated_at`: Timestamps

### Paper Analyses Table
- `id`: Primary key
- `paper_id`: Foreign key to papers
- `analysis_type`: Type of analysis
- `analysis_content`: LLM analysis text
- `model_used`: Which LLM model was used
- `context_tokens`: Number of tokens used
- `analysis_date`: When analysis was performed

## 🔍 Useful SQL Queries

### Find Papers by Author
```sql
SELECT * FROM papers WHERE 'Andrew D. White' = ANY(authors);
```

### Search by Journal and Year
```sql
SELECT title, authors, year 
FROM papers 
WHERE journal ILIKE '%chemical%' AND year BETWEEN 2020 AND 2024;
```

### Get Citation Formats
```sql
SELECT title, citations->>'ACS' as acs_citation FROM papers;
```

### Full-text Search
```sql
SELECT title, journal 
FROM papers 
WHERE to_tsvector('english', title) @@ plainto_tsquery('machine learning');
```

### Papers with Analysis Count
```sql
SELECT p.title, p.authors, COUNT(pa.id) as analysis_count
FROM papers p
LEFT JOIN paper_analyses pa ON p.id = pa.paper_id
GROUP BY p.id, p.title, p.authors;
```

## 🔧 Troubleshooting

### Connection Issues
```python
# Test basic connection
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    database="scientific_papers",
    user="postgres",
    password="password"
)
print("✅ Connection successful!")
```

### Common Errors

**Error: `database "scientific_papers" does not exist`**
```bash
createdb scientific_papers
```

**Error: `FATAL: password authentication failed`**
- Check your password in the connection parameters
- For Docker: make sure you used the same password when creating the container

**Error: `could not connect to server`**
- Make sure PostgreSQL is running
- For Docker: `docker start citations-db`
- For local: `brew services start postgresql` (macOS) or `sudo systemctl start postgresql` (Linux)

## 🎯 Next Steps

Once your database is set up:

1. **Update your notebook** to use the enhanced citation extractor
2. **Store existing papers** by running the extractor on your PDF collection
3. **Integrate with your analysis workflow** to automatically store LLM analyses
4. **Build queries** to find related papers and track your research

## 🔒 Security Notes

- Change default passwords in production
- Use environment variables for credentials
- Consider SSL connections for remote databases
- Regular backups recommended

---

**Ready to start storing citations!** 🎉
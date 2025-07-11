-- Scientific Paper Citation Database Schema
-- PostgreSQL database for storing extracted citations and paper metadata

-- Drop tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS paper_analyses CASCADE;
DROP TABLE IF EXISTS papers CASCADE;

-- Main papers table for citation storage
CREATE TABLE papers (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT[] NOT NULL DEFAULT '{}',  -- Array of author names
    journal VARCHAR(255),
    year INTEGER,
    volume VARCHAR(50),
    pages VARCHAR(50),
    doi VARCHAR(255) UNIQUE,
    pdf_path TEXT,
    
    -- Citation formats stored as JSONB for flexibility
    citations JSONB,
    
    -- Metadata
    extraction_method VARCHAR(100) DEFAULT 'citation_extractor',
    extraction_confidence DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Paper analyses table for storing LLM analysis results
CREATE TABLE paper_analyses (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL, -- 'comprehensive', 'summary', 'technical'
    analysis_content TEXT NOT NULL,
    
    -- Analysis metadata
    model_used VARCHAR(100),
    context_tokens INTEGER,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_papers_title ON papers USING GIN(to_tsvector('english', title));
CREATE INDEX idx_papers_authors ON papers USING GIN(authors);
CREATE INDEX idx_papers_journal ON papers(journal);
CREATE INDEX idx_papers_year ON papers(year);
CREATE INDEX idx_papers_doi ON papers(doi);
CREATE INDEX idx_papers_citations ON papers USING GIN(citations);

-- Full-text search index for paper content
CREATE INDEX idx_paper_analyses_content ON paper_analyses USING GIN(to_tsvector('english', analysis_content));

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_papers_updated_at 
    BEFORE UPDATE ON papers 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Sample queries for testing

-- Query 1: Find papers by author
-- SELECT * FROM papers WHERE 'Andrew D. White' = ANY(authors);

-- Query 2: Search by journal and year range
-- SELECT title, authors, year FROM papers 
-- WHERE journal ILIKE '%chemical%' AND year BETWEEN 2020 AND 2024;

-- Query 3: Get citation in specific format
-- SELECT title, citations->>'ACS' as acs_citation FROM papers;

-- Query 4: Full-text search in titles
-- SELECT title, journal FROM papers 
-- WHERE to_tsvector('english', title) @@ plainto_tsquery('machine learning');

-- Query 5: Papers with their analysis count
-- SELECT p.title, p.authors, COUNT(pa.id) as analysis_count
-- FROM papers p
-- LEFT JOIN paper_analyses pa ON p.id = pa.paper_id
-- GROUP BY p.id, p.title, p.authors;

COMMENT ON TABLE papers IS 'Scientific papers with extracted citation metadata';
COMMENT ON TABLE paper_analyses IS 'LLM-generated analyses of research papers';
COMMENT ON COLUMN papers.citations IS 'JSONB containing formatted citations in multiple styles (ACS, APA, BibTeX, etc.)';
COMMENT ON COLUMN papers.authors IS 'Array of author names extracted from the paper';
COMMENT ON COLUMN papers.extraction_confidence IS 'Confidence score (0.0-1.0) for citation extraction accuracy';
-- Add embedding support to existing database schema
-- Run this after the main database_setup.sql

-- Enable vector extension for PostgreSQL (if using pgvector)
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Add embeddings table for storing document chunk embeddings
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    
    -- Store embedding as JSONB array (compatible with all PostgreSQL versions)
    embedding_vector JSONB NOT NULL,
    embedding_model VARCHAR(100) DEFAULT 'nomic-embed-text',
    
    -- Metadata
    chunk_length INTEGER,
    relevance_score DECIMAL(5,4),
    section_type VARCHAR(100), -- 'abstract', 'methods', 'results', etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique chunks per paper
    UNIQUE(paper_id, chunk_index)
);

-- Add analysis results table for embedding-based analyses
CREATE TABLE IF NOT EXISTS embedding_analyses (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL, -- 'semantic_summary', 'comprehensive', etc.
    analysis_content TEXT NOT NULL,
    
    -- Analysis metadata
    model_used VARCHAR(100),
    embedding_model VARCHAR(100),
    chunks_used INTEGER,
    coverage_percent DECIMAL(5,2),
    avg_relevance_score DECIMAL(5,4),
    total_tokens INTEGER,
    analysis_goals TEXT[], -- Array of analysis objectives
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_embeddings_paper_id ON document_embeddings(paper_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_index ON document_embeddings(chunk_index);
CREATE INDEX IF NOT EXISTS idx_embeddings_section ON document_embeddings(section_type);
CREATE INDEX IF NOT EXISTS idx_embedding_analyses_paper_id ON embedding_analyses(paper_id);
CREATE INDEX IF NOT EXISTS idx_embedding_analyses_type ON embedding_analyses(analysis_type);

-- Add embedding-related columns to existing papers table
ALTER TABLE papers 
ADD COLUMN IF NOT EXISTS has_embeddings BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS total_chunks INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(100);

-- Comments for documentation
COMMENT ON TABLE document_embeddings IS 'Stores semantic embeddings for document chunks to enable similarity search';
COMMENT ON TABLE embedding_analyses IS 'Stores results from embedding-based semantic analysis';
COMMENT ON COLUMN document_embeddings.embedding_vector IS 'JSONB array storing the embedding vector for semantic similarity search';
COMMENT ON COLUMN embedding_analyses.coverage_percent IS 'Percentage of original document covered by selected relevant chunks';
COMMENT ON COLUMN embedding_analyses.avg_relevance_score IS 'Average cosine similarity score of chunks used in analysis';
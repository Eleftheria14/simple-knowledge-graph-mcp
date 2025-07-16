"""
Simple Configuration for GraphRAG MCP Toolkit

Core settings for PDF processing, citations, and MCP server.
"""

import os
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Model configuration"""
    llm_model: str = Field(default="llama3.1:8b", description="Local LLM model")
    embedding_model: str = Field(default="nomic-embed-text", description="Embedding model")
    temperature: float = Field(default=0.1, description="LLM temperature")
    max_context: int = Field(default=4096, description="Maximum context length")
    max_predict: int = Field(default=1024, description="Maximum prediction length")
    batch_size: int = Field(default=32, description="Embedding batch size")


class StorageConfig(BaseModel):
    """Storage configuration"""
    class ChromaDBConfig(BaseModel):
        persist_directory: str = Field(default="chroma_graph_db", description="ChromaDB path")
        collection_name: str = Field(default="graphrag_citations", description="Collection name")
    
    class Neo4jConfig(BaseModel):
        uri: str = Field(default="bolt://localhost:7687", description="Neo4j URI")
        username: str = Field(default="neo4j", description="Neo4j username")
        password: str = Field(default="password", description="Neo4j password")
        database: str = Field(default="neo4j", description="Neo4j database")
    
    chromadb: ChromaDBConfig = Field(default_factory=ChromaDBConfig)
    neo4j: Neo4jConfig = Field(default_factory=Neo4jConfig)


class ProcessingConfig(BaseModel):
    """Processing configuration"""
    chunk_size: int = Field(default=1000, description="Text chunk size")
    chunk_overlap: int = Field(default=200, description="Chunk overlap")
    processing_mode: str = Field(default="sequential", description="Processing mode")


class GraphRAGConfig(BaseModel):
    """Simple configuration for GraphRAG MCP Toolkit"""
    
    model: ModelConfig = Field(default_factory=ModelConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    
    # Citation settings
    default_citation_style: Literal["APA", "IEEE", "Nature", "MLA"] = Field(
        default="APA", 
        description="Default citation style"
    )
    
    # MCP settings
    mcp_server_name: str = Field(default="GraphRAG Research Assistant", description="MCP server name")
    
    @classmethod
    def from_env(cls) -> "GraphRAGConfig":
        """Load configuration from environment variables"""
        return cls(
            model=ModelConfig(
                llm_model=os.getenv("GRAPHRAG_LLM_MODEL", "llama3.1:8b"),
                embedding_model=os.getenv("GRAPHRAG_EMBEDDING_MODEL", "nomic-embed-text"),
                temperature=float(os.getenv("GRAPHRAG_TEMPERATURE", "0.1")),
                max_context=int(os.getenv("GRAPHRAG_MAX_CONTEXT", "4096")),
                max_predict=int(os.getenv("GRAPHRAG_MAX_PREDICT", "1024")),
                batch_size=int(os.getenv("GRAPHRAG_BATCH_SIZE", "32"))
            ),
            storage=StorageConfig(
                chromadb=StorageConfig.ChromaDBConfig(
                    persist_directory=os.getenv("GRAPHRAG_CHROMADB_PATH", "chroma_graph_db"),
                    collection_name=os.getenv("GRAPHRAG_CHROMADB_COLLECTION", "graphrag_citations")
                ),
                neo4j=StorageConfig.Neo4jConfig(
                    uri=os.getenv("GRAPHRAG_NEO4J_URI", "bolt://localhost:7687"),
                    username=os.getenv("GRAPHRAG_NEO4J_USER", "neo4j"),
                    password=os.getenv("GRAPHRAG_NEO4J_PASSWORD", "password"),
                    database=os.getenv("GRAPHRAG_NEO4J_DATABASE", "neo4j")
                )
            ),
            processing=ProcessingConfig(
                chunk_size=int(os.getenv("GRAPHRAG_CHUNK_SIZE", "1000")),
                chunk_overlap=int(os.getenv("GRAPHRAG_CHUNK_OVERLAP", "200")),
                processing_mode=os.getenv("GRAPHRAG_PROCESSING_MODE", "sequential")
            ),
            default_citation_style=os.getenv("GRAPHRAG_CITATION_STYLE", "APA"),
            mcp_server_name=os.getenv("GRAPHRAG_MCP_SERVER_NAME", "GraphRAG Research Assistant")
        )
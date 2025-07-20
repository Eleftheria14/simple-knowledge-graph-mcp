"""Simple configuration for knowledge graph MCP."""
import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# ChromaDB Configuration  
# Use absolute path relative to project root to avoid working directory issues
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMADB_PATH = os.getenv("CHROMADB_PATH", os.path.join(_project_root, "chroma_db"))
CHROMADB_COLLECTION = os.getenv("CHROMADB_COLLECTION", "knowledge_graph")

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

# Citation Styles
CITATION_STYLES = ["APA", "IEEE", "Nature", "MLA"]
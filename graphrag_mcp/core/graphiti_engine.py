#!/usr/bin/env python3
"""
Graphiti-based Knowledge Graph Engine
Replaces NetworkX with Graphiti for real-time, persistent knowledge graphs
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import json
from pathlib import Path

# Graphiti core imports
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.llm_client import OpenAIClient, LLMConfig
from graphiti_core.embedder import OpenAIEmbedder, OpenAIEmbedderConfig

# LangChain imports for document processing
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class GraphitiKnowledgeGraph:
    """
    Advanced knowledge graph system using Graphiti and Neo4j
    Provides real-time, persistent knowledge graphs for document analysis
    """
    
    def __init__(self, 
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j", 
                 neo4j_password: str = "password",
                 ollama_base_url: str = "http://localhost:11434/v1",
                 llm_model: str = "llama3.1:8b",
                 embedding_model: str = "nomic-embed-text"):
        """
        Initialize Graphiti knowledge graph engine
        
        Args:
            neo4j_uri: Neo4j database connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            ollama_base_url: Ollama API base URL
            llm_model: LLM model name for analysis
            embedding_model: Embedding model name
        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.ollama_base_url = ollama_base_url
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        
        # Initialize Graphiti components
        self.graphiti = None
        self.llm_client = None
        self.embedder = None
        
        # Document processing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Track processed documents
        self.processed_documents = {}
        
        logger.info(f"Initialized GraphitiKnowledgeGraph with Neo4j: {neo4j_uri}")
    
    async def initialize(self):
        """Initialize Graphiti connection and components"""
        try:
            # Set environment variables for OpenAI client compatibility
            import os
            os.environ['OPENAI_API_KEY'] = 'ollama'
            os.environ['OPENAI_BASE_URL'] = self.ollama_base_url
            
            # Create LLM configuration for Ollama
            llm_config = LLMConfig(
                api_key='ollama',
                base_url=self.ollama_base_url,
                model=self.llm_model,
                small_model=self.llm_model,
                temperature=0.1,
                max_tokens=4096
            )
            
            # Create LLM client
            self.llm_client = OpenAIClient(llm_config)
            
            # Create embedder configuration
            embedder_config = OpenAIEmbedderConfig(
                api_key='ollama',
                base_url=self.ollama_base_url,
                embedding_model=self.embedding_model
            )
            
            # Create embedder client
            self.embedder = OpenAIEmbedder(embedder_config)
            
            # Initialize Graphiti
            self.graphiti = Graphiti(
                uri=self.neo4j_uri,
                user=self.neo4j_user,
                password=self.neo4j_password,
                llm_client=self.llm_client,
                embedder=self.embedder
            )
            
            # Build database indices and constraints
            await self.graphiti.build_indices_and_constraints()
            
            logger.info("✅ Graphiti knowledge graph initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Graphiti: {e}")
            return False
    
    async def add_document(self, 
                          document_content: str,
                          document_id: str,
                          metadata: Dict[str, Any] = None,
                          source_description: str = "Academic paper") -> bool:
        """
        Add a document to the knowledge graph
        
        Args:
            document_content: Full text content of the document
            document_id: Unique identifier for the document
            metadata: Additional metadata (title, authors, etc.)
            source_description: Description of the document source
            
        Returns:
            bool: Success status
        """
        try:
            if not self.graphiti:
                await self.initialize()
            
            # Split document into chunks for processing
            chunks = self.text_splitter.split_text(document_content)
            
            # Process each chunk as an episode
            for i, chunk in enumerate(chunks):
                episode_name = f"{document_id}_chunk_{i}"
                
                # Create episode with metadata
                episode_body = {
                    "content": chunk,
                    "document_id": document_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "metadata": metadata or {}
                }
                
                # Add episode to Graphiti
                await self.graphiti.add_episode(
                    name=episode_name,
                    episode_body=json.dumps(episode_body),
                    source=EpisodeType.json,
                    source_description=f"{source_description} - Chunk {i+1}/{len(chunks)}",
                    reference_time=datetime.now()
                )
            
            # Track processed document
            self.processed_documents[document_id] = {
                "chunks": len(chunks),
                "metadata": metadata,
                "processed_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Added document {document_id} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add document {document_id}: {e}")
            return False
    
    async def search_knowledge_graph(self, 
                                   query: str,
                                   max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search the knowledge graph for relevant content
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with content and metadata
        """
        try:
            if not self.graphiti:
                await self.initialize()
            
            # Perform hybrid search using Graphiti
            search_results = await self.graphiti.search(query=query)
            
            # Process and format results
            formatted_results = []
            for result in search_results[:max_results]:
                # Handle different result types from Graphiti
                if hasattr(result, 'episode_body'):
                    # Episode result
                    try:
                        episode_data = json.loads(result.episode_body)
                        formatted_result = {
                            "content": episode_data.get("content", result.episode_body),
                            "document_id": episode_data.get("document_id"),
                            "chunk_index": episode_data.get("chunk_index"),
                            "metadata": episode_data.get("metadata", {}),
                            "episode_name": getattr(result, 'name', 'Unknown'),
                            "created_at": result.created_at.isoformat() if hasattr(result, 'created_at') and result.created_at else None,
                            "score": getattr(result, 'score', None),
                            "result_type": "episode"
                        }
                    except json.JSONDecodeError:
                        # Handle plain text episodes
                        formatted_result = {
                            "content": result.episode_body,
                            "document_id": None,
                            "chunk_index": None,
                            "metadata": {},
                            "episode_name": getattr(result, 'name', 'Unknown'),
                            "created_at": result.created_at.isoformat() if hasattr(result, 'created_at') and result.created_at else None,
                            "score": getattr(result, 'score', None),
                            "result_type": "episode"
                        }
                elif hasattr(result, 'name'):
                    # Entity result
                    formatted_result = {
                        "content": getattr(result, 'summary', result.name),
                        "document_id": None,
                        "chunk_index": None,
                        "metadata": {},
                        "episode_name": result.name,
                        "created_at": result.created_at.isoformat() if hasattr(result, 'created_at') and result.created_at else None,
                        "score": getattr(result, 'score', None),
                        "result_type": "entity"
                    }
                else:
                    # Unknown result type
                    formatted_result = {
                        "content": str(result),
                        "document_id": None,
                        "chunk_index": None,
                        "metadata": {},
                        "episode_name": "Unknown",
                        "created_at": None,
                        "score": getattr(result, 'score', None),
                        "result_type": "unknown"
                    }
                
                formatted_results.append(formatted_result)
            
            logger.info(f"🔍 Search for '{query}' returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Search failed for query '{query}': {e}")
            return []
    
    async def get_entity_relationships(self, entity_name: str) -> List[Dict[str, Any]]:
        """
        Get relationships for a specific entity
        
        Args:
            entity_name: Name of the entity to find relationships for
            
        Returns:
            List of relationships with connected entities
        """
        try:
            if not self.graphiti:
                await self.initialize()
            
            # Search for the entity
            entity_results = await self.graphiti.search(query=entity_name)
            
            relationships = []
            for result in entity_results:
                # Get related entities through graph traversal
                # This is a simplified implementation - Graphiti provides more advanced graph queries
                relationships.append({
                    "source_entity": entity_name,
                    "related_content": result.episode_body,
                    "relationship_type": "mentioned_in",
                    "episode_name": result.name,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                })
            
            logger.info(f"🔗 Found {len(relationships)} relationships for '{entity_name}'")
            return relationships
            
        except Exception as e:
            logger.error(f"❌ Failed to get relationships for '{entity_name}': {e}")
            return []
    
    async def get_document_summary(self, document_id: str) -> Dict[str, Any]:
        """
        Get summary information for a processed document
        
        Args:
            document_id: Unique document identifier
            
        Returns:
            Dictionary with document summary information
        """
        try:
            if document_id not in self.processed_documents:
                return {"error": f"Document {document_id} not found"}
            
            doc_info = self.processed_documents[document_id]
            
            # Search for all chunks of this document
            search_results = await self.search_knowledge_graph(
                query=f"document_id:{document_id}",
                max_results=doc_info["chunks"]
            )
            
            # Extract entities and concepts from search results
            entities = set()
            concepts = set()
            
            for result in search_results:
                # Simple entity extraction from content
                # In production, this would use more sophisticated NLP
                content = result.get("content", "")
                # Add basic entity extraction logic here
                
            return {
                "document_id": document_id,
                "chunks_processed": doc_info["chunks"],
                "processed_at": doc_info["processed_at"],
                "metadata": doc_info["metadata"],
                "entities_found": len(entities),
                "concepts_found": len(concepts),
                "total_content_length": sum(len(r.get("content", "")) for r in search_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get summary for document {document_id}: {e}")
            return {"error": str(e)}
    
    async def get_knowledge_graph_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph
        
        Returns:
            Dictionary with graph statistics
        """
        try:
            if not self.graphiti:
                await self.initialize()
            
            # Get basic statistics
            stats = {
                "total_documents": len(self.processed_documents),
                "total_chunks": sum(doc["chunks"] for doc in self.processed_documents.values()),
                "neo4j_uri": self.neo4j_uri,
                "llm_model": self.llm_model,
                "embedding_model": self.embedding_model,
                "last_updated": datetime.now().isoformat()
            }
            
            # Add document processing summary
            if self.processed_documents:
                stats["documents"] = [
                    {
                        "document_id": doc_id,
                        "chunks": doc_info["chunks"],
                        "processed_at": doc_info["processed_at"],
                        "title": doc_info["metadata"].get("title", "Unknown")
                    }
                    for doc_id, doc_info in self.processed_documents.items()
                ]
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get knowledge graph stats: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close Graphiti connection"""
        try:
            if self.graphiti:
                await self.graphiti.close()
                logger.info("✅ Graphiti connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Graphiti connection: {e}")

# Factory function for easy initialization
async def create_graphiti_knowledge_graph(**kwargs) -> GraphitiKnowledgeGraph:
    """
    Create and initialize a Graphiti knowledge graph
    
    Args:
        **kwargs: Configuration parameters for GraphitiKnowledgeGraph
        
    Returns:
        Initialized GraphitiKnowledgeGraph instance
    """
    kg = GraphitiKnowledgeGraph(**kwargs)
    await kg.initialize()
    return kg

# Example usage
async def main():
    """Example usage of GraphitiKnowledgeGraph"""
    
    # Initialize knowledge graph
    kg = await create_graphiti_knowledge_graph()
    
    # Add a test document
    test_content = """
    This is a research paper about machine learning for drug discovery.
    The paper discusses graph neural networks and their application to molecular property prediction.
    Key findings include improved accuracy using transformer-based architectures.
    """
    
    await kg.add_document(
        document_content=test_content,
        document_id="test_paper_001",
        metadata={
            "title": "ML for Drug Discovery",
            "authors": ["Dr. Smith", "Dr. Johnson"],
            "year": 2024
        }
    )
    
    # Search the knowledge graph
    results = await kg.search_knowledge_graph("machine learning")
    print(f"Search results: {len(results)}")
    
    # Get document summary
    summary = await kg.get_document_summary("test_paper_001")
    print(f"Document summary: {summary}")
    
    # Get graph statistics
    stats = await kg.get_knowledge_graph_stats()
    print(f"Graph stats: {stats}")
    
    # Close connection
    await kg.close()

if __name__ == "__main__":
    asyncio.run(main())
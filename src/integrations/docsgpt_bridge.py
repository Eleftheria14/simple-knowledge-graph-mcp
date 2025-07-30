"""
DocsGPT Integration Bridge

This module provides the abstraction layer to integrate our n8n + MCP knowledge graph system 
with DocsGPT's UI components. It implements DocsGPT's BaseRetriever interface while using
our superior knowledge graph backend.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Generator
from abc import ABC, abstractmethod

# DocsGPT's abstract interfaces (would be imported from their codebase)
class BaseRetriever(ABC):
    """DocsGPT's base retriever interface"""
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod 
    def gen(self, query: str, retriever=None, **kwargs) -> Generator[Dict[str, Any], None, None]:
        pass
    
    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        pass

# Our implementation
class KnowledgeGraphRetriever(BaseRetriever):
    """
    Knowledge Graph Retriever that bridges DocsGPT UI with our n8n + MCP system.
    
    This class implements DocsGPT's BaseRetriever interface but routes all requests
    to our n8n workflows which use MCP tools for Neo4j + ChromaDB operations.
    """
    
    def __init__(self, 
                 n8n_base_url: str = "http://localhost:5678",
                 webhook_path: str = "webhook/docsgpt-integration",
                 chunks: int = 5,
                 max_results: int = 10):
        self.n8n_webhook_url = f"{n8n_base_url}/{webhook_path}"
        self.chunks = chunks
        self.max_results = max_results
        self.logger = logging.getLogger(__name__)
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search our knowledge graph via n8n workflow.
        
        Args:
            query: Search query string
            **kwargs: Additional parameters from DocsGPT (chunks, etc.)
            
        Returns:
            List of document chunks with metadata in DocsGPT format:
            [
                {
                    "text": "chunk content",
                    "source": "document_name.pdf", 
                    "page": 1,
                    "score": 0.95
                }
            ]
        """
        try:
            payload = {
                "action": "search",
                "query": query,
                "chunks": kwargs.get("chunks", self.chunks),
                "max_results": self.max_results,
                "source": "docsgpt_ui"
            }
            
            response = requests.post(
                self.n8n_webhook_url, 
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            results = response.json()
            
            # Transform our knowledge graph results to DocsGPT format
            formatted_results = []
            for result in results.get("documents", []):
                formatted_results.append({
                    "text": result.get("content", ""),
                    "source": result.get("source", "Unknown"),
                    "page": result.get("page", 1),
                    "score": result.get("similarity_score", 0.0),
                    # Additional metadata from our knowledge graph
                    "entities": result.get("entities", []),
                    "relationships": result.get("relationships", [])
                })
            
            self.logger.info(f"Knowledge graph search returned {len(formatted_results)} results")
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error calling n8n webhook: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error in knowledge graph search: {e}")
            return []
    
    def gen(self, query: str, retriever=None, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Generate streaming response using our knowledge graph system.
        
        This method streams responses in DocsGPT's expected format:
        - {"answer": "partial text"} for streaming answers
        - {"sources": [...]} for source documents
        - {"tool_calls": [...]} for tool usage
        - {"thought": "reasoning"} for agent thinking
        
        Args:
            query: User query
            retriever: Unused (we are the retriever)
            **kwargs: Additional parameters
            
        Yields:
            Dict[str, Any]: Streaming response chunks in DocsGPT format
        """
        try:
            payload = {
                "action": "generate_answer",
                "query": query,
                "chat_history": kwargs.get("chat_history", []),
                "chunks": kwargs.get("chunks", self.chunks),
                "max_results": self.max_results,
                "source": "docsgpt_ui",
                "stream": True
            }
            
            # Make streaming request to n8n workflow
            response = requests.post(
                self.n8n_webhook_url,
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            # First, yield the sources we found
            search_results = self.search(query, **kwargs)
            if search_results:
                yield {"sources": search_results}
            
            # Then stream the generated answer
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        
                        if "answer" in data:
                            yield {"answer": data["answer"]}
                        elif "thought" in data:
                            yield {"thought": data["thought"]}
                        elif "tool_calls" in data:
                            yield {"tool_calls": data["tool_calls"]}
                        elif "error" in data:
                            self.logger.error(f"Error in knowledge graph generation: {data['error']}")
                            yield {"answer": f"Error: {data['error']}"}
                        
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error in streaming generation: {e}")
            yield {"answer": f"Error connecting to knowledge graph: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Unexpected error in generation: {e}")
            yield {"answer": f"Unexpected error: {str(e)}"}
    
    def get_params(self) -> Dict[str, Any]:
        """
        Return retriever parameters for DocsGPT's logging/analytics.
        
        Returns:
            Dict with retriever configuration
        """
        return {
            "retriever_type": "knowledge_graph",
            "backend": "n8n_mcp",
            "vector_store": "chromadb", 
            "graph_store": "neo4j",
            "chunks": self.chunks,
            "max_results": self.max_results,
            "webhook_url": self.n8n_webhook_url
        }


class DocumentProcessor:
    """
    Handle document uploads and processing through our n8n + MCP system.
    
    This class intercepts DocsGPT's document uploads and routes them to our
    n8n workflows for processing with our knowledge graph tools.
    """
    
    def __init__(self, n8n_base_url: str = "http://localhost:5678"):
        self.n8n_webhook_url = f"{n8n_base_url}/webhook/docsgpt-document-upload"
        self.logger = logging.getLogger(__name__)
    
    def process_document(self, 
                        file_content: bytes, 
                        filename: str, 
                        user_id: str,
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process uploaded document through our knowledge graph system.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            user_id: User identifier
            metadata: Additional document metadata
            
        Returns:
            Processing result with status and document ID
        """
        try:
            # Prepare document for n8n processing
            payload = {
                "action": "process_document",
                "filename": filename,
                "user_id": user_id,
                "metadata": metadata or {},
                "source": "docsgpt_ui"
            }
            
            # Send to n8n workflow with file content
            files = {"document": (filename, file_content)}
            response = requests.post(
                self.n8n_webhook_url,
                data={"payload": json.dumps(payload)},
                files=files,
                timeout=300  # 5 minute timeout for document processing
            )
            response.raise_for_status()
            
            result = response.json()
            
            self.logger.info(f"Document {filename} processed successfully")
            return {
                "success": True,
                "document_id": result.get("document_id"),
                "entities_extracted": result.get("entities_count", 0),
                "chunks_created": result.get("chunks_count", 0),
                "processing_time": result.get("processing_time", 0)
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error processing document {filename}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Unexpected error processing document {filename}: {e}")
            return {
                "success": False, 
                "error": str(e)
            }


def create_docsgpt_retriever(**kwargs) -> KnowledgeGraphRetriever:
    """
    Factory function to create our knowledge graph retriever.
    
    This function should be used to replace DocsGPT's RetrieverCreator.create_retriever()
    calls throughout their codebase.
    
    Args:
        **kwargs: Configuration parameters
        
    Returns:
        KnowledgeGraphRetriever instance configured for DocsGPT integration
    """
    return KnowledgeGraphRetriever(
        n8n_base_url=kwargs.get("n8n_base_url", "http://localhost:5678"),
        webhook_path=kwargs.get("webhook_path", "webhook/docsgpt-integration"),
        chunks=kwargs.get("chunks", 5),
        max_results=kwargs.get("max_results", 10)
    )
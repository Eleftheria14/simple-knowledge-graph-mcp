"""
Embedding Service for Context-Aware Vector Generation

Uses nomic-embed-text directly (not through Ollama) to generate embeddings
from entity-enriched text chunks. This provides better accuracy because
the embeddings understand the entity context.
"""

import logging
import time
from typing import List, Optional, Dict, Any
import numpy as np
from dataclasses import dataclass

from langchain_ollama import OllamaEmbeddings
from ..utils.error_handling import ProcessingError

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result from embedding generation"""
    embeddings: np.ndarray
    texts: List[str]
    processing_time: float
    embedding_model: str
    context_aware: bool = True
    metadata: Dict[str, Any] = None


class EmbeddingService:
    """
    Context-aware embedding service using nomic-embed-text.
    
    This service generates embeddings from entity-enriched text chunks
    rather than raw text, providing better semantic understanding
    for retrieval accuracy.
    """
    
    def __init__(self, 
                 embedding_model: str = "nomic-embed-text",
                 batch_size: int = 10,
                 max_retries: int = 3):
        """
        Initialize embedding service.
        
        Args:
            embedding_model: Model identifier for nomic-embed-text
            batch_size: Batch size for processing
            max_retries: Maximum retry attempts
        """
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        self.max_retries = max_retries
        
        # Initialize embedding model
        try:
            self.embeddings = OllamaEmbeddings(model=embedding_model)
            logger.info(f"🔢 Embedding Service initialized with {embedding_model}")
        except Exception as e:
            raise ProcessingError(f"Failed to initialize embedding model: {e}")
        
        # Service statistics
        self.stats = {
            "total_embeddings_generated": 0,
            "total_texts_processed": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "failed_generations": 0,
            "context_aware_embeddings": 0
        }
    
    def generate_context_aware_embeddings(self, 
                                        enhanced_texts: List[str],
                                        metadata: Optional[Dict[str, Any]] = None) -> EmbeddingResult:
        """
        Generate context-aware embeddings from enhanced text chunks.
        
        Args:
            enhanced_texts: List of entity-enriched text chunks
            metadata: Optional metadata about the texts
            
        Returns:
            EmbeddingResult with embeddings and metadata
        """
        if not enhanced_texts:
            raise ValueError("No texts provided for embedding generation")
        
        logger.info(f"🔢 Generating context-aware embeddings for {len(enhanced_texts)} texts")
        start_time = time.time()
        
        try:
            # Generate embeddings with retry logic
            embeddings = self._generate_embeddings_with_retry(enhanced_texts)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(len(enhanced_texts), processing_time, context_aware=True)
            
            result = EmbeddingResult(
                embeddings=embeddings,
                texts=enhanced_texts,
                processing_time=processing_time,
                embedding_model=self.embedding_model,
                context_aware=True,
                metadata=metadata or {}
            )
            
            logger.info(f"✅ Generated {len(embeddings)} context-aware embeddings in {processing_time:.2f}s")
            logger.info(f"   📊 Shape: {embeddings.shape}")
            logger.info(f"   🧠 Model: {self.embedding_model}")
            
            return result
            
        except Exception as e:
            self.stats["failed_generations"] += 1
            logger.error(f"❌ Context-aware embedding generation failed: {e}")
            raise ProcessingError(f"Embedding generation failed: {e}")
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query string.
        
        Args:
            query: Query string
            
        Returns:
            Query embedding as numpy array
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        logger.info(f"🔍 Generating query embedding for: {query[:100]}...")
        start_time = time.time()
        
        try:
            # Generate query embedding
            embedding = self._generate_query_embedding_with_retry(query)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(1, processing_time, context_aware=False)
            
            logger.info(f"✅ Generated query embedding in {processing_time:.2f}s")
            return embedding
            
        except Exception as e:
            self.stats["failed_generations"] += 1
            logger.error(f"❌ Query embedding generation failed: {e}")
            raise ProcessingError(f"Query embedding generation failed: {e}")
    
    def generate_batch_embeddings(self, 
                                 texts: List[str],
                                 batch_size: Optional[int] = None) -> EmbeddingResult:
        """
        Generate embeddings in batches for large text collections.
        
        Args:
            texts: List of texts to embed
            batch_size: Override default batch size
            
        Returns:
            EmbeddingResult with all embeddings
        """
        if not texts:
            raise ValueError("No texts provided for batch embedding")
        
        batch_size = batch_size or self.batch_size
        logger.info(f"🔢 Generating batch embeddings for {len(texts)} texts (batch size: {batch_size})")
        
        start_time = time.time()
        all_embeddings = []
        
        try:
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                logger.info(f"   Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                
                batch_embeddings = self._generate_embeddings_with_retry(batch_texts)
                all_embeddings.extend(batch_embeddings)
                
                # Small delay between batches to avoid overwhelming the model
                if i + batch_size < len(texts):
                    time.sleep(0.1)
            
            # Combine all embeddings
            combined_embeddings = np.array(all_embeddings)
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(len(texts), processing_time, context_aware=False)
            
            result = EmbeddingResult(
                embeddings=combined_embeddings,
                texts=texts,
                processing_time=processing_time,
                embedding_model=self.embedding_model,
                context_aware=False,
                metadata={"batch_size": batch_size, "total_batches": len(texts) // batch_size + 1}
            )
            
            logger.info(f"✅ Generated {len(combined_embeddings)} batch embeddings in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.stats["failed_generations"] += 1
            logger.error(f"❌ Batch embedding generation failed: {e}")
            raise ProcessingError(f"Batch embedding generation failed: {e}")
    
    def _generate_embeddings_with_retry(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings with retry logic.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Embeddings as numpy array
        """
        for attempt in range(self.max_retries):
            try:
                embeddings = self.embeddings.embed_documents(texts)
                
                if not embeddings:
                    raise ProcessingError("No embeddings returned from model")
                
                # Validate embeddings
                embeddings_array = np.array(embeddings)
                if embeddings_array.shape[0] != len(texts):
                    raise ProcessingError(f"Embedding count mismatch: {embeddings_array.shape[0]} vs {len(texts)}")
                
                return embeddings_array
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ProcessingError(f"Failed to generate embeddings after {self.max_retries} attempts: {e}")
                
                logger.warning(f"Embedding generation attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise ProcessingError("Should not reach here")
    
    def _generate_query_embedding_with_retry(self, query: str) -> np.ndarray:
        """
        Generate query embedding with retry logic.
        
        Args:
            query: Query string
            
        Returns:
            Query embedding as numpy array
        """
        for attempt in range(self.max_retries):
            try:
                embedding = self.embeddings.embed_query(query)
                
                if not embedding:
                    raise ProcessingError("No embedding returned for query")
                
                return np.array(embedding)
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ProcessingError(f"Failed to generate query embedding after {self.max_retries} attempts: {e}")
                
                logger.warning(f"Query embedding attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise ProcessingError("Should not reach here")
    
    def _update_stats(self, text_count: int, processing_time: float, context_aware: bool = False):
        """Update service statistics"""
        self.stats["total_embeddings_generated"] += text_count
        self.stats["total_texts_processed"] += text_count
        self.stats["total_processing_time"] += processing_time
        
        if context_aware:
            self.stats["context_aware_embeddings"] += text_count
        
        # Update average processing time
        total_calls = self.stats["total_embeddings_generated"]
        if total_calls > 0:
            self.stats["average_processing_time"] = self.stats["total_processing_time"] / total_calls
    
    def compute_similarity(self, 
                          embedding1: np.ndarray,
                          embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score
        """
        try:
            # Ensure embeddings are 1D
            if embedding1.ndim > 1:
                embedding1 = embedding1.flatten()
            if embedding2.ndim > 1:
                embedding2 = embedding2.flatten()
            
            # Compute cosine similarity
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            return 0.0
    
    def find_most_similar(self, 
                         query_embedding: np.ndarray,
                         document_embeddings: np.ndarray,
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find most similar documents to a query.
        
        Args:
            query_embedding: Query embedding
            document_embeddings: Document embeddings matrix
            top_k: Number of results to return
            
        Returns:
            List of similarity results with indices and scores
        """
        try:
            # Compute similarities
            similarities = []
            for i, doc_embedding in enumerate(document_embeddings):
                similarity = self.compute_similarity(query_embedding, doc_embedding)
                similarities.append({
                    "index": i,
                    "similarity": similarity
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return top k results
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def validate_embeddings(self, embeddings: np.ndarray) -> Dict[str, Any]:
        """
        Validate embeddings quality and consistency.
        
        Args:
            embeddings: Embeddings to validate
            
        Returns:
            Validation report
        """
        try:
            validation_report = {
                "valid": True,
                "shape": embeddings.shape,
                "dtype": str(embeddings.dtype),
                "has_nan": bool(np.isnan(embeddings).any()),
                "has_inf": bool(np.isinf(embeddings).any()),
                "mean_norm": float(np.mean(np.linalg.norm(embeddings, axis=1))),
                "std_norm": float(np.std(np.linalg.norm(embeddings, axis=1))),
                "dimension": embeddings.shape[1] if embeddings.ndim > 1 else embeddings.shape[0]
            }
            
            # Check for issues
            if validation_report["has_nan"] or validation_report["has_inf"]:
                validation_report["valid"] = False
                validation_report["issues"] = []
                if validation_report["has_nan"]:
                    validation_report["issues"].append("Contains NaN values")
                if validation_report["has_inf"]:
                    validation_report["issues"].append("Contains infinite values")
            
            # Check expected dimension for nomic-embed-text (384 dimensions)
            if validation_report["dimension"] != 768:  # nomic-embed-text uses 768 dimensions
                validation_report["dimension_warning"] = f"Expected 768 dimensions, got {validation_report['dimension']}"
            
            return validation_report
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        return {
            **self.stats,
            "model_info": {
                "embedding_model": self.embedding_model,
                "batch_size": self.batch_size,
                "max_retries": self.max_retries
            },
            "performance_metrics": {
                "embeddings_per_second": (
                    self.stats["total_embeddings_generated"] / self.stats["total_processing_time"]
                    if self.stats["total_processing_time"] > 0 else 0
                ),
                "context_aware_percentage": (
                    self.stats["context_aware_embeddings"] / self.stats["total_embeddings_generated"] * 100
                    if self.stats["total_embeddings_generated"] > 0 else 0
                )
            }
        }
    
    def clear_statistics(self):
        """Clear service statistics"""
        self.stats = {
            "total_embeddings_generated": 0,
            "total_texts_processed": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "failed_generations": 0,
            "context_aware_embeddings": 0
        }
        logger.info("🔄 Service statistics cleared")


# Factory function for easy initialization
def create_embedding_service(embedding_model: str = "nomic-embed-text",
                           batch_size: int = 10) -> EmbeddingService:
    """Create embedding service with default settings"""
    return EmbeddingService(
        embedding_model=embedding_model,
        batch_size=batch_size
    )
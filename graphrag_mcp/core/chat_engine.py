"""
Chat Engine for GraphRAG MCP Toolkit

Domain-agnostic chat interface combining RAG and Knowledge Graph capabilities.
Extracted and refactored from UnifiedPaperChat to support multiple domains.
"""

from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path

# Core components
from .document_processor import DocumentProcessor, DocumentData
from .ollama_engine import OllamaEngine

# Configuration
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ChatConfig(BaseModel):
    """Configuration for chat engine"""
    enable_graph_mode: bool = Field(default=True, description="Enable knowledge graph integration")
    enable_rag_mode: bool = Field(default=True, description="Enable RAG queries")
    auto_mode_routing: bool = Field(default=True, description="Automatic query routing")
    max_chat_history: int = Field(default=100, description="Maximum chat history entries")
    default_top_k: int = Field(default=5, description="Default number of chunks to retrieve")


class ChatResponse(BaseModel):
    """Structured chat response"""
    answer: str = Field(description="Generated answer")
    mode: str = Field(description="Processing mode used")
    source: str = Field(description="Information source")
    confidence: str = Field(default="medium", description="Response confidence")
    entities: Optional[List[str]] = Field(default=None, description="Related entities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error: Optional[str] = Field(default=None, description="Error message if any")


class ChatEngine:
    """
    Domain-agnostic chat interface combining RAG and Knowledge Graph.
    
    Provides intelligent routing between different query modes based on
    content analysis and domain configuration.
    """
    
    def __init__(self, 
                 document_processor: Optional[DocumentProcessor] = None,
                 ollama_engine: Optional[OllamaEngine] = None,
                 config: Optional[ChatConfig] = None):
        """Initialize chat engine with optional components"""
        self.config = config or ChatConfig()
        
        # Core components
        self.document_processor = document_processor or DocumentProcessor()
        self.ollama_engine = ollama_engine or OllamaEngine()
        
        # State tracking
        self.document_loaded = False
        self.entities_extracted = False
        self.knowledge_graph_data: Dict[str, Any] = {}
        
        # Chat history
        self.chat_history: List[Dict[str, Any]] = []
        
        logger.info("🚀 ChatEngine initialized")
    
    def load_document(self, pdf_path: str, extract_entities: bool = True) -> Dict[str, Any]:
        """
        Load document and prepare for chat
        
        Args:
            pdf_path: Path to PDF file
            extract_entities: Whether to extract entities immediately
            
        Returns:
            Loading results and capabilities
        """
        logger.info(f"📚 Loading document for chat: {pdf_path}")
        
        try:
            # Load document using processor
            document_data = self.document_processor.load_document(pdf_path)
            self.document_loaded = True
            
            # Extract entities if requested
            entities = {}
            if extract_entities:
                entities = self.document_processor.extract_entities()
                self.entities_extracted = True
            
            # Prepare response
            result = {
                'document_info': {
                    'title': document_data.title,
                    'chunks': len(document_data.chunks),
                    'characters': len(document_data.content),
                    'citation': document_data.citation
                },
                'entities': entities,
                'status': 'ready',
                'capabilities': []
            }
            
            # Add available capabilities
            if self.config.enable_rag_mode:
                result['capabilities'].append('rag_queries')
            if self.config.enable_graph_mode and self.entities_extracted:
                result['capabilities'].append('entity_exploration')
                result['capabilities'].append('relationship_discovery')
            
            logger.info("✅ Document loaded successfully for chat")
            return result
            
        except Exception as e:
            logger.error(f"❌ Document loading failed: {e}")
            return {
                'error': f'Failed to load document: {str(e)}',
                'status': 'failed'
            }
    
    def chat(self, message: str, mode: str = "auto") -> ChatResponse:
        """
        Process chat message with intelligent routing
        
        Args:
            message: User's question or command
            mode: Processing mode ("auto", "rag", "graph", "both")
            
        Returns:
            Structured chat response
        """
        if not self.document_loaded:
            return ChatResponse(
                answer="No document loaded. Please load a document first.",
                mode="error",
                source="system",
                error="No document loaded"
            )
        
        # Determine processing mode
        if mode == "auto" and self.config.auto_mode_routing:
            mode = self._determine_mode(message)
        
        try:
            # Route to appropriate handler
            if mode == "rag":
                response = self._rag_response(message)
            elif mode == "graph":
                response = self._graph_response(message)
            elif mode == "both":
                response = self._combined_response(message)
            else:
                response = ChatResponse(
                    answer=f"Unknown mode: {mode}",
                    mode="error",
                    source="system",
                    error=f"Invalid mode: {mode}"
                )
            
            # Store in chat history
            if not response.error:
                self.chat_history.append({
                    'message': message,
                    'response': response.model_dump(),
                    'timestamp': str(Path(__file__).stat().st_mtime),  # Simple timestamp
                    'mode': response.mode
                })
                
                # Trim history if needed
                if len(self.chat_history) > self.config.max_chat_history:
                    self.chat_history = self.chat_history[-self.config.max_chat_history:]
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Chat processing failed: {e}")
            return ChatResponse(
                answer=f"Error processing your message: {str(e)}",
                mode="error",
                source="system",
                error=str(e)
            )
    
    def _determine_mode(self, message: str) -> str:
        """Determine the best processing mode based on message content"""
        message_lower = message.lower()
        
        # Graph-oriented keywords
        graph_keywords = [
            'entities', 'relationships', 'connections', 'related to',
            'authors', 'methods', 'concepts', 'who', 'what methods',
            'connected', 'network', 'graph', 'entity'
        ]
        
        # RAG-oriented keywords  
        rag_keywords = [
            'explain', 'describe', 'how', 'why', 'findings', 'results',
            'conclusion', 'discussion', 'analysis', 'detailed',
            'methodology', 'approach', 'experiments'
        ]
        
        # Count keyword matches
        graph_score = sum(1 for keyword in graph_keywords if keyword in message_lower)
        rag_score = sum(1 for keyword in rag_keywords if keyword in message_lower)
        
        if graph_score > rag_score and self.entities_extracted:
            return "graph"
        elif rag_score > graph_score:
            return "rag"
        else:
            return "both" if self.entities_extracted else "rag"
    
    def _rag_response(self, message: str) -> ChatResponse:
        """Generate response using RAG system"""
        try:
            answer = self.document_processor.query(message, top_k=self.config.default_top_k)
            return ChatResponse(
                answer=answer,
                mode='rag',
                source='document_content',
                confidence='high'
            )
        except Exception as e:
            return ChatResponse(
                answer=f'RAG query failed: {str(e)}',
                mode='rag',
                source='error',
                error=str(e)
            )
    
    def _graph_response(self, message: str) -> ChatResponse:
        """Generate response using entity/graph information"""
        if not self.entities_extracted:
            return ChatResponse(
                answer="Entity information not available. Extract entities first.",
                mode='graph',
                source='error',
                error="No entities extracted"
            )
        
        try:
            message_lower = message.lower()
            entities = self.document_processor.document_data.entities
            
            # Handle specific entity type queries
            if 'authors' in message_lower:
                authors = entities.get('authors', [])
                if authors:
                    return ChatResponse(
                        answer=f"The authors of this document are: {', '.join(authors)}",
                        mode='graph',
                        source='knowledge_graph',
                        entities=authors
                    )
            
            elif 'methods' in message_lower:
                methods = entities.get('methods', [])
                if methods:
                    return ChatResponse(
                        answer=f"The methods mentioned in this document include: {', '.join(methods)}",
                        mode='graph',
                        source='knowledge_graph',
                        entities=methods
                    )
            
            elif 'concepts' in message_lower:
                concepts = entities.get('concepts', [])
                if concepts:
                    return ChatResponse(
                        answer=f"Key concepts in this document: {', '.join(concepts)}",
                        mode='graph',
                        source='knowledge_graph',
                        entities=concepts
                    )
            
            # General entity summary
            total_entities = sum(len(v) for v in entities.values())
            entity_summary = []
            for entity_type, entity_list in entities.items():
                if entity_list:
                    entity_summary.append(f"{entity_type}: {', '.join(entity_list[:3])}")
            
            return ChatResponse(
                answer=f"This document contains {total_entities} extracted entities:\\n" + 
                       "\\n".join(entity_summary[:5]),
                mode='graph',
                source='knowledge_graph',
                metadata={'total_entities': total_entities}
            )
            
        except Exception as e:
            return ChatResponse(
                answer=f'Graph query failed: {str(e)}',
                mode='graph',
                source='error',
                error=str(e)
            )
    
    def _combined_response(self, message: str) -> ChatResponse:
        """Generate response using both RAG and graph information"""
        try:
            # Get RAG response
            rag_response = self._rag_response(message)
            
            if rag_response.error:
                return rag_response
            
            # Enhance with entity context if available
            if self.entities_extracted:
                entities = self.document_processor.document_data.entities
                total_entities = sum(len(v) for v in entities.values())
                
                if total_entities > 0:
                    # Add entity context
                    enhanced_answer = rag_response.answer
                    enhanced_answer += "\\n\\n**Related entities from knowledge graph:** "
                    
                    # Add top entities from different categories
                    entity_context = []
                    for entity_type, entity_list in entities.items():
                        if entity_list:
                            entity_context.append(f"{entity_type}: {', '.join(entity_list[:2])}")
                    
                    enhanced_answer += "; ".join(entity_context[:3])
                    
                    return ChatResponse(
                        answer=enhanced_answer,
                        mode='both',
                        source='document_content + knowledge_graph',
                        confidence='high',
                        metadata={'entity_types': len([k for k, v in entities.items() if v])}
                    )
            
            # Return RAG response if no entities
            rag_response.mode = 'both'
            return rag_response
                
        except Exception as e:
            return ChatResponse(
                answer=f'Combined query failed: {str(e)}',
                mode='both',
                source='error',
                error=str(e)
            )
    
    def get_entities(self) -> Dict[str, List[str]]:
        """Get all extracted entities"""
        if not self.entities_extracted:
            return {}
        
        return self.document_processor.document_data.entities
    
    def explore_entity(self, entity_name: str) -> Dict[str, Any]:
        """Explore a specific entity and its context"""
        if not self.entities_extracted:
            return {'error': 'Knowledge graph not built yet. Load a document first.'}
        
        entities = self.document_processor.document_data.entities
        
        # Find entity across all categories
        found_in = []
        for entity_type, entity_list in entities.items():
            if entity_name.lower() in [e.lower() for e in entity_list]:
                found_in.append(entity_type)
        
        if not found_in:
            return {'error': f'Entity "{entity_name}" not found in extracted entities.'}
        
        # Get context using RAG
        try:
            context = self.document_processor.query(f"Tell me about {entity_name}")
            return {
                'entity': entity_name,
                'categories': found_in,
                'context': context,
                'related_entities': {cat: entities[cat] for cat in found_in}
            }
        except Exception as e:
            return {'error': f'Failed to get context for {entity_name}: {str(e)}'}
    
    def get_document_overview(self) -> Dict[str, Any]:
        """Get comprehensive overview of loaded document"""
        if not self.document_loaded:
            return {'error': 'No document loaded'}
        
        overview = {
            'document_info': self.document_processor.get_document_summary(),
            'entities': self.get_entities() if self.entities_extracted else {},
            'chat_history_length': len(self.chat_history),
            'capabilities': [],
            'status': 'ready' if self.document_loaded else 'not_loaded'
        }
        
        # Add available capabilities
        if self.config.enable_rag_mode:
            overview['capabilities'].append('rag_queries')
        if self.config.enable_graph_mode and self.entities_extracted:
            overview['capabilities'].extend(['entity_exploration', 'relationship_discovery'])
        
        return overview
    
    def suggest_questions(self) -> List[str]:
        """Suggest interesting questions based on document content"""
        if not self.document_loaded:
            return ["Load a document first to get question suggestions."]
        
        suggestions = [
            "What are the main findings of this document?",
            "What methods were used in this work?",
            "What are the key concepts discussed?",
        ]
        
        # Add entity-specific suggestions
        if self.entities_extracted:
            entities = self.get_entities()
            
            if entities.get('methods'):
                method = entities['methods'][0]
                suggestions.append(f"Tell me more about {method}")
            
            if entities.get('concepts'):
                concept = entities['concepts'][0]
                suggestions.append(f"How is {concept} used in this document?")
            
            if entities.get('authors'):
                suggestions.append("Who are the authors and what are their contributions?")
        
        return suggestions


# Factory function for easy initialization
def create_chat_engine(embedding_model: str = "nomic-embed-text",
                      llm_model: str = "llama3.1:8b") -> ChatEngine:
    """Create a ChatEngine with specified models"""
    # Create components
    document_processor = DocumentProcessor()
    ollama_engine = OllamaEngine()
    
    return ChatEngine(
        document_processor=document_processor,
        ollama_engine=ollama_engine
    )
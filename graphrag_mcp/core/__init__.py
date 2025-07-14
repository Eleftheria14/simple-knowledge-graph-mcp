"""
Core processing engine for GraphRAG MCP Toolkit

Domain-agnostic components for document processing, knowledge graph extraction,
and chat interface functionality. These components are used by all domain templates.

Components:
- DocumentProcessor: PDF processing and text chunking
- ChatEngine: RAG + Knowledge Graph unified interface  
- AdvancedAnalyzer: Enhanced document analysis with citations
- OllamaEngine: Local LLM integration layer
"""

from .document_processor import DocumentProcessor, ProcessingConfig, DocumentData, create_document_processor
from .chat_engine import ChatEngine, ChatConfig, ChatResponse, create_chat_engine
from .analyzer import AdvancedAnalyzer, AnalysisConfig, CorpusDocument, create_advanced_analyzer
from .ollama_engine import OllamaEngine, OllamaConfig, create_ollama_engine

__all__ = [
    # Main classes
    "DocumentProcessor",
    "ChatEngine",
    "AdvancedAnalyzer", 
    "OllamaEngine",
    
    # Configuration classes
    "ProcessingConfig",
    "ChatConfig", 
    "AnalysisConfig",
    "OllamaConfig",
    
    # Data classes
    "DocumentData",
    "ChatResponse",
    "CorpusDocument",
    
    # Factory functions
    "create_document_processor",
    "create_chat_engine",
    "create_advanced_analyzer",
    "create_ollama_engine",
]
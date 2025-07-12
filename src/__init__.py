"""
Simple Scientific Paper RAG + Knowledge Graph

A simple, personal tool for intelligent analysis of scientific papers using RAG and Knowledge Graph extraction.
Built with LangChain, LangGraph, and Ollama for local, private analysis.
"""

__version__ = "2.0.0"
__author__ = "Aimie Garces"

# Import simple, unified components
from .simple_paper_rag import SimplePaperRAG, analyze_paper
from .simple_knowledge_graph import SimpleKnowledgeGraph
from .unified_paper_chat import UnifiedPaperChat, analyze_paper_with_chat

__all__ = [
    # Main components
    'SimplePaperRAG',
    'SimpleKnowledgeGraph', 
    'UnifiedPaperChat',
    # Convenience functions
    'analyze_paper',
    'analyze_paper_with_chat'
]
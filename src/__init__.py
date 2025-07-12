"""
Scientific Paper Literature Review System

An intelligent system for analyzing scientific papers and building literature reviews.
Features enhanced paper analysis, knowledge graph extraction, and GraphRAG integration
for comprehensive cross-paper discovery and citation-accurate writing.

Built with LangChain, LangGraph, and Ollama for local, private analysis.
"""

__version__ = "2.1.0"
__author__ = "Aimie Garces"

# Core analysis components
from .simple_paper_rag import SimplePaperRAG, analyze_paper
from .simple_knowledge_graph import SimpleKnowledgeGraph
from .unified_paper_chat import UnifiedPaperChat, analyze_paper_with_chat, export_paper_for_corpus

# Enhanced components for literature reviews
from .enhanced_paper_analyzer import EnhancedPaperAnalyzer, analyze_paper_for_corpus
from .citation_tracker import CitationTracker, track_citations_in_paper, verify_citation_accuracy

__all__ = [
    # Main components
    'SimplePaperRAG',
    'SimpleKnowledgeGraph', 
    'UnifiedPaperChat',
    
    # Enhanced components
    'EnhancedPaperAnalyzer',
    'CitationTracker',
    
    # Analysis functions
    'analyze_paper',
    'analyze_paper_with_chat',
    'analyze_paper_for_corpus',
    'export_paper_for_corpus',
    
    # Citation functions
    'track_citations_in_paper',
    'verify_citation_accuracy'
]
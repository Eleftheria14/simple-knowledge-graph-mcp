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

# GraphRAG and visualization components
from .langchain_graph_rag import LangChainGraphRAG
from .yfiles_visualization import create_yfiles_visualization, YFilesGraphRAGVisualizer
from .notebook_visualization import show_knowledge_graph

# Tutorial helper functions
from .tutorial_helpers import (
    interactive_paper_chat, test_question_routing, analyze_system_performance,
    generate_comprehensive_summary, display_tutorial_results, show_suggested_next_steps
)

# Enhanced knowledge graph extraction
from .enhanced_knowledge_graph import EnhancedKnowledgeGraph, create_enhanced_knowledge_graph

__all__ = [
    # Main components
    'SimplePaperRAG',
    'SimpleKnowledgeGraph', 
    'UnifiedPaperChat',
    
    # Enhanced components
    'EnhancedPaperAnalyzer',
    'CitationTracker',
    
    # GraphRAG components
    'LangChainGraphRAG',
    'create_yfiles_visualization',
    'YFilesGraphRAGVisualizer',
    'show_knowledge_graph',
    
    # Analysis functions
    'analyze_paper',
    'analyze_paper_with_chat',
    'analyze_paper_for_corpus',
    'export_paper_for_corpus',
    
    # Citation functions
    'track_citations_in_paper',
    'verify_citation_accuracy',
    
    # Tutorial helpers
    'interactive_paper_chat',
    'test_question_routing', 
    'analyze_system_performance',
    'generate_comprehensive_summary',
    'display_tutorial_results',
    'show_suggested_next_steps',
    
    # Enhanced knowledge graphs
    'EnhancedKnowledgeGraph',
    'create_enhanced_knowledge_graph'
]
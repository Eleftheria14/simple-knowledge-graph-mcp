"""
Scientific Paper Analyzer Package

A comprehensive tool for analyzing scientific research papers using Large Language Models (LLMs) 
through LangChain and Ollama, with PostgreSQL database integration for citation storage.
"""

__version__ = "1.0.0"
__author__ = "Aimie Garces"

# Import main classes and functions for easy access
from .citation_extractor import extract_citation_info, format_citations, display_citation_info, get_acs_citation
from .enhanced_citation_extractor import extract_and_store_citation, display_and_store_citation, search_stored_citations
from .database_manager import CitationDatabaseManager, PaperRecord, store_citation_data

__all__ = [
    'extract_citation_info',
    'format_citations', 
    'display_citation_info',
    'get_acs_citation',
    'extract_and_store_citation',
    'display_and_store_citation',
    'search_stored_citations',
    'CitationDatabaseManager',
    'PaperRecord',
    'store_citation_data'
]
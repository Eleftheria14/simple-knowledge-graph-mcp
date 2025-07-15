"""
GraphRAG MCP Visualization Package

Advanced visualization components for knowledge graphs combining multiple technologies:
- Graphiti: Real-time knowledge graph backend with Neo4j persistence
- yFiles: Professional graph visualization
- Export capabilities for multiple formats

This package provides a unified interface for visualizing knowledge graphs
created from document collections, with support for real-time updates,
interactive exploration, and professional-grade output.
"""

from .graphiti_yfiles import (
    GraphitiYFilesVisualizer,
    create_graphiti_yfiles_visualizer,
    display_graphiti_knowledge_graph,
)

# NetworkX legacy code removed - Graphiti is now the only backend
NETWORKX_VISUALIZATION_AVAILABLE = False

__all__ = [
    # Graphiti + yFiles visualization (primary)
    'GraphitiYFilesVisualizer',
    'create_graphiti_yfiles_visualizer',
    'display_graphiti_knowledge_graph',

    # Status flags
    'NETWORKX_VISUALIZATION_AVAILABLE'
]

def get_available_visualizers():
    """Get information about available visualization backends"""
    available = {
        'graphiti_yfiles': True,  # Primary backend
        'matplotlib': True,  # Fallback visualization
        'yfiles': True  # Professional visualization
    }

    return available

def recommend_visualizer(use_case: str = "general") -> str:
    """
    Recommend the best visualizer for a specific use case
    
    Args:
        use_case: Type of visualization needed
                 ("general", "real_time", "export", "notebook", "web")
    
    Returns:
        str: Recommended visualizer name
    """
    # Always recommend Graphiti + yFiles - it's the only backend now
    return "graphiti_yfiles"

# Version information
__version__ = "0.1.0"
__author__ = "GraphRAG MCP Toolkit"
__description__ = "Advanced visualization for knowledge graphs"

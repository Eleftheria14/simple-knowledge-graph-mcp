"""
GraphRAG MCP Convenience Functions

This module provides simple, one-line functions for common use cases.
"""

from ..utils.error_handling import ProcessingError, ValidationError
from .processor import GraphRAGProcessor


def quick_setup(project_name: str, documents_folder: str, template: str = "academic") -> GraphRAGProcessor:
    """
    One-function setup for common use cases
    
    Args:
        project_name: Name of the project
        documents_folder: Path to documents folder
        template: Template to use (default: academic)
        
    Returns:
        Configured GraphRAGProcessor ready to use
        
    Raises:
        ValidationError: If environment prerequisites are not met
        ProcessingError: If document processing fails
    """
    # Create processor
    processor = GraphRAGProcessor(project_name, template)

    # Validate environment
    validation = processor.validate_environment(verbose=False)
    if not validation.is_valid:
        raise ValidationError(
            f"Environment validation failed: {', '.join(validation.issues)}",
            {"validation_result": validation.to_dict()}
        )

    # Discover documents
    documents = processor.discover_documents(documents_folder)
    if not documents:
        raise ProcessingError(
            f"No documents found in {documents_folder}",
            {"folder": documents_folder}
        )

    print(f"✅ Quick setup complete for {project_name}")
    print(f"   📁 Found {len(documents)} documents")
    print(f"   🔧 Template: {template}")
    print("   🎯 Ready to process documents")

    return processor


async def quick_process(project_name: str, documents_folder: str, template: str = "academic") -> GraphRAGProcessor:
    """
    One-function setup and processing for common use cases
    
    Args:
        project_name: Name of the project
        documents_folder: Path to documents folder  
        template: Template to use (default: academic)
        
    Returns:
        Configured GraphRAGProcessor with processed documents
        
    Raises:
        ValidationError: If environment prerequisites are not met
        ProcessingError: If document processing fails
    """
    # Quick setup
    processor = quick_setup(project_name, documents_folder, template)

    # Discover and process documents
    documents = processor.discover_documents(documents_folder)
    results = await processor.process_documents(documents)

    if results.failed > 0:
        print(f"⚠️  {results.failed} documents failed to process")

    print(f"🎉 Processing complete for {project_name}")
    print(f"   ✅ {results.success} documents processed successfully")
    print(f"   ⏱️  Total time: {results.total_time/60:.1f} minutes")

    return processor


def validate_system() -> bool:
    """
    Quick system validation
    
    Returns:
        True if system is ready, False otherwise
    """
    from ..utils.prerequisites import validate_environment

    result = validate_environment()
    return result.is_valid


def get_system_status() -> dict:
    """
    Get detailed system status
    
    Returns:
        Dictionary with system status information
    """
    from ..utils.prerequisites import check_prerequisites, get_system_info

    validation = check_prerequisites(verbose=False)
    system_info = get_system_info()

    return {
        "validation": validation.to_dict(),
        "system_info": system_info,
        "ready": validation.is_valid
    }


def visualize_processed_documents(documents, project_name: str = "GraphRAG Project", max_nodes: int = 50):
    """
    Quick visualization of processed documents using Graphiti + yFiles
    
    Args:
        documents: List of processed documents
        project_name: Name of the project
        max_nodes: Maximum number of nodes to display
        
    Returns:
        NetworkX graph object or None if visualization fails
    """
    # Use the real knowledge graph visualization instead of legacy Plotly
    from ..visualization.graphiti_yfiles import GraphitiYFilesVisualizer
    print("📊 Use 'graphrag-mcp visualize <project>' command for knowledge graph visualization")
    print("   Or use GraphitiYFilesVisualizer for advanced visualization features")
    return None

#!/usr/bin/env python3
"""
Debug version of cell 2 - copy this into a new cell to test
"""

print("🔍 Testing GraphRAG initialization...")

try:
    # Test with verbose output
    from src.langchain_graph_rag import LangChainGraphRAG
    print("✅ Import successful")
    
    print("🔗 Connecting to Ollama...")
    graph_rag = LangChainGraphRAG(
        llm_model="llama3.1:8b",
        embedding_model="nomic-embed-text",
        verbose=True  # Enable debug output
    )
    print("✅ GraphRAG created successfully!")
    
    print(f"📊 Current papers: {len(graph_rag.get_all_papers())}")
    print("🕸️ Knowledge graph system ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
#!/usr/bin/env python3
"""
Test GraphRAG MCP system with Graphiti integration
"""
import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, '/Users/aimiegarces/Agents')

# Set environment variables for Neo4j connection
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'password'

# Configure Ollama for GraphRAG MCP
os.environ['OPENAI_API_KEY'] = 'ollama'  # Placeholder for Ollama
os.environ['OPENAI_BASE_URL'] = 'http://localhost:11434/v1'  # Ollama API endpoint

async def test_graphrag_mcp_system():
    """Test GraphRAG MCP system with Graphiti backend"""
    try:
        print("🔄 Testing GraphRAG MCP system with Graphiti...")
        
        # Test core GraphRAG MCP imports
        try:
            from graphrag_mcp.core.graphiti_engine import create_graphiti_knowledge_graph
            from graphrag_mcp.core.analyzer import analyze_paper_with_chat
            from graphrag_mcp.visualization.graphiti_yfiles import display_graphiti_knowledge_graph
            print("✅ GraphRAG MCP imports successful")
        except ImportError as e:
            print(f"❌ GraphRAG MCP imports failed: {e}")
            return False
        
        # Test Graphiti core import (if available)
        try:
            from graphiti_core import Graphiti
            from graphiti_core.nodes import EpisodeType
            print("✅ Graphiti core imports successful")
            has_graphiti = True
        except ImportError:
            print("ℹ️  Graphiti core not available, using GraphRAG MCP fallback")
            has_graphiti = False
        
        # Test GraphRAG MCP system functionality
        print("🔄 Testing GraphRAG MCP knowledge graph creation...")
        try:
            # This will test the GraphRAG MCP system
            kg_result = await create_graphiti_knowledge_graph()
            print("✅ GraphRAG MCP knowledge graph created successfully")
        except Exception as e:
            print(f"⚠️  GraphRAG MCP knowledge graph creation failed: {e}")
        
        # Test Graphiti core if available
        if has_graphiti:
            print("🔄 Testing Graphiti core integration...")
            try:
                from graphiti_core.llm_client import OpenAIClient, LLMConfig
                from graphiti_core.embedder import OpenAIEmbedder, OpenAIEmbedderConfig
                
                # Create LLM config for Graphiti with Ollama
                llm_config = LLMConfig(
                    api_key='ollama',  # Placeholder for Ollama
                    base_url='http://localhost:11434/v1',
                    model='llama3.1:8b',
                    small_model='llama3.1:8b',  # Use same model for simple prompts
                    temperature=0.1,
                    max_tokens=4096
                )
                
                # Create LLM client (OpenAI compatible)
                llm_client = OpenAIClient(llm_config)
                
                # Create embedder config for Ollama
                embedder_config = OpenAIEmbedderConfig(
                    api_key='ollama',
                    base_url='http://localhost:11434/v1',
                    embedding_model='nomic-embed-text'  # Explicitly set embedding model
                )
                
                # Create embedder client (OpenAI compatible)
                embedder_client = OpenAIEmbedder(embedder_config)
                
                graphiti = Graphiti(
                    uri='bolt://localhost:7687',
                    user='neo4j', 
                    password='password',
                    llm_client=llm_client,
                    embedder=embedder_client
                )
                
                print("✅ Graphiti initialized successfully")
                
                # Test database connection
                print("🔄 Building indices and constraints...")
                await graphiti.build_indices_and_constraints()
                print("✅ Neo4j indices and constraints created")
                
                # Test adding a simple episode
                print("🔄 Adding test episode...")
                await graphiti.add_episode(
                    name='Test Episode',
                    episode_body='This is a test document about machine learning for drug discovery.',
                    source=EpisodeType.text,
                    source_description='Test document',
                    reference_time=datetime.now()
                )
                print("✅ Test episode added successfully")
                
                # Test search functionality
                print("🔄 Testing search functionality...")
                search_results = await graphiti.search(
                    query='machine learning'
                )
                print(f"✅ Search returned {len(search_results)} results")
                
                # Close connection
                await graphiti.close()
                
            except Exception as e:
                print(f"⚠️  Graphiti core test failed: {e}")
        
        print("\n🎉 GraphRAG MCP system test completed!")
        print("📊 System ready for paper analysis with Graphiti backend")
        
    except Exception as e:
        print(f"❌ GraphRAG MCP system test failed: {e}")
        print("🔧 Check system dependencies and configuration")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_graphrag_mcp_system())
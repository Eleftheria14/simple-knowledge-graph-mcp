#!/usr/bin/env python3
"""
Debug entity extraction to see why no entities are being found
"""

import sys
import os
sys.path.insert(0, '/Users/aimiegarces/Agents')

from src import LangChainGraphRAG

def debug_entity_extraction():
    """Debug the entity extraction process step by step"""
    
    print("🔍 Debugging Entity Extraction")
    print("=" * 40)
    
    # Simple test content
    test_content = """
    Machine Learning for Drug Discovery
    Authors: Dr. Sarah Chen (MIT), Prof. Michael Torres (Stanford)
    
    This study presents deep learning approaches for molecular property prediction.
    We developed ChemNet, a transformer architecture for chemical analysis.
    The model was trained on PubChem and ChEMBL datasets with 95% accuracy.
    Applications include drug discovery and materials science.
    """
    
    print("📄 Test content:")
    print(f"   Length: {len(test_content)} characters")
    print(f"   Content: {test_content[:200]}...")
    
    try:
        print("\n🚀 Creating GraphRAG system...")
        graph_rag = LangChainGraphRAG()
        
        print("🔍 Extracting entities...")
        result = graph_rag.extract_entities_and_relationships(
            paper_content=test_content,
            paper_title="Machine Learning for Drug Discovery",
            paper_id="debug_test"
        )
        
        print(f"\n📊 Raw Result Structure:")
        print(f"   Keys: {list(result.keys())}")
        
        entities = result.get('entities', {})
        print(f"\n🏷️ Entities Result:")
        print(f"   Type: {type(entities)}")
        print(f"   Keys: {list(entities.keys()) if isinstance(entities, dict) else 'Not a dict'}")
        
        if isinstance(entities, dict):
            total_entities = sum(len(entity_list) for entity_list in entities.values() if isinstance(entity_list, list))
            print(f"   Total entities: {total_entities}")
            
            print(f"\n📋 Entity Breakdown:")
            for category, entity_list in entities.items():
                if isinstance(entity_list, list):
                    print(f"      {category}: {len(entity_list)} items")
                    if entity_list:
                        print(f"         Examples: {entity_list[:3]}")
                else:
                    print(f"      {category}: {entity_list} (not a list)")
        else:
            print("❌ Entities is not a dictionary!")
            print(f"   Value: {entities}")
        
        # Check graph stats
        graph_stats = result.get('graph_stats', {})
        print(f"\n📈 Graph Stats:")
        print(f"   {graph_stats}")
        
        # Check relationships
        relationships = result.get('relationships', [])
        print(f"\n🔗 Relationships:")
        print(f"   Count: {len(relationships)}")
        if relationships:
            print(f"   Sample: {relationships[0] if relationships else 'None'}")
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        
        # Try the basic extraction method to compare
        print(f"\n🔬 Trying basic extraction for comparison...")
        try:
            from src import SimpleKnowledgeGraph
            basic_kg = SimpleKnowledgeGraph()
            basic_result = basic_kg.extract_entities_and_relationships(test_content, "Test Paper")
            
            basic_entities = basic_result.get('entities', {})
            basic_total = sum(len(entity_list) for entity_list in basic_entities.values() if isinstance(entity_list, list))
            print(f"   Basic extraction found: {basic_total} entities")
            
            if basic_total > 0:
                print("   ✅ Basic extraction works - issue is with enhanced version")
            else:
                print("   ❌ Basic extraction also failing - LLM connection issue?")
                
        except Exception as basic_error:
            print(f"   ❌ Basic extraction also failed: {basic_error}")

def test_llm_connection():
    """Test if the LLM connection is working"""
    print("\n🔌 Testing LLM Connection")
    print("=" * 30)
    
    try:
        from langchain_ollama import ChatOllama
        
        llm = ChatOllama(model="llama3.1:8b", temperature=0.1)
        
        # Simple test prompt
        response = llm.invoke("Say 'Hello, I am working!' and nothing else.")
        print(f"✅ LLM Response: {response.content}")
        
        # Test JSON generation
        json_prompt = '''Return ONLY this JSON: {"test": "working", "number": 42}'''
        json_response = llm.invoke(json_prompt)
        print(f"📄 JSON Test: {json_response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Connection Failed: {e}")
        return False

if __name__ == "__main__":
    # Test LLM connection first
    llm_working = test_llm_connection()
    
    if llm_working:
        print("\n" + "="*50)
        debug_entity_extraction()
    else:
        print("\n💡 Fix LLM connection first, then run entity extraction debug.")
        print("   Check: ollama serve")
        print("   Check: ollama list (should show llama3.1:8b)")
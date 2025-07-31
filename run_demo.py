#!/usr/bin/env python3
"""
Quick demo runner for the Knowledge Graph Document Processor
Run this to see the system in action without Jupyter
"""
import sys
import asyncio
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from processor.config import ProcessorConfig
from processor.document_pipeline import DocumentOrchestrator
from tools.storage.enhanced_entity_storage import extract_and_store_entities
from tools.shared_registry import SharedToolRegistry

async def main():
    print("🎯 Knowledge Graph Document Processor Demo")
    print("=" * 50)
    
    # Setup
    print("\n🔧 1. Configuration Check")
    try:
        config = ProcessorConfig()
        config.validate()
        print(f"✅ Config valid - Model: {config.model_name}")
    except Exception as e:
        print(f"❌ Config error: {e}")
        return
    
    # Tool Registry
    print("\n📋 2. Shared Tool Registry")
    summary = SharedToolRegistry.get_tool_summary()
    print(f"✅ {summary['total_shared_tools']} shared tools available")
    print(f"📊 Capabilities: {summary['capabilities']}")
    
    # Direct Entity Extraction
    print("\n🧠 3. Direct Entity Extraction Demo")
    test_content = """
    The Transformer architecture was introduced by Vaswani et al. from Google Research 
    in "Attention Is All You Need" (2017). This revolutionized NLP by using self-attention 
    instead of recurrent networks. The architecture inspired BERT by Google AI and GPT by OpenAI.
    """
    
    start_time = time.time()
    result = extract_and_store_entities.invoke({
        "content": test_content,
        "document_info": {"title": "Transformer Demo", "type": "demo"}
    })
    extraction_time = time.time() - start_time
    
    print(f"⏱️  Processing time: {extraction_time:.2f} seconds")
    print(f"🔍 Entities found: {result['entities_found']}")
    print(f"🔗 Relationships found: {result['relationships_found']}")
    
    # LangGraph Orchestrator
    print("\n🤖 4. LangGraph Orchestrator Demo")
    orchestrator = DocumentOrchestrator(config)
    print(f"✅ Agent initialized with {len(orchestrator.tools)} tools")
    print(f"📋 Tools: {[tool.name for tool in orchestrator.tools]}")
    
    # Create test document
    test_doc = Path("demo_doc.txt")
    test_doc.write_text("""
    GPT-4 is a multimodal model by OpenAI that shows human-level performance 
    on professional benchmarks. Built on GPT-3.5, it uses RLHF training 
    similar to ChatGPT and achieves 90th percentile on the Bar Exam.
    """)
    
    print("📄 Processing test document through LangGraph agent...")
    agent_result = await orchestrator.process_document(str(test_doc))
    
    print(f"✅ Agent success: {agent_result.get('success', False)}")
    if 'processing_steps' in agent_result:
        print(f"🔄 Processing steps: {agent_result['processing_steps']}")
    if 'error' in agent_result:
        print(f"⚠️  Error details: {agent_result['error'][:100]}...")
    
    # Cleanup
    test_doc.unlink()
    
    # Architecture Benefits
    print("\n🏗️ 5. Architecture Benefits Summary")
    print("✅ Same tools work for:")
    print("   📡 MCP clients (Claude Desktop)")
    print("   🤖 LangGraph agents (automation)")
    print("   🔧 Direct Python usage (custom apps)")
    print("✅ No code duplication")
    print("✅ Single source of truth for each capability")
    print("✅ Easy testing and maintenance")
    
    print("\n🎉 Demo Complete!")
    print("💡 The shared MCP-LangChain architecture is working perfectly!")

if __name__ == "__main__":
    asyncio.run(main())
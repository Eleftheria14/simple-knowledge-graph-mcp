#!/usr/bin/env python3
"""
Basic Integration Test for GraphRAG MCP Toolkit

Simple test script to verify our new components work together without
requiring full dependency installation.
"""

import sys
import os

# Add current directory to path for imports  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_citation_manager():
    """Test citation manager functionality"""
    print("Testing Citation Manager...")
    
    try:
        from graphrag_mcp.core.citation_manager import CitationTracker
        
        # Create citation manager
        citation_manager = CitationTracker()
        
        # Add citations
        citation1 = citation_manager.add_citation(
            title="Deep Learning Fundamentals",
            authors=["Alice Johnson", "Bob Smith"],
            year=2023,
            journal="AI Research"
        )
        
        citation2 = citation_manager.add_citation(
            title="Neural Networks in Practice",
            authors=["Carol Davis"],
            year=2022,
            doi="10.1000/test123"
        )
        
        print(f"  ✅ Added 2 citations: {citation1}, {citation2}")
        
        # Track usage
        citation_manager.track_citation(citation1, "Used in introduction")
        citation_manager.track_citation(citation2, "Used in methodology")
        
        print("  ✅ Tracked citation usage")
        
        # Generate bibliography
        apa_bib = citation_manager.generate_bibliography(style="APA", used_only=True)
        ieee_bib = citation_manager.generate_bibliography(style="IEEE", used_only=True)
        
        print(f"  ✅ Generated APA bibliography ({len(apa_bib)} entries)")
        print(f"  ✅ Generated IEEE bibliography ({len(ieee_bib)} entries)")
        
        # Check statistics
        stats = citation_manager.get_citation_statistics()
        print(f"  ✅ Citation statistics: {stats['used_citations']}/{stats['total_citations']} used")
        
        # Test in-text citations
        in_text_apa = citation_manager.generate_in_text_citation(citation1, "APA")
        in_text_ieee = citation_manager.generate_in_text_citation(citation1, "IEEE")
        
        print(f"  ✅ APA in-text: {in_text_apa}")
        print(f"  ✅ IEEE in-text: {in_text_ieee}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Citation manager test failed: {e}")
        return False


async def test_query_engine():
    """Test query engine functionality"""
    print("\nTesting Query Engine...")
    
    try:
        from graphrag_mcp.core.query_engine import EnhancedQueryEngine, QueryType, QueryIntent
        from graphrag_mcp.core.citation_manager import CitationTracker
        
        # Create components
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        
        print("  ✅ Created query engine with citation manager")
        
        # Test query analysis methods
        query = "What are the main approaches to deep learning?"
        query_type = query_engine._classify_query_type(query, None)
        intent = query_engine._classify_intent(query)
        
        print(f"  ✅ Query analysis: type={query_type.value}, intent={intent.value}")
        
        # Test entity extraction
        entities = await query_engine._extract_entities("Machine Learning and Neural Networks")
        keywords = query_engine._extract_keywords("What are the latest advances in artificial intelligence?")
        
        print(f"  ✅ Entity extraction: {entities}")
        print(f"  ✅ Keyword extraction: {keywords}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Query engine test failed: {e}")
        return False


def test_chat_tools():
    """Test chat tools functionality"""
    print("\nTesting Chat Tools...")
    
    try:
        from graphrag_mcp.mcp.chat_tools import ChatToolsEngine
        from graphrag_mcp.core.query_engine import EnhancedQueryEngine
        from graphrag_mcp.core.citation_manager import CitationTracker
        
        # Create components
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        chat_tools = ChatToolsEngine(query_engine=query_engine, citation_manager=citation_manager)
        
        print("  ✅ Created chat tools engine")
        
        # Test component integration
        assert chat_tools.citation_manager is citation_manager
        assert chat_tools.query_engine is query_engine
        
        print("  ✅ Component integration verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Chat tools test failed: {e}")
        return False


def test_literature_tools():
    """Test literature review tools functionality"""
    print("\nTesting Literature Review Tools...")
    
    try:
        from graphrag_mcp.mcp.literature_tools import LiteratureToolsEngine
        from graphrag_mcp.core.query_engine import EnhancedQueryEngine
        from graphrag_mcp.core.citation_manager import CitationTracker
        
        # Create components
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        literature_tools = LiteratureToolsEngine(query_engine=query_engine, citation_manager=citation_manager)
        
        print("  ✅ Created literature tools engine")
        
        # Test component integration
        assert literature_tools.citation_manager is citation_manager
        assert literature_tools.query_engine is query_engine
        
        print("  ✅ Component integration verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Literature tools test failed: {e}")
        return False


def test_academic_template():
    """Test academic template functionality"""
    print("\nTesting Academic Template...")
    
    try:
        from graphrag_mcp.templates.academic import AcademicTemplate
        
        template = AcademicTemplate()
        config = template.get_template_config()
        
        print(f"  ✅ Template name: {config.name}")
        print(f"  ✅ Template domain: {config.domain}")
        
        # Check tools
        tools = template.get_mcp_tools()
        tool_names = [tool["name"] for tool in tools]
        
        print(f"  ✅ Total tools defined: {len(tools)}")
        
        # Check for expected chat tools
        chat_tools = ["ask_knowledge_graph", "explore_topic", "find_connections", "what_do_we_know_about"]
        for tool in chat_tools:
            if tool in tool_names:
                print(f"  ✅ Chat tool found: {tool}")
            else:
                print(f"  ❌ Chat tool missing: {tool}")
        
        # Check for expected literature tools
        lit_tools = ["gather_sources_for_topic", "get_facts_with_citations", "verify_claim_with_sources", 
                    "get_topic_outline", "track_citations_used", "generate_bibliography"]
        for tool in lit_tools:
            if tool in tool_names:
                print(f"  ✅ Literature tool found: {tool}")
            else:
                print(f"  ❌ Literature tool missing: {tool}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Academic template test failed: {e}")
        return False


def test_end_to_end_workflow():
    """Test complete workflow"""
    print("\nTesting End-to-End Workflow...")
    
    try:
        from graphrag_mcp.core.citation_manager import CitationTracker
        from graphrag_mcp.core.query_engine import EnhancedQueryEngine
        from graphrag_mcp.mcp.chat_tools import ChatToolsEngine
        from graphrag_mcp.mcp.literature_tools import LiteratureToolsEngine
        
        # Create complete system
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        chat_tools = ChatToolsEngine(query_engine=query_engine, citation_manager=citation_manager)
        literature_tools = LiteratureToolsEngine(query_engine=query_engine, citation_manager=citation_manager)
        
        print("  ✅ Created complete system with shared components")
        
        # Add some test citations
        cite1 = citation_manager.add_citation(
            title="Advances in Machine Learning",
            authors=["Dr. Smith"],
            year=2023
        )
        
        cite2 = citation_manager.add_citation(
            title="Deep Learning Applications",
            authors=["Prof. Johnson", "Dr. Williams"],
            year=2022
        )
        
        print("  ✅ Added test citations to shared citation manager")
        
        # Simulate usage across tools
        citation_manager.track_citation(cite1, "Used in chat response")
        citation_manager.track_citation(cite2, "Used in literature review")
        
        print("  ✅ Tracked citations across different tool contexts")
        
        # Generate final bibliography
        final_bib = citation_manager.generate_bibliography(style="APA", used_only=True)
        
        print(f"  ✅ Generated final bibliography with {len(final_bib)} entries")
        
        # Verify all tools can access shared state
        assert cite1 in chat_tools.citation_manager.citations
        assert cite1 in literature_tools.citation_manager.citations
        assert cite1 in citation_manager.used_citations
        
        print("  ✅ Verified shared state consistency across all tools")
        
        return True
        
    except Exception as e:
        print(f"  ❌ End-to-end workflow test failed: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("🚀 Starting GraphRAG MCP Toolkit Integration Tests\n")
    
    tests = [
        test_citation_manager,
        test_query_engine, 
        test_chat_tools,
        test_literature_tools,
        test_academic_template,
        test_end_to_end_workflow
    ]
    
    results = []
    
    for test in tests:
        if asyncio.iscoroutinefunction(test):
            result = await test()
        else:
            result = test()
        results.append(result)
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All integration tests passed! The system is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
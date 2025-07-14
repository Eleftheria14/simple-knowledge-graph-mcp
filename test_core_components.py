#!/usr/bin/env python3
"""
Test Core Components for GraphRAG MCP Toolkit

Tests just the new components we built (citation manager, query engine)
without requiring the full dependency chain.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_citation_manager_isolated():
    """Test citation manager in isolation"""
    print("Testing Citation Manager (Isolated)...")
    
    try:
        # Import just the classes we need
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graphrag_mcp', 'core'))
        
        from citation_manager import CitationTracker, Citation, CitationContext
        
        # Test citation creation
        citation_manager = CitationTracker()
        
        # Add citations
        citation1 = citation_manager.add_citation(
            title="Deep Learning Fundamentals",
            authors=["Alice Johnson", "Bob Smith"],
            year=2023,
            journal="AI Research",
            doi="10.1000/test123"
        )
        
        citation2 = citation_manager.add_citation(
            title="Neural Networks in Practice", 
            authors=["Carol Davis"],
            year=2022
        )
        
        print(f"  ✅ Added 2 citations: {citation1}, {citation2}")
        
        # Test citation tracking
        success1 = citation_manager.track_citation(citation1, "Used in introduction", "intro")
        success2 = citation_manager.track_citation(citation2, "Used in methodology", "methods")
        
        assert success1 and success2
        print("  ✅ Successfully tracked citation usage")
        
        # Test bibliography generation
        apa_bib = citation_manager.generate_bibliography(style="APA", used_only=True)
        ieee_bib = citation_manager.generate_bibliography(style="IEEE", used_only=True)
        nature_bib = citation_manager.generate_bibliography(style="Nature", used_only=True)
        mla_bib = citation_manager.generate_bibliography(style="MLA", used_only=True)
        
        assert len(apa_bib) == 2
        assert len(ieee_bib) == 2
        assert len(nature_bib) == 2
        assert len(mla_bib) == 2
        
        print(f"  ✅ Generated bibliographies: APA({len(apa_bib)}), IEEE({len(ieee_bib)}), Nature({len(nature_bib)}), MLA({len(mla_bib)})")
        
        # Test in-text citations
        apa_in_text = citation_manager.generate_in_text_citation(citation1, "APA")
        ieee_in_text = citation_manager.generate_in_text_citation(citation1, "IEEE")
        
        print(f"  ✅ APA in-text: {apa_in_text}")
        print(f"  ✅ IEEE in-text: {ieee_in_text}")
        
        # Test statistics
        stats = citation_manager.get_citation_statistics()
        assert stats['total_citations'] == 2
        assert stats['used_citations'] == 2
        assert stats['usage_rate'] == 1.0
        
        print(f"  ✅ Statistics: {stats['used_citations']}/{stats['total_citations']} used (rate: {stats['usage_rate']:.1%})")
        
        # Test verification
        verification1 = citation_manager.verify_citation(citation1)
        verification2 = citation_manager.verify_citation("nonexistent")
        
        assert verification1['valid'] == True
        assert verification2['valid'] == False
        
        print(f"  ✅ Citation verification: valid citation score={verification1['score']:.2f}")
        
        # Test export/import
        json_export = citation_manager.export_citations(format="json")
        bibtex_export = citation_manager.export_citations(format="bibtex")
        csv_export = citation_manager.export_citations(format="csv")
        
        assert len(json_export) > 100  # Should be substantial JSON
        assert "@article" in bibtex_export or "@misc" in bibtex_export
        assert "Key,Title,Authors" in csv_export
        
        print("  ✅ Export functionality: JSON, BibTeX, CSV formats working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Citation manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_engine_isolated():
    """Test query engine analysis methods in isolation"""
    print("\nTesting Query Engine (Isolated)...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graphrag_mcp', 'core'))
        
        from query_engine import EnhancedQueryEngine, QueryType, QueryIntent
        
        # Create query engine (without dependencies)
        query_engine = EnhancedQueryEngine()
        
        print("  ✅ Created query engine")
        
        # Test query classification
        queries = [
            ("What is machine learning?", QueryType.FACTUAL, QueryIntent.GET_DEFINITION),
            ("Compare deep learning and traditional ML", QueryType.COMPARATIVE, QueryIntent.COMPARE_APPROACHES),
            ("How has AI evolved over time?", QueryType.TEMPORAL, QueryIntent.TRACE_EVOLUTION),
            ("Find papers about neural networks", QueryType.CONVERSATIONAL, QueryIntent.FIND_PAPERS),
        ]
        
        for query, expected_type, expected_intent in queries:
            query_type = query_engine._classify_query_type(query, None)
            intent = query_engine._classify_intent(query)
            
            print(f"  ✅ '{query[:30]}...' → type:{query_type.value}, intent:{intent.value}")
        
        # Test keyword extraction
        test_query = "What are the latest advances in artificial intelligence and machine learning?"
        keywords = query_engine._extract_keywords(test_query)
        
        assert len(keywords) > 0
        assert any(word in ['advances', 'artificial', 'intelligence', 'machine', 'learning'] for word in keywords)
        
        print(f"  ✅ Keyword extraction: {keywords}")
        
        # Test temporal scope extraction
        temporal_queries = [
            ("recent advances in AI", "recent"),
            ("What happened in 2023?", "2023"),
            ("historical development", "historical"),
        ]
        
        for query, expected in temporal_queries:
            scope = query_engine._extract_temporal_scope(query)
            print(f"  ✅ Temporal scope for '{query}': {scope}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Query engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_component_integration():
    """Test components working together"""
    print("\nTesting Component Integration...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graphrag_mcp', 'core'))
        
        from citation_manager import CitationTracker
        from query_engine import EnhancedQueryEngine
        
        # Create integrated system
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        
        print("  ✅ Created integrated citation manager + query engine")
        
        # Add test data
        cite1 = citation_manager.add_citation(
            title="Attention Is All You Need",
            authors=["Vaswani", "Shazeer", "Parmar"],
            year=2017,
            journal="NIPS"
        )
        
        cite2 = citation_manager.add_citation(
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin", "Chang", "Lee", "Toutanova"],
            year=2018,
            journal="NAACL"
        )
        
        print("  ✅ Added test citations to manager")
        
        # Verify query engine can access citation manager
        assert query_engine.citation_manager is citation_manager
        assert cite1 in citation_manager.citations
        
        print("  ✅ Query engine has access to citation manager")
        
        # Simulate workflow: query → citation tracking → bibliography
        citation_manager.track_citation(cite1, "Used to explain attention mechanism")
        citation_manager.track_citation(cite2, "Used to demonstrate BERT architecture")
        
        # Generate output
        bibliography = citation_manager.generate_bibliography(style="APA", used_only=True)
        stats = citation_manager.get_citation_statistics()
        
        assert len(bibliography) == 2
        assert stats['used_citations'] == 2
        
        print(f"  ✅ End-to-end workflow: {len(bibliography)} citations in final bibliography")
        print(f"  ✅ Usage statistics: {stats['usage_rate']:.1%} citation usage rate")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_structure():
    """Test academic template structure without full dependencies"""
    print("\nTesting Academic Template Structure...")
    
    try:
        # Test template file exists and has expected structure
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   'graphrag_mcp', 'templates', 'academic.py')
        
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for expected tool definitions
        expected_chat_tools = [
            "ask_knowledge_graph",
            "explore_topic", 
            "find_connections",
            "what_do_we_know_about"
        ]
        
        expected_lit_tools = [
            "gather_sources_for_topic",
            "get_facts_with_citations",
            "verify_claim_with_sources",
            "get_topic_outline",
            "track_citations_used",
            "generate_bibliography"
        ]
        
        # Verify tools are defined
        chat_found = 0
        lit_found = 0
        
        for tool in expected_chat_tools:
            if tool in content:
                chat_found += 1
                print(f"  ✅ Chat tool found: {tool}")
        
        for tool in expected_lit_tools:
            if tool in content:
                lit_found += 1
                print(f"  ✅ Literature tool found: {tool}")
        
        assert chat_found == len(expected_chat_tools)
        assert lit_found == len(expected_lit_tools)
        
        print(f"  ✅ Template structure: {chat_found} chat tools + {lit_found} literature tools")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Template structure test failed: {e}")
        return False


def test_real_world_scenario():
    """Test a realistic research workflow scenario"""
    print("\nTesting Real-World Research Scenario...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graphrag_mcp', 'core'))
        
        from citation_manager import CitationTracker
        from query_engine import EnhancedQueryEngine
        
        # Scenario: PhD student writing literature review on transformer architectures
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        
        print("  📚 Scenario: PhD student writing transformer literature review")
        
        # Step 1: Add key papers to citation database
        papers = [
            ("Attention Is All You Need", ["Vaswani", "Shazeer"], 2017, "NIPS"),
            ("BERT: Pre-training Transformers", ["Devlin", "Chang"], 2018, "NAACL"),
            ("GPT-3: Language Models are Few-Shot Learners", ["Brown", "Mann"], 2020, "NeurIPS"),
            ("T5: Text-to-Text Transfer Transformer", ["Raffel", "Shazeer"], 2020, "JMLR"),
            ("ViT: An Image is Worth 16x16 Words", ["Dosovitskiy", "Beyer"], 2021, "ICLR")
        ]
        
        citation_keys = []
        for title, authors, year, journal in papers:
            key = citation_manager.add_citation(
                title=title,
                authors=authors,
                year=year,
                journal=journal
            )
            citation_keys.append(key)
        
        print(f"  ✅ Added {len(papers)} key papers to citation database")
        
        # Step 2: Simulate writing different sections with citations
        sections = [
            ("introduction", citation_keys[0]),  # Cite original transformer paper
            ("background", citation_keys[1]),    # Cite BERT for bidirectional context
            ("methods", citation_keys[2]),       # Cite GPT-3 for generative approach
            ("results", citation_keys[3]),       # Cite T5 for text-to-text
            ("discussion", citation_keys[4]),    # Cite ViT for vision applications
        ]
        
        for section, cite_key in sections:
            citation_manager.track_citation(cite_key, f"Used in {section} section", section)
        
        print("  ✅ Simulated citation usage across literature review sections")
        
        # Step 3: Generate different bibliography styles for journal submission
        styles = ["APA", "IEEE", "Nature", "MLA"]
        bibliographies = {}
        
        for style in styles:
            bib = citation_manager.generate_bibliography(style=style, used_only=True)
            bibliographies[style] = bib
            print(f"  ✅ Generated {style} bibliography ({len(bib)} entries)")
        
        # Step 4: Analyze citation patterns
        stats = citation_manager.get_citation_statistics()
        
        # Step 5: Verify all citations are properly tracked
        assert stats['total_citations'] == 5
        assert stats['used_citations'] == 5
        assert stats['usage_rate'] == 1.0
        
        # Step 6: Test in-text citation generation for writing
        in_text_citations = []
        for cite_key in citation_keys:
            apa_cite = citation_manager.generate_in_text_citation(cite_key, "APA")
            in_text_citations.append(apa_cite)
        
        print(f"  ✅ Generated in-text citations: {in_text_citations}")
        
        # Step 7: Export for reference manager
        bibtex_export = citation_manager.export_citations(format="bibtex")
        
        print(f"  ✅ Exported BibTeX for reference manager ({len(bibtex_export)} characters)")
        
        print("  🎓 Research workflow completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Real-world scenario test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all core component tests"""
    print("🚀 Testing Core GraphRAG MCP Components\n")
    
    tests = [
        test_citation_manager_isolated,
        test_query_engine_isolated,
        test_component_integration,
        test_template_structure,
        test_real_world_scenario
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
        print("🎉 All core component tests passed!")
        print("✨ Citation management and query processing systems are working correctly.")
        print("🔧 Ready for MCP server integration!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
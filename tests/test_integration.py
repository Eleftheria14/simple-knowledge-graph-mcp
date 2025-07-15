"""
Integration Tests for GraphRAG MCP Toolkit

Tests the complete system integration including chat tools, literature review tools,
citation management, and MCP server functionality.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components to test
from graphrag_mcp.core.citation_manager import CitationTracker
from graphrag_mcp.core.query_engine import EnhancedQueryEngine
from graphrag_mcp.mcp.chat_tools import ChatToolsEngine
from graphrag_mcp.mcp.literature_tools import LiteratureToolsEngine
from graphrag_mcp.mcp.server_generator import UniversalMCPServer
from graphrag_mcp.templates.academic import AcademicTemplate


class TestBasicIntegration:
    """Test basic component integration"""

    def test_citation_manager_initialization(self):
        """Test citation manager can be created and used"""
        citation_manager = CitationTracker()

        # Add a citation
        citation_key = citation_manager.add_citation(
            title="Test Paper",
            authors=["John Doe", "Jane Smith"],
            year=2023
        )

        assert citation_key in citation_manager.citations
        assert citation_manager.citations[citation_key].title == "Test Paper"

        # Track usage
        success = citation_manager.track_citation(citation_key, "Test context")
        assert success
        assert citation_key in citation_manager.used_citations

    def test_query_engine_initialization(self):
        """Test query engine can be created with citation manager"""
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)

        assert query_engine.citation_manager is citation_manager

    def test_chat_tools_initialization(self):
        """Test chat tools engine can be created"""
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        chat_tools = ChatToolsEngine(query_engine=query_engine, citation_manager=citation_manager)

        assert chat_tools.query_engine is query_engine
        assert chat_tools.citation_manager is citation_manager

    def test_literature_tools_initialization(self):
        """Test literature tools engine can be created"""
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        literature_tools = LiteratureToolsEngine(query_engine=query_engine, citation_manager=citation_manager)

        assert literature_tools.query_engine is query_engine
        assert literature_tools.citation_manager is citation_manager

    def test_academic_template_tool_definitions(self):
        """Test academic template has the expected tools"""
        template = AcademicTemplate()
        config = template.get_template_config()

        tool_names = [tool.name for tool in config.mcp_tools]

        # Check for chat tools
        assert "ask_knowledge_graph" in tool_names
        assert "explore_topic" in tool_names
        assert "find_connections" in tool_names
        assert "what_do_we_know_about" in tool_names

        # Check for literature review tools
        assert "gather_sources_for_topic" in tool_names
        assert "get_facts_with_citations" in tool_names
        assert "verify_claim_with_sources" in tool_names
        assert "get_topic_outline" in tool_names
        assert "track_citations_used" in tool_names
        assert "generate_bibliography" in tool_names

        # Check for legacy tools
        assert "query_papers" in tool_names
        assert "research_gaps" in tool_names


class TestCitationWorkflow:
    """Test citation tracking across components"""

    def test_citation_tracking_workflow(self):
        """Test complete citation tracking workflow"""
        # Setup components
        citation_manager = CitationTracker()

        # Add some test citations
        citation1 = citation_manager.add_citation(
            title="Deep Learning in NLP",
            authors=["Alice Johnson"],
            year=2023,
            journal="AI Review"
        )

        citation2 = citation_manager.add_citation(
            title="Transformer Networks",
            authors=["Bob Wilson", "Carol Davis"],
            year=2022,
            journal="ML Journal"
        )

        # Track usage
        citation_manager.track_citation(citation1, "Used in introduction")
        citation_manager.track_citation(citation2, "Used in methods section")

        # Generate bibliography
        bibliography = citation_manager.generate_bibliography(style="APA", used_only=True)

        assert len(bibliography) == 2
        assert any("Deep Learning in NLP" in entry for entry in bibliography)
        assert any("Transformer Networks" in entry for entry in bibliography)

        # Check statistics
        stats = citation_manager.get_citation_statistics()
        assert stats["total_citations"] == 2
        assert stats["used_citations"] == 2
        assert stats["usage_rate"] == 1.0


# Mocked tests would go here - skipping for basic integration test


class TestServerIntegration:
    """Test MCP server integration"""

    def test_server_initialization(self):
        """Test that server can be initialized with all components"""
        server = UniversalMCPServer()

        # Check that components are initialized
        assert server.citation_manager is not None
        assert server.query_engine is not None
        assert server.chat_tools is not None
        assert server.literature_tools is not None

        # Check that citation manager is shared
        assert server.query_engine.citation_manager is server.citation_manager
        assert server.chat_tools.citation_manager is server.citation_manager
        assert server.literature_tools.citation_manager is server.citation_manager

    def test_template_loading(self):
        """Test that academic template loads successfully"""
        server = UniversalMCPServer()

        # Academic template should be loaded by default
        assert server.current_template is not None
        assert server.state.current_template == "academic"
        assert isinstance(server.current_template, AcademicTemplate)


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""

    def test_citation_workflow_integration(self):
        """Test complete workflow from citation creation to bibliography"""
        # Initialize system
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        literature_tools = LiteratureToolsEngine(
            query_engine=query_engine,
            citation_manager=citation_manager
        )

        # Add test citations
        citation1 = citation_manager.add_citation(
            title="Machine Learning Fundamentals",
            authors=["Dr. Alice Smith"],
            year=2023,
            journal="AI Research",
            doi="10.1000/test123"
        )

        citation2 = citation_manager.add_citation(
            title="Neural Network Architectures",
            authors=["Prof. Bob Johnson", "Dr. Carol Wilson"],
            year=2022,
            journal="Deep Learning Review"
        )

        # Simulate tool usage that tracks citations
        citation_manager.track_citation(citation1, "Used in background section")
        citation_manager.track_citation(citation2, "Used in methodology")

        # Test bibliography generation through tools
        bibliography = citation_manager.generate_bibliography(style="APA", used_only=True)

        # Verify workflow results
        assert len(bibliography) == 2
        assert citation_manager.get_citation_statistics()["used_citations"] == 2

        # Test different citation styles
        ieee_bibliography = citation_manager.generate_bibliography(style="IEEE", used_only=True)
        assert len(ieee_bibliography) == 2
        assert ieee_bibliography != bibliography  # Different formatting

    def test_tool_component_consistency(self):
        """Test that all tool components use consistent interfaces"""
        # Create shared components
        citation_manager = CitationTracker()
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)

        # Create tool engines
        chat_tools = ChatToolsEngine(
            query_engine=query_engine,
            citation_manager=citation_manager
        )

        literature_tools = LiteratureToolsEngine(
            query_engine=query_engine,
            citation_manager=citation_manager
        )

        # Verify shared state
        assert chat_tools.citation_manager is citation_manager
        assert literature_tools.citation_manager is citation_manager
        assert chat_tools.query_engine is query_engine
        assert literature_tools.query_engine is query_engine

        # Add a citation and verify both tools can access it
        citation_key = citation_manager.add_citation(
            title="Test Integration Paper",
            authors=["Integration Tester"],
            year=2024
        )

        # Both engines should see the same citation
        assert citation_key in chat_tools.citation_manager.citations
        assert citation_key in literature_tools.citation_manager.citations

        # Citation should be the same object
        assert (chat_tools.citation_manager.citations[citation_key] is
                literature_tools.citation_manager.citations[citation_key])


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running basic integration tests...")

    # Test 1: Basic component creation
    try:
        citation_manager = CitationTracker()
        citation_key = citation_manager.add_citation("Test", ["Author"], 2023)
        citation_manager.track_citation(citation_key, "test")
        print("✅ Citation manager integration test passed")
    except Exception as e:
        print(f"❌ Citation manager test failed: {e}")

    # Test 2: Tool engine creation
    try:
        query_engine = EnhancedQueryEngine(citation_manager=citation_manager)
        chat_tools = ChatToolsEngine(query_engine=query_engine, citation_manager=citation_manager)
        literature_tools = LiteratureToolsEngine(query_engine=query_engine, citation_manager=citation_manager)
        print("✅ Tool engines integration test passed")
    except Exception as e:
        print(f"❌ Tool engines test failed: {e}")

    # Test 3: Server creation
    try:
        server = UniversalMCPServer()
        print("✅ MCP server integration test passed")
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")

    # Test 4: Template loading
    try:
        template = AcademicTemplate()
        config = template.get_template_config()
        tool_count = len(config.mcp_tools)
        print(f"✅ Academic template test passed ({tool_count} tools defined)")
    except Exception as e:
        print(f"❌ Academic template test failed: {e}")

    print("\nIntegration tests completed!")

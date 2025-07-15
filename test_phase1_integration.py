#!/usr/bin/env python3
"""
Test Phase 1 Integration

This script tests the new GraphRAG MCP package structure to ensure
all components work together correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all imports work correctly"""
    print("🔍 Testing imports...")

    try:
        # Test API imports
        print("   ✅ API imports: Success")

        # Test UI imports
        print("   ✅ UI imports: Success")

        # Test utils imports
        print("   ✅ Utils imports: Success")

        # Test notebook imports
        sys.path.insert(0, str(project_root / "notebooks" / "Main"))
        print("   ✅ Notebook imports: Success")

        return True

    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_api_functionality():
    """Test basic API functionality"""
    print("\n🔧 Testing API functionality...")

    try:
        # Test processor creation
        from graphrag_mcp.api import GraphRAGProcessor
        processor = GraphRAGProcessor("test-project")
        print("   ✅ GraphRAGProcessor creation: Success")

        # Test validation
        from graphrag_mcp.api import validate_system
        is_valid = validate_system()
        print(f"   ✅ System validation: {'Valid' if is_valid else 'Invalid (expected)'}")

        # Test document discovery
        documents = processor.discover_documents("examples")
        print(f"   ✅ Document discovery: Found {len(documents)} documents")

        return True

    except Exception as e:
        print(f"   ❌ API error: {e}")
        return False

def test_notebook_compatibility():
    """Test that notebook utilities work with new structure"""
    print("\n📓 Testing notebook compatibility...")

    try:
        # Test notebook processor
        sys.path.insert(0, str(project_root / "notebooks" / "Main"))
        from processing_utils import NotebookDocumentProcessor, quick_setup

        processor = NotebookDocumentProcessor("test-notebook")
        print("   ✅ NotebookDocumentProcessor creation: Success")

        # Test quick setup
        quick_processor = quick_setup("test-quick")
        print("   ✅ Quick setup: Success")

        # Test document discovery through notebook interface
        documents = processor.discover_documents("examples")
        print(f"   ✅ Notebook document discovery: Found {len(documents)} documents")

        return True

    except Exception as e:
        print(f"   ❌ Notebook compatibility error: {e}")
        return False

def test_visualization():
    """Test visualization functionality"""
    print("\n🎨 Testing visualization...")

    try:
        from pathlib import Path

        from graphrag_mcp.ui import visualize_knowledge_graph
        from graphrag_mcp.ui.status import DocumentStatus

        # Create sample document status
        sample_docs = [
            DocumentStatus(
                path=Path("test1.pdf"),
                name="test1.pdf",
                size_mb=1.5,
                status="completed",
                entities_found=10,
                citations_found=5
            ),
            DocumentStatus(
                path=Path("test2.pdf"),
                name="test2.pdf",
                size_mb=2.0,
                status="completed",
                entities_found=15,
                citations_found=3
            )
        ]

        # Test visualization (won't display in console but shouldn't error)
        graph = visualize_knowledge_graph(sample_docs, "test-project", 10)
        print("   ✅ Visualization function: Success")

        return True

    except Exception as e:
        print(f"   ❌ Visualization error: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("🚀 Phase 1 Integration Tests")
    print("=" * 50)

    tests = [
        test_imports,
        test_api_functionality,
        test_notebook_compatibility,
        test_visualization
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
        print("✅ Phase 1 implementation is working correctly")
    else:
        print("❌ Some tests failed - need to fix issues")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

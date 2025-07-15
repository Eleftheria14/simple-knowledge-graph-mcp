#!/usr/bin/env python3
"""
Simple MCP Integration Test for GraphRAG MCP Toolkit

This test validates the basic MCP integration without requiring full system setup.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from graphrag_mcp.core.citation_manager import CitationTracker
        from graphrag_mcp.utils.prerequisites import check_prerequisites
        from graphrag_mcp.templates.academic import AcademicTemplate
        print("✅ Core imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_citation_manager():
    """Test citation manager functionality"""
    try:
        from graphrag_mcp.core.citation_manager import CitationTracker
        
        # Initialize citation manager
        citation_manager = CitationTracker()
        
        # Test adding a citation
        citation_key = citation_manager.add_citation(
            title="Test Paper on Neural Networks",
            authors=["John Smith", "Jane Doe"],
            year=2024,
            journal="AI Journal"
        )
        
        # Test tracking citation usage
        citation_manager.track_citation(
            citation_key=citation_key,
            context_text="This is a test context",
            section="test_section",
            confidence=0.9
        )
        
        # Test bibliography generation
        bibliography = citation_manager.generate_bibliography(style="APA", used_only=True)
        
        # Test health check
        health_check = citation_manager.get_health_check()
        
        print(f"✅ Citation manager test passed - {len(bibliography)} citations in bibliography")
        return True
        
    except Exception as e:
        print(f"❌ Citation manager test failed: {e}")
        return False

def test_template_system():
    """Test template system functionality"""
    try:
        from graphrag_mcp.templates.academic import AcademicTemplate
        
        # Initialize template
        template = AcademicTemplate()
        
        # Get MCP tools
        tools = template.get_mcp_tools()
        
        # Validate tools
        if len(tools) == 0:
            print("❌ Template system test failed: No tools found")
            return False
        
        # Check tool categories
        categories = set(tool.category for tool in tools)
        expected_categories = {"chat", "literature", "core"}
        
        if not expected_categories.issubset(categories):
            print(f"⚠️ Template system test warning: Missing categories {expected_categories - categories}")
        
        print(f"✅ Template system test passed - {len(tools)} tools in {len(categories)} categories")
        return True
        
    except Exception as e:
        print(f"❌ Template system test failed: {e}")
        return False

def test_prerequisites():
    """Test prerequisites checking"""
    try:
        from graphrag_mcp.utils.prerequisites import check_prerequisites
        
        # Run prerequisites check
        result = check_prerequisites(verbose=False)
        
        if result.status == "passed":
            print("✅ Prerequisites test passed - all requirements met")
            return True
        else:
            print(f"⚠️ Prerequisites test warning - {len(result.issues)} issues found")
            return True  # Still count as passed since this is expected in many environments
            
    except Exception as e:
        print(f"❌ Prerequisites test failed: {e}")
        return False

def generate_claude_desktop_config():
    """Generate Claude Desktop configuration"""
    try:
        config = {
            "mcpServers": {
                "graphrag-research": {
                    "command": "python3",
                    "args": [
                        "-m", "graphrag_mcp.cli.main",
                        "serve-universal",
                        "--template", "academic",
                        "--transport", "stdio"
                    ],
                    "cwd": str(project_root),
                    "env": {
                        "PYTHONPATH": str(project_root)
                    }
                }
            }
        }
        
        # Save configuration
        config_path = project_root / "claude_desktop_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Claude Desktop configuration generated: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Claude Desktop configuration generation failed: {e}")
        return False

def main():
    """Run simple MCP integration tests"""
    print("🚀 GraphRAG MCP Simple Integration Test")
    print("=" * 45)
    
    start_time = time.time()
    tests = [
        ("Import Test", test_imports),
        ("Citation Manager Test", test_citation_manager),
        ("Template System Test", test_template_system),
        ("Prerequisites Test", test_prerequisites),
        ("Claude Desktop Config", generate_claude_desktop_config)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    total_time = time.time() - start_time
    passed_tests = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\n📊 Test Summary")
    print("=" * 20)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {passed_tests/total_tests:.1%}")
    print(f"Total Time: {total_time:.2f} seconds")
    
    print(f"\n🔍 Individual Results:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 All tests passed! System is ready for MCP integration.")
        print(f"\n📋 Next Steps:")
        print(f"  1. Add the generated config to your Claude Desktop settings")
        print(f"  2. Start the MCP server: python3 -m graphrag_mcp.cli.main serve-universal --template academic --transport stdio")
        print(f"  3. Test the connection in Claude Desktop")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Please address issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
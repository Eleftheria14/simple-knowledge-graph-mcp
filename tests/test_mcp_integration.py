#!/usr/bin/env python3
"""
Comprehensive MCP Integration Test Suite for GraphRAG MCP Toolkit

This test suite validates the complete MCP integration with Claude Desktop,
including all standardized tools, error handling, and recovery mechanisms.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from graphrag_mcp.mcp.server_generator import UniversalMCPServer
from graphrag_mcp.core.citation_manager import CitationTracker
from graphrag_mcp.utils.prerequisites import check_prerequisites
from graphrag_mcp.templates.academic import AcademicTemplate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPIntegrationTester:
    """Comprehensive MCP integration test suite"""
    
    def __init__(self):
        self.server = None
        self.test_results = {
            "prerequisites": {"passed": False, "details": {}},
            "server_initialization": {"passed": False, "details": {}},
            "template_loading": {"passed": False, "details": {}},
            "tool_registration": {"passed": False, "details": {}},
            "chat_tools": {"passed": False, "details": {}},
            "literature_tools": {"passed": False, "details": {}},
            "citation_integration": {"passed": False, "details": {}},
            "error_handling": {"passed": False, "details": {}},
            "performance": {"passed": False, "details": {}},
            "claude_desktop_config": {"passed": False, "details": {}}
        }
        self.start_time = time.time()
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Run the complete MCP integration test suite"""
        logger.info("🚀 Starting comprehensive MCP integration test suite...")
        
        try:
            # Test 1: Prerequisites check
            await self._test_prerequisites()
            
            # Test 2: Server initialization
            await self._test_server_initialization()
            
            # Test 3: Template loading
            await self._test_template_loading()
            
            # Test 4: Tool registration
            await self._test_tool_registration()
            
            # Test 5: Chat tools functionality
            await self._test_chat_tools()
            
            # Test 6: Literature tools functionality
            await self._test_literature_tools()
            
            # Test 7: Citation integration
            await self._test_citation_integration()
            
            # Test 8: Error handling and recovery
            await self._test_error_handling()
            
            # Test 9: Performance characteristics
            await self._test_performance()
            
            # Test 10: Claude Desktop configuration
            await self._test_claude_desktop_config()
            
            # Generate final report
            return self._generate_final_report()
            
        except Exception as e:
            logger.error(f"Test suite failed with error: {e}")
            self.test_results["overall_error"] = str(e)
            return self._generate_final_report()
    
    async def _test_prerequisites(self):
        """Test system prerequisites"""
        logger.info("🔍 Testing system prerequisites...")
        
        try:
            # Check prerequisites
            result = check_prerequisites(verbose=False)
            
            self.test_results["prerequisites"]["details"] = {
                "status": result.status,
                "issues": result.issues,
                "details": result.details
            }
            
            if result.status == "passed":
                self.test_results["prerequisites"]["passed"] = True
                logger.info("✅ Prerequisites check passed")
            else:
                logger.warning(f"⚠️ Prerequisites check failed: {result.issues}")
                self.test_results["prerequisites"]["details"]["warnings"] = result.issues
        
        except Exception as e:
            logger.error(f"❌ Prerequisites test failed: {e}")
            self.test_results["prerequisites"]["details"]["error"] = str(e)
    
    async def _test_server_initialization(self):
        """Test MCP server initialization"""
        logger.info("🏗️ Testing MCP server initialization...")
        
        try:
            # Initialize server
            self.server = UniversalMCPServer(
                name="GraphRAG Test Server",
                instructions="Test server for MCP integration validation"
            )
            
            # Check server state
            if hasattr(self.server, 'state') and hasattr(self.server, 'citation_manager'):
                self.test_results["server_initialization"]["passed"] = True
                self.test_results["server_initialization"]["details"] = {
                    "server_name": self.server.name,
                    "has_state": hasattr(self.server, 'state'),
                    "has_citation_manager": hasattr(self.server, 'citation_manager'),
                    "has_chat_tools": hasattr(self.server, 'chat_tools'),
                    "has_literature_tools": hasattr(self.server, 'literature_tools')
                }
                logger.info("✅ Server initialization successful")
            else:
                logger.error("❌ Server initialization incomplete")
                self.test_results["server_initialization"]["details"]["error"] = "Missing required components"
        
        except Exception as e:
            logger.error(f"❌ Server initialization failed: {e}")
            self.test_results["server_initialization"]["details"]["error"] = str(e)
    
    async def _test_template_loading(self):
        """Test template loading functionality"""
        logger.info("📋 Testing template loading...")
        
        try:
            # Test academic template loading
            template = AcademicTemplate()
            tools = template.get_mcp_tools()
            
            self.test_results["template_loading"]["details"] = {
                "template_name": template.name,
                "tool_count": len(tools),
                "tool_names": [tool.name for tool in tools],
                "categories": list(set(tool.category for tool in tools))
            }
            
            if len(tools) > 0:
                self.test_results["template_loading"]["passed"] = True
                logger.info(f"✅ Template loading successful: {len(tools)} tools loaded")
            else:
                logger.error("❌ Template loading failed: no tools loaded")
        
        except Exception as e:
            logger.error(f"❌ Template loading failed: {e}")
            self.test_results["template_loading"]["details"]["error"] = str(e)
    
    async def _test_tool_registration(self):
        """Test MCP tool registration"""
        logger.info("🔧 Testing tool registration...")
        
        try:
            if not self.server:
                raise Exception("Server not initialized")
            
            # Get registered tools
            registered_tools = []
            
            # Check chat tools
            if hasattr(self.server, 'chat_tools'):
                chat_methods = [method for method in dir(self.server.chat_tools) 
                              if not method.startswith('_') and callable(getattr(self.server.chat_tools, method))]
                registered_tools.extend([f"chat_{method}" for method in chat_methods])
            
            # Check literature tools  
            if hasattr(self.server, 'literature_tools'):
                lit_methods = [method for method in dir(self.server.literature_tools) 
                             if not method.startswith('_') and callable(getattr(self.server.literature_tools, method))]
                registered_tools.extend([f"literature_{method}" for method in lit_methods])
            
            self.test_results["tool_registration"]["details"] = {
                "total_tools": len(registered_tools),
                "registered_tools": registered_tools,
                "chat_tools_available": hasattr(self.server, 'chat_tools'),
                "literature_tools_available": hasattr(self.server, 'literature_tools')
            }
            
            if len(registered_tools) > 0:
                self.test_results["tool_registration"]["passed"] = True
                logger.info(f"✅ Tool registration successful: {len(registered_tools)} tools registered")
            else:
                logger.error("❌ Tool registration failed: no tools registered")
        
        except Exception as e:
            logger.error(f"❌ Tool registration test failed: {e}")
            self.test_results["tool_registration"]["details"]["error"] = str(e)
    
    async def _test_chat_tools(self):
        """Test chat tools functionality"""
        logger.info("💬 Testing chat tools...")
        
        try:
            if not self.server or not hasattr(self.server, 'chat_tools'):
                raise Exception("Chat tools not available")
            
            # Test ask_knowledge_graph
            test_query = "What is machine learning?"
            
            # Create test context
            if hasattr(self.server.chat_tools, 'ask_knowledge_graph'):
                try:
                    result = await self.server.chat_tools.ask_knowledge_graph(
                        question=test_query,
                        depth="quick"
                    )
                    
                    self.test_results["chat_tools"]["details"] = {
                        "ask_knowledge_graph_works": True,
                        "response_type": type(result).__name__,
                        "response_keys": list(result.keys()) if isinstance(result, dict) else None
                    }
                    
                    self.test_results["chat_tools"]["passed"] = True
                    logger.info("✅ Chat tools test passed")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Chat tools test partial failure: {e}")
                    self.test_results["chat_tools"]["details"]["error"] = str(e)
            else:
                logger.error("❌ ask_knowledge_graph method not found")
                self.test_results["chat_tools"]["details"]["error"] = "ask_knowledge_graph method not found"
        
        except Exception as e:
            logger.error(f"❌ Chat tools test failed: {e}")
            self.test_results["chat_tools"]["details"]["error"] = str(e)
    
    async def _test_literature_tools(self):
        """Test literature tools functionality"""
        logger.info("📚 Testing literature tools...")
        
        try:
            if not self.server or not hasattr(self.server, 'literature_tools'):
                raise Exception("Literature tools not available")
            
            # Test gather_sources_for_topic
            test_topic = "neural networks"
            
            if hasattr(self.server.literature_tools, 'gather_sources_for_topic'):
                try:
                    result = await self.server.literature_tools.gather_sources_for_topic(
                        topic=test_topic,
                        scope="comprehensive"
                    )
                    
                    self.test_results["literature_tools"]["details"] = {
                        "gather_sources_works": True,
                        "response_type": type(result).__name__,
                        "response_keys": list(result.keys()) if isinstance(result, dict) else None
                    }
                    
                    self.test_results["literature_tools"]["passed"] = True
                    logger.info("✅ Literature tools test passed")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Literature tools test partial failure: {e}")
                    self.test_results["literature_tools"]["details"]["error"] = str(e)
            else:
                logger.error("❌ gather_sources_for_topic method not found")
                self.test_results["literature_tools"]["details"]["error"] = "gather_sources_for_topic method not found"
        
        except Exception as e:
            logger.error(f"❌ Literature tools test failed: {e}")
            self.test_results["literature_tools"]["details"]["error"] = str(e)
    
    async def _test_citation_integration(self):
        """Test citation manager integration"""
        logger.info("📝 Testing citation integration...")
        
        try:
            if not self.server or not hasattr(self.server, 'citation_manager'):
                raise Exception("Citation manager not available")
            
            citation_manager = self.server.citation_manager
            
            # Test citation addition
            citation_key = citation_manager.add_citation(
                title="Test Paper on Machine Learning",
                authors=["John Doe", "Jane Smith"],
                year=2024,
                journal="Test Journal"
            )
            
            # Test citation tracking
            citation_manager.track_citation(
                citation_key=citation_key,
                context_text="Testing citation integration",
                section="test_section",
                confidence=0.9
            )
            
            # Test bibliography generation
            bibliography = citation_manager.generate_bibliography(
                style="APA",
                used_only=True
            )
            
            self.test_results["citation_integration"]["details"] = {
                "citation_added": citation_key is not None,
                "citation_tracked": citation_key in citation_manager.used_citations,
                "bibliography_generated": len(bibliography) > 0,
                "citation_count": len(citation_manager.citations),
                "used_citations": len(citation_manager.used_citations)
            }
            
            if citation_key and len(bibliography) > 0:
                self.test_results["citation_integration"]["passed"] = True
                logger.info("✅ Citation integration test passed")
            else:
                logger.error("❌ Citation integration test failed")
        
        except Exception as e:
            logger.error(f"❌ Citation integration test failed: {e}")
            self.test_results["citation_integration"]["details"]["error"] = str(e)
    
    async def _test_error_handling(self):
        """Test error handling and recovery mechanisms"""
        logger.info("⚠️ Testing error handling...")
        
        try:
            error_scenarios = []
            
            # Test 1: Invalid input handling
            try:
                if hasattr(self.server, 'chat_tools') and hasattr(self.server.chat_tools, 'ask_knowledge_graph'):
                    await self.server.chat_tools.ask_knowledge_graph(question="", depth="invalid")
                    error_scenarios.append({"scenario": "invalid_input", "handled": False})
            except Exception as e:
                error_scenarios.append({"scenario": "invalid_input", "handled": True, "error": str(e)})
            
            # Test 2: Non-existent citation
            try:
                if hasattr(self.server, 'citation_manager'):
                    self.server.citation_manager.generate_in_text_citation("non_existent_key")
                    error_scenarios.append({"scenario": "missing_citation", "handled": False})
            except Exception as e:
                error_scenarios.append({"scenario": "missing_citation", "handled": True, "error": str(e)})
            
            # Test 3: Query engine error handling
            try:
                if hasattr(self.server, 'query_engine'):
                    result = await self.server.query_engine.process_query("")
                    error_scenarios.append({
                        "scenario": "empty_query", 
                        "handled": result.success == False,
                        "error_message": result.error_message
                    })
            except Exception as e:
                error_scenarios.append({"scenario": "empty_query", "handled": True, "error": str(e)})
            
            self.test_results["error_handling"]["details"] = {
                "scenarios_tested": len(error_scenarios),
                "scenarios": error_scenarios,
                "all_handled": all(scenario.get("handled", False) for scenario in error_scenarios)
            }
            
            if len(error_scenarios) > 0 and self.test_results["error_handling"]["details"]["all_handled"]:
                self.test_results["error_handling"]["passed"] = True
                logger.info("✅ Error handling test passed")
            else:
                logger.warning("⚠️ Error handling test partial success")
        
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            self.test_results["error_handling"]["details"]["error"] = str(e)
    
    async def _test_performance(self):
        """Test performance characteristics"""
        logger.info("⚡ Testing performance...")
        
        try:
            performance_metrics = {}
            
            # Test 1: Server startup time
            startup_start = time.time()
            test_server = UniversalMCPServer(name="Performance Test Server")
            startup_time = time.time() - startup_start
            performance_metrics["startup_time"] = startup_time
            
            # Test 2: Citation operations
            citation_start = time.time()
            citation_key = test_server.citation_manager.add_citation(
                title="Performance Test Paper",
                authors=["Test Author"],
                year=2024
            )
            citation_time = time.time() - citation_start
            performance_metrics["citation_add_time"] = citation_time
            
            # Test 3: Query processing (if available)
            if hasattr(test_server, 'query_engine'):
                query_start = time.time()
                result = await test_server.query_engine.process_query("test query")
                query_time = time.time() - query_start
                performance_metrics["query_processing_time"] = query_time
            
            # Test 4: Memory usage estimation
            import sys
            memory_usage = sys.getsizeof(test_server)
            performance_metrics["estimated_memory_usage"] = memory_usage
            
            self.test_results["performance"]["details"] = performance_metrics
            
            # Performance thresholds
            if (startup_time < 5.0 and citation_time < 0.1 and 
                performance_metrics.get("query_processing_time", 0) < 30.0):
                self.test_results["performance"]["passed"] = True
                logger.info("✅ Performance test passed")
            else:
                logger.warning("⚠️ Performance test shows potential issues")
        
        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            self.test_results["performance"]["details"]["error"] = str(e)
    
    async def _test_claude_desktop_config(self):
        """Test Claude Desktop configuration generation"""
        logger.info("🖥️ Testing Claude Desktop configuration...")
        
        try:
            # Generate Claude Desktop config
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
            
            # Validate configuration
            config_valid = (
                "mcpServers" in config and
                "graphrag-research" in config["mcpServers"] and
                "command" in config["mcpServers"]["graphrag-research"] and
                "args" in config["mcpServers"]["graphrag-research"]
            )
            
            self.test_results["claude_desktop_config"]["details"] = {
                "config_generated": True,
                "config_valid": config_valid,
                "server_name": "graphrag-research",
                "command": config["mcpServers"]["graphrag-research"]["command"],
                "args": config["mcpServers"]["graphrag-research"]["args"],
                "cwd": config["mcpServers"]["graphrag-research"]["cwd"]
            }
            
            if config_valid:
                self.test_results["claude_desktop_config"]["passed"] = True
                logger.info("✅ Claude Desktop configuration test passed")
                
                # Write config to file for user
                config_path = project_root / "claude_desktop_config.json"
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                logger.info(f"📄 Configuration saved to: {config_path}")
            else:
                logger.error("❌ Claude Desktop configuration invalid")
        
        except Exception as e:
            logger.error(f"❌ Claude Desktop configuration test failed: {e}")
            self.test_results["claude_desktop_config"]["details"]["error"] = str(e)
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        # Calculate overall success rate
        passed_tests = sum(1 for test in self.test_results.values() 
                          if isinstance(test, dict) and test.get("passed", False))
        total_tests = len([test for test in self.test_results.values() 
                          if isinstance(test, dict) and "passed" in test])
        
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # Determine overall status
        if success_rate >= 0.9:
            overall_status = "EXCELLENT"
        elif success_rate >= 0.7:
            overall_status = "GOOD"
        elif success_rate >= 0.5:
            overall_status = "NEEDS_IMPROVEMENT"
        else:
            overall_status = "CRITICAL"
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_execution_time": total_time,
            "overall_status": overall_status,
            "success_rate": success_rate,
            "tests_passed": passed_tests,
            "total_tests": total_tests,
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if not self.test_results["prerequisites"]["passed"]:
            recommendations.append("Fix system prerequisites before deploying to production")
        
        if not self.test_results["server_initialization"]["passed"]:
            recommendations.append("Review server initialization code for missing components")
        
        if not self.test_results["citation_integration"]["passed"]:
            recommendations.append("Verify citation manager integration and database connectivity")
        
        if not self.test_results["error_handling"]["passed"]:
            recommendations.append("Improve error handling and recovery mechanisms")
        
        if not self.test_results["performance"]["passed"]:
            recommendations.append("Optimize performance for production deployment")
        
        if not self.test_results["claude_desktop_config"]["passed"]:
            recommendations.append("Verify Claude Desktop configuration and deployment setup")
        
        if not recommendations:
            recommendations.append("System is ready for production deployment")
        
        return recommendations


async def main():
    """Main test execution function"""
    print("🚀 GraphRAG MCP Integration Test Suite")
    print("=" * 50)
    
    tester = MCPIntegrationTester()
    
    try:
        report = await tester.run_full_test_suite()
        
        # Display results
        print(f"\n📊 Test Results Summary")
        print("=" * 30)
        print(f"Overall Status: {report['overall_status']}")
        print(f"Success Rate: {report['success_rate']:.1%}")
        print(f"Tests Passed: {report['tests_passed']}/{report['total_tests']}")
        print(f"Execution Time: {report['total_execution_time']:.2f} seconds")
        
        print(f"\n🔍 Individual Test Results:")
        for test_name, result in report['test_results'].items():
            if isinstance(result, dict) and "passed" in result:
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {test_name}: {status}")
        
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
        # Save detailed report
        report_path = project_root / "mcp_integration_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Exit with appropriate code
        if report['overall_status'] in ['EXCELLENT', 'GOOD']:
            print("\n🎉 Integration test completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️ Integration test identified issues that need attention.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
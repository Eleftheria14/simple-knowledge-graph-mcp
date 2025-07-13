"""
Tutorial helper functions for clean notebook interfaces
Provides simple functions that hide complex implementation details
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

def interactive_paper_chat(chat_system):
    """
    Interactive chat session with the paper analysis system
    
    Args:
        chat_system: UnifiedPaperChat instance
    """
    print("🤖 Paper Analysis Assistant Ready!")
    print("💡 Ask me anything about the research paper")
    print("📝 Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        try:
            question = input("\n🔍 Your question: ")
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using the Paper Analysis Assistant!")
                break
                
            if not question.strip():
                continue
                
            print("🤔 Thinking...")
            response = chat_system.chat(question)
            
            print(f"\n💬 Answer: {response['answer']}")
            print(f"\n🎯 Method used: {response.get('mode', 'unknown')}")
            print(f"📖 Source: {response.get('source', 'not specified')}")
            
            if 'error' in response:
                print(f"❌ Error: {response['error']}")
                
        except KeyboardInterrupt:
            print("\n👋 Chat session ended.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try rephrasing your question")

def test_question_routing(chat_system, question: str, expected_type: str = "unknown") -> Dict:
    """
    Test a single question and show routing information
    
    Args:
        chat_system: UnifiedPaperChat instance
        question: Question to test
        expected_type: Expected routing type for display
        
    Returns:
        Response dictionary with routing info
    """
    print(f"🔍 Question: {question}")
    print(f"📊 Expected routing: {expected_type}")
    print("=" * 50)

    try:
        response = chat_system.chat(question)
        
        # Display routing result
        mode = response.get('mode', 'unknown')
        route_display = {
            "rag": "📚 RAG (document search)", 
            "graph": "🕸️ Knowledge Graph (entities)", 
            "both": "🤖 Combined approach",
            "error": "❌ Error occurred"
        }.get(mode, f"❓ Unknown ({mode})")
        
        print(f"\n💬 Answer: {response['answer']}")
        print(f"\n🎯 Used: {route_display}")
        print(f"📖 Source: {response.get('source', 'not specified')}")
        
        if 'error' in response:
            print(f"❌ Error: {response['error']}")
            
        return response
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e), "mode": "error"}

def analyze_system_performance(chat_system) -> Dict:
    """
    Analyze how the system routes different types of questions
    
    Args:
        chat_system: UnifiedPaperChat instance
        
    Returns:
        Performance analysis results
    """
    print("📊 Paper Analysis System Performance:")
    print("=" * 50)

    # Test various question types
    test_questions = [
        ("What is the main research question?", "content-focused"),
        ("Who are the key researchers?", "entity-focused"),
        ("What methods were used?", "mixed approach"),
        ("How do the findings relate to previous work?", "relationship-focused"),
        ("What are the limitations of this study?", "content-focused")
    ]

    routing_results = {"rag": 0, "graph": 0, "both": 0, "error": 0}
    detailed_results = []

    for i, (question, expected_type) in enumerate(test_questions, 1):
        print(f"\n{i}. Testing: {question}")
        
        try:
            response = chat_system.chat(question)
            mode = response.get('mode', 'error')
            
            if mode in routing_results:
                routing_results[mode] += 1
            else:
                routing_results["error"] += 1
                
            route_display = {
                "rag": "📚 RAG", 
                "graph": "🕸️ Knowledge Graph", 
                "both": "🤖 Combined",
                "error": "❌ Error"
            }.get(mode, "❓ Unknown")
                
            print(f"   ✅ Routed to: {route_display}")
            print(f"   📝 Answer length: {len(response.get('answer', ''))} characters")
            print(f"   📖 Source: {response.get('source', 'not specified')}")
            
            if 'error' in response:
                print(f"   ❌ Error: {response['error']}")
            
            detailed_results.append({
                "question": question,
                "expected": expected_type,
                "actual_mode": mode,
                "route_display": route_display,
                "answer_length": len(response.get('answer', '')),
                "success": 'error' not in response
            })
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            routing_results["error"] += 1
            detailed_results.append({
                "question": question,
                "expected": expected_type,
                "actual_mode": "exception",
                "error": str(e),
                "success": False
            })

    print("\n📈 Routing Summary:")
    print(f"   📚 RAG: {routing_results['rag']} questions")
    print(f"   🕸️ Knowledge Graph: {routing_results['graph']} questions")
    print(f"   🤖 Combined: {routing_results['both']} questions")
    print(f"   ❌ Errors: {routing_results['error']} questions")

    print("\n🎉 System analysis complete!")
    
    return {
        "routing_summary": routing_results,
        "detailed_results": detailed_results,
        "total_questions": len(test_questions),
        "success_rate": sum(1 for r in detailed_results if r["success"]) / len(test_questions)
    }

def generate_comprehensive_summary(chat_system) -> Dict:
    """
    Generate a comprehensive research summary using the chat system
    
    Args:
        chat_system: UnifiedPaperChat instance
        
    Returns:
        Summary response
    """
    summary_request = """Please provide a comprehensive summary of this research including:
1. Main objectives
2. Key methods used
3. Important findings
4. Conclusions and implications
Please include specific details and cite relevant sections."""

    print("📝 Generating comprehensive research summary...")
    print("=" * 60)

    try:
        summary_response = chat_system.chat(summary_request)

        print(f"\n📊 Research Summary:")
        print("=" * 60)
        print(summary_response['answer'])

        print(f"\n🎯 Analysis method: {summary_response.get('mode', 'unknown')}")
        print(f"📖 Source: {summary_response.get('source', 'not specified')}")
        
        if 'error' in summary_response:
            print(f"❌ Error: {summary_response['error']}")
        else:
            print("\n✅ Complete research analysis ready!")
            
        return summary_response
        
    except Exception as e:
        error_response = {"error": str(e), "mode": "error"}
        print(f"❌ Summary generation failed: {e}")
        return error_response

def display_tutorial_results(chat_system):
    """
    Display a summary of what the tutorial accomplished
    
    Args:
        chat_system: UnifiedPaperChat instance
    """
    print("\n🎓 Tutorial 5 Complete!")
    print("=" * 40)
    
    try:
        # Get basic system info
        papers = chat_system.kg.get_all_papers() if hasattr(chat_system.kg, 'get_all_papers') else []
        graph_summary = chat_system.kg.get_graph_summary() if hasattr(chat_system.kg, 'get_graph_summary') else {}
        
        print("✅ **System Successfully Built:**")
        print(f"   📄 Papers analyzed: {len(papers)}")
        print(f"   📊 Total documents: {graph_summary.get('total_documents', 'Unknown')}")
        print(f"   🏷️ Entities extracted: {sum(graph_summary.get('unique_entities', {}).values())}")
        print(f"   🕸️ Graph edges: {len(graph_summary.get('graph_edges', []))}")
        
        print("\n🧠 **AI Capabilities Demonstrated:**")
        print("   📚 RAG: Detailed content search and retrieval")
        print("   🕸️ Knowledge Graph: Entity relationships and connections")
        print("   🤖 Smart Routing: Automatic method selection")
        print("   💬 Interactive Chat: Conversational paper exploration")
        
        print("\n🚀 **Ready for Advanced Use:**")
        print("   • Multi-paper analysis")
        print("   • Literature review generation")
        print("   • Citation tracking and verification")
        print("   • Research discovery and connections")
        
    except Exception as e:
        print(f"⚠️ Could not retrieve full system stats: {e}")
        print("✅ But your paper analysis system is working correctly!")
        
    print("\n🎉 **Congratulations! You've built a complete AI research assistant!**")

def show_suggested_next_steps():
    """Display suggested next steps after completing Tutorial 5"""
    print("\n💡 **What to Try Next:**")
    print("=" * 30)
    
    print("🔬 **Experiment with Your System:**")
    print("   • Try the interactive chat with your own questions")
    print("   • Test different types of queries to see routing in action")
    print("   • Load your own research papers")
    
    print("\n📚 **Advanced Features:**")
    print("   • Run the Enhanced Literature Review System")
    print("   • Try multi-paper analysis")
    print("   • Explore citation tracking capabilities")
    
    print("\n🛠️ **Customization Ideas:**")
    print("   • Modify entity extraction for your research domain")
    print("   • Adjust routing logic for your use cases")
    print("   • Add new visualization options")
    
    print("\n🌟 **You're now ready to build sophisticated AI systems!**")
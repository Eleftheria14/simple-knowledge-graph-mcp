"""
Unified Paper Chat Interface
Combines RAG and Knowledge Graph for intelligent paper analysis and chat.
"""

from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
from .simple_paper_rag import SimplePaperRAG
from .langchain_graph_rag import LangChainGraphRAG
from .enhanced_paper_analyzer import EnhancedPaperAnalyzer
from .citation_tracker import CitationTracker

logger = logging.getLogger(__name__)


class UnifiedPaperChat:
    """
    Unified interface combining RAG and Knowledge Graph for comprehensive paper analysis.
    Provides intelligent routing between RAG queries and graph exploration.
    """
    
    def __init__(self, embedding_model: str = "nomic-embed-text", 
                 llm_model: str = "llama3.1:8b"):
        """Initialize the unified system"""
        self.rag = SimplePaperRAG(embedding_model, llm_model)
        self.kg = LangChainGraphRAG(llm_model, embedding_model)
        self.enhanced_analyzer = EnhancedPaperAnalyzer(embedding_model, llm_model)
        self.citation_tracker = CitationTracker()
        
        self.paper_loaded = False
        self.entities_extracted = False
        
        logger.info("🚀 UnifiedPaperChat initialized")
    
    def load_paper(self, pdf_path: str) -> Dict:
        """
        Load paper and build both RAG and Knowledge Graph
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Complete analysis results
        """
        logger.info(f"📚 Loading paper for unified analysis: {pdf_path}")
        
        # Load paper into RAG system
        paper_info = self.rag.load_paper(pdf_path)
        self.paper_loaded = True
        
        # Extract entities and build knowledge graph
        logger.info("🕸️ Building knowledge graph...")
        paper_id = f"paper_{hash(pdf_path) % 10000}"
        kg_result = self.kg.extract_entities_and_relationships(
            self.rag.paper_data['content'],
            self.rag.paper_data['title'],
            paper_id
        )
        self.entities_extracted = True
        
        # Also store entities in RAG system for cross-reference
        self.rag.paper_data['entities'] = kg_result['entities']
        
        result = {
            'paper_info': paper_info,
            'knowledge_graph': kg_result,
            'status': 'ready',
            'capabilities': [
                'rag_queries',
                'entity_exploration', 
                'relationship_discovery',
                'graph_navigation'
            ]
        }
        
        logger.info("✅ Paper fully loaded with RAG + Knowledge Graph")
        return result
    
    def chat(self, message: str, mode: str = "auto") -> Dict:
        """
        Intelligent chat interface that routes queries appropriately
        
        Args:
            message: User's question or command
            mode: "auto", "rag", "graph", or "both"
            
        Returns:
            Response with source information
        """
        if not self.paper_loaded:
            return {
                'error': 'No paper loaded. Please load a paper first.',
                'suggestion': 'Use load_paper(pdf_path) to get started.'
            }
        
        # Determine the best approach based on message content
        if mode == "auto":
            mode = self._determine_mode(message)
        
        if mode == "rag":
            return self._rag_response(message)
        elif mode == "graph":
            return self._graph_response(message)
        elif mode == "both":
            return self._combined_response(message)
        else:
            return {'error': f'Unknown mode: {mode}'}
    
    def _determine_mode(self, message: str) -> str:
        """Determine the best mode based on message content"""
        message_lower = message.lower()
        
        # Graph-oriented keywords
        graph_keywords = [
            'entities', 'relationships', 'connections', 'related to',
            'authors', 'methods', 'concepts', 'who', 'what methods',
            'connected', 'network', 'graph', 'entity'
        ]
        
        # RAG-oriented keywords  
        rag_keywords = [
            'explain', 'describe', 'how', 'why', 'findings', 'results',
            'conclusion', 'discussion', 'analysis', 'detailed',
            'methodology', 'approach', 'experiments'
        ]
        
        # Count keyword matches
        graph_score = sum(1 for keyword in graph_keywords if keyword in message_lower)
        rag_score = sum(1 for keyword in rag_keywords if keyword in message_lower)
        
        if graph_score > rag_score:
            return "graph"
        elif rag_score > graph_score:
            return "rag"
        else:
            return "both"  # Use both when unclear
    
    def _rag_response(self, message: str) -> Dict:
        """Generate response using RAG system"""
        try:
            answer = self.rag.query(message)
            return {
                'answer': answer,
                'mode': 'rag',
                'source': 'document_content',
                'confidence': 'high'
            }
        except Exception as e:
            return {
                'error': f'RAG query failed: {str(e)}',
                'mode': 'rag'
            }
    
    def _graph_response(self, message: str) -> Dict:
        """Generate response using Knowledge Graph"""
        try:
            # Simple entity-based responses
            message_lower = message.lower()
            
            if 'authors' in message_lower:
                papers = self.kg.get_all_papers()
                if papers:
                    paper = papers[0]
                    authors = paper.get('authors', [])
                    if authors:
                        return {
                            'answer': f"The authors of this paper are: {', '.join(authors)}",
                            'mode': 'graph',
                            'source': 'knowledge_graph',
                            'entities': authors
                        }
            
            elif 'methods' in message_lower:
                result = self.kg.query_graph("methods")
                papers = result.get('papers', {})
                if papers:
                    paper = list(papers.values())[0]
                    methods = paper.get('entities', {}).get('methods', [])
                    if methods:
                        return {
                            'answer': f"The methods mentioned in this paper include: {', '.join(methods)}",
                            'mode': 'graph',
                            'source': 'knowledge_graph',
                            'entities': methods
                        }
            
            elif 'concepts' in message_lower:
                result = self.kg.query_graph("concepts")
                papers = result.get('papers', {})
                if papers:
                    paper = list(papers.values())[0]
                    concepts = paper.get('entities', {}).get('concepts', [])
                    if concepts:
                        return {
                            'answer': f"Key concepts in this paper: {', '.join(concepts)}",
                            'mode': 'graph',
                            'source': 'knowledge_graph',
                            'entities': concepts
                        }
            
            # Query graph for entity connections
            query_result = self.kg.query_graph(message)
            if query_result.get('papers'):
                papers = query_result['papers']
                paper_summaries = []
                for paper_id, paper_data in papers.items():
                    title = paper_data.get('paper_title', paper_id)
                    entities = paper_data.get('entities', {})
                    paper_summaries.append(f"Paper: {title}")
                    for entity_type, entity_list in entities.items():
                        if entity_list:
                            paper_summaries.append(f"  {entity_type}: {', '.join(entity_list[:3])}")
                
                return {
                    'answer': f"Found related information:\n" + "\n".join(paper_summaries[:10]),
                    'mode': 'graph',
                    'source': 'knowledge_graph',
                    'query_result': query_result
                }
            
            # Default graph response
            summary = self.kg.get_graph_summary()
            return {
                'answer': f"This paper's knowledge graph contains {summary.get('total_nodes', 0)} entities and {summary.get('total_edges', 0)} relationships.",
                'mode': 'graph',
                'source': 'knowledge_graph',
                'graph_summary': summary
            }
            
        except Exception as e:
            return {
                'error': f'Graph query failed: {str(e)}',
                'mode': 'graph'
            }
    
    def _combined_response(self, message: str) -> Dict:
        """Generate response using both RAG and Knowledge Graph"""
        try:
            # Get RAG response
            rag_result = self._rag_response(message)
            
            # Get relevant entities for context
            graph_summary = self.kg.get_graph_summary()
            
            # Enhance RAG response with graph context
            if 'answer' in rag_result:
                enhanced_answer = rag_result['answer']
                
                # Add entity context if available
                if graph_summary.get('total_nodes', 0) > 0:
                    enhanced_answer += f"\n\n**Related entities from knowledge graph:** "
                    
                    # Add top entities
                    most_connected = graph_summary.get('most_connected', [])
                    if most_connected:
                        top_entities = [item['node'] for item in most_connected[:3]]
                        enhanced_answer += f"{', '.join(top_entities)}"
                
                return {
                    'answer': enhanced_answer,
                    'mode': 'both',
                    'rag_source': 'document_content',
                    'graph_context': graph_summary,
                    'confidence': 'high'
                }
            else:
                return rag_result
                
        except Exception as e:
            return {
                'error': f'Combined query failed: {str(e)}',
                'mode': 'both'
            }
    
    def get_entities(self) -> Dict:
        """Get all extracted entities"""
        if not self.entities_extracted:
            return {'error': 'Entities not extracted yet. Load a paper first.'}
        
        papers = self.kg.get_all_papers()
        if papers:
            # Return entities from the first (or latest) paper
            first_paper = papers[0]
            paper_id = first_paper['paper_id']
            corpus_doc = self.kg.export_for_corpus(paper_id)
            if corpus_doc:
                return corpus_doc.get('metadata', {})
        
        return {'error': 'No entities found'}
    
    def explore_entity(self, entity_name: str) -> Dict:
        """Explore a specific entity and its connections"""
        if not self.entities_extracted:
            return {'error': 'Knowledge graph not built yet. Load a paper first.'}
        
        # Find related papers using the entity
        related_papers = self.kg.find_related_papers(
            f"paper_{hash(self.rag.current_pdf_path) % 10000}" if hasattr(self.rag, 'current_pdf_path') else "paper_1",
            "concepts"  # Default to concepts, could be made dynamic
        )
        
        if 'error' not in related_papers:
            # Also get RAG context about this entity
            try:
                rag_context = self.rag.query(f"Tell me about {entity_name}")
                related_papers['rag_context'] = rag_context
            except:
                related_papers['rag_context'] = "No additional context available."
        
        return related_papers
    
    def get_paper_overview(self) -> Dict:
        """Get comprehensive overview of the loaded paper"""
        if not self.paper_loaded:
            return {'error': 'No paper loaded'}
        
        overview = {
            'paper_info': self.rag.get_paper_summary(),
            'knowledge_graph': self.kg.get_graph_summary() if self.entities_extracted else None,
            'chat_history': len(self.rag.chat_history),
            'status': 'ready' if self.paper_loaded and self.entities_extracted else 'partial'
        }
        
        return overview
    
    def suggest_questions(self) -> List[str]:
        """Suggest interesting questions based on the paper content"""
        if not self.entities_extracted:
            return ["Load a paper first to get question suggestions."]
        
        suggestions = [
            "What are the main findings of this paper?",
            "What methods were used in this research?",
            "Who are the authors and what are their contributions?",
            "What concepts are most important in this work?",
            "How do the different methods relate to each other?",
        ]
        
        # Add entity-specific suggestions from RAG system if available
        if hasattr(self.rag, 'paper_data') and self.rag.paper_data:
            entities = self.rag.paper_data.get('entities', {})
            
            if entities.get('methods'):
                method = entities['methods'][0]
                suggestions.append(f"Tell me more about {method}")
            
            if entities.get('concepts'):
                concept = entities['concepts'][0]
                suggestions.append(f"How is {concept} used in this paper?")
        
        return suggestions
    
    def export_for_corpus(self, pdf_path: str) -> Dict:
        """
        Export paper analysis in corpus-ready format for GraphRAG
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            GraphRAG-compatible document format
        """
        logger.info(f"📤 Exporting paper for corpus: {Path(pdf_path).name}")
        
        # Use enhanced analyzer for comprehensive analysis
        corpus_doc = self.enhanced_analyzer.analyze_for_corpus(pdf_path)
        
        # Add citation tracking
        citation_map = self.citation_tracker.build_citation_map(
            corpus_doc['content'], 
            corpus_doc['metadata']
        )
        
        # Enhance with chat system capabilities
        if not self.paper_loaded:
            self.load_paper(pdf_path)
        
        # Add chat-ready features
        corpus_doc.update({
            "chat_capabilities": {
                "entities": self.get_entities(),
                "graph_summary": self.kg.get_graph_summary() if self.entities_extracted else None,
                "suggested_questions": self.suggest_questions()
            },
            "citation_tracking": citation_map,
            "corpus_metadata": {
                "export_date": citation_map["paper_info"]["processed_date"] if "paper_info" in citation_map else None,
                "analysis_version": "enhanced_v1.0",
                "capabilities": [
                    "rag_queries",
                    "entity_exploration", 
                    "relationship_discovery",
                    "precise_citations",
                    "cross_paper_linking"
                ]
            }
        })
        
        logger.info(f"✅ Corpus export complete: {corpus_doc['metadata']['title'][:50]}...")
        return corpus_doc


# Convenience function for quick paper analysis
def analyze_paper_with_chat(pdf_path: str) -> UnifiedPaperChat:
    """
    Quick setup for paper analysis with chat interface
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Ready-to-use UnifiedPaperChat instance
    """
    chat_system = UnifiedPaperChat()
    result = chat_system.load_paper(pdf_path)
    
    if 'error' not in result:
        print("✅ Paper loaded successfully!")
        
        # Show graph stats if available
        kg_result = result.get('knowledge_graph', {})
        if 'graph_stats' in kg_result:
            stats = kg_result['graph_stats']
            print(f"📊 Knowledge Graph: {stats['nodes']} entities, {stats['edges']} relationships")
        else:
            print("📊 Knowledge Graph: Built successfully")
            
        print("💬 Ready for chat! Try asking questions about the paper.")
        
        # Show suggested questions
        suggestions = chat_system.suggest_questions()
        print("\n🤔 Suggested questions:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"  {i}. {suggestion}")
    else:
        print(f"❌ Error loading paper: {result['error']}")
    
    return chat_system


# Convenience function for corpus export
def export_paper_for_corpus(pdf_path: str) -> Dict:
    """
    Quick export of paper for corpus inclusion
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        GraphRAG-compatible document
    """
    chat_system = UnifiedPaperChat()
    return chat_system.export_for_corpus(pdf_path)


if __name__ == "__main__":
    # Test the unified system
    test_pdf = "../examples/d4sc03921a.pdf"
    
    if Path(test_pdf).exists():
        print("🧪 Testing UnifiedPaperChat...")
        chat_system = analyze_paper_with_chat(test_pdf)
        
        # Test some queries
        test_queries = [
            "What are the main findings?",
            "Who are the authors?",
            "What methods were used?"
        ]
        
        for query in test_queries:
            print(f"\n❓ {query}")
            response = chat_system.chat(query)
            print(f"💬 {response.get('answer', response.get('error', 'No response'))}")
        
        print("\n✅ Test completed!")
    else:
        print("❌ Test PDF not found")
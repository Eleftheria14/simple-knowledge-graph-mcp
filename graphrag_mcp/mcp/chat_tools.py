"""
Chat Tools for GraphRAG MCP Toolkit

Conversational tools that enable Claude to naturally explore knowledge graphs
and engage in dynamic Q&A about research content. These tools prioritize
natural interaction and discovery over formal citation requirements.
"""

import asyncio
import logging
from typing import Any

from fastmcp import Context
from pydantic import BaseModel

from ..core.citation_manager import CitationTracker
from ..core.query_engine import EnhancedQueryEngine

logger = logging.getLogger(__name__)


class ChatResponse(BaseModel):
    """Structured response for chat interactions"""
    answer: str
    confidence: float
    sources_count: int
    related_topics: list[str] = []
    follow_up_suggestions: list[str] = []
    entities_mentioned: list[str] = []
    processing_time: float = 0.0


class TopicExploration(BaseModel):
    """Structured response for topic exploration"""
    topic: str
    overview: str
    key_aspects: list[dict[str, str]] = []
    relationships: list[dict[str, str]] = []
    gaps_identified: list[str] = []
    suggested_deep_dives: list[str] = []
    confidence: float = 0.0


class ConnectionAnalysis(BaseModel):
    """Analysis of connections between concepts"""
    concept_a: str
    concept_b: str
    connection_strength: float
    connection_types: list[str] = []
    evidence: list[dict[str, Any]] = []
    explanation: str = ""
    related_connections: list[dict[str, str]] = []


class ChatToolsEngine:
    """
    Engine for conversational research exploration tools.
    
    Provides natural language interfaces for:
    - Asking questions about research content
    - Exploring topics and discovering relationships
    - Finding connections between concepts
    - Getting overviews of research areas
    """

    def __init__(self,
                 query_engine: EnhancedQueryEngine | None = None,
                 citation_manager: CitationTracker | None = None,
                 document_store=None,
                 knowledge_graph=None):
        """Initialize chat tools engine"""
        self.query_engine = query_engine or EnhancedQueryEngine()
        self.citation_manager = citation_manager
        self.document_store = document_store
        self.knowledge_graph = knowledge_graph

    async def ask_knowledge_graph(self,
                                question: str,
                                depth: str = "quick",
                                ctx: Context | None = None) -> dict[str, Any]:
        """
        Ask natural questions about the knowledge graph and get conversational answers.
        
        This is the main conversational interface - designed to feel like chatting
        with an expert who has read all the papers in your collection.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if ctx:
                ctx.info(f"Processing question: {question}")

            # Use enhanced query engine for processing
            result = await self.query_engine.process_query(
                query=question,
                context={"chat_mode": True, "depth": depth},
                response_type="conversational"
            )

            # Format for chat interface
            response = ChatResponse(
                answer=result.conversational_response or "I couldn't find specific information about that question.",
                confidence=result.confidence,
                sources_count=len(result.primary_results),
                related_topics=await self._extract_related_topics(result),
                follow_up_suggestions=result.suggestions,
                entities_mentioned=await self._extract_entities_from_response(result),
                processing_time=asyncio.get_event_loop().time() - start_time
            )

            return {
                "success": True,
                "question": question,
                "response": response.dict(),
                "conversation_context": {
                    "query_type": result.query_type.value,
                    "intent": result.intent.value,
                    "depth": depth
                }
            }

        except Exception as e:
            logger.error(f"Question processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "question": question,
                "response": {
                    "answer": f"I encountered an error while processing your question: {str(e)}",
                    "confidence": 0.0,
                    "sources_count": 0,
                    "processing_time": asyncio.get_event_loop().time() - start_time
                }
            }

    async def explore_topic(self,
                          topic: str,
                          scope: str = "overview",
                          ctx: Context | None = None) -> dict[str, Any]:
        """
        Explore a research topic to understand its key aspects and relationships.
        
        Provides structured exploration of topics with different levels of detail.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if ctx:
                ctx.info(f"Exploring topic: {topic} (scope: {scope})")

            # Generate exploration queries based on scope
            if scope == "overview":
                queries = [
                    f"What is {topic}?",
                    f"What are the main aspects of {topic}?",
                    f"What research exists on {topic}?"
                ]
            elif scope == "detailed":
                queries = [
                    f"What is {topic} and how is it defined?",
                    f"What are the key methodologies used in {topic} research?",
                    f"What are the main findings about {topic}?",
                    f"What challenges exist in {topic} research?"
                ]
            else:  # comprehensive
                queries = [
                    f"Comprehensive overview of {topic}",
                    f"Historical development of {topic}",
                    f"Current state of {topic} research",
                    f"Methodologies and approaches in {topic}",
                    f"Key findings and breakthroughs in {topic}",
                    f"Limitations and challenges in {topic}",
                    f"Future directions for {topic} research"
                ]

            # Execute exploration queries
            exploration_results = []
            for query in queries:
                try:
                    result = await self.query_engine.process_query(
                        query=query,
                        context={"exploration_mode": True, "topic": topic},
                        response_type="conversational"
                    )
                    exploration_results.append(result)
                except Exception as e:
                    logger.warning(f"Exploration query failed: {query} - {e}")

            # Synthesize exploration findings
            exploration = await self._synthesize_exploration(topic, exploration_results, scope)

            return {
                "success": True,
                "topic": topic,
                "scope": scope,
                "exploration": exploration.dict(),
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "metadata": {
                    "queries_executed": len(queries),
                    "successful_queries": len(exploration_results)
                }
            }

        except Exception as e:
            logger.error(f"Topic exploration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "exploration": {
                    "overview": f"Failed to explore topic '{topic}': {str(e)}",
                    "confidence": 0.0
                }
            }

    async def find_connections(self,
                             concept_a: str,
                             concept_b: str,
                             connection_types: list[str] | None = None,
                             ctx: Context | None = None) -> dict[str, Any]:
        """
        Discover how different concepts, methods, or ideas are connected.
        
        Analyzes relationships between concepts using graph traversal and
        semantic analysis.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if ctx:
                ctx.info(f"Finding connections between '{concept_a}' and '{concept_b}'")

            # Use enhanced query engine for connection analysis
            result = await self.query_engine.find_connections(
                concept_a=concept_a,
                concept_b=concept_b,
                connection_types=connection_types
            )

            # Analyze connection strength and types
            connection_analysis = await self._analyze_connections(
                concept_a, concept_b, result, connection_types
            )

            return {
                "success": True,
                "concept_a": concept_a,
                "concept_b": concept_b,
                "connection_analysis": connection_analysis.dict(),
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "metadata": {
                    "search_results": len(result.primary_results),
                    "confidence": result.confidence
                }
            }

        except Exception as e:
            logger.error(f"Connection analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "concept_a": concept_a,
                "concept_b": concept_b,
                "connection_analysis": {
                    "explanation": f"Failed to analyze connections: {str(e)}",
                    "connection_strength": 0.0
                }
            }

    async def what_do_we_know_about(self,
                                  topic: str,
                                  include_gaps: bool = True,
                                  ctx: Context | None = None) -> dict[str, Any]:
        """
        Get a comprehensive overview of what the research says about a specific topic.
        
        Provides a structured summary of current knowledge with optional gap analysis.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if ctx:
                ctx.info(f"Gathering knowledge about: {topic}")

            # Comprehensive knowledge gathering
            knowledge_queries = [
                f"What do we know about {topic}?",
                f"What are the key findings about {topic}?",
                f"What methods are used to study {topic}?",
                f"What are the main theories about {topic}?"
            ]

            if include_gaps:
                knowledge_queries.extend([
                    f"What are the limitations in {topic} research?",
                    f"What gaps exist in our knowledge of {topic}?",
                    f"What future research is needed for {topic}?"
                ])

            # Execute knowledge gathering
            knowledge_results = []
            for query in knowledge_queries:
                try:
                    result = await self.query_engine.process_query(
                        query=query,
                        context={"knowledge_synthesis": True, "topic": topic},
                        response_type="conversational"
                    )
                    knowledge_results.append(result)
                except Exception as e:
                    logger.warning(f"Knowledge query failed: {query} - {e}")

            # Synthesize comprehensive overview
            knowledge_overview = await self._synthesize_knowledge_overview(
                topic, knowledge_results, include_gaps
            )

            return {
                "success": True,
                "topic": topic,
                "knowledge_overview": knowledge_overview,
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "metadata": {
                    "sources_analyzed": sum(len(r.primary_results) for r in knowledge_results),
                    "queries_executed": len(knowledge_queries),
                    "include_gaps": include_gaps
                }
            }

        except Exception as e:
            logger.error(f"Knowledge overview failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "knowledge_overview": {
                    "summary": f"Failed to gather knowledge about '{topic}': {str(e)}",
                    "confidence": 0.0
                }
            }

    # Helper methods for processing and synthesis

    async def _extract_related_topics(self, query_result) -> list[str]:
        """Extract related topics from query results"""
        related_topics = []

        # Extract from entities mentioned in results
        for result in query_result.primary_results:
            entities = result.get("entities", [])
            if isinstance(entities, list):
                related_topics.extend(entities)
            elif isinstance(entities, dict):
                for entity_list in entities.values():
                    if isinstance(entity_list, list):
                        related_topics.extend(entity_list)

        # Remove duplicates and limit
        return list(set(related_topics))[:5]

    async def _extract_entities_from_response(self, query_result) -> list[str]:
        """Extract key entities mentioned in the response"""
        entities = []

        # Simple entity extraction from response text
        response_text = query_result.conversational_response or ""

        # Look for capitalized terms (simplified approach)
        import re
        capitalized_terms = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', response_text)

        # Filter out common words
        common_words = {"The", "This", "That", "These", "Those", "When", "Where", "What", "How", "Why"}
        entities = [term for term in capitalized_terms if term not in common_words]

        return list(set(entities))[:10]  # Limit to 10

    async def _synthesize_exploration(self,
                                    topic: str,
                                    exploration_results: list,
                                    scope: str) -> TopicExploration:
        """Synthesize topic exploration results"""

        if not exploration_results:
            return TopicExploration(
                topic=topic,
                overview=f"No specific information found about '{topic}' in the available research.",
                confidence=0.0
            )

        # Combine responses
        combined_content = []
        all_suggestions = []

        for result in exploration_results:
            if result.conversational_response:
                combined_content.append(result.conversational_response)
            all_suggestions.extend(result.suggestions)

        overview = " ".join(combined_content)

        # Extract key aspects (simplified)
        key_aspects = []
        if "methodology" in overview.lower() or "method" in overview.lower():
            key_aspects.append({"aspect": "Methodology", "description": "Research methods and approaches"})
        if "finding" in overview.lower() or "result" in overview.lower():
            key_aspects.append({"aspect": "Key Findings", "description": "Main research results"})
        if "challenge" in overview.lower() or "limitation" in overview.lower():
            key_aspects.append({"aspect": "Challenges", "description": "Current limitations and obstacles"})

        # Calculate confidence
        avg_confidence = sum(r.confidence for r in exploration_results) / len(exploration_results)

        return TopicExploration(
            topic=topic,
            overview=overview[:1000] + "..." if len(overview) > 1000 else overview,
            key_aspects=key_aspects,
            suggested_deep_dives=list(set(all_suggestions))[:5],
            confidence=avg_confidence
        )

    async def _analyze_connections(self,
                                 concept_a: str,
                                 concept_b: str,
                                 query_result,
                                 connection_types: list[str] | None) -> ConnectionAnalysis:
        """Analyze connections between concepts"""

        # Calculate connection strength based on results
        connection_strength = 0.0
        if query_result.primary_results:
            # Simple strength calculation based on number of results and confidence
            result_count = len(query_result.primary_results)
            connection_strength = min(1.0, (result_count / 10.0) * query_result.confidence)

        # Extract connection types from results
        found_connections = []
        if connection_types:
            found_connections = connection_types[:3]  # Use provided types
        else:
            # Infer connection types from response
            response = query_result.conversational_response or ""
            if "similar" in response.lower() or "alike" in response.lower():
                found_connections.append("similarity")
            if "different" in response.lower() or "contrast" in response.lower():
                found_connections.append("contrast")
            if "uses" in response.lower() or "employs" in response.lower():
                found_connections.append("uses")
            if "builds" in response.lower() or "extends" in response.lower():
                found_connections.append("extends")

        # Evidence from search results
        evidence = []
        for result in query_result.primary_results[:3]:  # Top 3 results
            evidence.append({
                "source": result.get("title", "Unknown Source"),
                "relevance": result.get("relevance_score", 0.0),
                "snippet": result.get("snippet", "")[:200]
            })

        explanation = query_result.conversational_response or f"Analysis of connections between '{concept_a}' and '{concept_b}'"

        return ConnectionAnalysis(
            concept_a=concept_a,
            concept_b=concept_b,
            connection_strength=connection_strength,
            connection_types=found_connections,
            evidence=evidence,
            explanation=explanation
        )

    async def _synthesize_knowledge_overview(self,
                                           topic: str,
                                           knowledge_results: list,
                                           include_gaps: bool) -> dict[str, Any]:
        """Synthesize comprehensive knowledge overview"""

        if not knowledge_results:
            return {
                "summary": f"No research information available about '{topic}'",
                "confidence": 0.0,
                "key_findings": [],
                "knowledge_gaps": [] if include_gaps else None
            }

        # Combine all knowledge
        all_content = []
        key_findings = []
        knowledge_gaps = []

        for result in knowledge_results:
            if result.conversational_response:
                content = result.conversational_response
                all_content.append(content)

                # Extract findings (simplified)
                if "finding" in content.lower():
                    key_findings.append(content[:200] + "...")

                # Extract gaps if requested
                if include_gaps and ("gap" in content.lower() or "limitation" in content.lower()):
                    knowledge_gaps.append(content[:200] + "...")

        summary = " ".join(all_content)
        if len(summary) > 2000:
            summary = summary[:2000] + "..."

        # Calculate overall confidence
        avg_confidence = sum(r.confidence for r in knowledge_results) / len(knowledge_results)

        overview = {
            "summary": summary,
            "confidence": avg_confidence,
            "key_findings": key_findings[:5],  # Top 5 findings
            "total_sources": sum(len(r.primary_results) for r in knowledge_results),
            "research_breadth": len(knowledge_results)
        }

        if include_gaps:
            overview["knowledge_gaps"] = knowledge_gaps[:3]  # Top 3 gaps

        return overview


# Factory function for easy integration
def create_chat_tools_engine(query_engine=None, citation_manager=None) -> ChatToolsEngine:
    """Create a chat tools engine with default components"""
    return ChatToolsEngine(
        query_engine=query_engine,
        citation_manager=citation_manager
    )

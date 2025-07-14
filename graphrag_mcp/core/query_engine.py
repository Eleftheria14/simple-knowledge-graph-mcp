"""
Enhanced Query Engine for GraphRAG MCP Toolkit

Provides intelligent query processing for both conversational chat and formal
literature review workflows. Combines semantic search, graph traversal, and
context-aware response generation.
"""

import re
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Classification of query types"""
    CONVERSATIONAL = "conversational"  # Natural chat queries
    LITERATURE_REVIEW = "literature"   # Formal writing queries
    FACTUAL = "factual"                # Specific fact finding
    EXPLORATORY = "exploratory"        # Open-ended exploration
    COMPARATIVE = "comparative"        # Comparison queries
    TEMPORAL = "temporal"              # Time-based queries


class QueryIntent(Enum):
    """Intent classification for queries"""
    FIND_PAPERS = "find_papers"
    GET_DEFINITION = "get_definition"
    COMPARE_APPROACHES = "compare_approaches"
    FIND_GAPS = "find_gaps"
    GET_METHODS = "get_methods"
    TRACE_EVOLUTION = "trace_evolution"
    GET_CITATIONS = "get_citations"
    VERIFY_CLAIM = "verify_claim"
    EXPLORE_TOPIC = "explore_topic"
    SUMMARIZE = "summarize"


@dataclass
class QueryContext:
    """Context information for query processing"""
    query_type: QueryType
    intent: QueryIntent
    entities: List[str]
    keywords: List[str]
    temporal_scope: Optional[str] = None
    domain_filter: Optional[str] = None
    confidence: float = 1.0


class QueryResult(BaseModel):
    """Structured query result"""
    query: str
    query_type: QueryType
    intent: QueryIntent
    
    # Core results
    primary_results: List[Dict[str, Any]] = Field(default_factory=list)
    related_results: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Response formatting
    conversational_response: Optional[str] = None
    formal_response: Optional[str] = None
    
    # Citation support
    citations_used: List[str] = Field(default_factory=list)
    citation_contexts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    total_documents_searched: int = 0
    processing_time: float = 0.0
    confidence: float = 0.0
    suggestions: List[str] = Field(default_factory=list)


class EnhancedQueryEngine:
    """
    Advanced query processing engine for GraphRAG MCP toolkit.
    
    Provides:
    - Natural language query understanding
    - Intent classification and entity extraction
    - Multi-modal search (semantic + graph traversal)
    - Context-aware response generation
    - Citation-aware content generation
    """
    
    def __init__(self, 
                 knowledge_interface=None,
                 citation_manager=None,
                 ollama_engine=None):
        """Initialize query engine with core components"""
        self.knowledge_interface = knowledge_interface
        self.citation_manager = citation_manager
        self.ollama_engine = ollama_engine
        
        # Query patterns for intent classification
        self.intent_patterns = self._initialize_intent_patterns()
        
    async def process_query(self, 
                          query: str,
                          context: Optional[Dict[str, Any]] = None,
                          response_type: str = "conversational") -> QueryResult:
        """
        Process a natural language query and return structured results.
        
        Args:
            query: Natural language query
            context: Optional context information
            response_type: "conversational" or "literature" or "both"
            
        Returns:
            Structured query result with formatted responses
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Analyze query
            query_context = await self._analyze_query(query, context)
            
            # Step 2: Execute search based on intent
            search_results = await self._execute_search(query, query_context)
            
            # Step 3: Generate responses
            result = QueryResult(
                query=query,
                query_type=query_context.query_type,
                intent=query_context.intent,
                primary_results=search_results.get("primary", []),
                related_results=search_results.get("related", []),
                total_documents_searched=search_results.get("total_searched", 0)
            )
            
            # Generate appropriate response format(s)
            if response_type in ["conversational", "both"]:
                result.conversational_response = await self._generate_conversational_response(
                    query, query_context, search_results
                )
            
            if response_type in ["literature", "both"]:
                result.formal_response = await self._generate_formal_response(
                    query, query_context, search_results
                )
            
            # Extract citations and track usage
            if self.citation_manager:
                citations = self._extract_citations_from_results(search_results)
                result.citations_used = citations
                
                # Track citation usage
                for citation_key in citations:
                    self.citation_manager.track_citation(
                        citation_key, 
                        context_text=query,
                        section="query_response",
                        confidence=query_context.confidence
                    )
            
            # Calculate processing time and confidence
            result.processing_time = asyncio.get_event_loop().time() - start_time
            result.confidence = self._calculate_result_confidence(search_results, query_context)
            
            # Generate suggestions for follow-up queries
            result.suggestions = await self._generate_suggestions(query, query_context, search_results)
            
            return result
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            # Return error result
            return QueryResult(
                query=query,
                query_type=QueryType.CONVERSATIONAL,
                intent=QueryIntent.EXPLORE_TOPIC,
                conversational_response=f"I encountered an error processing your query: {str(e)}",
                processing_time=asyncio.get_event_loop().time() - start_time,
                confidence=0.0
            )
    
    async def process_literature_query(self, 
                                     topic: str,
                                     section: str = None,
                                     scope: str = "comprehensive") -> QueryResult:
        """
        Process a query specifically for literature review generation.
        
        Args:
            topic: Research topic or question
            section: Specific section (e.g., "background", "methods", "results")
            scope: Scope of review ("narrow", "comprehensive", "survey")
            
        Returns:
            Literature-focused query result with citations
        """
        # Construct literature-specific query
        if section:
            query = f"For a literature review section on '{section}' covering '{topic}', provide comprehensive analysis with citations"
        else:
            query = f"Provide comprehensive literature review content on '{topic}'"
        
        context = {
            "literature_mode": True,
            "section": section,
            "scope": scope,
            "citation_required": True
        }
        
        return await self.process_query(query, context, response_type="literature")
    
    async def find_connections(self, 
                             concept_a: str, 
                             concept_b: str,
                             connection_types: List[str] = None) -> QueryResult:
        """
        Find and analyze connections between concepts.
        
        Args:
            concept_a: First concept
            concept_b: Second concept
            connection_types: Specific relationship types to look for
            
        Returns:
            Connection analysis results
        """
        query = f"How are '{concept_a}' and '{concept_b}' related or connected?"
        
        context = {
            "connection_analysis": True,
            "concepts": [concept_a, concept_b],
            "connection_types": connection_types or ["related_to", "uses", "extends", "compares"]
        }
        
        return await self.process_query(query, context, response_type="both")
    
    async def verify_claim(self, 
                          claim: str,
                          evidence_threshold: float = 0.7) -> QueryResult:
        """
        Verify a claim against available evidence.
        
        Args:
            claim: Claim to verify
            evidence_threshold: Minimum confidence for evidence
            
        Returns:
            Verification results with supporting/opposing evidence
        """
        query = f"Find evidence to support or refute the claim: '{claim}'"
        
        context = {
            "verification_mode": True,
            "claim": claim,
            "evidence_threshold": evidence_threshold,
            "require_citations": True
        }
        
        return await self.process_query(query, context, response_type="both")
    
    # Private methods for query processing
    
    async def _analyze_query(self, query: str, context: Optional[Dict[str, Any]]) -> QueryContext:
        """Analyze query to determine type, intent, and extract entities"""
        
        # Classify query type
        query_type = self._classify_query_type(query, context)
        
        # Determine intent
        intent = self._classify_intent(query)
        
        # Extract entities and keywords
        entities = await self._extract_entities(query)
        keywords = self._extract_keywords(query)
        
        # Determine temporal scope
        temporal_scope = self._extract_temporal_scope(query)
        
        # Calculate confidence
        confidence = self._calculate_analysis_confidence(query, intent, entities)
        
        return QueryContext(
            query_type=query_type,
            intent=intent,
            entities=entities,
            keywords=keywords,
            temporal_scope=temporal_scope,
            confidence=confidence
        )
    
    def _classify_query_type(self, query: str, context: Optional[Dict[str, Any]]) -> QueryType:
        """Classify the type of query"""
        if context and context.get("literature_mode"):
            return QueryType.LITERATURE_REVIEW
        
        query_lower = query.lower()
        
        # Check for specific patterns
        if any(word in query_lower for word in ["compare", "versus", "vs", "difference"]):
            return QueryType.COMPARATIVE
        
        if any(word in query_lower for word in ["when", "timeline", "evolution", "history", "over time"]):
            return QueryType.TEMPORAL
        
        if any(word in query_lower for word in ["what is", "define", "definition", "meaning"]):
            return QueryType.FACTUAL
        
        if any(word in query_lower for word in ["explore", "overview", "survey", "landscape"]):
            return QueryType.EXPLORATORY
        
        return QueryType.CONVERSATIONAL
    
    def _classify_intent(self, query: str) -> QueryIntent:
        """Classify query intent using pattern matching"""
        query_lower = query.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        return QueryIntent.EXPLORE_TOPIC  # Default intent
    
    async def _extract_entities(self, query: str) -> List[str]:
        """Extract entities from query using NLP"""
        # Simplified entity extraction - in production, use proper NLP
        entities = []
        
        # Look for quoted terms
        quoted_terms = re.findall(r'"([^"]*)"', query)
        entities.extend(quoted_terms)
        
        # Look for capitalized terms (potential proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-zA-Z]+\b', query)
        entities.extend(capitalized)
        
        # Remove duplicates and common words
        common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        entities = list(set([e for e in entities if e.lower() not in common_words]))
        
        return entities
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        # Remove stop words and extract meaningful terms
        stop_words = {
            "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "what", "how", "when", "where", "why", "who", "which", "is", "are", "was", "were",
            "a", "an", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"
        }
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return list(set(keywords))
    
    def _extract_temporal_scope(self, query: str) -> Optional[str]:
        """Extract temporal scope from query"""
        query_lower = query.lower()
        
        # Look for temporal indicators
        if any(word in query_lower for word in ["recent", "latest", "current", "new"]):
            return "recent"
        
        if any(word in query_lower for word in ["historical", "past", "previous", "old", "earlier"]):
            return "historical"
        
        if any(word in query_lower for word in ["future", "upcoming", "next", "planned"]):
            return "future"
        
        # Look for specific time periods
        time_patterns = [
            r"(\d{4})",  # Years
            r"(19\d{2}|20\d{2})",  # Specific year ranges
            r"(last \d+ years?)",  # Last N years
            r"(past decade)",  # Past decade
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_analysis_confidence(self, query: str, intent: QueryIntent, entities: List[str]) -> float:
        """Calculate confidence in query analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on clarity
        if len(query.split()) > 3:  # Reasonable length
            confidence += 0.1
        
        if entities:  # Has identifiable entities
            confidence += 0.2
        
        if intent != QueryIntent.EXPLORE_TOPIC:  # Specific intent identified
            confidence += 0.2
        
        return min(1.0, confidence)
    
    async def _execute_search(self, query: str, query_context: QueryContext) -> Dict[str, Any]:
        """Execute search based on query context"""
        search_results = {
            "primary": [],
            "related": [],
            "total_searched": 0
        }
        
        try:
            # Use knowledge interface if available
            if self.knowledge_interface:
                if query_context.intent == QueryIntent.FIND_PAPERS:
                    results = await self.knowledge_interface.semantic_search(
                        query, 
                        entity_filter=query_context.entities
                    )
                elif query_context.intent == QueryIntent.COMPARE_APPROACHES:
                    results = await self.knowledge_interface.comparative_search(
                        query_context.entities
                    )
                elif query_context.intent == QueryIntent.FIND_GAPS:
                    results = await self.knowledge_interface.gap_analysis(
                        query, 
                        domain=query_context.domain_filter
                    )
                else:
                    results = await self.knowledge_interface.general_search(query)
                
                search_results["primary"] = results.get("documents", [])
                search_results["related"] = results.get("related", [])
                search_results["total_searched"] = results.get("total", 0)
            
            # Fallback to basic search if no interface
            else:
                # Placeholder for basic search implementation
                search_results["primary"] = [
                    {
                        "title": "Sample Document",
                        "relevance": 0.8,
                        "snippet": "Sample content matching query",
                        "citation_key": "sample2024"
                    }
                ]
                search_results["total_searched"] = 1
            
        except Exception as e:
            logger.error(f"Search execution failed: {e}")
        
        return search_results
    
    async def _generate_conversational_response(self, 
                                              query: str,
                                              query_context: QueryContext,
                                              search_results: Dict[str, Any]) -> str:
        """Generate conversational response"""
        
        if not search_results["primary"]:
            return f"I couldn't find specific information about '{query}' in the available documents. Try rephrasing your question or ask about a related topic."
        
        # Build conversational response
        response_parts = []
        
        # Opening based on intent
        if query_context.intent == QueryIntent.GET_DEFINITION:
            response_parts.append("Based on the available literature,")
        elif query_context.intent == QueryIntent.COMPARE_APPROACHES:
            response_parts.append("When comparing these approaches,")
        elif query_context.intent == QueryIntent.FIND_GAPS:
            response_parts.append("Looking at the research landscape,")
        else:
            response_parts.append("From what I can find in the documents,")
        
        # Summarize key findings
        primary_results = search_results["primary"][:3]  # Top 3 results
        for i, result in enumerate(primary_results):
            snippet = result.get("snippet", "")
            if snippet:
                if i == 0:
                    response_parts.append(f" {snippet}")
                else:
                    response_parts.append(f" Additionally, {snippet}")
        
        # Add related information if available
        if search_results["related"]:
            response_parts.append(f" I also found {len(search_results['related'])} related documents that might be helpful.")
        
        # Suggest follow-up
        response_parts.append(" Would you like me to explore any specific aspect in more detail?")
        
        return "".join(response_parts)
    
    async def _generate_formal_response(self, 
                                      query: str,
                                      query_context: QueryContext,
                                      search_results: Dict[str, Any]) -> str:
        """Generate formal literature review response with citations"""
        
        if not search_results["primary"]:
            return "Insufficient literature available for comprehensive analysis of this topic."
        
        # Build formal response with proper citation integration
        response_parts = []
        
        # Introduction
        if query_context.intent == QueryIntent.COMPARE_APPROACHES:
            response_parts.append("A comparative analysis of the literature reveals several distinct approaches.")
        elif query_context.intent == QueryIntent.FIND_GAPS:
            response_parts.append("Analysis of the current literature identifies several research gaps and opportunities.")
        else:
            response_parts.append("The existing literature provides substantial evidence regarding this topic.")
        
        # Main content with citations
        primary_results = search_results["primary"]
        for result in primary_results:
            snippet = result.get("snippet", "")
            citation_key = result.get("citation_key", "unknown")
            
            if snippet:
                # Format with in-text citation
                if self.citation_manager:
                    citation = self.citation_manager.generate_in_text_citation(citation_key)
                    response_parts.append(f" {snippet} {citation}.")
                else:
                    response_parts.append(f" {snippet} [{citation_key}].")
        
        # Synthesis and conclusion
        if len(primary_results) > 1:
            response_parts.append(" Collectively, these studies demonstrate the complexity and multifaceted nature of this research area.")
        
        return "".join(response_parts)
    
    def _extract_citations_from_results(self, search_results: Dict[str, Any]) -> List[str]:
        """Extract citation keys from search results"""
        citations = []
        
        for result in search_results.get("primary", []):
            citation_key = result.get("citation_key")
            if citation_key:
                citations.append(citation_key)
        
        for result in search_results.get("related", []):
            citation_key = result.get("citation_key")
            if citation_key:
                citations.append(citation_key)
        
        return list(set(citations))  # Remove duplicates
    
    def _calculate_result_confidence(self, 
                                   search_results: Dict[str, Any], 
                                   query_context: QueryContext) -> float:
        """Calculate confidence in query results"""
        if not search_results["primary"]:
            return 0.0
        
        # Base confidence from query analysis
        confidence = query_context.confidence
        
        # Adjust based on result quality
        primary_count = len(search_results["primary"])
        if primary_count >= 3:
            confidence += 0.2
        elif primary_count >= 1:
            confidence += 0.1
        
        # Check relevance scores if available
        relevance_scores = [
            result.get("relevance", 0.5) 
            for result in search_results["primary"]
        ]
        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            confidence = (confidence + avg_relevance) / 2
        
        return min(1.0, confidence)
    
    async def _generate_suggestions(self, 
                                  query: str,
                                  query_context: QueryContext,
                                  search_results: Dict[str, Any]) -> List[str]:
        """Generate follow-up query suggestions"""
        suggestions = []
        
        # Suggestions based on intent
        if query_context.intent == QueryIntent.EXPLORE_TOPIC:
            suggestions.extend([
                "What are the main methodologies used in this area?",
                "How has this field evolved over time?",
                "What are the current limitations and challenges?"
            ])
        
        elif query_context.intent == QueryIntent.FIND_PAPERS:
            suggestions.extend([
                "What methodologies do these papers use?",
                "How do these approaches compare?",
                "What gaps exist in this research area?"
            ])
        
        elif query_context.intent == QueryIntent.COMPARE_APPROACHES:
            suggestions.extend([
                "Which approach shows the best results?",
                "What are the trade-offs between these methods?",
                "Are there hybrid approaches that combine these methods?"
            ])
        
        # Entity-based suggestions
        for entity in query_context.entities[:2]:  # Max 2 entity suggestions
            suggestions.append(f"Tell me more about {entity}")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _initialize_intent_patterns(self) -> Dict[QueryIntent, List[str]]:
        """Initialize patterns for intent classification"""
        return {
            QueryIntent.FIND_PAPERS: [
                "find papers", "search papers", "papers about", "literature on",
                "studies on", "research on", "articles about"
            ],
            QueryIntent.GET_DEFINITION: [
                "what is", "define", "definition", "meaning of", "explain",
                "what does", "how would you define"
            ],
            QueryIntent.COMPARE_APPROACHES: [
                "compare", "comparison", "versus", "vs", "difference between",
                "similarities", "contrast", "which is better"
            ],
            QueryIntent.FIND_GAPS: [
                "gaps", "missing", "limitations", "challenges", "problems",
                "unsolved", "future work", "research opportunities"
            ],
            QueryIntent.GET_METHODS: [
                "methodology", "methods", "approach", "technique", "procedure",
                "how to", "implementation", "algorithm"
            ],
            QueryIntent.TRACE_EVOLUTION: [
                "evolution", "history", "timeline", "development", "progress",
                "over time", "changes", "trends"
            ],
            QueryIntent.GET_CITATIONS: [
                "citations", "references", "sources", "evidence", "support",
                "bibliography", "cite", "reference"
            ],
            QueryIntent.VERIFY_CLAIM: [
                "verify", "confirm", "validate", "evidence for", "support for",
                "true that", "fact check", "prove"
            ],
            QueryIntent.SUMMARIZE: [
                "summary", "summarize", "overview", "key points", "main findings",
                "in summary", "briefly", "outline"
            ]
        }
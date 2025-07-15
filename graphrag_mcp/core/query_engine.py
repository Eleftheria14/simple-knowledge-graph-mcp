"""
Enhanced Query Engine for GraphRAG MCP Toolkit

Provides intelligent query processing for both conversational chat and formal
literature review workflows. Combines semantic search, graph traversal, and
context-aware response generation.
"""

import asyncio
import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field
from ..utils.error_handling import ProcessingError, ValidationError

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
    entities: list[str]
    keywords: list[str]
    temporal_scope: str | None = None
    domain_filter: str | None = None
    confidence: float = 1.0


class QueryResult(BaseModel):
    """Structured query result with comprehensive error handling"""
    query: str
    query_type: QueryType
    intent: QueryIntent

    # Core results
    primary_results: list[dict[str, Any]] = Field(default_factory=list)
    related_results: list[dict[str, Any]] = Field(default_factory=list)

    # Response formatting
    conversational_response: str | None = None
    formal_response: str | None = None

    # Citation support
    citations_used: list[str] = Field(default_factory=list)
    citation_contexts: list[dict[str, Any]] = Field(default_factory=list)

    # Metadata
    total_documents_searched: int = 0
    processing_time: float = 0.0
    confidence: float = 0.0
    suggestions: list[str] = Field(default_factory=list)
    
    # Error handling and recovery
    success: bool = True
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    recovery_attempted: bool = False
    recovery_strategies: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    
    # Performance metrics
    search_time: float = 0.0
    analysis_time: float = 0.0
    response_generation_time: float = 0.0
    retry_count: int = 0


class EnhancedQueryEngine:
    """
    Advanced query processing engine for GraphRAG MCP toolkit with comprehensive error handling.
    
    Provides:
    - Natural language query understanding
    - Intent classification and entity extraction
    - Multi-modal search (semantic + graph traversal)
    - Context-aware response generation
    - Citation-aware content generation
    - Robust error handling and recovery
    """

    def __init__(self,
                 knowledge_interface=None,
                 citation_manager=None,
                 ollama_engine=None,
                 max_retries: int = 3,
                 timeout_seconds: int = 30):
        """Initialize query engine with core components and error handling"""
        self.knowledge_interface = knowledge_interface
        self.citation_manager = citation_manager
        self.ollama_engine = ollama_engine
        
        # Configuration
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        
        # Error tracking
        self.error_history: list[dict] = []
        self.recovery_strategies = [
            "fallback_search",
            "simplified_analysis",
            "cached_response",
            "minimal_response"
        ]
        
        # Performance monitoring
        self.query_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "recovery_attempts": 0,
            "average_response_time": 0.0
        }

        # Query patterns for intent classification
        self.intent_patterns = self._initialize_intent_patterns()

    async def process_query(self,
                          query: str,
                          context: dict[str, Any] | None = None,
                          response_type: str = "conversational") -> QueryResult:
        """
        Process a natural language query with comprehensive error handling and recovery.
        
        Args:
            query: Natural language query
            context: Optional context information
            response_type: "conversational" or "literature" or "both"
            
        Returns:
            Structured query result with formatted responses
        """
        start_time = time.time()
        self.query_stats["total_queries"] += 1
        
        # Input validation
        if not query or not isinstance(query, str):
            return self._create_error_result(
                query or "<empty>",
                "Invalid query: must be a non-empty string",
                "ValidationError",
                start_time
            )
        
        query = query.strip()
        if len(query) > 10000:  # Reasonable limit
            return self._create_error_result(
                query[:50] + "...",
                "Query too long: maximum 10,000 characters",
                "ValidationError",
                start_time
            )
        
        # Validate response type
        valid_response_types = ["conversational", "literature", "both"]
        if response_type not in valid_response_types:
            return self._create_error_result(
                query,
                f"Invalid response_type: {response_type}. Must be one of {valid_response_types}",
                "ValidationError",
                start_time
            )
        
        # Attempt processing with retry logic
        for attempt in range(self.max_retries + 1):
            try:
                result = await self._process_query_with_timeout(
                    query, context, response_type, start_time, attempt
                )
                
                if result.success:
                    self.query_stats["successful_queries"] += 1
                    self._update_performance_stats(result.processing_time)
                    return result
                else:
                    # Try recovery strategies
                    if attempt < self.max_retries:
                        logger.warning(f"Query attempt {attempt + 1} failed, trying recovery...")
                        recovery_result = await self._attempt_recovery(
                            query, context, response_type, result.error_message, attempt
                        )
                        if recovery_result.success:
                            self.query_stats["successful_queries"] += 1
                            self.query_stats["recovery_attempts"] += 1
                            self._update_performance_stats(recovery_result.processing_time)
                            return recovery_result
                    else:
                        # Final failure
                        self.query_stats["failed_queries"] += 1
                        self._log_error(query, result.error_message, result.error_type)
                        return result
                        
            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    logger.warning(f"Query timeout on attempt {attempt + 1}, retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.query_stats["failed_queries"] += 1
                    return self._create_error_result(
                        query,
                        f"Query processing timed out after {self.timeout_seconds} seconds",
                        "TimeoutError",
                        start_time,
                        retry_count=attempt + 1
                    )
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")
                    await asyncio.sleep(2 ** attempt)
                else:
                    self.query_stats["failed_queries"] += 1
                    return self._create_error_result(
                        query,
                        f"Unexpected error: {str(e)}",
                        type(e).__name__,
                        start_time,
                        retry_count=attempt + 1
                    )
        
        # Should not reach here, but just in case
        self.query_stats["failed_queries"] += 1
        return self._create_error_result(
            query,
            "Maximum retry attempts exceeded",
            "RetryError",
            start_time
        )
    
    async def _process_query_with_timeout(self,
                                        query: str,
                                        context: dict[str, Any] | None,
                                        response_type: str,
                                        start_time: float,
                                        attempt: int) -> QueryResult:
        """Process query with timeout protection"""
        try:
            # Wrap the actual processing in a timeout
            return await asyncio.wait_for(
                self._process_query_internal(query, context, response_type, start_time, attempt),
                timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            # Convert to structured error result
            return self._create_error_result(
                query,
                str(e),
                type(e).__name__,
                start_time,
                retry_count=attempt + 1
            )
    
    async def _process_query_internal(self,
                                    query: str,
                                    context: dict[str, Any] | None,
                                    response_type: str,
                                    start_time: float,
                                    attempt: int) -> QueryResult:
        """Internal query processing with detailed timing"""
        # Step 1: Analyze query
        analysis_start = time.time()
        try:
            query_context = await self._analyze_query(query, context)
        except Exception as e:
            return self._create_error_result(
                query,
                f"Query analysis failed: {str(e)}",
                "AnalysisError",
                start_time,
                retry_count=attempt + 1
            )
        analysis_time = time.time() - analysis_start

        # Step 2: Execute search based on intent
        search_start = time.time()
        try:
            search_results = await self._execute_search(query, query_context)
        except Exception as e:
            return self._create_error_result(
                query,
                f"Search execution failed: {str(e)}",
                "SearchError",
                start_time,
                retry_count=attempt + 1
            )
        search_time = time.time() - search_start

        # Step 3: Generate responses
        response_start = time.time()
        try:
            result = QueryResult(
                query=query,
                query_type=query_context.query_type,
                intent=query_context.intent,
                primary_results=search_results.get("primary", []),
                related_results=search_results.get("related", []),
                total_documents_searched=search_results.get("total_searched", 0),
                analysis_time=analysis_time,
                search_time=search_time,
                retry_count=attempt
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
                try:
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
                except Exception as e:
                    result.warnings.append(f"Citation tracking failed: {str(e)}")

            # Calculate processing time and confidence
            result.response_generation_time = time.time() - response_start
            result.processing_time = time.time() - start_time
            result.confidence = self._calculate_result_confidence(search_results, query_context)

            # Generate suggestions for follow-up queries
            try:
                result.suggestions = await self._generate_suggestions(query, query_context, search_results)
            except Exception as e:
                result.warnings.append(f"Suggestion generation failed: {str(e)}")
                result.suggestions = []

            return result
            
        except Exception as e:
            return self._create_error_result(
                query,
                f"Response generation failed: {str(e)}",
                "ResponseError",
                start_time,
                retry_count=attempt + 1
            )
    
    async def _attempt_recovery(self,
                              query: str,
                              context: dict[str, Any] | None,
                              response_type: str,
                              error_message: str,
                              attempt: int) -> QueryResult:
        """Attempt recovery using various strategies"""
        start_time = time.time()
        
        # Try different recovery strategies in order
        for strategy in self.recovery_strategies:
            try:
                if strategy == "fallback_search":
                    result = await self._fallback_search_recovery(query, context, response_type)
                elif strategy == "simplified_analysis":
                    result = await self._simplified_analysis_recovery(query, context, response_type)
                elif strategy == "cached_response":
                    result = await self._cached_response_recovery(query, context, response_type)
                elif strategy == "minimal_response":
                    result = await self._minimal_response_recovery(query, context, response_type)
                else:
                    continue
                
                if result.success:
                    result.recovery_attempted = True
                    result.recovery_strategies = [strategy]
                    result.processing_time = time.time() - start_time
                    return result
                    
            except Exception as e:
                logger.warning(f"Recovery strategy {strategy} failed: {e}")
                continue
        
        # All recovery strategies failed
        return self._create_error_result(
            query,
            f"All recovery strategies failed. Original error: {error_message}",
            "RecoveryError",
            start_time,
            retry_count=attempt + 1
        )
    
    def _create_error_result(self,
                           query: str,
                           error_message: str,
                           error_type: str,
                           start_time: float,
                           retry_count: int = 0) -> QueryResult:
        """Create standardized error result"""
        return QueryResult(
            query=query,
            query_type=QueryType.CONVERSATIONAL,
            intent=QueryIntent.EXPLORE_TOPIC,
            success=False,
            error_message=error_message,
            error_type=error_type,
            conversational_response=f"I'm sorry, I encountered an error processing your query: {error_message}",
            processing_time=time.time() - start_time,
            confidence=0.0,
            retry_count=retry_count,
            suggestions=[
                "Try rephrasing your question",
                "Ask about a more specific topic",
                "Check if the system is working properly"
            ]
        )
    
    def _log_error(self, query: str, error_message: str, error_type: str):
        """Log error to history for analysis"""
        error_entry = {
            "timestamp": time.time(),
            "query": query[:200],  # Truncate for storage
            "error_message": error_message,
            "error_type": error_type
        }
        
        self.error_history.append(error_entry)
        
        # Keep only last 100 errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
    
    def _update_performance_stats(self, processing_time: float):
        """Update performance statistics"""
        if self.query_stats["successful_queries"] > 0:
            current_avg = self.query_stats["average_response_time"]
            n = self.query_stats["successful_queries"]
            self.query_stats["average_response_time"] = (
                (current_avg * (n - 1) + processing_time) / n
            )
        else:
            self.query_stats["average_response_time"] = processing_time

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
                             connection_types: list[str] = None) -> QueryResult:
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

    async def _analyze_query(self, query: str, context: dict[str, Any] | None) -> QueryContext:
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

    def _classify_query_type(self, query: str, context: dict[str, Any] | None) -> QueryType:
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

    async def _extract_entities(self, query: str) -> list[str]:
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

    def _extract_keywords(self, query: str) -> list[str]:
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

    def _extract_temporal_scope(self, query: str) -> str | None:
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

    def _calculate_analysis_confidence(self, query: str, intent: QueryIntent, entities: list[str]) -> float:
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

    async def _execute_search(self, query: str, query_context: QueryContext) -> dict[str, Any]:
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
                                              search_results: dict[str, Any]) -> str:
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
                                      search_results: dict[str, Any]) -> str:
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

    def _extract_citations_from_results(self, search_results: dict[str, Any]) -> list[str]:
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
                                   search_results: dict[str, Any],
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
                                  search_results: dict[str, Any]) -> list[str]:
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

    def _initialize_intent_patterns(self) -> dict[QueryIntent, list[str]]:
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

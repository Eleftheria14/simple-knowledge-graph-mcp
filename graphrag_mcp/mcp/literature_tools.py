"""
Literature Review Tools for GraphRAG MCP Toolkit

Formal writing tools that enable Claude to generate literature reviews with
proper citations, evidence-based claims, and structured academic content.
These tools prioritize accuracy, citation management, and formal writing standards.
"""

import asyncio
import logging
from typing import Any

from fastmcp import Context
from pydantic import BaseModel, Field

from ..core.citation_manager import CitationTracker
from ..core.query_engine import EnhancedQueryEngine

logger = logging.getLogger(__name__)


class SourceGathering(BaseModel):
    """Result of source gathering for literature review"""
    topic: str
    scope: str
    total_sources: int
    relevant_sources: list[dict[str, Any]] = Field(default_factory=list)
    source_categories: dict[str, int] = Field(default_factory=dict)
    coverage_assessment: str = ""
    recommended_sections: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class CitedFacts(BaseModel):
    """Facts with proper citation support"""
    topic: str
    section: str | None
    facts: list[dict[str, Any]] = Field(default_factory=list)
    citation_style: str = "APA"
    evidence_strength: str = "strong"
    total_citations: int = 0
    confidence: float = 0.0


class ClaimVerification(BaseModel):
    """Result of claim verification with evidence"""
    claim: str
    verification_status: str  # "supported", "contradicted", "insufficient", "mixed"
    evidence_strength: str
    supporting_evidence: list[dict[str, Any]] = Field(default_factory=list)
    contradicting_evidence: list[dict[str, Any]] = Field(default_factory=list)
    neutral_evidence: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    recommendation: str = ""


class LiteratureOutline(BaseModel):
    """Structured outline for literature review"""
    topic: str
    section_type: str
    outline_structure: list[dict[str, Any]] = Field(default_factory=list)
    key_themes: list[str] = Field(default_factory=list)
    source_distribution: dict[str, int] = Field(default_factory=dict)
    estimated_length: str = ""
    writing_guidance: list[str] = Field(default_factory=list)


class LiteratureToolsEngine:
    """
    Engine for formal literature review writing tools.
    
    Provides structured, citation-aware tools for:
    - Gathering and organizing sources
    - Generating fact statements with citations
    - Verifying claims with evidence
    - Creating literature review outlines
    - Managing citation tracking
    """

    def __init__(self,
                 query_engine: EnhancedQueryEngine | None = None,
                 citation_manager: CitationTracker | None = None,
                 document_store=None,
                 knowledge_graph=None):
        """Initialize literature review tools engine"""
        self.query_engine = query_engine or EnhancedQueryEngine()
        self.citation_manager = citation_manager or CitationTracker()
        self.document_store = document_store
        self.knowledge_graph = knowledge_graph

    async def gather_sources_for_topic(self,
                                     topic: str,
                                     scope: str = "comprehensive",
                                     sections: list[str] | None = None,
                                     ctx: Context | None = None) -> dict[str, Any]:
        """
        Gather and organize sources for a specific literature review topic.
        
        Systematically identifies relevant sources and organizes them by
        relevance, methodology, and potential contribution to different sections.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if ctx:
                ctx.info(f"Gathering sources for literature review on: {topic}")

            # Define search strategies based on scope
            if scope == "focused":
                search_queries = [
                    f"{topic} research findings",
                    f"{topic} methodology",
                    f"recent {topic} studies"
                ]
            elif scope == "survey":
                search_queries = [
                    f"{topic} survey",
                    f"{topic} systematic review",
                    f"{topic} meta-analysis",
                    f"comprehensive {topic} analysis"
                ]
            else:  # comprehensive
                search_queries = [
                    f"{topic} research",
                    f"{topic} methodology",
                    f"{topic} findings",
                    f"{topic} applications",
                    f"{topic} limitations",
                    f"{topic} future research",
                    f"recent advances in {topic}",
                    f"theoretical foundations of {topic}"
                ]

            # Execute comprehensive source gathering
            all_sources = []
            source_categories = {"methodology": 0, "findings": 0, "reviews": 0, "applications": 0}

            for query in search_queries:
                try:
                    result = await self.query_engine.process_query(
                        query=query,
                        context={"literature_mode": True, "topic": topic},
                        response_type="literature"
                    )

                    # Process and categorize sources
                    for source in result.primary_results:
                        categorized_source = await self._categorize_source(source, topic, sections)
                        all_sources.append(categorized_source)

                        # Update category counts
                        category = categorized_source.get("category", "other")
                        if category in source_categories:
                            source_categories[category] += 1

                except Exception as e:
                    logger.warning(f"Source gathering query failed: {query} - {e}")

            # Remove duplicates and rank by relevance
            unique_sources = await self._deduplicate_and_rank_sources(all_sources, topic)

            # Assess coverage and make recommendations
            coverage_assessment = await self._assess_source_coverage(unique_sources, topic, scope)
            recommended_sections = await self._recommend_sections(unique_sources, topic, sections)

            # Build source gathering result
            source_gathering = SourceGathering(
                topic=topic,
                scope=scope,
                total_sources=len(unique_sources),
                relevant_sources=unique_sources[:20],  # Top 20 sources
                source_categories=source_categories,
                coverage_assessment=coverage_assessment,
                recommended_sections=recommended_sections,
                confidence=min(1.0, len(unique_sources) / 10.0)  # Confidence based on source count
            )

            return {
                "success": True,
                "topic": topic,
                "source_gathering": source_gathering.dict(),
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "metadata": {
                    "queries_executed": len(search_queries),
                    "total_sources_found": len(all_sources),
                    "unique_sources": len(unique_sources)
                }
            }

        except Exception as e:
            logger.error(f"Source gathering failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "source_gathering": {
                    "coverage_assessment": f"Failed to gather sources: {str(e)}",
                    "total_sources": 0,
                    "confidence": 0.0
                }
            }

    async def get_facts_with_citations(self,
                                     topic: str,
                                     section: str | None = None,
                                     citation_style: str = "APA",
                                     ctx: Context | None = None) -> dict[str, Any]:
        """
        Get factual statements about a topic with proper citations for literature review writing.
        
        Generates evidence-based statements suitable for formal academic writing,
        each backed by appropriate citations and formatted for immediate use.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if ctx:
                ctx.info(f"Generating cited facts for: {topic} (section: {section})")

            # Customize fact-finding based on section type
            if section:
                query_contexts = await self._get_section_specific_queries(topic, section)
            else:
                query_contexts = [
                    f"key findings about {topic}",
                    f"main research results on {topic}",
                    f"established facts about {topic}",
                    f"evidence regarding {topic}"
                ]

            # Generate cited facts
            cited_facts = []
            used_citations = set()

            for query_context in query_contexts:
                try:
                    result = await self.query_engine.process_literature_query(
                        topic=query_context,
                        section=section,
                        scope="comprehensive"
                    )

                    # Extract facts with citations
                    facts = await self._extract_cited_facts(result, citation_style)

                    for fact in facts:
                        if fact["citation_key"] not in used_citations:
                            cited_facts.append(fact)
                            used_citations.add(fact["citation_key"])

                            # Track citation usage
                            self.citation_manager.track_citation(
                                fact["citation_key"],
                                context_text=fact["statement"],
                                section=section or "literature_review",
                                confidence=fact.get("confidence", 0.8)
                            )

                except Exception as e:
                    logger.warning(f"Fact extraction failed for: {query_context} - {e}")

            # Organize facts by strength and relevance
            organized_facts = await self._organize_facts_by_strength(cited_facts, topic)

            facts_result = CitedFacts(
                topic=topic,
                section=section,
                facts=organized_facts,
                citation_style=citation_style,
                total_citations=len(used_citations),
                confidence=min(1.0, len(organized_facts) / 5.0)
            )

            return {
                "success": True,
                "topic": topic,
                "section": section,
                "cited_facts": facts_result.dict(),
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "metadata": {
                    "facts_generated": len(organized_facts),
                    "unique_citations": len(used_citations),
                    "citation_style": citation_style
                }
            }

        except Exception as e:
            logger.error(f"Cited facts generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "cited_facts": {
                    "facts": [],
                    "total_citations": 0,
                    "confidence": 0.0
                }
            }

    async def verify_claim_with_sources(self,
                                      claim: str,
                                      evidence_strength: str = "strong",
                                      ctx: Context | None = None) -> dict[str, Any]:
        """
        Verify a claim and provide supporting evidence with citations.
        
        Systematically evaluates claims against available evidence and provides
        balanced assessment with supporting and contradicting evidence.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if ctx:
                ctx.info(f"Verifying claim: {claim}")

            # Use enhanced query engine for claim verification
            result = await self.query_engine.verify_claim(
                claim=claim,
                evidence_threshold=0.7 if evidence_strength == "strong" else 0.5
            )

            # Analyze evidence for and against claim
            verification = await self._analyze_claim_evidence(claim, result, evidence_strength)

            # Track citations used in verification
            all_citations = set()
            for evidence in verification.supporting_evidence + verification.contradicting_evidence:
                citation_key = evidence.get("citation_key")
                if citation_key:
                    all_citations.add(citation_key)
                    self.citation_manager.track_citation(
                        citation_key,
                        context_text=claim,
                        section="claim_verification",
                        confidence=evidence.get("confidence", 0.7)
                    )

            return {
                "success": True,
                "claim": claim,
                "verification": verification.dict(),
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "metadata": {
                    "evidence_strength": evidence_strength,
                    "supporting_sources": len(verification.supporting_evidence),
                    "contradicting_sources": len(verification.contradicting_evidence),
                    "total_citations": len(all_citations)
                }
            }

        except Exception as e:
            logger.error(f"Claim verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "claim": claim,
                "verification": {
                    "verification_status": "error",
                    "recommendation": f"Unable to verify claim: {str(e)}",
                    "confidence": 0.0
                }
            }

    async def get_topic_outline(self,
                              topic: str,
                              section_type: str = "full_review",
                              ctx: Context | None = None) -> dict[str, Any]:
        """
        Generate an outline for a literature review section with key points and sources.
        
        Creates structured outlines that organize content logically and ensure
        comprehensive coverage of the topic.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if ctx:
                ctx.info(f"Generating outline for: {topic} ({section_type})")

            # Generate section-specific outline structure
            outline_structure = await self._generate_outline_structure(topic, section_type)

            # Populate outline with sources and key points
            populated_outline = await self._populate_outline_with_sources(outline_structure, topic)

            # Extract key themes and estimate content
            key_themes = await self._extract_key_themes(populated_outline, topic)
            source_distribution = await self._calculate_source_distribution(populated_outline)
            estimated_length = await self._estimate_section_length(populated_outline, section_type)
            writing_guidance = await self._generate_writing_guidance(section_type, topic)

            outline = LiteratureOutline(
                topic=topic,
                section_type=section_type,
                outline_structure=populated_outline,
                key_themes=key_themes,
                source_distribution=source_distribution,
                estimated_length=estimated_length,
                writing_guidance=writing_guidance
            )

            return {
                "success": True,
                "topic": topic,
                "section_type": section_type,
                "outline": outline.dict(),
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "metadata": {
                    "outline_sections": len(populated_outline),
                    "themes_identified": len(key_themes),
                    "sources_referenced": sum(source_distribution.values())
                }
            }

        except Exception as e:
            logger.error(f"Outline generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "outline": {
                    "outline_structure": [],
                    "estimated_length": "Unable to estimate",
                    "writing_guidance": [f"Outline generation failed: {str(e)}"]
                }
            }

    async def track_citations_used(self,
                                 citation_keys: list[str],
                                 context: str | None = None,
                                 ctx: Context | None = None) -> dict[str, Any]:
        """
        Track which citations you've used in your writing to maintain proper attribution.
        
        Maintains comprehensive records of citation usage for bibliography generation
        and ensures no citations are missed or improperly attributed.
        """
        try:
            if ctx:
                ctx.info(f"Tracking {len(citation_keys)} citations")

            tracked_citations = []
            tracking_results = {"successful": 0, "failed": 0, "warnings": []}

            for citation_key in citation_keys:
                try:
                    # Track the citation
                    success = self.citation_manager.track_citation(
                        citation_key=citation_key,
                        context_text=context or "Manual citation tracking",
                        section="user_content",
                        confidence=1.0
                    )

                    if success:
                        # Get citation details
                        if citation_key in self.citation_manager.citations:
                            citation = self.citation_manager.citations[citation_key]
                            tracked_citations.append({
                                "citation_key": citation_key,
                                "title": citation.title,
                                "authors": citation.authors,
                                "usage_count": citation.citation_count,
                                "status": "tracked"
                            })
                        tracking_results["successful"] += 1
                    else:
                        tracking_results["failed"] += 1
                        tracking_results["warnings"].append(f"Citation not found: {citation_key}")

                except Exception as e:
                    tracking_results["failed"] += 1
                    tracking_results["warnings"].append(f"Failed to track {citation_key}: {str(e)}")

            # Get current citation statistics
            stats = self.citation_manager.get_citation_statistics()

            return {
                "success": True,
                "tracking_results": tracking_results,
                "tracked_citations": tracked_citations,
                "citation_statistics": stats,
                "context": context,
                "metadata": {
                    "total_requested": len(citation_keys),
                    "successfully_tracked": tracking_results["successful"],
                    "failed_to_track": tracking_results["failed"]
                }
            }

        except Exception as e:
            logger.error(f"Citation tracking failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tracking_results": {"successful": 0, "failed": len(citation_keys)},
                "tracked_citations": []
            }

    # Helper methods for literature review processing

    async def _categorize_source(self, source: dict[str, Any], topic: str, sections: list[str] | None) -> dict[str, Any]:
        """Categorize a source for literature review purposes"""
        title = source.get("title", "").lower()
        snippet = source.get("snippet", "").lower()

        # Determine category based on content
        if any(word in title + snippet for word in ["method", "approach", "technique", "procedure"]):
            category = "methodology"
        elif any(word in title + snippet for word in ["result", "finding", "outcome", "effect"]):
            category = "findings"
        elif any(word in title + snippet for word in ["review", "survey", "meta-analysis"]):
            category = "reviews"
        elif any(word in title + snippet for word in ["application", "implementation", "case study"]):
            category = "applications"
        else:
            category = "other"

        # Add literature review metadata
        enhanced_source = source.copy()
        enhanced_source.update({
            "category": category,
            "topic_relevance": source.get("relevance_score", 0.5),
            "potential_sections": await self._identify_relevant_sections(source, sections),
            "citation_key": source.get("citation_key", f"unknown_{hash(source.get('title', ''))}")
        })

        return enhanced_source

    async def _deduplicate_and_rank_sources(self, sources: list[dict], topic: str) -> list[dict]:
        """Remove duplicate sources and rank by relevance"""
        # Simple deduplication based on title similarity
        unique_sources = []
        seen_titles = set()

        for source in sources:
            title = source.get("title", "").lower()
            title_key = "".join(title.split()[:5])  # First 5 words as key

            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_sources.append(source)

        # Rank by relevance score
        unique_sources.sort(key=lambda x: x.get("topic_relevance", 0), reverse=True)

        return unique_sources

    async def _assess_source_coverage(self, sources: list[dict], topic: str, scope: str) -> str:
        """Assess the coverage quality of gathered sources"""
        if not sources:
            return f"No sources found for '{topic}'. Consider broadening search terms or checking document collection."

        # Analyze source distribution
        categories = {}
        for source in sources:
            category = source.get("category", "other")
            categories[category] = categories.get(category, 0) + 1

        coverage_notes = []

        if len(sources) < 5:
            coverage_notes.append("Limited source count - consider expanding search")
        elif len(sources) > 50:
            coverage_notes.append("Extensive sources available - may need to focus scope")
        else:
            coverage_notes.append("Good source coverage identified")

        # Check for methodological diversity
        if categories.get("methodology", 0) < 2:
            coverage_notes.append("Consider adding more methodological sources")

        # Check for empirical evidence
        if categories.get("findings", 0) < 3:
            coverage_notes.append("More empirical studies would strengthen the review")

        return "; ".join(coverage_notes)

    async def _recommend_sections(self, sources: list[dict], topic: str, requested_sections: list[str] | None) -> list[str]:
        """Recommend literature review sections based on source analysis"""
        standard_sections = ["background", "methodology", "results", "discussion"]

        if requested_sections:
            return requested_sections

        # Recommend sections based on source categories
        recommendations = ["background"]  # Always include background

        source_categories = {}
        for source in sources:
            category = source.get("category", "other")
            source_categories[category] = source_categories.get(category, 0) + 1

        if source_categories.get("methodology", 0) > 2:
            recommendations.append("methodology")

        if source_categories.get("findings", 0) > 3:
            recommendations.append("results")

        if len(sources) > 10:
            recommendations.append("discussion")

        return recommendations

    async def _get_section_specific_queries(self, topic: str, section: str) -> list[str]:
        """Generate section-specific queries for fact finding"""
        if section == "background":
            return [
                f"background of {topic}",
                f"historical development of {topic}",
                f"theoretical foundations of {topic}",
                f"definition and scope of {topic}"
            ]
        elif section == "methodology":
            return [
                f"research methods used in {topic}",
                f"methodological approaches to {topic}",
                f"data collection techniques for {topic}",
                f"analysis methods in {topic} research"
            ]
        elif section == "results":
            return [
                f"key findings in {topic} research",
                f"main results of {topic} studies",
                f"empirical evidence about {topic}",
                f"quantitative results on {topic}"
            ]
        elif section == "discussion":
            return [
                f"implications of {topic} research",
                f"limitations in {topic} studies",
                f"future directions for {topic}",
                f"controversies in {topic} research"
            ]
        else:
            return [f"comprehensive analysis of {topic}"]

    async def _extract_cited_facts(self, query_result, citation_style: str) -> list[dict[str, Any]]:
        """Extract facts with citations from query results"""
        facts = []

        if not query_result.formal_response:
            return facts

        # Simple fact extraction (in production, use more sophisticated NLP)
        sentences = query_result.formal_response.split('.')

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) > 20:  # Reasonable sentence length
                # Look for citations in the sentence
                citation_key = None
                if query_result.citations_used and i < len(query_result.citations_used):
                    citation_key = query_result.citations_used[i % len(query_result.citations_used)]

                # Generate in-text citation
                if citation_key and self.citation_manager:
                    in_text_citation = self.citation_manager.generate_in_text_citation(
                        citation_key, citation_style
                    )
                    statement = f"{sentence} {in_text_citation}."
                else:
                    statement = f"{sentence}."
                    citation_key = "unknown"

                facts.append({
                    "statement": statement,
                    "citation_key": citation_key,
                    "confidence": query_result.confidence,
                    "strength": "strong" if query_result.confidence > 0.8 else "moderate"
                })

        return facts

    async def _organize_facts_by_strength(self, facts: list[dict], topic: str) -> list[dict[str, Any]]:
        """Organize facts by evidence strength and relevance"""
        # Sort by confidence and then by relevance to topic
        facts.sort(key=lambda f: (f.get("confidence", 0), len(f.get("statement", ""))), reverse=True)

        # Add metadata
        for i, fact in enumerate(facts):
            fact["rank"] = i + 1
            fact["evidence_quality"] = "high" if fact.get("confidence", 0) > 0.8 else "moderate"

        return facts

    async def _analyze_claim_evidence(self, claim: str, query_result, evidence_strength: str) -> ClaimVerification:
        """Analyze evidence for claim verification"""
        supporting_evidence = []
        contradicting_evidence = []
        neutral_evidence = []

        # Analyze search results for evidence type
        for result in query_result.primary_results:
            snippet = result.get("snippet", "").lower()

            # Simple sentiment analysis for claim support
            if any(word in snippet for word in ["confirm", "support", "validate", "evidence for"]):
                supporting_evidence.append({
                    "source": result.get("title", "Unknown"),
                    "evidence": result.get("snippet", ""),
                    "citation_key": result.get("citation_key", "unknown"),
                    "confidence": result.get("relevance_score", 0.5)
                })
            elif any(word in snippet for word in ["contradict", "oppose", "challenge", "refute"]):
                contradicting_evidence.append({
                    "source": result.get("title", "Unknown"),
                    "evidence": result.get("snippet", ""),
                    "citation_key": result.get("citation_key", "unknown"),
                    "confidence": result.get("relevance_score", 0.5)
                })
            else:
                neutral_evidence.append({
                    "source": result.get("title", "Unknown"),
                    "evidence": result.get("snippet", ""),
                    "citation_key": result.get("citation_key", "unknown"),
                    "confidence": result.get("relevance_score", 0.5)
                })

        # Determine verification status
        support_strength = len(supporting_evidence)
        contradict_strength = len(contradicting_evidence)

        if support_strength > contradict_strength * 2:
            status = "supported"
            recommendation = "Claim is well-supported by available evidence"
        elif contradict_strength > support_strength * 2:
            status = "contradicted"
            recommendation = "Claim is contradicted by available evidence"
        elif support_strength > 0 and contradict_strength > 0:
            status = "mixed"
            recommendation = "Mixed evidence - claim requires careful qualification"
        else:
            status = "insufficient"
            recommendation = "Insufficient evidence to verify claim"

        confidence = min(1.0, (support_strength + contradict_strength) / 5.0)

        return ClaimVerification(
            claim=claim,
            verification_status=status,
            evidence_strength=evidence_strength,
            supporting_evidence=supporting_evidence,
            contradicting_evidence=contradicting_evidence,
            neutral_evidence=neutral_evidence,
            confidence=confidence,
            recommendation=recommendation
        )

    async def _generate_outline_structure(self, topic: str, section_type: str) -> list[dict[str, Any]]:
        """Generate basic outline structure for section type"""
        if section_type == "background":
            return [
                {"title": "Introduction and Context", "content": [], "subsections": []},
                {"title": "Historical Development", "content": [], "subsections": []},
                {"title": "Theoretical Foundations", "content": [], "subsections": []},
                {"title": "Current State", "content": [], "subsections": []}
            ]
        elif section_type == "methodology":
            return [
                {"title": "Research Approaches", "content": [], "subsections": []},
                {"title": "Data Collection Methods", "content": [], "subsections": []},
                {"title": "Analysis Techniques", "content": [], "subsections": []},
                {"title": "Methodological Considerations", "content": [], "subsections": []}
            ]
        elif section_type == "results":
            return [
                {"title": "Key Findings", "content": [], "subsections": []},
                {"title": "Quantitative Results", "content": [], "subsections": []},
                {"title": "Qualitative Insights", "content": [], "subsections": []},
                {"title": "Comparative Analysis", "content": [], "subsections": []}
            ]
        elif section_type == "discussion":
            return [
                {"title": "Interpretation of Findings", "content": [], "subsections": []},
                {"title": "Implications", "content": [], "subsections": []},
                {"title": "Limitations", "content": [], "subsections": []},
                {"title": "Future Directions", "content": [], "subsections": []}
            ]
        else:  # full_review
            return [
                {"title": "Introduction", "content": [], "subsections": []},
                {"title": "Background and Context", "content": [], "subsections": []},
                {"title": "Methodology and Approaches", "content": [], "subsections": []},
                {"title": "Key Findings and Results", "content": [], "subsections": []},
                {"title": "Discussion and Implications", "content": [], "subsections": []},
                {"title": "Conclusions and Future Work", "content": [], "subsections": []}
            ]

    async def _populate_outline_with_sources(self, outline_structure: list[dict], topic: str) -> list[dict[str, Any]]:
        """Populate outline structure with relevant sources and content points"""
        # This would be implemented with actual source matching logic
        # For now, return the structure with placeholder content

        for section in outline_structure:
            section["content"] = [
                f"Key point about {topic} relevant to {section['title'].lower()}",
                f"Evidence and findings related to {section['title'].lower()}",
                f"Synthesis of research on {section['title'].lower()}"
            ]
            section["source_count"] = 3  # Placeholder

        return outline_structure

    async def _extract_key_themes(self, outline: list[dict], topic: str) -> list[str]:
        """Extract key themes from populated outline"""
        # Simplified theme extraction
        themes = []
        for section in outline:
            title_words = section["title"].lower().split()
            for word in title_words:
                if len(word) > 4 and word not in ["and", "the", "of", "in", "for"]:
                    themes.append(word.title())

        return list(set(themes))[:5]  # Top 5 unique themes

    async def _calculate_source_distribution(self, outline: list[dict]) -> dict[str, int]:
        """Calculate distribution of sources across outline sections"""
        distribution = {}
        for section in outline:
            distribution[section["title"]] = section.get("source_count", 0)
        return distribution

    async def _estimate_section_length(self, outline: list[dict], section_type: str) -> str:
        """Estimate the length of the literature review section"""
        section_count = len(outline)

        if section_type == "background":
            return f"Approximately {section_count * 2}-{section_count * 3} pages"
        elif section_type == "methodology":
            return f"Approximately {section_count * 1}-{section_count * 2} pages"
        elif section_type == "full_review":
            return f"Approximately {section_count * 3}-{section_count * 5} pages"
        else:
            return f"Approximately {section_count * 1.5}-{section_count * 2.5} pages"

    async def _generate_writing_guidance(self, section_type: str, topic: str) -> list[str]:
        """Generate writing guidance for the section"""
        guidance = [
            "Maintain formal academic tone throughout",
            "Ensure each claim is supported by appropriate citations",
            "Use clear topic sentences to introduce each paragraph"
        ]

        if section_type == "background":
            guidance.extend([
                "Begin with broad context and narrow to specific topic",
                "Establish the importance and relevance of the research area",
                "Define key terms and concepts clearly"
            ])
        elif section_type == "methodology":
            guidance.extend([
                "Group similar methodological approaches together",
                "Compare and contrast different research methods",
                "Highlight methodological innovations and limitations"
            ])
        elif section_type == "results":
            guidance.extend([
                "Present findings in logical order",
                "Use quantitative data where available",
                "Acknowledge conflicting results and explain discrepancies"
            ])

        return guidance

    async def _identify_relevant_sections(self, source: dict[str, Any], sections: list[str] | None) -> list[str]:
        """Identify which sections a source is relevant for"""
        if not sections:
            return ["general"]

        title = source.get("title", "").lower()
        snippet = source.get("snippet", "").lower()

        relevant = []
        for section in sections:
            if section.lower() in title or section.lower() in snippet:
                relevant.append(section)

        return relevant if relevant else ["general"]


# Factory function for easy integration
def create_literature_tools_engine(query_engine=None, citation_manager=None) -> LiteratureToolsEngine:
    """Create a literature review tools engine with default components"""
    return LiteratureToolsEngine(
        query_engine=query_engine,
        citation_manager=citation_manager
    )

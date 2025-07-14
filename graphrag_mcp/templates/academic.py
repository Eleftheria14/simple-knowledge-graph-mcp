"""
Academic Domain Template for GraphRAG MCP Toolkit

Specialized template for academic literature review and research analysis.
Optimized for scientific papers, citations, and research workflows.
"""

from typing import Dict, List, Any

from .base import (
    BaseTemplate, TemplateConfig, EntityConfig, RelationshipConfig, 
    MCPToolConfig, template_registry
)


class AcademicTemplate(BaseTemplate):
    """
    Academic domain template for literature review and research analysis.
    
    Optimized for:
    - Scientific paper analysis
    - Literature review synthesis  
    - Citation tracking and verification
    - Research gap identification
    - Cross-paper relationship discovery
    """
    
    def get_template_config(self) -> TemplateConfig:
        """Get academic template configuration"""
        
        # Academic domain guidance (hints, not constraints)
        # These suggest what might be important but don't limit discovery
        domain_guidance = [
            EntityConfig(
                name="academic_guidance",
                description="Guidance for academic document analysis - extract everything but pay special attention to research-related entities",
                max_entities=999,  # No limits
                examples=["authors", "institutions", "research methods", "theories", "datasets", "metrics", "citations"]
            )
        ]
        
        # Define academic relationship patterns (applied to discovered entities)
        relationships = [
            RelationshipConfig(
                name="cites",
                description="One entity cites, references, or builds upon another",
                source_entities=["any"],  # Applied to discovered entities
                target_entities=["any"]
            ),
            RelationshipConfig(
                name="extends",
                description="One approach extends or builds upon another", 
                source_entities=["any"],
                target_entities=["any"]
            ),
            RelationshipConfig(
                name="compares",
                description="Entities that are compared or contrasted",
                source_entities=["any"],
                target_entities=["any"]
            ),
            RelationshipConfig(
                name="uses",
                description="One entity uses, employs, or leverages another",
                source_entities=["any"],
                target_entities=["any"]
            ),
            RelationshipConfig(
                name="evaluates_on",
                description="Evaluation or testing relationships",
                source_entities=["any"],
                target_entities=["any"]
            ),
            RelationshipConfig(
                name="improves",
                description="One entity improves, enhances, or optimizes another",
                source_entities=["any"],
                target_entities=["any"]
            ),
            RelationshipConfig(
                name="addresses",
                description="Solutions addressing problems or challenges",
                source_entities=["any"],
                target_entities=["any"] 
            ),
            RelationshipConfig(
                name="collaborates_with",
                description="Collaborative or partnership relationships",
                source_entities=["any"],
                target_entities=["any"]
            ),
            RelationshipConfig(
                name="authored_by",
                description="Work or contribution authorship",
                source_entities=["any"],
                target_entities=["any"]
            ),
            RelationshipConfig(
                name="related_to", 
                description="General semantic relationship between entities",
                source_entities=["any"],
                target_entities=["any"]
            )
        ]
        
        # Define MCP tools for academic domain - organized by category
        mcp_tools = []
        
        # CHAT TOOLS - Conversational knowledge exploration
        chat_tools = [
            MCPToolConfig(
                name="ask_knowledge_graph",
                description="Ask natural questions about the knowledge graph and get conversational answers",
                parameters={
                    "question": {"type": "string", "description": "Your question about the research"},
                    "depth": {"type": "string", "enum": ["quick", "detailed"], "default": "quick", "description": "Response detail level"}
                },
                implementation="conversational_query"
            ),
            MCPToolConfig(
                name="explore_topic", 
                description="Explore a research topic to understand its key aspects and relationships",
                parameters={
                    "topic": {"type": "string", "description": "Research topic to explore"},
                    "scope": {"type": "string", "enum": ["overview", "detailed", "comprehensive"], "default": "overview", "description": "Exploration scope"}
                },
                implementation="topic_exploration"
            ),
            MCPToolConfig(
                name="find_connections",
                description="Discover how different concepts, methods, or ideas are connected",
                parameters={
                    "concept_a": {"type": "string", "description": "First concept or idea"},
                    "concept_b": {"type": "string", "description": "Second concept or idea"},
                    "connection_types": {"type": "array", "items": {"type": "string"}, "optional": True, "description": "Types of connections to look for"}
                },
                implementation="connection_analysis"
            ),
            MCPToolConfig(
                name="what_do_we_know_about",
                description="Get a comprehensive overview of what the research says about a specific topic",
                parameters={
                    "topic": {"type": "string", "description": "Topic to summarize knowledge about"},
                    "include_gaps": {"type": "boolean", "default": True, "description": "Include knowledge gaps"}
                },
                implementation="knowledge_overview"
            )
        ]
        
        # LITERATURE REVIEW TOOLS - Formal writing with citations
        literature_tools = [
            MCPToolConfig(
                name="gather_sources_for_topic",
                description="Gather and organize sources for a specific literature review topic",
                parameters={
                    "topic": {"type": "string", "description": "Literature review topic"},
                    "scope": {"type": "string", "enum": ["focused", "comprehensive", "survey"], "default": "comprehensive", "description": "Review scope"},
                    "sections": {"type": "array", "items": {"type": "string"}, "optional": True, "description": "Specific sections to focus on"}
                },
                implementation="source_gathering"
            ),
            MCPToolConfig(
                name="get_facts_with_citations",
                description="Get factual statements about a topic with proper citations for literature review writing",
                parameters={
                    "topic": {"type": "string", "description": "Topic to get facts about"},
                    "section": {"type": "string", "optional": True, "description": "Literature review section (background, methods, results, etc.)"},
                    "citation_style": {"type": "string", "enum": ["APA", "IEEE", "Nature", "MLA"], "default": "APA", "description": "Citation format"}
                },
                implementation="cited_facts"
            ),
            MCPToolConfig(
                name="verify_claim_with_sources",
                description="Verify a claim and provide supporting evidence with citations",
                parameters={
                    "claim": {"type": "string", "description": "Claim to verify"},
                    "evidence_strength": {"type": "string", "enum": ["any", "strong", "conclusive"], "default": "strong", "description": "Required evidence strength"}
                },
                implementation="claim_verification"
            ),
            MCPToolConfig(
                name="get_topic_outline",
                description="Generate an outline for a literature review section with key points and sources",
                parameters={
                    "topic": {"type": "string", "description": "Topic for the outline"},
                    "section_type": {"type": "string", "enum": ["background", "methods", "results", "discussion", "full_review"], "default": "full_review", "description": "Type of literature review section"}
                },
                implementation="outline_generation"
            ),
            MCPToolConfig(
                name="track_citations_used",
                description="Track which citations you've used in your writing to maintain proper attribution",
                parameters={
                    "citation_keys": {"type": "array", "items": {"type": "string"}, "description": "Citation keys being used"},
                    "context": {"type": "string", "optional": True, "description": "Context where citations are used"}
                },
                implementation="citation_tracking"
            ),
            MCPToolConfig(
                name="generate_bibliography",
                description="Generate a formatted bibliography of all used citations",
                parameters={
                    "style": {"type": "string", "enum": ["APA", "IEEE", "Nature", "MLA"], "default": "APA", "description": "Citation style"},
                    "used_only": {"type": "boolean", "default": True, "description": "Only include cited papers"},
                    "sort_by": {"type": "string", "enum": ["author", "year", "title", "usage"], "default": "author", "description": "Sort order"}
                },
                implementation="bibliography_generation"
            )
        ]
        
        # LEGACY/CORE TOOLS - Existing functionality 
        core_tools = [
            MCPToolConfig(
                name="query_papers",
                description="Search and query papers in the corpus (core search functionality)",
                parameters={
                    "query": {"type": "string", "description": "Natural language query"},
                    "entity_filter": {"type": "string", "optional": True, "description": "Filter by entity type"},
                    "limit": {"type": "integer", "default": 10, "description": "Maximum results"}
                },
                implementation="semantic_search"
            ),
            MCPToolConfig(
                name="research_gaps",
                description="Identify research gaps and opportunities (analytical tool)",
                parameters={
                    "domain": {"type": "string", "description": "Research domain or topic"},
                    "depth": {"type": "string", "enum": ["surface", "deep"], "default": "surface"}
                },
                implementation="gap_analysis"
            ),
            MCPToolConfig(
                name="methodology_overview",
                description="Compare and analyze research methodologies (analytical tool)",
                parameters={
                    "topic": {"type": "string", "description": "Research topic or area"},
                    "include_evolution": {"type": "boolean", "default": True, "description": "Include temporal evolution"}
                },
                implementation="methodology_analysis"
            ),
            MCPToolConfig(
                name="author_analysis",
                description="Analyze author contributions and collaborations (analytical tool)",
                parameters={
                    "author": {"type": "string", "optional": True, "description": "Specific author name"},
                    "institution": {"type": "string", "optional": True, "description": "Institution filter"}
                },
                implementation="author_network_analysis"
            ),
            MCPToolConfig(
                name="concept_evolution",
                description="Track how concepts evolve across papers (analytical tool)",
                parameters={
                    "concept": {"type": "string", "description": "Concept to track"},
                    "time_range": {"type": "string", "optional": True, "description": "Time period"}
                },
                implementation="temporal_concept_analysis"
            )
        ]
        
        # Combine all tools
        mcp_tools = chat_tools + literature_tools + core_tools
        
        return TemplateConfig(
            name="Academic Research",
            description="Template for academic literature review and research analysis",
            version="1.0.0",
            domain="academic",
            entities=domain_guidance,  # Guidance hints, not constraints
            relationships=relationships,
            mcp_tools=mcp_tools,
            metadata={
                "citation_styles": ["APA", "IEEE", "Nature", "MLA"],
                "supported_formats": ["PDF", "arXiv", "DOI"],
                "analysis_types": ["literature_review", "gap_analysis", "methodology_comparison"],
                "output_formats": ["structured_text", "markdown", "latex"],
                "workflow_phases": [
                    "corpus_building",
                    "entity_extraction", 
                    "relationship_mapping",
                    "analysis_and_synthesis",
                    "writing_and_citation"
                ]
            }
        )
    
    def get_entity_schema(self) -> Dict[str, str]:
        """Get domain guidance for academic documents (not constraints)"""
        return {
            "academic": "academic research context - extract all entities but focus on research-related information like authors, institutions, methods, concepts, datasets, and citations"
        }
    
    def get_relationship_schema(self) -> List[Dict[str, Any]]:
        """Get relationship schema for academic knowledge graphs"""
        return [
            {
                "name": rel.name,
                "description": rel.description,
                "source_entities": rel.source_entities,
                "target_entities": rel.target_entities
            }
            for rel in self.config.relationships
        ]
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tool definitions for academic domain"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "implementation": tool.implementation
            }
            for tool in self.config.mcp_tools
        ]
    
    def generate_example_queries(self) -> List[str]:
        """Generate academic-specific example queries"""
        return [
            # General academic queries
            "What are the main findings of this research?",
            "What research methods were employed in this study?",
            "Who are the primary contributors to this field?",
            "What datasets were used for evaluation?",
            
            # Literature review specific
            "How has this field evolved over time?",
            "What are the current limitations and challenges?",
            "Which approaches have been most successful?",
            "What gaps exist in the current research?",
            
            # Methodology focused
            "Compare the different approaches to solving this problem",
            "What evaluation metrics are commonly used?",
            "How do the proposed methods differ from existing work?",
            "What are the theoretical foundations of these approaches?",
            
            # Citation and evidence
            "Find evidence for the claim that deep learning outperforms traditional methods",
            "What papers support the use of transformer architectures?",
            "Show me the citation trail for this specific technique",
            "Verify the accuracy of this performance benchmark"
        ]
    
    def validate_document(self, document_path: str) -> Dict[str, Any]:
        """Validate document for academic template"""
        result = super().validate_document(document_path)
        
        if not result["valid"]:
            return result
        
        # Additional academic-specific validation
        from pathlib import Path
        path = Path(document_path)
        
        # Check for academic indicators in filename
        academic_indicators = [
            "arxiv", "paper", "research", "study", "analysis", 
            "conference", "journal", "proceedings"
        ]
        
        filename_lower = path.stem.lower()
        has_academic_indicators = any(
            indicator in filename_lower for indicator in academic_indicators
        )
        
        if has_academic_indicators:
            result["score"] = min(result["score"] + 0.1, 1.0)
            result["messages"].append("Filename suggests academic content")
        
        # Add academic-specific recommendations
        result["recommendations"].extend([
            "Ensure document contains citations and references",
            "Check for methodology and results sections",
            "Verify author and institution information is present"
        ])
        
        return result
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get academic-specific processing configuration"""
        config = super().get_processing_config()
        
        # Academic-specific settings
        config.update({
            "citation_extraction": True,
            "author_extraction": True,
            "methodology_focus": True,
            "section_analysis": ["abstract", "introduction", "methodology", "results", "discussion", "conclusion"],
            "reference_parsing": True,
            "academic_entity_priority": ["authors", "methods", "concepts", "institutions"],
            "literature_review_mode": True
        })
        
        return config


# Register the academic template
template_registry.register("academic", AcademicTemplate)
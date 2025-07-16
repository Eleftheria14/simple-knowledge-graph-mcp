"""
Advanced Document Analyzer for GraphRAG MCP Toolkit

Domain-agnostic advanced analysis with GraphRAG-compatible output.
Extracted and refactored from EnhancedPaperAnalyzer to support multiple domains.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
from pydantic import BaseModel, Field

# Core components
from .document_processor import DocumentData, DocumentProcessor
from .ollama_engine import OllamaEngine

logger = logging.getLogger(__name__)


class AnalysisConfig(BaseModel):
    """Configuration for advanced analysis"""
    extract_entities: bool = Field(default=True, description="Extract entities during analysis")
    extract_relationships: bool = Field(default=True, description="Extract entity relationships")
    generate_summary: bool = Field(default=True, description="Generate document summary")
    max_entities_per_type: int = Field(default=10, description="Maximum entities per type")
    citation_tracking: bool = Field(default=True, description="Track citation locations")
    corpus_format: bool = Field(default=True, description="Output in corpus-compatible format")


class CorpusDocument(BaseModel):
    """GraphRAG-compatible corpus document format"""
    document_id: str = Field(description="Unique document identifier")
    title: str = Field(description="Document title")
    content: str = Field(description="Full document content")
    metadata: dict[str, Any] = Field(description="Rich metadata")
    entities: dict[str, list[str]] = Field(description="Extracted entities")
    relationships: list[dict[str, Any]] = Field(description="Entity relationships")
    sections: dict[str, str] = Field(description="Document sections")
    citations: list[dict[str, Any]] = Field(description="Citation information")
    analysis_date: str = Field(description="Analysis timestamp")
    source_path: str = Field(description="Original file path")


class AdvancedAnalyzer:
    """
    Advanced document analyzer with GraphRAG-compatible output.
    
    Provides comprehensive analysis including entity extraction, relationship
    mapping, and corpus-ready formatting for cross-document analysis.
    """

    def __init__(self,
                 document_processor: DocumentProcessor | None = None,
                 ollama_engine: OllamaEngine | None = None,
                 config: AnalysisConfig | None = None):
        """Initialize advanced analyzer"""
        self.config = config or AnalysisConfig()

        # Core components
        self.document_processor = document_processor or DocumentProcessor()
        self.ollama_engine = ollama_engine or OllamaEngine()

        logger.info("🔬 AdvancedAnalyzer initialized")

    def analyze_for_corpus(self, pdf_path: str,
                          domain_schema: dict[str, str] | None = None) -> CorpusDocument:
        """
        Analyze document and return GraphRAG-compatible corpus format
        
        Args:
            pdf_path: Path to PDF file
            domain_schema: Domain-specific entity schema
            
        Returns:
            Corpus-compatible document with rich metadata
        """
        logger.info(f"📄 Analyzing document for corpus: {Path(pdf_path).name}")

        try:
            # Load document
            document_data = self.document_processor.load_document(pdf_path)

            # Extract entities with domain schema
            entities = {}
            if self.config.extract_entities:
                entities = self.document_processor.extract_entities(
                    domain_guidance=domain_schema or self._get_default_schema()
                )

            # Extract relationships if enabled
            relationships = []
            if self.config.extract_relationships:
                relationships = self._extract_relationships(document_data, entities)

            # Generate document sections
            sections = self._extract_sections(document_data.content)

            # Extract citations
            citations = []
            if self.config.citation_tracking:
                citations = self._extract_citations(document_data.content)

            # Generate summary if enabled
            summary = ""
            if self.config.generate_summary:
                summary = self._generate_summary(document_data)

            # Create corpus document
            document_id = self._generate_document_id(pdf_path)

            corpus_doc = CorpusDocument(
                document_id=document_id,
                title=document_data.title,
                content=document_data.content,
                metadata={
                    "file_path": pdf_path,
                    "file_name": Path(pdf_path).name,
                    "chunk_count": len(document_data.chunks),
                    "character_count": len(document_data.content),
                    "citation": document_data.citation,
                    "summary": summary,
                    "processing_config": self.config.model_dump(),
                    "analysis_version": "advanced_v1.0",
                    "capabilities": [
                        "entity_extraction",
                        "relationship_mapping",
                        "citation_tracking",
                        "cross_document_linking"
                    ]
                },
                entities=entities,
                relationships=relationships,
                sections=sections,
                citations=citations,
                analysis_date=datetime.now().isoformat(),
                source_path=pdf_path
            )

            logger.info(f"✅ Corpus analysis complete: {document_data.title[:50]}...")
            return corpus_doc

        except Exception as e:
            logger.error(f"❌ Corpus analysis failed: {e}")
            raise

    def analyze_document(self, pdf_path: str,
                        domain_schema: dict[str, str] | None = None) -> dict[str, Any]:
        """
        Standard document analysis with flexible output
        
        Args:
            pdf_path: Path to PDF file
            domain_schema: Domain-specific entity schema
            
        Returns:
            Analysis results dictionary
        """
        logger.info(f"📊 Standard document analysis: {Path(pdf_path).name}")

        try:
            # Load and process document
            document_data = self.document_processor.load_document(pdf_path)

            # Extract entities
            entities = self.document_processor.extract_entities(
                domain_guidance=domain_schema or self._get_default_schema()
            )

            # Create analysis result
            result = {
                "document_info": {
                    "title": document_data.title,
                    "citation": document_data.citation,
                    "file_path": pdf_path,
                    "chunk_count": len(document_data.chunks),
                    "character_count": len(document_data.content)
                },
                "entities": entities,
                "analysis_date": datetime.now().isoformat(),
                "status": "completed"
            }

            # Add optional components
            if self.config.extract_relationships:
                result["relationships"] = self._extract_relationships(document_data, entities)

            if self.config.generate_summary:
                result["summary"] = self._generate_summary(document_data)

            logger.info("✅ Document analysis completed successfully")
            return result

        except Exception as e:
            logger.error(f"❌ Document analysis failed: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "analysis_date": datetime.now().isoformat()
            }

    def _get_default_schema(self) -> dict[str, str]:
        """Get default entity schema for general documents"""
        return {
            "authors": "Authors and contributors",
            "organizations": "Organizations and institutions",
            "methods": "Methods and techniques",
            "concepts": "Key concepts and theories",
            "technologies": "Technologies and tools",
            "metrics": "Measurements and metrics",
            "datasets": "Datasets and data sources",
            "locations": "Geographic locations",
            "dates": "Important dates and timeframes",
            "products": "Products and systems"
        }

    def _extract_relationships(self, document_data: DocumentData,
                             entities: dict[str, list[str]]) -> list[dict[str, Any]]:
        """Extract relationships between entities"""
        relationships = []

        try:
            # Use LLM to identify relationships
            entity_text = ""
            for entity_type, entity_list in entities.items():
                if entity_list:
                    entity_text += f"{entity_type}: {', '.join(entity_list[:3])}\\n"

            if not entity_text:
                return relationships

            # Use first 2000 characters for relationship extraction
            content_sample = document_data.content[:2000]

            # Create prompt with direct f-string formatting to avoid LangChain template issues
            prompt_text = f"""
Analyze the relationships between entities in this document. 
Return relationships in JSON format:

[
  {{"source": "Entity1", "relationship": "uses", "target": "Entity2"}},
  {{"source": "Entity2", "relationship": "improves", "target": "Entity3"}}
]

Entities:
{entity_text}

Document excerpt:
{content_sample}

Focus on the most important relationships. Limit to 10 relationships.

JSON:"""

            # Use direct chat method instead of create_chain
            result = self.ollama_engine.chat(prompt_text)

            # Parse JSON response
            import json
            json_start = result.find('[')
            json_end = result.rfind(']') + 1

            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                relationships = json.loads(json_str)
                logger.debug(f"🔗 Extracted {len(relationships)} relationships")

        except Exception as e:
            logger.error(f"❌ Relationship extraction failed: {e}")

        return relationships

    def _extract_sections(self, content: str) -> dict[str, str]:
        """Extract document sections"""
        sections = {}

        try:
            # Common section patterns
            section_patterns = [
                r"(?i)^(abstract|introduction|methodology|methods|results|discussion|conclusion|references?)\\s*$",
                r"(?i)^\\d+\\.?\\s+(introduction|methodology|methods|results|discussion|conclusion)",
                r"(?i)^(background|literature\\s+review|related\\s+work|experimental|analysis)"
            ]

            lines = content.split('\\n')
            current_section = "content"
            current_content = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if line is a section header
                is_section = False
                for pattern in section_patterns:
                    if re.match(pattern, line):
                        # Save previous section
                        if current_content:
                            sections[current_section] = '\\n'.join(current_content)

                        # Start new section
                        current_section = line.lower().strip(':.')
                        current_content = []
                        is_section = True
                        break

                if not is_section:
                    current_content.append(line)

            # Save final section
            if current_content:
                sections[current_section] = '\\n'.join(current_content)

            logger.debug(f"📑 Extracted {len(sections)} sections")

        except Exception as e:
            logger.error(f"❌ Section extraction failed: {e}")
            sections = {"content": content}

        return sections

    def _extract_citations(self, content: str) -> list[dict[str, Any]]:
        """Extract citation information"""
        citations = []

        try:
            # Citation patterns
            patterns = [
                r"\\[(\\d+)\\]",  # [1], [2], etc.
                r"\\(([^)]+,\\s*\\d{4})\\)",  # (Author, 2020)
                r"(\\w+\\s+et\\s+al\\.?,?\\s*\\d{4})",  # Smith et al. 2020
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    citations.append({
                        "text": match.group(0),
                        "position": match.start(),
                        "type": "inline_citation",
                        "extracted_by": "regex_pattern"
                    })

            logger.debug(f"📚 Extracted {len(citations)} citations")

        except Exception as e:
            logger.error(f"❌ Citation extraction failed: {e}")

        return citations

    def _generate_summary(self, document_data: DocumentData) -> str:
        """Generate document summary"""
        try:
            # Use first 3000 characters for summary
            content_sample = document_data.content[:3000]

            # Create a simple prompt without template variables to avoid LangChain issues
            prompt_text = f"""
Provide a concise summary of this document in 2-3 sentences.
Focus on the main purpose, key findings, and significance.

Document:
{content_sample}

Summary:"""

            # Use the simpler chat method instead of create_chain
            summary = self.ollama_engine.chat(prompt_text)

            logger.debug("📝 Generated document summary")
            return summary.strip()

        except Exception as e:
            logger.error(f"❌ Summary generation failed: {e}")
            return f"Summary generation failed: {str(e)}"

    def _generate_document_id(self, pdf_path: str) -> str:
        """Generate unique document ID"""
        # Use filename and hash for unique ID
        filename = Path(pdf_path).stem
        path_hash = hash(pdf_path) % 10000
        return f"{filename}_{path_hash}"


# Factory function for easy initialization
def create_advanced_analyzer(embedding_model: str = "nomic-embed-text",
                           llm_model: str = "llama3.1:8b") -> AdvancedAnalyzer:
    """Create an AdvancedAnalyzer with specified models"""
    # Create components
    document_processor = DocumentProcessor()
    ollama_engine = OllamaEngine()

    return AdvancedAnalyzer(
        document_processor=document_processor,
        ollama_engine=ollama_engine
    )

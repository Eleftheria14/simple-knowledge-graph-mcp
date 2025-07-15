"""
Citation Management System for GraphRAG MCP Toolkit

Provides comprehensive citation tracking, formatting, and bibliography generation
for literature review workflows. Supports multiple citation styles and maintains
precise source attribution for AI-generated content.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


@dataclass
class Citation:
    """Structured citation information"""
    key: str  # Unique citation key (e.g., "smith2023deep")
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    journal: str | None = None
    volume: str | None = None
    pages: str | None = None
    doi: str | None = None
    url: str | None = None
    abstract: str | None = None
    document_path: str | None = None
    citation_count: int = 0
    first_cited: datetime | None = None
    last_cited: datetime | None = None

    def __post_init__(self):
        if self.first_cited is None:
            self.first_cited = datetime.now()


class CitationContext(BaseModel):
    """Context information for where a citation was used"""
    citation_key: str
    context_text: str = Field(description="Text where citation was used")
    section: str | None = Field(default=None, description="Document section")
    page_number: int | None = Field(default=None)
    confidence: float = Field(default=1.0, description="Confidence in citation accuracy")
    timestamp: datetime = Field(default_factory=datetime.now)


class CitationUsage(BaseModel):
    """Track citation usage in generated content"""
    citation_key: str
    used_in_sections: list[str] = Field(default_factory=list)
    usage_contexts: list[CitationContext] = Field(default_factory=list)
    total_uses: int = 0

    def add_usage(self, context: CitationContext):
        """Add a new usage context"""
        self.usage_contexts.append(context)
        if context.section and context.section not in self.used_in_sections:
            self.used_in_sections.append(context.section)
        self.total_uses += 1


class CitationTracker:
    """
    Central citation management system for GraphRAG MCP toolkit.
    
    Provides:
    - Citation key generation and management
    - Usage tracking throughout document generation
    - Bibliography formatting in multiple styles
    - Citation verification and validation
    """

    def __init__(self):
        self.citations: dict[str, Citation] = {}
        self.used_citations: set[str] = set()
        self.citation_usage: dict[str, CitationUsage] = {}
        self.bibliography_style: str = "APA"

    def add_citation(self,
                    title: str,
                    authors: list[str] = None,
                    year: int = None,
                    **kwargs) -> str:
        """
        Add a new citation and return its key.
        
        Args:
            title: Paper title
            authors: List of author names
            year: Publication year
            **kwargs: Additional citation metadata
            
        Returns:
            Citation key for referencing
        """
        authors = authors or []

        # Generate citation key
        citation_key = self._generate_citation_key(title, authors, year)

        # Create citation object
        citation = Citation(
            key=citation_key,
            title=title,
            authors=authors,
            year=year,
            **kwargs
        )

        # Store citation
        self.citations[citation_key] = citation

        return citation_key

    def track_citation(self,
                      citation_key: str,
                      context_text: str = "",
                      section: str = None,
                      confidence: float = 1.0) -> bool:
        """
        Track usage of a citation in generated content.
        
        Args:
            citation_key: The citation key being used
            context_text: Text context where citation appears
            section: Document section (e.g., "Introduction", "Methods")
            confidence: Confidence in citation accuracy (0.0-1.0)
            
        Returns:
            True if tracking successful, False if citation not found
        """
        if citation_key not in self.citations:
            return False

        # Mark as used
        self.used_citations.add(citation_key)

        # Update citation usage count
        if citation_key in self.citations:
            self.citations[citation_key].citation_count += 1
            self.citations[citation_key].last_cited = datetime.now()

        # Track detailed usage
        if citation_key not in self.citation_usage:
            self.citation_usage[citation_key] = CitationUsage(citation_key=citation_key)

        context = CitationContext(
            citation_key=citation_key,
            context_text=context_text,
            section=section,
            confidence=confidence
        )

        self.citation_usage[citation_key].add_usage(context)

        return True

    def get_used_citations(self) -> list[Citation]:
        """Get all citations that have been used in generated content"""
        return [self.citations[key] for key in self.used_citations if key in self.citations]

    def get_unused_citations(self) -> list[Citation]:
        """Get all citations that haven't been used yet"""
        return [
            citation for key, citation in self.citations.items()
            if key not in self.used_citations
        ]

    def generate_bibliography(self,
                            style: str = "APA",
                            used_only: bool = True,
                            sort_by: str = "author") -> list[str]:
        """
        Generate formatted bibliography.
        
        Args:
            style: Citation style ("APA", "IEEE", "Nature", "MLA")
            used_only: Only include citations that were actually used
            sort_by: Sort order ("author", "year", "title", "usage")
            
        Returns:
            List of formatted citation strings
        """
        # Select citations
        if used_only:
            citations_to_format = self.get_used_citations()
        else:
            citations_to_format = list(self.citations.values())

        # Sort citations
        if sort_by == "author":
            citations_to_format.sort(key=lambda c: c.authors[0] if c.authors else c.title)
        elif sort_by == "year":
            citations_to_format.sort(key=lambda c: c.year or 0)
        elif sort_by == "title":
            citations_to_format.sort(key=lambda c: c.title)
        elif sort_by == "usage":
            citations_to_format.sort(key=lambda c: c.citation_count, reverse=True)

        # Format citations
        formatted_citations = []
        for citation in citations_to_format:
            formatted = self._format_citation(citation, style)
            if formatted:
                formatted_citations.append(formatted)

        return formatted_citations

    def generate_in_text_citation(self,
                                citation_key: str,
                                style: str = "APA",
                                page_number: str = None) -> str:
        """
        Generate in-text citation format.
        
        Args:
            citation_key: Citation to reference
            style: Citation style
            page_number: Optional page number
            
        Returns:
            Formatted in-text citation
        """
        if citation_key not in self.citations:
            return f"[{citation_key}]"  # Fallback

        citation = self.citations[citation_key]

        if style == "APA":
            author_part = self._get_author_year_apa(citation)
            if page_number:
                return f"({author_part}, p. {page_number})"
            return f"({author_part})"

        elif style == "IEEE":
            # Find index in bibliography order
            index = list(self.citations.keys()).index(citation_key) + 1
            return f"[{index}]"

        elif style == "Nature":
            index = list(self.citations.keys()).index(citation_key) + 1
            return f"{index}"

        elif style == "MLA":
            if citation.authors:
                author = citation.authors[0].split()[-1]  # Last name
                if page_number:
                    return f"({author} {page_number})"
                return f"({author})"

        return f"({citation_key})"

    def verify_citation(self, citation_key: str) -> dict[str, Any]:
        """
        Verify citation accuracy and completeness.
        
        Args:
            citation_key: Citation to verify
            
        Returns:
            Verification results
        """
        if citation_key not in self.citations:
            return {"valid": False, "error": "Citation not found"}

        citation = self.citations[citation_key]
        issues = []
        score = 1.0

        # Check required fields
        if not citation.title:
            issues.append("Missing title")
            score -= 0.3

        if not citation.authors:
            issues.append("Missing authors")
            score -= 0.2

        if not citation.year:
            issues.append("Missing publication year")
            score -= 0.2

        # Check DOI/URL availability
        if not citation.doi and not citation.url:
            issues.append("Missing DOI or URL")
            score -= 0.1

        # Check usage context
        if citation_key in self.citation_usage:
            usage = self.citation_usage[citation_key]
            avg_confidence = sum(ctx.confidence for ctx in usage.usage_contexts) / len(usage.usage_contexts)
            if avg_confidence < 0.7:
                issues.append("Low confidence in citation accuracy")
                score -= 0.2

        return {
            "valid": score > 0.5,
            "score": max(0.0, score),
            "issues": issues,
            "usage_count": citation.citation_count,
            "completeness": self._calculate_completeness(citation)
        }

    def export_citations(self, format: str = "json") -> str:
        """
        Export citations in various formats.
        
        Args:
            format: Export format ("json", "bibtex", "csv")
            
        Returns:
            Formatted export string
        """
        if format == "json":
            return json.dumps({
                "citations": {k: self._citation_to_dict(v) for k, v in self.citations.items()},
                "usage": {k: v.dict() for k, v in self.citation_usage.items()},
                "used_citations": list(self.used_citations)
            }, indent=2, default=str)

        elif format == "bibtex":
            bibtex_entries = []
            for citation in self.citations.values():
                bibtex_entries.append(self._citation_to_bibtex(citation))
            return "\n\n".join(bibtex_entries)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Key", "Title", "Authors", "Year", "Journal", "Used", "Usage Count"])

            for citation in self.citations.values():
                writer.writerow([
                    citation.key,
                    citation.title,
                    "; ".join(citation.authors),
                    citation.year,
                    citation.journal or "",
                    citation.key in self.used_citations,
                    citation.citation_count
                ])

            return output.getvalue()

        return ""

    def import_citations(self, data: str, format: str = "json"):
        """
        Import citations from external sources.
        
        Args:
            data: Citation data
            format: Data format ("json", "bibtex")
        """
        if format == "json":
            parsed = json.loads(data)

            # Import citations
            for key, citation_data in parsed.get("citations", {}).items():
                citation = Citation(**citation_data)
                self.citations[key] = citation

            # Import usage data
            for key, usage_data in parsed.get("usage", {}).items():
                self.citation_usage[key] = CitationUsage(**usage_data)

            # Import used citations set
            self.used_citations.update(parsed.get("used_citations", []))

    def get_citation_statistics(self) -> dict[str, Any]:
        """Get comprehensive citation statistics"""
        total_citations = len(self.citations)
        used_citations = len(self.used_citations)

        # Calculate usage statistics
        usage_counts = [citation.citation_count for citation in self.citations.values()]
        avg_usage = sum(usage_counts) / len(usage_counts) if usage_counts else 0

        # Most cited papers
        most_cited = sorted(self.citations.values(), key=lambda c: c.citation_count, reverse=True)[:5]

        return {
            "total_citations": total_citations,
            "used_citations": used_citations,
            "unused_citations": total_citations - used_citations,
            "usage_rate": used_citations / total_citations if total_citations > 0 else 0,
            "average_usage_per_citation": avg_usage,
            "most_cited": [{"key": c.key, "title": c.title, "count": c.citation_count} for c in most_cited],
            "citation_styles_supported": ["APA", "IEEE", "Nature", "MLA"]
        }

    # Private helper methods

    def _generate_citation_key(self, title: str, authors: list[str], year: int = None) -> str:
        """Generate unique citation key"""
        # Use first author's last name if available
        if authors:
            first_author = authors[0].split()[-1].lower()  # Last name
            # Remove non-alphanumeric characters
            first_author = re.sub(r'[^a-z]', '', first_author)
        else:
            # Use first word of title
            first_author = re.sub(r'[^a-z]', '', title.split()[0].lower())

        year_str = str(year) if year else "unknown"

        # Create base key
        base_key = f"{first_author}{year_str}"

        # Handle duplicates
        if base_key in self.citations:
            counter = 1
            while f"{base_key}_{counter}" in self.citations:
                counter += 1
            base_key = f"{base_key}_{counter}"

        return base_key

    def _format_citation(self, citation: Citation, style: str) -> str:
        """Format citation according to style"""
        if style == "APA":
            return self._format_apa(citation)
        elif style == "IEEE":
            return self._format_ieee(citation)
        elif style == "Nature":
            return self._format_nature(citation)
        elif style == "MLA":
            return self._format_mla(citation)
        else:
            return self._format_apa(citation)  # Default to APA

    def _format_apa(self, citation: Citation) -> str:
        """Format citation in APA style"""
        parts = []

        # Authors
        if citation.authors:
            if len(citation.authors) == 1:
                parts.append(citation.authors[0])
            elif len(citation.authors) <= 7:
                parts.append(", ".join(citation.authors[:-1]) + ", & " + citation.authors[-1])
            else:
                parts.append(", ".join(citation.authors[:6]) + ", ... " + citation.authors[-1])

        # Year
        if citation.year:
            parts.append(f"({citation.year})")

        # Title
        parts.append(f"{citation.title}.")

        # Journal
        if citation.journal:
            journal_part = f"*{citation.journal}*"
            if citation.volume:
                journal_part += f", {citation.volume}"
            if citation.pages:
                journal_part += f", {citation.pages}"
            parts.append(journal_part + ".")

        # DOI/URL
        if citation.doi:
            parts.append(f"https://doi.org/{citation.doi}")
        elif citation.url:
            parts.append(citation.url)

        return " ".join(parts)

    def _format_ieee(self, citation: Citation) -> str:
        """Format citation in IEEE style"""
        parts = []

        # Authors
        if citation.authors:
            if len(citation.authors) <= 3:
                parts.append(", ".join(citation.authors))
            else:
                parts.append(f"{citation.authors[0]} et al.")

        # Title
        parts.append(f'"{citation.title},"')

        # Journal
        if citation.journal:
            journal_part = f"*{citation.journal}*"
            if citation.volume:
                journal_part += f", vol. {citation.volume}"
            if citation.pages:
                journal_part += f", pp. {citation.pages}"
            parts.append(journal_part)

        # Year
        if citation.year:
            parts.append(f"{citation.year}.")

        return " ".join(parts)

    def _format_nature(self, citation: Citation) -> str:
        """Format citation in Nature style"""
        parts = []

        # Authors
        if citation.authors:
            if len(citation.authors) <= 5:
                parts.append(" & ".join(citation.authors))
            else:
                parts.append(f"{citation.authors[0]} et al.")

        # Title
        parts.append(f"{citation.title}.")

        # Journal
        if citation.journal:
            journal_part = f"*{citation.journal}*"
            if citation.volume:
                journal_part += f" **{citation.volume}**"
            if citation.pages:
                journal_part += f", {citation.pages}"
            parts.append(journal_part)

        # Year
        if citation.year:
            parts.append(f"({citation.year}).")

        return " ".join(parts)

    def _format_mla(self, citation: Citation) -> str:
        """Format citation in MLA style"""
        parts = []

        # Authors
        if citation.authors:
            if len(citation.authors) == 1:
                parts.append(f"{citation.authors[0]}.")
            else:
                first_author = citation.authors[0]
                others = citation.authors[1:]
                parts.append(f"{first_author}, et al.")

        # Title
        parts.append(f'"{citation.title}."')

        # Journal
        if citation.journal:
            journal_part = f"*{citation.journal}*"
            if citation.volume:
                journal_part += f", vol. {citation.volume}"
            if citation.pages:
                journal_part += f", pp. {citation.pages}"
            parts.append(journal_part)

        # Year
        if citation.year:
            parts.append(f"{citation.year}.")

        return " ".join(parts)

    def _get_author_year_apa(self, citation: Citation) -> str:
        """Get author-year format for APA in-text citations"""
        if not citation.authors:
            return citation.key

        if len(citation.authors) == 1:
            author_part = citation.authors[0].split()[-1]  # Last name
        elif len(citation.authors) == 2:
            author1 = citation.authors[0].split()[-1]
            author2 = citation.authors[1].split()[-1]
            author_part = f"{author1} & {author2}"
        else:
            first_author = citation.authors[0].split()[-1]
            author_part = f"{first_author} et al."

        year_part = str(citation.year) if citation.year else "n.d."

        return f"{author_part}, {year_part}"

    def _citation_to_dict(self, citation: Citation) -> dict[str, Any]:
        """Convert citation to dictionary for serialization"""
        return {
            "key": citation.key,
            "title": citation.title,
            "authors": citation.authors,
            "year": citation.year,
            "journal": citation.journal,
            "volume": citation.volume,
            "pages": citation.pages,
            "doi": citation.doi,
            "url": citation.url,
            "abstract": citation.abstract,
            "document_path": citation.document_path,
            "citation_count": citation.citation_count,
            "first_cited": citation.first_cited.isoformat() if citation.first_cited else None,
            "last_cited": citation.last_cited.isoformat() if citation.last_cited else None
        }

    def _citation_to_bibtex(self, citation: Citation) -> str:
        """Convert citation to BibTeX format"""
        entry_type = "article" if citation.journal else "misc"

        bibtex = f"@{entry_type}{{{citation.key},\n"
        bibtex += f"  title = {{{citation.title}}},\n"

        if citation.authors:
            authors_str = " and ".join(citation.authors)
            bibtex += f"  author = {{{authors_str}}},\n"

        if citation.year:
            bibtex += f"  year = {{{citation.year}}},\n"

        if citation.journal:
            bibtex += f"  journal = {{{citation.journal}}},\n"

        if citation.volume:
            bibtex += f"  volume = {{{citation.volume}}},\n"

        if citation.pages:
            bibtex += f"  pages = {{{citation.pages}}},\n"

        if citation.doi:
            bibtex += f"  doi = {{{citation.doi}}},\n"

        if citation.url:
            bibtex += f"  url = {{{citation.url}}},\n"

        bibtex += "}"

        return bibtex

    def _calculate_completeness(self, citation: Citation) -> float:
        """Calculate citation completeness score"""
        required_fields = ["title", "authors", "year"]
        optional_fields = ["journal", "volume", "pages", "doi", "url"]

        score = 0.0

        # Required fields (70% of score)
        for field in required_fields:
            if getattr(citation, field):
                score += 0.7 / len(required_fields)

        # Optional fields (30% of score)
        for field in optional_fields:
            if getattr(citation, field):
                score += 0.3 / len(optional_fields)

        return min(1.0, score)

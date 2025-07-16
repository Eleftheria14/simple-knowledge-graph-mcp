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
from typing import Any, Optional, List, Dict
from pathlib import Path

from pydantic import BaseModel, Field, validator
from ..utils.error_handling import ValidationError, ProcessingError


@dataclass
class Citation:
    """Structured citation information with validation"""
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
    _validation_errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.first_cited is None:
            self.first_cited = datetime.now()
        
        # Validate citation data
        self._validate_citation_data()
    
    def _validate_citation_data(self):
        """Validate citation data integrity"""
        self._validation_errors = []
        
        # Validate key format
        if not self.key or not isinstance(self.key, str):
            self._validation_errors.append("Citation key must be a non-empty string")
        elif not re.match(r'^[a-zA-Z0-9_-]+$', self.key):
            self._validation_errors.append("Citation key contains invalid characters")
        
        # Validate title
        if not self.title or not self.title.strip():
            self._validation_errors.append("Citation title cannot be empty")
        elif len(self.title) > 1000:
            self._validation_errors.append("Citation title too long (max 1000 characters)")
        
        # Validate authors
        if self.authors:
            for i, author in enumerate(self.authors):
                if not isinstance(author, str) or not author.strip():
                    self._validation_errors.append(f"Author {i+1} must be a non-empty string")
                elif len(author) > 200:
                    self._validation_errors.append(f"Author {i+1} name too long (max 200 characters)")
        
        # Validate year
        if self.year is not None:
            if not isinstance(self.year, int) or self.year < 1000 or self.year > datetime.now().year + 1:
                self._validation_errors.append(f"Invalid year: {self.year}")
        
        # Validate DOI format
        if self.doi:
            if not re.match(r'^10\.\d{4,}/.+', self.doi):
                self._validation_errors.append(f"Invalid DOI format: {self.doi}")
        
        # Validate URL format
        if self.url:
            if not re.match(r'^https?://', self.url):
                self._validation_errors.append(f"Invalid URL format: {self.url}")
        
        # Validate document path
        if self.document_path:
            try:
                path = Path(self.document_path)
                if not path.exists():
                    self._validation_errors.append(f"Document path does not exist: {self.document_path}")
            except Exception:
                self._validation_errors.append(f"Invalid document path: {self.document_path}")
        
        # Validate citation count
        if self.citation_count < 0:
            self._validation_errors.append("Citation count cannot be negative")
    
    def is_valid(self) -> bool:
        """Check if citation data is valid"""
        return len(self._validation_errors) == 0
    
    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors"""
        return self._validation_errors.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert citation to dictionary for serialization"""
        return {
            'key': self.key,
            'title': self.title,
            'authors': self.authors,
            'year': self.year,
            'journal': self.journal,
            'volume': self.volume,
            'pages': self.pages,
            'doi': self.doi,
            'url': self.url,
            'abstract': self.abstract,
            'document_path': self.document_path,
            'citation_count': self.citation_count,
            'first_cited': self.first_cited.isoformat() if self.first_cited else None,
            'last_cited': self.last_cited.isoformat() if self.last_cited else None
        }


class CitationContext(BaseModel):
    """Context information for where a citation was used"""
    citation_key: str = Field(min_length=1, max_length=100)
    context_text: str = Field(description="Text where citation was used", max_length=5000)
    section: str | None = Field(default=None, description="Document section", max_length=100)
    page_number: int | None = Field(default=None, ge=1, le=10000)
    confidence: float = Field(default=1.0, description="Confidence in citation accuracy", ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('citation_key')
    def validate_citation_key(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Citation key contains invalid characters')
        return v
    
    @validator('context_text')
    def validate_context_text(cls, v):
        if not v.strip():
            raise ValueError('Context text cannot be empty')
        return v.strip()


class CitationUsage(BaseModel):
    """Track citation usage in generated content"""
    citation_key: str = Field(min_length=1, max_length=100)
    used_in_sections: list[str] = Field(default_factory=list)
    usage_contexts: list[CitationContext] = Field(default_factory=list)
    total_uses: int = Field(default=0, ge=0)
    
    @validator('citation_key')
    def validate_citation_key(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Citation key contains invalid characters')
        return v

    def add_usage(self, context: CitationContext):
        """Add a new usage context with validation"""
        # Validate context before adding
        if context.citation_key != self.citation_key:
            raise ValidationError(
                f"Context citation key '{context.citation_key}' does not match usage key '{self.citation_key}'",
                {"context_key": context.citation_key, "usage_key": self.citation_key}
            )
        
        self.usage_contexts.append(context)
        if context.section and context.section not in self.used_in_sections:
            self.used_in_sections.append(context.section)
        self.total_uses += 1
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of citation usage"""
        return {
            "citation_key": self.citation_key,
            "total_uses": self.total_uses,
            "sections_used": len(self.used_in_sections),
            "sections": self.used_in_sections,
            "average_confidence": sum(ctx.confidence for ctx in self.usage_contexts) / len(self.usage_contexts) if self.usage_contexts else 0.0,
            "first_use": min(ctx.timestamp for ctx in self.usage_contexts) if self.usage_contexts else None,
            "last_use": max(ctx.timestamp for ctx in self.usage_contexts) if self.usage_contexts else None
        }


class CitationTracker:
    """
    Central citation management system for GraphRAG MCP toolkit with comprehensive validation.
    
    Provides:
    - Citation key generation and management
    - Usage tracking throughout document generation
    - Bibliography formatting in multiple styles
    - Citation verification and validation
    - Data integrity checking and error handling
    """

    def __init__(self):
        self.citations: dict[str, Citation] = {}
        self.used_citations: set[str] = set()
        self.citation_usage: dict[str, CitationUsage] = {}
        self.bibliography_style: str = "APA"
        self._validation_enabled: bool = True
        self._integrity_errors: List[str] = []
        self._duplicate_keys: set[str] = set()
    
    def enable_validation(self, enabled: bool = True):
        """Enable or disable comprehensive validation"""
        self._validation_enabled = enabled
    
    def get_integrity_report(self) -> Dict[str, Any]:
        """Get comprehensive data integrity report"""
        report = {
            "total_citations": len(self.citations),
            "used_citations": len(self.used_citations),
            "unused_citations": len(self.citations) - len(self.used_citations),
            "validation_enabled": self._validation_enabled,
            "integrity_errors": self._integrity_errors.copy(),
            "duplicate_keys": list(self._duplicate_keys),
            "invalid_citations": []
        }
        
        # Check for invalid citations
        for citation in self.citations.values():
            if not citation.is_valid():
                report["invalid_citations"].append({
                    "key": citation.key,
                    "errors": citation.get_validation_errors()
                })
        
        # Check for orphaned usage records
        orphaned_usage = [key for key in self.citation_usage.keys() if key not in self.citations]
        if orphaned_usage:
            report["orphaned_usage_records"] = orphaned_usage
        
        # Check for inconsistent usage counts
        inconsistent_counts = []
        for key, citation in self.citations.items():
            if key in self.citation_usage:
                expected_count = self.citation_usage[key].total_uses
                if citation.citation_count != expected_count:
                    inconsistent_counts.append({
                        "key": key,
                        "citation_count": citation.citation_count,
                        "usage_count": expected_count
                    })
        if inconsistent_counts:
            report["inconsistent_counts"] = inconsistent_counts
        
        return report
    
    def repair_data_integrity(self) -> Dict[str, Any]:
        """Attempt to repair data integrity issues"""
        repair_report = {
            "repairs_made": [],
            "repairs_failed": [],
            "warnings": []
        }
        
        # Remove orphaned usage records
        orphaned_usage = [key for key in self.citation_usage.keys() if key not in self.citations]
        for key in orphaned_usage:
            del self.citation_usage[key]
            repair_report["repairs_made"].append(f"Removed orphaned usage record: {key}")
        
        # Fix inconsistent citation counts
        for key, citation in self.citations.items():
            if key in self.citation_usage:
                expected_count = self.citation_usage[key].total_uses
                if citation.citation_count != expected_count:
                    citation.citation_count = expected_count
                    repair_report["repairs_made"].append(f"Fixed citation count for {key}: {citation.citation_count}")
        
        # Update used_citations set
        self.used_citations = {key for key in self.citation_usage.keys() if key in self.citations}
        
        # Clear integrity errors after repair
        self._integrity_errors = []
        
        return repair_report
    
    def validate_citation_data(self, citation_key: str) -> bool:
        """Validate a specific citation's data"""
        if citation_key not in self.citations:
            return False
        
        citation = self.citations[citation_key]
        return citation.is_valid()
    
    def _validate_citation_key(self, citation_key: str) -> bool:
        """Validate citation key format and uniqueness"""
        if not citation_key or not isinstance(citation_key, str):
            return False
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', citation_key):
            return False
        
        if len(citation_key) > 100:
            return False
        
        return True

    def add_citation(self,
                    title: str,
                    authors: list[str] = None,
                    year: int = None,
                    **kwargs) -> str:
        """
        Add a new citation with comprehensive validation.
        
        Args:
            title: Paper title
            authors: List of author names
            year: Publication year
            **kwargs: Additional citation metadata
            
        Returns:
            Citation key for referencing
            
        Raises:
            ValidationError: If citation data is invalid
        """
        # Validate inputs
        if not title or not isinstance(title, str) or not title.strip():
            raise ValidationError("Citation title must be a non-empty string", {"title": title})
        
        title = title.strip()
        authors = authors or []
        
        # Validate authors
        if not isinstance(authors, list):
            raise ValidationError("Authors must be a list", {"authors": authors})
        
        for i, author in enumerate(authors):
            if not isinstance(author, str) or not author.strip():
                raise ValidationError(f"Author {i+1} must be a non-empty string", {"author": author})
        
        # Validate year
        if year is not None:
            if not isinstance(year, int) or year < 1000 or year > datetime.now().year + 1:
                raise ValidationError(f"Invalid year: {year}", {"year": year})
        
        # Generate citation key
        citation_key = self._generate_citation_key(title, authors, year)
        
        # Check for duplicate key
        if citation_key in self.citations:
            existing_citation = self.citations[citation_key]
            if existing_citation.title == title and existing_citation.authors == authors:
                # Exact duplicate - return existing key
                return citation_key
            else:
                # Key collision - generate unique key
                self._duplicate_keys.add(citation_key)
                citation_key = self._generate_unique_citation_key(title, authors, year)
        
        # Create citation object
        try:
            citation = Citation(
                key=citation_key,
                title=title,
                authors=authors,
                year=year,
                **kwargs
            )
        except Exception as e:
            raise ValidationError(f"Failed to create citation: {str(e)}", {"title": title, "authors": authors})
        
        # Validate citation if validation is enabled
        if self._validation_enabled and not citation.is_valid():
            errors = citation.get_validation_errors()
            raise ValidationError(f"Citation validation failed: {'; '.join(errors)}", {"errors": errors})
        
        # Store citation
        self.citations[citation_key] = citation
        
        return citation_key
    
    def _generate_unique_citation_key(self, title: str, authors: list[str], year: int = None) -> str:
        """Generate a unique citation key when there's a collision"""
        base_key = self._generate_citation_key(title, authors, year)
        counter = 1
        
        while f"{base_key}_{counter}" in self.citations:
            counter += 1
        
        return f"{base_key}_{counter}"

    def track_citation(self,
                      citation_key: str,
                      context_text: str = "",
                      section: str = None,
                      confidence: float = 1.0) -> bool:
        """
        Track usage of a citation in generated content with validation.
        
        Args:
            citation_key: The citation key being used
            context_text: Text context where citation appears
            section: Document section (e.g., "Introduction", "Methods")
            confidence: Confidence in citation accuracy (0.0-1.0)
            
        Returns:
            True if tracking successful, False if citation not found
            
        Raises:
            ValidationError: If input validation fails
        """
        # Validate inputs
        if not citation_key or not isinstance(citation_key, str):
            raise ValidationError("Citation key must be a non-empty string", {"citation_key": citation_key})
        
        if not self._validate_citation_key(citation_key):
            raise ValidationError(f"Invalid citation key format: {citation_key}", {"citation_key": citation_key})
        
        if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
            raise ValidationError(f"Confidence must be between 0.0 and 1.0, got {confidence}", {"confidence": confidence})
        
        # Check if citation exists
        if citation_key not in self.citations:
            self._integrity_errors.append(f"Attempted to track non-existent citation: {citation_key}")
            return False
        
        # Mark as used
        self.used_citations.add(citation_key)
        
        # Update citation usage count
        citation = self.citations[citation_key]
        citation.citation_count += 1
        citation.last_cited = datetime.now()
        
        # Track detailed usage
        if citation_key not in self.citation_usage:
            self.citation_usage[citation_key] = CitationUsage(citation_key=citation_key)
        
        try:
            context = CitationContext(
                citation_key=citation_key,
                context_text=context_text or "",
                section=section,
                confidence=confidence
            )
            
            self.citation_usage[citation_key].add_usage(context)
            
        except Exception as e:
            # Roll back citation count on error
            citation.citation_count -= 1
            raise ValidationError(f"Failed to track citation usage: {str(e)}", {"citation_key": citation_key})
        
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
        Generate formatted bibliography with validation.
        
        Args:
            style: Citation style ("APA", "IEEE", "Nature", "MLA")
            used_only: Only include citations that were actually used
            sort_by: Sort order ("author", "year", "title", "usage")
            
        Returns:
            List of formatted citation strings
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        valid_styles = ["APA", "IEEE", "Nature", "MLA"]
        if style not in valid_styles:
            raise ValidationError(
                f"Invalid citation style: {style}. Must be one of {valid_styles}",
                {"style": style, "valid_styles": valid_styles}
            )
        
        valid_sort_options = ["author", "year", "title", "usage"]
        if sort_by not in valid_sort_options:
            raise ValidationError(
                f"Invalid sort option: {sort_by}. Must be one of {valid_sort_options}",
                {"sort_by": sort_by, "valid_options": valid_sort_options}
            )
        
        # Select citations with validation
        if used_only:
            citations_to_format = self.get_used_citations()
        else:
            citations_to_format = list(self.citations.values())
        
        # Validate citations before formatting
        if self._validation_enabled:
            invalid_citations = []
            for citation in citations_to_format:
                if not citation.is_valid():
                    invalid_citations.append({
                        "key": citation.key,
                        "errors": citation.get_validation_errors()
                    })
            
            if invalid_citations:
                self._integrity_errors.extend([
                    f"Invalid citation in bibliography: {c['key']} - {'; '.join(c['errors'])}"
                    for c in invalid_citations
                ])
                
                if len(invalid_citations) > len(citations_to_format) * 0.5:  # More than 50% invalid
                    raise ValidationError(
                        f"Too many invalid citations in bibliography: {len(invalid_citations)}/{len(citations_to_format)}",
                        {"invalid_citations": invalid_citations}
                    )
        
        # Sort citations with error handling
        try:
            if sort_by == "author":
                citations_to_format.sort(key=lambda c: c.authors[0] if c.authors else c.title)
            elif sort_by == "year":
                citations_to_format.sort(key=lambda c: c.year or 0)
            elif sort_by == "title":
                citations_to_format.sort(key=lambda c: c.title)
            elif sort_by == "usage":
                citations_to_format.sort(key=lambda c: c.citation_count, reverse=True)
        except Exception as e:
            raise ValidationError(
                f"Failed to sort citations by {sort_by}: {str(e)}",
                {"sort_by": sort_by, "citation_count": len(citations_to_format)}
            )

        # Format citations with error handling
        formatted_citations = []
        formatting_errors = []
        
        for citation in citations_to_format:
            try:
                formatted = self._format_citation(citation, style)
                if formatted:
                    formatted_citations.append(formatted)
                else:
                    formatting_errors.append(f"Empty format result for citation: {citation.key}")
            except Exception as e:
                formatting_errors.append(f"Failed to format citation {citation.key}: {str(e)}")
        
        # Handle formatting errors
        if formatting_errors:
            self._integrity_errors.extend(formatting_errors)
            
            if len(formatting_errors) > len(citations_to_format) * 0.3:  # More than 30% failed
                raise ValidationError(
                    f"Too many formatting errors: {len(formatting_errors)}/{len(citations_to_format)}",
                    {"formatting_errors": formatting_errors}
                )

        return formatted_citations

    def generate_in_text_citation(self,
                                citation_key: str,
                                style: str = "APA",
                                page_number: str = None) -> str:
        """
        Generate in-text citation format with validation.
        
        Args:
            citation_key: Citation to reference
            style: Citation style
            page_number: Optional page number
            
        Returns:
            Formatted in-text citation
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        if not citation_key or not isinstance(citation_key, str):
            raise ValidationError(
                "Citation key must be a non-empty string",
                {"citation_key": citation_key}
            )
        
        if not self._validate_citation_key(citation_key):
            raise ValidationError(
                f"Invalid citation key format: {citation_key}",
                {"citation_key": citation_key}
            )
        
        valid_styles = ["APA", "IEEE", "Nature", "MLA"]
        if style not in valid_styles:
            raise ValidationError(
                f"Invalid citation style: {style}. Must be one of {valid_styles}",
                {"style": style, "valid_styles": valid_styles}
            )
        
        # Validate page number if provided
        if page_number is not None:
            if not isinstance(page_number, str) or not page_number.strip():
                raise ValidationError(
                    "Page number must be a non-empty string if provided",
                    {"page_number": page_number}
            )
            page_number = page_number.strip()
        
        # Check if citation exists
        if citation_key not in self.citations:
            self._integrity_errors.append(f"In-text citation requested for non-existent citation: {citation_key}")
            return f"[{citation_key}]"  # Fallback

        citation = self.citations[citation_key]
        
        # Validate citation if validation is enabled
        if self._validation_enabled and not citation.is_valid():
            errors = citation.get_validation_errors()
            self._integrity_errors.append(f"In-text citation for invalid citation {citation_key}: {'; '.join(errors)}")
        
        try:
            if style == "APA":
                author_part = self._get_author_year_apa(citation)
                if page_number:
                    return f"({author_part}, p. {page_number})"
                return f"({author_part})"

            elif style == "IEEE":
                # Find index in bibliography order
                try:
                    index = list(self.citations.keys()).index(citation_key) + 1
                    return f"[{index}]"
                except ValueError:
                    # Fallback if not found in order
                    return f"[{citation_key}]"

            elif style == "Nature":
                try:
                    index = list(self.citations.keys()).index(citation_key) + 1
                    return f"{index}"
                except ValueError:
                    return f"{citation_key}"

            elif style == "MLA":
                if citation.authors:
                    try:
                        author = citation.authors[0].split()[-1]  # Last name
                        if page_number:
                            return f"({author} {page_number})"
                        return f"({author})"
                    except (IndexError, AttributeError):
                        # Fallback if author parsing fails
                        return f"({citation_key})"
                else:
                    return f"({citation_key})"

            return f"({citation_key})"  # Final fallback
            
        except Exception as e:
            self._integrity_errors.append(f"Failed to generate in-text citation for {citation_key}: {str(e)}")
            return f"[{citation_key}]"  # Error fallback

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
        Export citations in various formats with validation.
        
        Args:
            format: Export format ("json", "bibtex", "csv")
            
        Returns:
            Formatted export string
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate format
        valid_formats = ["json", "bibtex", "csv"]
        if format not in valid_formats:
            raise ValidationError(
                f"Invalid export format: {format}. Must be one of {valid_formats}",
                {"format": format, "valid_formats": valid_formats}
            )
        
        # Check if we have citations to export
        if not self.citations:
            return "" if format != "json" else "{\"citations\": {}, \"usage\": {}, \"used_citations\": []}"
        
        try:
            if format == "json":
                # Validate citation data before export
                export_data = {
                    "citations": {},
                    "usage": {},
                    "used_citations": list(self.used_citations),
                    "export_metadata": {
                        "export_timestamp": datetime.now().isoformat(),
                        "total_citations": len(self.citations),
                        "validation_enabled": self._validation_enabled
                    }
                }
                
                for k, v in self.citations.items():
                    try:
                        export_data["citations"][k] = v.to_dict()
                    except Exception as e:
                        self._integrity_errors.append(f"Failed to export citation {k}: {str(e)}")
                        continue
                
                for k, v in self.citation_usage.items():
                    try:
                        export_data["usage"][k] = v.model_dump()
                    except Exception as e:
                        self._integrity_errors.append(f"Failed to export usage for {k}: {str(e)}")
                        continue
                
                return json.dumps(export_data, indent=2, default=str)

            elif format == "bibtex":
                bibtex_entries = []
                failed_exports = []
                
                for citation in self.citations.values():
                    try:
                        bibtex_entry = self._citation_to_bibtex(citation)
                        if bibtex_entry:
                            bibtex_entries.append(bibtex_entry)
                        else:
                            failed_exports.append(citation.key)
                    except Exception as e:
                        failed_exports.append(f"{citation.key}: {str(e)}")
                
                if failed_exports:
                    self._integrity_errors.extend([f"Failed to export to BibTeX: {f}" for f in failed_exports])
                
                return "\n\n".join(bibtex_entries)

            elif format == "csv":
                import csv
                import io

                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["Key", "Title", "Authors", "Year", "Journal", "Used", "Usage Count", "Valid"])

                failed_exports = []
                for citation in self.citations.values():
                    try:
                        writer.writerow([
                            citation.key,
                            citation.title,
                            "; ".join(citation.authors) if citation.authors else "",
                            citation.year or "",
                            citation.journal or "",
                            citation.key in self.used_citations,
                            citation.citation_count,
                            citation.is_valid() if self._validation_enabled else "Unknown"
                        ])
                    except Exception as e:
                        failed_exports.append(f"{citation.key}: {str(e)}")
                
                if failed_exports:
                    self._integrity_errors.extend([f"Failed to export to CSV: {f}" for f in failed_exports])

                return output.getvalue()

        except Exception as e:
            raise ValidationError(
                f"Export failed for format {format}: {str(e)}",
                {"format": format, "error": str(e)}
            )

        return ""

    def import_citations(self, data: str, format: str = "json") -> dict[str, Any]:
        """
        Import citations from external sources with comprehensive validation.
        
        Args:
            data: Citation data
            format: Data format ("json", "bibtex")
            
        Returns:
            Import results with statistics
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        if not data or not isinstance(data, str):
            raise ValidationError(
                "Import data must be a non-empty string",
                {"data_type": type(data).__name__, "data_length": len(data) if data else 0}
            )
        
        valid_formats = ["json", "bibtex"]
        if format not in valid_formats:
            raise ValidationError(
                f"Invalid import format: {format}. Must be one of {valid_formats}",
                {"format": format, "valid_formats": valid_formats}
            )
        
        import_stats = {
            "citations_imported": 0,
            "citations_failed": 0,
            "usage_imported": 0,
            "usage_failed": 0,
            "errors": [],
            "warnings": []
        }
        
        try:
            if format == "json":
                try:
                    parsed = json.loads(data)
                except json.JSONDecodeError as e:
                    raise ValidationError(
                        f"Invalid JSON format: {str(e)}",
                        {"json_error": str(e)}
                    )
                
                if not isinstance(parsed, dict):
                    raise ValidationError(
                        "JSON data must be a dictionary",
                        {"data_type": type(parsed).__name__}
                    )

                # Import citations with validation
                citations_data = parsed.get("citations", {})
                if not isinstance(citations_data, dict):
                    import_stats["warnings"].append("Citations data is not a dictionary, skipping")
                else:
                    for key, citation_data in citations_data.items():
                        try:
                            # Validate citation data structure
                            if not isinstance(citation_data, dict):
                                import_stats["errors"].append(f"Citation {key}: invalid data structure")
                                import_stats["citations_failed"] += 1
                                continue
                            
                            # Handle datetime fields
                            if "first_cited" in citation_data and citation_data["first_cited"]:
                                try:
                                    citation_data["first_cited"] = datetime.fromisoformat(citation_data["first_cited"])
                                except (ValueError, TypeError):
                                    citation_data["first_cited"] = None
                            
                            if "last_cited" in citation_data and citation_data["last_cited"]:
                                try:
                                    citation_data["last_cited"] = datetime.fromisoformat(citation_data["last_cited"])
                                except (ValueError, TypeError):
                                    citation_data["last_cited"] = None
                            
                            # Create citation object
                            citation = Citation(**citation_data)
                            
                            # Validate citation if validation is enabled
                            if self._validation_enabled and not citation.is_valid():
                                errors = citation.get_validation_errors()
                                import_stats["warnings"].append(f"Citation {key} has validation errors: {'; '.join(errors)}")
                            
                            # Check for duplicate keys
                            if key in self.citations:
                                import_stats["warnings"].append(f"Overwriting existing citation: {key}")
                            
                            self.citations[key] = citation
                            import_stats["citations_imported"] += 1
                            
                        except Exception as e:
                            import_stats["errors"].append(f"Citation {key}: {str(e)}")
                            import_stats["citations_failed"] += 1

                # Import usage data with validation
                usage_data = parsed.get("usage", {})
                if not isinstance(usage_data, dict):
                    import_stats["warnings"].append("Usage data is not a dictionary, skipping")
                else:
                    for key, usage_info in usage_data.items():
                        try:
                            # Validate usage data structure
                            if not isinstance(usage_info, dict):
                                import_stats["errors"].append(f"Usage {key}: invalid data structure")
                                import_stats["usage_failed"] += 1
                                continue
                            
                            # Handle datetime fields in usage contexts
                            if "usage_contexts" in usage_info:
                                for context in usage_info["usage_contexts"]:
                                    if "timestamp" in context and context["timestamp"]:
                                        try:
                                            context["timestamp"] = datetime.fromisoformat(context["timestamp"])
                                        except (ValueError, TypeError):
                                            context["timestamp"] = datetime.now()
                            
                            usage_obj = CitationUsage(**usage_info)
                            
                            # Validate that the citation exists
                            if key not in self.citations:
                                import_stats["warnings"].append(f"Usage record for non-existent citation: {key}")
                            
                            self.citation_usage[key] = usage_obj
                            import_stats["usage_imported"] += 1
                            
                        except Exception as e:
                            import_stats["errors"].append(f"Usage {key}: {str(e)}")
                            import_stats["usage_failed"] += 1

                # Import used citations set
                used_citations_data = parsed.get("used_citations", [])
                if isinstance(used_citations_data, list):
                    valid_used_citations = []
                    for citation_key in used_citations_data:
                        if citation_key in self.citations:
                            valid_used_citations.append(citation_key)
                        else:
                            import_stats["warnings"].append(f"Used citation reference to non-existent citation: {citation_key}")
                    
                    self.used_citations.update(valid_used_citations)
                else:
                    import_stats["warnings"].append("Used citations data is not a list, skipping")

            elif format == "bibtex":
                # BibTeX import would be implemented here
                # For now, just indicate it's not supported
                import_stats["errors"].append("BibTeX import not yet implemented")
                import_stats["citations_failed"] = 1
            
            # Final validation and cleanup
            if self._validation_enabled:
                repair_report = self.repair_data_integrity()
                import_stats["warnings"].extend(repair_report.get("warnings", []))
                import_stats["repairs_made"] = repair_report.get("repairs_made", [])
            
            return import_stats
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Import failed: {str(e)}",
                {"format": format, "error": str(e)}
            )

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
    
    def clear_all_data(self) -> dict[str, Any]:
        """Clear all citation data and return summary"""
        summary = {
            "citations_cleared": len(self.citations),
            "usage_records_cleared": len(self.citation_usage),
            "used_citations_cleared": len(self.used_citations),
            "errors_cleared": len(self._integrity_errors),
            "duplicate_keys_cleared": len(self._duplicate_keys)
        }
        
        # Clear all data
        self.citations.clear()
        self.used_citations.clear()
        self.citation_usage.clear()
        self._integrity_errors.clear()
        self._duplicate_keys.clear()
        
        return summary
    
    def get_health_check(self) -> dict[str, Any]:
        """Get comprehensive health check of citation system"""
        health_check = {
            "overall_health": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system_status": {
                "validation_enabled": self._validation_enabled,
                "total_citations": len(self.citations),
                "active_usage_tracking": len(self.citation_usage),
                "memory_usage_estimate_mb": self._estimate_memory_usage()
            },
            "issues": [],
            "recommendations": []
        }
        
        # Check for issues
        if self._integrity_errors:
            health_check["issues"].append(f"{len(self._integrity_errors)} integrity errors detected")
            health_check["overall_health"] = "warning"
        
        if self._duplicate_keys:
            health_check["issues"].append(f"{len(self._duplicate_keys)} duplicate keys detected")
            health_check["overall_health"] = "warning"
        
        # Check for invalid citations
        if self._validation_enabled:
            invalid_count = sum(1 for c in self.citations.values() if not c.is_valid())
            if invalid_count > 0:
                health_check["issues"].append(f"{invalid_count} invalid citations")
                health_check["overall_health"] = "error" if invalid_count > len(self.citations) * 0.5 else "warning"
        
        # Check for orphaned usage records
        orphaned = [key for key in self.citation_usage.keys() if key not in self.citations]
        if orphaned:
            health_check["issues"].append(f"{len(orphaned)} orphaned usage records")
            health_check["overall_health"] = "warning"
        
        # Add recommendations
        if health_check["overall_health"] != "healthy":
            health_check["recommendations"].append("Run repair_data_integrity() to fix issues")
        
        if not self._validation_enabled:
            health_check["recommendations"].append("Enable validation with enable_validation(True)")
        
        if len(self.citations) > 1000:
            health_check["recommendations"].append("Consider clearing unused citations to improve performance")
        
        return health_check
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        import sys
        
        total_size = 0
        
        # Estimate citation size
        for citation in self.citations.values():
            total_size += sys.getsizeof(citation.title or "")
            total_size += sum(sys.getsizeof(author) for author in citation.authors)
        
        # Estimate usage tracking size
        for usage in self.citation_usage.values():
            total_size += sum(sys.getsizeof(ctx.context_text) for ctx in usage.usage_contexts)
        
        return total_size / (1024 * 1024)  # Convert to MB

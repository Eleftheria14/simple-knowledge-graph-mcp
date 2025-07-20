"""Citation quality assessment and scoring utilities."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class CitationQualityReport:
    """Comprehensive citation quality assessment."""
    overall_score: float  # 0-100
    completeness_score: float  # 0-100
    credibility_score: float  # 0-100
    missing_fields: List[str]
    warnings: List[str]
    recommendations: List[str]
    citation_preview: Optional[str] = None

class CitationQualityScorer:
    """Assess and score citation quality for research integrity."""
    
    def __init__(self):
        self.quality_factors = {
            "has_doi": 25,
            "peer_reviewed_journal": 25, 
            "complete_author_list": 20,
            "publication_dates": 15,
            "funding_info": 10,
            "open_access_status": 5
        }
        
        self.required_fields = ["doi", "journal", "year", "authors_all"]
        self.recommended_fields = ["volume", "pages", "issue"]
        self.optional_fields = ["received_date", "accepted_date", "published_date", "funding", "open_access"]
        
        self.high_impact_journals = {
            "nature", "science", "cell", "nature chemistry", "nature physics",
            "journal of the american chemical society", "jacs", "angewandte chemie",
            "physical review letters", "prl", "ieee", "acm"
        }
    
    def assess_citation_quality(self, publication_entity: Dict[str, Any]) -> CitationQualityReport:
        """
        Comprehensive citation quality assessment.
        
        Args:
            publication_entity: Entity with type='publication' containing citation data
            
        Returns:
            CitationQualityReport with detailed assessment
        """
        properties = publication_entity.get("properties", {})
        
        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(properties)
        
        # Calculate credibility score
        credibility_score = self._calculate_credibility_score(properties)
        
        # Overall score (weighted average)
        overall_score = (completeness_score * 0.7) + (credibility_score * 0.3)
        
        # Identify issues
        missing_fields = self._find_missing_fields(properties)
        warnings = self._generate_warnings(properties)
        recommendations = self._generate_recommendations(properties, missing_fields)
        
        # Generate citation preview if possible
        citation_preview = self._generate_citation_preview(properties)
        
        return CitationQualityReport(
            overall_score=round(overall_score, 2),
            completeness_score=round(completeness_score, 2),
            credibility_score=round(credibility_score, 2),
            missing_fields=missing_fields,
            warnings=warnings,
            recommendations=recommendations,
            citation_preview=citation_preview
        )
    
    def _calculate_completeness_score(self, properties: Dict[str, Any]) -> float:
        """Calculate completeness score based on available metadata."""
        score = 0.0
        max_score = 100.0
        
        # Required fields (60% of score)
        required_weight = 60.0 / len(self.required_fields)
        for field in self.required_fields:
            if self._field_is_complete(properties, field):
                score += required_weight
        
        # Recommended fields (30% of score)
        recommended_weight = 30.0 / len(self.recommended_fields)
        for field in self.recommended_fields:
            if self._field_is_complete(properties, field):
                score += recommended_weight
        
        # Optional fields (10% of score)
        optional_weight = 10.0 / len(self.optional_fields)
        for field in self.optional_fields:
            if self._field_is_complete(properties, field):
                score += optional_weight
        
        return min(score, max_score)
    
    def _calculate_credibility_score(self, properties: Dict[str, Any]) -> float:
        """Calculate credibility score based on journal, DOI, peer review status."""
        score = 0.0
        
        # DOI presence (40% of credibility)
        if self._field_is_complete(properties, "doi"):
            doi = properties.get("doi", "").lower()
            if self._is_valid_doi(doi):
                score += 40.0
            else:
                score += 20.0  # Partial credit for having a DOI field
        
        # Journal credibility (40% of credibility)
        journal = properties.get("journal", "").lower()
        if journal:
            if any(high_journal in journal for high_journal in self.high_impact_journals):
                score += 40.0  # High-impact journal
            elif "ieee" in journal or "acm" in journal or "nature" in journal:
                score += 35.0  # Known reputable publisher
            elif any(keyword in journal for keyword in ["journal", "proceedings", "transactions"]):
                score += 25.0  # Academic publication format
            else:
                score += 15.0  # Has journal field
        
        # Author completeness (20% of credibility)
        authors = properties.get("authors_all", "")
        if authors:
            if ";" in authors or "," in authors:
                score += 20.0  # Multiple authors
            else:
                score += 10.0  # Single author (less common in academics)
        
        return min(score, 100.0)
    
    def _field_is_complete(self, properties: Dict[str, Any], field: str) -> bool:
        """Check if a field has meaningful content."""
        value = properties.get(field)
        if not value:
            return False
        
        if isinstance(value, str):
            return value.strip() not in ["", "NOT_FOUND", "UNKNOWN", "N/A"]
        
        return True
    
    def _is_valid_doi(self, doi: str) -> bool:
        """Basic DOI format validation."""
        # DOI pattern: 10.XXXX/XXXXX
        doi_pattern = r"^10\.\d{4,}/[^\s]+$"
        return bool(re.match(doi_pattern, doi))
    
    def _find_missing_fields(self, properties: Dict[str, Any]) -> List[str]:
        """Identify missing required and recommended fields."""
        missing = []
        
        for field in self.required_fields:
            if not self._field_is_complete(properties, field):
                missing.append(f"{field} (required)")
        
        for field in self.recommended_fields:
            if not self._field_is_complete(properties, field):
                missing.append(f"{field} (recommended)")
        
        return missing
    
    def _generate_warnings(self, properties: Dict[str, Any]) -> List[str]:
        """Generate specific warnings about citation quality."""
        warnings = []
        
        # DOI warnings
        doi = properties.get("doi", "")
        if not doi:
            warnings.append("Missing DOI - reduces citation credibility")
        elif not self._is_valid_doi(doi.lower()):
            warnings.append("DOI format appears invalid")
        
        # Author warnings
        authors = properties.get("authors_all", "")
        if not authors:
            warnings.append("Missing author information")
        elif ";" not in authors and "," not in authors:
            warnings.append("Appears to have only one author - verify completeness")
        
        # Journal warnings
        journal = properties.get("journal", "")
        if not journal:
            warnings.append("Missing journal information")
        elif len(journal) < 5:
            warnings.append("Journal name appears too short - verify completeness")
        
        # Year warnings
        year = properties.get("year")
        if not year:
            warnings.append("Missing publication year")
        elif isinstance(year, int) and (year < 1900 or year > 2030):
            warnings.append("Publication year appears unrealistic")
        
        return warnings
    
    def _generate_recommendations(self, properties: Dict[str, Any], missing_fields: List[str]) -> List[str]:
        """Generate actionable recommendations for improving citation quality."""
        recommendations = []
        
        if missing_fields:
            recommendations.append(f"Complete missing fields: {', '.join(missing_fields)}")
        
        if not self._field_is_complete(properties, "doi"):
            recommendations.append("Search for DOI on journal website or CrossRef")
        
        if not self._field_is_complete(properties, "funding"):
            recommendations.append("Check acknowledgments section for funding information")
        
        if not self._field_is_complete(properties, "pages"):
            recommendations.append("Include page numbers for complete citation")
        
        if properties.get("open_access") is None:
            recommendations.append("Determine open access status for better accessibility")
        
        return recommendations
    
    def _generate_citation_preview(self, properties: Dict[str, Any]) -> Optional[str]:
        """Generate a formatted citation preview."""
        try:
            authors = properties.get("authors_all", "Unknown Authors")
            year = properties.get("year", "Unknown Year")
            title = properties.get("title", "Unknown Title")
            journal = properties.get("journal", "Unknown Journal")
            volume = properties.get("volume", "")
            issue = properties.get("issue", "")
            pages = properties.get("pages", "")
            
            # Handle author formatting
            if ";" in authors:
                author_list = authors.split(";")
                if len(author_list) > 3:
                    formatted_authors = f"{author_list[0].strip()} et al."
                else:
                    formatted_authors = authors.replace(";", ",")
            else:
                formatted_authors = authors
            
            # Build citation
            citation = f"{formatted_authors} ({year}). {title}. {journal}"
            
            if volume:
                citation += f", {volume}"
                if issue:
                    citation += f"({issue})"
            
            if pages:
                citation += f", {pages}"
            
            citation += "."
            
            return citation
            
        except Exception:
            return None

def assess_knowledge_graph_citations(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Assess citation quality across all publication entities in a knowledge graph.
    
    Args:
        entities: List of entity dictionaries
        
    Returns:
        Comprehensive citation quality report
    """
    scorer = CitationQualityScorer()
    
    # Find all publication entities
    publications = [e for e in entities if e.get("type") == "publication"]
    
    if not publications:
        return {
            "error": "No publication entities found",
            "recommendation": "Create publication entities with complete citation data"
        }
    
    # Assess each publication
    assessments = []
    for pub in publications:
        assessment = scorer.assess_citation_quality(pub)
        assessments.append({
            "entity_id": pub.get("id"),
            "entity_name": pub.get("name"),
            "assessment": assessment
        })
    
    # Calculate overall statistics
    overall_scores = [a["assessment"].overall_score for a in assessments]
    avg_score = sum(overall_scores) / len(overall_scores)
    
    # Count quality levels
    excellent = sum(1 for score in overall_scores if score >= 90)
    good = sum(1 for score in overall_scores if 75 <= score < 90)
    fair = sum(1 for score in overall_scores if 60 <= score < 75)
    poor = sum(1 for score in overall_scores if score < 60)
    
    return {
        "total_publications": len(publications),
        "average_quality_score": round(avg_score, 2),
        "quality_distribution": {
            "excellent (90+)": excellent,
            "good (75-89)": good,
            "fair (60-74)": fair,
            "poor (<60)": poor
        },
        "individual_assessments": assessments,
        "overall_status": "excellent" if avg_score >= 90 else "good" if avg_score >= 75 else "needs_improvement"
    }
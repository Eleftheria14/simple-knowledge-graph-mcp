"""
Domain template system

Template-driven configuration for different professional domains.
Templates provide domain-smart interpretation and MCP tools while allowing
unconstrained entity discovery.

Templates:
- BaseTemplate: Abstract base class for all domain templates  
- AcademicTemplate: Literature review and research analysis (ready)
- LegalTemplate: Legal document analysis (planned)
- MedicalTemplate: Clinical guidelines and protocols (planned)

Key principle: Templates guide interpretation, not extraction constraints.
"""

from .base import BaseTemplate, TemplateConfig, EntityConfig, RelationshipConfig, MCPToolConfig, template_registry
from .academic import AcademicTemplate

__all__ = [
    # Base classes
    "BaseTemplate",
    "TemplateConfig", 
    "EntityConfig",
    "RelationshipConfig",
    "MCPToolConfig",
    "template_registry",
    
    # Domain templates
    "AcademicTemplate",
]
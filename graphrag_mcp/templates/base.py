"""
Base Template System for GraphRAG MCP Toolkit

Abstract base class and template system for creating domain-specific
GraphRAG configurations and MCP tool definitions.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import json

from pydantic import BaseModel, Field


class EntityConfig(BaseModel):
    """Configuration for entity extraction"""
    name: str = Field(description="Entity type name")
    description: str = Field(description="Entity description for LLM")
    max_entities: int = Field(default=10, description="Maximum entities to extract")
    examples: List[str] = Field(default_factory=list, description="Example entities")


class RelationshipConfig(BaseModel):
    """Configuration for relationship extraction"""
    name: str = Field(description="Relationship type name")
    description: str = Field(description="Relationship description")
    source_entities: List[str] = Field(description="Valid source entity types")
    target_entities: List[str] = Field(description="Valid target entity types")


class MCPToolConfig(BaseModel):
    """Configuration for MCP tool generation"""
    name: str = Field(description="Tool function name")
    description: str = Field(description="Tool description")
    parameters: Dict[str, Any] = Field(description="Tool parameter schema")
    implementation: str = Field(description="Implementation strategy")


class TemplateConfig(BaseModel):
    """Complete template configuration"""
    name: str = Field(description="Template name")
    description: str = Field(description="Template description")
    version: str = Field(default="1.0.0", description="Template version")
    domain: str = Field(description="Domain category")
    entities: List[EntityConfig] = Field(description="Entity configurations")
    relationships: List[RelationshipConfig] = Field(description="Relationship configurations")
    mcp_tools: List[MCPToolConfig] = Field(description="MCP tool configurations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseTemplate(ABC):
    """
    Abstract base class for all domain templates.
    
    Templates define domain-specific entity types, relationships,
    and MCP tool configurations for different professional fields.
    """
    
    def __init__(self):
        """Initialize base template"""
        self.config = self.get_template_config()
        self._validate_config()
    
    @abstractmethod
    def get_template_config(self) -> TemplateConfig:
        """
        Get the complete template configuration.
        
        Returns:
            Template configuration with entities, relationships, and tools
        """
        pass
    
    @abstractmethod
    def get_entity_schema(self) -> Dict[str, str]:
        """
        Get entity schema for document processing.
        
        Returns:
            Dict mapping entity types to descriptions
        """
        pass
    
    @abstractmethod
    def get_relationship_schema(self) -> List[Dict[str, Any]]:
        """
        Get relationship schema for knowledge graph construction.
        
        Returns:
            List of relationship configurations
        """
        pass
    
    @abstractmethod
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Get MCP tool definitions for this domain.
        
        Returns:
            List of MCP tool configurations
        """
        pass
    
    def get_processing_config(self) -> Dict[str, Any]:
        """
        Get domain-specific processing configuration.
        
        Returns:
            Processing configuration dictionary
        """
        return {
            "entity_schema": self.get_entity_schema(),
            "relationship_schema": self.get_relationship_schema(),
            "max_entities_per_type": max(e.max_entities for e in self.config.entities),
            "domain": self.config.domain,
            "template_name": self.config.name,
            "template_version": self.config.version
        }
    
    def generate_example_queries(self) -> List[str]:
        """
        Generate example queries for this domain.
        
        Returns:
            List of example natural language queries
        """
        # Default examples based on entity types
        entity_types = list(self.get_entity_schema().keys())
        
        examples = [
            "What are the main findings of this document?",
            "Provide a summary of the key concepts discussed.",
        ]
        
        # Add entity-specific examples
        if "authors" in entity_types:
            examples.append("Who are the authors and what are their contributions?")
        if "methods" in entity_types:
            examples.append("What methods were used in this work?")
        if "concepts" in entity_types:
            examples.append("What are the key concepts and theories?")
        
        return examples
    
    def validate_document(self, document_path: str) -> Dict[str, Any]:
        """
        Validate if document is suitable for this template.
        
        Args:
            document_path: Path to document file
            
        Returns:
            Validation result with score and recommendations
        """
        # Basic validation - can be overridden by subclasses
        path = Path(document_path)
        
        result = {
            "valid": True,
            "score": 0.8,  # Default score
            "messages": [],
            "recommendations": []
        }
        
        if not path.exists():
            result["valid"] = False
            result["score"] = 0.0
            result["messages"].append("File does not exist")
            return result
        
        if path.suffix.lower() != ".pdf":
            result["score"] *= 0.7
            result["messages"].append("Non-PDF files may have reduced accuracy")
        
        return result
    
    def export_config(self, output_path: Optional[str] = None) -> str:
        """
        Export template configuration to JSON file.
        
        Args:
            output_path: Optional output file path
            
        Returns:
            Path to exported configuration file
        """
        if output_path is None:
            output_path = f"{self.config.name.lower()}_template.json"
        
        config_dict = self.config.model_dump()
        
        with open(output_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        return output_path
    
    @classmethod
    def from_config_file(cls, config_path: str) -> 'BaseTemplate':
        """
        Create template instance from configuration file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            Template instance
        """
        with open(config_path) as f:
            config_dict = json.load(f)
        
        # This would need to be implemented by specific template classes
        raise NotImplementedError("Subclasses must implement from_config_file")
    
    def _validate_config(self):
        """Validate template configuration"""
        # Get entity names (including special "any" for unconstrained relationships)
        entity_names = {e.name for e in self.config.entities}
        entity_names.add("any")  # Allow "any" for unconstrained relationships
        
        # Check relationship consistency (only if not using "any")
        for rel in self.config.relationships:
            for source in rel.source_entities:
                if source != "any" and source not in entity_names:
                    raise ValueError(f"Relationship '{rel.name}' references unknown entity '{source}'")
            for target in rel.target_entities:
                if target != "any" and target not in entity_names:
                    raise ValueError(f"Relationship '{rel.name}' references unknown entity '{target}'")
        
        # Validate MCP tools have required fields
        for tool in self.config.mcp_tools:
            if not tool.name or not tool.description:
                raise ValueError(f"MCP tool missing required fields: {tool}")
    
    def __str__(self) -> str:
        """String representation of template"""
        return f"{self.config.name} Template (v{self.config.version}) - {self.config.domain}"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"BaseTemplate(name='{self.config.name}', "
                f"domain='{self.config.domain}', "
                f"entities={len(self.config.entities)}, "
                f"relationships={len(self.config.relationships)}, "
                f"tools={len(self.config.mcp_tools)})")


class TemplateRegistry:
    """
    Registry for managing available templates.
    """
    
    def __init__(self):
        """Initialize template registry"""
        self._templates: Dict[str, type] = {}
    
    def register(self, name: str, template_class: type):
        """
        Register a template class.
        
        Args:
            name: Template name
            template_class: Template class (subclass of BaseTemplate)
        """
        if not issubclass(template_class, BaseTemplate):
            raise ValueError(f"Template class must inherit from BaseTemplate")
        
        self._templates[name] = template_class
    
    def get_template(self, name: str) -> BaseTemplate:
        """
        Get template instance by name.
        
        Args:
            name: Template name
            
        Returns:
            Template instance
        """
        if name not in self._templates:
            raise ValueError(f"Template '{name}' not found. Available: {list(self._templates.keys())}")
        
        template_class = self._templates[name]
        return template_class()
    
    def list_templates(self) -> List[str]:
        """
        List available template names.
        
        Returns:
            List of template names
        """
        return list(self._templates.keys())
    
    def get_template_info(self, name: str) -> Dict[str, Any]:
        """
        Get template information.
        
        Args:
            name: Template name
            
        Returns:
            Template information dictionary
        """
        template = self.get_template(name)
        return {
            "name": template.config.name,
            "description": template.config.description,
            "domain": template.config.domain,
            "version": template.config.version,
            "entities": len(template.config.entities),
            "relationships": len(template.config.relationships),
            "mcp_tools": len(template.config.mcp_tools)
        }


# Global template registry
template_registry = TemplateRegistry()
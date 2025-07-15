"""
Base Template System for GraphRAG MCP Toolkit

Abstract base class and template system for creating domain-specific
GraphRAG configurations and MCP tool definitions.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class EntityConfig(BaseModel):
    """Configuration for entity extraction"""
    name: str = Field(description="Entity type name")
    description: str = Field(description="Entity description for LLM")
    max_entities: int = Field(default=10, description="Maximum entities to extract")
    examples: list[str] = Field(default_factory=list, description="Example entities")


class RelationshipConfig(BaseModel):
    """Configuration for relationship extraction"""
    name: str = Field(description="Relationship type name")
    description: str = Field(description="Relationship description")
    source_entities: list[str] = Field(description="Valid source entity types")
    target_entities: list[str] = Field(description="Valid target entity types")


class MCPToolConfig(BaseModel):
    """Configuration for MCP tool generation"""
    name: str = Field(description="Tool function name")
    description: str = Field(description="Tool description")
    parameters: dict[str, Any] = Field(description="Tool parameter schema")
    implementation: str = Field(description="Implementation strategy")
    category: str = Field(default="general", description="Tool category (chat, literature, core, utility)")
    priority: int = Field(default=1, description="Tool priority (1=highest, 5=lowest)")
    requirements: list[str] = Field(default_factory=list, description="Required components or dependencies")
    examples: list[dict[str, Any]] = Field(default_factory=list, description="Example usage scenarios")
    validation_rules: dict[str, Any] = Field(default_factory=dict, description="Parameter validation rules")
    performance_hints: dict[str, Any] = Field(default_factory=dict, description="Performance optimization hints")


class TemplateConfig(BaseModel):
    """Complete template configuration"""
    name: str = Field(description="Template name")
    description: str = Field(description="Template description")
    version: str = Field(default="1.0.0", description="Template version")
    domain: str = Field(description="Domain category")
    entities: list[EntityConfig] = Field(description="Entity configurations")
    relationships: list[RelationshipConfig] = Field(description="Relationship configurations")
    mcp_tools: list[MCPToolConfig] = Field(description="MCP tool configurations")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Enhanced template configuration
    supported_formats: list[str] = Field(default_factory=lambda: ["pdf"], description="Supported document formats")
    workflow_phases: list[str] = Field(default_factory=list, description="Processing workflow phases")
    validation_config: dict[str, Any] = Field(default_factory=dict, description="Document validation configuration")
    processing_config: dict[str, Any] = Field(default_factory=dict, description="Processing configuration")
    output_formats: list[str] = Field(default_factory=lambda: ["text"], description="Supported output formats")


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
    def get_entity_schema(self) -> dict[str, str]:
        """
        Get entity schema for document processing.
        
        Returns:
            Dict mapping entity types to descriptions
        """
        pass

    @abstractmethod
    def get_relationship_schema(self) -> list[dict[str, Any]]:
        """
        Get relationship schema for knowledge graph construction.
        
        Returns:
            List of relationship configurations
        """
        pass

    @abstractmethod
    def get_mcp_tools(self) -> list[dict[str, Any]]:
        """
        Get MCP tool definitions for this domain.
        
        Returns:
            List of MCP tool configurations
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "implementation": tool.implementation,
                "category": tool.category,
                "priority": tool.priority,
                "requirements": tool.requirements,
                "examples": tool.examples,
                "validation_rules": tool.validation_rules,
                "performance_hints": tool.performance_hints
            }
            for tool in self.config.mcp_tools
        ]

    def get_processing_config(self) -> dict[str, Any]:
        """
        Get domain-specific processing configuration.
        
        Returns:
            Processing configuration dictionary
        """
        base_config = {
            "entity_schema": self.get_entity_schema(),
            "relationship_schema": self.get_relationship_schema(),
            "max_entities_per_type": max(e.max_entities for e in self.config.entities) if self.config.entities else 10,
            "domain": self.config.domain,
            "template_name": self.config.name,
            "template_version": self.config.version,
            "supported_formats": self.config.supported_formats,
            "workflow_phases": self.config.workflow_phases,
            "output_formats": self.config.output_formats
        }
        
        # Merge with template-specific processing config
        base_config.update(self.config.processing_config)
        return base_config

    def generate_example_queries(self) -> list[str]:
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

    def validate_document(self, document_path: str) -> dict[str, Any]:
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

    def export_config(self, output_path: str | None = None) -> str:
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
            
            # Validate tool categories
            valid_categories = ["chat", "literature", "core", "utility", "general"]
            if tool.category not in valid_categories:
                raise ValueError(f"Invalid tool category '{tool.category}'. Must be one of: {valid_categories}")
            
            # Validate priority range
            if not (1 <= tool.priority <= 5):
                raise ValueError(f"Tool priority must be between 1 and 5, got {tool.priority}")
            
            # Validate parameter schema
            if not isinstance(tool.parameters, dict):
                raise ValueError(f"Tool parameters must be a dictionary, got {type(tool.parameters)}")

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
        self._templates: dict[str, type] = {}

    def register(self, name: str, template_class: type):
        """
        Register a template class.
        
        Args:
            name: Template name
            template_class: Template class (subclass of BaseTemplate)
        """
        if not issubclass(template_class, BaseTemplate):
            raise ValueError("Template class must inherit from BaseTemplate")

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

    def list_templates(self) -> list[str]:
        """
        List available template names.
        
        Returns:
            List of template names
        """
        return list(self._templates.keys())
    
    def get_templates_by_domain(self, domain: str) -> list[str]:
        """
        Get templates for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of template names for the domain
        """
        matching_templates = []
        for name in self._templates.keys():
            template = self.get_template(name)
            if template.config.domain == domain:
                matching_templates.append(name)
        return matching_templates
    
    def get_template_capabilities(self, name: str) -> dict[str, Any]:
        """
        Get detailed capabilities of a template.
        
        Args:
            name: Template name
            
        Returns:
            Template capabilities dictionary
        """
        template = self.get_template(name)
        
        # Analyze tool capabilities
        capabilities = {
            "conversational_tools": [],
            "literature_tools": [],
            "analytical_tools": [],
            "utility_tools": [],
            "total_tools": len(template.config.mcp_tools)
        }
        
        for tool in template.config.mcp_tools:
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "priority": tool.priority,
                "requirements": tool.requirements
            }
            
            if tool.category == "chat":
                capabilities["conversational_tools"].append(tool_info)
            elif tool.category == "literature":
                capabilities["literature_tools"].append(tool_info)
            elif tool.category == "core":
                capabilities["analytical_tools"].append(tool_info)
            else:
                capabilities["utility_tools"].append(tool_info)
        
        return capabilities
    
    def validate_template_configuration(self, name: str) -> dict[str, Any]:
        """
        Validate template configuration.
        
        Args:
            name: Template name
            
        Returns:
            Validation results
        """
        try:
            template = self.get_template(name)
            
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "info": {
                    "total_entities": len(template.config.entities),
                    "total_relationships": len(template.config.relationships),
                    "total_tools": len(template.config.mcp_tools)
                }
            }
            
            # Check for missing recommended tools
            tool_names = {tool.name for tool in template.config.mcp_tools}
            recommended_tools = ["ask_knowledge_graph", "search_documents", "get_facts_with_citations"]
            
            for recommended in recommended_tools:
                if recommended not in tool_names:
                    validation_results["warnings"].append(f"Missing recommended tool: {recommended}")
            
            # Check tool priority distribution
            priorities = [tool.priority for tool in template.config.mcp_tools]
            if priorities and max(priorities) == min(priorities):
                validation_results["warnings"].append("All tools have the same priority - consider varying priorities")
            
            return validation_results
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "info": {}
            }

    def get_template_info(self, name: str) -> dict[str, Any]:
        """
        Get template information.
        
        Args:
            name: Template name
            
        Returns:
            Template information dictionary
        """
        template = self.get_template(name)
        
        # Categorize tools by category
        tool_categories = {}
        for tool in template.config.mcp_tools:
            category = tool.category
            if category not in tool_categories:
                tool_categories[category] = []
            tool_categories[category].append({
                "name": tool.name,
                "description": tool.description,
                "priority": tool.priority,
                "requirements": tool.requirements
            })
        
        return {
            "name": template.config.name,
            "description": template.config.description,
            "domain": template.config.domain,
            "version": template.config.version,
            "entities": len(template.config.entities),
            "relationships": len(template.config.relationships),
            "mcp_tools": len(template.config.mcp_tools),
            "tool_categories": tool_categories,
            "supported_formats": template.config.supported_formats,
            "workflow_phases": template.config.workflow_phases,
            "output_formats": template.config.output_formats,
            "metadata": template.config.metadata
        }


# Enhanced template utility functions
def create_tool_config(name: str, description: str, parameters: dict[str, Any], 
                       category: str = "general", priority: int = 1, 
                       implementation: str = "default", **kwargs) -> MCPToolConfig:
    """
    Create a standardized MCP tool configuration.
    
    Args:
        name: Tool name
        description: Tool description
        parameters: Tool parameters
        category: Tool category
        priority: Tool priority
        implementation: Implementation strategy
        **kwargs: Additional configuration options
        
    Returns:
        MCPToolConfig instance
    """
    return MCPToolConfig(
        name=name,
        description=description,
        parameters=parameters,
        category=category,
        priority=priority,
        implementation=implementation,
        requirements=kwargs.get("requirements", []),
        examples=kwargs.get("examples", []),
        validation_rules=kwargs.get("validation_rules", {}),
        performance_hints=kwargs.get("performance_hints", {})
    )

def create_entity_config(name: str, description: str, max_entities: int = 10, 
                        examples: list[str] = None) -> EntityConfig:
    """
    Create a standardized entity configuration.
    
    Args:
        name: Entity name
        description: Entity description
        max_entities: Maximum entities to extract
        examples: Example entities
        
    Returns:
        EntityConfig instance
    """
    return EntityConfig(
        name=name,
        description=description,
        max_entities=max_entities,
        examples=examples or []
    )

def create_relationship_config(name: str, description: str, 
                             source_entities: list[str] = None,
                             target_entities: list[str] = None) -> RelationshipConfig:
    """
    Create a standardized relationship configuration.
    
    Args:
        name: Relationship name
        description: Relationship description
        source_entities: Valid source entity types
        target_entities: Valid target entity types
        
    Returns:
        RelationshipConfig instance
    """
    return RelationshipConfig(
        name=name,
        description=description,
        source_entities=source_entities or ["any"],
        target_entities=target_entities or ["any"]
    )

# Global template registry
template_registry = TemplateRegistry()

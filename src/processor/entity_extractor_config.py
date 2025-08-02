"""
Configuration system for the Entity Extractor Agent
Allows customization of entity extraction prompts, models, and extraction parameters
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import yaml
import json
from enum import Enum

class EntityType(Enum):
    """Supported entity types for extraction"""
    PERSON = "person"
    ORGANIZATION = "organization"
    CONCEPT = "concept"
    TECHNOLOGY = "technology"
    PUBLICATION = "publication"
    LOCATION = "location"
    EVENT = "event"
    DATE = "date"
    METRIC = "metric"
    METHODOLOGY = "methodology"

class RelationshipType(Enum):
    """Supported relationship types"""
    AUTHORED = "AUTHORED"
    WORKS_AT = "WORKS_AT"
    USES = "USES"
    CITES = "CITES"
    RELATED_TO = "RELATED_TO"
    DEVELOPED = "DEVELOPED"
    APPLIED = "APPLIED"
    LOCATED_AT = "LOCATED_AT"
    PARTICIPATED_IN = "PARTICIPATED_IN"
    MEASURED = "MEASURED"
    BASED_ON = "BASED_ON"

class ExtractionMode(Enum):
    """Entity extraction modes"""
    COMPREHENSIVE = "comprehensive"  # Extract all possible entities
    FOCUSED = "focused"             # Extract only high-confidence entities  
    ACADEMIC = "academic"           # Focus on academic/research entities
    BUSINESS = "business"           # Focus on business/organizational entities
    TECHNICAL = "technical"         # Focus on technical/technology entities
    CUSTOM = "custom"              # User-defined extraction criteria

@dataclass
class EntityTypeConfig:
    """Configuration for specific entity types"""
    enabled: bool = True
    confidence_threshold: float = 0.7
    max_entities: Optional[int] = None
    required_properties: List[str] = field(default_factory=list)
    example_entities: List[str] = field(default_factory=list)
    extraction_hints: List[str] = field(default_factory=list)

@dataclass
class PromptTemplate:
    """Configurable prompt templates for entity extraction"""
    system_prompt: str = ""
    instruction_template: str = ""
    entity_guidelines: Dict[str, str] = field(default_factory=dict)
    relationship_guidelines: Dict[str, str] = field(default_factory=dict)
    output_format_example: str = ""
    context_instructions: List[str] = field(default_factory=list)

@dataclass 
class EntityExtractorConfig:
    """Main configuration for the Entity Extractor Agent"""
    
    # Model settings
    model_name: str = "llama-3.1-8b-instant"
    temperature: float = 0.1
    max_tokens: Optional[int] = 4096
    timeout_seconds: int = 60
    
    # Extraction settings
    extraction_mode: ExtractionMode = ExtractionMode.COMPREHENSIVE
    global_confidence_threshold: float = 0.7
    max_content_length: int = 4000
    enable_fallback_extraction: bool = True
    
    # Entity type configuration
    enabled_entity_types: Set[EntityType] = field(default_factory=lambda: {
        EntityType.PERSON, EntityType.ORGANIZATION, EntityType.CONCEPT, 
        EntityType.TECHNOLOGY, EntityType.PUBLICATION
    })
    entity_type_configs: Dict[EntityType, EntityTypeConfig] = field(default_factory=dict)
    
    # Relationship configuration
    enabled_relationship_types: Set[RelationshipType] = field(default_factory=lambda: {
        RelationshipType.AUTHORED, RelationshipType.WORKS_AT, RelationshipType.USES,
        RelationshipType.CITES, RelationshipType.RELATED_TO, RelationshipType.DEVELOPED
    })
    max_relationships_per_entity: int = 10
    relationship_confidence_threshold: float = 0.6
    
    # Prompt configuration
    prompt_template: PromptTemplate = field(default_factory=PromptTemplate)
    custom_instructions: List[str] = field(default_factory=list)
    domain_context: str = ""
    
    # Output configuration
    include_metadata: bool = True
    include_confidence_scores: bool = True
    include_extraction_reasoning: bool = False
    validate_json_output: bool = True
    
    # Performance settings
    retry_on_json_error: bool = True
    max_retry_attempts: int = 2
    enable_caching: bool = False
    
    def __post_init__(self):
        """Initialize default configurations"""
        if not self.entity_type_configs:
            self._init_default_entity_configs()
        
        if not self.prompt_template.instruction_template:
            self._init_default_prompt_template()
    
    def _init_default_entity_configs(self):
        """Initialize default entity type configurations"""
        self.entity_type_configs = {
            EntityType.PERSON: EntityTypeConfig(
                enabled=True,
                confidence_threshold=0.8,
                required_properties=["affiliation"],
                example_entities=["John Smith", "Dr. Jane Doe", "Prof. Alan Turing"],
                extraction_hints=["Look for author names, researchers, historical figures"]
            ),
            EntityType.ORGANIZATION: EntityTypeConfig(
                enabled=True,
                confidence_threshold=0.7,
                required_properties=["type"],
                example_entities=["Google Research", "MIT", "IEEE", "Microsoft"],
                extraction_hints=["Universities, companies, research institutions, journals"]
            ),
            EntityType.CONCEPT: EntityTypeConfig(
                enabled=True,
                confidence_threshold=0.7,
                max_entities=20,
                example_entities=["machine learning", "neural networks", "algorithm"],
                extraction_hints=["Technical terms, theories, methodologies, key ideas"]
            ),
            EntityType.TECHNOLOGY: EntityTypeConfig(
                enabled=True,
                confidence_threshold=0.8,
                example_entities=["TensorFlow", "Python", "GPU", "Transformer"],
                extraction_hints=["Tools, frameworks, programming languages, hardware"]
            ),
            EntityType.PUBLICATION: EntityTypeConfig(
                enabled=True,
                confidence_threshold=0.8,
                required_properties=["year", "type"],
                example_entities=["Nature", "NIPS 2017", "Attention Is All You Need"],
                extraction_hints=["Papers, books, journals, conferences, citations"]
            )
        }
    
    def _init_default_prompt_template(self):
        """Initialize default prompt template"""
        entity_types_str = ", ".join([et.value for et in self.enabled_entity_types])
        relationship_types_str = ", ".join([rt.value for rt in self.enabled_relationship_types])
        
        self.prompt_template = PromptTemplate(
            system_prompt=f"""You are an expert entity extraction agent specialized in analyzing document content.
Your task is to identify and extract structured knowledge from text with high accuracy.

Extraction Mode: {self.extraction_mode.value}
Domain Context: {self.domain_context or 'General document analysis'}

Focus on precision and relevance. Only extract entities you are confident about.""",
            
            instruction_template=f"""Analyze the following document content and extract entities and relationships.

TARGET ENTITY TYPES: {entity_types_str}
TARGET RELATIONSHIP TYPES: {relationship_types_str}

EXTRACTION GUIDELINES:
{{entity_guidelines}}

RELATIONSHIP GUIDELINES:  
{{relationship_guidelines}}

QUALITY REQUIREMENTS:
- Only extract entities with confidence >= {self.global_confidence_threshold}
- Provide clear, standardized entity names
- Include relevant properties for context
- Ensure relationships are meaningful and accurate

{{context_instructions}}

IMPORTANT: Return ONLY valid JSON format with no additional text, explanations, or markdown formatting. Do not use backticks or code blocks. Start directly with {{ and end with }}.
{{
  "entities": [
    {{
      "id": "unique_entity_id",
      "name": "Standardized Entity Name", 
      "type": "entity_type",
      "properties": {{"key": "value"}},
      "confidence": 0.0-1.0
    }}
  ],
  "relationships": [
    {{
      "source": "source_entity_id",
      "target": "target_entity_id", 
      "type": "RELATIONSHIP_TYPE",
      "context": "Brief explanation of relationship",
      "confidence": 0.0-1.0
    }}
  ],
  "metadata": {{
    "total_entities": 0,
    "total_relationships": 0,
    "extraction_mode": "{self.extraction_mode.value}",
    "confidence_threshold": {self.global_confidence_threshold}
  }}
}}

Document content:
{{content}}""",
            
            entity_guidelines={
                EntityType.PERSON.value: "Extract authors, researchers, historical figures. Include affiliation when available.",
                EntityType.ORGANIZATION.value: "Extract companies, universities, institutions. Specify organization type.",
                EntityType.CONCEPT.value: "Extract key technical terms, theories, methodologies. Focus on domain-specific concepts.",
                EntityType.TECHNOLOGY.value: "Extract tools, frameworks, systems, algorithms. Include version info when relevant.",
                EntityType.PUBLICATION.value: "Extract papers, books, journals. Include publication year and venue when available."
            },
            
            relationship_guidelines={
                RelationshipType.AUTHORED.value: "Person -> Publication (authored/wrote)",
                RelationshipType.WORKS_AT.value: "Person -> Organization (employment/affiliation)",
                RelationshipType.USES.value: "Entity -> Technology (utilizes/implements)",
                RelationshipType.CITES.value: "Publication -> Publication (references/cites)",
                RelationshipType.RELATED_TO.value: "General conceptual relationship",
                RelationshipType.DEVELOPED.value: "Person/Organization -> Technology (created/built)"
            },
            
            context_instructions=[
                "Focus on entities that are central to the document's main topic",
                "Prioritize entities that appear multiple times or in important sections",
                "Extract relationships that provide meaningful connections between entities"
            ]
        )
    
    def get_enabled_entity_types(self) -> List[EntityType]:
        """Get list of enabled entity types"""
        return [et for et in self.enabled_entity_types 
                if self.entity_type_configs.get(et, EntityTypeConfig()).enabled]
    
    def get_entity_config(self, entity_type: EntityType) -> EntityTypeConfig:
        """Get configuration for specific entity type"""
        return self.entity_type_configs.get(entity_type, EntityTypeConfig())
    
    def build_extraction_prompt(self, content: str) -> str:
        """Build complete extraction prompt with current configuration"""
        # Format entity guidelines
        enabled_types = self.get_enabled_entity_types()
        entity_guidelines = "\n".join([
            f"- {et.value.upper()}: {self.prompt_template.entity_guidelines.get(et.value, 'Extract relevant entities')}"
            for et in enabled_types
        ])
        
        # Format relationship guidelines  
        relationship_guidelines = "\n".join([
            f"- {rt.value}: {self.prompt_template.relationship_guidelines.get(rt.value, 'General relationship')}"
            for rt in self.enabled_relationship_types
        ])
        
        # Format context instructions
        context_instructions = ""
        if self.prompt_template.context_instructions or self.custom_instructions:
            all_instructions = self.prompt_template.context_instructions + self.custom_instructions
            context_instructions = "ADDITIONAL INSTRUCTIONS:\n" + "\n".join([f"- {inst}" for inst in all_instructions])
        
        # Build complete prompt
        prompt = self.prompt_template.instruction_template.format(
            entity_guidelines=entity_guidelines,
            relationship_guidelines=relationship_guidelines,
            context_instructions=context_instructions,
            content=content[:self.max_content_length]
        )
        
        return prompt
    
    def save_to_file(self, file_path: str):
        """Save configuration to YAML file"""
        config_dict = {
            "model_settings": {
                "model_name": self.model_name,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "timeout_seconds": self.timeout_seconds
            },
            "extraction_settings": {
                "extraction_mode": self.extraction_mode.value,
                "global_confidence_threshold": self.global_confidence_threshold,
                "max_content_length": self.max_content_length,
                "enable_fallback_extraction": self.enable_fallback_extraction
            },
            "entity_types": {
                "enabled_types": [et.value for et in self.enabled_entity_types],
                "type_configs": {
                    et.value: {
                        "enabled": config.enabled,
                        "confidence_threshold": config.confidence_threshold,
                        "max_entities": config.max_entities,
                        "required_properties": config.required_properties,
                        "example_entities": config.example_entities,
                        "extraction_hints": config.extraction_hints
                    }
                    for et, config in self.entity_type_configs.items()
                }
            },
            "relationships": {
                "enabled_types": [rt.value for rt in self.enabled_relationship_types],
                "max_per_entity": self.max_relationships_per_entity,
                "confidence_threshold": self.relationship_confidence_threshold
            },
            "prompts": {
                "system_prompt": self.prompt_template.system_prompt,
                "instruction_template": self.prompt_template.instruction_template,
                "entity_guidelines": self.prompt_template.entity_guidelines,
                "relationship_guidelines": self.prompt_template.relationship_guidelines,
                "context_instructions": self.prompt_template.context_instructions,
                "custom_instructions": self.custom_instructions,
                "domain_context": self.domain_context
            },
            "output": {
                "include_metadata": self.include_metadata,
                "include_confidence_scores": self.include_confidence_scores,
                "include_extraction_reasoning": self.include_extraction_reasoning,
                "validate_json_output": self.validate_json_output
            },
            "performance": {
                "retry_on_json_error": self.retry_on_json_error,
                "max_retry_attempts": self.max_retry_attempts,
                "enable_caching": self.enable_caching
            }
        }
        
        with open(file_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'EntityExtractorConfig':
        """Load configuration from YAML file"""
        with open(file_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        config = cls()
        
        # Load model settings
        if 'model_settings' in config_dict:
            model = config_dict['model_settings']
            config.model_name = model.get('model_name', config.model_name)
            config.temperature = model.get('temperature', config.temperature)
            config.max_tokens = model.get('max_tokens', config.max_tokens)
            config.timeout_seconds = model.get('timeout_seconds', config.timeout_seconds)
        
        # Load extraction settings
        if 'extraction_settings' in config_dict:
            extraction = config_dict['extraction_settings']
            config.extraction_mode = ExtractionMode(extraction.get('extraction_mode', 'comprehensive'))
            config.global_confidence_threshold = extraction.get('global_confidence_threshold', config.global_confidence_threshold)
            config.max_content_length = extraction.get('max_content_length', config.max_content_length)
            config.enable_fallback_extraction = extraction.get('enable_fallback_extraction', config.enable_fallback_extraction)
        
        # Load entity types
        if 'entity_types' in config_dict:
            entity_types = config_dict['entity_types']
            config.enabled_entity_types = {EntityType(et) for et in entity_types.get('enabled_types', [])}
            
            if 'type_configs' in entity_types:
                for et_name, et_config in entity_types['type_configs'].items():
                    entity_type = EntityType(et_name)
                    config.entity_type_configs[entity_type] = EntityTypeConfig(
                        enabled=et_config.get('enabled', True),
                        confidence_threshold=et_config.get('confidence_threshold', 0.7),
                        max_entities=et_config.get('max_entities'),
                        required_properties=et_config.get('required_properties', []),
                        example_entities=et_config.get('example_entities', []),
                        extraction_hints=et_config.get('extraction_hints', [])
                    )
        
        # Load relationships
        if 'relationships' in config_dict:
            relationships = config_dict['relationships']
            config.enabled_relationship_types = {RelationshipType(rt) for rt in relationships.get('enabled_types', [])}
            config.max_relationships_per_entity = relationships.get('max_per_entity', config.max_relationships_per_entity)
            config.relationship_confidence_threshold = relationships.get('confidence_threshold', config.relationship_confidence_threshold)
        
        # Load prompts
        if 'prompts' in config_dict:
            prompts = config_dict['prompts']
            config.prompt_template.system_prompt = prompts.get('system_prompt', '')
            config.prompt_template.instruction_template = prompts.get('instruction_template', '')
            config.prompt_template.entity_guidelines = prompts.get('entity_guidelines', {})
            config.prompt_template.relationship_guidelines = prompts.get('relationship_guidelines', {})
            config.prompt_template.context_instructions = prompts.get('context_instructions', [])
            config.custom_instructions = prompts.get('custom_instructions', [])
            config.domain_context = prompts.get('domain_context', '')
        
        # Load output settings
        if 'output' in config_dict:
            output = config_dict['output']
            config.include_metadata = output.get('include_metadata', config.include_metadata)
            config.include_confidence_scores = output.get('include_confidence_scores', config.include_confidence_scores)
            config.include_extraction_reasoning = output.get('include_extraction_reasoning', config.include_extraction_reasoning)
            config.validate_json_output = output.get('validate_json_output', config.validate_json_output)
        
        # Load performance settings
        if 'performance' in config_dict:
            perf = config_dict['performance']
            config.retry_on_json_error = perf.get('retry_on_json_error', config.retry_on_json_error)
            config.max_retry_attempts = perf.get('max_retry_attempts', config.max_retry_attempts)
            config.enable_caching = perf.get('enable_caching', config.enable_caching)
        
        return config

def create_default_config() -> EntityExtractorConfig:
    """Create default entity extractor configuration"""
    return EntityExtractorConfig()

def create_academic_config() -> EntityExtractorConfig:
    """Create configuration optimized for academic/research papers"""
    config = EntityExtractorConfig()
    config.extraction_mode = ExtractionMode.ACADEMIC
    config.domain_context = "Academic research paper analysis"
    config.global_confidence_threshold = 0.8
    config.temperature = 0.05  # Lower temperature for more precise extraction
    
    # Focus on academic entities
    config.enabled_entity_types = {
        EntityType.PERSON, EntityType.ORGANIZATION, EntityType.CONCEPT,
        EntityType.PUBLICATION, EntityType.METHODOLOGY
    }
    
    # Academic-specific relationships
    config.enabled_relationship_types = {
        RelationshipType.AUTHORED, RelationshipType.WORKS_AT, RelationshipType.CITES,
        RelationshipType.BASED_ON, RelationshipType.APPLIED
    }
    
    # Academic-specific instructions
    config.custom_instructions = [
        "Prioritize author names and institutional affiliations",
        "Extract research methodologies and experimental approaches", 
        "Identify key contributions and novel concepts",
        "Map citation relationships between publications",
        "Focus on technical terminology and domain concepts"
    ]
    
    return config

def create_business_config() -> EntityExtractorConfig:
    """Create configuration optimized for business documents"""
    config = EntityExtractorConfig()
    config.extraction_mode = ExtractionMode.BUSINESS
    config.domain_context = "Business and organizational document analysis"
    
    # Business-focused entities
    config.enabled_entity_types = {
        EntityType.PERSON, EntityType.ORGANIZATION, EntityType.TECHNOLOGY,
        EntityType.EVENT, EntityType.METRIC, EntityType.LOCATION
    }
    
    # Business relationships
    config.enabled_relationship_types = {
        RelationshipType.WORKS_AT, RelationshipType.USES, RelationshipType.DEVELOPED,
        RelationshipType.PARTICIPATED_IN, RelationshipType.LOCATED_AT
    }
    
    return config

def create_fast_config() -> EntityExtractorConfig:
    """Create configuration for fast, lightweight extraction"""
    config = EntityExtractorConfig()
    config.extraction_mode = ExtractionMode.FOCUSED
    config.global_confidence_threshold = 0.8  # Higher threshold for fewer, higher-quality entities
    config.max_content_length = 2000  # Shorter content analysis
    config.temperature = 0.2
    config.max_tokens = 2048
    
    # Minimal entity types
    config.enabled_entity_types = {
        EntityType.PERSON, EntityType.ORGANIZATION, EntityType.CONCEPT
    }
    
    # Simple relationships
    config.enabled_relationship_types = {
        RelationshipType.WORKS_AT, RelationshipType.RELATED_TO
    }
    
    return config
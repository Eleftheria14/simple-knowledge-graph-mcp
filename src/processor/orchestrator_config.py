"""
Configuration system for the DocumentOrchestrator agent
Allows customization of agent prompts, workflows, and tool selection
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
import json
from enum import Enum

class WorkflowType(Enum):
    """Predefined workflow types"""
    RESEARCH_PAPER = "research_paper"
    GENERAL_DOCUMENT = "general_document"
    TECHNICAL_MANUAL = "technical_manual"
    LEGAL_DOCUMENT = "legal_document"
    CUSTOM = "custom"

class ProcessingMode(Enum):
    """Processing modes for different use cases"""
    THOROUGH = "thorough"  # Complete analysis with all tools
    FAST = "fast"         # Quick processing, minimal tools
    SELECTIVE = "selective"  # User-specified tool subset
    ADAPTIVE = "adaptive"   # Agent decides based on content

@dataclass
class PromptTemplate:
    """Template for agent prompts"""
    system_prompt: str = ""
    instruction_template: str = ""
    response_format: str = ""
    examples: List[str] = field(default_factory=list)

@dataclass
class ToolConfig:
    """Configuration for individual tools"""
    name: str
    enabled: bool = True
    priority: int = 1  # 1=high, 2=medium, 3=low
    required: bool = False
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowConfig:
    """Configuration for specific workflow types"""
    name: str
    description: str
    tool_sequence: List[str] = field(default_factory=list)
    parallel_tools: List[List[str]] = field(default_factory=list)
    prompt_template: PromptTemplate = field(default_factory=PromptTemplate)
    success_criteria: List[str] = field(default_factory=list)

@dataclass
class OrchestratorConfig:
    """Main orchestrator configuration"""
    
    # Agent settings
    model_name: str = "llama-3.1-8b-instant"
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    processing_mode: ProcessingMode = ProcessingMode.THOROUGH
    
    # Tool configuration
    enabled_tools: List[str] = field(default_factory=list)
    tool_configs: Dict[str, ToolConfig] = field(default_factory=dict)
    
    # Workflow configuration
    default_workflow: WorkflowType = WorkflowType.GENERAL_DOCUMENT
    workflows: Dict[str, WorkflowConfig] = field(default_factory=dict)
    
    # Prompt configuration
    system_prompt: str = "You are an intelligent document processing assistant."
    custom_instructions: str = ""
    response_format: str = "structured_summary"
    
    # Processing settings
    timeout_seconds: int = 300
    retry_attempts: int = 2
    parallel_processing: bool = False
    
    # Output settings
    include_intermediate_results: bool = True
    detailed_logging: bool = False
    save_processing_trace: bool = False
    
    def __post_init__(self):
        """Initialize default configurations"""
        if not self.enabled_tools:
            self.enabled_tools = ["llamaparse_pdf", "extract_and_store_entities"]
        
        if not self.tool_configs:
            self._init_default_tool_configs()
        
        if not self.workflows:
            self._init_default_workflows()
    
    def _init_default_tool_configs(self):
        """Initialize default tool configurations"""
        self.tool_configs = {
            "llamaparse_pdf": ToolConfig(
                name="llamaparse_pdf",
                enabled=True,
                priority=1,
                required=True,
                parameters={"parsing_instruction": "Extract all text and structure"}
            ),
            "extract_and_store_entities": ToolConfig(
                name="extract_and_store_entities",
                enabled=True,
                priority=1,
                required=False,
                parameters={"confidence_threshold": 0.7}
            ),
            "store_vectors": ToolConfig(
                name="store_vectors",
                enabled=True,
                priority=2,
                required=False,
                parameters={"chunk_size": 500, "overlap": 50}
            ),
            "query_knowledge_graph": ToolConfig(
                name="query_knowledge_graph",
                enabled=False,
                priority=3,
                required=False
            )
        }
    
    def _init_default_workflows(self):
        """Initialize default workflow configurations"""
        self.workflows = {
            WorkflowType.RESEARCH_PAPER.value: WorkflowConfig(
                name="Research Paper Processing",
                description="Comprehensive analysis for academic papers",
                tool_sequence=["llamaparse_pdf", "extract_and_store_entities", "store_vectors"],
                prompt_template=PromptTemplate(
                    system_prompt="You are processing an academic research paper. Focus on extracting key concepts, methodologies, results, and citations.",
                    instruction_template="""
                    Process the research paper at: {file_path}
                    
                    1. Extract and structure the content using llamaparse_pdf
                    2. Identify and extract:
                       - Key concepts and terminology
                       - Research methodologies
                       - Results and findings
                       - Author citations and references
                       - Relationships between concepts
                    3. Store entities and relationships in the knowledge graph
                    4. Create searchable text chunks for future reference
                    
                    Focus on academic rigor and comprehensive knowledge extraction.
                    """,
                    response_format="academic_summary"
                ),
                success_criteria=["PDF parsed", "Entities extracted", "Knowledge graph updated"]
            ),
            
            WorkflowType.GENERAL_DOCUMENT.value: WorkflowConfig(
                name="General Document Processing",
                description="Standard processing for typical documents",
                tool_sequence=["llamaparse_pdf", "extract_and_store_entities"],
                prompt_template=PromptTemplate(
                    system_prompt="You are processing a general document. Extract key information and relationships.",
                    instruction_template="""
                    Process the document at: {file_path}
                    
                    1. Extract content using llamaparse_pdf
                    2. Identify key entities, concepts, and relationships
                    3. Store the knowledge in the graph database
                    
                    Provide a clear summary of what was extracted and stored.
                    """,
                    response_format="standard_summary"
                ),
                success_criteria=["PDF parsed", "Content analyzed", "Data stored"]
            ),
            
            "fast_processing": WorkflowConfig(
                name="Fast Processing",
                description="Quick processing with minimal analysis",
                tool_sequence=["llamaparse_pdf"],
                prompt_template=PromptTemplate(
                    instruction_template="""
                    Quickly extract content from: {file_path}
                    
                    Use llamaparse_pdf to get the text content. 
                    Provide a brief summary of the document content.
                    """,
                    response_format="brief_summary"
                ),
                success_criteria=["PDF parsed", "Summary provided"]
            )
        }
    
    def get_enabled_tools(self) -> List[ToolConfig]:
        """Get list of enabled tools based on configuration"""
        return [
            config for name, config in self.tool_configs.items() 
            if config.enabled and name in self.enabled_tools
        ]
    
    def get_workflow(self, workflow_type: WorkflowType) -> WorkflowConfig:
        """Get workflow configuration for specified type"""
        return self.workflows.get(workflow_type.value, self.workflows[WorkflowType.GENERAL_DOCUMENT.value])
    
    def save_to_file(self, file_path: str):
        """Save configuration to YAML file"""
        config_dict = {
            "agent_settings": {
                "model_name": self.model_name,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "processing_mode": self.processing_mode.value
            },
            "tools": {
                "enabled_tools": self.enabled_tools,
                "tool_configs": {
                    name: {
                        "enabled": config.enabled,
                        "priority": config.priority,
                        "required": config.required,
                        "parameters": config.parameters
                    }
                    for name, config in self.tool_configs.items()
                }
            },
            "workflows": {
                name: {
                    "description": workflow.description,
                    "tool_sequence": workflow.tool_sequence,
                    "parallel_tools": workflow.parallel_tools,
                    "prompt_template": {
                        "system_prompt": workflow.prompt_template.system_prompt,
                        "instruction_template": workflow.prompt_template.instruction_template,
                        "response_format": workflow.prompt_template.response_format
                    },
                    "success_criteria": workflow.success_criteria
                }
                for name, workflow in self.workflows.items()
            },
            "prompts": {
                "system_prompt": self.system_prompt,
                "custom_instructions": self.custom_instructions,
                "response_format": self.response_format
            },
            "processing": {
                "timeout_seconds": self.timeout_seconds,
                "retry_attempts": self.retry_attempts,
                "parallel_processing": self.parallel_processing
            },
            "output": {
                "include_intermediate_results": self.include_intermediate_results,
                "detailed_logging": self.detailed_logging,
                "save_processing_trace": self.save_processing_trace
            }
        }
        
        with open(file_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'OrchestratorConfig':
        """Load configuration from YAML file"""
        with open(file_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Create instance with loaded values
        config = cls()
        
        # Load agent settings
        if 'agent_settings' in config_dict:
            agent = config_dict['agent_settings']
            config.model_name = agent.get('model_name', config.model_name)
            config.temperature = agent.get('temperature', config.temperature)
            config.max_tokens = agent.get('max_tokens')
            config.processing_mode = ProcessingMode(agent.get('processing_mode', 'thorough'))
        
        # Load tool configurations
        if 'tools' in config_dict:
            tools = config_dict['tools']
            config.enabled_tools = tools.get('enabled_tools', config.enabled_tools)
            
            if 'tool_configs' in tools:
                for name, tool_config in tools['tool_configs'].items():
                    config.tool_configs[name] = ToolConfig(
                        name=name,
                        enabled=tool_config.get('enabled', True),
                        priority=tool_config.get('priority', 1),
                        required=tool_config.get('required', False),
                        parameters=tool_config.get('parameters', {})
                    )
        
        # Load workflow configurations
        if 'workflows' in config_dict:
            for name, workflow_dict in config_dict['workflows'].items():
                prompt_template = PromptTemplate()
                if 'prompt_template' in workflow_dict:
                    pt = workflow_dict['prompt_template']
                    prompt_template.system_prompt = pt.get('system_prompt', '')
                    prompt_template.instruction_template = pt.get('instruction_template', '')
                    prompt_template.response_format = pt.get('response_format', '')
                
                config.workflows[name] = WorkflowConfig(
                    name=workflow_dict.get('description', name),
                    description=workflow_dict.get('description', ''),
                    tool_sequence=workflow_dict.get('tool_sequence', []),
                    parallel_tools=workflow_dict.get('parallel_tools', []),
                    prompt_template=prompt_template,
                    success_criteria=workflow_dict.get('success_criteria', [])
                )
        
        # Load other settings
        if 'prompts' in config_dict:
            prompts = config_dict['prompts']
            config.system_prompt = prompts.get('system_prompt', config.system_prompt)
            config.custom_instructions = prompts.get('custom_instructions', config.custom_instructions)
            config.response_format = prompts.get('response_format', config.response_format)
        
        if 'processing' in config_dict:
            processing = config_dict['processing']
            config.timeout_seconds = processing.get('timeout_seconds', config.timeout_seconds)
            config.retry_attempts = processing.get('retry_attempts', config.retry_attempts)
            config.parallel_processing = processing.get('parallel_processing', config.parallel_processing)
        
        if 'output' in config_dict:
            output = config_dict['output']
            config.include_intermediate_results = output.get('include_intermediate_results', config.include_intermediate_results)
            config.detailed_logging = output.get('detailed_logging', config.detailed_logging)
            config.save_processing_trace = output.get('save_processing_trace', config.save_processing_trace)
        
        return config

def create_default_config() -> OrchestratorConfig:
    """Create a default orchestrator configuration"""
    return OrchestratorConfig()

def create_research_config() -> OrchestratorConfig:
    """Create a configuration optimized for research papers"""
    config = OrchestratorConfig()
    config.default_workflow = WorkflowType.RESEARCH_PAPER
    config.processing_mode = ProcessingMode.THOROUGH
    config.detailed_logging = True
    config.include_intermediate_results = True
    return config

def create_fast_config() -> OrchestratorConfig:
    """Create a configuration for fast processing"""
    config = OrchestratorConfig()
    config.default_workflow = WorkflowType.FAST
    config.processing_mode = ProcessingMode.FAST
    config.enabled_tools = ["llamaparse_pdf"]
    config.timeout_seconds = 60
    return config
"""LangGraph document processing orchestrator"""
from typing import Dict, Any, List
import asyncio
from pathlib import Path

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from processor.config import ProcessorConfig
from processor.orchestrator_config import OrchestratorConfig, WorkflowType, ProcessingMode
from processor.tools.llamaparse_tool import llamaparse_pdf
from tools.shared_registry import SharedToolRegistry

class DocumentOrchestrator:
    """Intelligent document processing orchestrator using LangGraph"""
    
    def __init__(self, config: ProcessorConfig, orchestrator_config: OrchestratorConfig = None):
        self.config = config
        self.orchestrator_config = orchestrator_config or OrchestratorConfig()
        
        # Initialize Groq LLM with orchestrator config
        self.llm = ChatGroq(
            model=self.orchestrator_config.model_name,
            temperature=self.orchestrator_config.temperature,
            groq_api_key=config.groq_api_key,
            max_tokens=self.orchestrator_config.max_tokens
        )
        
        # Initialize tools based on configuration
        self.tools = self._initialize_tools()
        
        # Create LangGraph agent with system prompt
        self.agent = create_react_agent(
            self.llm, 
            self.tools, 
            checkpointer=MemorySaver(),
            state_modifier=self.orchestrator_config.system_prompt
        )
        
        print(f"✅ DocumentOrchestrator initialized")
        print(f"🤖 Model: {self.orchestrator_config.model_name}")
        print(f"🔧 Mode: {self.orchestrator_config.processing_mode.value}")
        print(f"📋 Tools: {len(self.tools)} ({[tool.name for tool in self.tools]})")
        print(f"🚀 Workflow: {self.orchestrator_config.default_workflow.value}")
    
    def _initialize_tools(self) -> List:
        """Initialize tools based on configuration"""
        all_tools = [llamaparse_pdf] + SharedToolRegistry.get_all_tools()
        enabled_tool_configs = self.orchestrator_config.get_enabled_tools()
        enabled_names = [config.name for config in enabled_tool_configs]
        
        # Filter tools based on configuration
        selected_tools = [
            tool for tool in all_tools 
            if tool.name in enabled_names
        ]
        
        # Sort by priority (lower number = higher priority)
        tool_priority_map = {
            config.name: config.priority 
            for config in enabled_tool_configs
        }
        
        selected_tools.sort(key=lambda t: tool_priority_map.get(t.name, 999))
        
        return selected_tools
    
    async def process_document(self, file_path: str, workflow_type: WorkflowType = None) -> Dict[str, Any]:
        """Process a single document through the LangGraph agent using configured workflows"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            print(f"🔄 Processing document: {file_path.name}")
            
            # Determine workflow to use
            workflow_type = workflow_type or self.orchestrator_config.default_workflow
            workflow = self.orchestrator_config.get_workflow(workflow_type)
            
            print(f"📋 Using workflow: {workflow.name}")
            
            # Create processing instruction using workflow template
            processing_instruction = self._build_processing_instruction(
                file_path, workflow
            )
            
            # Add custom instructions if configured
            if self.orchestrator_config.custom_instructions:
                processing_instruction += f"\n\nAdditional Instructions:\n{self.orchestrator_config.custom_instructions}"
            
            print(f"🤖 Executing agent with {len(self.tools)} tools...")
            
            # Execute through LangGraph agent
            response = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": processing_instruction}]},
                config={"configurable": {"thread_id": str(file_path)}}
            )
            
            # Extract final message from agent response
            final_message = response.get("messages", [])[-1].content if response.get("messages") else "Processing completed"
            
            # Build result based on configuration
            result = {
                "success": True,
                "file_path": str(file_path),
                "workflow_used": workflow.name,
                "workflow_type": workflow_type.value,
                "agent_response": final_message,
                "processing_steps": len(response.get("messages", [])),
                "message": f"Document {file_path.name} processed using {workflow.name}",
                "tools_used": [tool.name for tool in self.tools]
            }
            
            # Include intermediate results if configured
            if self.orchestrator_config.include_intermediate_results:
                result["intermediate_messages"] = [
                    msg.content for msg in response.get("messages", [])
                ]
            
            # Check success criteria
            result["success_criteria_met"] = self._check_success_criteria(
                result, workflow.success_criteria
            )
            
            print(f"✅ Completed processing: {file_path.name}")
            return result
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
            return {
                "success": False,
                "file_path": str(file_path),
                "workflow_type": workflow_type.value if workflow_type else "unknown",
                "error": str(e)
            }
    
    def _build_processing_instruction(self, file_path: Path, workflow) -> str:
        """Build processing instruction from workflow template"""
        if workflow.prompt_template.instruction_template:
            # Use workflow-specific template
            instruction = workflow.prompt_template.instruction_template.format(
                file_path=file_path,
                llamaparse_api_key=self.config.llamaparse_api_key
            )
        else:
            # Fallback to basic instruction
            instruction = f"""
            Process the document at: {file_path}
            
            Available tools: {[tool.name for tool in self.tools]}
            Tool sequence (if specified): {workflow.tool_sequence}
            
            Extract key information and relationships from the document.
            Use the available tools in the most effective order.
            """
        
        return instruction
    
    def _check_success_criteria(self, result: Dict[str, Any], criteria: List[str]) -> List[str]:
        """Check which success criteria were met"""
        met_criteria = []
        
        for criterion in criteria:
            if criterion.lower() in result.get("agent_response", "").lower():
                met_criteria.append(criterion)
        
        return met_criteria
    
    def process_document_sync(self, file_path: str) -> Dict[str, Any]:
        """Synchronous wrapper for document processing"""
        return asyncio.run(self.process_document(file_path))

# CLI interface for testing
async def main():
    """Main CLI interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python document_pipeline.py <pdf_file_path>")
        print("Example: python document_pipeline.py /path/to/document.pdf")
        return
    
    pdf_path = sys.argv[1]
    
    try:
        config = ProcessorConfig()
        config.validate()
        
        orchestrator = DocumentOrchestrator(config)
        result = await orchestrator.process_document(pdf_path)
        
        print("\n" + "="*50)
        print("PROCESSING RESULT:")
        print("="*50)
        for key, value in result.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Test function
async def test_orchestrator():
    """Test the basic orchestrator setup"""
    config = ProcessorConfig()
    config.validate()
    
    orchestrator = DocumentOrchestrator(config)
    
    # Create a dummy test file for testing
    test_file = Path("test_document.txt")
    test_file.write_text("This is a test document for processing.")
    
    try:
        result = await orchestrator.process_document(str(test_file))
        print("Test result:", result)
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # CLI mode with file argument
        asyncio.run(main())
    else:
        # Test mode
        asyncio.run(test_orchestrator())
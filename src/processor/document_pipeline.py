"""LangGraph document processing orchestrator"""
from typing import Dict, Any, List
import asyncio
from pathlib import Path

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from processor.config import ProcessorConfig
from processor.tools.llamaparse_tool import llamaparse_pdf
from processor.tools.citation_tool import extract_citations
from processor.tools.storage_tool import store_in_neo4j

class DocumentOrchestrator:
    """Intelligent document processing orchestrator using LangGraph"""
    
    def __init__(self, config: ProcessorConfig):
        self.config = config
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            model=config.model_name,
            temperature=config.temperature,
            groq_api_key=config.groq_api_key
        )
        
        # Initialize tools
        self.tools = [
            llamaparse_pdf,
            extract_citations, 
            store_in_neo4j
        ]
        
        # Create LangGraph agent
        self.agent = create_react_agent(
            self.llm, 
            self.tools, 
            checkpointer=MemorySaver()
        )
        
        print(f"✅ DocumentOrchestrator initialized with {len(self.tools)} tools")
        print(f"📋 Available tools: {[tool.name for tool in self.tools]}")
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a single document through the LangGraph agent"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            print(f"🔄 Processing document: {file_path.name}")
            
            # Create processing instruction for the agent
            processing_instruction = f"""
            Process the PDF document at: {file_path}
            
            Follow these steps:
            1. Use llamaparse_pdf to extract content from the PDF (pass the API key from config)
            2. Use extract_citations to find all citations and references from the extracted content
            3. Extract entities and relationships from the content (create sample entities and relationships for now)
            4. Use store_in_neo4j to save everything to the knowledge graph
            
            Return a summary of what was processed and stored.
            """
            
            # Execute through LangGraph agent
            response = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": processing_instruction}]},
                config={"configurable": {"thread_id": str(file_path)}}
            )
            
            # Extract final message from agent response
            final_message = response.get("messages", [])[-1].content if response.get("messages") else "Processing completed"
            
            result = {
                "success": True,
                "file_path": str(file_path),
                "agent_response": final_message,
                "processing_steps": len(response.get("messages", [])),
                "message": f"Document {file_path.name} processed through LangGraph agent"
            }
            
            print(f"✅ Completed processing: {file_path.name}")
            return result
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
            return {
                "success": False,
                "file_path": str(file_path),
                "error": str(e)
            }
    
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
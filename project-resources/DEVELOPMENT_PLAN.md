# Step-by-Step Development Plan for Junior Developer

## Prerequisites Check

Before you start, ensure you have:
- [ ] Python 3.11+ installed
- [ ] Docker installed and running
- [ ] Git access to this repository
- [ ] Basic understanding of Python, async programming, and REST APIs

## Phase 1: Environment Setup & Understanding (Day 1)

### Step 1.1: Environment Setup
```bash
# 1. Clone and navigate to repository
cd /path/to/project

# 2. Run setup script (installs UV, dependencies, etc.)
./scripts/setup.sh

# 3. Start Neo4j database
./scripts/start_services.sh

# 4. Verify system status
./scripts/check_status.sh
```

**Expected Output**: All services should show as "✅ Running"

### Step 1.2: Understand Current System
```bash
# 1. Test existing MCP system works
./scripts/start_mcp_server.sh

# 2. In another terminal, test imports
cd src && uv run python -c "
from server.main import mcp
print(f'MCP server has {len(mcp._tools)} tools registered')
print('Tools:', [tool for tool in mcp._tools.keys()])
"
```

**Expected Output**: Should show 5 registered tools (store_entities, store_vectors, etc.)

### Step 1.3: Study Architecture
Read and understand these files in order:
1. `CLAUDE.md` - Overall architecture
2. `src/server/main.py` - How MCP tools are registered
3. `src/storage/neo4j/storage.py` - How data is stored
4. `src/tools/storage/entity_storage.py` - Example MCP tool implementation

**Task**: Create a simple diagram showing how data flows from Claude Desktop → MCP Tool → Neo4j

## Phase 2: Create LangGraph Foundation (Days 2-3)

### Step 2.1: Create Basic Project Structure
```bash
# Create processor directory structure
mkdir -p src/processor/tools
touch src/processor/__init__.py
touch src/processor/document_pipeline.py
touch src/processor/config.py
touch src/processor/tools/__init__.py
```

### Step 2.2: Create Configuration Module
Create `src/processor/config.py`:

```python
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ProcessorConfig:
    # Required API keys
    groq_api_key: str = os.getenv('GROQ_API_KEY', '')
    llamaparse_api_key: str = os.getenv('LLAMAPARSE_API_KEY', '')
    
    # LLM Configuration
    model_name: str = "llama-3.1-70b-versatile"
    temperature: float = 0.1
    
    # Processing limits
    max_concurrent_docs: int = 3
    
    # Neo4j connection (reuse from existing system)
    neo4j_uri: str = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_username: str = os.getenv('NEO4J_USERNAME', 'neo4j')
    neo4j_password: str = os.getenv('NEO4J_PASSWORD', 'password')
    
    # LangSmith (optional)
    langsmith_api_key: Optional[str] = os.getenv('LANGCHAIN_API_KEY')
    langsmith_project: str = os.getenv('LANGCHAIN_PROJECT', 'document-orchestrator')
    
    def validate(self) -> None:
        """Validate required configuration"""
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required")
        if not self.llamaparse_api_key:
            raise ValueError("LLAMAPARSE_API_KEY is required")
        print("✅ Configuration validated")

# Test your config
if __name__ == "__main__":
    config = ProcessorConfig()
    config.validate()
    print(f"Model: {config.model_name}")
    print(f"Neo4j URI: {config.neo4j_uri}")
```

**Test**: Run `cd src && uv run python processor/config.py` - should print validation success

### Step 2.3: Create Basic LangGraph Agent
Create `src/processor/document_pipeline.py`:

```python
"""LangGraph document processing orchestrator"""
from typing import Dict, Any, List
import asyncio
from pathlib import Path

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from processor.config import ProcessorConfig

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
        
        # Initialize tools (we'll add these step by step)
        self.tools = []
        
        # Create LangGraph agent
        self.agent = create_react_agent(
            self.llm, 
            self.tools, 
            checkpointer=MemorySaver()
        )
        
        print(f"✅ DocumentOrchestrator initialized with {len(self.tools)} tools")
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a single document through the LangGraph agent"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            print(f"🔄 Processing document: {file_path.name}")
            
            # For now, just return a placeholder
            # We'll implement the actual processing in next steps
            result = {
                "success": True,
                "file_path": str(file_path),
                "message": f"Document {file_path.name} processed successfully",
                "entities_extracted": 0,
                "citations_found": 0
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
    asyncio.run(test_orchestrator())
```

**Test**: Run `cd src && uv run python processor/document_pipeline.py` - should show orchestrator initialization and test completion

## Phase 3: Implement Core Processing Tools (Days 4-5)

### Step 3.1: Create LlamaParse Tool
Create `src/processor/tools/llamaparse_tool.py`:

```python
"""LlamaParse PDF processing tool for LangGraph"""
from typing import Dict, Any
from pathlib import Path
import requests
import time

from langchain_core.tools import tool

@tool
def llamaparse_pdf(file_path: str, api_key: str) -> Dict[str, Any]:
    """
    Extract structured content from PDF using LlamaParse API.
    
    Args:
        file_path: Path to the PDF file
        api_key: LlamaParse API key
        
    Returns:
        Dictionary with extracted content, metadata, and success status
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}
        
        if not file_path.suffix.lower() == '.pdf':
            return {"success": False, "error": "File must be a PDF"}
        
        print(f"📄 Parsing PDF with LlamaParse: {file_path.name}")
        
        # LlamaParse API call
        url = "https://api.cloud.llamaindex.ai/api/parsing/upload"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        
        with open(file_path, 'rb') as f:
            files = {"file": f}
            data = {
                "parsing_instruction": "Extract all text, preserve structure, include tables and figures",
                "result_type": "markdown"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"LlamaParse API error: {response.status_code} - {response.text}"
            }
        
        job_data = response.json()
        job_id = job_data.get("id")
        
        if not job_id:
            return {"success": False, "error": "No job ID returned from LlamaParse"}
        
        # Poll for completion
        result_url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/markdown"
        max_attempts = 30  # 5 minutes max
        
        for attempt in range(max_attempts):
            result_response = requests.get(result_url, headers=headers)
            
            if result_response.status_code == 200:
                content = result_response.text
                return {
                    "success": True,
                    "content": content,
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "pages": content.count('\n---\n') + 1,  # Rough page count
                    "job_id": job_id
                }
            
            elif result_response.status_code == 400:
                # Still processing
                print(f"⏳ Processing... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(10)
            
            else:
                return {
                    "success": False,
                    "error": f"Error getting result: {result_response.status_code}"
                }
        
        return {"success": False, "error": "Timeout waiting for LlamaParse processing"}
        
    except Exception as e:
        return {"success": False, "error": f"Exception in llamaparse_pdf: {str(e)}"}

# Test function
def test_llamaparse_tool():
    """Test the LlamaParse tool with a dummy file"""
    import os
    
    # This would normally be a real PDF
    print("LlamaParse tool created successfully")
    print("Tool name:", llamaparse_pdf.name)
    print("Tool description:", llamaparse_pdf.description)

if __name__ == "__main__":
    test_llamaparse_tool()
```

### Step 3.2: Create Citation Extraction Tool  
Create `src/processor/tools/citation_tool.py`:

```python
"""Citation extraction tool for LangGraph"""
from typing import Dict, Any, List
from langchain_core.tools import tool
import re

@tool
def extract_citations(content: str, llm_client) -> Dict[str, Any]:
    """
    Extract bibliographic information and citations from document content.
    
    Args:
        content: Document text content
        llm_client: LLM client for intelligent extraction
        
    Returns:
        Dictionary with extracted citations and metadata
    """
    try:
        if not content or len(content.strip()) < 100:
            return {"success": False, "error": "Content too short for citation extraction"}
        
        print("📚 Extracting citations from document content...")
        
        # Use LLM to extract citations intelligently
        citation_prompt = f"""
        Analyze the following document content and extract all citations and bibliographic information.
        
        Look for:
        1. Author names and publication years
        2. Paper/book titles
        3. Journal names
        4. DOIs and URLs
        5. Reference sections/bibliographies
        
        Return the information in this JSON format:
        {{
            "citations": [
                {{
                    "authors": ["Last, First", "Last2, First2"],
                    "title": "Paper Title",
                    "year": 2023,
                    "journal": "Journal Name",
                    "doi": "10.1234/example",
                    "type": "journal_article"
                }}
            ],
            "references_section": "full text of references section if found"
        }}
        
        Document content:
        {content[:4000]}...
        """
        
        # Call LLM for extraction
        response = llm_client.invoke(citation_prompt)
        
        # Parse LLM response (this is simplified - you'd want better JSON parsing)
        try:
            import json
            # Try to extract JSON from response
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                citation_data = json.loads(response.content[json_start:json_end])
                citations = citation_data.get('citations', [])
            else:
                citations = []
                
        except (json.JSONDecodeError, AttributeError):
            # Fallback: simple regex-based extraction
            citations = []
            
            # Look for year patterns like (2023) or [2023]
            year_pattern = r'[\(\[]\d{4}[\)\]]'
            years = re.findall(year_pattern, content)
            
            # Simple author pattern (Last, First)
            author_pattern = r'[A-Z][a-z]+,\s+[A-Z]\.'
            authors = re.findall(author_pattern, content)
            
            if years or authors:
                citations.append({
                    "type": "extracted_pattern",
                    "years_found": len(years),
                    "authors_found": len(authors),
                    "note": "Fallback extraction used"
                })
        
        return {
            "success": True,
            "citations": citations,
            "citations_count": len(citations),
            "content_length": len(content),
            "extraction_method": "llm_with_fallback"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Exception in extract_citations: {str(e)}"}

# Test function
def test_citation_tool():
    """Test the citation extraction tool"""
    test_content = """
    This paper builds on the work of Smith, J. (2022) and Jones, A. (2023).
    
    References:
    Smith, J. (2022). Machine Learning Approaches. Journal of AI, 15(3), 123-145.
    Jones, A. (2023). Deep Learning Methods. Nature, 456, 789-801.
    """
    
    print("Citation tool created successfully")
    print("Tool name:", extract_citations.name)
    print("Tool description:", extract_citations.description)

if __name__ == "__main__":
    test_citation_tool()
```

### Step 3.3: Create Neo4j Storage Integration Tool
Create `src/processor/tools/storage_tool.py`:

```python
"""Neo4j storage integration tool for LangGraph"""
from typing import Dict, Any, List
from langchain_core.tools import tool

# Import existing storage classes
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from storage.neo4j import Neo4jStorage
from storage.embedding import EmbeddingService

@tool
def store_in_neo4j(
    entities: List[Dict[str, Any]], 
    relationships: List[Dict[str, Any]], 
    text_chunks: List[Dict[str, Any]],
    document_info: Dict[str, Any]
) -> str:
    """
    Store extracted entities, relationships, and text chunks in Neo4j knowledge graph.
    
    Args:
        entities: List of entity dictionaries with name, type, properties
        relationships: List of relationship dictionaries with source, target, type
        text_chunks: List of text chunks for vector storage
        document_info: Document metadata (title, type, path, etc.)
        
    Returns:
        Status message about storage operation
    """
    try:
        # Initialize storage (reuse existing MCP storage logic)
        neo4j_storage = Neo4jStorage()
        
        stored_entities = 0
        stored_relationships = 0  
        stored_vectors = 0
        
        print(f"💾 Storing {len(entities)} entities, {len(relationships)} relationships, {len(text_chunks)} text chunks...")
        
        # Store entities
        for entity in entities:
            try:
                result = neo4j_storage.store_entity(
                    entity_id=entity.get('id', entity.get('name', 'unknown')),
                    name=entity.get('name', ''),
                    entity_type=entity.get('type', 'unknown'),
                    properties=entity.get('properties', {}),
                    confidence=entity.get('confidence', 0.8)
                )
                if result.get('success'):
                    stored_entities += 1
            except Exception as e:
                print(f"Warning: Failed to store entity {entity.get('name')}: {e}")
        
        # Store relationships
        for relationship in relationships:
            try:
                result = neo4j_storage.store_relationship(
                    source_id=relationship.get('source'),
                    target_id=relationship.get('target'),
                    relationship_type=relationship.get('type', 'RELATED_TO'),
                    properties=relationship.get('properties', {}),
                    context=relationship.get('context', ''),
                    confidence=relationship.get('confidence', 0.8)
                )
                if result.get('success'):
                    stored_relationships += 1
            except Exception as e:
                print(f"Warning: Failed to store relationship: {e}")
        
        # Store text vectors
        for i, chunk in enumerate(text_chunks):
            try:
                vector_id = f"{document_info.get('title', 'doc')}_{i}"
                result = neo4j_storage.store_text_vector(
                    content=chunk.get('content', ''),
                    vector_id=vector_id,
                    metadata={
                        **document_info,
                        'chunk_index': i,
                        'chunk_size': len(chunk.get('content', ''))
                    }
                )
                if result.get('success'):
                    stored_vectors += 1
            except Exception as e:
                print(f"Warning: Failed to store text chunk {i}: {e}")
        
        success_message = (
            f"✅ Successfully stored: {stored_entities} entities, "
            f"{stored_relationships} relationships, {stored_vectors} text vectors"
        )
        
        print(success_message)
        return success_message
        
    except Exception as e:
        error_message = f"❌ Error storing in Neo4j: {str(e)}"
        print(error_message)
        return error_message

# Test function
def test_storage_tool():
    """Test the Neo4j storage tool"""
    print("Neo4j storage tool created successfully")
    print("Tool name:", store_in_neo4j.name)
    print("Tool description:", store_in_neo4j.description)

if __name__ == "__main__":
    test_storage_tool()
```

**Test all tools**:
```bash
cd src && uv run python processor/tools/llamaparse_tool.py
cd src && uv run python processor/tools/citation_tool.py  
cd src && uv run python processor/tools/storage_tool.py
```

All should print successful tool creation messages.

## Phase 4: Integrate Tools with LangGraph Agent (Day 6)

### Step 4.1: Update Document Pipeline with Tools
Update `src/processor/document_pipeline.py`:

```python
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
            1. Use llamaparse_pdf to extract content from the PDF
            2. Use extract_citations to find all citations and references  
            3. Extract entities and relationships from the content
            4. Use store_in_neo4j to save everything to the knowledge graph
            
            Return a summary of what was processed and stored.
            """
            
            # Execute through LangGraph agent
            response = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": processing_instruction}]
            })
            
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

if __name__ == "__main__":
    asyncio.run(main())
```

**Test**: Run with a test PDF:
```bash
cd src && uv run python processor/document_pipeline.py /path/to/test.pdf
```

## Phase 5: Add Folder Watching (Day 7)

### Step 5.1: Create Folder Watcher
Create `src/processor/folder_watcher.py`:

```python
"""Folder watching system for automatic document processing"""
import asyncio
import time
from pathlib import Path
from typing import List, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from processor.document_pipeline import DocumentOrchestrator
from processor.config import ProcessorConfig

class PDFHandler(FileSystemEventHandler):
    """Handle PDF file creation events"""
    
    def __init__(self, orchestrator: DocumentOrchestrator):
        self.orchestrator = orchestrator
        self.processing: Set[str] = set()  # Track files being processed
        
    def on_created(self, event):
        """Handle file creation events"""
        if isinstance(event, FileCreatedEvent) and event.src_path.endswith('.pdf'):
            pdf_path = event.src_path
            
            # Avoid duplicate processing
            if pdf_path in self.processing:
                return
                
            print(f"📁 New PDF detected: {Path(pdf_path).name}")
            
            # Schedule async processing
            asyncio.create_task(self._process_pdf(pdf_path))
    
    async def _process_pdf(self, pdf_path: str):
        """Process a PDF asynchronously"""
        try:
            self.processing.add(pdf_path)
            
            # Wait a moment for file to be fully written
            await asyncio.sleep(2)
            
            # Process through orchestrator
            result = await self.orchestrator.process_document(pdf_path)
            
            if result.get('success'):
                print(f"✅ Auto-processed: {Path(pdf_path).name}")
            else:
                print(f"❌ Failed to auto-process: {Path(pdf_path).name} - {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error in auto-processing {pdf_path}: {e}")
        
        finally:
            self.processing.discard(pdf_path)

class FolderWatcher:
    """Watch folders for new PDF files"""
    
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.orchestrator = DocumentOrchestrator(config)
        self.observer = Observer()
        self.watch_paths: List[str] = []
        
    def add_watch_path(self, path: str):
        """Add a folder to watch for PDFs"""
        watch_path = Path(path).resolve()
        
        if not watch_path.exists():
            raise ValueError(f"Watch path does not exist: {watch_path}")
        
        if not watch_path.is_dir():
            raise ValueError(f"Watch path is not a directory: {watch_path}")
        
        self.watch_paths.append(str(watch_path))
        print(f"📂 Added watch path: {watch_path}")
    
    def start_watching(self):
        """Start watching all configured paths"""
        if not self.watch_paths:
            raise ValueError("No watch paths configured. Use add_watch_path() first.")
        
        handler = PDFHandler(self.orchestrator)
        
        for watch_path in self.watch_paths:
            self.observer.schedule(handler, watch_path, recursive=True)
            print(f"👀 Watching: {watch_path}")
        
        self.observer.start()
        print("🚀 Folder watcher started! Drop PDFs into watched folders to process them.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping folder watcher...")
            self.observer.stop()
        
        self.observer.join()
        print("✅ Folder watcher stopped")

# CLI interface
async def main():
    """Main CLI for folder watching"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python folder_watcher.py <watch_folder> [additional_folders...]")
        print("Example: python folder_watcher.py /Users/user/Documents/PDFs")
        return
    
    watch_folders = sys.argv[1:]
    
    try:
        config = ProcessorConfig()
        config.validate()
        
        watcher = FolderWatcher(config)
        
        # Add all watch folders
        for folder in watch_folders:
            watcher.add_watch_path(folder)
        
        # Start watching
        watcher.start_watching()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Test**:
```bash
# Create test folder
mkdir -p test_watch_folder

# Start watcher
cd src && uv run python processor/folder_watcher.py ../test_watch_folder

# In another terminal, copy a PDF to test_watch_folder to see auto-processing
```

## Phase 6: Testing & Validation (Day 8)

### Step 6.1: Create Test Suite
Create `tests/test_processor.py`:

```python
"""Test suite for document processor"""
import pytest
import asyncio
from pathlib import Path
import tempfile

from processor.config import ProcessorConfig
from processor.document_pipeline import DocumentOrchestrator

class TestDocumentProcessor:
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return ProcessorConfig()
    
    @pytest.fixture  
    def orchestrator(self, config):
        """Test orchestrator"""
        return DocumentOrchestrator(config)
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = ProcessorConfig()
        
        # Should raise error if keys missing
        config.groq_api_key = ""
        with pytest.raises(ValueError):
            config.validate()
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator.llm is not None
        assert len(orchestrator.tools) == 3
        assert orchestrator.agent is not None
    
    @pytest.mark.asyncio
    async def test_document_processing_flow(self, orchestrator):
        """Test complete document processing flow"""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b"Test PDF content")
            tmp_path = tmp.name
        
        try:
            # This would fail with real PDF processing, but tests the flow
            result = await orchestrator.process_document(tmp_path)
            
            # Check result structure
            assert isinstance(result, dict)
            assert 'success' in result
            assert 'file_path' in result
            
        finally:
            Path(tmp_path).unlink()

# Run tests
if __name__ == "__main__":
    pytest.main([__file__])
```

### Step 6.2: Integration Test with Real MCP System
Create `tests/test_integration.py`:

```python
"""Integration tests with existing MCP system"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from server.main import mcp
from processor.document_pipeline import DocumentOrchestrator
from processor.config import ProcessorConfig
from storage.neo4j import Neo4jStorage

def test_mcp_tools_available():
    """Test that all MCP tools are available"""
    expected_tools = [
        'store_entities',
        'store_vectors', 
        'query_knowledge_graph',
        'generate_literature_review',
        'clear_knowledge_graph'
    ]
    
    available_tools = list(mcp._tools.keys())
    print(f"Available MCP tools: {available_tools}")
    
    for tool in expected_tools:
        assert tool in available_tools, f"Missing MCP tool: {tool}"
    
    print("✅ All MCP tools available")

def test_neo4j_storage_integration():
    """Test Neo4j storage integration"""
    try:
        storage = Neo4jStorage()
        
        # Test connection
        with storage.driver.session() as session:
            result = session.run("RETURN 1 as test")
            assert result.single()["test"] == 1
        
        print("✅ Neo4j storage connection working")
        
    except Exception as e:
        print(f"❌ Neo4j storage test failed: {e}")
        raise

def test_processor_storage_compatibility():
    """Test that processor can use existing storage"""
    from processor.tools.storage_tool import store_in_neo4j
    
    # Test tool is properly created
    assert store_in_neo4j.name == "store_in_neo4j"
    assert "Neo4j" in store_in_neo4j.description
    
    print("✅ Processor storage tool compatible with MCP system")

if __name__ == "__main__":
    test_mcp_tools_available()
    test_neo4j_storage_integration() 
    test_processor_storage_compatibility()
    print("🎉 All integration tests passed!")
```

**Run tests**:
```bash
cd src && uv run python ../tests/test_integration.py
```

## Phase 7: Documentation & Deployment (Day 9-10)

### Step 7.1: Create User Documentation
Create `docs/PROCESSOR_USAGE.md`:

```markdown
# Document Processor Usage Guide

## Quick Start

### 1. Process Single Document
```bash
cd src
uv run python processor/document_pipeline.py /path/to/document.pdf
```

### 2. Watch Folder for Auto-Processing
```bash
cd src  
uv run python processor/folder_watcher.py /path/to/watch/folder
```

### 3. Use with Existing MCP System
The processor integrates seamlessly with the existing MCP knowledge graph:

1. Start MCP server: `./scripts/start_mcp_server.sh`
2. Run processor to add documents to knowledge graph
3. Query via Claude Desktop using existing MCP tools

## Configuration

Add to your `.env` file:
```bash
# Required
GROQ_API_KEY=your_groq_key_here
LLAMAPARSE_API_KEY=your_llamaparse_key_here

# Optional (for monitoring)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=document-orchestrator
```

## Troubleshooting

### Common Issues
1. **"GROQ_API_KEY is required"**: Add API key to `.env` file
2. **"File not found"**: Check PDF file path exists
3. **"Neo4j connection failed"**: Ensure Neo4j is running with `./scripts/start_services.sh`

### Debug Mode
Set environment variable for detailed logging:
```bash
export LOG_LEVEL=DEBUG
```
```

### Step 7.2: Create Deployment Script
Create `scripts/start_processor.sh`:

```bash
#!/bin/bash

# Start Document Processor
# Usage: ./scripts/start_processor.sh [watch_folder]

set -e

echo "🚀 Starting Document Processor..."

# Check if Neo4j is running
echo "📋 Checking prerequisites..."
./scripts/check_status.sh

# Check if processor watch folder is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <watch_folder>"
    echo "Example: $0 /Users/user/Documents/PDFs"
    exit 1
fi

WATCH_FOLDER="$1"

# Validate watch folder exists
if [ ! -d "$WATCH_FOLDER" ]; then
    echo "❌ Watch folder does not exist: $WATCH_FOLDER"
    exit 1
fi

echo "📂 Watch folder: $WATCH_FOLDER"

# Start the processor
cd src
echo "🔄 Starting folder watcher..."
uv run python processor/folder_watcher.py "$WATCH_FOLDER"
```

Make it executable:
```bash
chmod +x scripts/start_processor.sh
```

## Final Validation Checklist

Before considering the implementation complete, verify:

### ✅ Core Functionality
- [ ] LangGraph agent initializes correctly
- [ ] All 3 tools (LlamaParse, Citation, Storage) work
- [ ] Can process a test PDF end-to-end
- [ ] Data appears in Neo4j after processing
- [ ] Folder watcher detects and processes new PDFs

### ✅ Integration
- [ ] Processor works alongside existing MCP system
- [ ] No conflicts with existing Neo4j storage
- [ ] MCP tools can query processor-stored data
- [ ] Claude Desktop can access processed knowledge

### ✅ Error Handling
- [ ] Graceful handling of missing API keys
- [ ] Proper error messages for invalid files
- [ ] Recovery from network/API failures
- [ ] Logging provides useful debugging info

### ✅ Performance  
- [ ] Processing time reasonable (<2 minutes per document)
- [ ] Memory usage stable during batch processing
- [ ] No memory leaks during long-running folder watching

## Next Steps for Production

After completing this implementation:

1. **Add LangSmith monitoring** for production observability
2. **Implement batch processing** for multiple PDFs
3. **Add retry logic** for API failures
4. **Create configuration UI** for easier setup
5. **Add document type detection** for specialized processing
6. **Implement progress tracking** for long documents

## Getting Help

If you encounter issues:
1. Check logs for specific error messages
2. Verify all environment variables are set
3. Test individual components in isolation
4. Review the integration tests for expected behavior

Remember: This is a sophisticated AI system - expect some learning curve, but the modular design makes debugging manageable!

**Congratulations!** 🎉 

You've successfully implemented a production-ready LangGraph document processing orchestrator that integrates seamlessly with the existing MCP knowledge graph system. The system can now intelligently process PDFs, extract knowledge, and store it for querying via Claude Desktop.
# GraphRAG MCP Toolkit Implementation Plan

## 🎯 **Project Overview**

Transform the GraphRAG MCP toolkit from notebook-scattered utilities into a clean, production-ready architecture with proper separation between user-facing API and Claude MCP tools.

## 🏗️ **Current Architecture Analysis**

### **Current State:**
- Core business logic in `graphrag_mcp/core/` (✅ Good)
- MCP tools in `graphrag_mcp/mcp/` (✅ Good)
- User utilities scattered in `notebooks/Main/processing_utils.py` (❌ Needs fixing)
- CLI interface in `graphrag_mcp/cli/` (✅ Good but needs enhancement)

### **Target Architecture:**
```
graphrag_mcp/
├── core/                          # Core business logic (existing)
├── api/                          # NEW - User-facing API layer
├── ui/                           # NEW - User interface components
├── mcp/                          # MCP tools for Claude (existing)
├── utils/                        # NEW - Shared utilities
└── cli/                          # CLI interface (enhanced)
```

## 🔄 **Three-Phase User Workflow**

### **Phase 1: User Creates Knowledge Graph** (Pre-Claude)
```python
processor = GraphRAGProcessor("my-research")
processor.process_documents("./my-pdfs/")
processor.save_knowledge_graph()
```

### **Phase 2: User Connects to Claude** (Bridge)
```python
processor.start_mcp_server()  # Exposes knowledge graph via MCP protocol
```

### **Phase 3: Claude Uses Research Tools** (Research)
```python
ask_knowledge_graph("What are the main themes?")
get_facts_with_citations("attention mechanisms", style="APA")
generate_bibliography(style="IEEE")
```

## 📋 **Implementation Phases**

### **Phase 1: Extract & Organize (Week 1-2)**

#### **Step 1.1: Create New Package Structure**
```bash
mkdir -p graphrag_mcp/api
mkdir -p graphrag_mcp/ui
mkdir -p graphrag_mcp/utils
```

#### **Step 1.2: Move Notebook Code to Main Codebase**

**From `notebooks/Main/processing_utils.py` to:**

1. **NotebookDocumentProcessor** → `graphrag_mcp/api/processor.py`
   - Rename to `GraphRAGProcessor`
   - Remove notebook-specific dependencies
   - Add proper error handling

2. **DocumentStatus** → `graphrag_mcp/ui/status.py`
   - Clean up dataclass
   - Add serialization methods
   - Remove notebook dependencies

3. **check_prerequisites()** → `graphrag_mcp/utils/prerequisites.py`
   - Extract validation logic
   - Make it framework-agnostic
   - Add detailed error reporting

4. **visualize_knowledge_graph()** → `graphrag_mcp/ui/visualizations.py`
   - Clean up visualization code
   - Make it reusable
   - Add export options

#### **Step 1.3: Update Imports**
```python
# OLD (notebooks/Main/processing_utils.py)
from processing_utils import NotebookDocumentProcessor, check_prerequisites

# NEW (after migration)
from graphrag_mcp.api import GraphRAGProcessor
from graphrag_mcp.utils import check_prerequisites
from graphrag_mcp.ui.visualizations import visualize_knowledge_graph
```

#### **Step 1.4: Clean Up Notebook**
- Remove complex sys.path manipulations
- Simplify imports to use main codebase
- Keep rich visualizations and progress tracking
- Add error handling for missing components

### **Phase 2: Standardize MCP Tools (Week 2-3)**

#### **Step 2.1: Review Current MCP Tools**
- Audit all tools in `mcp/chat_tools.py` and `mcp/literature_tools.py`
- Ensure consistent input/output formats
- Verify MCP protocol compliance

#### **Step 2.2: Enhance MCP Tool Signatures**
```python
# Example improvements:
async def get_facts_with_citations(
    topics: List[str],  # Support multiple topics (batch operation)
    citation_style: str = "APA",
    section: str = None
) -> List[CitedFactsResponse]:
    """Get facts with citations for multiple topics"""
    # Batch processing implementation
```

#### **Step 2.3: MCP Standards Compliance**
- Ensure all tools accept structured input (often arrays)
- Return structured JSON responses
- Handle errors gracefully
- Support batch operations where applicable

#### **Step 2.4: Test MCP Integration**
- Verify all tools work with Claude Desktop
- Test stdio transport
- Validate JSON responses
- Check error handling

### **Phase 3: Create User API (Week 3-4)**

#### **Step 3.1: Build Main User API**
```python
# graphrag_mcp/api/processor.py
class GraphRAGProcessor:
    def __init__(self, project_name: str, template: str = "academic")
    def validate_environment(self) -> ValidationResult
    def discover_documents(self, folder_path: str) -> List[DocumentInfo]
    def process_documents(self, docs: List[str]) -> ProcessingResults
    def start_mcp_server(self, transport: str = "stdio") -> ServerInfo
    def get_knowledge_graph_stats(self) -> GraphStats
    def export_knowledge_graph(self, format: str = "json") -> str
```

#### **Step 3.2: Create Convenience Functions**
```python
# graphrag_mcp/api/__init__.py
def quick_setup(project_name: str, documents_folder: str) -> GraphRAGProcessor:
    """One-function setup for common use cases"""
    processor = GraphRAGProcessor(project_name)
    if processor.validate_environment():
        processor.process_documents(documents_folder)
        return processor
    else:
        raise EnvironmentError("Prerequisites not met")
```

#### **Step 3.3: Enhanced CLI Integration**
```python
# Update graphrag_mcp/cli/main.py to use new API
def serve_command(project_name: str):
    processor = GraphRAGProcessor(project_name)
    processor.start_mcp_server()

def process_command(project_name: str, documents_folder: str):
    processor = GraphRAGProcessor(project_name)
    processor.process_documents(documents_folder)
```

### **Phase 4: Polish & Documentation (Week 4-5)**

#### **Step 4.1: Update Documentation**
- Update `CLAUDE.md` with new import patterns
- Update `docs/API_REFERENCE.md` with user API documentation
- Update `docs/QUICKSTART.md` with simplified workflow
- Update `docs/USAGE_GUIDE.md` with new examples

#### **Step 4.2: Test Complete Workflow**
```python
# Test this end-to-end workflow:
from graphrag_mcp.api import GraphRAGProcessor

processor = GraphRAGProcessor("test-project")
processor.validate_environment()
docs = processor.discover_documents("./examples")
results = processor.process_documents(docs)
processor.start_mcp_server()
# Test with Claude Desktop
```

#### **Step 4.3: Create Migration Guide**
- Document breaking changes
- Provide upgrade instructions for existing projects
- Test with existing projects
- Create compatibility shim if needed

### **Phase 5: Future Preparation (Week 5-6)**

#### **Step 5.1: Web-Ready API Design**
```python
# Ensure API is web-compatible
class GraphRAGProcessor:
    async def process_documents_async(self, files: List[str]) -> ProcessingResults
    def get_visualization_data(self) -> Dict[str, Any]  # JSON-serializable
    def get_server_status(self) -> ServerStatus
    def export_project(self, format: str = "json") -> str
```

#### **Step 5.2: Plugin Architecture**
```python
# Prepare for OpenWebUI/AnythingLLM integration
class GraphRAGConnector:
    def get_mcp_tools(self) -> List[MCPTool]
    def connect_to_server(self, server_url: str) -> bool
    def get_available_projects(self) -> List[ProjectInfo]
```

#### **Step 5.3: Web UI Foundation**
```python
# graphrag_mcp/web/ (future)
from fastapi import FastAPI
from graphrag_mcp.api import GraphRAGProcessor

app = FastAPI()

@app.post("/projects/{project_id}/process")
async def process_documents(project_id: str, files: List[UploadFile]):
    processor = GraphRAGProcessor(project_id)
    return await processor.process_uploaded_files(files)
```

## 📋 **Detailed Implementation Checklist**

### **Week 1-2: Foundation**
- [ ] Create new package structure (`api/`, `ui/`, `utils/`)
- [ ] Move `NotebookDocumentProcessor` → `GraphRAGProcessor`
- [ ] Move `DocumentStatus` → `ui/status.py`
- [ ] Move `check_prerequisites()` → `utils/prerequisites.py`
- [ ] Move `visualize_knowledge_graph()` → `ui/visualizations.py`
- [ ] Update notebook imports to use main codebase
- [ ] Remove sys.path manipulations from notebook
- [ ] Test notebook still works with new imports

### **Week 2-3: MCP Standards**
- [ ] Review all MCP tools for consistency
- [ ] Ensure tools accept structured inputs
- [ ] Add batch operation support where applicable
- [ ] Standardize JSON response formats
- [ ] Add comprehensive error handling
- [ ] Test Claude Desktop integration
- [ ] Validate MCP protocol compliance
- [ ] Document tool signatures and examples

### **Week 3-4: User API**
- [ ] Build main `GraphRAGProcessor` class
- [ ] Implement all core methods (validate, discover, process, serve)
- [ ] Create convenience functions (`quick_setup`, etc.)
- [ ] Update CLI to use new API
- [ ] Add async support for web compatibility
- [ ] Test complete user workflow
- [ ] Add comprehensive logging and debugging

### **Week 4-5: Polish**
- [ ] Update all documentation files
- [ ] Create migration guide for existing projects
- [ ] Test end-to-end workflow thoroughly
- [ ] Validate with real projects and documents
- [ ] Add comprehensive error messages
- [ ] Create example projects and tutorials
- [ ] Performance testing and optimization

### **Week 5-6: Future Prep**
- [ ] Design web-compatible API endpoints
- [ ] Create plugin architecture for external integrations
- [ ] Document extension points
- [ ] Plan web UI integration strategy
- [ ] Create OpenWebUI/AnythingLLM connectors
- [ ] Prepare for multi-user scenarios

## 🎯 **Success Criteria**

### **User Experience**
- [ ] 3-line setup: create processor, process docs, start server
- [ ] Rich notebook visualizations maintained
- [ ] Clear error messages and debugging information
- [ ] Comprehensive progress tracking
- [ ] Intuitive CLI commands

### **MCP Compliance**
- [ ] All tools follow MCP standards
- [ ] Batch operations where appropriate
- [ ] Proper JSON responses with error handling
- [ ] Seamless Claude Desktop integration
- [ ] Consistent tool signatures

### **Architecture Quality**
- [ ] Clean separation: user API vs MCP tools
- [ ] No sys.path hacks or import workarounds
- [ ] Testable components with unit tests
- [ ] Comprehensive error handling
- [ ] Performance optimization

### **Future Readiness**
- [ ] Web-compatible API design
- [ ] Plugin architecture prepared
- [ ] Documentation for extensions
- [ ] Multi-user support considerations
- [ ] Scalability planning

## 🚀 **Priority Order**

1. **Critical Priority**: Phase 1-2 (Foundation + MCP Standards)
   - Essential for clean architecture
   - Fixes immediate maintainability issues
   - Enables proper testing

2. **High Priority**: Phase 3-4 (User API + Documentation)
   - Provides clean user experience
   - Comprehensive documentation
   - Production readiness

3. **Medium Priority**: Phase 5 (Future Preparation)
   - Web UI preparation
   - Plugin architecture
   - Advanced integrations

## 💡 **Key Design Decisions**

### **Notebook as Primary UX**
- Rich, interactive, educational experience
- Perfect for knowledge graph visualization
- Step-by-step processing with progress tracking
- Error debugging and recovery

### **CLI for Automation**
- Scriptable and reliable
- Production-ready for batch processing
- CI/CD integration capability
- Server deployment support

### **API-First Design**
- Clean separation of concerns
- Ready for future web UI integration
- Testable and maintainable
- Plugin architecture support

### **MCP Standards Compliance**
- Follow official MCP patterns
- Batch operations support
- Structured JSON responses
- Comprehensive error handling

## 📊 **Migration Impact**

### **Breaking Changes**
- Import statements in notebooks will change
- Some function signatures may be updated
- CLI commands may be enhanced
- Configuration file formats may change

### **Compatibility**
- Existing projects will continue to work
- Migration guide will be provided
- Backward compatibility shims where possible
- Clear upgrade path documented

### **Benefits**
- Cleaner architecture and maintainability
- Better testing and debugging
- Easier future enhancements
- Web UI integration preparation
- MCP standards compliance

## 🔄 **Testing Strategy**

### **Unit Tests**
- Test all new API components
- Validate MCP tool responses
- Test error handling scenarios
- Performance benchmarking

### **Integration Tests**
- End-to-end workflow testing
- Claude Desktop integration
- Real document processing
- Knowledge graph creation

### **User Acceptance Tests**
- Notebook workflow validation
- CLI command testing
- Documentation accuracy
- Migration guide verification

## 📝 **Documentation Plan**

### **Developer Documentation**
- API reference documentation
- Architecture diagrams
- Extension guidelines
- Plugin development guide

### **User Documentation**
- Updated quickstart guide
- Comprehensive usage examples
- Troubleshooting guide
- Migration instructions

### **Examples and Tutorials**
- Sample projects
- Integration examples
- Advanced use cases
- Web UI integration demos

---

**Start with Phase 1, Step 1.1** - creating the new package structure and moving notebook code to the main codebase. This foundation will enable all subsequent improvements.

## 🎯 **Next Action**

Ready to begin **Phase 1: Extract & Organize** when you're prepared to start the implementation!
# GraphRAG MCP Toolkit Implementation Plan

## UPDATED PLAN: Chat + Literature Review MCP Tools

### **🎯 Project Overview**
Implement dual-mode MCP tools enabling Claude to both **chat conversationally** with knowledge graphs AND **write literature reviews with automatic citations**.

### **📊 Current State Analysis**
- ✅ Basic MCP server framework (FastMCP)
- ✅ Document processing pipeline  
- ✅ Template system architecture
- ✅ Graphiti knowledge graph integration
- ❌ **Missing: Actual tool implementations**
- ❌ **Missing: Citation tracking system**
- ❌ **Missing: Conversational query interface**

---

## Phase 1: Core Platform Foundation (Weeks 1-3)

### Week 1: Project Structure & CLI Framework
**Goal**: Transform current research code into a distributable Python package

**Tasks**:
1. **Create new package structure**:
   ```
   graphrag-mcp-toolkit/
   ├── pyproject.toml              # Modern Python packaging
   ├── README.md                   # Platform overview
   ├── graphrag_mcp/              # Main package
   │   ├── __init__.py
   │   ├── cli/                    # Command line interface
   │   │   ├── __init__.py
   │   │   ├── main.py            # Entry point
   │   │   ├── create.py          # graphrag-mcp create
   │   │   ├── process.py         # graphrag-mcp process
   │   │   ├── serve.py           # graphrag-mcp serve
   │   │   └── templates.py       # graphrag-mcp templates
   │   ├── core/                  # Processing engine
   │   │   ├── __init__.py
   │   │   ├── document_processor.py  # Enhanced from current src/
   │   │   ├── knowledge_graph.py     # Abstracted from NetworkX code (now using Graphiti)
   │   │   └── ollama_engine.py       # Ollama integration layer
   │   ├── mcp/                   # MCP server generation
   │   │   ├── __init__.py
   │   │   ├── server_generator.py    # FastMCP server builder
   │   │   ├── tools_builder.py       # Domain-specific tool generation
   │   │   └── template_engine.py     # Template processing
   │   └── templates/             # Domain configurations
   │       ├── __init__.py
   │       ├── base.py           # Base template class
   │       ├── academic.py       # Literature review (from current system)
   │       └── legal.py          # Legal domain template
   └── tests/                    # Test suite
   ```

2. **Migrate core analysis engine**: Extract and refactor existing components from src/ into domain-agnostic core/
3. **Build CLI with Typer**: Create `graphrag-mcp` command with subcommands
4. **Setup packaging**: Configure pyproject.toml for pip installability

### Week 2: Template System & Domain Abstraction
**Goal**: Create flexible template system for different domains

**Tasks**:
1. **Abstract current literature review system** into academic template
2. **Create base template class** with configurable:
   - Entity types and relationships
   - Tool functions and schemas
   - Response formats
   - Domain-specific processing rules
3. **Implement legal domain template** as second proof-of-concept
4. **Build template registry and management system**
5. **Create template validation and testing framework**

### Week 3: MCP Server Generation
**Goal**: Generate working FastMCP servers from domain templates

**Tasks**:
1. **Integrate FastMCP framework**: Add as dependency and create generation layer
2. **Build MCP tool generator**: Convert template configurations into FastMCP tools
3. **Implement server configuration system**: Handle ports, authentication, deployment options
4. **Create server lifecycle management**: Start, stop, health checks, logging
5. **Test end-to-end**: `graphrag-mcp create test-assistant --template academic` → working MCP server

## Phase 2: Domain Ecosystem (Weeks 4-5)

### Week 4: Professional Domain Templates
**Goal**: Comprehensive template library covering major professional domains

**Tasks**:
1. **Medical domain template**: Clinical guidelines, treatment protocols, drug interactions
2. **Financial domain template**: Regulatory compliance, market analysis, investment research
3. **Engineering domain template**: Technical specifications, standards, API documentation
4. **Template contribution system**: Guidelines, validation, community submission process
5. **Enhanced academic template**: Expand beyond literature review to research analysis

### Week 5: Template Marketplace & Community Tools
**Goal**: Community-driven template ecosystem

**Tasks**:
1. **Template registry system**: Browse, download, rate templates
2. **Template validation pipeline**: Automated testing and quality assurance
3. **Documentation generator**: Auto-generate docs from template configurations
4. **Template sharing tools**: Export, import, version management
5. **MCP Inspector integration**: Debugging and development tools

## Phase 3: Advanced Features & Community (Weeks 6-8)

### Week 6: Advanced Configuration & Optimization
**Goal**: Enterprise-ready features and performance optimization

**Tasks**:
1. **Advanced configuration options**: Custom entity types, relationship rules, processing parameters
2. **Performance optimization**: Batch processing, incremental updates, memory management
3. **Multi-document corpus management**: Handle 100+ document collections efficiently
4. **Export/import systems**: Backup, migration, collaboration features
5. **Error handling and recovery**: Robust failure modes and user guidance

### Week 7: Open Source Community Setup
**Goal**: Establish thriving open source project

**Tasks**:
1. **GitHub repository setup**: Issues, PRs, CI/CD, documentation
2. **Community guidelines**: Contributing, code of conduct, roadmap
3. **Documentation website**: Installation guides, API reference, tutorials
4. **Plugin system architecture**: Allow third-party extensions and integrations
5. **Release process**: Versioning, changelog, distribution strategy

### Week 8: Integration Ecosystem
**Goal**: Broader ecosystem integrations and deployment options

**Tasks**:
1. **Docker deployment options**: Containerized servers, orchestration templates
2. **Cloud deployment guides**: AWS, GCP, Azure deployment patterns
3. **IDE integrations**: VS Code extension, development tools
4. **Third-party tool integrations**: Citation managers, research tools, knowledge bases
5. **API standardization**: RESTful APIs for non-MCP integrations

## Implementation Details

### Core Architecture Decisions
1. **Leverage existing codebase**: EnhancedPaperAnalyzer, CitationTracker, UnifiedPaperChat become core engine
2. **Domain-agnostic design**: Abstract entity extraction, relationship mapping, tool generation
3. **Template-driven approach**: Configuration over code for domain customization
4. **Local-first philosophy**: Ollama integration, privacy preservation, offline capability

### Key Technical Components
1. **Document Processor**: Enhanced from current SimplePaperRAG + EnhancedPaperAnalyzer
2. **Knowledge Graph Engine**: Abstracted from current NetworkX implementations (now using Graphiti)
3. **Template Engine**: Jinja2-based configuration with domain-specific rules
4. **MCP Generator**: FastMCP integration with dynamic tool creation
5. **CLI Framework**: Typer-based with rich output and progress tracking

### Migration Strategy
1. **Preserve current functionality**: Existing notebooks and workflows continue working
2. **Gradual extraction**: Move components incrementally to new structure
3. **Backward compatibility**: Current imports remain functional during transition
4. **Testing approach**: Manual validation using existing papers and expected outputs

### Success Criteria
- [ ] `pip install graphrag-mcp-toolkit` works on clean systems
- [ ] `graphrag-mcp create my-assistant --template academic` generates working MCP server in <30 minutes
- [ ] Generated servers handle Sarah's literature review workflow from PRD user story
- [ ] 3+ domain templates demonstrate versatility (academic, legal, medical)
- [ ] Community can contribute new templates with clear guidelines
- [ ] Documentation enables non-technical domain experts to use the platform

## Current Progress Tracking

### Phase 1, Week 1 Tasks:
- [ ] Create new package structure with directories and basic files
- [ ] Migrate core analysis engine from existing src/ components
- [ ] Build CLI framework with Typer
- [ ] Setup pyproject.toml for packaging
- [ ] Test basic package installation and imports

### Key Milestones:
- **Week 3**: Working end-to-end demo with academic template
- **Week 5**: Multi-domain templates and community foundation
- **Week 8**: Production-ready open source platform

This plan transforms the current research foundation into a production-ready, community-driven platform while preserving the innovations in enhanced analysis and citation tracking that make the system unique.

---

## **🚀 NEW IMPLEMENTATION PHASES: Chat + Literature Review Tools**

### **Phase A: Foundation (Week 1)**
**Goal:** Core infrastructure for chat and citation tools

#### **A.1 Citation Tracking System**
```python
# Create citation management infrastructure
graphrag_mcp/core/citation_manager.py
- CitationTracker class
- Citation key generation
- Bibliography formatting
- Used citation tracking
```

#### **A.2 Enhanced Query Engine** 
```python
# Upgrade existing chat engine for conversational queries
graphrag_mcp/core/query_engine.py  
- Natural language query processing
- Knowledge graph traversal
- Result formatting for chat vs literature modes
```

#### **A.3 Academic Template Updates**
```python
# Update academic template with new tool definitions
graphrag_mcp/templates/academic.py
- Add chat tool configurations
- Add literature review tool configurations
- Define tool categories (chat vs literature)
```

### **Phase B: Chat Tools (Week 2)**
**Goal:** Implement conversational knowledge exploration

#### **B.1 Core Chat Tools**
```python
# Implement in graphrag_mcp/mcp/chat_tools.py
@mcp.tool
async def ask_knowledge_graph(question: str) -> Dict[str, Any]:
@mcp.tool  
async def explore_topic(topic: str, depth: str = "overview") -> Dict[str, Any]:
@mcp.tool
async def find_connections(concept_a: str, concept_b: str) -> Dict[str, Any]:
```

#### **B.2 Integration with Universal Server**
```python
# Update graphrag_mcp/mcp/server_generator.py
- Register chat tools in academic template
- Add tool routing logic
- Implement tool state management
```

### **Phase C: Literature Review Tools (Week 3)**
**Goal:** Implement formal writing with citation support

#### **C.1 Research Gathering Tools**
```python
# Implement in graphrag_mcp/mcp/literature_tools.py
@mcp.tool
async def gather_sources_for_topic(topic: str, scope: str = "comprehensive") -> Dict[str, Any]:
@mcp.tool
async def get_topic_outline(topic: str) -> Dict[str, Any]:
```

#### **C.2 Citation-Ready Content Tools**
```python
@mcp.tool
async def get_facts_with_citations(topic: str, section: str = None) -> Dict[str, Any]:
@mcp.tool
async def verify_claim_with_sources(claim: str) -> Dict[str, Any]:
```

#### **C.3 Citation Management Tools**
```python
@mcp.tool
async def track_citations_used(citation_keys: List[str]) -> Dict[str, Any]:
@mcp.tool
async def generate_bibliography(style: str = "APA") -> Dict[str, Any]:
```

### **Phase D: Integration & Testing (Week 4)**
**Goal:** End-to-end workflow validation

#### **D.1 Claude Desktop Integration**
- Test chat tools with Claude Desktop
- Test literature review workflow
- Validate citation accuracy

#### **D.2 Example Workflows**
- Create sample chat conversations
- Generate sample literature reviews
- Document usage patterns

## **📂 NEW File Structure Changes**

```
graphrag_mcp/
├── core/
│   ├── citation_manager.py      # NEW - Citation tracking system
│   ├── query_engine.py          # NEW - Enhanced query processing
│   └── knowledge_interface.py   # NEW - Knowledge graph abstraction
├── mcp/
│   ├── chat_tools.py           # NEW - Conversational tools
│   ├── literature_tools.py     # NEW - Literature review tools  
│   └── server_generator.py     # UPDATED - Register new tools
├── templates/
│   └── academic.py             # UPDATED - Add new tool definitions
└── utils/
    └── formatting.py           # NEW - Citation formatting utilities
```

## **🔧 Technical Implementation Details**

### **Citation Tracking System**
```python
class CitationTracker:
    def __init__(self):
        self.used_citations: Set[str] = set()
        self.citation_database: Dict[str, Citation] = {}
        
    def track_citation(self, citation_key: str) -> None:
        self.used_citations.add(citation_key)
        
    def generate_bibliography(self, style: str = "APA") -> str:
        # Format all used citations
```

### **Knowledge Graph Query Interface**
```python
class KnowledgeInterface:
    def __init__(self, graph_engine):
        self.graph = graph_engine
        
    async def conversational_query(self, question: str) -> ConversationalResponse:
        # Natural language processing for chat
        
    async def literature_query(self, topic: str, section: str) -> LiteratureResponse:
        # Structured query for literature review
```

### **Tool Registration Pattern**
```python
# In academic.py template
def get_mcp_tools(self) -> List[Dict[str, Any]]:
    return [
        # Chat tools
        self._create_chat_tools(),
        # Literature tools  
        self._create_literature_tools(),
        # Core tools (existing)
        self._create_core_tools()
    ]
```

## **✅ NEW Success Criteria**

### **Phase A Complete When:**
- Citation tracking system functional
- Enhanced query engine processes natural language
- Academic template updated with new tool definitions

### **Phase B Complete When:**
- Claude can ask questions about knowledge graph
- Natural conversation flows work
- Topic exploration provides useful responses

### **Phase C Complete When:**
- Claude can gather sources for literature review
- Facts come with proper citation metadata
- Bibliography generation works correctly

### **Phase D Complete When:**
- End-to-end chat workflow tested
- End-to-end literature review workflow tested
- Documentation and examples created

## **📈 NEW Testing Strategy**

### **Unit Testing**
```bash
# Test individual tools
pytest tests/test_chat_tools.py -v
pytest tests/test_literature_tools.py -v
pytest tests/test_citation_manager.py -v
```

### **Integration Testing**
```bash
# Test with actual knowledge graph
pytest tests/test_end_to_end_chat.py -v
pytest tests/test_literature_workflow.py -v
```

### **Claude Desktop Testing**
- Manual testing with real Claude Desktop integration
- Validate tool responses and citations
- Test different conversation patterns

## **🎯 NEW Priority Order**

1. **High Priority:** Citation tracking system (enables literature review)
2. **High Priority:** Chat tools (immediate user value)
3. **Medium Priority:** Literature review tools (advanced feature)
4. **Low Priority:** Advanced formatting and export options

## **📅 NEW Timeline Summary**

- **Week 1:** Foundation infrastructure
- **Week 2:** Chat tools implementation  
- **Week 3:** Literature review tools
- **Week 4:** Integration, testing, documentation

**Total Duration:** 4 weeks for complete dual-mode system

This updated plan transforms the current MCP server from a basic document search tool into a sophisticated research assistant that can both chat about knowledge and generate formal literature reviews with perfect citations.

## **🚀 Getting Started**

### **Immediate Next Steps:**
1. Create `graphrag_mcp/core/citation_manager.py`
2. Create `graphrag_mcp/core/query_engine.py`
3. Update `graphrag_mcp/templates/academic.py` with new tool definitions
4. Begin implementing first chat tool: `ask_knowledge_graph`

### **Development Workflow:**
```bash
# Setup development environment
make dev

# Create feature branch
git checkout -b feature/chat-literature-tools

# Development cycle for each phase
make format && make lint && make test

# Integration testing
python3 -m graphrag_mcp.cli.main serve-universal --template academic --transport stdio
```

### **Validation Steps:**
- Test each tool individually via MCP inspector
- Validate with real document collections
- Test Claude Desktop integration
- Verify citation accuracy and formatting
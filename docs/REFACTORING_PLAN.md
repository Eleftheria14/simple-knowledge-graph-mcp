# GraphRAG MCP Refactoring Plan

## 🎯 **Goal: Clean Up Large Files & Improve Separation of Concerns**

Make the codebase more maintainable by splitting large files and separating concerns, without over-engineering the research tool.

## 📊 **Current File Sizes Analysis**

### **Files That Need Splitting:**
- `processing_utils.py` (866 lines) - **HIGHEST PRIORITY**
- `literature_tools.py` (889 lines) - **MEDIUM PRIORITY**
- `citation_manager.py` (654 lines) - **MEDIUM PRIORITY**
- `cli/main.py` (934 lines) - **LOWER PRIORITY**
- `query_engine.py` (654 lines) - **LOWER PRIORITY**

### **Files That Are Good Size:**
- `document_processor.py` (373 lines) ✅
- `analyzer.py` (397 lines) ✅
- `chat_engine.py` (445 lines) ✅
- `ollama_engine.py` (319 lines) ✅

## 🏗️ **Proposed Structure**

### **1. Split `processing_utils.py` (866 → 4 files)**

#### **Current Structure:**
```
notebooks/Main/
└── processing_utils.py (866 lines)
    ├── DocumentStatus dataclass
    ├── NotebookDocumentProcessor class
    ├── Complex import/reload logic
    ├── Document discovery
    ├── Processing coordination
    ├── Progress tracking
    ├── Analytics generation
    ├── Visualization (200+ lines)
    └── Error handling
```

#### **Proposed Structure:**
```
notebooks/Main/
├── document_discovery.py      (~100 lines)
│   ├── DocumentStatus dataclass
│   ├── DocumentDiscovery class
│   └── PDF scanning and file discovery
├── processing_coordinator.py  (~200 lines)
│   ├── ProcessingCoordinator class
│   ├── Single document processing
│   ├── Batch processing with progress
│   └── Error handling and retry logic
├── analytics_utils.py         (~300 lines)
│   ├── show_analytics() function
│   ├── visualize_knowledge_graph() function
│   ├── Progress tracking utilities
│   └── Chart generation functions
├── notebook_interface.py      (~100 lines)
│   ├── Simple NotebookInterface class
│   ├── Clean imports (no reload logic)
│   └── Ties everything together
└── Simple_Document_Processing.ipynb (updated)
```

### **2. Split `literature_tools.py` (889 → 3 files)**

#### **Current Structure:**
```
graphrag_mcp/mcp/
└── literature_tools.py (889 lines)
    ├── LiteratureToolsEngine class
    ├── gather_sources_for_topic
    ├── get_facts_with_citations
    ├── verify_claim_with_sources
    ├── get_topic_outline
    ├── track_citations_used
    └── generate_bibliography
```

#### **Proposed Structure:**
```
graphrag_mcp/mcp/
├── source_tools.py           (~300 lines)
│   ├── gather_sources_for_topic
│   ├── verify_claim_with_sources
│   └── Related source gathering functions
├── citation_tools.py         (~300 lines)
│   ├── get_facts_with_citations
│   ├── track_citations_used
│   └── Citation integration functions
├── writing_tools.py          (~300 lines)
│   ├── get_topic_outline
│   ├── generate_bibliography
│   └── Writing assistance functions
└── literature_tools.py       (~100 lines)
    └── LiteratureToolsEngine (coordinator)
```

### **3. Split `citation_manager.py` (654 → 3 files)**

#### **Current Structure:**
```
graphrag_mcp/core/
└── citation_manager.py (654 lines)
    ├── CitationTracker class
    ├── Citation tracking logic
    ├── Multiple format support (APA, IEEE, Nature, MLA)
    ├── Bibliography generation
    └── Export functionality (JSON, CSV, BibTeX)
```

#### **Proposed Structure:**
```
graphrag_mcp/core/
├── citation_tracker.py       (~200 lines)
│   ├── Core CitationTracker class
│   ├── Citation storage and tracking
│   └── Usage context management
├── citation_formatter.py     (~250 lines)
│   ├── Format citations in different styles
│   ├── APA, IEEE, Nature, MLA formatters
│   └── Bibliography generation
├── citation_export.py        (~200 lines)
│   ├── Export to JSON, CSV, BibTeX
│   ├── Import functionality
│   └── Data conversion utilities
└── citation_manager.py       (~100 lines)
    └── Main CitationManager (coordinator)
```

### **4. Split `cli/main.py` (934 → 3 files)** *(Lower Priority)*

#### **Proposed Structure:**
```
graphrag_mcp/cli/
├── serve_commands.py         (~300 lines)
│   ├── MCP server commands
│   ├── serve-universal
│   └── Server management
├── process_commands.py       (~300 lines)
│   ├── Document processing commands
│   ├── Batch processing
│   └── Analysis commands
├── utility_commands.py       (~300 lines)
│   ├── Status checking
│   ├── Template management
│   └── Configuration commands
└── main.py                   (~100 lines)
    └── Main CLI app and routing
```

## 🚀 **Implementation Strategy**

### **Phase 1: Notebook Interface (2-3 hours)**
**Priority: HIGHEST** - Most used by researchers

1. **Extract Analytics Functions** (1 hour)
   - Move `show_analytics()` and `visualize_knowledge_graph()` to `analytics_utils.py`
   - Keep as standalone functions, not class methods

2. **Extract Document Discovery** (1 hour)
   - Move `DocumentStatus` and discovery logic to `document_discovery.py`
   - Create clean `DocumentDiscovery` class

3. **Extract Processing Coordinator** (1 hour)
   - Move processing logic to `processing_coordinator.py`
   - Clean up async handling and error management

4. **Create Simple Interface** (30 minutes)
   - Create `notebook_interface.py` with clean imports
   - Remove complex module reloading logic

### **Phase 2: MCP Tools (1-2 hours)**
**Priority: MEDIUM** - Used by MCP server

1. **Split Literature Tools** (1-2 hours)
   - Group related tools into separate files
   - Maintain clean imports in main `literature_tools.py`

### **Phase 3: Citation Management (1-2 hours)**
**Priority: MEDIUM** - If time permits

1. **Split Citation Components** (1-2 hours)
   - Separate tracking, formatting, and export logic
   - Maintain clean coordinator class

## 📋 **What Each File Will Do**

### **Notebook Files:**
- **`document_discovery.py`**: Scan folders, find PDFs, create DocumentStatus objects
- **`processing_coordinator.py`**: Process documents with progress tracking and error handling
- **`analytics_utils.py`**: Generate charts, graphs, and knowledge graph visualization
- **`notebook_interface.py`**: Simple class that ties everything together for notebooks

### **MCP Tools:**
- **`source_tools.py`**: Tools for gathering and verifying sources
- **`citation_tools.py`**: Tools for getting cited facts and tracking citations
- **`writing_tools.py`**: Tools for outlines and bibliography generation

### **Citation Management:**
- **`citation_tracker.py`**: Core citation tracking and storage
- **`citation_formatter.py`**: Format citations in different academic styles
- **`citation_export.py`**: Export citations to various formats

## ✅ **Benefits**

### **1. Improved Maintainability**
- Smaller, focused files are easier to understand
- Clear separation of concerns
- Easier to debug and modify

### **2. Better Contributor Experience**
- New contributors can focus on specific components
- Easier to understand the codebase structure
- Clear boundaries between different functionalities

### **3. Preserved Research Focus**
- Keeps the tool's academic research mission
- Doesn't over-engineer the solution
- Maintains simplicity while improving organization

### **4. Backward Compatibility**
- Existing imports and usage patterns remain the same
- Notebooks continue to work without changes
- MCP server functionality preserved

## ⏱️ **Time Estimate**

- **Phase 1 (Notebook Interface)**: 2-3 hours
- **Phase 2 (MCP Tools)**: 1-2 hours
- **Phase 3 (Citation Management)**: 1-2 hours

**Total: 4-7 hours** of focused refactoring work.

This plan focuses on making the codebase cleaner and more maintainable while preserving its effectiveness as an open-source research tool.
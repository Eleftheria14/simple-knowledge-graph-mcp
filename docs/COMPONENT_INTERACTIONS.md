# GraphRAG MCP Component Interactions

## Component Communication Patterns

### 1. Inter-Component Message Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              COMPONENT INTERACTION MATRIX                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │ UnifiedPaperChat│
                    │   (Orchestrator) │
                    └─────────┬───────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │SimplePaperRAG│   │SimpleKnowl  │   │LangChain    │
    │    (RAG)     │   │edgeGraph    │   │GraphRAG     │
    │              │   │   (Graph)   │   │  (Hybrid)   │
    └─────────────┘   └─────────────┘   └─────────────┘
            │                 │                 │
            ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │   ChromaDB   │   │  Graphiti   │   │  Enhanced   │
    │   Vector     │   │   Graph     │   │  Analyzer   │
    │   Store      │   │   Store     │   │             │
    └─────────────┘   └─────────────┘   └─────────────┘
```

### 2. Component Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DEPENDENCY RELATIONSHIPS                                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   User Input    │
│   (Query/PDF)   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Jupyter         │    │ CLI Interface   │    │ MCP Server      │
│ Interface       │    │ (Typer)         │    │ (FastMCP)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────┐
                    │ UnifiedPaperChat│
                    │ (Main Router)   │
                    └─────────┬───────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │SimplePaper  │ │SimpleKnowl  │ │LangChain    │
        │RAG          │ │edgeGraph    │ │GraphRAG     │
        └─────────────┘ └─────────────┘ └─────────────┘
                │             │             │
                ▼             ▼             ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │   Ollama    │ │  Graphiti   │ │  ChromaDB   │
        │   LLM       │ │  Graph      │ │  Vector     │
        │   Service   │ │  Engine     │ │  Database   │
        └─────────────┘ └─────────────┘ └─────────────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Enhanced        │
                    │ Paper Analyzer  │
                    │ & Citation      │
                    │ Tracker         │
                    └─────────────────┘
```

### 3. API Integration Patterns

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              API COMMUNICATION FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  External APIs  │
│  & Services     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│ Ollama Service  │◄──────────────►│ LLM Interface   │
│ localhost:11434 │                │ (ChatOllama)    │
└─────────────────┘                └─────────┬───────┘
                                             │
                                             ▼
┌─────────────────┐    Python API   ┌─────────────────┐
│ ChromaDB        │◄──────────────►│ Vector Store    │
│ Local Database  │                │ Interface       │
└─────────────────┘                └─────────┬───────┘
                                             │
                                             ▼
┌─────────────────┐    Memory API   ┌─────────────────┐
│ Graphiti        │◄──────────────►│ Graph Engine    │
│ Graph Store     │                │ Interface       │
└─────────────────┘                └─────────┬───────┘
                                             │
                                             ▼
┌─────────────────┐    File I/O     ┌─────────────────┐
│ File System     │◄──────────────►│ Document        │
│ Storage         │                │ Processor       │
└─────────────────┘                └─────────────────┘
```

## Detailed Component Interactions

### 4. SimplePaperRAG Component Interactions

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              SIMPLEPAPER RAG INTERACTIONS                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ SimplePaperRAG  │
│ (Core RAG)      │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │     INPUT │
    │           │
    ▼           ▼
┌─────────┐   ┌─────────┐
│   PDF   │   │ Query   │
│Document │   │ String  │
└─────────┘   └─────────┘
    │           │
    ▼           ▼
┌─────────────────┐
│ PyPDFLoader     │
│ • Extract Text  │
│ • Preserve Meta │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ TextSplitter    │───▶│ Chunk Creation  │
│ • 800 chars     │    │ • Context Aware │
│ • 100 overlap   │    │ • Boundary Resp │
└─────────────────┘    └─────────┬───────┘
                                 │
                                 ▼
┌─────────────────┐    ┌─────────────────┐
│ OllamaEmbedding │◄───│ Embedding Gen   │
│ nomic-embed-text│    │ • Semantic Vec  │
│ HTTP API        │    │ • Batch Process │
└─────────────────┘    └─────────┬───────┘
                                 │
                                 ▼
┌─────────────────┐    ┌─────────────────┐
│ Similarity      │◄───│ Vector Storage  │
│ Calculation     │    │ • NumPy Arrays  │
│ • Cosine Sim    │    │ • Indexing      │
│ • Top-K Select  │    │ • Persistence   │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ ChatOllama      │◄───│ Context Builder │
│ llama3.1:8b     │    │ • Chunk Merge   │
│ temp=0.1        │    │ • Prompt Format │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐
│ Response        │
│ • Answer        │
│ • Confidence    │
│ • Sources       │
└─────────────────┘
```

### 5. SimpleKnowledgeGraph Component Interactions

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              SIMPLE KNOWLEDGE GRAPH INTERACTIONS                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│SimpleKnowledgeG │
│ (Graph Builder) │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Content         │───▶│ LLM Processing  │
│ Chunks          │    │ • Entity Prompt │
│ • Preprocessed  │    │ • JSON Response │
│ • Structured    │    │ • Error Handle  │
└─────────────────┘    └─────────┬───────┘
                                 │
                                 ▼
┌─────────────────┐    ┌─────────────────┐
│ Entity Parser   │◄───│ JSON Extraction │
│ • 8 Categories  │    │ • Validation    │
│ • Validation    │    │ • Fallback      │
│ • Deduplication │    │ • Clean Format  │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Relationship    │───▶│ Graph Builder   │
│ Extraction      │    │ • Node Creation │
│ • Co-occurrence │    │ • Edge Creation │
│ • Semantic      │    │ • Attributes    │
│ • Explicit      │    │ • Validation    │
└─────────────────┘    └─────────┬───────┘
                                 │
                                 ▼
┌─────────────────┐    ┌─────────────────┐
│ Graphiti        │◄───│ Graph Storage   │
│ Graph Engine    │    │ • Nodes/Edges   │
│ • Algorithms    │    │ • Metadata      │
│ • Centrality    │    │ • Persistence   │
│ • Traversal     │    │ • Queries       │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Visualization   │───▶│ Export Options  │
│ • Matplotlib    │    │ • GraphML       │
│ • yFiles        │    │ • JSON          │
│ • Interactive   │    │ • Cytoscape     │
│ • Layouts       │    │ • Custom        │
└─────────────────┘    └─────────────────┘
```

### 6. UnifiedPaperChat Orchestration

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              UNIFIED PAPER CHAT ORCHESTRATION                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ UnifiedPaperChat│
│ (Main Router)   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Query Analysis  │───▶│ Mode Selection  │
│ • Keyword Score │    │ • RAG Score     │
│ • Intent Parse  │    │ • Graph Score   │
│ • Context       │    │ • Confidence    │
│ • History       │    │ • Fallback      │
└─────────────────┘    └─────────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │ RAG Mode    │ │ Graph Mode  │ │ Both Mode   │
            │ Processing  │ │ Processing  │ │ Processing  │
            └─────────────┘ └─────────────┘ └─────────────┘
                    │            │            │
                    ▼            ▼            ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │SimplePaper  │ │SimpleKnowl  │ │ Parallel    │
            │RAG.query()  │ │edgeGraph    │ │ Execution   │
            │             │ │.traverse()  │ │ • RAG+Graph │
            └─────────────┘ └─────────────┘ └─────────────┘
                    │            │            │
                    └────────────┼────────────┘
                                 │
                                 ▼
                    ┌─────────────────┐
                    │ Response        │
                    │ Synthesis       │
                    │ • Context Merge │
                    │ • Entity Enrich │
                    │ • Citation Add  │
                    └─────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Enhanced        │
                    │ Response        │
                    │ • Answer        │
                    │ • Entities      │
                    │ • Relations     │
                    │ • Sources       │
                    └─────────────────┘
```

### 7. Enhanced Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ENHANCED ANALYSIS PIPELINE                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│EnhancedAnalyzer │
│ (Corpus Ready)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Section-Based   │───▶│ Multi-Pass      │
│ Processing      │    │ Extraction      │
│ • 6000 chars    │    │ • Pass 1: Basic │
│ • 1000 overlap  │    │ • Pass 2: Detail│
│ • Context Aware │    │ • Pass 3: Refine│
└─────────────────┘    └─────────┬───────┘
                                 │
                                 ▼
┌─────────────────┐    ┌─────────────────┐
│ Entity          │◄───│ Enhanced        │
│ Categorization  │    │ Extraction      │
│ • 20+ Categories│    │ • Domain Aware  │
│ • Importance    │    │ • Confidence    │
│ • Relationships │    │ • Validation    │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Citation        │───▶│ Location        │
│ Tracking        │    │ Mapping         │
│ • 4 Formats     │    │ • Char Position │
│ • Context       │    │ • Line Numbers  │
│ • Validation    │    │ • Section Map   │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Corpus          │───▶│ Export          │
│ Document        │    │ Formatting      │
│ • Structured    │    │ • GraphML       │
│ • Metadata Rich │    │ • JSON          │
│ • Cross-Linked  │    │ • Custom        │
└─────────────────┘    └─────────────────┘
```

## Cross-Component Communication Protocols

### 8. Inter-Service Communication

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              COMMUNICATION PROTOCOLS                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ Message Passing │
│ Protocols       │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐   ┌─────────┐
│Synchronous│ │Asynchronous│
│ Calls     │ │ Events    │
└─────────┘   └─────────┘
    │           │
    ▼           ▼
┌─────────────────┐   ┌─────────────────┐
│ Method Calls    │   │ Event Queue     │
│ • Direct invoke │   │ • Async/await   │
│ • Return values │   │ • Callbacks     │
│ • Exception     │   │ • Observers     │
│ • Blocking      │   │ • Non-blocking  │
└─────────────────┘   └─────────────────┘
```

### 9. State Synchronization

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              STATE SYNCHRONIZATION                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ State Manager   │
│ (Coordinator)   │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐   ┌─────────┐
│ Session │   │ Global  │
│ State   │   │ State   │
└─────────┘   └─────────┘
    │           │
    ▼           ▼
┌─────────────────┐   ┌─────────────────┐
│ Chat History    │   │ Loaded Papers   │
│ • Conversation  │   │ • Document Cache│
│ • Context       │   │ • Embeddings    │
│ • Preferences   │   │ • Graph Data    │
│ • Temp Data     │   │ • Persistent    │
└─────────────────┘   └─────────────────┘
```

### 10. Error Propagation and Handling

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ERROR PROPAGATION CHAIN                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ Error Source    │
│ (Any Component) │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Local Error     │───▶│ Error           │
│ Handling        │    │ Enrichment      │
│ • Try/Catch     │    │ • Context Add   │
│ • Validation    │    │ • Stack Trace   │
│ • Logging       │    │ • Metadata      │
└─────────────────┘    └─────────┬───────┘
                                 │
                                 ▼
┌─────────────────┐    ┌─────────────────┐
│ Error           │◄───│ Propagation     │
│ Recovery        │    │ Decision        │
│ • Retry         │    │ • Severity      │
│ • Fallback      │    │ • Recovery      │
│ • Degradation   │    │ • User Impact   │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ User            │───▶│ System          │
│ Notification    │    │ Monitoring      │
│ • Friendly Msg  │    │ • Metrics       │
│ • Suggestions   │    │ • Alerts        │
│ • Alternatives  │    │ • Dashboards    │
└─────────────────┘    └─────────────────┘
```

This comprehensive documentation of component interactions demonstrates how the GraphRAG MCP system achieves sophisticated document analysis through well-orchestrated component collaboration while maintaining robustness, scalability, and user-friendly interfaces.
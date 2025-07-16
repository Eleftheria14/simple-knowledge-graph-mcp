# GraphRAG MCP Component Interactions

## 🚀 Simplified Enhanced Architecture Component Interactions

This document explains how the components of the GraphRAG MCP Toolkit interact in the simplified enhanced architecture.

### 1. Core Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CORE COMPONENT INTERACTIONS                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │ Universal       │
                    │ MCP Server      │
                    │ (FastMCP)       │
                    └─────────┬───────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ Chat Tools  │   │Literature   │   │Core Tools   │
    │ Engine      │   │Tools Engine │   │Engine       │
    └─────────────┘   └─────────────┘   └─────────────┘
            │                 │                 │
            ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ Enhanced    │   │ Citation    │   │ Document    │
    │ Query       │   │ Manager     │   │ Processor   │
    │ Engine      │   │(ChromaDB)   │   │             │
    └─────────────┘   └─────────────┘   └─────────────┘
            │                 │                 │
            ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ Neo4j       │   │ ChromaDB    │   │ LLM         │
    │ Entity      │   │ Vector      │   │ Analysis    │
    │ Manager     │   │ Storage     │   │ Engine      │
    └─────────────┘   └─────────────┘   └─────────────┘
```

### 2. Sequential Processing Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              SEQUENTIAL PROCESSING FLOW                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   PDF Input     │
│   Documents     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Document        │───▶│ Text Chunking   │
│ Processor       │    │ • 1000 chars    │
│ • LangChain     │    │ • 200 overlap   │
│ • PDF Extract   │    │ • Context Aware │
└─────────────────┘    └─────────┬───────┘
                                 │
                                 ▼
┌─────────────────┐    ┌─────────────────┐
│ LLM Analysis    │◄───│ Text Chunks     │
│ Engine          │    │ • Raw Text      │
│ • llama3.1:8b   │    │ • Metadata      │
│ • Sequential    │    │ • Structure     │
│ • Comprehensive │    │ • Context       │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Analysis        │───▶│ Enhanced        │
│ Results         │    │ Content         │
│ • Entities      │    │ • Entity Tags   │
│ • Citations     │    │ • Relationships │
│ • Relationships │    │ • Enriched Text │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│ Persistent      │    │ Context-Aware   │
│ Storage         │    │ Embeddings      │
│ • ChromaDB      │    │ • nomic-embed   │
│ • Neo4j         │    │ • Enhanced Text │
│ • Citations     │    │ • Semantic Vec  │
└─────────────────┘    └─────────────────┘
```

### 3. MCP Tools Integration

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              MCP TOOLS INTEGRATION                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ Claude Desktop  │
│ User Interface  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ MCP Protocol    │───▶│ Universal       │
│ Communication   │    │ MCP Server      │
│ • Tool Calls    │    │ • FastMCP       │
│ • Responses     │    │ • Tool Registry │
└─────────────────┘    └─────────┬───────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
        ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
        │ Chat Tools  │   │Literature   │   │ Core Tools  │
        │ • ask_kg    │   │ Tools       │   │ • load_docs │
        │ • explore   │   │ • get_facts │   │ • search    │
        │ • connect   │   │ • verify    │   │ • templates │
        │ • summarize │   │ • outline   │   │ • status    │
        └─────────────┘   └─────────────┘   └─────────────┘
                │                │                │
                ▼                ▼                ▼
        ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
        │ Shared      │   │ Shared      │   │ Shared      │
        │ Citation    │   │ Citation    │   │ Document    │
        │ Manager     │   │ Manager     │   │ Processor   │
        └─────────────┘   └─────────────┘   └─────────────┘
```

### 4. Citation Management Integration

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CITATION MANAGEMENT INTEGRATION                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ Citation        │
│ Manager         │
│ (ChromaDB)      │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐   ┌─────────┐
│Citation │   │ Usage   │
│Storage  │   │Tracking │
└─────────┘   └─────────┘
    │           │
    ▼           ▼
┌─────────────────┐   ┌─────────────────┐
│ Persistent      │   │ Context         │
│ Citation Data   │   │ Tracking        │
│ • Metadata      │   │ • Confidence    │
│ • Provenance    │   │ • Usage Count   │
│ • Relationships │   │ • Sections      │
└─────────┬───────┘   └─────────┬───────┘
          │                     │
          ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Bibliography    │   │ Style           │
│ Generation      │   │ Management      │
│ • APA           │   │ • 4 Styles      │
│ • IEEE          │   │ • Formatting    │
│ • Nature        │   │ • Validation    │
│ • MLA           │   │ • Consistency   │
└─────────────────┘   └─────────────────┘
```

### 5. Knowledge Graph Integration

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              KNOWLEDGE GRAPH INTEGRATION                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ Neo4j Entity    │
│ Manager         │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐   ┌─────────┐
│ Entity  │   │Relation │
│Storage  │   │Storage  │
└─────────┘   └─────────┘
    │           │
    ▼           ▼
┌─────────────────┐   ┌─────────────────┐
│ Entity-Citation │   │ Bidirectional   │
│ Links           │   │ Relationships   │
│ • Provenance    │   │ • Entity-Entity │
│ • Source Track  │   │ • Cite-Entity   │
│ • Confidence    │   │ • Cross-Links   │
└─────────┬───────┘   └─────────┬───────┘
          │                     │
          ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Graph           │   │ Visualization   │
│ Traversal       │   │ • Graphiti      │
│ • Algorithms    │   │ • yFiles        │
│ • Queries       │   │ • Interactive   │
│ • Analysis      │   │ • Real-time     │
└─────────────────┘   └─────────────────┘
```

### 6. CLI Interface Integration

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CLI INTERFACE INTEGRATION                                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ CLI Interface   │
│ (Typer)         │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐   ┌─────────┐
│Project  │   │Document │
│Mgmt     │   │Process  │
└─────────┘   └─────────┘
    │           │
    ▼           ▼
┌─────────────────┐   ┌─────────────────┐
│ • create        │   │ • add-documents │
│ • templates     │   │ • process       │
│ • status        │   │ • visualize     │
│ • validate      │   │ • quick-setup   │
└─────────┬───────┘   └─────────┬───────┘
          │                     │
          ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Server          │   │ Enhanced        │
│ Management      │   │ Document        │
│ • serve         │   │ Processor       │
│ • serve-univ    │   │ • Sequential    │
│ • serve-graph   │   │ • Persistent    │
└─────────────────┘   └─────────────────┘
```

### 7. Python API Integration

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              PYTHON API INTEGRATION                                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ Python API      │
│ Interface       │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐   ┌─────────┐
│Quick    │   │Full     │
│Setup    │   │Control  │
└─────────┘   └─────────┘
    │           │
    ▼           ▼
┌─────────────────┐   ┌─────────────────┐
│ quick_setup()   │   │ GraphRAGProcessor│
│ quick_process() │   │ • validate_env  │
│ validate_sys()  │   │ • discover_docs │
│ get_status()    │   │ • process_docs  │
└─────────┬───────┘   └─────────┬───────┘
          │                     │
          ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Convenience     │   │ Enhanced        │
│ Functions       │   │ Architecture    │
│ • One-line      │   │ • Full Control  │
│ • Common Tasks  │   │ • Configuration │
│ • Validation    │   │ • Error Handle  │
└─────────────────┘   └─────────────────┘
```

## Component Communication Patterns

### 8. Data Flow Patterns

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW PATTERNS                                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ Input Data      │
│ • PDFs          │
│ • Queries       │
│ • Commands      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Enhanced        │───▶│ Sequential      │
│ Document        │    │ Processing      │
│ Processor       │    │ • Step-by-Step  │
│ • Validation    │    │ • Context Flow  │
│ • Preparation   │    │ • State Track   │
└─────────────────┘    └─────────┬───────┘
                                 │
                                 ▼
┌─────────────────┐    ┌─────────────────┐
│ Persistent      │◄───│ Analysis        │
│ Storage         │    │ Results         │
│ • ChromaDB      │    │ • Entities      │
│ • Neo4j         │    │ • Citations     │
│ • File System   │    │ • Relations     │
└─────────┬───────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ MCP Tools       │───▶│ User Interface  │
│ • Chat          │    │ • Claude        │
│ • Literature    │    │ • CLI           │
│ • Core          │    │ • Python API    │
└─────────────────┘    └─────────────────┘
```

### 9. Error Handling and Recovery

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ERROR HANDLING PATTERNS                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ Error Detection │
│ • Validation    │
│ • Monitoring    │
│ • Health Check  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Error Types     │───▶│ Recovery        │
│ • Validation    │    │ Strategy        │
│ • Processing    │    │ • Retry         │
│ • Configuration │    │ • Fallback      │
│ • Network       │    │ • Graceful      │
└─────────────────┘    └─────────┬───────┘
                                 │
                                 ▼
┌─────────────────┐    ┌─────────────────┐
│ User            │◄───│ Recovery        │
│ Feedback        │    │ Execution       │
│ • Clear Msg     │    │ • Cleanup       │
│ • Suggestions   │    │ • Restore       │
│ • Alternatives  │    │ • Notify        │
└─────────────────┘    └─────────────────┘
```

### 10. Configuration Management

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURATION MANAGEMENT                                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ GraphRAGConfig  │
│ (Simplified)    │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐   ┌─────────┐
│ Model   │   │Storage  │
│ Config  │   │Config   │
└─────────┘   └─────────┘
    │           │
    ▼           ▼
┌─────────────────┐   ┌─────────────────┐
│ • llm_model     │   │ • chromadb      │
│ • embed_model   │   │ • neo4j         │
│ • temperature   │   │ • persistence   │
│ • max_tokens    │   │ • connections   │
└─────────┬───────┘   └─────────┬───────┘
          │                     │
          ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Processing      │   │ Environment     │
│ Config          │   │ Variables       │
│ • chunk_size    │   │ • Override      │
│ • overlap       │   │ • Validation    │
│ • citation_style│   │ • Defaults      │
└─────────────────┘   └─────────────────┘
```

This simplified component interaction model demonstrates how the GraphRAG MCP Toolkit achieves sophisticated document analysis through streamlined component collaboration while maintaining robustness and user-friendly interfaces. The enhanced sequential processing architecture ensures accuracy and consistency across all operations.
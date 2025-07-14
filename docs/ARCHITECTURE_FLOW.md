# GraphRAG MCP Architecture Flow

## System Overview
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              GraphRAG MCP Toolkit Architecture                         │
│                          Research Foundation → Production Platform                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Core Data Flow Architecture

### 1. Document Ingestion Pipeline
```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Input │───▶│ PyPDFLoader     │───▶│ Text Extraction │───▶│ Content Chunks  │
│             │    │ (LangChain)     │    │ & Preprocessing │    │ (1000 chars)    │
└─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Dual Processing Pathways

#### LEGACY: NetworkX Analysis Flow (Deprecated - Use Graphiti)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Content Chunks  │───▶│ SimplePaperRAG  │───▶│ UnifiedPaperChat│───▶│ User Interface  │
│                 │    │ • Embeddings    │    │ • Query Router  │    │ • Jupyter       │
│                 │    │ • Vector Search │    │ • Mode Select   │    │ • CLI           │
│                 │    │ • Q&A System    │    │ • Response Gen  │    │ • MCP Server    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲                       ▲
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │SimpleKnowledgeG │    │LangChainGraphRAG│
                       │ • 8 Categories  │    │ • Vector+Graph  │
                       │ • NetworkX (dep)│    │ • ChromaDB Meta │
                       │ • Relationships │    │ • Cross-Paper   │
                       └─────────────────┘    └─────────────────┘
```

#### NEW: Graphiti Real-time Analysis Flow
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Content Chunks  │───▶│GraphitiKnowledge│───▶│ GraphitiMCP     │───▶│ Real-time UI    │
│                 │    │ Graph Engine    │    │ Server          │    │ • Jupyter       │
│                 │    │ • AI Extraction │    │ • Template Sys  │    │ • CLI           │
│                 │    │ • Neo4j Backend │    │ • Real-time     │    │ • MCP Tools     │
│                 │    │ • Ollama LLM    │    │ • Hybrid Search │    │ • Visualization │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲                       ▲
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Neo4j Database  │    │ yFiles Visualiz │
                       │ • Persistent    │    │ • Professional  │
                       │ • Real-time     │    │ • Interactive   │
                       │ • Scalable      │    │ • Export Ready  │
                       └─────────────────┘    └─────────────────┘
```

## Component Interaction Matrix

### 3. Core Components & Their Interactions

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              FOUNDATION LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ SimplePaperRAG  │  │DocumentProcessor│  │ Ollama Service  │  │ ChromaDB Store  │   │
│  │ src/simple_     │  │ src/document_   │  │ llama3.1:8b    │  │ Vector Storage  │   │
│  │ paper_rag.py    │  │ processor.py    │  │ nomic-embed     │  │ Metadata Index  │   │
│  │                 │  │                 │  │                 │  │                 │   │
│  │ • PDF Loading   │  │ • Domain Agnostic│ │ • Local LLM     │  │ • Embeddings    │   │
│  │ • Text Chunks   │  │ • Entity Config │  │ • Privacy First │  │ • Similarity    │   │
│  │ • Embeddings    │  │ • Pydantic Mod  │  │ • HTTP API      │  │ • Persistence   │   │
│  │ • Q&A System    │  │ • Extensible    │  │ • Health Check  │  │ • Collections   │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│           │                     │                     │                     │          │
│           └─────────────────────┼─────────────────────┼─────────────────────┘          │
│                                 │                     │                                │
└─────────────────────────────────┼─────────────────────┼────────────────────────────────┘
                                  │                     │
┌─────────────────────────────────┼─────────────────────┼────────────────────────────────┐
│                                 │    GRAPH LAYER      │                                │
├─────────────────────────────────┼─────────────────────┼────────────────────────────────┤
│                                 │                     │                                │
│  ┌─────────────────┐  ┌─────────▼───────┐  ┌─────────▼───────┐  ┌─────────────────┐   │
│  │SimpleKnowledgeG │  │EnhancedKnowledgeG│ │CitationTracker │  │ Graphiti Graph  │   │
│  │ src/simple_     │  │ src/enhanced_   │  │ src/citation_   │  │ Graph Storage   │   │
│  │ knowledge_      │  │ knowledge_      │  │ tracker.py      │  │ Node/Edge Attrs │   │
│  │ graph.py        │  │ graph.py        │  │                 │  │                 │   │
│  │                 │  │                 │  │                 │  │                 │   │
│  │ • 8 Categories  │  │ • 20+ Categories│  │ • 4 Cite Formats│  │ • Relationships │   │
│  │ • Basic Extract │  │ • Section Based │  │ • Location Map  │  │ • Centrality    │   │
│  │ • Relationships │  │ • Multi-Pass    │  │ • Context Track │  │ • Traversal     │   │
│  │ • Graphiti      │  │ • Importance    │  │ • Reference Link│  │ • Visualization │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│           │                     │                     │                     │          │
│           └─────────────────────┼─────────────────────┼─────────────────────┘          │
│                                 │                     │                                │
└─────────────────────────────────┼─────────────────────┼────────────────────────────────┘
                                  │                     │
┌─────────────────────────────────┼─────────────────────┼────────────────────────────────┐
│                                 │  INTEGRATION LAYER  │                                │
├─────────────────────────────────┼─────────────────────┼────────────────────────────────┤
│                                 │                     │                                │
│  ┌─────────────────┐  ┌─────────▼───────┐  ┌─────────▼───────┐  ┌─────────────────┐   │
│  │UnifiedPaperChat │  │LangChainGraphRAG│  │ ChatEngine      │  │AdvancedAnalyzer │   │
│  │ src/unified_    │  │ src/langchain_  │  │ graphrag_mcp/   │  │ graphrag_mcp/   │   │
│  │ paper_chat.py   │  │ graph_rag.py    │  │ core/chat_      │  │ core/analyzer.py│   │
│  │                 │  │                 │  │ engine.py       │  │                 │   │
│  │ • Query Router  │  │ • Vector+Graph  │  │ • Domain Agnostic│ │ • Corpus Ready  │   │
│  │ • Mode Select   │  │ • ChromaDB Meta │  │ • Structured    │  │ • Multi-Domain  │   │
│  │ • Response Gen  │  │ • Cross-Paper   │  │ • Pydantic      │  │ • Configurable  │   │
│  │ • Entity Explore│  │ • Professional  │  │ • Extensible    │  │ • Error Handle  │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│           │                     │                     │                     │          │
│           └─────────────────────┼─────────────────────┼─────────────────────┘          │
│                                 │                     │                                │
└─────────────────────────────────┼─────────────────────┼────────────────────────────────┘
                                  │                     │
┌─────────────────────────────────┼─────────────────────┼────────────────────────────────┐
│                                 │  USER INTERFACE     │                                │
├─────────────────────────────────┼─────────────────────┼────────────────────────────────┤
│                                 │                     │                                │
│  ┌─────────────────┐  ┌─────────▼───────┐  ┌─────────▼───────┐  ┌─────────────────┐   │
│  │Jupyter Notebooks│  │ CLI Interface   │  │ MCP Server      │  │ Tutorial System │   │
│  │ notebooks/      │  │ graphrag_mcp/   │  │ graphrag_mcp/   │  │ tutorial/       │   │
│  │ Simple_Paper_   │  │ cli/main.py     │  │ mcp/server_     │  │ 01-05.ipynb     │   │
│  │ RAG_Chat.ipynb  │  │                 │  │ generator.py    │  │                 │   │
│  │                 │  │                 │  │                 │  │                 │   │
│  │ • Interactive   │  │ • Typer CLI     │  │ • FastMCP       │  │ • Learning Path │   │
│  │ • Rich Display  │  │ • Project Mgmt  │  │ • Claude Desktop│  │ • Step-by-Step  │   │
│  │ • Entity Explore│  │ • Rich Console  │  │ • Template Sys  │  │ • Comprehensive │   │
│  │ • Visualization │  │ • Health Check  │  │ • Universal     │  │ • Hands-On      │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Query Processing Flow

### 4. Intelligent Query Routing System

```
┌─────────────────┐
│ User Question   │
│ "What are the   │
│ main findings?" │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Query Analysis  │
│ • Keyword Score │
│ • Intent Detect │
│ • Mode Select   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Mode Decision   │
│ RAG │ Graph │Both│
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐   ┌─────────────┐
│RAG Mode │   │ Graph Mode  │
│         │   │             │
│Vector   │   │Entity-Based │
│Search   │   │Retrieval    │
│         │   │             │
│Context  │   │Relationship │
│Retrieval│   │Exploration  │
└─────────┘   └─────────────┘
    │           │
    └─────┬─────┘
          │
          ▼
┌─────────────────┐
│ Response Fusion │
│ • Context Merge │
│ • Entity Enrich │
│ • Citation Add  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Enhanced Answer │
│ • RAG Context   │
│ • Graph Insights│
│ • Citations     │
└─────────────────┘
```

## Data Storage Architecture

### 5. Multi-Modal Storage System

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                STORAGE LAYER                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ ChromaDB        │  │ Neo4j Database  │  │ File System     │  │ Memory Cache    │   │
│  │ Vector Store    │  │ Graph Store     │  │ Project Store   │  │ Runtime Store   │   │
│  │ (Legacy)        │  │ (NEW PRIMARY)   │  │                 │  │                 │   │
│  │ • Embeddings    │  │ • Nodes/Edges   │  │ • ~/.graphrag-  │  │ • Chat History  │   │
│  │ • Metadata      │  │ • Real-time     │  │   mcp/projects/ │  │ • Loaded Docs   │   │
│  │ • Collections   │  │ • Persistent    │  │ • Documents/    │  │ • Entity Cache  │   │
│  │ • Similarity    │  │ • Scalable      │  │ • Processed/    │  │ • Embeddings    │   │
│  │ • Persistence   │  │ • Visualization │  │ • Config.json   │  │ • Graph Objects │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Template System Architecture

### 6. Domain Extension Framework

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              TEMPLATE SYSTEM                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│           ┌─────────────────┐              ┌─────────────────┐                         │
│           │ BaseTemplate    │              │TemplateManager │                         │
│           │ (Abstract)      │◄─────────────┤ Orchestrator    │                         │
│           └─────────────────┘              └─────────────────┘                         │
│                    ▲                                                                   │
│                    │                                                                   │
│    ┌───────────────┼───────────────┐                                                   │
│    │               │               │                                                   │
│    ▼               ▼               ▼                                                   │
│ ┌─────────┐  ┌─────────┐  ┌─────────────┐                                             │
│ │Academic │  │Business │  │ Future      │                                             │
│ │Template │  │Template │  │ Templates   │                                             │
│ │         │  │         │  │             │                                             │
│ │• 20+ Ent│  │• KPIs   │  │ • Medical   │                                             │
│ │• Citation│  │• Metrics│  │ • Legal     │                                             │
│ │• Methods │  │• Reports│  │ • Technical │                                             │
│ │• Papers  │  │• Analysis│  │ • Custom    │                                             │
│ └─────────┘  └─────────┘  └─────────────┘                                             │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Complete System Flow

### 7. End-to-End Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE SYSTEM FLOW                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

INPUT STAGE
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  PDF Files  │───▶│ User Query  │───▶│ Interface   │
│             │    │             │    │ Selection   │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
PROCESSING STAGE
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│ INTERACTIVE PATH                          CORPUS PATH                                   │
│ ┌─────────────┐                          ┌─────────────────┐                           │
│ │ Quick       │                          │ Enhanced        │                           │
│ │ Analysis    │                          │ Analysis        │                           │
│ │             │                          │                 │                           │
│ │ SimplePaper │                          │ EnhancedPaper   │                           │
│ │ RAG         │                          │ Analyzer        │                           │
│ │     +       │                          │        +        │                           │
│ │ SimpleKnowl │                          │ Citation        │                           │
│ │ edgeGraph   │                          │ Tracker         │                           │
│ │     ▼       │                          │        ▼        │                           │
│ │ Unified     │                          │ Corpus          │                           │
│ │ PaperChat   │                          │ Document        │                           │
│ └─────────────┘                          └─────────────────┘                           │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
OUTPUT STAGE
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│ │ Jupyter     │  │ CLI         │  │ MCP Server  │  │ Export      │                    │
│ │ Interface   │  │ Interface   │  │ Integration │  │ Formats     │                    │
│ │             │  │             │  │             │  │             │                    │
│ │ • Chat      │  │ • Commands  │  │ • Claude    │  │ • GraphML   │                    │
│ │ • Entities  │  │ • Projects  │  │ • STDIO     │  │ • JSON      │                    │
│ │ • Graphs    │  │ • Status    │  │ • Templates │  │ • Cytoscape │                    │
│ │ • Viz       │  │ • Health    │  │ • Universal │  │ • Citations │                    │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘                    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Performance & Scalability Characteristics

### 8. System Performance Profile

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           PERFORMANCE METRICS                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│ PROCESSING TIMES:                    RESOURCE USAGE:                                   │
│ ┌─────────────────────────────────┐   ┌─────────────────────────────────┐              │
│ │ Basic Analysis:   30-60 seconds │   │ Model Storage:       ~5GB      │              │
│ │ Enhanced Analysis: 10-60 minutes│   │ Per Paper:          ~10-50MB   │              │
│ │ Query Response:    1-3 seconds  │   │ Memory Usage:       ~1-2GB     │              │
│ │ Graph Generation:  5-10 seconds │   │ CPU Usage:          Single Core │              │
│ └─────────────────────────────────┘   └─────────────────────────────────┘              │
│                                                                                         │
│ SCALABILITY LIMITS:                  ACCURACY METRICS:                                 │
│ ┌─────────────────────────────────┐   ┌─────────────────────────────────┐              │
│ │ Papers per Project:     ~100    │   │ Citation Extraction:    >90%    │              │
│ │ Concurrent Users:       1       │   │ Entity Extraction:      >85%    │              │
│ │ Projects per System:    Multiple│   │ Relationship Mapping:   >80%    │              │
│ │ Deployment:             Local   │   │ Query Relevance:        >90%    │              │
│ └─────────────────────────────────┘   └─────────────────────────────────┘              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Future Evolution Path

### 9. Roadmap Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              EVOLUTION ROADMAP                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│ PHASE 1: RESEARCH FOUNDATION (COMPLETED)                                               │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ • Academic paper analysis                                                           │ │
│ │ • Local privacy-first processing                                                    │ │
│ │ • Jupyter notebook interface                                                        │ │
│ │ • Basic MCP server integration                                                      │ │
│ │ • Graphiti knowledge graphs (NetworkX legacy support)                          │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                         │
│ PHASE 2: GRAPHITI MIGRATION (COMPLETED)                                                │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ • Graphiti real-time knowledge graphs                                              │ │
│ │ • Neo4j persistent backend                                                         │ │
│ │ • Advanced MCP server with templates                                               │ │
│ │ • Hybrid visualization (Graphiti + yFiles)                                         │ │
│ │ • Professional CLI interface                                                       │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                         │
│ PHASE 3: UNIVERSAL PLATFORM (CURRENT TARGET)                                           │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ • Multi-domain templates                                                            │ │
│ │ • Enterprise deployment options                                                     │ │
│ │ • Advanced notebook interfaces                                                      │ │
│ │ • Multi-user collaboration                                                          │ │
│ │ • Cloud-native architecture                                                         │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

This architectural flow demonstrates the sophisticated design of a system that successfully bridges research-grade capabilities with production-ready architecture, maintaining privacy and extensibility while providing powerful document analysis and knowledge extraction capabilities.
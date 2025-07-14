# GraphRAG MCP Architecture Flow

## System Overview - Dual-Mode Architecture
```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              GraphRAG MCP Toolkit Architecture                         │
│               Dual-Mode: Conversational Research + Formal Literature Review            │
│                    Graphiti-Powered Persistent Knowledge Graphs                       │
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

### 2. Dual-Mode Processing Architecture

#### Phase 1: Document Processing → Graphiti Knowledge Graph
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Content Chunks  │───▶│ Enhanced        │───▶│ Graphiti        │───▶│ Persistent      │
│                 │    │ Analyzer        │    │ Engine          │    │ Knowledge Graph │
│                 │    │ • 20+ Entities  │    │ • AI Extraction │    │ • Neo4j Storage │
│                 │    │ • Citation Track│    │ • Real-time     │    │ • Project NS    │
│                 │    │ • Multi-pass    │    │ • Relationships │    │ • Async Ops     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲                       ▲
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Citation        │    │ Ollama          │
                       │ Manager         │    │ Integration     │
                       │ • 4 Styles      │    │ • llama3.1:8b   │
                       │ • Usage Track   │    │ • nomic-embed   │
                       │ • Bibliography  │    │ • Local Privacy │
                       └─────────────────┘    └─────────────────┘
```

#### Phase 2: MCP Server → Dual-Mode Research Interface
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Neo4j Knowledge │───▶│ GraphitiMCP     │───▶│ Dual-Mode       │───▶│ Research        │
│ Graph           │    │ Server          │    │ Tools           │    │ Interfaces      │
│ • Persistent    │    │ • FastMCP       │    │ • Chat Tools    │    │ • Claude Desktop│
│ • Project-aware │    │ • Real-time     │    │ • Literature    │    │ • Jupyter       │
│ • Scalable      │    │ • Template Sys  │    │ • Citation Mgmt │    │ • CLI Tools     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲                       ▲
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Chat Tools      │    │ Literature Tools│
                       │ • ask_knowledge │    │ • gather_sources│
                       │ • explore_topic │    │ • get_facts_cite│
                       │ • find_connect  │    │ • verify_claims │
                       │ • what_know     │    │ • track_citations│
                       └─────────────────┘    └─────────────────┘
```

#### Legacy Support (Backwards Compatibility)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ UniversalMCP    │───▶│ In-Memory       │───▶│ Development     │───▶│ Testing         │
│ Server          │    │ Processing      │    │ Interface       │    │ Environment     │
│ • serve-universal│    │ • ChromaDB      │    │ • Quick Setup   │    │ • No Neo4j      │
│ • Template Sys  │    │ • JSON Storage  │    │ • No Persistence│    │ • Rapid Proto   │
│ • FastMCP       │    │ • NetworkX      │    │ • Memory Only   │    │ • Legacy Tools  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
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
│  │ Neo4j/Graphiti  │  │ Citation        │  │ File System     │  │ MCP Server      │   │
│  │ Knowledge Graph │  │ Manager         │  │ Project Store   │  │ Runtime State   │   │
│  │ (PRIMARY)       │  │ (NEW)           │  │                 │  │                 │   │
│  │ • Nodes/Edges   │  │ • 4 Styles      │  │ • ~/.graphrag-  │  │ • Chat Tools    │   │
│  │ • Real-time     │  │ • Usage Track   │  │   mcp/projects/ │  │ • Literature    │   │
│  │ • Persistent    │  │ • Bibliography  │  │ • Documents/    │  │ • Query Engine  │   │
│  │ • Project NS    │  │ • Validation    │  │ • Processed/    │  │ • Session State │   │
│  │ • AI-optimized  │  │ • Location Map  │  │ • Config.json   │  │ • Tool Registry │   │
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

### 7. Complete Dual-Mode System Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        DUAL-MODE GRAPHRAG MCP SYSTEM FLOW                             │
└─────────────────────────────────────────────────────────────────────────────────────────┘

PHASE 1: KNOWLEDGE GRAPH CREATION
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  PDF Files  │───▶│ Enhanced    │───▶│ Graphiti    │───▶│ Neo4j       │
│             │    │ Analyzer    │    │ Engine      │    │ Database    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                │
       ▼                   ▼                   ▼                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ CLI Command │    │ Citation    │    │ Real-time   │    │ Persistent  │
│ process     │    │ Tracking    │    │ Knowledge   │    │ Project     │
│ my-project  │    │ 4 Styles    │    │ Graph       │    │ Storage     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

PHASE 2: MCP SERVER DEPLOYMENT
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Neo4j Graph │───▶│ GraphitiMCP │───▶│ Dual-Mode   │───▶│ Research    │
│ (Existing)  │    │ Server      │    │ Interface   │    │ Assistant   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                │
       ▼                   ▼                   ▼                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ CLI Command │    │ FastMCP     │    │ Chat +      │    │ Claude      │
│ serve       │    │ Protocol    │    │ Literature  │    │ Desktop     │
│ my-project  │    │ Server      │    │ Tools       │    │ Integration │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

DUAL-MODE RESEARCH INTERFACE
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│ CONVERSATIONAL MODE                       LITERATURE REVIEW MODE                       │
│ ┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐      │
│ │ Chat Tools                          │  │ Literature Tools                    │      │
│ │ • ask_knowledge_graph              │  │ • gather_sources_for_topic         │      │
│ │ • explore_topic                    │  │ • get_facts_with_citations         │      │
│ │ • find_connections                 │  │ • verify_claim_with_sources        │      │
│ │ • what_do_we_know_about           │  │ • track_citations_used             │      │
│ │                                    │  │ • generate_bibliography            │      │
│ │ Focus: Discovery & Understanding   │  │ Focus: Formal Writing & Citations  │      │
│ └─────────────────────────────────────┘  └─────────────────────────────────────┘      │
│                                     │                        │                        │
│                                     ▼                        ▼                        │
│                           ┌─────────────────────────────────────┐                     │
│                           │ Shared Graphiti Knowledge Graph    │                     │
│                           │ • Project-namespaced storage       │                     │
│                           │ • Real-time relationship discovery │                     │
│                           │ • Citation-aware responses         │                     │
│                           │ • Persistent across sessions       │                     │
│                           └─────────────────────────────────────┘                     │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

OUTPUT CAPABILITIES
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│ │ Research    │  │ Citation    │  │ Knowledge   │  │ Export      │                    │
│ │ Insights    │  │ Management  │  │ Discovery   │  │ Formats     │                    │
│ │             │  │             │  │             │  │             │                    │
│ │ • Gap ID    │  │ • APA Style │  │ • Entity    │  │ • GraphML   │                    │
│ │ • Synthesis │  │ • IEEE      │  │ • Relations │  │ • JSON      │                    │
│ │ • Trends    │  │ • Nature    │  │ • Concepts  │  │ • Citations │                    │
│ │ • Evolution │  │ • MLA       │  │ • Networks  │  │ • Reports   │                    │
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
# Simple Knowledge Graph MCP

Turn your documents into a queryable knowledge graph using any MCP-compatible LLM client with zero API setup.

## What This Does

This is a **Model Context Protocol (MCP) server** that transforms documents into an intelligent, searchable knowledge base. It provides any MCP-compatible client (Claude Desktop, ChatGPT Desktop, etc.) with 5 specialized tools to extract, store, and query information from your documents using a dual-database system.

### Core Architecture
- **Neo4j Graph Database**: Stores entities (people, concepts, technologies) and their relationships
- **ChromaDB Vector Database**: Stores text chunks with local embeddings for semantic search
- **FastMCP Server**: Orchestrates 5 tools that any MCP client can use
- **Local Processing**: No external APIs - everything runs on your machine

## MCP Architecture Flow

```mermaid
flowchart TB
    subgraph clients["🖥️ LLM Clients"]
        A[Claude Desktop]
        B[ChatGPT Desktop] 
        C[Other MCP Clients]
    end
    
    subgraph mcp["📡 MCP Server"]
        E[FastMCP Server]
    end
    
    subgraph storage_flow["📥 STORAGE WORKFLOW"]
        direction TB
        F[store_entities<br/>Extract & Store Entities]
        G[store_vectors<br/>Store Vector Content]
        
        subgraph entity_pipeline["Entity Pipeline"]
            F1[Entities + Relationships] --> F2[Neo4j Graph Store]
        end
        
        subgraph text_pipeline["Text Pipeline"] 
            G1[Text Chunks] --> G2[Local Embeddings] --> G3[ChromaDB Vector Store]
        end
        
        F --> F1
        G --> G1
    end
    
    subgraph databases["🗄️ Knowledge Stores"]
        direction LR
        NEO@{shape: database, label: "Neo4j<br/>Entity Graph<br/>Relationships"}
        CHROMA@{shape: database, label: "ChromaDB<br/>Vector Store<br/>Text + Embeddings"}
    end
    
    subgraph query_flow["🔍 QUERYING WORKFLOW"]
        direction TB
        H[query_knowledge_graph<br/>Search Both Stores]
        I[generate_literature_review<br/>Format Results]
        
        subgraph graphrag["GraphRAG Pipeline"]
            H1[Graph Traversal<br/>Neo4j] 
            H2[Vector Search<br/>ChromaDB]
            H3[Combine Results]
        end
        
        H --> H1
        H --> H2
        H1 --> H3
        H2 --> H3
        H3 --> I
    end
    
    %% Client connections
    A --> E
    B --> E  
    C --> E
    
    %% Storage flow
    E --> F
    E --> G
    F2 --> NEO
    G3 --> CHROMA
    
    %% Query flow
    E --> H
    E --> I
    NEO --> H1
    CHROMA --> H2
    
    %% Styling
    classDef storageBox fill:#e1f5fe
    classDef queryBox fill:#f3e5f5
    classDef dbBox fill:#fff3e0
    
    class storage_flow,entity_pipeline,text_pipeline storageBox
    class query_flow,graphrag queryBox
    class databases,NEO,CHROMA dbBox
```

### How Data Flows Through the System

**📥 Storage Workflow:**
1. **LLM extracts entities** → `store_entities` → Neo4j Graph (entities + relationships)
2. **LLM extracts content** → `store_vectors` → Local embeddings → ChromaDB Vector Store

**🔍 Query Workflow (GraphRAG):**
1. **LLM asks question** → `query_knowledge_graph` 
2. **Parallel search**: Neo4j graph traversal + ChromaDB vector similarity
3. **Combine results** → Return comprehensive answer with citations
4. **Optional**: `generate_literature_review` formats results for academic writing

**🗄️ Dual Knowledge Stores:**
- **Neo4j**: Entities, relationships, graph connections
- **ChromaDB**: Text chunks, embeddings, semantic search

## Step-by-Step: How It Works

### 1. Document Upload & Processing
```
You → Upload PDFs to LLM Client (Claude Desktop, ChatGPT, etc.)
LLM → Uses MCP tools to extract structured data
```

**What the LLM extracts:**
- **Entities**: People, concepts, technologies, organizations with properties
- **Relationships**: How entities connect (e.g., "Hinton developed backpropagation")
- **Text chunks**: Important passages with full citation information
- **Metadata**: Document provenance, confidence scores, context

### 2. Intelligent Storage
```
Entities + Relationships → Neo4j Graph Database
Text + Citations → ChromaDB with local embeddings
```

**Example data stored:**
```json
// Neo4j Entity
{
  "id": "hinton_2006",
  "name": "Geoffrey Hinton", 
  "type": "person",
  "properties": {"affiliation": "University of Toronto"},
  "confidence": 0.95
}

// Neo4j Relationship  
{
  "source": "hinton_2006",
  "target": "backprop_concept",
  "type": "developed",
  "context": "Hinton pioneered backpropagation algorithms in the 1980s"
}

// ChromaDB Text Chunk
{
  "text": "Deep learning networks require careful initialization...",
  "embedding": [0.1, -0.3, 0.8, ...],
  "citation": {"authors": ["Hinton, G."], "year": 2006, "title": "..."}
}
```

### 3. Intelligent Querying
```
You → Ask LLM questions in natural language
LLM → Uses MCP tools to search both databases simultaneously
LLM → Returns comprehensive answers with citations
```

**Query types supported:**
- **Entity searches**: "Who are the key researchers in transformer architectures?"
- **Relationship mapping**: "How do GANs relate to diffusion models?"
- **Semantic searches**: "What papers discuss attention mechanisms?" (finds content even with different terminology)
- **Cross-document analysis**: "What are the contradictions between these papers?"
- **Literature reviews**: "Generate a review of deep learning optimization methods"

### 4. Knowledge Graph Growth
```
More documents → Richer connections → Smarter answers
```

**As you add documents:**
- **Cross-references emerge**: System identifies when papers cite each other
- **Research networks form**: Maps collaborations between authors
- **Concept evolution tracked**: Shows how ideas develop over time
- **Knowledge gaps identified**: Highlights areas needing more research

## The 5 MCP Tools Available to Claude

1. **`store_entities`** - Extract and store entities/relationships in Neo4j graph database
2. **`store_vectors`** - Store any content as vectors in ChromaDB (entities, text chunks, concepts, etc.)
3. **`query_knowledge_graph`** - Search both databases for comprehensive answers
4. **`generate_literature_review`** - Format results with proper citations (APA, IEEE, Nature, MLA)
5. **`clear_knowledge_graph`** - Reset all data for fresh start

## Real-World Example Workflow

### Scenario: Building an AI Research Knowledge Base

**Step 1: Batch Upload**
```bash
# Upload 20 AI research papers to Claude Desktop project
- attention_is_all_you_need.pdf
- bert_paper.pdf  
- gpt3_paper.pdf
- ... (17 more papers)
```

**Step 2: Knowledge Extraction**
```
You: "Extract entities and relationships from all these AI papers"

Claude: *Uses store_entities tool*
- Extracts 500+ entities (researchers, concepts, architectures)
- Maps 1000+ relationships between them
- Stores everything in Neo4j with confidence scores

You: "Store the key text passages and citations"

Claude: *Uses store_vectors tool*  
- Stores 2000+ text chunks with embeddings
- Preserves full bibliographic information
- Enables semantic search across all content
```

**Step 3: Intelligent Analysis**
```
You: "What are the main innovations in transformer architectures?"

Claude: *Uses query_knowledge_graph tool*
- Searches Neo4j for transformer-related entities
- Finds semantic matches in ChromaDB text
- Returns: Attention mechanisms, positional encoding, multi-head attention
- Includes citations from Vaswani et al., Devlin et al., Radford et al.

You: "Generate a literature review on attention mechanisms"

Claude: *Uses generate_literature_review tool*
- Organizes findings by themes
- Formats with proper academic citations
- Includes summary statistics and research trends
```

**Step 4: Advanced Queries**
```
You: "Which researchers have collaborated across multiple papers?"

Claude: Maps collaboration networks from stored relationships

You: "What are the contradictions between different optimization approaches?"

Claude: Finds conflicting claims across papers using semantic search

You: "Show me the evolution of language model architectures from 2017-2023"

Claude: Traces concept development through temporal analysis
```

## Key Benefits

### For Researchers
- **Literature review automation**: Generate comprehensive reviews with proper citations
- **Cross-paper analysis**: Find connections your manual reading might miss
- **Research gap identification**: Discover unexplored areas in your field
- **Collaboration mapping**: Identify potential research partners

### For Students  
- **Study aid creation**: Build comprehensive knowledge bases from course materials
- **Citation management**: Automatic extraction and formatting of references
- **Concept mapping**: Understand how ideas connect across different sources
- **Exam preparation**: Query your knowledge base for comprehensive review

### For Professionals
- **Industry analysis**: Track trends across company reports and market research
- **Competitive intelligence**: Map relationships between companies and technologies
- **Knowledge management**: Build searchable repositories of internal documents
- **Decision support**: Query historical data for informed decision-making

## Technical Architecture

### Storage Layer (`src/storage/`)
```
storage/
├── neo4j/           # Graph database operations
│   ├── storage.py   # Entity and relationship persistence
│   └── query.py     # Graph traversal and relationship mapping
├── chroma/          # Vector database operations  
│   ├── storage.py   # Text storage with local embeddings
│   └── query.py     # Semantic search and similarity matching
└── embedding/       # Local embedding generation
    └── service.py   # sentence-transformers integration (no external APIs)
```

### Tools Layer (`src/tools/`)
```
tools/
├── storage/         # Data persistence tools
│   ├── entity_storage.py      # store_entities MCP tool
│   ├── text_storage.py        # store_vectors MCP tool
│   └── database_management.py # clear_knowledge_graph MCP tool
└── query/           # Data retrieval tools
    ├── knowledge_search.py     # query_knowledge_graph MCP tool
    └── literature_generation.py # generate_literature_review MCP tool
```

### Server Layer (`src/server/`)
- **`main.py`** - FastMCP server that registers all 5 tools and handles Claude Desktop communication

## Local-First Privacy Design

- **No external API dependencies** - All LLM processing via Claude Desktop
- **Local embeddings** - Uses sentence-transformers for complete privacy
- **Local databases** - Neo4j via Docker, ChromaDB as local files  
- **Zero API keys required** - Complete offline operation capability
- **Your data stays yours** - Everything processed and stored locally

## Quick Start

### Prerequisites
- Python 3.11+ (required for FastMCP)
- Docker (for Neo4j database)
- MCP-compatible LLM client (Claude Desktop, ChatGPT Desktop, etc.)

### Installation
```bash
# 1. Clone repository
git clone <repository-url>
cd simple-knowledge-graph-mcp

# 2. Complete setup (installs UV, Python 3.11, dependencies)
./scripts/setup.sh

# 3. Start Neo4j database
./scripts/start_services.sh

# 4. Verify everything works
./scripts/check_status.sh
```

### Configure Your MCP Client

#### For Claude Desktop & ChatGPT Desktop (Easy GUI Setup)
```bash
# Start HTTP server
./scripts/start_http_server.sh
```

Then in Claude Desktop or ChatGPT Desktop:
- Settings → Connectors → Add custom connector
- **Name**: `Knowledge Graph`
- **URL**: `http://localhost:3001`
- Click "Add" and restart the application

#### For Advanced Users (JSON Configuration)
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "uv",
      "args": ["run", "python", "/full/path/to/project/src/server/main.py"]
    }
  }
}
```

#### For Other MCP Clients  
Both Claude Desktop and ChatGPT Desktop support MCP connectors via GUI setup. Other MCP-compatible clients should work similarly with the HTTP server URL `http://localhost:3001`.

### Start Using
```bash
# Option 1: HTTP server (for GUI setup)
./scripts/start_http_server.sh

# Option 2: STDIO server (for JSON setup)  
./scripts/start_mcp_server.sh

# In your MCP client (Claude Desktop, ChatGPT Desktop, etc.):
# 1. Upload PDFs to project
# 2. "Extract entities and relationships from these documents"  
# 3. "Store the key text passages"
# 4. "What does my knowledge graph say about [topic]?"
```

That's it! Your personal research assistant is ready to help you build and query knowledge graphs from any collection of documents.

## What Makes This Different

Unlike traditional document management or search tools, this system:

1. **Understands relationships** - Maps how concepts, people, and ideas connect
2. **Grows smarter over time** - Each document enhances the knowledge graph
3. **Speaks your language** - Natural language queries, no complex syntax
4. **Preserves context** - Maintains full provenance and citation information
5. **Works offline** - Complete privacy with local processing
6. **Integrates with Claude** - Seamless experience within Claude Desktop

Perfect for anyone who works with large collections of documents and wants to unlock the hidden connections within their knowledge base.
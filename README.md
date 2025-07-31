# GROBID-Powered Academic Knowledge Graph MCP

Transform research papers into intelligent, queryable knowledge graphs using Claude Desktop with zero API costs and superior academic understanding.

## What This Does

This is a **GROBID-powered Model Context Protocol (MCP) server** specifically designed for academic research. It transforms research papers into an intelligent, searchable knowledge base with superior citation network analysis. It provides Claude Desktop with 5 specialized tools to extract, store, and query academic information using advanced academic document processing.

### Core Architecture
- **GROBID Academic Parser**: Self-hosted service providing 87-90% F1-score accuracy for research papers
- **Neo4j Unified Database**: Stores entities, relationships, and vector embeddings in one database
- **FastMCP Server**: Orchestrates 5 academic-focused tools for Claude Desktop
- **Zero API Costs**: Self-hosted GROBID eliminates expensive PDF processing fees
- **Academic Focus**: Built specifically for research papers, not generic documents

## Academic Processing Architecture

```mermaid
flowchart TB
    subgraph clients["🖥️ LLM Clients"]
        A[Claude Desktop]
        B[Other MCP Clients]
    end
    
    subgraph services["🐳 Academic Services"]
        GROBID[GROBID Docker<br/>Academic PDF Parser<br/>87-90% F1-Score]
    end
    
    subgraph mcp["📡 MCP Server"]
        E[FastMCP Server<br/>Academic Tools]
    end
    
    subgraph academic_flow["📚 ACADEMIC PROCESSING WORKFLOW"]
        direction TB
        F[extract_and_store_entities<br/>Academic Entity Extraction]
        G[store_vectors<br/>Neo4j Vector Storage]
        H[grobid_extract<br/>Academic PDF Processing]
        
        subgraph grobid_pipeline["GROBID Pipeline"]
            H1[Authors & Affiliations] 
            H2[Citations & References]
            H3[Academic Structure]
            H4[Tables & Figures]
        end
        
        subgraph entity_pipeline["Academic Entity Pipeline"]
            F1[Research Concepts] --> F2[Author Networks]
            F2 --> F3[Citation Relationships]
            F3 --> F4[Neo4j Graph Store]
        end
        
        subgraph vector_pipeline["Vector Pipeline"] 
            G1[Academic Text Chunks] --> G2[Local Embeddings] --> G3[Neo4j Vector Store]
        end
        
        H --> H1
        H --> H2  
        H --> H3
        H --> H4
        F --> F1
        G --> G1
    end
    
    subgraph database["🗄️ Unified Knowledge Store"]
        NEO@{shape: database, label: "Neo4j Database<br/>• Academic Entities<br/>• Citation Networks<br/>• Vector Embeddings<br/>• Research Relationships"}
    end
    
    subgraph query_flow["🔍 ACADEMIC QUERYING WORKFLOW"]
        direction TB
        I[query_knowledge_graph<br/>Academic Search]
        J[generate_literature_review<br/>Citation Formatting]
        
        subgraph academic_rag["Academic GraphRAG"]
            I1[Author Network<br/>Traversal] 
            I2[Citation Network<br/>Analysis]
            I3[Semantic Research<br/>Search]
            I4[Combine Academic<br/>Results]
        end
        
        I --> I1
        I --> I2
        I --> I3
        I1 --> I4
        I2 --> I4
        I3 --> I4
        I4 --> J
    end
    
    %% Client connections
    A --> E
    B --> E
    
    %% Service connections
    GROBID --> H
    
    %% Processing flow
    E --> H
    E --> F
    E --> G
    F4 --> NEO
    G3 --> NEO
    
    %% Query flow
    E --> I
    E --> J
    NEO --> I1
    NEO --> I2
    NEO --> I3
    
    %% Styling
    classDef academicBox fill:#e8f5e8
    classDef serviceBox fill:#fff3e0
    classDef queryBox fill:#f3e5f5
    classDef dbBox fill:#e1f5fe
    
    class academic_flow,grobid_pipeline,entity_pipeline,vector_pipeline academicBox
    class services,GROBID serviceBox
    class query_flow,academic_rag queryBox
    class database,NEO dbBox
```

### How Academic Data Flows Through the System

**📚 Academic Processing Workflow:**
1. **GROBID extracts structured data** → `grobid_extract` → Authors, citations, academic structure
2. **LLM analyzes academic content** → `extract_and_store_entities` → Research concepts, author networks
3. **Academic text storage** → `store_vectors` → Local embeddings → Neo4j Vector Store

**🔍 Academic Query Workflow (Academic GraphRAG):**
1. **Research question** → `query_knowledge_graph` 
2. **Multi-modal academic search**: Author networks + Citation analysis + Semantic research search
3. **Academic result synthesis** → Comprehensive answer with proper citations
4. **Literature review generation** → `generate_literature_review` → Formatted academic output

**🗄️ Unified Academic Knowledge Store:**
- **Neo4j Database**: Academic entities, citation networks, author relationships, and vector embeddings all in one system

## Step-by-Step: How Academic Processing Works

### 1. Research Paper Upload & Academic Processing
```
You → Upload PDFs to Claude Desktop
Claude → Uses GROBID for superior academic extraction
```

**What GROBID + Claude extracts:**
- **Academic Entities**: Authors, institutions, research concepts, methodologies with confidence scores
- **Citation Networks**: Paper-to-paper references, author collaboration patterns  
- **Academic Structure**: Abstracts, sections, tables, figures with proper academic context
- **Research Relationships**: How concepts, authors, and papers interconnect across the literature

### 2. Academic Data Storage
```
Academic Entities + Citation Networks → Neo4j Graph Database
Research Text + Academic Context → Neo4j Vector Store with local embeddings
```

**Example academic data stored:**
```json
// Academic Entity (Author)
{
  "id": "hinton_2006",
  "name": "Geoffrey Hinton", 
  "type": "person",
  "properties": {
    "affiliation": "University of Toronto",
    "research_areas": ["deep learning", "neural networks"],
    "h_index": 180
  },
  "confidence": 0.95
}

// Citation Relationship  
{
  "source": "hinton_2006_paper",
  "target": "lecun_1998_paper",
  "type": "cites",
  "context": "Building on LeCun's convolutional architecture...",
  "citation_count": 1
}

// Academic Text Vector (in Neo4j)
{
  "text": "Our proposed attention mechanism allows the model to focus...",
  "embedding": [0.1, -0.3, 0.8, ...],
  "document_title": "Attention Is All You Need",
  "section": "methodology",
  "authors": ["Vaswani, A.", "Shazeer, N."],
  "year": 2017
}
```

### 3. Academic Intelligence Querying
```
You → Ask research questions in natural language
Claude → Uses academic MCP tools to search citation networks + semantic content
Claude → Returns comprehensive academic answers with proper citations
```

**Academic query types supported:**
- **Author network analysis**: "Who are the key collaborators in transformer research?"
- **Citation relationship mapping**: "How do attention mechanisms relate to BERT?"
- **Research concept evolution**: "How has the transformer architecture evolved since 2017?"
- **Cross-paper methodology analysis**: "What are the different approaches to fine-tuning in these papers?"
- **Academic literature reviews**: "Generate a comprehensive review of attention mechanisms with citations"

### 4. Academic Knowledge Graph Evolution
```
More research papers → Richer citation networks → Deeper academic insights
```

**As you add research papers:**
- **Citation networks emerge**: GROBID identifies when papers reference each other with high accuracy
- **Author collaboration networks form**: Maps institutional and research partnerships
- **Research concept evolution tracked**: Shows how methodologies develop across publications
- **Research gaps identified**: Highlights understudied areas and potential research opportunities

## The 5 Academic MCP Tools Available to Claude

1. **`extract_and_store_entities`** - Extract academic entities (authors, concepts, methodologies) and relationships from research content
2. **`store_vectors`** - Store research text chunks as vectors in Neo4j with academic context preservation
3. **`query_knowledge_graph`** - Search both citation networks and semantic content for comprehensive academic answers
4. **`generate_literature_review`** - Format academic results with proper citations (APA, IEEE, Nature, MLA)
5. **`clear_knowledge_graph`** - Reset all academic data for fresh research projects

## Real-World Academic Workflow

### Scenario: Building a Transformer Research Knowledge Base

**Step 1: Research Paper Collection**
```bash
# Upload 20 transformer research papers to Claude Desktop project
- attention_is_all_you_need.pdf (Vaswani et al., 2017)
- bert_pretraining.pdf (Devlin et al., 2018)
- gpt_language_models.pdf (Radford et al., 2018)
- ... (17 more seminal transformer papers)
```

**Step 2: GROBID-Powered Academic Extraction**
```
You: "Process these transformer papers with academic extraction"

Claude: *Uses GROBID + extract_and_store_entities*
- GROBID extracts 150+ authors with institutional affiliations
- Maps 300+ research concepts (attention, positional encoding, etc.)
- Identifies 200+ citation relationships between papers
- Stores everything in Neo4j with 87-90% accuracy

You: "Store the key research passages with academic context"

Claude: *Uses store_vectors tool*  
- Stores 2000+ academic text chunks with section context
- Preserves author information and publication details
- Enables semantic search across methodologies and results
```

**Step 3: Academic Intelligence Analysis**
```
You: "What are the key innovations in transformer architectures across these papers?"

Claude: *Uses query_knowledge_graph tool*
- Searches Neo4j citation networks for transformer innovations
- Finds semantic matches in academic text vectors
- Returns: Self-attention mechanisms, positional encoding, multi-head attention, layer normalization
- Includes proper citations with institutional context (Google Research, OpenAI, etc.)

You: "Generate a literature review on attention mechanisms evolution"

Claude: *Uses generate_literature_review tool*
- Organizes findings by chronological development
- Formats with proper academic citations (APA style)
- Includes author collaboration patterns and research trends
- Shows institutional contributions to attention mechanism development
```

**Step 4: Advanced Academic Queries**
```
You: "Which researchers have collaborated most frequently in transformer research?"

Claude: Maps collaboration networks from GROBID-extracted author relationships
Result: Shows Vaswani-Shazeer collaborations, Google Research teams, etc.

You: "What are the different approaches to positional encoding across these papers?"

Claude: Finds methodological variations using semantic search + citation analysis
Result: Sinusoidal encoding (Vaswani), learned embeddings (BERT), relative positioning

You: "Trace the evolution of attention mechanisms from 2017-2023"

Claude: Temporal analysis through citation networks and concept development
Result: Self-attention → Multi-head → Sparse attention → Efficient transformers
```

## Key Academic Benefits

### For Researchers
- **Superior PDF processing**: GROBID provides 87-90% F1-score accuracy vs generic tools (60-70%)
- **Zero API costs**: Self-hosted GROBID eliminates expensive LlamaParse fees ($10-30/month)
- **Citation network analysis**: Map author collaborations and institutional partnerships automatically  
- **Research gap identification**: Discover understudied areas through comprehensive literature mapping
- **Academic literature reviews**: Generate properly formatted reviews with correct citations

### For Graduate Students
- **Thesis research acceleration**: Build comprehensive knowledge bases from research literature
- **Academic writing support**: Automatic citation extraction with proper formatting (APA, IEEE, Nature, MLA)
- **Methodology comparison**: Understand how research approaches connect across different papers
- **Advisor collaboration**: Share queryable knowledge graphs with supervisors

### For Academic Institutions
- **Research intelligence**: Track institutional research output and collaboration patterns
- **Literature monitoring**: Stay current with developments in specific research areas
- **Grant application support**: Identify research trends and potential collaborators
- **Publication analysis**: Map citation networks and research impact across departments

## Technical Architecture

### Academic Processing Layer (`src/processor/`)
```
processor/
├── document_pipeline.py        # LangGraph orchestrator for academic workflows
├── tools/
│   ├── grobid_tool.py          # GROBID academic PDF extraction (87-90% accuracy)
│   └── storage_tool.py         # Neo4j integration for academic data
├── config.py                   # Processing configuration management
├── orchestrator_config.py      # Academic workflow definitions
└── entity_extractor_config.py  # Academic extraction settings
```

### Storage Layer (`src/storage/`)
```
storage/
├── neo4j/           # Unified graph and vector database
│   ├── storage.py   # Academic entities, citations, and vector storage
│   └── query.py     # Citation network traversal and semantic search
└── embedding/       # Local embedding generation
    └── service.py   # sentence-transformers integration (privacy-focused)
```

### Tools Layer (`src/tools/`)
```
tools/
├── storage/         # Academic data persistence tools
│   ├── enhanced_entity_storage.py   # Academic entity extraction MCP tool
│   ├── neo4j_vector_storage.py      # Vector storage in Neo4j MCP tool
│   └── database_management.py       # clear_knowledge_graph MCP tool
├── query/           # Academic data retrieval tools
│   ├── knowledge_search.py          # query_knowledge_graph MCP tool (citation networks + semantic)
│   └── literature_generation.py     # generate_literature_review MCP tool
└── shared_registry.py               # Dual MCP/LangChain tool registry
```

### Server Layer (`src/server/`)
- **`main.py`** - FastMCP server with all 5 academic tools registered for Claude Desktop

## Academic-First Privacy Design

- **Self-hosted GROBID** - No external APIs for PDF processing, complete privacy
- **Local embeddings** - Uses sentence-transformers for complete research confidentiality
- **Neo4j via Docker** - Academic data stays on your machine
- **Zero API costs** - No LlamaParse or external PDF processing fees
- **Research data security** - Everything processed and stored locally, perfect for sensitive research

## Quick Start

### Prerequisites
- Python 3.11+ (required for FastMCP)
- Docker (for Neo4j database and GROBID service)
- Claude Desktop (recommended MCP client for academic research)

### Installation
```bash
# 1. Clone repository
git clone <repository-url>
cd simple-knowledge-graph-mcp

# 2. Complete setup (installs UV, Python 3.11, academic dependencies)
./scripts/setup.sh

# 3. Start Neo4j database + GROBID academic service
./scripts/start_services.sh
docker run -d --name grobid -p 8070:8070 lfoppiano/grobid:0.8.0

# 4. Verify academic system is ready
./scripts/check_status.sh
curl http://localhost:8070/api/isalive  # Should return "true"
```

### Configure Claude Desktop

#### Recommended: Easy GUI Setup
```bash
# Start HTTP server for academic tools
./scripts/start_http_server.sh
```

Then in Claude Desktop:
- Settings → Connectors → Add custom connector
- **Name**: `Academic Knowledge Graph`
- **URL**: `http://localhost:3001`
- Click "Add" and restart Claude Desktop

#### Alternative: JSON Configuration (Advanced)
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "academic-knowledge-graph": {
      "command": "uv",
      "args": ["run", "python", "/full/path/to/project/src/server/main.py"]
    }
  }
}
```

### Start Academic Research
```bash
# Start the academic MCP server
./scripts/start_http_server.sh

# In Claude Desktop:
# 1. Upload research PDFs to your project
# 2. "Process these papers with GROBID for academic extraction"  
# 3. "Extract author networks and citation relationships"
# 4. "What are the key research trends in these papers?"
# 5. "Generate a literature review on [specific topic]"
```

### Test Academic Processing
```bash
# Test GROBID + academic pipeline
python process_literature.py

# Your academic research assistant is now ready with:
# - GROBID's 87-90% accuracy for research papers
# - Zero API costs for PDF processing  
# - Citation network analysis
# - Author collaboration mapping
# - Academic literature review generation
```

That's it! Your GROBID-powered academic research assistant is ready to transform research papers into intelligent, queryable knowledge graphs.

## What Makes This Academic System Superior

Unlike generic document tools or expensive PDF processing services, this system:

1. **Academic specialization** - GROBID provides 87-90% F1-score accuracy specifically for research papers
2. **Zero API costs** - Self-hosted GROBID eliminates LlamaParse fees ($10-30/month saved)
3. **Citation network intelligence** - Maps author collaborations and paper relationships automatically
4. **Research privacy** - All processing stays local, perfect for sensitive academic research
5. **Institutional analysis** - Tracks university collaborations and research partnerships
6. **Academic writing support** - Generates properly formatted literature reviews with citations
7. **Claude Desktop integration** - Seamless research workflow within your existing environment

Perfect for researchers, graduate students, and academic institutions who need sophisticated analysis of research literature without compromising privacy or incurring API costs.
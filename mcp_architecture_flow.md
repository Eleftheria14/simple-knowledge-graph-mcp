# MCP Server Architecture Flow

```mermaid
flowchart TD
    subgraph clients["🖥️ LLM Clients"]
        A[Claude Desktop<br/>STDIO Transport]
        B[ChatGPT Desktop<br/>HTTP Transport]
        C[Other MCP Clients<br/>Various Transports]
    end
    
    subgraph comm["📡 MCP Communication"]
        D[MCP Protocol]
        E[FastMCP Server<br/>Multi-Transport]
    end
    
    subgraph tools["🛠️ MCP Tools"]
        subgraph core_tools["Core Knowledge Graph Tools"]
            F[store_entities]
            G[store_vectors]
            H[query_knowledge_graph]
            I[generate_literature_review]
            J[clear_knowledge_graph]
        end
        subgraph text_tools["Text Processing Tools"]
            K[generate_systematic_chunks]
            L[estimate_chunking_requirements]
            M[validate_text_coverage]
        end
    end
    
    subgraph storage["💾 Storage Layer"]
        N[Neo4j Storage]
        O[ChromaDB Storage]
        P[Neo4j Query]
        Q[ChromaDB Query]
    end
    
    subgraph databases["🗄️ Databases"]
        R@{shape: database, label: "Neo4j Graph DB"}
        S@{shape: database, label: "ChromaDB Vector DB"}
    end
    
    subgraph embedding["🧠 Local AI"]
        T[sentence-transformers]
        U[Local Embeddings]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    
    E --> F
    E --> G
    E --> H
    E --> I
    E --> J
    E --> K
    E --> L
    E --> M
    
    F --> N
    G --> O
    H --> P
    H --> Q
    I --> P
    I --> Q
    J --> N
    J --> O
    K --> O
    L --> O
    M --> O
    
    N --> R
    O --> S
    P --> R
    Q --> S
    
    O --> T
    Q --> T
    T --> U
```

## Data Flow Examples

### 1. Entity Storage Flow
```mermaid
sequenceDiagram
    participant LLM as LLM Client
    participant MCP as MCP Server
    participant Neo4j as Neo4j Storage
    participant DB as Neo4j Database
    
    LLM->>MCP: store_entities(entities, relationships, doc_info)
    MCP->>Neo4j: Convert to graph format
    Neo4j->>DB: CREATE entities and relationships
    DB->>Neo4j: Confirmation
    Neo4j->>MCP: Success + counts
    MCP->>LLM: JSON response with stats
```

### 2. Vector Storage Flow
```mermaid
sequenceDiagram
    participant LLM as LLM Client
    participant MCP as MCP Server
    participant Chroma as ChromaDB Storage
    participant Embed as Embedding Service
    participant DB as ChromaDB Database
    
    LLM->>MCP: store_vectors(vectors, doc_info)
    MCP->>Embed: Generate embeddings for vector content
    Embed->>MCP: Vector embeddings
    MCP->>Chroma: Store content + embeddings + metadata
    Chroma->>DB: INSERT documents with vectors
    DB->>Chroma: Confirmation
    Chroma->>MCP: Success + counts
    MCP->>LLM: JSON response with stats
```

### 3. Text Processing Flow
```mermaid
sequenceDiagram
    participant LLM as LLM Client
    participant MCP as MCP Server
    participant TextProc as Text Processing Tools
    participant Chroma as ChromaDB Storage
    participant DB as ChromaDB Database
    
    LLM->>MCP: estimate_chunking_requirements(paper_text)
    MCP->>TextProc: Analyze text structure and word count
    TextProc->>MCP: Chunking recommendations and estimates
    MCP->>LLM: Optimization suggestions
    
    LLM->>MCP: generate_systematic_chunks(paper_text, settings)
    MCP->>TextProc: Create overlapping chunks with section detection
    TextProc->>MCP: Systematic chunks with metadata
    MCP->>LLM: Chunks ready for storage
    
    LLM->>MCP: validate_text_coverage(original_text, chunks)
    MCP->>TextProc: Calculate coverage statistics
    TextProc->>MCP: Coverage report and quality assessment
    MCP->>LLM: Validation results
    
    LLM->>MCP: store_vectors(chunks, doc_info)
    MCP->>Chroma: Store validated chunks
    Chroma->>DB: INSERT chunks with embeddings
    DB->>Chroma: Success confirmation
    Chroma->>MCP: Storage complete
    MCP->>LLM: All chunks stored successfully
```

### 4. Knowledge Query Flow
```mermaid
sequenceDiagram
    participant LLM as LLM Client
    participant MCP as MCP Server
    participant Neo4jQ as Neo4j Query
    participant ChromaQ as ChromaDB Query
    participant Neo4jDB as Neo4j Database
    participant ChromaDB as ChromaDB Database
    participant Embed as Embedding Service
    
    LLM->>MCP: query_knowledge_graph(query, options)
    
    par Entity Search
        MCP->>Neo4jQ: Search entities by query
        Neo4jQ->>Neo4jDB: MATCH entities WHERE name CONTAINS query
        Neo4jDB->>Neo4jQ: Matching entities + relationships
    and Text Search
        MCP->>Embed: Generate query embedding
        Embed->>MCP: Query vector
        MCP->>ChromaQ: Similarity search with vector
        ChromaQ->>ChromaDB: Vector similarity query
        ChromaDB->>ChromaQ: Similar text chunks + metadata
    end
    
    Neo4jQ->>MCP: Entity results
    ChromaQ->>MCP: Text results + citations
    MCP->>LLM: Combined JSON response
```

## Connection Methods

### Claude Desktop (STDIO Transport)
- **Configuration**: `claude_desktop_config.json` file
- **Transport**: STDIO (Standard Input/Output)
- **Setup**: No manual server startup required
- **How it works**: Claude Desktop launches the server automatically

### Other MCP Clients (HTTP Transport)
- **Configuration**: Manual HTTP server startup
- **Transport**: HTTP on localhost:3001
- **Setup**: Run `./scripts/start_http_server.sh`
- **How it works**: Client connects to running HTTP server

### Why Different Transports?
- **STDIO**: More secure, no network exposure, automatically managed
- **HTTP**: More flexible, easier for development, works across networks

Both methods use the same MCP protocol and provide identical functionality.
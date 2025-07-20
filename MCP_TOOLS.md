# MCP Tools Reference for Claude Desktop

This document describes the 8+ MCP tools available to Claude Desktop when connected to the Simple Knowledge Graph MCP server.

## 🎯 For End Users

**You don't need to understand these technical details!** Just ask Claude things like:
- "Extract entities from this document"
- "Store the key information from these papers"  
- "What does my knowledge graph say about transformers?"
- "Generate a literature review on machine learning"
- "Chunk this paper systematically for complete coverage"
- "Estimate how many chunks I need for this document"

Claude will use these tools automatically. This reference is for developers who want to understand what's happening under the hood.

## Technical Overview

These tools enable Claude to build and query knowledge graphs from documents. All tools operate on two local databases:
- **Neo4j**: Graph database for entities and relationships
- **ChromaDB**: Full vector database for any content with embeddings (entities, text chunks, concepts, etc.)

## Tool 1: `store_entities`

### Purpose
Store entities and relationships in Neo4j graph database.

### Parameters
```json
{
  "entities": [
    {
      "id": "unique_identifier",
      "name": "Entity Name", 
      "type": "person|concept|technology|organization|method|etc",
      "properties": {"key": "value", "affiliation": "MIT"},
      "confidence": 0.95
    }
  ],
  "relationships": [
    {
      "source": "entity_id_1",
      "target": "entity_id_2", 
      "type": "researches|uses|part_of|collaborates_with|etc",
      "confidence": 0.85,
      "context": "Text snippet supporting this relationship"
    }
  ],
  "document_info": {
    "title": "Document Title",
    "type": "research_paper|book|article|etc",
    "id": "optional_doc_id",
    "path": "optional_file_path"
  }
}
```

### Example Usage
```json
{
  "entities": [
    {
      "id": "hinton_2006",
      "name": "Geoffrey Hinton",
      "type": "person",
      "properties": {"affiliation": "University of Toronto", "role": "professor"},
      "confidence": 0.98
    },
    {
      "id": "backprop_concept", 
      "name": "Backpropagation",
      "type": "concept",
      "properties": {"domain": "machine_learning", "year_introduced": "1986"},
      "confidence": 0.92
    }
  ],
  "relationships": [
    {
      "source": "hinton_2006",
      "target": "backprop_concept",
      "type": "developed",
      "confidence": 0.95,
      "context": "Hinton was instrumental in developing and popularizing backpropagation"
    }
  ],
  "document_info": {
    "title": "Learning representations by back-propagating errors",
    "type": "research_paper"
  }
}
```

### Return Value
```json
{
  "success": true,
  "message": "Stored 2 entities and 1 relationships",
  "document_id": "generated_uuid",
  "entities_created": 2,
  "relationships_created": 1
}
```

## Tool 2: `store_vectors`

### Purpose
Store any type of content as vectors in ChromaDB (entities, concepts, text chunks, etc.).

### Parameters
```json
{
  "vectors": [
    {
      "id": "unique_vector_id",
      "content": "Text content to embed",
      "type": "entity|text_chunk|concept|method|etc",
      "properties": {"key": "value", "domain": "NLP"}
    }
  ],
  "document_info": {
    "title": "Document Title",
    "type": "research_paper|book|article|etc",
    "id": "optional_doc_id",
    "path": "optional_file_path"
  }
}
```

### Example Usage
```json
{
  "vectors": [
    {
      "id": "transformer_concept",
      "content": "Transformer architecture revolutionized natural language processing through self-attention mechanisms",
      "type": "entity",
      "properties": {"domain": "NLP", "year": 2017, "key_innovation": "self-attention"}
    },
    {
      "id": "attention_mechanism",
      "content": "Self-attention mechanism allowing models to focus on different parts of input sequences",
      "type": "concept", 
      "properties": {"domain": "deep_learning", "computational_complexity": "O(n^2)"}
    },
    {
      "id": "methodology_chunk",
      "content": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms",
      "type": "text_chunk",
      "properties": {"section": "methodology", "word_count": 16}
    }
  ],
  "document_info": {
    "title": "Attention Is All You Need",
    "type": "research_paper"
  }
}
```

### Return Value
```json
{
  "success": true,
  "message": "Stored 3 vectors of types: {'entity', 'concept', 'text_chunk'}",
  "document_id": "generated_uuid",
  "vectors_stored": 3
}
```

## Tool 3: `query_knowledge_graph`

### Purpose
Search Neo4j and ChromaDB for matching content.

### Parameters
```json
{
  "query": "Search query text",
  "include_entities": true,
  "include_text": true,
  "limit": 10
}
```

### Parameter Details
- **query**: Natural language search query
- **include_entities**: Whether to search entities in Neo4j (default: true)
- **include_text**: Whether to search text content (default: true) 
- **limit**: Maximum results per category (default: 10)

### Example Usage
```json
{
  "query": "transformer attention mechanisms in neural networks",
  "include_entities": true,
  "include_text": true,
  "limit": 5
}
```

### Return Value
```json
{
  "success": true,
  "query": "transformer attention mechanisms in neural networks",
  "entities": [
    {
      "id": "transformer_arch",
      "name": "Transformer Architecture",
      "type": "concept",
      "properties": {"domain": "NLP"},
      "relationships": [
        {
          "target": "attention_mechanism",
          "type": "uses",
          "context": "Transformers rely heavily on attention"
        }
      ]
    }
  ],
  "text_results": [
    {
      "text": "Self-attention allows the model to focus on different parts...",
      "similarity": 0.87,
      "document_title": "Attention Paper",
      "citation": {"authors": ["Vaswani, A."], "year": 2017}
    }
  ],
  "citations": [
    {
      "authors": ["Vaswani, A."],
      "title": "Attention Is All You Need", 
      "year": 2017,
      "relevance": 0.92
    }
  ],
  "message": "Found 1 entities, 1 text matches, 1 citations"
}
```

## Tool 4: `generate_literature_review`

### Purpose
Generate formatted output by querying stored data.

### Parameters
```json
{
  "topic": "Research topic to review",
  "citation_style": "APA|IEEE|Nature|MLA",
  "max_sources": 20,
  "include_summary": true
}
```

### Parameter Details
- **topic**: Topic to search for and organize
- **citation_style**: Citation format (default: APA)
- **max_sources**: Maximum sources to include (default: 20)
- **include_summary**: Whether to include summary statistics (default: true)

### Example Usage
```json
{
  "topic": "attention mechanisms in deep learning",
  "citation_style": "APA", 
  "max_sources": 15,
  "include_summary": true
}
```

### Return Value
```json
{
  "success": true,
  "literature_review": {
    "topic": "attention mechanisms in deep learning",
    "citation_style": "APA",
    "entity_themes": {
      "person": [{"name": "Vaswani", "type": "person"}],
      "concept": [{"name": "Self-Attention", "type": "concept"}]
    },
    "key_concepts": [
      {"name": "Self-Attention", "properties": {"domain": "NLP"}}
    ],
    "key_researchers": [
      {"name": "Ashish Vaswani", "properties": {"affiliation": "Google"}}
    ],
    "technologies": [
      {"name": "Transformer", "properties": {"year": 2017}}
    ],
    "relevant_text": [
      {
        "text": "Attention mechanisms allow models to focus...",
        "citation": "Vaswani et al., 2017"
      }
    ],
    "citations": [
      {
        "authors": ["Vaswani, A."],
        "title": "Attention Is All You Need",
        "year": 2017,
        "formatted": "Vaswani, A. et al. (2017). Attention Is All You Need. NIPS."
      }
    ],
    "summary": {
      "total_entities": 25,
      "total_citations": 15,
      "main_themes": ["person", "concept", "technology"],
      "coverage": "Review covers 15 sources with 25 key entities"
    },
    "generated_at": "2024-01-15T10:30:00Z"
  },
  "message": "Generated literature review for 'attention mechanisms' with 15 sources"
}
```

## Tool 5: `clear_knowledge_graph`

### Purpose
Clear all data from both databases.

### Parameters
None - this tool takes no parameters.

### Example Usage
```json
{}
```

### Return Value
```json
{
  "success": true,
  "message": "Knowledge graph cleared successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Warning
This permanently deletes ALL stored data and cannot be undone.

## Tool 6: `generate_systematic_chunks`

### Purpose
Generate systematic chunks for complete paper coverage with automatic section detection and overlap management.

### Parameters
```json
{
  "paper_text": "Full paper text to chunk",
  "paper_title": "Research Paper Title",
  "chunk_size": 300,
  "overlap": 75
}
```

### Parameter Details
- **paper_text**: Complete text of the paper to be chunked
- **paper_title**: Title for chunk naming (default: "Research Paper")
- **chunk_size**: Target words per chunk (200-400 recommended, default: 300)
- **overlap**: Overlap words between chunks (50-100 recommended, default: 75)

### Example Usage
```json
{
  "paper_text": "Abstract: This paper presents a novel approach...[full paper text]",
  "paper_title": "Attention Is All You Need",
  "chunk_size": 300,
  "overlap": 75
}
```

### Return Value
```json
{
  "success": true,
  "message": "Generated 25 systematic chunks with good coverage",
  "chunks": [
    {
      "id": "attention_paper_chunk_001",
      "content": "Abstract: This paper presents a novel...",
      "type": "text_chunk",
      "properties": {
        "section": "abstract",
        "word_count": 287,
        "chunk_sequence": 1,
        "overlap_with_previous": false,
        "page": 1
      }
    }
  ],
  "statistics": {
    "total_chunks": 25,
    "total_words": 7500,
    "average_chunk_size": 300,
    "sections_covered": ["abstract", "introduction", "methods", "results", "conclusion"],
    "coverage_report": {
      "coverage_status": "good",
      "coverage_ratio": "96%"
    }
  },
  "ready_for_vector_storage": true
}
```

## Tool 7: `estimate_chunking_requirements`

### Purpose
Estimate chunking requirements for a paper to plan optimal processing strategy.

### Parameters
```json
{
  "paper_text": "Full paper text to analyze"
}
```

### Example Usage
```json
{
  "paper_text": "Abstract: This paper presents a novel approach...[full paper text]"
}
```

### Return Value
```json
{
  "success": true,
  "estimates": {
    "total_words": 7500,
    "estimated_chunks": 25,
    "estimated_processing_time": "2-3 minutes",
    "recommended_chunk_size": 300,
    "sections_detected": ["abstract", "introduction", "methods", "results", "conclusion"]
  },
  "recommendations": [
    "Medium paper - systematic chunking with 200-300 word chunks",
    "Target: 25 chunks for 95%+ coverage"
  ],
  "suggested_chunk_size": 300,
  "suggested_overlap": 75,
  "research_standards": {
    "minimum_coverage": "85%",
    "excellent_coverage": "95%",
    "systematic_chunking": "Required for research databases"
  }
}
```

## Tool 8: `validate_text_coverage`

### Purpose
Validate how well chunks cover the original paper for research integrity.

### Parameters
```json
{
  "original_text": "Full original paper text",
  "stored_chunks": [
    {
      "content": "Chunk text content",
      "properties": {"word_count": 295}
    }
  ]
}
```

### Example Usage
```json
{
  "original_text": "Abstract: This paper presents...[full original text]",
  "stored_chunks": [
    {
      "content": "Abstract: This paper presents a novel approach...",
      "properties": {"word_count": 287}
    },
    {
      "content": "Introduction: Recent advances in machine learning...",
      "properties": {"word_count": 312}
    }
  ]
}
```

### Return Value
```json
{
  "success": true,
  "coverage_report": {
    "coverage_ratio": "94%",
    "status": "good",
    "meets_research_standards": true
  },
  "statistics": {
    "original_words": 7500,
    "stored_words": 7050,
    "total_chunks": 25
  },
  "message": "Coverage: 94% (✅ Good)"
}

## Usage Patterns for Claude

### Document Processing Workflow

**Basic Workflow:**
1. **Extract entities**: Use `store_entities` with extracted entities and relationships
2. **Store vectors**: Use `store_vectors` for any content (entities, text chunks, concepts, etc.)
3. **Query**: Use `query_knowledge_graph` to find information
4. **Generate reviews**: Use `generate_literature_review` for formatted output

**Advanced Text Processing Workflow:**
1. **Plan chunking**: Use `estimate_chunking_requirements` to analyze paper structure
2. **Generate chunks**: Use `generate_systematic_chunks` for complete coverage
3. **Validate coverage**: Use `validate_text_coverage` to ensure research standards
4. **Store chunks**: Use `store_vectors` to store the systematic chunks
5. **Query and review**: Use `query_knowledge_graph` and `generate_literature_review`

### Batch Processing
```json
// Process multiple documents with systematic chunking
foreach document {
  // Optional: Plan chunking strategy
  estimate_chunking_requirements(paper_text)
  
  // Generate systematic chunks
  chunks = generate_systematic_chunks(paper_text, paper_title, 300, 75)
  
  // Validate coverage
  validate_text_coverage(paper_text, chunks)
  
  // Store entities and systematic chunks
  store_entities(extracted_entities, extracted_relationships, document_info)
  store_vectors(chunks, document_info)
}

// Query the complete knowledge base
query_knowledge_graph("research question")
generate_literature_review("topic", "APA")
```

### Error Handling
All tools return a `success` field. When `success: false`:
```json
{
  "success": false,
  "error": "Detailed error message",
  "message": "User-friendly error description"
}
```

### Best Practices

#### Entity Extraction
- Use descriptive, unique IDs for entities
- Include confidence scores for quality assessment
- Provide rich properties for better querying
- Include context for relationships

#### Text Storage
- Store meaningful chunks (paragraphs, key passages)
- Include complete citation information
- Maintain document provenance

#### Querying
- Use natural language queries
- Combine entity and text search for comprehensive results
- Adjust limits based on expected result size

#### Literature Reviews
- Choose appropriate citation style for target audience
- Include summary for overview statistics
- Use reasonable max_sources limit for readability

#### Text Processing
- Use `estimate_chunking_requirements` before processing to plan strategy
- Generate systematic chunks with appropriate size (200-400 words)
- Validate coverage to ensure research-grade quality (85%+ coverage)
- Use overlapping chunks (50-100 words) for better context preservation

## Data Models Reference

### EntityData
```typescript
{
  id: string              // Unique identifier
  name: string           // Display name
  type: string           // Category (person, concept, etc.)
  properties: object     // Additional attributes
  confidence: number     // 0.0 to 1.0
}
```

### RelationshipData
```typescript
{
  source: string         // Source entity ID
  target: string         // Target entity ID
  type: string           // Relationship type
  confidence: number     // 0.0 to 1.0
  context: string        // Supporting text
}
```

### VectorData
```typescript
{
  id: string             // Unique identifier
  content: string        // Text content to embed
  type: string           // Type (entity, text_chunk, concept, etc.)
  properties: object     // Additional metadata
}
```

### DocumentInfo
```typescript
{
  title: string          // Document title
  type: string           // Document type
  id: string             // Optional unique ID
  path: string           // Optional file path
}
```

This toolset enables Claude to build sophisticated knowledge graphs from documents and provide intelligent querying capabilities for research and analysis.
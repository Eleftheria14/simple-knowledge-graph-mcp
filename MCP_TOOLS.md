# MCP Tools Reference for Claude Desktop

This document describes the 5 MCP tools available to Claude Desktop when connected to the Simple Knowledge Graph MCP server.

## Overview

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

## Usage Patterns for Claude

### Document Processing Workflow
1. **Extract entities**: Use `store_entities` with extracted entities and relationships
2. **Store vectors**: Use `store_vectors` for any content (entities, text chunks, concepts, etc.)
3. **Query**: Use `query_knowledge_graph` to find information
4. **Generate reviews**: Use `generate_literature_review` for formatted output

### Batch Processing
```json
// Process multiple documents
foreach document {
  store_entities(extracted_entities, extracted_relationships, document_info)
  store_vectors(entities_and_text_as_vectors, document_info)
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
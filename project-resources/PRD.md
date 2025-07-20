# Product Requirements Document (PRD)
## Simple Knowledge Graph MCP

### Executive Summary

**Product Vision:** Make knowledge graph creation accessible to every researcher, student, and professional who has access to Claude or ChatGPT, without requiring API keys, complex setup, or technical expertise.

**Problem Statement:** Current knowledge graph tools require significant technical setup (APIs, complex configurations, local LLM installation). Most people have Claude Desktop or ChatGPT access but can't easily build research knowledge graphs from their documents.

**Solution:** A minimal MCP (Model Context Protocol) server that enables Claude/ChatGPT to intelligently extract entities from documents and store them in a queryable knowledge graph, all through simple conversational commands.

---

## Product Overview

### Target Users

**Primary Users:**
- **Academic Researchers** - Need to synthesize literature across multiple papers
- **Graduate Students** - Writing literature reviews and theses
- **Research Scientists** - Building knowledge bases from scientific papers
- **Knowledge Workers** - Creating structured knowledge from documents

**Secondary Users:**
- **Consultants** - Building client knowledge bases
- **Journalists** - Researching and organizing sources
- **Legal Professionals** - Document analysis and case research

### Core Value Proposition

1. **Zero Technical Barrier**: Works with existing Claude Desktop or ChatGPT subscriptions
2. **No API Setup**: Local embeddings, no external API keys required
3. **Intelligent Extraction**: Claude decides what entities are important (no rigid prompts)
4. **Dual Search**: Both semantic search (vector) and relationship search (graph)
5. **Academic Ready**: Automatic citation formatting and literature review generation

---

## Product Requirements

### Functional Requirements

#### Core Features (MVP)

**F1: Entity Storage**
- **Requirement**: Store extracted entities in Neo4j with relationships
- **User Story**: "As a researcher, I want Claude to identify and store key people, concepts, and technologies from my papers so I can track important elements across my research."
- **Acceptance Criteria**:
  - Entities stored with type, properties, and confidence scores
  - Relationships between entities preserved
  - Document provenance tracked for all entities

**F2: Text Storage with Embeddings**
- **Requirement**: Store text chunks in ChromaDB with semantic embeddings
- **User Story**: "As a student, I want to search my document collection semantically so I can find relevant passages even when I don't remember exact keywords."
- **Acceptance Criteria**:
  - Text chunks embedded using local sentence-transformers
  - Citations linked to relevant text passages
  - Metadata preserved for all stored content

**F3: Unified Query Interface**
- **Requirement**: Query both graph and vector databases simultaneously
- **User Story**: "As a researcher, I want to ask questions about my research domain and get comprehensive answers combining entity relationships and relevant text passages."
- **Acceptance Criteria**:
  - Single query searches both Neo4j and ChromaDB
  - Results ranked by relevance and confidence
  - Related entities and relationships included

**F4: Literature Review Generation**
- **Requirement**: Format query results as academic literature reviews
- **User Story**: "As a graduate student, I want to generate properly formatted literature review sections with citations so I can accelerate my thesis writing."
- **Acceptance Criteria**:
  - Multiple citation styles supported (APA, IEEE, Nature, MLA)
  - Proper academic formatting
  - Source tracking and bibliography generation

#### Enhanced Features (Future)

**F5: Visual Knowledge Graph**
- Interactive graph visualization of entities and relationships
- Export capabilities for presentations and papers

**F6: Collaboration Features**
- Shared knowledge graphs between team members
- Version control for research projects

**F7: Domain Templates**
- Pre-configured entity types for specific fields (chemistry, biology, computer science)
- Domain-specific relationship templates

### Non-Functional Requirements

#### Performance Requirements

**P1: Response Time**
- Entity storage: < 5 seconds for typical academic paper
- Query response: < 3 seconds for most queries
- Embedding generation: < 10 seconds for 20-page document

**P2: Scalability**
- Support 1000+ documents per knowledge graph
- Handle 10,000+ entities efficiently
- Concurrent access for multiple users

**P3: Reliability**
- 99.9% uptime for local deployments
- Automatic error recovery and retry logic
- Data integrity preservation across operations

#### Usability Requirements

**U1: Ease of Setup**
- One-click service startup script
- Automatic dependency installation
- Clear error messages and troubleshooting

**U2: Intuitive Commands**
- Natural language MCP tool usage
- Self-documenting prompt templates
- Helpful error messages and suggestions

**U3: Documentation Quality**
- Complete setup documentation
- Example workflows and use cases
- Troubleshooting guides

---

## Technical Architecture

### System Components

**MCP Server Layer**
- 4 core MCP tools (store_entities, store_vectors, query_knowledge_graph, generate_literature_review)
- FastMCP framework for tool registration
- Pydantic models for data validation

**Storage Layer**
- Neo4j: Entity and relationship storage
- ChromaDB: Vector embeddings and text search
- Local sentence-transformers: Embedding generation

**Integration Layer**
- Claude Desktop MCP integration
- ChatGPT tool compatibility (future)
- Standard JSON-based tool interfaces

### Data Models

**Entity Model**
```json
{
  "id": "unique_identifier",
  "name": "entity_name", 
  "type": "person|concept|technology|organization",
  "properties": {"key": "value"},
  "confidence": 0.95,
  "source_document": "document_id"
}
```

**Relationship Model**
```json
{
  "source": "entity_id",
  "target": "entity_id", 
  "type": "relationship_type",
  "confidence": 0.90,
  "context": "supporting_text"
}
```

**Citation Model**
```json
{
  "authors": ["Author Name"],
  "title": "Paper Title",
  "year": 2024,
  "journal": "Journal Name", 
  "doi": "10.1000/xyz",
  "context": "relevant_passage"
}
```

### Dependencies

**Core Dependencies**
- fastmcp >= 0.2.0 (MCP framework)
- neo4j >= 5.0.0 (graph database)
- chromadb >= 0.4.0 (vector database)
- sentence-transformers >= 2.0.0 (local embeddings)
- pydantic >= 2.0.0 (data validation)

**Infrastructure Dependencies**
- Docker (for Neo4j deployment)
- Python 3.8+ runtime
- 4GB+ RAM recommended

---

## User Experience Design

### Primary User Workflows

#### Workflow 1: Initial Knowledge Graph Creation

1. **Setup Phase**
   - User runs `./start_services.sh`
   - Neo4j starts in Docker container
   - MCP server launches successfully

2. **Configuration Phase**
   - User adds MCP server to Claude Desktop config
   - Claude Desktop restarts and connects to server
   - User uploads PDF to Claude Project

3. **Extraction Phase**
   - User: "Analyze this document and store the entities and relationships"
   - Claude extracts entities intelligently using `store_entities` tool
   - Claude extracts content and stores with `store_vectors` tool
   - User receives confirmation of entities and citations stored

#### Workflow 2: Querying Knowledge Graph

1. **Research Phase**
   - User: "What do I know about transformer architectures?"
   - Claude uses `query_knowledge_graph` tool
   - Results include entities, relationships, and relevant text passages
   - User receives comprehensive answer with source citations

2. **Deep Dive Phase**
   - User: "Show me connections between attention mechanisms and performance"
   - Claude traces entity relationships in Neo4j
   - Semantic search finds related text in ChromaDB
   - User receives detailed relationship analysis

#### Workflow 3: Literature Review Generation

1. **Topic Selection**
   - User: "Generate a literature review section on machine learning in drug discovery"
   - Claude queries knowledge graph for relevant entities and citations
   - Results organized by research themes and chronology

2. **Formatting Phase**
   - Claude uses `generate_literature_review` tool
   - Proper citations formatted in requested style (APA/IEEE/etc.)
   - User receives publication-ready literature review section

### Error Handling

**Common Error Scenarios**
- Neo4j connection failure → Clear restart instructions
- ChromaDB initialization error → Automatic retry with fallback
- Embedding model download failure → Progress indicators and troubleshooting
- MCP tool timeout → Graceful degradation and user notification

---

## Success Metrics

### Primary KPIs

**Adoption Metrics**
- Number of active users per month
- Number of documents processed per user
- Retention rate after first successful use

**Usage Metrics**
- Average entities extracted per document
- Query frequency per knowledge graph
- Literature reviews generated per month

**Quality Metrics**
- Entity extraction accuracy (manual evaluation)
- User satisfaction scores
- Time to first successful workflow completion

### Secondary Metrics

**Technical Performance**
- Average response time per tool
- System uptime percentage
- Error rate per operation type

**User Engagement**
- Documents per knowledge graph
- Queries per user session
- Feature adoption rate

---

## Development Roadmap

### Phase 1: MVP Release (Week 1-2)
- ✅ Core 4 MCP tools implemented
- ✅ Basic Neo4j and ChromaDB integration
- ✅ Local embedding service
- ✅ Documentation and setup scripts

### Phase 2: Polish & Testing (Week 3-4)
- Comprehensive error handling
- Performance optimization
- User testing with real academic papers
- Documentation improvements

### Phase 3: Enhanced Features (Month 2)
- Visual knowledge graph interface
- Additional citation styles
- Batch document processing
- Export functionality

### Phase 4: Collaboration Features (Month 3)
- Shared knowledge graphs
- Team collaboration tools
- Version control integration
- API for external tools

---

## Risk Assessment

### Technical Risks

**High Risk**
- MCP protocol changes breaking compatibility
- Neo4j Docker setup complexity for non-technical users
- Embedding model performance on diverse document types

**Mitigation Strategies**
- Pin MCP dependencies and test thoroughly
- Provide Docker troubleshooting guide and alternatives
- Test with diverse document corpus and provide fallback models

### Market Risks

**Medium Risk**
- Claude Desktop adoption may be limited
- Competition from existing knowledge graph tools
- User willingness to set up local databases

**Mitigation Strategies**
- Support multiple AI platforms (ChatGPT, future tools)
- Focus on simplicity and ease of use as differentiator
- Provide cloud hosting options for less technical users

### User Adoption Risks

**Medium Risk**
- Learning curve for MCP tool usage
- Expectation mismatch for entity extraction quality
- Setup complexity deterring non-technical users

**Mitigation Strategies**
- Comprehensive tutorials and examples
- Clear documentation of capabilities and limitations
- One-click setup scripts and detailed troubleshooting

---

## Conclusion

The Simple Knowledge Graph MCP represents a paradigm shift in making advanced research tools accessible to mainstream users. By leveraging the Model Context Protocol and existing AI subscriptions, we can democratize knowledge graph creation for researchers, students, and professionals worldwide.

The minimal technical architecture (200 lines vs 10,000+ in existing solutions) ensures maintainability while the intelligent entity extraction approach provides maximum flexibility for diverse research domains. Success will be measured by user adoption, workflow completion rates, and the quality of generated literature reviews.

This product has the potential to transform how researchers organize and synthesize knowledge, accelerating scientific discovery and academic writing across all disciplines.
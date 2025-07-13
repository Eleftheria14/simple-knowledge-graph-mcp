# HISTORICAL REFERENCE: Implementation Plan: Scientific RAG + Knowledge Graph Platform

**⚠️ HISTORICAL DOCUMENT - This represents the original implementation plan but the system evolved differently. See current CLAUDE.md for actual architecture.**

## 🧹 Current Codebase Analysis & Cleanup

### **Files to Keep & Refactor:**
- ✅ `src/embedding_analyzer.py` → Expand for RAG capabilities
- ✅ `src/database_manager.py` → Add knowledge graph tables  
- ✅ `src/enhanced_citation_extractor.py` → Keep for metadata extraction
- ✅ `database/database_setup.sql` → Extend for graph schema
- ✅ `database/add_embeddings_schema.sql` → Integrate into main schema
- ✅ `docs/` → Keep all documentation
- ✅ `examples/d4sc03921a.pdf` → Keep for testing

### **Files to Remove/Archive:**
- ❌ `src/citation_extractor.py` → Legacy, superseded by enhanced version
- ❌ `notebooks/Tutorial.ipynb` → Too basic for RAG platform
- ❌ `notebooks/Scientific_Paper_Analyzer.ipynb` → Outdated approach
- ❌ `notebooks/Maximum_Context_Scientific_Analyzer.ipynb` → Replace with RAG version

### **New Files to Create:**
- 🆕 `src/rag_system.py` → Core RAG functionality with persistent storage
- 🆕 `src/knowledge_graph.py` → LangGraph-based entity extraction and relationships
- 🆕 `src/unified_intelligence.py` → RAG + Graph combined query engine
- 🆕 `notebooks/Scientific_RAG_Knowledge_Graph.ipynb` → Main user interface
- 🆕 `database/complete_schema.sql` → Unified schema for RAG + Graph

---

## 🎯 Implementation Strategy

### **Phase 1: Foundation (Week 1-2)**

#### **1.1 Codebase Cleanup**
- Remove legacy files
- Consolidate database schemas  
- Update requirements.txt with LangGraph dependencies
- Restructure src/ for new architecture

#### **1.2 Core RAG System**
```python
# src/rag_system.py
class ScientificRAGSystem:
    def __init__(self):
        self.embeddings = OllamaEmbeddings("nomic-embed-text")
        self.llm = ChatOllama("llama3.1:8b")
        self.vector_store = PostgreSQLVectorStore()
    
    def ingest_paper(self, pdf_path: str) -> str:
        # Extract text, chunk, embed, store
        pass
    
    def query(self, question: str, paper_ids: List[str] = None) -> str:
        # Retrieve relevant chunks, generate answer
        pass
    
    def chat(self, session_id: str, message: str) -> str:
        # Conversational interface with context
        pass
```

#### **1.3 Database Schema Update**
```sql
-- Complete unified schema
-- Papers, embeddings, entities, relationships, chat sessions
```

### **Phase 2: Knowledge Graph (Week 3-4)**

#### **2.1 Entity Extraction**
```python
# src/knowledge_graph.py  
class ScientificKnowledgeGraph:
    def extract_entities(self, paper_content: str) -> List[Entity]:
        # LangGraph workflow for entity extraction
        # Authors, Methods, Concepts, Metrics, Institutions
        pass
    
    def build_relationships(self, entities: List[Entity]) -> List[Relationship]:
        # Citation analysis, method usage, concept relationships
        pass
```

#### **2.2 LangGraph Workflows**
- **Entity Extraction Workflow**: Paper → Entities → Store
- **Relationship Building**: Entities → Relationships → Graph
- **Graph Traversal**: Query → Multi-hop → Results

### **Phase 3: Unified Intelligence (Week 5-6)**

#### **3.1 Combined Query Engine**
```python
# src/unified_intelligence.py
class UnifiedIntelligence:
    def __init__(self):
        self.rag = ScientificRAGSystem()
        self.graph = ScientificKnowledgeGraph()
    
    def intelligent_query(self, question: str) -> IntelligentResponse:
        # Determine if RAG, Graph, or combined approach needed
        # Route query appropriately
        # Merge results intelligently
        pass
```

#### **3.2 Chat Interface**
- Natural language queries
- Context-aware conversations
- Multi-turn interactions
- Source attribution

### **Phase 4: User Interface (Week 7-8)**

#### **4.1 Comprehensive Notebook**
- Paper ingestion workflow
- RAG query examples  
- Knowledge graph exploration
- Visualization capabilities

#### **4.2 Advanced Features**
- Batch processing
- Relationship visualization
- Export capabilities
- Performance analytics

---

## 📋 Detailed Technical Specifications

### **RAG System Architecture:**
```
PDF → Text Extraction → Chunking → Embeddings → PostgreSQL Vector Store
                                                        ↓
User Query → Embedding → Similarity Search → Retrieve Chunks → LLM → Response
```

### **Knowledge Graph Architecture:**
```
Paper Content → LangGraph Entity Extraction → Entities (Authors, Methods, etc.)
                       ↓
             Relationship Detection → Store in Graph DB
                       ↓
User Query → Graph Traversal → Related Entities → Context for RAG
```

### **Database Schema Evolution:**
```sql
-- Core tables (existing, enhanced)
papers (enhanced with graph metadata)
document_embeddings (optimized for retrieval)

-- New knowledge graph tables
entities (id, type, name, properties, paper_id)
relationships (source_id, target_id, type, confidence)
entity_embeddings (entity_id, embedding_vector)

-- Chat and session management
chat_sessions (id, user_id, created_at)
chat_messages (id, session_id, role, content, timestamp)
query_cache (query_hash, results, created_at)
```

### **LangGraph Workflows:**

#### **Entity Extraction Workflow:**
```python
from langgraph.graph import StateGraph, Graph

def entity_extraction_workflow():
    graph = StateGraph()
    
    # Nodes
    graph.add_node("extract_authors", extract_authors_node)
    graph.add_node("extract_methods", extract_methods_node) 
    graph.add_node("extract_concepts", extract_concepts_node)
    graph.add_node("extract_metrics", extract_metrics_node)
    graph.add_node("validate_entities", validate_entities_node)
    
    # Edges
    graph.add_edge("extract_authors", "extract_methods")
    graph.add_edge("extract_methods", "extract_concepts")
    graph.add_edge("extract_concepts", "extract_metrics")
    graph.add_edge("extract_metrics", "validate_entities")
    
    return graph.compile()
```

---

## 🛠️ Development Dependencies

### **New Requirements:**
```txt
# Existing (keep)
langchain>=0.1.0
langchain-community>=0.0.10  
langchain-ollama>=0.1.0
psycopg2-binary>=2.9.0
scikit-learn>=1.6.0

# New additions
langgraph>=0.1.0
networkx>=3.0
pyvis>=0.3.0
spacy>=3.7.0
en_core_web_sm>=3.7.0
```

### **Database Extensions:**
```sql
-- Enable vector and graph capabilities
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS ltree;  -- For hierarchical relationships
```

---

## 🎮 User Experience Flows

### **Paper Ingestion Flow:**
1. Upload PDF → "Processing paper..."
2. Extract text → "Extracting content..."  
3. Generate embeddings → "Creating embeddings..."
4. Extract entities → "Finding authors, methods, concepts..."
5. Build relationships → "Mapping connections..."
6. Ready for queries → "Paper added to knowledge base!"

### **Query Flow:**
1. User types question → "What are the key findings?"
2. System determines approach → RAG + Graph  
3. Retrieve relevant chunks → Show sources
4. Traverse relationships → Show connected concepts
5. Generate comprehensive answer → With attribution
6. Follow-up suggestions → Related questions

### **Knowledge Discovery Flow:**
1. Start with paper → Show its entities
2. Explore relationships → "Papers that cite this"
3. Visual graph → Interactive network
4. Deep dive → RAG analysis of connections
5. Export insights → Research report

---

## 📊 Testing Strategy

### **Unit Tests:**
- RAG embedding and retrieval accuracy
- Entity extraction precision/recall
- Relationship detection confidence
- Query response quality

### **Integration Tests:**
- End-to-end paper ingestion
- RAG + Graph combined queries
- Chat session management
- Database consistency

### **Performance Tests:**
- Query response time (<5s)
- Embedding generation speed
- Graph traversal efficiency
- Concurrent user handling

---

## 🚀 Deployment Plan

### **Local Development:**
- Jupyter notebook interface
- Docker PostgreSQL
- Local Ollama server

### **Production Ready:**
- Web interface (FastAPI + React)
- Cloud PostgreSQL with pgvector
- Container orchestration
- API rate limiting

---

## 📈 Success Metrics

### **Technical KPIs:**
- **RAG Accuracy**: >80% relevant chunks in top-5
- **Entity Extraction**: >90% precision for authors, >85% for methods
- **Response Time**: <5s for 95% of queries
- **Graph Completeness**: >80% of relationships captured

### **User Experience KPIs:**
- **Query Success Rate**: >90% satisfactory answers
- **Session Length**: >10 minutes average
- **Discovery Rate**: >3 new connections per session
- **Retention**: >70% weekly active users

---

**Next Steps:** 
1. Review and approve this plan
2. Execute codebase cleanup
3. Begin Phase 1 implementation
4. Create new unified notebook interface

**Ready to transform scientific paper analysis! 🚀**
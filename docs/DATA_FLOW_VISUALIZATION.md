# GraphRAG MCP Data Flow Visualization

## Dual-Mode Real-Time Data Processing Pipeline

### 1. Document Processing Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DOCUMENT INGESTION PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘

INPUT → PROCESSING → STORAGE → RETRIEVAL → OUTPUT

┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ PDF Document│──▶│ Enhanced        │──▶│ Graphiti        │──▶│ Citation        │──▶│ Neo4j       │
│ (Binary)    │   │ Analyzer        │   │ Processing      │   │ Integration     │   │ Database    │
│             │   │                 │   │                 │   │                 │   │             │
│ • Research  │   │ • 20+ Entities  │   │ • AI Extraction │   │ • 4 Styles      │   │ • Project NS│
│ • Papers    │   │ • Citation Track│   │ • Relationships │   │ • Location Map  │   │ • Persistent│
│ • Citations │   │ • Multi-pass    │   │ • Real-time     │   │ • Usage Track   │   │ • Scalable  │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Metadata    │   │ Section         │   │ Chunk           │   │ Embedding       │   │ Collection  │
│ Extraction  │   │ Identification  │   │ Validation      │   │ Validation      │   │ Management  │
│             │   │                 │   │                 │   │                 │   │             │
│ • Title     │   │ • Abstract      │   │ • Min Length    │   │ • Dimension     │   │ • Namespace │
│ • Authors   │   │ • Methods       │   │ • Max Length    │   │ • Quality       │   │ • Versioning│
│ • Journal   │   │ • Results       │   │ • Coherence     │   │ • Consistency   │   │ • Cleanup   │
│ • DOI       │   │ • Discussion    │   │ • Overlap Check │   │ • Performance   │   │ • Backup    │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
```

### 2. Entity Extraction Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ENTITY EXTRACTION PIPELINE                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

CONTENT → ANALYSIS → EXTRACTION → VALIDATION → STORAGE

┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Text Chunks │──▶│ LLM Processing  │──▶│ Entity Parsing  │──▶│ Deduplication   │──▶│ Graph Store │
│ (Processed) │   │ (Llama 3.1:8b)  │   │ (JSON Format)   │   │ (Set-based)     │   │ (Graphiti)  │
│             │   │                 │   │                 │   │                 │   │             │
│ • 6000 chars│   │ • Temp = 0.1    │   │ • 20+ Categories│   │ • Name Matching │   │ • Nodes     │
│ • 1000 overlap│  │ • Prompt Eng   │   │ • Relationships │   │ • Fuzzy Match   │   │ • Edges     │
│ • Context   │   │ • Retry Logic   │   │ • Confidence    │   │ • Canonical     │   │ • Attributes│
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Multi-Pass  │   │ Error Handling  │   │ Category        │   │ Quality Control │   │ Relationship│
│ Processing  │   │ & Fallback      │   │ Classification  │   │ & Validation    │   │ Building    │
│             │   │                 │   │                 │   │                 │   │             │
│ • Section 1 │   │ • JSON Parse    │   │ • Authors       │   │ • Existence     │   │ • Co-occur  │
│ • Section 2 │   │ • Regex Backup  │   │ • Methods       │   │ • Uniqueness    │   │ • Semantic  │
│ • Section N │   │ • Partial Extr  │   │ • Concepts      │   │ • Completeness  │   │ • Explicit  │
│ • Merge     │   │ • Graceful Deg  │   │ • 17 more...    │   │ • Consistency   │   │ • Weighted  │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
```

### 3. Query Processing Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              QUERY PROCESSING PIPELINE                                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘

QUERY → ANALYSIS → ROUTING → PROCESSING → SYNTHESIS → RESPONSE

┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ User Query  │──▶│ Intent Analysis │──▶│ Mode Selection  │──▶│ Dual Processing │──▶│ Response    │
│ (Natural    │   │ (Keyword Score) │   │ (RAG/Graph/Both)│   │ (Parallel Exec) │   │ Generation  │
│ Language)   │   │                 │   │                 │   │                 │   │             │
│             │   │ • Graph Keywords│   │ • Confidence    │   │ • Vector Search │   │ • Context   │
│ • Question  │   │ • RAG Keywords  │   │ • Fallback      │   │ • Graph Travers │   │ • Entities  │
│ • Intent    │   │ • Complexity    │   │ • Optimization  │   │ • Fusion Logic  │   │ • Citations │
│ • Context   │   │ • History       │   │ • Resource      │   │ • Ranking       │   │ • Metadata  │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Preprocessing│   │ Keyword         │   │ RAG Processing  │   │ Graph Processing│   │ Post-       │
│ & Validation │   │ Extraction      │   │ Path            │   │ Path            │   │ Processing  │
│             │   │                 │   │                 │   │                 │   │             │
│ • Normalize │   │ • "entities"    │   │ • Embed Query   │   │ • Entity Match  │   │ • Format    │
│ • Tokenize  │   │ • "methods"     │   │ • Similarity    │   │ • Relationship  │   │ • Enrich    │
│ • Clean     │   │ • "explain"     │   │ • Top-K Chunks  │   │ • Traverse      │   │ • Validate  │
│ • Validate  │   │ • "findings"    │   │ • Context Build │   │ • Aggregate     │   │ • Cache     │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
```

### 4. Citation Tracking Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CITATION TRACKING PIPELINE                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

DOCUMENT → PATTERN MATCHING → LOCATION MAPPING → CONTEXT EXTRACTION → LINKED REFERENCES

┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Full Text   │──▶│ Citation        │──▶│ Position        │──▶│ Context         │──▶│ Reference   │
│ Document    │   │ Detection       │   │ Tracking        │   │ Extraction      │   │ Linking     │
│             │   │                 │   │                 │   │                 │   │             │
│ • Complete  │   │ • Numbered [1]  │   │ • Char Position │   │ • Sentence      │   │ • Inline →  │
│ • Processed │   │ • Author-Year   │   │ • Line Number   │   │ • Paragraph     │   │   Reference │
│ • Structured│   │ • Superscript   │   │ • Section       │   │ • Section       │   │ • Validation│
│ • Cleaned   │   │ • Full Author   │   │ • Page          │   │ • Purpose       │   │ • Metadata  │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Multi-Format│   │ Pattern         │   │ Precise         │   │ Contextual      │   │ Quality     │
│ Support     │   │ Matching        │   │ Localization    │   │ Understanding   │   │ Assurance   │
│             │   │                 │   │                 │   │                 │   │             │
│ • 4 Formats │   │ • Regex Engine  │   │ • Byte Offset   │   │ • Semantic Role │   │ • Accuracy  │
│ • Flexible  │   │ • Confidence    │   │ • Visual Pos    │   │ • Citation Type │   │ • Coverage  │
│ • Robust    │   │ • Fallback      │   │ • Boundaries    │   │ • Importance    │   │ • Validation│
│ • Extensible│   │ • Optimization  │   │ • Verification  │   │ • Relevance     │   │ • Reporting │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
```

## Data State Transitions

### 5. State Management Across Components

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              STATE TRANSITION DIAGRAM                                  │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│ RAW_PDF     │
│ • Binary    │
│ • Metadata  │
└─────┬───────┘
      │ PyPDFLoader
      ▼
┌─────────────┐
│ EXTRACTED   │
│ • Text      │
│ • Structure │
└─────┬───────┘
      │ TextSplitter
      ▼
┌─────────────┐    ┌─────────────┐
│ CHUNKED     │───▶│ EMBEDDED    │
│ • Segments  │    │ • Vectors   │
│ • Overlap   │    │ • Indexed   │
└─────┬───────┘    └─────┬───────┘
      │                  │
      ▼                  ▼
┌─────────────┐    ┌─────────────┐
│ ANALYZED    │    │ SEARCHABLE  │
│ • Entities  │    │ • Similarity│
│ • Relations │    │ • Retrieval │
└─────┬───────┘    └─────┬───────┘
      │                  │
      ▼                  ▼
┌─────────────┐    ┌─────────────┐
│ GRAPHED     │    │ QUERYABLE   │
│ • Nodes     │    │ • Responses │
│ • Edges     │    │ • Context   │
└─────┬───────┘    └─────┬───────┘
      │                  │
      ▼                  ▼
┌─────────────┐    ┌─────────────┐
│ VISUALIZED  │    │ EXPORTED    │
│ • Layout    │    │ • Formats   │
│ • Interactive│    │ • Portable  │
└─────────────┘    └─────────────┘
```

### 6. Memory Management Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              MEMORY MANAGEMENT PIPELINE                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

LOAD → PROCESS → CACHE → PERSIST → CLEANUP

┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Document    │──▶│ Memory          │──▶│ Runtime Cache   │──▶│ Persistent      │──▶│ Cleanup     │
│ Loading     │   │ Processing      │   │ Management      │   │ Storage         │   │ Management  │
│             │   │                 │   │                 │   │                 │   │             │
│ • Lazy Load │   │ • Chunk Limit   │   │ • LRU Cache     │   │ • ChromaDB      │   │ • Memory    │
│ • Streaming │   │ • Batch Process │   │ • Size Limit    │   │ • File System   │   │ • Disk      │
│ • Validation│   │ • Memory Pool   │   │ • TTL Expire    │   │ • Backup        │   │ • Temp Files│
│ • Metadata  │   │ • Buffer Mgmt   │   │ • Priority      │   │ • Versioning    │   │ • Logs      │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Resource    │   │ Memory          │   │ Cache           │   │ Storage         │   │ Garbage     │
│ Allocation  │   │ Optimization    │   │ Strategy        │   │ Optimization    │   │ Collection  │
│             │   │                 │   │                 │   │                 │   │             │
│ • Pool Size │   │ • Fragmentation │   │ • Hit Rate      │   │ • Compression   │   │ • Weak Refs │
│ • Limits    │   │ • Compaction    │   │ • Miss Penalty  │   │ • Indexing      │   │ • Cleanup   │
│ • Monitoring│   │ • Garbage       │   │ • Eviction      │   │ • Replication   │   │ • Monitoring│
│ • Scaling   │   │ • Profiling     │   │ • Preloading    │   │ • Consistency   │   │ • Reporting │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
```

## Performance Monitoring Data Flow

### 7. Real-Time Performance Tracking

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              PERFORMANCE MONITORING FLOW                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘

METRICS → COLLECTION → AGGREGATION → ANALYSIS → ALERTING

┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ System      │──▶│ Data            │──▶│ Metric          │──▶│ Performance     │──▶│ Health      │
│ Metrics     │   │ Collection      │   │ Aggregation     │   │ Analysis        │   │ Monitoring  │
│             │   │                 │   │                 │   │                 │   │             │
│ • CPU Usage │   │ • Sampling      │   │ • Time Windows  │   │ • Bottlenecks   │   │ • Alerts    │
│ • Memory    │   │ • Logging       │   │ • Statistical   │   │ • Trends        │   │ • Reporting │
│ • I/O       │   │ • Buffering     │   │ • Moving Avg    │   │ • Anomalies     │   │ • Dashboard │
│ • Network   │   │ • Queuing       │   │ • Percentiles   │   │ • Predictions   │   │ • Actions   │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Application │   │ Data            │   │ Time-Series     │   │ Pattern         │   │ Automated   │
│ Metrics     │   │ Preprocessing   │   │ Database        │   │ Recognition     │   │ Response    │
│             │   │                 │   │                 │   │                 │   │             │
│ • Query Time│   │ • Filtering     │   │ • Retention     │   │ • ML Models     │   │ • Scaling   │
│ • Accuracy  │   │ • Normalization │   │ • Compression   │   │ • Thresholds    │   │ • Failover  │
│ • Throughput│   │ • Validation    │   │ • Partitioning  │   │ • Correlations  │   │ • Recovery  │
│ • Errors    │   │ • Enrichment    │   │ • Backup        │   │ • Forecasting   │   │ • Notification│
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
```

### 8. Error Handling Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ERROR HANDLING PIPELINE                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘

ERROR → DETECTION → CLASSIFICATION → RECOVERY → LOGGING → PREVENTION

┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Error       │──▶│ Exception       │──▶│ Error           │──▶│ Recovery        │──▶│ Learning    │
│ Occurrence  │   │ Handling        │   │ Classification  │   │ Strategy        │   │ System      │
│             │   │                 │   │                 │   │                 │   │             │
│ • PDF Parse │   │ • Try/Catch     │   │ • Severity      │   │ • Retry Logic   │   │ • Pattern   │
│ • LLM Error │   │ • Graceful      │   │ • Category      │   │ • Fallback      │   │ • Prevention│
│ • Network   │   │ • Fallback      │   │ • Root Cause    │   │ • Degradation   │   │ • Improvement│
│ • Storage   │   │ • User Message  │   │ • Impact        │   │ • Notification  │   │ • Adaptation│
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Context     │   │ Error           │   │ Recovery        │   │ State           │   │ Continuous  │
│ Preservation│   │ Reporting       │   │ Verification    │   │ Restoration     │   │ Monitoring  │
│             │   │                 │   │                 │   │                 │   │             │
│ • Stack     │   │ • Structured    │   │ • Health Check  │   │ • Rollback      │   │ • Metrics   │
│ • Variables │   │ • Telemetry     │   │ • Validation    │   │ • Consistency   │   │ • Alerts    │
│ • State     │   │ • Alerting      │   │ • Performance   │   │ • Cleanup       │   │ • Trends    │
│ • History   │   │ • Dashboard     │   │ • User Impact   │   │ • Recovery Time │   │ • Insights  │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
```

## Data Consistency and Validation

### 9. Data Quality Assurance Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA QUALITY PIPELINE                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

INPUT → VALIDATION → TRANSFORMATION → VERIFICATION → OUTPUT

┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Raw Data    │──▶│ Schema          │──▶│ Data            │──▶│ Quality         │──▶│ Certified   │
│ Ingestion   │   │ Validation      │   │ Transformation  │   │ Verification    │   │ Data Output │
│             │   │                 │   │                 │   │                 │   │             │
│ • PDF Text  │   │ • Type Check    │   │ • Normalization │   │ • Completeness  │   │ • Validated │
│ • Metadata  │   │ • Format Check  │   │ • Standardization│   │ • Accuracy      │   │ • Enriched  │
│ • Entities  │   │ • Range Check   │   │ • Enrichment    │   │ • Consistency   │   │ • Consistent│
│ • Relations │   │ • Constraint    │   │ • Deduplication │   │ • Integrity     │   │ • Reliable  │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────┐
│ Data        │   │ Business        │   │ Data            │   │ Automated       │   │ Quality     │
│ Profiling   │   │ Rules           │   │ Lineage         │   │ Testing         │   │ Metrics     │
│             │   │ Validation      │   │ Tracking        │   │ & Monitoring    │   │ Reporting   │
│             │   │                 │   │                 │   │                 │   │             │
│ • Statistics│   │ • Domain Rules  │   │ • Source Track  │   │ • Unit Tests    │   │ • Dashboards│
│ • Patterns  │   │ • Relationships │   │ • Transform Log │   │ • Integration   │   │ • Alerts    │
│ • Anomalies │   │ • Dependencies  │   │ • Version Ctrl  │   │ • Regression    │   │ • Trends    │
│ • Trends    │   │ • Constraints   │   │ • Audit Trail   │   │ • Performance   │   │ • SLA Track │
└─────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────┘
```

This comprehensive data flow visualization demonstrates the sophisticated data processing pipeline that transforms raw PDF documents into searchable, analyzable knowledge graphs while maintaining data quality, performance, and reliability throughout the entire system.
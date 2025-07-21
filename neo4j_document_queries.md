# Neo4j Browser Queries for Literature Management

## Document Storage and Management

### 1. View All Documents
```cypher
MATCH (doc:Document)
RETURN doc.title, doc.authors, doc.year, doc.processing_status, doc.uploaded_date
ORDER BY doc.uploaded_date DESC
```

### 2. Check Processing Status
```cypher
MATCH (doc:Document)
WITH doc.processing_status as status, count(*) as count
RETURN status, count
ORDER BY count DESC
```

### 3. Find Documents by Author
```cypher
MATCH (doc:Document)
WHERE any(author IN doc.authors WHERE author CONTAINS "Smith")
RETURN doc.title, doc.authors, doc.year
```

### 4. Find Documents by Year Range
```cypher
MATCH (doc:Document)
WHERE doc.year >= 2020 AND doc.year <= 2024
RETURN doc.title, doc.year, doc.journal
ORDER BY doc.year DESC
```

### 5. Documents with Processing Errors
```cypher
MATCH (doc:Document)
WHERE doc.processing_status = "failed" OR doc.processing_status = "error"
RETURN doc.title, doc.pdf_path, doc.processing_status
```

### 6. Mark Document for Reprocessing
```cypher
MATCH (doc:Document {title: "Your Paper Title Here"})
SET doc.processing_status = "pending",
    doc.reprocess_requested = datetime()
RETURN doc.title, doc.processing_status
```

### 7. View Document with Extracted Entities
```cypher
MATCH (doc:Document)-[:CONTAINS_ENTITY]->(entity:Entity)
WHERE doc.title CONTAINS "knowledge graph"
RETURN doc.title, collect(entity.name) as entities
```

### 8. Literature Statistics
```cypher
MATCH (doc:Document)
RETURN 
  count(*) as total_documents,
  avg(doc.file_size) as avg_file_size,
  min(doc.year) as earliest_year,
  max(doc.year) as latest_year,
  count(DISTINCT doc.journal) as unique_journals
```

## Batch Processing Management

### 9. Start Batch Processing Queue
```cypher
MATCH (doc:Document)
WHERE doc.processing_status = "pending"
SET doc.processing_status = "queued",
    doc.queue_time = datetime()
RETURN count(*) as documents_queued
```

### 10. Processing Time Analysis
```cypher
MATCH (doc:Document)
WHERE doc.processing_end IS NOT NULL AND doc.processing_start IS NOT NULL
WITH doc, duration.between(doc.processing_start, doc.processing_end) as processing_time
RETURN 
  doc.title,
  processing_time.seconds as processing_seconds,
  doc.file_size
ORDER BY processing_time.seconds DESC
LIMIT 10
```

### 11. Clear Failed Documents for Retry
```cypher
MATCH (doc:Document)
WHERE doc.processing_status = "failed"
SET doc.processing_status = "pending",
    doc.retry_count = coalesce(doc.retry_count, 0) + 1,
    doc.last_retry = datetime()
RETURN count(*) as documents_reset_for_retry
```

### 12. Find Duplicate Documents
```cypher
MATCH (doc1:Document), (doc2:Document)
WHERE doc1.doi = doc2.doi AND id(doc1) < id(doc2) AND doc1.doi IS NOT NULL
RETURN doc1.title, doc2.title, doc1.doi
```

## Research Queries

### 13. Documents by Research Area
```cypher
MATCH (doc:Document)
WHERE any(keyword IN doc.keywords WHERE keyword CONTAINS "machine learning")
RETURN doc.title, doc.authors, doc.year, doc.keywords
```

### 14. Citation Network Analysis
```cypher
MATCH (doc1:Document)-[:CONTAINS_ENTITY]->(entity:Entity)<-[:CONTAINS_ENTITY]-(doc2:Document)
WHERE doc1 <> doc2
WITH doc1, doc2, count(entity) as shared_entities
WHERE shared_entities > 3
RETURN doc1.title, doc2.title, shared_entities
ORDER BY shared_entities DESC
```

### 15. Export Processing Report
```cypher
MATCH (doc:Document)
OPTIONAL MATCH (doc)-[:CONTAINS_ENTITY]->(entity:Entity)
RETURN 
  doc.title,
  doc.authors,
  doc.year,
  doc.journal,
  doc.processing_status,
  doc.uploaded_date,
  doc.pdf_path,
  count(entity) as entity_count
ORDER BY doc.uploaded_date DESC
```

## Workflow Integration

### 16. Get Next Document for Processing
```cypher
MATCH (doc:Document)
WHERE doc.processing_status = "pending"
WITH doc
ORDER BY doc.uploaded_date ASC
LIMIT 1
SET doc.processing_status = "processing",
    doc.processing_start = datetime()
RETURN doc.pair_id, doc.pdf_path, doc.ris_path, doc.title
```

### 17. Update Processing Progress
```cypher
MATCH (doc:Document {pair_id: $document_id})
SET doc.processing_status = $status,
    doc.last_updated = datetime()
RETURN doc.title, doc.processing_status
```

### 18. Link Extracted Entities to Document
```cypher
MATCH (doc:Document {pair_id: $document_id})
MATCH (entity:Entity)
WHERE entity.source_document = $document_id
CREATE (doc)-[:CONTAINS_ENTITY]->(entity)
RETURN count(*) as entities_linked
```
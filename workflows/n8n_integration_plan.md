# n8n Workflow Integration Plan
## DocsGPT + LlamaParse + Knowledge Graph

---

## **Workflow Overview**

```
DocsGPT "Process Files" → Webhook → LlamaParse → Entity Extraction → Direct Storage → Response
```

### **Goal**: 
When users click "Process Files" in DocsGPT batch upload, trigger n8n workflow that processes PDFs with LlamaParse and stores results directly in Neo4j + ChromaDB.

---

## **Step-by-Step Implementation Plan**

### **Phase 1: DocsGPT Integration**

#### **1.1 Add Webhook Call to DocsGPT**
**File**: `docsgpt-source/application/api/knowledge/upload_routes.py`

```python
# Add to batch processing endpoint
import requests

@blueprint.route("/batch-process", methods=["POST"])
def batch_process_files():
    files = request.json.get('files', [])
    user_id = request.json.get('user_id')
    batch_id = str(uuid.uuid4())
    
    # Trigger n8n webhook
    webhook_payload = {
        "batch_id": batch_id,
        "user_id": user_id,
        "files": [{"path": f.path, "name": f.name} for f in files],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            "http://localhost:5678/webhook/docsgpt-batch-process",
            json=webhook_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return {"status": "processing", "batch_id": batch_id}
        else:
            return {"error": "Failed to trigger processing"}, 500
            
    except requests.RequestException:
        return {"error": "Processing service unavailable"}, 503
```

#### **1.2 Add Processing Status Endpoint**
```python
@blueprint.route("/batch-status/<batch_id>", methods=["GET"])
def get_batch_status(batch_id):
    # Check processing status from database or cache
    # Return current status to frontend
    pass
```

### **Phase 2: n8n Workflow Development**

#### **2.1 Webhook Trigger Node**
**Configuration**:
```json
{
  "type": "nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "docsgpt-batch-process",
    "responseMode": "lastNode",
    "responseData": "allEntries",
    "authentication": "none"
  }
}
```

**Expected Input**:
```json
{
  "batch_id": "uuid",
  "user_id": "string",
  "files": [{"path": "/path/to/file.pdf", "name": "file.pdf"}],
  "timestamp": "2025-01-26T..."
}
```

#### **2.2 Process Each File Node (Loop)**
**Configuration**: Split in batches to handle multiple files
```json
{
  "type": "nodes-base.splitInBatches",
  "parameters": {
    "batchSize": 1,
    "options": {}
  }
}
```

#### **2.3 LlamaParse API Call Node**
**Configuration**:
```json
{
  "type": "nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.cloud.llamaindex.ai/api/parsing/upload",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Authorization", 
          "value": "Bearer {{ $credentials.llamaParseApi.apiKey }}"
        }
      ]
    },
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "result_type",
          "value": "markdown"
        },
        {
          "name": "premium_mode", 
          "value": "true"
        }
      ]
    },
    "sendBinaryData": true,
    "binaryPropertyName": "file"
  }
}
```

#### **2.4 Wait for Processing Node**
```json
{
  "type": "nodes-base.wait",
  "parameters": {
    "unit": "seconds",
    "amount": 30
  }
}
```

#### **2.5 Get LlamaParse Results Node**
```json
{
  "type": "nodes-base.httpRequest",
  "parameters": {
    "method": "GET",
    "url": "https://api.cloud.llamaindex.ai/api/parsing/job/{{ $json.id }}/result/markdown",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth"
  }
}
```

#### **2.6 Entity Extraction Node (OpenAI)**
**Configuration**:
```json
{
  "type": "nodes-base.openAi",
  "parameters": {
    "resource": "chat",
    "operation": "message", 
    "modelId": "gpt-4",
    "messages": {
      "values": [
        {
          "role": "system",
          "content": "You are an expert at extracting entities and relationships from academic chemistry papers. Extract entities (compounds, authors, methods, results) and relationships from the provided text. Return as JSON with entities and relationships arrays."
        },
        {
          "role": "user",
          "content": "{{ $json.markdown }}"
        }
      ]
    },
    "options": {
      "temperature": 0.1,
      "maxTokens": 4000
    }
  }
}
```

#### **2.7 Create Systematic Text Chunks Node**
**Configuration**: Code node to chunk text systematically
```json
{
  "type": "nodes-base.code",
  "parameters": {
    "jsCode": "// Systematic chunking code (300 words + 75 overlap)\nconst text = $json.markdown;\nconst chunks = createSystematicChunks(text, 300, 75);\nreturn [{ json: { chunks, originalText: text } }];"
  }
}
```

#### **2.8 Store in Neo4j Node**
**Configuration**: 
```json
{
  "type": "nodes-base.httpRequest", 
  "parameters": {
    "method": "POST",
    "url": "http://localhost:7474/db/neo4j/tx/commit",
    "authentication": "genericCredentialType",
    "sendBody": true,
    "bodyParameters": {
      "statements": [
        {
          "statement": "CREATE (d:Document {id: $doc_id, title: $title}) RETURN d",
          "parameters": {
            "doc_id": "{{ $json.document_id }}",
            "title": "{{ $json.title }}"
          }
        }
      ]
    }
  }
}
```

#### **2.9 Store in ChromaDB Node**
**Configuration**: HTTP request to ChromaDB
```json
{
  "type": "nodes-base.httpRequest",
  "parameters": {
    "method": "POST", 
    "url": "http://localhost:8000/api/v1/collections/knowledge_graph/add",
    "sendBody": true,
    "bodyParameters": {
      "documents": "{{ $json.chunks }}",
      "metadatas": "{{ $json.metadata }}",
      "ids": "{{ $json.chunk_ids }}"
    }
  }
}
```

#### **2.10 Send Completion Response Node**
**Configuration**: Respond to DocsGPT
```json
{
  "type": "nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "http://localhost:5173/api/batch-complete",
    "sendBody": true,
    "bodyParameters": {
      "batch_id": "{{ $('Webhook').first().json.batch_id }}",
      "status": "completed",
      "results": {
        "entities_count": "{{ $json.entities.length }}",
        "chunks_count": "{{ $json.chunks.length }}"
      }
    }
  }
}
```

### **Phase 3: Database Integration**

#### **3.1 Neo4j Connection Setup**
- Configure Neo4j HTTP API credentials in n8n
- Test connection with simple query
- Set up proper error handling

#### **3.2 ChromaDB Integration** 
- Set up ChromaDB HTTP API endpoint
- Configure embedding service endpoint
- Test vector storage and retrieval

#### **3.3 Data Format Standardization**
Ensure n8n stored data matches MCP tool format:
```json
{
  "entities": [
    {
      "id": "string",
      "name": "string", 
      "type": "string",
      "properties": {},
      "confidence": 0.9
    }
  ],
  "relationships": [
    {
      "source": "entity_id",
      "target": "entity_id",
      "type": "string",
      "context": "string"
    }
  ]
}
```

### **Phase 4: Testing & Validation**

#### **4.1 Unit Testing**
- Test each n8n node individually
- Validate LlamaParse integration
- Test entity extraction quality
- Verify database storage

#### **4.2 Integration Testing**
- End-to-end workflow testing
- DocsGPT → n8n → Database → Query
- Error handling scenarios
- Large file processing

#### **4.3 Performance Testing**
- Multiple file processing
- Concurrent batch handling
- Memory usage monitoring
- Processing time benchmarks

---

## **Implementation Priority**

### **Week 1: Core Workflow**
1. Set up n8n webhook endpoint
2. Implement LlamaParse integration  
3. Basic entity extraction with OpenAI
4. Simple storage in Neo4j

### **Week 2: DocsGPT Integration**
1. Add webhook calls to DocsGPT
2. Implement status tracking
3. Frontend status display
4. Error handling

### **Week 3: Enhanced Processing**
1. Systematic text chunking
2. ChromaDB vector storage
3. Batch processing optimization
4. Quality validation

### **Week 4: Polish & Testing**
1. Comprehensive error handling
2. Performance optimization
3. User feedback integration
4. Documentation

---

## **Required n8n Nodes**

### **Core Nodes**:
- `nodes-base.webhook` - Receive DocsGPT requests
- `nodes-base.httpRequest` - LlamaParse API calls
- `nodes-base.openAi` - Entity extraction
- `nodes-base.code` - Text processing
- `nodes-base.splitInBatches` - Handle multiple files

### **Database Nodes**:
- `nodes-base.httpRequest` - Neo4j HTTP API
- `nodes-base.httpRequest` - ChromaDB HTTP API

### **Utility Nodes**:
- `nodes-base.wait` - Processing delays
- `nodes-base.if` - Conditional logic
- `nodes-base.merge` - Combine results

---

## **Configuration Requirements**

### **Credentials**:
- LlamaParse API key
- OpenAI API key  
- Neo4j authentication
- ChromaDB endpoint

### **Environment Variables**:
- `NEO4J_URI`
- `CHROMADB_URL`
- `DOCSGPT_URL`
- `N8N_WEBHOOK_URL`

---

## **Success Metrics**

1. **Functionality**: Files uploaded in DocsGPT → Processed by n8n → Queryable in knowledge graph
2. **Performance**: <2 minutes processing per chemistry paper
3. **Reliability**: >95% success rate on valid PDFs
4. **Integration**: Seamless UX within DocsGPT interface
5. **Quality**: Entity extraction quality comparable to manual MCP processing

---

## **Next Steps**

1. **Review this plan** with project requirements
2. **Set up n8n environment** and test basic webhook
3. **Implement Phase 1** DocsGPT webhook integration
4. **Build core n8n workflow** with LlamaParse + OpenAI
5. **Test with sample chemistry papers** from Literature folder

This plan provides a complete roadmap for building the integrated DocsGPT + n8n + LlamaParse workflow with direct database storage.
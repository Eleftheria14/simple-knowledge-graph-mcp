# DocsGPT + n8n Integration Architecture Guide

## Overview
This document outlines the correct architecture and implementation for integrating DocsGPT with n8n workflows for automated document processing using LlamaParse and knowledge graph storage.

## Problem Statement
Initial attempts to integrate DocsGPT with n8n workflows failed due to:
- **n8n HTTP Request binary upload issues**: `n8nBinaryData` parameter consistently results in empty `"file": ""` parameters
- **Docker networking complexity**: API calls between containers failing with HTTP 500 errors
- **Wrong integration pattern**: Attempting API-based file transfers instead of leveraging shared volumes

## Solution Architecture

### Docker Container Setup
```
Container Network: docsgpt-oss_default (172.18.0.0/16)

┌─────────────────────────────────────────────────────────────────┐
│  Container Name          │ Internal IP  │ External Port │ Role   │
├─────────────────────────────────────────────────────────────────┤
│ docsgpt-oss-backend-1    │ 172.18.0.8   │ :7091        │ API    │
│ docsgpt-oss-frontend-1   │ 172.18.0.9   │ :5173        │ UI     │
│ docsgpt-oss-worker-1     │ 172.18.0.7   │ internal     │ Tasks  │
│ docsgpt-oss-n8n-1       │ 172.18.0.6   │ :5678        │ n8n    │
│ docsgpt-oss-redis-1      │ 172.18.0.2   │ :6379        │ Cache  │
│ docsgpt-oss-mongo-1      │ 172.18.0.5   │ :27017       │ DB     │
│ docsgpt-oss-neo4j-1      │ 172.18.0.3   │ :7474,:7687  │ Graph  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Volume Mounts
```yaml
# Critical shared volume configuration
docsgpt-oss-backend-1:
  volumes:
    - ./application/inputs:/app/inputs  # DocsGPT file storage

docsgpt-oss-n8n-1:
  volumes:
    - ./application/inputs:/data        # Same files accessible to n8n
```

**File Path Mapping:**
- DocsGPT stores: `/app/inputs/local/chemistry-paper.pdf/d4sc03921a.pdf`
- n8n accesses: `/data/local/chemistry-paper.pdf/d4sc03921a.pdf`

## Correct Integration Pattern: Shared Volume Approach

### Why This Works
1. **No API calls between containers** - eliminates HTTP compatibility issues
2. **Direct file system access** - fastest and most reliable
3. **Proper n8n binary handling** - uses `sendBinaryData: true` correctly
4. **Leverages existing volume sharing** - no infrastructure changes needed

### Data Flow
```
User Upload → DocsGPT Backend → File Storage (/app/inputs)
                     ↓
              Webhook Trigger (with file path)
                     ↓
              n8n Workflow → Read File (/data/inputs) → LlamaParse → Process → Store
```

## Implementation Steps

### Step 1: Working n8n Workflow
**File:** `workflows/WORKING_SHARED_VOLUME.json`

Key components:
```json
{
  "nodes": [
    {
      "name": "DocsGPT Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "working-shared-volume"
      }
    },
    {
      "name": "Read PDF File", 
      "type": "n8n-nodes-base.readBinaryFile",
      "parameters": {
        "filePath": "/data/local/chemistry-paper.pdf/d4sc03921a.pdf"
      }
    },
    {
      "name": "LlamaParse Upload",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "sendBinaryData": true,
        "binaryPropertyName": "data",
        "contentType": "multipart-form-data"
      }
    }
  ]
}
```

### Step 2: DocsGPT Webhook Integration  
**File:** `docsgpt-source/application/api/user/routes.py`

Current implementation (lines 662-722):
```python
# Generate batch ID for n8n workflow
batch_id = str(uuid.uuid4())

# Prepare webhook payload for n8n
webhook_payload = {
    'batch_id': batch_id,
    'user_id': user,
    'batch_name': job_name,
    'files': [{
        'name': filename,
        'path': file_path,                          # DocsGPT internal path
        'n8n_path': f'/data/local/{dir_name}/{filename}',  # n8n accessible path
        'user': safe_user,
        'job_name': dir_name
    }],
    'timestamp': datetime.datetime.now().isoformat(),
    'total_files': 1
}

# Trigger n8n workflow instead of Celery
try:
    response = requests.post(
        'http://docsgpt-oss-n8n-1:5678/webhook/working-shared-volume',
        json=webhook_payload,
        timeout=10
    )
```

### Step 3: Complete Workflow Pipeline
**Recommended workflow structure:**
1. **Webhook Trigger** - Receives DocsGPT file metadata
2. **Read Binary File** - Loads PDF from shared volume 
3. **LlamaParse Upload** - Processes PDF to markdown
4. **Wait Node** - Allows processing time (45 seconds)
5. **Get Results** - Retrieves processed content
6. **MCP Knowledge Graph** - Stores entities and text vectors
7. **Response** - Returns processing status

## Debugging Lessons Learned

### What Didn't Work
1. **URL-based approach**: `input_url` parameter with DocsGPT download API
   - Problem: API endpoint incompatibility and authentication issues
   
2. **n8n Binary Upload**: Multiple attempts with `n8nBinaryData`, `formBinaryData`, etc.
   - Problem: n8n HTTP Request node binary handling is fundamentally broken
   
3. **Manual HTTP requests in Code nodes**: Attempted direct multipart form construction
   - Problem: n8n sandbox restrictions block Node.js core modules

### What Works
1. **Shared volume file access** - Direct file system reads
2. **`sendBinaryData: true`** - Proper n8n binary parameter handling  
3. **Docker container networking** - Service name resolution works correctly
4. **Webhook integration** - Event-driven architecture scales well

## Directory Structure
```
/Users/aimiegarces/Agents/
├── docs/
│   └── DOCSGPT_N8N_INTEGRATION_GUIDE.md        # This document
├── workflows/
│   ├── WORKING_SHARED_VOLUME.json              # Production workflow
│   ├── CORRECT_SHARED_VOLUME.json              # Dynamic path version
│   └── [Various debugging workflows]           # Historical attempts
├── docsgpt-source/
│   └── application/
│       ├── api/user/routes.py                  # Webhook integration point
│       └── inputs/                             # Shared volume mount point
└── src/                                        # MCP Knowledge Graph tools
```

## Testing Commands

### Manual Workflow Testing
```bash
# Test webhook trigger
curl -X POST http://localhost:5678/webhook/working-shared-volume \
  -H "Content-Type: application/json" \
  -d '{"batch_id": "test", "files": [{"name": "d4sc03921a.pdf"}]}'

# Check n8n logs
docker logs docsgpt-oss-n8n-1 --tail 10

# Verify file accessibility
docker exec docsgpt-oss-n8n-1 ls -la /data/local/chemistry-paper.pdf/
```

### Container Status Verification
```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}"

# Verify volume mounts
docker inspect docsgpt-oss-backend-1 | grep -A 10 '"Mounts"'
docker inspect docsgpt-oss-n8n-1 | grep -A 10 '"Mounts"'

# Test container networking
docker exec docsgpt-oss-n8n-1 curl -I http://docsgpt-oss-backend-1:7091/
```

## Next Development Steps

### Phase 1: Core Integration (Completed)
- [x] Identify correct shared volume architecture
- [x] Create working n8n workflow with hardcoded paths
- [x] Implement DocsGPT webhook trigger

### Phase 2: Dynamic Processing (In Progress)  
- [ ] Update webhook payload with dynamic n8n paths
- [ ] Test dynamic file path workflow
- [ ] Add error handling and status reporting

### Phase 3: Full Pipeline Integration
- [ ] Add MCP knowledge graph storage nodes
- [ ] Implement entity extraction with Claude
- [ ] Add systematic text chunking for complete coverage
- [ ] Create user feedback and progress tracking

### Phase 4: Production Readiness
- [ ] Add comprehensive error handling
- [ ] Implement retry logic for failed workflows
- [ ] Add monitoring and logging
- [ ] Create user documentation and tutorials

## Key Success Factors

1. **Use shared volumes, not API calls** - Eliminates compatibility issues
2. **Leverage n8n's native binary handling** - `sendBinaryData: true` works reliably  
3. **Keep workflows simple initially** - Hardcode paths, then make dynamic
4. **Use Docker service names** - `docsgpt-oss-backend-1` resolves correctly
5. **Event-driven architecture** - Webhooks scale better than polling

## Architecture Benefits

- **Scalability**: Event-driven processing handles multiple documents
- **Reliability**: Shared volumes eliminate network failure points  
- **Performance**: Direct file access is fastest approach
- **Maintainability**: Clear separation between DocsGPT and n8n concerns
- **Extensibility**: n8n workflows can easily add new processing steps

This architecture provides a robust foundation for automated document processing while maintaining the flexibility to extend with additional AI services and knowledge graph capabilities.
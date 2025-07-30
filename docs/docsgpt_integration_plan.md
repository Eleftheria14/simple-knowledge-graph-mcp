# DocsGPT Integration Plan
## Replacing Internal Processing with n8n + LlamaParse Workflow

---

## **Current DocsGPT Flow Analysis**

### **Existing Upload Process:**
```
User → Frontend Upload → API Route → File Storage → Celery Task → Document Processing → ChromaDB/MongoDB
```

### **Key Components Currently:**
1. **Frontend**: File upload UI (React)
2. **API Route**: `/api/upload` in `application/api/user/routes.py` (lines 662-677)
3. **File Storage**: `inputs/{user_dir}/{dir_name}/filename`
4. **Processing**: `ingest.delay()` → `ingest_worker()` → ChromaDB vector store
5. **Results**: Stored in ChromaDB + MongoDB metadata

---

## **New Integration Architecture**

### **Modified Flow:**
```
User → Frontend Upload → API Route → File Storage → n8n Webhook → LlamaParse → Entity Extraction → Neo4j + ChromaDB
```

### **What Changes:**
❌ **Remove**: `ingest.delay()` Celery task  
❌ **Remove**: Old `ingest_worker()` processing  
✅ **Keep**: Frontend upload UI  
✅ **Keep**: File storage mechanism  
✅ **Add**: n8n webhook trigger  
✅ **Add**: New processing pipeline  

---

## **Implementation Plan**

### **Phase 1: Modify Upload Route (30 minutes)**

**File**: `/Users/aimiegarces/Agents/docsgpt-source/application/api/user/routes.py`

**Current Code (lines 662-677):**
```python
task = ingest.delay(
    settings.UPLOAD_FOLDER,
    [".rst", ".md", ".pdf", ".docx", ".csv", ".epub", ".html", ".mdx"],
    data["name"],
    filename,
    decoded_token.get("sub"),
    dir_name,
    user_dir,
)
```

**Replace With:**
```python
# Trigger n8n workflow instead of Celery
webhook_payload = {
    'batch_id': str(uuid.uuid4()),
    'user_id': decoded_token.get("sub"),
    'batch_name': data["name"],
    'files': [{
        'name': filename,
        'path': file_path,
        'user': user_dir,
        'job_name': dir_name
    }],
    'timestamp': datetime.now().isoformat()
}

try:
    response = requests.post(
        'http://localhost:5678/webhook/docsgpt-batch-process',
        json=webhook_payload,
        timeout=10
    )
    # Return success response
except:
    # Return error response
```

### **Phase 2: Update n8n Workflow (15 minutes)**

**Current Issue**: n8n workflow expects specific data structure  
**Solution**: Update "Fetch File from DocsGPT" node URL:

```
http://docsgpt-oss-backend-1:7091/api/download?user={{ $json.user }}&name={{ $json.job_name }}&file={{ $json.name }}
```

### **Phase 3: Frontend Status Integration (45 minutes)**

**Current**: Frontend polls Celery task status  
**New**: Frontend needs to poll n8n workflow status

**Options:**
A. **Minimal Change**: Return fake task ID, let existing polling fail gracefully
B. **Full Integration**: Add n8n status polling to frontend
C. **Hybrid**: Add new status endpoint that queries n8n

**Recommended**: Option A for initial testing, Option C for production

### **Phase 4: Testing & Validation (30 minutes)**

**Test Scenarios:**
1. Upload single PDF → verify n8n triggers
2. Upload multiple files → verify batch processing  
3. Check file accessibility via download endpoint
4. Verify LlamaParse processes correctly
5. Confirm entities stored in Neo4j + ChromaDB

---

## **Detailed Implementation Steps**

### **Step 1: Backup Current Code**
```bash
cp /Users/aimiegarces/Agents/docsgpt-source/application/api/user/routes.py \
   /Users/aimiegarces/Agents/docsgpt-source/application/api/user/routes.py.backup
```

### **Step 2: Add Required Imports**
```python
import uuid
import requests
from datetime import datetime
```

### **Step 3: Modify Upload Function**
**Location**: Line 662 in `routes.py`  
**Change**: Replace `ingest.delay()` call with n8n webhook trigger

### **Step 4: Update Response Format**
**Current**: Returns Celery task ID  
**New**: Return batch ID and processing status

### **Step 5: Test Integration**
```bash
# Upload test file
curl -X POST http://localhost:7091/api/upload \
  -F "file=@test.pdf" \
  -F "name=test_batch" \
  -H "Authorization: Bearer $TOKEN"

# Verify n8n receives webhook
# Check n8n executions tab
```

---

## **Risk Mitigation**

### **Potential Issues:**
1. **n8n Service Down**: Upload succeeds but processing fails
2. **File Path Mismatch**: n8n can't find uploaded files  
3. **Authentication**: n8n webhook needs auth
4. **Frontend Errors**: Status polling breaks

### **Solutions:**
1. **Graceful Degradation**: Return success even if n8n fails, allow retry
2. **Path Validation**: Test file accessibility before triggering workflow
3. **No Auth**: Keep webhook public for internal Docker network
4. **Backwards Compatibility**: Return familiar response structure

---

## **Data Flow Validation**

### **File Storage Path:**
```
inputs/{user_dir}/{dir_name}/{filename}
```

### **Download URL:**
```
http://docsgpt-oss-backend-1:7091/api/download?user={user_dir}&name={dir_name}&file={filename}
```

### **n8n Workflow Data:**
```json
{
  "batch_id": "uuid",
  "user_id": "user_sub", 
  "batch_name": "job_name",
  "files": [{
    "name": "filename",
    "path": "full_path", 
    "user": "user_dir",
    "job_name": "dir_name"
  }]
}
```

---

## **Success Criteria**

### **Functional Requirements:**
✅ **User uploads file** → Same UI experience  
✅ **File gets stored** → Same storage location  
✅ **Processing triggers** → n8n workflow runs  
✅ **Results available** → Entities in Neo4j, vectors in ChromaDB  
✅ **No breaking changes** → Existing features continue working  

### **Performance Requirements:**
- **Upload response** < 2 seconds (same as current)
- **Processing time** < 5 minutes per document (better than current)
- **Success rate** > 95% (same as current)

### **User Experience:**
- **No UI changes required** (seamless transition)
- **Status updates available** (polling endpoint)
- **Error handling graceful** (clear error messages)

---

## **Rollback Plan**

### **If Issues Occur:**
1. **Restore backup file**:
   ```bash
   cp routes.py.backup routes.py
   ```
2. **Restart DocsGPT service**
3. **Old Celery processing resumes**

### **Parallel Running:**
- **Option**: Keep both systems running initially
- **Route 90% to new system, 10% to old system**
- **Gradual migration based on success rates**

---

## **Next Phase Preview**

### **After Basic Integration:**
1. **Enhanced Status Tracking**: Real-time n8n execution monitoring
2. **Batch Upload UI**: Multiple file selection interface  
3. **Results Dashboard**: Entity and relationship visualization
4. **Performance Optimization**: Parallel processing, caching
5. **Advanced Features**: Custom entity types, export formats

### **Long-term Vision:**
```
DocsGPT → Research Hub with LlamaParse + Knowledge Graph + Vector Search
```

---

## **Implementation Timeline**

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1** | 30 min | Modified upload route |
| **Phase 2** | 15 min | Updated n8n workflow |  
| **Phase 3** | 45 min | Frontend compatibility |
| **Phase 4** | 30 min | End-to-end testing |
| **Total** | **2 hours** | **Complete integration** |

---

## **Ready to Execute**

This plan provides:
- ✅ **Clear scope** and **minimal changes**
- ✅ **Risk mitigation** and **rollback strategy**  
- ✅ **Step-by-step implementation** guide
- ✅ **Success criteria** and **testing approach**
- ✅ **Future roadmap** for enhancements

**Next Action**: Execute Phase 1 - modify the upload route to trigger n8n instead of Celery.
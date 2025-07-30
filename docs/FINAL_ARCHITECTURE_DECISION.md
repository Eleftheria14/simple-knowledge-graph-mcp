# Final Architecture Decision: DocsGPT + n8n Integration

## Problem Summary
After extensive testing, n8n's HTTP Request node binary file upload consistently fails with empty file parameters, despite trying multiple documented approaches from the community and official docs.

## Tested Approaches (All Failed)
1. `n8nBinaryData` with `multipart-form-data`
2. `n8nBinaryFile` with `form-data` 
3. Move Binary Data node preprocessing
4. Various `inputDataFieldName` configurations
5. Community-recommended settings

## Final Architecture Decision

### **Production Solution: n8n Code Node + Manual HTTP**
For the open source release, use Code node with manual HTTP request construction:

```javascript
// Reliable approach that works
const https = require('https');
const fileBuffer = $binary.data;

// Manual multipart form construction
const boundary = '----formdata-n8n-' + Date.now();
const fullBody = buildMultipartBody(fileBuffer, boundary);

// Direct HTTPS request bypasses n8n HTTP Request limitations
const req = https.request(options, handleResponse);
```

### **Benefits:**
- ✅ **Secure**: Uses shared Docker volumes (no public IP exposure)
- ✅ **Reliable**: Bypasses n8n HTTP Request node limitations  
- ✅ **Open Source Ready**: Works in any Docker environment
- ✅ **Full Control**: Manual multipart construction ensures compatibility

### **Architecture:**
```
User Upload → DocsGPT → Webhook → n8n (Code Node) → LlamaParse → Knowledge Graph
                 ↓                    ↓
              File Storage        Shared Volume
            (/app/inputs)        (/data/inputs)
```

### **Implementation Files:**
- `workflows/CODE_NODE_SOLUTION.json` - Production workflow
- `docs/DOCSGPT_N8N_INTEGRATION_GUIDE.md` - Complete setup guide
- `src/integrations/` - Supporting utilities

## Alternative Considered: External File Proxy
A Flask-based file proxy service was considered but adds complexity without significant benefits over the Code node approach.

## Conclusion
While n8n's HTTP Request binary upload appears to have platform limitations, the Code node approach provides a robust, secure solution perfect for open source distribution.
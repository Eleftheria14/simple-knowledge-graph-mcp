# Open WebUI + n8n + MCP Knowledge Graph Integration Plan

## Architecture Overview

```
PDF Upload → Open WebUI → n8n Webhook → MCP Tools → Neo4j + ChromaDB → Results → Open WebUI Chat
```

## Implementation Steps

### Phase 1: Set Up Open WebUI
```bash
# Install Open WebUI with Docker
docker run -d --name open-webui -p 3000:8080 \
  -v open-webui:/app/backend/data \
  --add-host=host.docker.internal:host-gateway \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

### Phase 2: Create n8n Webhook Workflow
```json
{
  "nodes": [
    {
      "name": "OpenWebUI Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "openwebui-pdf-processing",
        "responseMode": "responseNode"
      }
    },
    {
      "name": "Process PDF via MCP",
      "type": "n8n-nodes-mcp.mcp",
      "parameters": {
        "tool": "store_vectors",
        "parameters": {
          "content": "={{ $json.message }}",
          "metadata": {
            "source": "openwebui_upload",
            "user_id": "={{ $json.user }}"
          }
        }
      }
    },
    {
      "name": "Extract Entities",
      "type": "n8n-nodes-mcp.mcp", 
      "parameters": {
        "tool": "store_entities",
        "parameters": {
          "entities": "={{ $json.extracted_entities }}"
        }
      }
    },
    {
      "name": "Query Knowledge Graph",
      "type": "n8n-nodes-mcp.mcp",
      "parameters": {
        "tool": "query_knowledge_graph",
        "parameters": {
          "query": "={{ $json.user_query }}",
          "max_results": 10
        }
      }
    },
    {
      "name": "Return to OpenWebUI",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "options": {
          "responseBody": "={{ JSON.stringify($json) }}"
        }
      }
    }
  ]
}
```

### Phase 3: Install Open WebUI n8n Function
```python
# Open WebUI Function for n8n Integration
import requests
import json

class Tools:
    def __init__(self):
        self.n8n_webhook_url = "http://localhost:5678/webhook/openwebui-pdf-processing"
        
    def process_with_knowledge_graph(self, user_message: str, user_id: str) -> str:
        """
        Process user message through n8n workflow with MCP knowledge graph
        """
        payload = {
            "message": user_message,
            "user": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(self.n8n_webhook_url, json=payload)
            result = response.json()
            
            return f"Knowledge Graph Results: {result.get('summary', 'Processing complete')}"
            
        except Exception as e:
            return f"Error processing request: {str(e)}"
```

### Phase 4: PDF Upload Integration
```python
def handle_pdf_upload(self, file_content: bytes, filename: str, user_id: str) -> str:
    """
    Handle PDF upload and process through knowledge graph
    """
    # Extract text from PDF (simplified)
    extracted_text = self.extract_pdf_text(file_content)
    
    # Send to n8n workflow
    payload = {
        "message": extracted_text,
        "filename": filename,
        "user": user_id,
        "action": "pdf_upload"
    }
    
    response = requests.post(self.n8n_webhook_url, json=payload)
    return f"PDF processed and added to knowledge graph: {filename}"
```

## Benefits of This Approach

### ✅ **Proven Integration**
- Open WebUI ↔ n8n integration already exists
- Community support and examples
- Voice chat capabilities included

### ✅ **Preserves Your MCP System**
- Zero changes to existing MCP tools
- Same Neo4j + ChromaDB backend
- Proven entity extraction logic

### ✅ **User-Friendly Interface**
- Web UI for PDF uploads
- Chat interface for querying
- Real-time processing feedback

### ✅ **Scalable Architecture**
- n8n handles workflow orchestration
- MCP tools handle knowledge graph logic
- Open WebUI provides clean user interface

## Next Steps

1. **Install Open WebUI** (5 minutes)
2. **Create n8n webhook workflow** (30 minutes)
3. **Install n8n function in Open WebUI** (15 minutes)
4. **Test PDF upload → knowledge graph flow** (15 minutes)

Total setup time: ~1 hour to get working system!
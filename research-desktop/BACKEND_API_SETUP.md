# Backend API Server Setup

## Overview

The research-desktop app now uses a clean HTTP API architecture instead of subprocess-based integration. This fixes the issues with:

- ✅ Documents disappearing from UI after processing
- ✅ Slow session loading performance  
- ✅ Missing citations/references display
- ✅ E2BIG errors with large JSON payloads

## Architecture

```
Electron App (Frontend) → HTTP API Server → Backend Tools → Neo4j Database
                     ↘                    ↘
                       Original GROBID    Original MCP Tools
```

## Quick Start

### 1. Start Required Services

```bash
# Start Neo4j database
./scripts/start_services.sh

# Start GROBID service
docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0
```

### 2. Start Backend API Server

```bash
# In research-desktop directory
./start_backend_server.sh
```

The server will start on `http://localhost:8001` with API documentation at `http://localhost:8001/docs`.

### 3. Start Electron App

```bash
npm run dev
```

## API Endpoints

### Documents
- `POST /api/documents` - Store processed document
- `GET /api/documents` - Get all documents  
- `DELETE /api/documents` - Clear all documents
- `GET /api/documents/{id}` - Get document details

### Sessions
- `POST /api/sessions` - Create session
- `GET /api/sessions` - Get all sessions
- `GET /api/sessions/{id}/documents` - Get session documents
- `DELETE /api/sessions/{id}` - Delete session

### Processing
- `POST /api/process-grobid` - Process PDF with GROBID
- `POST /api/documents/{id}/extract-entities` - Extract entities

## Performance Improvements

### React State Optimization
- **Optimistic Updates**: Documents appear immediately in UI after processing
- **Error Resilience**: API failures don't clear existing document list
- **No Slow Reloads**: Batch processing doesn't reload entire session

### Backend Efficiency  
- **Direct Tool Calls**: HTTP API calls existing backend tools directly
- **Proper Error Handling**: Failed requests don't break the application
- **Session Management**: Fast session switching with cached data

## Troubleshooting

### Documents Not Appearing
1. Check if backend API server is running on port 8001
2. Check browser console for API errors
3. Verify Neo4j is running and accessible

### Slow Performance
1. Ensure GROBID Docker container is running
2. Check Neo4j connection and memory settings
3. Monitor API server logs for slow queries

### Citations/References Missing
1. Verify GROBID is processing PDF correctly
2. Check that `result.references` is an array in UI console
3. Ensure API server is mapping fields correctly

## Development

### Adding New Endpoints
1. Add endpoint to `backend_api_server.py`
2. Add IPC handler to `main.js` 
3. Add frontend API call to `preload.js`

### Testing API Server
```bash
# Health check
curl http://localhost:8001/health

# Get documents
curl http://localhost:8001/api/documents

# API documentation
open http://localhost:8001/docs
```

## Files Changed

### New Files
- `backend_api_server.py` - HTTP API server
- `start_backend_server.sh` - Server startup script
- `BACKEND_API_SETUP.md` - This documentation

### Modified Files
- `main.js` - Updated IPC handlers to use HTTP API
- `preload.js` - Fixed field mapping for references/citations
- `src/App.jsx` - Added optimistic updates and error resilience

### Protected Files
- `src/processor/tools/grobid_tool.py` - Read-only GROBID client (chmod 444)
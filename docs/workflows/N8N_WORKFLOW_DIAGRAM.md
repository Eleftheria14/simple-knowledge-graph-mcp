# n8n Workflow Diagram: Batch Research Paper Processing

## Overview
This document provides a comprehensive visual and technical guide for building the n8n workflow that will enable batch processing of research papers through your existing MCP knowledge graph system.

## Complete Workflow Diagram

```
                    📁 BATCH PAPER PROCESSING WORKFLOW
                           
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Manual        │    │  File Upload │    │  PDF to Text    │
│   Trigger       │───▶│  (Multiple   │───▶│  Conversion     │
│   🔘 START      │    │   PDFs)      │    │  📄➡️📝         │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
                                                     ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Split in      │    │  LLM Provider│    │  Set Batch      │
│   Batches       │◀───│  Selection   │◀───│  Configuration  │
│   🔄 One by One │    │  🤖 Choice   │    │  ⚙️ Settings    │
└─────────────────┘    └──────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM PROVIDER ROUTING                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Claude    │  │   GPT-4     │  │   Gemini    │        │
│  │   🔵 API    │  │   🟢 API    │  │   🔴 API    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Entity        │    │  Store       │    │  Store Vectors  │
│   Extraction    │───▶│  Entities    │───▶│  in ChromaDB    │
│   🧠 Analysis   │    │  in Neo4j    │    │  🗃️ Embeddings  │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
                                                     ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Progress      │    │  Error       │    │  Merge Results  │
│   Counter       │◀───│  Handling    │◀───│  📊 Combine     │
│   📈 Tracking   │    │  🚨 Retry    │    │     All Papers  │
└─────────────────┘    └──────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETION & RESULTS                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Generate   │  │    Email    │  │   Save      │        │
│  │  Literature │  │ Notification│  │   Report    │        │
│  │   Review    │  │     📧      │  │     💾      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Workflow Phases

### 📥 Phase 1: Input & Setup
**Goal**: Accept multiple PDFs and configure processing settings

1. **Manual Trigger Node**
   - **Type**: Core > Manual Trigger
   - **Purpose**: Start the workflow execution
   - **Configuration**: Simple button to begin batch processing

2. **File Upload Node** 
   - **Type**: Core > HTTP Request (to your FastAPI `/upload-batch` endpoint)
   - **Purpose**: Accept multiple PDF files for processing
   - **Configuration**: 
     - Method: POST
     - File upload handling
     - Multiple file selection enabled

3. **PDF to Text Conversion**
   - **Type**: HTTP Request (to your FastAPI `/pdf-to-text` endpoint)
   - **Purpose**: Convert all PDFs to text using pdfplumber
   - **Configuration**:
     - Batch processing enabled
     - Text extraction with metadata

### ⚙️ Phase 2: Configuration & Routing
**Goal**: Set processing parameters and choose LLM provider

4. **Set Batch Configuration**
   - **Type**: Core > Set
   - **Purpose**: Configure processing settings
   - **Configuration**:
     - Batch size (papers per batch)
     - Processing timeout
     - Retry attempts
     - Output format preferences

5. **LLM Provider Selection**
   - **Type**: Core > Switch
   - **Purpose**: Route to different AI providers based on settings
   - **Configuration**:
     - Claude API branch
     - OpenAI GPT-4 branch  
     - Google Gemini branch
     - Cost optimization logic

6. **Split in Batches**
   - **Type**: Core > Split In Batches
   - **Purpose**: Process papers one at a time to avoid rate limits
   - **Configuration**:
     - Batch size: 1 (sequential processing)
     - Reset option enabled

### 🤖 Phase 3: LLM Processing
**Goal**: Extract entities and relationships using chosen AI provider

7. **Claude API Node**
   - **Type**: AI > Anthropic Claude
   - **Purpose**: Use Claude for entity extraction
   - **Configuration**:
     - Model: Claude-3.5-Sonnet
     - Your entity extraction prompt
     - Temperature: 0.1 for consistency

8. **GPT-4 API Node**
   - **Type**: AI > OpenAI
   - **Purpose**: Use OpenAI for entity extraction
   - **Configuration**:
     - Model: gpt-4-turbo
     - Same entity extraction prompt
     - Temperature: 0.1

9. **Gemini API Node**
   - **Type**: Core > HTTP Request
   - **Purpose**: Use Google Gemini via API
   - **Configuration**:
     - Custom HTTP request to Gemini API
     - Prompt formatting for Gemini
     - Response parsing

### 💾 Phase 4: Data Storage
**Goal**: Store extracted entities and text in your knowledge graph

10. **Entity Extraction Processing**
    - **Type**: Core > Code (JavaScript)
    - **Purpose**: Parse and validate LLM responses
    - **Configuration**:
      - JSON validation
      - Entity ID generation
      - Relationship formatting

11. **Store Entities in Neo4j**
    - **Type**: HTTP Request (to your FastAPI `/store-entities` endpoint)
    - **Purpose**: Save entities and relationships to graph database
    - **Configuration**:
      - POST request to your MCP wrapper
      - Entity and relationship data
      - Error handling for duplicates

12. **Store Vectors in ChromaDB**
    - **Type**: HTTP Request (to your FastAPI `/store-vectors` endpoint)
    - **Purpose**: Save text chunks with embeddings
    - **Configuration**:
      - POST request to your MCP wrapper
      - Text chunking data
      - Embedding metadata

### 📊 Phase 5: Progress & Error Management
**Goal**: Track progress and handle failures gracefully

13. **Progress Counter**
    - **Type**: Core > Set
    - **Purpose**: Track processing statistics
    - **Configuration**:
      - Papers processed count
      - Success/failure rates
      - Processing time tracking

14. **Error Handling**
    - **Type**: Core > If
    - **Purpose**: Detect and retry failed operations
    - **Configuration**:
      - Error detection logic
      - Retry mechanisms
      - Failure notifications

15. **Merge Results**
    - **Type**: Core > Merge
    - **Purpose**: Combine results from all processed papers
    - **Configuration**:
      - Wait for all branches
      - Aggregate statistics
      - Final data compilation

### ✅ Phase 6: Completion & Output
**Goal**: Generate final outputs and notify completion

16. **Generate Literature Review**
    - **Type**: HTTP Request (to your FastAPI `/generate-review` endpoint)
    - **Purpose**: Create formatted academic literature review
    - **Configuration**:
      - Query your knowledge graph
      - Format citations properly
      - Generate summary insights

17. **Email Notification**
    - **Type**: Productivity > Email
    - **Purpose**: Alert you when batch processing completes
    - **Configuration**:
      - SMTP settings
      - Processing summary
      - Success/failure report

18. **Save Processing Report**
    - **Type**: Core > Write Binary File
    - **Purpose**: Export batch processing statistics and results
    - **Configuration**:
      - JSON report format
      - Processing metrics
      - Error logs

## Integration with Existing MCP System

### FastAPI Wrapper Endpoints Needed
Your n8n workflow will call these endpoints you'll create in Phase 1:

```
POST /api/upload-batch        # Multiple PDF upload
POST /api/pdf-to-text         # Convert PDFs to text  
POST /api/store-entities      # Wrapper for your MCP store_entities
POST /api/store-vectors       # Wrapper for your MCP store_vectors
POST /api/query-graph         # Wrapper for your MCP query_knowledge_graph
POST /api/generate-review     # Wrapper for your MCP generate_literature_review
GET  /api/status              # Check processing status
DELETE /api/clear-database    # Wrapper for your MCP clear_knowledge_graph
```

### Data Flow Architecture

```
n8n Workflow ←→ FastAPI HTTP Wrapper ←→ Existing MCP Tools ←→ Neo4j + ChromaDB
```

**Benefits**:
- ✅ Zero changes to your existing MCP system
- ✅ Same databases (Neo4j + ChromaDB)
- ✅ Same entity extraction logic
- ✅ Visual workflow management
- ✅ Batch processing capabilities

## Cost Optimization Features

### Smart LLM Routing
```
[Document Complexity Analysis] 
    ├─ Simple papers → Claude Haiku (cheap)
    ├─ Medium papers → GPT-4o (balanced)
    └─ Complex papers → Claude Opus (expensive but thorough)
```

### Rate Limiting & Efficiency
- **Sequential processing** to avoid API rate limits
- **Retry logic** for failed requests
- **Progress tracking** for long batches
- **Error recovery** without restarting entire batch

## Building This Workflow in n8n

### Step-by-Step Construction:

1. **Start with Manual Trigger**: Drag from Core nodes
2. **Add File Upload**: Connect HTTP Request node
3. **Build LLM Routing**: Add Switch node with 3 branches
4. **Add Storage Nodes**: HTTP Request nodes for your FastAPI endpoints
5. **Connect Error Handling**: Add If nodes and retry logic
6. **Add Completion Actions**: Email and file saving nodes

### Visual Building Tips:
- **Use descriptive node names** for clarity
- **Add notes** to explain complex logic
- **Group related nodes** visually
- **Test each section** before building the next
- **Save frequently** as you build

## Advanced Features to Add Later

### Batch Analytics Dashboard
- Processing time per paper
- Token usage and costs
- Success/failure rates
- Entity extraction statistics

### Multi-User Support
- Queue management for multiple researchers
- Priority processing
- Resource allocation

### Integration Extensions
- Slack notifications
- Google Drive integration
- Zotero library sync
- Citation manager export

This workflow design gives you a production-ready batch processing system while preserving your excellent existing interactive MCP workflow for single-paper analysis.
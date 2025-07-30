# n8n Community Nodes Cheat Sheet

Based on actual installed community nodes in this project.

**✅ VERIFIED**: Node availability confirmed in n8n interface at `http://localhost:5678`
- LlamaParse and LlamaExtract nodes are visible in node palette
- Both show llama icons and are available for use in workflows

**📚 DOCS CHECKED**: Official documentation reviewed
- [LlamaCloud Repo](https://github.com/run-llama/n8n-llamacloud)
- [Neo4j Node Repo](https://github.com/Kurea/n8n-nodes-neo4j)  
- [n8n Community Nodes Docs](https://docs.n8n.io/integrations/community-nodes/)

## LlamaParse Node (n8n-llamacloud)

### Node Type
- **Type**: `"LlamaCloud"` (internal name from source)
- **Display Name**: "LlamaParse" (✅ CONFIRMED in n8n interface)
- **Class**: LlamaParse
- **Group**: transform
- **Icon**: llamacloud.svg (llama icon visible in UI)

### Credentials Required
- **Name**: `"LlamaCloudApi"`
- **Required**: Yes
- **API Key**: Your LlamaCloud API key

### Parameters Structure
```json
{
  "resource": "parsing",           // Fixed value, only option
  "operation": "parse",           // Fixed value, only option  
  "filePath": "/path/to/file.pdf" // Required string parameter
}
```

### Parameter Details
- **Resource**: Always `"parsing"` (only option available)
- **Operation**: Always `"parse"` (only option available) 
- **File Path**: 
  - Required: Yes
  - Type: string
  - Placeholder: `/User/user/Desktop/file.pdf`
  - Description: Path to your PDF file

### Input/Output
- **Inputs**: [NodeConnectionType.Main]
- **Outputs**: [NodeConnectionType.Main] 
- **Output Format**: JSON array with document content in markdown

### Implementation Details
- Uses `llamaindex.LlamaParseReader` internally
- Result type: markdown
- Returns documents array via `documents[i].toJSON()`

## LlamaExtract Node (n8n-llamacloud)

### Node Type
- **Type**: `"LlamaExtract"` (internal name from source)
- **Display Name**: "LlamaExtract" (✅ CONFIRMED in n8n interface)
- **Class**: LlamaExtract
- **Group**: transform
- **Icon**: llamacloud.svg (llama icon visible in UI)

### Credentials Required
- **Name**: `"LlamaCloudApi"`
- **Required**: Yes
- **API Key**: Your LlamaCloud API key

### Parameters Structure
```json
{
  "resource": "extracting",       // Fixed value, only option
  "operation": "extract",         // Fixed value, only option
  "agentId": "agent_id_string",   // Required string parameter
  "filePath": "/path/to/file.pdf" // Required string parameter
}
```

### Parameter Details
- **Resource**: Always `"extracting"` (only option available)
- **Operation**: Always `"extract"` (only option available)
- **Agent Id**: 
  - Required: Yes
  - Type: string
  - Description: Extraction Agent Id
- **File Path**: 
  - Required: Yes
  - Type: string
  - Placeholder: `/User/user/Desktop/file.pdf`
  - Description: Path to your file

### Input/Output
- **Inputs**: [NodeConnectionType.Main]
- **Outputs**: [NodeConnectionType.Main]
- **Output Format**: JSON array with extracted structured data

### Implementation Details
- Uses custom `extractDataFromFile()` function
- Requires pre-configured LlamaExtract agent
- Returns structured extraction results

## Neo4j Node (n8n-nodes-neo4j)

### Node Type
- **Type**: `"neo4j"` (lowercase)
- **Display Name**: "Neo4j" (✅ CONFIRMED in n8n interface)
- **Group**: transform
- **Icon**: neo4j.svg
- **Status**: ✅ INSTALLED (6,256 Downloads, Published by kurea)

### Credentials Required  
- **Name**: `"neo4jApi"`
- **Required**: Yes
- **Connection details**: URL, username, password

### Available Actions (6 Total)

#### VECTOR STORE ACTIONS
1. **Vector Store Similarity Search**
   - Operation: Search for similar vectors
   - Requires: ai_embedding input connection
   
2. **Vector Store Add Texts** 
   - Operation: Add text documents to vector store
   - Requires: ai_embedding input connection

#### GRAPH DATABASE ACTIONS  
3. **Graph Database Execute Query**
   - Operation: Execute Cypher queries
   - Most flexible option for custom operations
   - ✅ CONFIRMED in docs

4. **Graph Database Create Node**
   - Operation: Create individual nodes  
   - Requires: node label and properties in JSON format
   - ✅ CONFIRMED in docs

5. **Graph Database Create Relationship**
   - Operation: Create relationships between nodes
   - ⚠️ STATUS: "Coming soon" according to docs (but visible in interface)

6. **Graph Database Get Schema**
   - Operation: Get database schema information
   - Status: Not mentioned in docs but visible in interface

### Vector Store Operations

#### Special Input Requirements
- **Main Input**: Standard n8n input
- **Embedding Input**: Required AI embedding connection when using vectorStore
  - Type: `"ai_embedding"`
  - Required: Yes
  - Max Connections: 1

### Graph Database Operations

#### Parameters Structure  
```json
{
  "operation": "executeQuery" | "createNode" | "createRelationship" | "getSchema",
  "indexName": "vector"  // Optional string, default: "vector"
}
```

### Vector Store Detailed Parameters

#### Similarity Search
```json
{
  "resource": "vectorStore",
  "operation": "similaritySearch", 
  "indexName": "vector",           // Optional, default: "vector"
  "queryText": "search text",      // Required string
  "moreOptions": {                 // Optional collection
    "distanceMetric": "COSINE",    // COSINE|EUCLIDEAN_DISTANCE|MAX_INNER_PRODUCT|DOT_PRODUCT|JACCARD
    "metadataFilter": {},          // JSON object for filtering
    "retrievalQuery": ""           // Custom Cypher query
  }
}
```

#### Add Texts  
```json
{
  "resource": "vectorStore",
  "operation": "addTexts",
  "indexName": "vector",           // Optional, default: "vector" 
  "texts": ["text1", "text2"],     // Required string array (multipleValues: true)
  "metadatas": [{"key": "value"}]  // Optional metadata array
}
```

### Implementation Details
- Uses `@langchain/community/graphs/neo4j_graph`
- Uses `@langchain/community/vectorstores/neo4j_vector`
- Built with LangChain integration
- Supports both vector operations and graph operations

## Additional Built-in Nodes (Relevant)

### Webhook Node
- **Type**: `"n8n-nodes-base.webhook"`
- **Purpose**: Receive HTTP requests
- **Parameters**: httpMethod, path, responseMode, responseData

### Code Node  
- **Type**: `"n8n-nodes-base.code"`
- **Purpose**: Execute JavaScript code
- **Parameters**: mode, jsCode
- **Modes**: runOnceForAllItems, runOnceForEachItem

### LLM Node (Groq)
- **Type**: `"n8n-nodes-base.llm"`  
- **Purpose**: AI text generation
- **Credentials**: groqApi
- **Parameters**: model, messages, options (temperature, maxTokens)

## LangChain AI Nodes (Advanced Pattern)

### Chat Trigger Node
- **Type**: `"@n8n/n8n-nodes-langchain.chatTrigger"`
- **TypeVersion**: 1.1
- **Purpose**: Receive chat messages and trigger LangChain workflows
- **Parameters**: options: {}
- **Output**: Provides webhookId for chat integration
- **✅ CONFIRMED**: From `pdf-processing-3.json` working example

### LangChain LLM Chain Node
- **Type**: `"@n8n/n8n-nodes-langchain.chainLlm"`
- **TypeVersion**: 1.7  
- **Purpose**: Execute LLM chains with batching support
- **Parameters**: batching: {}
- **Special Connections**: Accepts `ai_languageModel` input connections
- **✅ CONFIRMED**: From `pdf-processing-3.json` working example

### Groq Chat Model Node (LangChain)
- **Type**: `"@n8n/n8n-nodes-langchain.lmChatGroq"`
- **TypeVersion**: 1
- **Purpose**: Groq language model for LangChain integration
- **Parameters**: options: {}
- **Connection Type**: Provides `ai_languageModel` output connection
- **Credentials**: Uses Groq API credentials
- **✅ CONFIRMED**: From `pdf-processing-3.json` working example

### LangChain Connection Types
- **ai_languageModel**: Special connection type for LangChain AI models
- **Usage Pattern**: LM nodes connect to Chain nodes via `ai_languageModel` connections
- **Example Connection**:
  ```json
  "Groq Chat Model": {
    "ai_languageModel": [[
      {
        "node": "Basic LLM Chain",
        "type": "ai_languageModel", 
        "index": 0
      }
    ]]
  }
  ```

## Workflow Node Type Summary

For proper n8n workflow JSON:

### Community Nodes
1. **LlamaParse**: `"CUSTOM.LlamaCloud"` (with LlamaCloudApi credentials)
2. **LlamaExtract**: `"CUSTOM.LlamaExtract"` (with LlamaCloudApi credentials)
3. **Neo4j (All Operations)**: `"n8n-nodes-neo4j.neo4j"` (with neo4jApi credentials)

### Built-in Nodes
4. **Webhook**: `"n8n-nodes-base.webhook"`
5. **Code**: `"n8n-nodes-base.code"`
6. **LLM/Groq**: `"n8n-nodes-base.llm"` (with groqApi credentials)

### LangChain AI Nodes (Advanced)
7. **Chat Trigger**: `"@n8n/n8n-nodes-langchain.chatTrigger"`
8. **LLM Chain**: `"@n8n/n8n-nodes-langchain.chainLlm"`
9. **Groq Chat Model**: `"@n8n/n8n-nodes-langchain.lmChatGroq"`

## Key Findings: Docs vs Interface vs Source Code

### **Node Type Naming - SOLVED!**
From actual working n8n workflow exports:

**Standard Pattern** (`pdf-processing.json` and `pdf-processing-2.json`):
- **LlamaParse**: `"CUSTOM.LlamaCloud"` ✅ CONFIRMED
- **LlamaExtract**: `"CUSTOM.LlamaExtract"` ✅ CONFIRMED  
- **Neo4j**: `"n8n-nodes-neo4j.neo4j"` ✅ CONFIRMED

**LangChain Pattern** (`pdf-processing-3.json`):
- **Chat Trigger**: `"@n8n/n8n-nodes-langchain.chatTrigger"` ✅ CONFIRMED
- **LLM Chain**: `"@n8n/n8n-nodes-langchain.chainLlm"` ✅ CONFIRMED
- **Groq Chat Model**: `"@n8n/n8n-nodes-langchain.lmChatGroq"` ✅ CONFIRMED

**Key Discoveries**: 
- Community nodes use the `CUSTOM.` prefix in workflow JSON!
- LangChain AI nodes use the `@n8n/n8n-nodes-langchain.` prefix!
- Special `ai_languageModel` connection type for LangChain workflows!

### **Neo4j Node Status**
- **Interface shows 6 actions** but docs only document 4
- **"Create Relationship"** marked as "Coming soon" in docs but visible in interface
- **"Get Schema"** not mentioned in docs but available in interface

### **Recommendations**
1. **Test node types** in actual workflow to determine correct identifiers
2. **Use interface as primary source** since it shows what's actually available
3. **Documentation may be outdated** compared to installed versions

❌ **Wrong**: Complex LlamaParse parameters (Processing Mode, Language, etc.)
✅ **Correct**: Only `filePath` parameter required

❌ **Wrong**: `"Neo4j"` with `operation: "Execute Cypher Query"`
✅ **Correct**: `"neo4j"` with `resource: "graphDb"` and `operation: "executeQuery"`

❌ **Wrong**: Separate vector store node type
✅ **Correct**: Same `"neo4j"` node with `resource: "vectorStore"`

## Authentication Requirements

### LlamaCloud API Credential
```json
{
  "name": "LlamaCloudApi", 
  "apiKey": "llx-your-api-key-here"
}
```

### Neo4j API Credential
```json
{
  "name": "neo4jApi",
  "url": "neo4j://localhost:7687",
  "username": "neo4j", 
  "password": "password123"
}
```

### Groq API Credential  
```json
{
  "name": "groqApi",
  "apiKey": "gsk_your-groq-key-here"
}
```
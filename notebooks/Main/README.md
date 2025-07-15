# 📚 GraphRAG MCP Main Notebooks

This folder contains the primary notebooks for the GraphRAG MCP Document Processing workflow.

## 📁 Files

### **`Simple_Document_Processing.ipynb`**
**🎯 Main notebook for document processing and knowledge graph creation**

**What it does:**
- ✅ Processes PDF documents into knowledge graphs
- ✅ Creates interactive visualizations
- ✅ Provides analytics and performance metrics
- ✅ Guides you through MCP server setup

**Prerequisites:**
- Ollama running with `llama3.1:8b` and `nomic-embed-text` models
- Neo4j database running on Docker
- Python environment with required dependencies

**Usage:**
1. Open the notebook in Jupyter
2. Update `PROJECT_NAME` and `DOCUMENTS_FOLDER` in the setup cell
3. Run all cells (Cell → Run All)
4. Follow the generated next steps for Claude Desktop integration

### **`processing_utils.py`**
**🔧 Support utilities for the main notebook**

**Contains:**
- `DocumentProcessor` class for managing document processing
- `DocumentStatus` dataclass for tracking progress
- Interactive visualization functions
- Error handling and retry mechanisms
- Prerequisites checking

## 🗂️ Folder Structure Context

```
notebooks/
├── Main/                          # ← You are here
│   ├── Simple_Document_Processing.ipynb
│   ├── processing_utils.py
│   └── README.md
├── Google CoLab/                  # Google Colab versions
├── Other/                         # Archive/alternative notebooks
└── Simple_Paper_RAG_Chat.ipynb   # Legacy notebook
```

## 🚀 Quick Start

1. **Ensure services are running:**
   ```bash
   # Start Ollama
   ollama serve
   
   # Start Neo4j
   docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
   ```

2. **Open and run the notebook:**
   ```bash
   jupyter notebook Simple_Document_Processing.ipynb
   ```

3. **Customize settings:**
   - Update `PROJECT_NAME` to your project name
   - Update `DOCUMENTS_FOLDER` to point to your PDFs
   - Default: `../../examples` (points to main project examples)

4. **Run all cells and follow the guided workflow**

## 📊 Expected Output

After running the notebook, you'll have:
- 🕸️ **Knowledge graph** stored in Neo4j
- 📊 **Processing analytics** with visualizations
- 🎨 **Interactive graph visualization**
- 🤖 **Ready-to-use MCP server** for Claude Desktop
- 📝 **Next steps** for AI research assistant setup

## 🔧 Path Configuration

The notebook uses these relative paths from the `Main/` folder:
- `../../examples` - Default documents folder
- `../../../` - Project root for imports
- `./processing_utils.py` - Local utility file

## 💡 Tips

- **Document folder**: Use 5-20 documents for testing (more = longer processing)
- **Processing time**: ~2-10 minutes per document depending on size
- **Visualization**: Requires `plotly` and `networkx` libraries
- **Error recovery**: Built-in retry mechanism for failed documents

## 🆘 Troubleshooting

If you encounter issues:

1. **Import errors**: Ensure you're running from the correct directory
2. **Service errors**: Check Ollama and Neo4j are running
3. **Path errors**: Verify `DOCUMENTS_FOLDER` path is correct
4. **Visualization errors**: Install `pip install plotly networkx`

For more help, see the troubleshooting section in the notebook itself.
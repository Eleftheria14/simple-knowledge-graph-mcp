#!/bin/bash
# Convenient script to activate GraphRAG MCP environment
source graphrag-env/bin/activate
echo "🚀 GraphRAG MCP environment activated!"
echo "📁 Python: $(which python)"
echo "🐍 Version: $(python --version)"
echo ""
echo "💡 To start Jupyter notebook:"
echo "   jupyter notebook"
echo ""
echo "💡 To run the processing notebook:"
echo "   cd notebooks/Main && jupyter notebook Simple_Document_Processing.ipynb"

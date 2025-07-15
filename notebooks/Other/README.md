# Notebooks

This directory contains Jupyter notebooks for the Scientific Paper Literature Review System.

## Main Notebook

### `Simple_Paper_RAG_Chat.ipynb` ⭐
**Complete RAG + Knowledge Graph system** - Analyze one paper with intelligent chat interface.

**Features:**
- Upload and process a single PDF paper
- RAG-based question answering with semantic search
- Knowledge graph entity extraction (authors, methods, concepts)
- Interactive chat interface for exploring the paper
- Citation extraction and formatting
- Enhanced metadata extraction for literature reviews

**Workflow:**
1. **Load Paper**: Upload PDF and extract content
2. **Build Knowledge**: Create embeddings and extract entities
3. **Chat Interface**: Ask questions using natural language
4. **Explore Graph**: Discover relationships and connections
5. **Export for Corpus**: Generate GraphRAG-compatible documents

**Perfect for:**
- Personal research and paper analysis
- Understanding complex scientific papers
- Preparing papers for literature review corpus
- Quick literature exploration

## Getting Started

### Prerequisites
1. **Ollama running** with required models:
   ```bash
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ollama serve
   ```

2. **Python environment**:
   ```bash
   source langchain-env/bin/activate
   pip install -r requirements.txt
   ```

3. **Jupyter installed**:
   ```bash
   pip install jupyter
   ```

### Running the Notebook

1. **Start Jupyter**:
   ```bash
   jupyter notebook
   ```

2. **Navigate to notebooks directory**

3. **Open `Simple_Paper_RAG_Chat.ipynb`**

4. **Update PDF path** in the first code cell:
   ```python
   pdf_path = "../examples/d4sc03921a.pdf"  # or your own paper
   ```

5. **Run all cells**

## Features Available

### Basic Analysis
- Paper loading and processing
- Entity extraction (authors, methods, concepts)
- Knowledge graph construction
- Interactive chat interface

### Enhanced Analysis (New)
- GraphRAG-compatible metadata extraction
- Precise citation tracking and location mapping
- Section structure analysis
- Domain and research type classification
- Export functionality for literature review corpus

### Example Usage

```python
# Basic paper analysis
from src import analyze_paper_with_chat
chat_system = analyze_paper_with_chat("path/to/paper.pdf")

# Enhanced corpus-ready analysis  
from src import export_paper_for_corpus
corpus_doc = export_paper_for_corpus("path/to/paper.pdf")

# Citation tracking
from src import track_citations_in_paper
citations = track_citations_in_paper(content, metadata)
```

## Future Notebooks

Coming soon for the complete literature review system:
- `Literature_Review_System.ipynb` - Complete corpus management and GraphRAG
- `Corpus_Builder.ipynb` - Batch processing of multiple papers
- `Review_Writer.ipynb` - Automated literature review generation

## Customization

### Changing Analysis Focus
Modify the analysis to focus on different aspects:
- **Technical focus**: Emphasize methodology and implementation
- **Review focus**: Highlight findings and comparisons
- **Citation focus**: Track references and evidence

### Using Different Models
Update the Ollama configuration:
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="mistral",  # or other models
    temperature=0.1,
    num_ctx=32768
)
```

## Output Examples

The notebook produces:
- **Interactive chat responses** with paper insights
- **Entity graphs** showing relationships
- **Citation maps** with precise locations
- **Corpus-ready documents** for literature reviews
- **Metadata extracts** including domain classification

See the notebook for example outputs and expected results.
# Notebooks

This directory contains the main Jupyter notebook for the Simple Scientific Paper RAG + Knowledge Graph system.

## Main Notebook

### `Simple_Paper_RAG_Chat.ipynb` ⭐
**Complete RAG + Knowledge Graph system** - Analyze one paper with intelligent chat interface.

**Features:**
- Upload and process a single PDF paper
- RAG-based question answering with semantic search
- Knowledge graph entity extraction (authors, methods, concepts)
- Interactive chat interface for exploring the paper
- Citation extraction and formatting
- Visual relationship mapping

**Workflow:**
1. **Load Paper**: Upload PDF and extract content
2. **Build Knowledge**: Create embeddings and extract entities
3. **Chat Interface**: Ask questions using natural language
4. **Explore Graph**: Discover relationships and connections
5. **Export Results**: Get citations and insights

**Perfect for:**
- Personal research and paper analysis
- Understanding complex scientific papers
- Discovering hidden connections in research
- Quick literature exploration

## Getting Started

### Prerequisites
1. **Ollama running** with required models:
   ```bash
   ollama pull llama3.1:8b
   ollama serve
   ```

2. **PostgreSQL database** (for main notebook):
   ```bash
   # See docs/database_setup_instructions.md for setup
   ```

3. **Jupyter installed**:
   ```bash
   pip install jupyter
   ```

### Running the Notebooks

1. **Start Jupyter**:
   ```bash
   jupyter notebook
   ```

2. **Navigate to notebooks directory**

3. **Open desired notebook**

4. **Update PDF path** in the first code cell:
   ```python
   pdf_path = "../examples/d4sc03921a.pdf"  # or your own paper
   ```

5. **Run all cells**

## Recommended Learning Path

1. **Start with `Tutorial.ipynb`**
   - Learn basic concepts
   - Understand PDF processing
   - Get familiar with Ollama

2. **Move to `Scientific_Paper_Analyzer.ipynb`**
   - Learn about chunking strategies
   - Understand multi-stage processing
   - Experiment with analysis approaches

3. **Use `Maximum_Context_Scientific_Analyzer.ipynb`**
   - Production-ready analysis
   - Database integration
   - Comprehensive R&D analysis

## Customization

### Changing Analysis Focus
Modify the analysis prompt in the notebooks to focus on different aspects:
- **Technical focus**: Emphasize methodology and implementation
- **Business focus**: Highlight commercial applications and market impact
- **Academic focus**: Focus on research contributions and citations

### Using Different Models
Update the Ollama configuration:
```python
llm = ChatOllama(
    model="mistral",  # or other models
    temperature=0.1,
    num_ctx=32768
)
```

### Processing Multiple Papers
Create a loop to process multiple PDFs:
```python
import os

pdf_directory = "../examples/"
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, filename)
        # Run analysis...
```

## Output Examples

Each notebook produces different types of output:

- **Tutorial**: Simple abstract summaries
- **Scientific_Paper_Analyzer**: Structured multi-section analysis
- **Maximum_Context_Scientific_Analyzer**: Comprehensive R&D analysis with database storage

See the individual notebooks for example outputs and expected results.
# Notebooks

This directory contains Jupyter notebooks for different aspects of the Scientific Paper Analyzer.

## Notebooks

### `Maximum_Context_Scientific_Analyzer.ipynb` ⭐
**Main notebook** - Complete scientific paper analysis with maximum context preservation.

**Features:**
- Citation extraction and database storage
- Maximum context preservation within Ollama limits
- Comprehensive LLM analysis focused on R&D implications
- Integration with PostgreSQL database

**Use this notebook for:**
- Production analysis of research papers
- Comprehensive R&D-focused analysis
- Building a database of analyzed papers

### `Tutorial.ipynb`
**Beginner-friendly tutorial** - Simple introduction to LangChain and Ollama.

**Features:**
- Basic PDF loading and processing
- Simple abstract summarization
- Step-by-step explanations
- Good for learning LangChain concepts

**Use this notebook for:**
- Learning how LangChain works
- Understanding the basics of PDF processing
- Getting started with Ollama

### `Scientific_Paper_Analyzer.ipynb`
**Intermediate notebook** - Multi-stage analysis with chunking approach.

**Features:**
- Document chunking and processing
- Multi-stage analysis pipeline
- More complex than tutorial, simpler than main notebook

**Use this notebook for:**
- Understanding chunking strategies
- Learning about multi-stage processing
- Experimenting with different analysis approaches

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
# Simple Scientific Paper RAG + Knowledge Graph

A simple, personal tool for intelligent analysis of scientific papers using RAG (Retrieval-Augmented Generation) and Knowledge Graph extraction. Built with LangChain, LangGraph, and Ollama for local, private analysis.

## 🎯 Features

- **🤖 RAG Chat Interface**: Ask natural language questions about your paper
- **🕸️ Knowledge Graph**: Automatically extract entities (authors, methods, concepts) and relationships
- **📚 Smart Retrieval**: Find relevant content using semantic similarity
- **🧠 Local AI**: Uses Ollama for complete privacy - no data sent to external APIs
- **📝 Citation Management**: Extract and format citations in academic styles
- **🔍 Entity Discovery**: Identify key concepts, methods, and relationships in papers

## 🛠️ Setup

### Prerequisites

1. **Ollama**: Install and run Ollama locally
   ```bash
   # Install Ollama (visit https://ollama.ai for installation instructions)
   # Pull required models
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

2. **Python Environment**: Python 3.8+ recommended
   ```bash
   # Create virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Dependencies**: Install required packages
   ```bash
   pip install langchain langchain-community langchain-ollama
   ```

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd scientific-paper-analyzer
   ```

2. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

3. Place your PDF research paper in the project directory or update the `pdf_path` in the notebook

## 📁 Project Structure

```
├── src/                                       # Core Python modules
│   ├── citation_extractor.py                 # Citation extraction engine
│   ├── enhanced_citation_extractor.py        # Database-integrated extractor
│   ├── database_manager.py                   # PostgreSQL database operations
│   └── __init__.py                           # Package initialization
├── notebooks/                                # Jupyter notebooks
│   ├── Maximum_Context_Scientific_Analyzer.ipynb  # Main analysis notebook
│   ├── Tutorial.ipynb                        # Beginner tutorial
│   ├── Scientific_Paper_Analyzer.ipynb       # Intermediate analysis
│   └── README.md                             # Notebook documentation
├── database/                                 # Database setup files
│   └── database_setup.sql                   # PostgreSQL schema
├── docs/                                     # Documentation
│   ├── database_setup_instructions.md       # Database setup guide
│   ├── API_REFERENCE.md                     # API documentation
│   └── INSTALLATION.md                      # Installation instructions
├── examples/                                 # Example files and papers
│   ├── d4sc03921a.pdf                       # Example research paper
│   └── README.md                            # Examples documentation
├── config/                                   # Configuration files
│   ├── database_config.py                   # Database configuration
│   └── __init__.py                          # Config package
├── requirements.txt                          # Python dependencies
├── README.md                                # This file
└── .gitignore                               # Git ignore rules
```

## 🚀 Usage

### Quick Start

1. Open the main Jupyter notebook:
   ```bash
   jupyter notebook notebooks/Maximum_Context_Scientific_Analyzer.ipynb
   ```

2. Update the PDF path in the first cell:
   ```python
   pdf_path = "../examples/d4sc03921a.pdf"  # or your own paper
   ```

3. Run all cells to:
   - Extract paper citations
   - Analyze paper sections
   - Generate comprehensive scientific analysis

### Citation Extraction Only

To use just the citation extractor:

```python
from src import display_citation_info, get_acs_citation

# Extract and display full citation info
citation_result = display_citation_info("examples/d4sc03921a.pdf", show_all_formats=True)

# Get just ACS formatted citation
acs_citation = get_acs_citation("examples/d4sc03921a.pdf")
print(acs_citation)
```

## 📊 Analysis Output

The tool generates a comprehensive analysis including:

- **Executive Summary**: Core findings and scientific impact
- **Technical Architecture**: Model details and training approaches
- **Scientific Applications**: Demonstrated use cases and performance
- **Research Acceleration Potential**: Time savings and productivity gains
- **Implementation Considerations**: Deployment and infrastructure needs
- **Strategic R&D Implications**: Business and competitive insights
- **Future Research Directions**: Limitations and opportunities

## 🎯 Example Output

```
📖 PAPER CITATION (ACS Style):
Ramos, M. C.; Collison, C. J.; White, A. D. A review of large language models 
and autonomous agents in chemistry. Chemical Science 2024. DOI: 10.1039/d4sc03921a.

📊 ANALYSIS METADATA:
🧠 Context used: 24,567 characters (~6,142 tokens)
📄 Sections analyzed: 5
⏱️ Analysis date: 2024-07-11 14:30
```

## 🔧 Configuration

### Ollama Settings

The notebook is configured for optimal performance with:
- **Model**: llama3.1:8b
- **Context Window**: 32,768 tokens
- **Temperature**: 0.1 (for analytical consistency)
- **Max Prediction**: 4,096 tokens

### Customization

You can modify the analysis by:
- Changing the analysis prompt in the notebook
- Adjusting Ollama parameters for different models
- Modifying section extraction patterns for different paper formats
- Adding new citation formats in `citation_extractor.py`

## 📋 Supported Citation Formats

- **ACS** (American Chemical Society)
- **APA** (American Psychological Association)
- **BibTeX** (LaTeX bibliography format)
- **Simple** (Quick reference format)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Support for additional citation formats
- Enhanced section extraction for different journal formats
- Integration with additional LLM providers
- Multi-language paper support

## 📄 License

This project is open source. Please ensure you comply with the terms of service for Ollama and any models you use.

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain) for LLM orchestration
- Uses [Ollama](https://ollama.ai) for local LLM deployment
- Designed for scientific research acceleration and R&D applications

## 📞 Support

For issues or questions:
1. Check the existing issues in this repository
2. Create a new issue with detailed description
3. Include sample outputs and error messages when relevant

---

**Note**: This tool is designed for educational and research purposes. Always verify citations and analysis results for academic or professional use.
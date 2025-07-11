# Scientific Paper Analyzer with LangChain & Ollama

A comprehensive tool for analyzing scientific research papers using Large Language Models (LLMs) through LangChain and Ollama. This project focuses on maximum context preservation and detailed scientific analysis with proper academic citation extraction.

## 🎯 Features

- **Maximum Context Preservation**: Extracts and preserves key sections while staying within Ollama's token limits
- **Comprehensive Citation Extraction**: Automatically extracts and formats citations in multiple academic styles (ACS, APA, BibTeX)
- **Scientific Analysis**: Generates detailed analysis focused on R&D implications and scientific applications
- **Local LLM Integration**: Uses Ollama for private, local analysis without sending data to external APIs
- **Modular Design**: Clean, reusable components for citation extraction and analysis

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
├── Maximum_Context_Scientific_Analyzer.ipynb  # Main analysis notebook
├── citation_extractor.py                      # Citation extraction module
├── d4sc03921a.pdf                            # Example research paper
├── README.md                                  # This file
└── .gitignore                                # Git ignore rules
```

## 🚀 Usage

### Quick Start

1. Open the Jupyter notebook:
   ```bash
   jupyter notebook Maximum_Context_Scientific_Analyzer.ipynb
   ```

2. Update the PDF path in the first cell:
   ```python
   pdf_path = "path/to/your/research_paper.pdf"
   ```

3. Run all cells to:
   - Extract paper citations
   - Analyze paper sections
   - Generate comprehensive scientific analysis

### Citation Extraction Only

To use just the citation extractor:

```python
from citation_extractor import display_citation_info, get_acs_citation

# Extract and display full citation info
citation_result = display_citation_info("paper.pdf", show_all_formats=True)

# Get just ACS formatted citation
acs_citation = get_acs_citation("paper.pdf")
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
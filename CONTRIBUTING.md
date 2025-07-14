# Contributing to GraphRAG MCP Toolkit

Thank you for your interest in contributing to the GraphRAG MCP Toolkit! We welcome contributions from the community to help make this project better.

## 🌟 Ways to Contribute

### 🐛 Bug Reports
- Search existing issues first to avoid duplicates
- Use the bug report template
- Include detailed reproduction steps
- Provide system information (OS, Python version, etc.)

### 💡 Feature Requests
- Check if the feature aligns with project goals
- Use the feature request template
- Explain the use case and benefits
- Consider implementation complexity

### 🔧 Code Contributions
- Bug fixes
- Feature implementations
- Performance improvements
- Documentation improvements
- Test coverage enhancements

### 📚 Documentation
- Fix typos and improve clarity
- Add usage examples
- Create tutorials and guides
- Update API documentation

### 🎨 Templates
- Create domain-specific templates
- Improve existing templates
- Add new MCP tools
- Enhance entity extraction patterns

## 🚀 Development Setup

### Prerequisites

1. **Python 3.10+** - Required for FastMCP compatibility
2. **UV** - Package manager (recommended)
3. **Ollama** - Local LLM inference
4. **Git** - Version control

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/graphrag-mcp-toolkit.git
cd graphrag-mcp-toolkit

# Install with development dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install

# Verify installation
uv run graphrag-mcp --help
```

### Ollama Setup

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# Start Ollama server
ollama serve
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=graphrag_mcp

# Run specific test file
uv run pytest tests/test_templates.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code
uv run black .
uv run ruff check --fix .

# Type checking
uv run mypy graphrag_mcp/

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## 📁 Project Structure

```
graphrag-mcp-toolkit/
├── graphrag_mcp/           # Main package
│   ├── core/               # Core processing components
│   ├── templates/          # Domain templates
│   ├── mcp/               # MCP server components
│   └── cli/               # Command-line interface
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example documents
├── CLAUDE.md             # Project instructions
├── IMPLEMENTATION_PLAN.md # Development roadmap
└── requirements.txt      # Dependencies
```

## 🔄 Development Workflow

### 1. Fork and Branch

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/graphrag-mcp-toolkit.git
cd graphrag-mcp-toolkit

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the existing code style
- Write comprehensive tests
- Update documentation
- Add type hints
- Follow the "extract everything" philosophy

### 3. Test Your Changes

```bash
# Run tests
uv run pytest

# Test CLI commands
uv run graphrag-mcp templates --list
uv run graphrag-mcp status

# Test end-to-end workflow
uv run graphrag-mcp create test-project --template academic
```

### 4. Submit Pull Request

```bash
# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## 🎯 Contribution Guidelines

### Code Style

- **Python**: Follow PEP 8, enforced by Black and Ruff
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Use Google-style docstrings
- **Comments**: Explain complex logic, not obvious code

### Testing

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test full workflows
- **Coverage**: Aim for >80% test coverage

### Documentation

- **README**: Keep examples up-to-date
- **Docstrings**: Document all public APIs
- **CLAUDE.md**: Update development instructions
- **Type Hints**: Serve as inline documentation

### Git Conventions

#### Commit Messages
```
feat: add new template for legal documents
fix: resolve citation extraction bug
docs: update installation instructions
test: add tests for MCP server
refactor: improve entity extraction performance
```

#### Branch Names
```
feature/legal-template
fix/citation-bug
docs/installation-guide
test/mcp-server
refactor/entity-extraction
```

## 📋 Creating Templates

### Template Structure

```python
from graphrag_mcp.templates import BaseTemplate, TemplateConfig, EntityConfig

class MyTemplate(BaseTemplate):
    def get_template_config(self) -> TemplateConfig:
        return TemplateConfig(
            name="My Domain",
            description="Template for my specific domain",
            domain="my_domain",
            version="1.0.0",
            entities=[
                EntityConfig(
                    name="domain_guidance",
                    description="Extract everything relevant to my domain",
                    max_entities=999,
                    examples=["key", "domain", "concepts"]
                )
            ],
            relationships=[
                # Define relationships...
            ],
            mcp_tools=[
                # Define MCP tools...
            ]
        )
```

### Template Guidelines

1. **"Extract Everything" Philosophy**: Don't constrain entity discovery
2. **Domain Guidance**: Provide hints, not rigid constraints
3. **Relationship Flexibility**: Use "any" for unconstrained relationships
4. **MCP Tools**: Create domain-specific tools
5. **Validation**: Implement document validation logic

### Template Testing

```python
def test_my_template():
    template = MyTemplate()
    
    # Test configuration
    config = template.get_template_config()
    assert config.name == "My Domain"
    
    # Test entity schema
    schema = template.get_entity_schema()
    assert "my_domain" in schema
    
    # Test MCP tools
    tools = template.get_mcp_tools()
    assert len(tools) > 0
```

## 🐛 Debugging Tips

### Common Issues

1. **Import Errors**: Check `__init__.py` files
2. **Template Loading**: Verify template registration
3. **Ollama Connection**: Check server status
4. **MCP Server**: Test with universal server first

### Debug Mode

```bash
# Enable verbose logging
uv run graphrag-mcp --verbose status

# Debug specific component
uv run python -c "
from graphrag_mcp.templates import template_registry
print(template_registry.list_templates())
"
```

### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Component-specific logging
logger = logging.getLogger('graphrag_mcp.templates')
logger.setLevel(logging.DEBUG)
```

## 🚀 Release Process

### Version Management

- Follow semantic versioning (SemVer)
- Update `__init__.py` version
- Update `pyproject.toml` version
- Create git tag

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Git tag created
- [ ] PyPI package published

## 🤝 Code of Conduct

### Our Standards

- **Be respectful** to all contributors
- **Be constructive** in feedback
- **Be patient** with newcomers
- **Be open** to different perspectives

### Enforcement

- Report issues to project maintainers
- Follow GitHub community guidelines
- Maintain professional communication

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Q&A and general discussion
- **Discord**: Real-time community chat (if available)
- **Email**: Direct contact with maintainers

### Support

- **Documentation**: Check README and docs/
- **Examples**: See examples/ directory
- **CLAUDE.md**: Development instructions
- **Community**: Ask questions in discussions

## 🙏 Recognition

Contributors are recognized in:
- **README.md**: Major contributors
- **CONTRIBUTORS.md**: All contributors
- **Release Notes**: Feature contributors
- **GitHub**: Contributor graphs

---

**Thank you for contributing to GraphRAG MCP Toolkit!** Your contributions help make domain-specific AI assistants accessible to everyone. 🚀
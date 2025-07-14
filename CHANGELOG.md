# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial GraphRAG MCP Toolkit implementation
- Enhanced paper analysis with 20+ entity categories
- Citation tracking with precise location mapping
- Dual analysis pathways (interactive and corpus)
- Embedding-first architecture for optimized processing
- Tutorial system for comprehensive learning
- yFiles integration for professional graph visualization

### Changed
- Evolved from simple paper analysis to GraphRAG foundation
- Enhanced entity extraction beyond basic 8 categories
- Improved citation accuracy with character-level positioning
- Migrated from NetworkX to Graphiti for knowledge graph processing

### Fixed
- ChromaDB database management and cleanup
- Ollama integration stability

## [0.1.0] - Initial Release

### Added
- SimplePaperRAG with Ollama embeddings
- SimpleKnowledgeGraph with Graphiti (NetworkX legacy support)
- Basic paper analysis workflow
- ChromaDB vector storage
- Jupyter notebook interface

### Deprecated
- NetworkX knowledge graph backend (replaced by Graphiti)
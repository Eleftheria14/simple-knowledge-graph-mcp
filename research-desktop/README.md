# Academic Research Assistant - Desktop App

A modern Electron desktop application for academic research with AI-powered knowledge graphs and PDF processing.

## Features

🕸️ **Interactive Knowledge Graph**
- Visualize entities and relationships from academic papers
- Multiple layout algorithms (force-directed, hierarchical, circular)
- Filter by entity type and search functionality
- Export graphs as PNG, SVG, or GraphML

🔍 **Intelligent Search**
- Search across entities, relationships, and document content
- Semantic search with confidence scoring
- Tabbed results view for different content types

📝 **Literature Review Generator**
- AI-powered academic writing assistance
- Multiple citation styles (APA, IEEE, Nature, MLA)
- Export to Word, LaTeX, and Markdown
- Summary statistics and source tracking

📚 **Document Library Management**
- Drag-and-drop PDF processing with GROBID
- Batch processing and status tracking
- Document metadata and citation management
- Author and publication tracking

⚙️ **Advanced Configuration**
- Neo4j database connection settings
- AI model configuration (Groq API)
- Processing options and thresholds
- Display themes and preferences

## Requirements

- **macOS 10.15+** (Catalina or newer)
- **Node.js 18+** and **npm**
- **MCP Server** running on port 3001
- **Neo4j Database** (local or remote)
- **GROBID Service** for PDF processing

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start MCP Server
Ensure your MCP server is running:
```bash
# From the parent directory
./scripts/start_mcp_server.sh
```

### 3. Development Mode
```bash
npm run dev
```

### 4. Build for Production
```bash
npm run build:mac
```

## Architecture

```
┌─────────────────┐    HTTP     ┌─────────────────┐
│                 │ ◄─────────► │                 │
│  Electron App   │   :3001     │   MCP Server    │
│                 │             │                 │
└─────────────────┘             └─────────────────┘
        │                               │
        │                               │
        ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│                 │             │                 │
│  React Frontend │             │  Neo4j Database │
│                 │             │                 │
└─────────────────┘             └─────────────────┘
```

### Components

- **Main Process** (`main.js`) - Electron window management and native menus
- **Preload Script** (`preload.js`) - Secure IPC bridge and MCP API wrapper
- **React App** (`src/`) - Modern UI with TypeScript support
- **MCP Integration** - HTTP communication with backend services

### Key Features

**PDF Processing Pipeline:**
1. Drag & drop PDFs into the application
2. GROBID extracts academic content (authors, citations, entities)
3. AI processes content for entity/relationship extraction
4. Data stored in Neo4j for graph visualization and search

**Knowledge Graph Visualization:**
- Cytoscape.js for interactive network rendering
- Real-time filtering and search capabilities
- Multiple layout algorithms for different analysis needs
- Export functionality for presentations and papers

**Literature Review Generation:**
- AI analyzes stored knowledge graph
- Generates structured academic content
- Proper citation formatting in multiple styles
- Export to publication-ready formats

## Configuration

### Database Settings
```javascript
neo4j: {
  uri: 'bolt://localhost:7687',
  username: 'neo4j',
  password: 'your-password'
}
```

### AI Settings
```javascript
ai: {
  groqApiKey: 'your-groq-api-key',
  model: 'llama-3.1-70b-versatile',
  confidenceThreshold: 0.7
}
```

### Processing Options
```javascript
processing: {
  autoProcess: true,
  extractFigures: true,
  maxConcurrentFiles: 3
}
```

## Development

### Project Structure
```
research-desktop/
├── main.js                    # Electron main process
├── preload.js                 # Secure IPC bridge
├── src/
│   ├── App.jsx               # Main React application
│   ├── components/           # UI components
│   │   ├── PDFDropZone.jsx   # File upload interface
│   │   ├── GraphVisualization.jsx  # Knowledge graph
│   │   ├── SearchInterface.jsx     # Search functionality
│   │   ├── ReviewGenerator.jsx     # Literature review tool
│   │   └── ...
│   ├── hooks/                # Custom React hooks
│   └── utils/                # Utility functions
├── assets/                   # Icons and static files
└── dist/                     # Built application
```

### Adding New Features

1. **New Components**: Add to `src/components/`
2. **API Integration**: Extend `preload.js` MCP API wrapper
3. **State Management**: Use React hooks in `src/hooks/`
4. **Styling**: Tailwind CSS classes with custom design system

### Testing

```bash
# Run in development mode
npm run dev

# Test specific functionality
npm run dev:electron  # Just Electron
npm run dev:vite      # Just React app
```

## Building & Distribution

### macOS Distribution
```bash
# Build DMG installer
npm run build:mac

# Build for Mac App Store
npm run build:mas

# Build universal binary (Intel + Apple Silicon)
npm run build:universal
```

### Code Signing (for distribution)
```bash
# Set up Apple Developer certificates
export APPLE_ID="your-apple-id"
export APPLE_APP_SPECIFIC_PASSWORD="app-specific-password"

# Build and notarize
npm run build:mac
npm run notarize
```

## Troubleshooting

### Common Issues

**MCP Server Connection Failed**
- Ensure MCP server is running on port 3001
- Check firewall settings
- Verify Neo4j database connection

**PDF Processing Errors**
- Confirm GROBID service is available
- Check file permissions for uploaded PDFs
- Verify Groq API key configuration

**Graph Rendering Issues**
- Clear browser cache and reload app
- Check console for JavaScript errors
- Verify Cytoscape.js dependencies

**Performance Issues**
- Reduce max concurrent file processing
- Lower confidence thresholds
- Use hierarchical layout for large graphs

### Debug Mode

Enable debug logging:
```bash
DEBUG=* npm run dev
```

View logs in Developer Tools (Cmd+Option+I).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.
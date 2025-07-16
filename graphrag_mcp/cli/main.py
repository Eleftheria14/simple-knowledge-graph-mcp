"""
Main CLI Application for GraphRAG MCP Toolkit

Typer-based command-line interface for creating, managing, and deploying
GraphRAG MCP servers across different domains.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import typer

# Configuration
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

# Core components
from ..core import EnhancedDocumentProcessor, LLMAnalysisEngine, GraphRAGConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create CLI app
app = typer.Typer(
    name="graphrag-mcp",
    help="GraphRAG MCP Toolkit - Create domain-specific AI assistants",
    add_completion=False,
    rich_markup_mode="rich"
)

# Console for rich output
console = Console()

# CLI State
class CLIState(BaseModel):
    """CLI application state"""
    current_project: str | None = None
    config_dir: Path = Path.home() / ".graphrag-mcp"
    projects_dir: Path = Path.home() / ".graphrag-mcp" / "projects"
    templates_dir: Path = Path.home() / ".graphrag-mcp" / "templates"

cli_state = CLIState()


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    config_dir: str | None = typer.Option(None, "--config-dir", help="Custom config directory")
):
    """
    GraphRAG MCP Toolkit - Transform documents into domain-specific AI assistants.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        console.print("🔍 Verbose mode enabled", style="dim")

    if config_dir:
        cli_state.config_dir = Path(config_dir)
        cli_state.projects_dir = cli_state.config_dir / "projects"
        cli_state.templates_dir = cli_state.config_dir / "templates"

    # Ensure directories exist
    cli_state.config_dir.mkdir(exist_ok=True)
    cli_state.projects_dir.mkdir(exist_ok=True)
    cli_state.templates_dir.mkdir(exist_ok=True)


@app.command()
def create(
    name: str = typer.Argument(..., help="Name of the assistant to create"),
    template: str = typer.Option("academic", "--template", "-t", help="Domain template to use"),
    directory: str | None = typer.Option(None, "--directory", "-d", help="Project directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing project")
):
    """
    Create a new domain-specific GraphRAG assistant.
    
    Examples:
    
        graphrag-mcp create literature-assistant --template academic
        
        graphrag-mcp create legal-helper --template legal --directory ./my-projects
    """
    console.print(f"🚀 Creating new assistant: [bold blue]{name}[/bold blue]")

    # Determine project directory
    if directory:
        project_dir = Path(directory) / name
    else:
        project_dir = cli_state.projects_dir / name

    # Check if project exists
    if project_dir.exists() and not force:
        if not Confirm.ask(f"Project '{name}' already exists. Overwrite?"):
            console.print("❌ Project creation cancelled", style="red")
            raise typer.Exit(1)

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Task 1: Validate template
        task1 = progress.add_task("Validating template...", total=None)

        available_templates = _get_available_templates()
        if template not in available_templates:
            progress.update(task1, description="❌ Template validation failed")
            console.print(f"❌ Template '{template}' not found", style="red")
            console.print("Available templates:")
            for tmpl in available_templates:
                console.print(f"  • {tmpl}")
            raise typer.Exit(1)

        progress.update(task1, description="✅ Template validated")

        # Task 2: Create project structure
        task2 = progress.add_task("Creating project structure...", total=None)

        # Create project files
        _create_project_structure(project_dir, name, template)

        progress.update(task2, description="✅ Project structure created")

        # Task 3: Initialize configuration
        task3 = progress.add_task("Initializing configuration...", total=None)

        project_config = {
            "name": name,
            "template": template,
            "created_date": str(Path(__file__).stat().st_mtime),
            "version": "0.1.0",
            "documents": [],
            "mcp_server": {
                "port": 8080,
                "host": "localhost",
                "enabled": False
            }
        }

        config_file = project_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(project_config, f, indent=2)

        progress.update(task3, description="✅ Configuration initialized")

    # Success message
    console.print()
    panel = Panel.fit(
        f"[green]✅ Assistant '{name}' created successfully![/green]\\n\\n"
        f"📁 Location: {project_dir}\\n"
        f"🎯 Template: {template}\\n\\n"
        f"[dim]Next steps:[/dim]\\n"
        f"  1. Add documents: [code]graphrag-mcp add-documents {name} ./papers/[/code]\\n"
        f"  2. Process corpus: [code]graphrag-mcp process {name}[/code]\\n"
        f"  3. Start server: [code]graphrag-mcp serve {name}[/code]",
        title="🎉 Success",
        border_style="green"
    )
    console.print(panel)


@app.command("templates")
def templates_command(
    list_templates: bool = typer.Option(True, "--list", "-l", help="List available templates"),
    info: str | None = typer.Option(None, "--info", "-i", help="Show template info"),
    install: str | None = typer.Option(None, "--install", help="Install template from URL/path")
):
    """
    Manage domain templates.
    
    Examples:
    
        graphrag-mcp templates --list
        
        graphrag-mcp templates --info academic
    """
    if install:
        console.print(f"📥 Installing template from: {install}")
        console.print("⚠️  Template installation not yet implemented", style="yellow")
        return

    if info:
        _show_template_info(info)
        return

    if list_templates:
        _list_templates()


@app.command("add-documents")
def add_documents(
    project: str = typer.Argument(..., help="Project name"),
    paths: list[str] = typer.Argument(..., help="Document paths to add"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan directories recursively")
):
    """
    Add documents to a project for processing.
    
    Examples:
    
        graphrag-mcp add-documents literature-assistant ./papers/paper1.pdf
        
        graphrag-mcp add-documents legal-helper ./documents/ --recursive
    """
    console.print(f"📄 Adding documents to project: [bold blue]{project}[/bold blue]")

    project_dir = _get_project_dir(project)
    if not project_dir:
        return

    # Create documents directory
    docs_dir = project_dir / "documents"
    docs_dir.mkdir(exist_ok=True)

    added_files = []

    for path_str in paths:
        path = Path(path_str)

        if path.is_file() and path.suffix.lower() == '.pdf':
            # Copy single PDF file
            dest = docs_dir / path.name
            dest.write_bytes(path.read_bytes())
            added_files.append(dest)

        elif path.is_dir() and recursive:
            # Scan directory for PDFs
            for pdf_file in path.rglob("*.pdf"):
                dest = docs_dir / pdf_file.name
                dest.write_bytes(pdf_file.read_bytes())
                added_files.append(dest)

        elif path.is_dir():
            # Scan directory (non-recursive)
            for pdf_file in path.glob("*.pdf"):
                dest = docs_dir / pdf_file.name
                dest.write_bytes(pdf_file.read_bytes())
                added_files.append(dest)

    if added_files:
        console.print(f"✅ Added {len(added_files)} documents:")
        for doc in added_files:
            console.print(f"  📄 {doc.name}")
    else:
        console.print("⚠️  No PDF documents found", style="yellow")


@app.command()
def process(
    project: str = typer.Argument(..., help="Project name to process"),
    force: bool = typer.Option(False, "--force", "-f", help="Reprocess existing documents"),
    graphiti_only: bool = typer.Option(False, "--graphiti-only", help="Only populate Graphiti, skip JSON export")
):
    """
    Process documents into persistent Graphiti knowledge graphs.
    
    This command:
    1. Analyzes documents using enhanced extraction
    2. Populates persistent Graphiti/Neo4j knowledge graph
    3. Saves metadata for MCP server reference
    
    Examples:
    
        graphrag-mcp process literature-assistant
        
        graphrag-mcp process legal-helper --force
        
        graphrag-mcp process my-research --graphiti-only
    """
    console.print(f"⚙️  Processing project: [bold blue]{project}[/bold blue]")

    project_dir = _get_project_dir(project)
    if not project_dir:
        return

    docs_dir = project_dir / "documents"
    if not docs_dir.exists():
        console.print("❌ No documents directory found. Add documents first.", style="red")
        return

    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        console.print("❌ No PDF documents found. Add documents first.", style="red")
        return

    # Load project config to get template
    config_file = project_dir / "config.json"
    template = "academic"  # Default
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
            template = config.get('template', 'academic')

    console.print(f"📋 Template: {template}")
    console.print(f"📁 Documents: {len(pdf_files)} PDF files")
    console.print("🧠 Knowledge Graph: Persistent Graphiti/Neo4j")

    # Initialize components
    config = GraphRAGConfig()
    processor = EnhancedDocumentProcessor(config)

    # Create output directory
    output_dir = project_dir / "processed"
    output_dir.mkdir(exist_ok=True)

    # Initialize Graphiti with project namespace
    async def process_with_graphiti():
        from ..core.graphiti_engine import GraphitiKnowledgeGraph

        # Create project-specific Graphiti instance
        graphiti_engine = GraphitiKnowledgeGraph()

        # Initialize Graphiti connection
        console.print("🔌 Connecting to Neo4j/Graphiti...")
        init_success = await graphiti_engine.initialize()
        if not init_success:
            console.print("❌ Failed to connect to Neo4j. Make sure Neo4j is running.", style="red")
            console.print("💡 Start Neo4j: make setup-neo4j", style="yellow")
            return False

        console.print("✅ Connected to Graphiti knowledge graph")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Track processed documents for this project
            project_metadata = {
                "project_name": project,
                "template": template,
                "processed_date": datetime.now().isoformat(),
                "documents_processed": [],
                "graphiti_stats": {}
            }

            for i, pdf_file in enumerate(pdf_files):
                task = progress.add_task(f"Processing {pdf_file.name}...", total=None)

                try:
                    # Check if already processed (JSON file exists)
                    output_file = output_dir / f"{pdf_file.stem}.json"
                    if output_file.exists() and not force:
                        progress.update(task, description=f"⏭️  Skipping {pdf_file.name} (already processed)")

                        # Load existing metadata
                        with open(output_file) as f:
                            existing_data = json.load(f)
                            project_metadata["documents_processed"].append({
                                "filename": pdf_file.name,
                                "document_id": pdf_file.stem,
                                "status": "skipped",
                                "title": existing_data.get("title", pdf_file.stem)
                            })
                        continue

                    progress.update(task, description=f"📄 Analyzing {pdf_file.name}...")

                    # Process document
                    processing_result = processor.process_document(str(pdf_file))

                    progress.update(task, description="🧠 Adding to knowledge graph...")

                    # Add to Graphiti knowledge graph
                    # Use enhanced chunks as content (better than raw text)
                    document_content = "\n\n".join(processing_result.enhanced_chunks)
                    success = await graphiti_engine.add_document(
                        document_content=document_content,
                        document_id=f"{project}_{pdf_file.stem}",  # Project-namespaced ID
                        metadata={
                            "title": processing_result.document_title,
                            "project": project,
                            "template": template,
                            "filename": pdf_file.name,
                            "entities": processing_result.entities_created,
                            "processing_date": datetime.now().isoformat(),
                            **processing_result.metadata
                        },
                        source_description=f"{template} document from {project} project"
                    )

                    if success:
                        progress.update(task, description=f"✅ Added to knowledge graph: {pdf_file.name}")

                        # Save JSON metadata (unless graphiti-only mode)
                        if not graphiti_only:
                            # Create a serializable dict from ProcessingResult
                            processing_data = {
                                "document_title": processing_result.document_title,
                                "document_path": processing_result.document_path,
                                "text_chunks": processing_result.text_chunks,
                                "enhanced_chunks": processing_result.enhanced_chunks,
                                "entities_created": processing_result.entities_created,
                                "citations_stored": processing_result.citations_stored,
                                "relationships_created": processing_result.relationships_created,
                                "processing_time": processing_result.processing_time,
                                "metadata": processing_result.metadata
                            }
                            with open(output_file, 'w') as f:
                                json.dump(processing_data, f, indent=2)

                        # Update project metadata
                        project_metadata["documents_processed"].append({
                            "filename": pdf_file.name,
                            "document_id": f"{project}_{pdf_file.stem}",
                            "status": "processed",
                            "title": processing_result.document_title,
                            "entities_count": processing_result.entities_created,
                            "graphiti_success": True
                        })

                    else:
                        progress.update(task, description=f"⚠️  Knowledge graph failed, saved locally: {pdf_file.name}")

                        # Save JSON as fallback
                        processing_data = {
                            "document_title": processing_result.document_title,
                            "document_path": processing_result.document_path,
                            "text_chunks": processing_result.text_chunks,
                            "enhanced_chunks": processing_result.enhanced_chunks,
                            "entities_created": processing_result.entities_created,
                            "citations_stored": processing_result.citations_stored,
                            "relationships_created": processing_result.relationships_created,
                            "processing_time": processing_result.processing_time,
                            "metadata": processing_result.metadata
                        }
                        with open(output_file, 'w') as f:
                            json.dump(processing_data, f, indent=2)

                        project_metadata["documents_processed"].append({
                            "filename": pdf_file.name,
                            "document_id": pdf_file.stem,
                            "status": "processed_local_only",
                            "title": processing_result.document_title,
                            "graphiti_success": False
                        })

                except Exception as e:
                    progress.update(task, description=f"❌ Failed {pdf_file.name}: {str(e)}")
                    logger.error(f"Processing failed for {pdf_file}: {e}")

                    project_metadata["documents_processed"].append({
                        "filename": pdf_file.name,
                        "status": "failed",
                        "error": str(e)
                    })

            # Get Graphiti statistics
            try:
                stats = await graphiti_engine.get_knowledge_graph_stats()
                project_metadata["graphiti_stats"] = stats
                console.print(f"📊 Knowledge Graph Stats: {stats.get('total_nodes', 0)} nodes, {stats.get('total_edges', 0)} relationships")
            except Exception as e:
                logger.warning(f"Could not get Graphiti stats: {e}")

            # Save project processing metadata
            metadata_file = project_dir / "processing_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(project_metadata, f, indent=2)

            # Update project config
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
                config["last_processed"] = datetime.now().isoformat()
                config["documents_in_graph"] = len([d for d in project_metadata["documents_processed"] if d.get("graphiti_success", False)])
                config["graphiti_enabled"] = True
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)

        await graphiti_engine.close()
        return True

    # Run async processing
    try:
        import asyncio
        success = asyncio.run(process_with_graphiti())

        if success:
            processed_count = len([f for f in pdf_files])
            console.print()
            console.print(Panel.fit(
                f"[green]🎉 Processing Complete![/green]\\n\\n"
                f"📄 Documents: {processed_count} processed\\n"
                f"🧠 Knowledge Graph: Populated in Neo4j\\n"
                f"📁 Metadata: Saved to {output_dir}\\n\\n"
                f"[dim]Next step:[/dim]\\n"
                f"  Start MCP server: [code]graphrag-mcp serve {project}[/code]",
                title="✅ Success",
                border_style="green"
            ))
        else:
            console.print("❌ Processing failed. Check Neo4j connection.", style="red")

    except Exception as e:
        console.print(f"❌ Processing failed: {e}", style="red")
        logger.error(f"Async processing failed: {e}")


@app.command()
def serve(
    project: str = typer.Argument(..., help="Project name to serve"),
    port: int = typer.Option(8080, "--port", "-p", help="Server port"),
    host: str = typer.Option("localhost", "--host", help="Server host"),
    transport: str = typer.Option("http", "--transport", "-t", help="Transport method (http/stdio)"),
    background: bool = typer.Option(False, "--background", "-b", help="Run in background")
):
    """
    Start Graphiti MCP server for a project.
    
    Serves the persistent knowledge graph created during 'process' phase.
    Connects to existing Neo4j/Graphiti data for the project.
    
    Examples:
    
        graphrag-mcp serve literature-assistant
        
        graphrag-mcp serve legal-helper --port 8081 --transport stdio
    """
    console.print(f"🚀 Starting Graphiti MCP server for: [bold blue]{project}[/bold blue]")

    project_dir = _get_project_dir(project)
    if not project_dir:
        return

    # Check if project has been processed
    metadata_file = project_dir / "processing_metadata.json"
    if not metadata_file.exists():
        console.print("❌ No processing metadata found. Run 'process' first.", style="red")
        console.print("💡 Process documents: [code]graphrag-mcp process {project}[/code]", style="yellow")
        return

    # Load project metadata
    with open(metadata_file) as f:
        metadata = json.load(f)

    # Load project config
    config_file = project_dir / "config.json"
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
        template = config.get('template', 'academic')
        graphiti_enabled = config.get('graphiti_enabled', False)
    else:
        template = 'academic'
        graphiti_enabled = False

    if not graphiti_enabled:
        console.print("⚠️  Project not processed with Graphiti. Run 'process' with current version.", style="yellow")
        console.print("💡 Reprocess: [code]graphrag-mcp process {project} --force[/code]", style="yellow")

    # Display server info
    documents_in_graph = metadata.get("documents_processed", [])
    successful_docs = [d for d in documents_in_graph if d.get("graphiti_success", False)]

    console.print(f"📋 Server: {host}:{port} ({transport})")
    console.print(f"🎯 Template: {template}")
    console.print("🧠 Knowledge Graph: Neo4j/Graphiti")
    console.print(f"📊 Documents in Graph: {len(successful_docs)}/{len(documents_in_graph)}")

    if metadata.get("graphiti_stats"):
        stats = metadata["graphiti_stats"]
        console.print(f"📈 Graph Stats: {stats.get('total_nodes', 0)} nodes, {stats.get('total_edges', 0)} relationships")

    if background:
        console.print("⚠️  Background mode not yet implemented", style="yellow")
        return

    # Start Graphiti MCP server
    async def start_graphiti_server():
        try:
            from ..mcp.graphiti_server import GraphitiMCPServer

            console.print("🔌 Connecting to Graphiti knowledge graph...")

            # Create Graphiti MCP server with project context
            server = GraphitiMCPServer(
                name=f"GraphRAG {project.title()} Assistant",
                instructions=f"Graphiti-powered research assistant for {project} project",
                host=host,
                port=port
            )

            # Initialize server and connect to existing Graphiti graph
            await server.initialize()

            # Set project context for queries
            server.project_name = project
            server.template_name = template

            console.print("✅ Connected to knowledge graph")
            console.print()
            console.print(Panel.fit(
                f"[green]🚀 Graphiti MCP Server Running![/green]\\n\\n"
                f"📡 Endpoint: {host}:{port}\\n"
                f"🧠 Knowledge Graph: Connected to Neo4j\\n"
                f"📋 Project: {project} ({template} template)\\n"
                f"📊 Documents: {len(successful_docs)} in knowledge graph\\n\\n"
                f"[dim]Claude Desktop Integration:[/dim]\\n"
                f'[code]{{"mcpServers": {{"graphrag-{project}": {{"command": "graphrag-mcp", "args": ["serve", "{project}", "--transport", "stdio"]}}}}[/code]\\n\\n'
                f"[dim]Stop server:[/dim] Ctrl+C",
                title="🎯 Server Ready",
                border_style="green"
            ))

            # Start server
            if transport == "http":
                await server.run_server(transport="http", host=host, port=port)
            else:
                await server.run_server(transport="stdio")

        except Exception as e:
            console.print(f"❌ Failed to start Graphiti server: {e}", style="red")
            logger.error(f"Graphiti server startup failed: {e}")
            raise

    try:
        import asyncio
        asyncio.run(start_graphiti_server())

    except KeyboardInterrupt:
        console.print("\n👋 Graphiti MCP server stopped by user")
    except Exception as e:
        console.print(f"❌ Server failed to start: {e}", style="red")
        logger.error(f"Server startup failed: {e}")


@app.command("serve-universal")
def serve_universal(
    template: str = typer.Option("academic", "--template", "-t", help="Domain template to use"),
    port: int = typer.Option(8080, "--port", "-p", help="Server port"),
    host: str = typer.Option("localhost", "--host", help="Server host"),
    transport: str = typer.Option("http", "--transport", help="Transport method (http/stdio)")
):
    """
    Start universal MCP server without a project (for testing).
    
    Examples:
    
        graphrag-mcp serve-universal --template academic
        
        graphrag-mcp serve-universal --template academic --transport stdio
    """
    console.print("🚀 Starting Universal MCP Server")
    console.print(f"📋 Server: {host}:{port} ({transport})")
    console.print(f"🎯 Template: {template}")
    console.print("📄 No documents loaded (use load_document_collection tool)")

    # Import and start server
    try:
        import asyncio

        from ..mcp.server_generator import run_universal_server_cli

        console.print("🚀 Starting Universal MCP Server...")
        
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            console.print("⚠️ Already running in asyncio event loop")
            console.print("💡 Try running this command in a fresh terminal or Python process")
            return
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            asyncio.run(run_universal_server_cli(
                template=template,
                host=host,
                port=port,
                transport=transport
            ))

    except KeyboardInterrupt:
        console.print("\n👋 Server stopped by user")
    except Exception as e:
        console.print(f"❌ Server failed to start: {e}", style="red")
        logger.error(f"Server startup failed: {e}")


@app.command()
def status(
    project: str | None = typer.Argument(None, help="Project name (optional)")
):
    """
    Show status of projects and system health.
    """
    console.print("📊 [bold]GraphRAG MCP Toolkit Status[/bold]")
    console.print()

    # System health
    console.print("🔧 [bold]System Health[/bold]")

    # Check Ollama
    try:
        config = GraphRAGConfig()
        llm_engine = LLMAnalysisEngine(
            llm_model=config.model.llm_model,
            temperature=config.model.temperature,
            max_context=config.model.max_context,
            max_predict=config.model.max_predict
        )
        
        # Try a simple test to verify connection
        test_result = llm_engine.analyze_document_comprehensive(["Test connection"], "test_doc")
        if test_result:
            console.print("✅ Ollama server: Online")
            console.print(f"✅ LLM model ({config.model.llm_model}): Available")
            console.print(f"✅ Embedding model ({config.model.embedding_model}): Available")
        else:
            console.print("❌ Ollama server: Connection failed", style="red")
    except Exception as e:
        console.print(f"❌ Ollama health check failed: {e}", style="red")

    console.print()

    # Projects overview
    if project:
        _show_project_status(project)
    else:
        _show_all_projects_status()


def _get_available_templates() -> list[str]:
    """Get list of available domain templates"""
    # For now, return built-in templates
    # Later this will scan the templates directory
    return ["academic", "legal", "medical", "financial", "engineering"]


def _create_project_structure(project_dir: Path, name: str, template: str):
    """Create the basic project structure"""
    # Create directories
    (project_dir / "documents").mkdir(exist_ok=True)
    (project_dir / "processed").mkdir(exist_ok=True)
    (project_dir / "mcp").mkdir(exist_ok=True)

    # Create README
    readme_content = f"""# {name}

GraphRAG MCP Assistant using {template} template.

## Directory Structure

- `documents/` - Source PDF documents
- `processed/` - Processed knowledge graphs  
- `mcp/` - Generated MCP server files
- `config.json` - Project configuration

## Usage

1. Add documents: `graphrag-mcp add-documents {name} ./papers/`
2. Process corpus: `graphrag-mcp process {name}`
3. Start server: `graphrag-mcp serve {name}`
"""

    (project_dir / "README.md").write_text(readme_content)


def _list_templates():
    """List available templates"""
    console.print("📋 [bold]Available Templates[/bold]")
    console.print()

    templates = {
        "academic": "Literature review and research analysis",
        "legal": "Legal document analysis (planned)",
        "medical": "Clinical guidelines and protocols (planned)",
        "financial": "Financial document analysis (planned)",
        "engineering": "Technical specifications (planned)"
    }

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Template", style="cyan")
    table.add_column("Description")
    table.add_column("Status")

    for name, desc in templates.items():
        status = "✅ Available" if name == "academic" else "🚧 Planned"
        table.add_row(name, desc, status)

    console.print(table)


def _show_template_info(template: str):
    """Show detailed template information"""
    templates_info = {
        "academic": {
            "name": "Academic Research",
            "description": "Optimized for literature review and research analysis",
            "entities": ["authors", "institutions", "methods", "concepts", "technologies"],
            "tools": ["query_papers", "find_citations", "research_gaps", "methodology_overview"],
            "status": "available"
        }
    }

    if template not in templates_info:
        console.print(f"❌ Template '{template}' not found", style="red")
        return

    info = templates_info[template]

    panel = Panel.fit(
        f"[bold]{info['name']}[/bold]\\n\\n"
        f"{info['description']}\\n\\n"
        f"[dim]Entity Types:[/dim] {', '.join(info['entities'])}\\n"
        f"[dim]MCP Tools:[/dim] {', '.join(info['tools'])}\\n"
        f"[dim]Status:[/dim] {info['status']}",
        title=f"📋 Template: {template}",
        border_style="blue"
    )
    console.print(panel)


def _get_project_dir(project: str) -> Path | None:
    """Get project directory and validate it exists"""
    project_dir = cli_state.projects_dir / project

    if not project_dir.exists():
        console.print(f"❌ Project '{project}' not found", style="red")
        console.print(f"Available projects: {[p.name for p in cli_state.projects_dir.glob('*') if p.is_dir()]}")
        return None

    return project_dir


def _show_project_status(project: str):
    """Show status for specific project"""
    project_dir = _get_project_dir(project)
    if not project_dir:
        return

    console.print(f"📁 [bold]Project: {project}[/bold]")

    # Load config
    config_file = project_dir / "config.json"
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
        console.print(f"🎯 Template: {config.get('template', 'unknown')}")

    # Document count
    docs_dir = project_dir / "documents"
    doc_count = len(list(docs_dir.glob("*.pdf"))) if docs_dir.exists() else 0
    console.print(f"📄 Documents: {doc_count}")

    # Processed count
    processed_dir = project_dir / "processed"
    processed_count = len(list(processed_dir.glob("*.json"))) if processed_dir.exists() else 0
    console.print(f"⚙️  Processed: {processed_count}")

    # MCP server status
    console.print("🚀 MCP Server: Not started")


def _show_all_projects_status():
    """Show status for all projects"""
    console.print("📁 [bold]Projects[/bold]")

    projects = [p for p in cli_state.projects_dir.glob("*") if p.is_dir()]

    if not projects:
        console.print("No projects found. Create one with: [code]graphrag-mcp create my-assistant[/code]")
        return

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Project", style="cyan")
    table.add_column("Template")
    table.add_column("Documents", justify="right")
    table.add_column("Processed", justify="right")
    table.add_column("Status")

    for project_dir in projects:
        name = project_dir.name

        # Load config
        config_file = project_dir / "config.json"
        template = "unknown"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                template = config.get('template', 'unknown')
            except:
                pass

        # Count documents
        docs_dir = project_dir / "documents"
        doc_count = len(list(docs_dir.glob("*.pdf"))) if docs_dir.exists() else 0

        # Count processed
        processed_dir = project_dir / "processed"
        processed_count = len(list(processed_dir.glob("*.json"))) if processed_dir.exists() else 0

        # Determine status
        if processed_count > 0:
            status = "✅ Ready"
        elif doc_count > 0:
            status = "🔄 Needs processing"
        else:
            status = "📄 Needs documents"

        table.add_row(name, template, str(doc_count), str(processed_count), status)

    console.print(table)


@app.command()
def serve_graphiti(
    template: str = typer.Option("academic", "--template", "-t", help="Domain template to use"),
    port: int = typer.Option(8080, "--port", "-p", help="Server port"),
    host: str = typer.Option("localhost", "--host", help="Server host"),
    neo4j_uri: str = typer.Option("bolt://localhost:7687", "--neo4j-uri", help="Neo4j connection URI"),
    neo4j_user: str = typer.Option("neo4j", "--neo4j-user", help="Neo4j username"),
    neo4j_password: str = typer.Option("password", "--neo4j-password", help="Neo4j password")
):
    """
    Start Graphiti-powered MCP server with real-time knowledge graphs.
    
    Examples:
    
        graphrag-mcp serve-graphiti --template academic
        
        graphrag-mcp serve-graphiti --template academic --port 8081
        
        graphrag-mcp serve-graphiti --neo4j-uri bolt://localhost:7687
    """
    console.print("🚀 Starting Graphiti MCP Server")
    console.print(f"📋 Server: {host}:{port}")
    console.print(f"🎯 Template: {template}")
    console.print(f"🗃️  Neo4j: {neo4j_uri}")
    console.print("🧠 Backend: [bold magenta]Graphiti + Neo4j[/bold magenta]")

    # Check Neo4j connection
    console.print("🔍 Checking Neo4j connection...")
    try:
        import asyncio

        from ..mcp.graphiti_server import GraphitiMCPServer

        # Create server
        server = GraphitiMCPServer(
            name="GraphRAG Graphiti Assistant",
            instructions=f"Real-time knowledge graph assistant using {template} template",
            host=host,
            port=port,
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password
        )

        console.print("🚀 Starting Graphiti MCP Server...")
        console.print("📊 Real-time knowledge graph capabilities enabled")
        console.print("🔗 Use add_document_to_graph tool to add documents")
        console.print("🔍 Use search_knowledge_graph tool for semantic search")

        # Run server
        asyncio.run(server.run())

    except KeyboardInterrupt:
        console.print("\n👋 Server stopped by user", style="yellow")
    except Exception as e:
        console.print(f"❌ Error starting Graphiti server: {e}", style="red")
        console.print("💡 Make sure Neo4j is running: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest", style="dim")
        raise typer.Exit(1)


@app.command()
def visualize(
    project: str = typer.Argument(..., help="Project name to visualize"),
    max_nodes: int = typer.Option(50, "--max-nodes", help="Maximum nodes to display"),
    interactive: bool = typer.Option(True, "--interactive/--static", help="Interactive visualization"),
    output: str | None = typer.Option(None, "--output", help="Save visualization to file")
):
    """
    Show knowledge graph visualization using Graphiti + yFiles.
    
    Examples:
    
        graphrag-mcp visualize my-project
        
        graphrag-mcp visualize research --max-nodes 100 --output graph.html
    """
    console.print(f"🕸️  Visualizing knowledge graph for: [bold blue]{project}[/bold blue]")
    
    project_dir = _get_project_dir(project)
    if not project_dir:
        return
    
    # Check if project has been processed
    metadata_file = project_dir / "processing_metadata.json"
    if not metadata_file.exists():
        console.print("❌ No processing metadata found. Run 'process' first.", style="red")
        return
    
    try:
        from ..visualization.graphiti_yfiles import GraphitiYFilesVisualizer
        from ..core.graphiti_engine import GraphitiKnowledgeGraph
        
        # Create knowledge graph connection
        graphiti_engine = GraphitiKnowledgeGraph()
        
        # Create visualizer
        visualizer = GraphitiYFilesVisualizer(graphiti_engine)
        
        console.print("🔍 Creating knowledge graph visualization...")
        
        # Create visualization
        import asyncio
        result = asyncio.run(visualizer.create_visualization(
            title=f"Knowledge Graph: {project}",
            max_nodes=max_nodes,
            enable_sidebar=interactive,
            enable_search=interactive,
            enable_neighborhood=interactive
        ))
        
        if result:
            console.print("✅ Knowledge graph visualization created successfully!")
            if output:
                console.print(f"📄 Saved to: {output}")
        else:
            console.print("⚠️  Visualization creation failed", style="yellow")
            
    except ImportError:
        console.print("❌ Visualization dependencies not installed", style="red")
        console.print("💡 Install with: pip install yfiles plotly networkx", style="yellow")
    except Exception as e:
        console.print(f"❌ Visualization failed: {e}", style="red")


@app.command()
def validate(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed validation info"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix common issues")
):
    """
    Validate system prerequisites and configuration.
    
    Examples:
    
        graphrag-mcp validate
        
        graphrag-mcp validate --verbose --fix
    """
    console.print("🔍 [bold]System Validation[/bold]")
    console.print()
    
    validation_results = []
    
    # Check Python version
    import sys
    python_version = sys.version_info
    if python_version >= (3, 11):
        console.print("✅ Python version: 3.11+ (recommended)")
        validation_results.append(True)
    elif python_version >= (3, 9):
        console.print("⚠️  Python version: 3.9+ (minimum, 3.11+ recommended)", style="yellow")
        validation_results.append(True)
    else:
        console.print("❌ Python version: Too old (3.9+ required)", style="red")
        validation_results.append(False)
    
    # Check Ollama connection
    try:
        config = GraphRAGConfig()
        llm_engine = LLMAnalysisEngine(
            llm_model=config.model.llm_model,
            temperature=config.model.temperature,
            max_context=config.model.max_context,
            max_predict=config.model.max_predict
        )
        
        test_result = llm_engine.analyze_document_comprehensive(["Test connection"], "test_doc")
        if test_result:
            console.print("✅ Ollama server: Connected and working")
            console.print(f"✅ LLM model ({config.model.llm_model}): Available")
            validation_results.append(True)
        else:
            console.print("❌ Ollama server: Connection failed", style="red")
            validation_results.append(False)
    except Exception as e:
        console.print(f"❌ Ollama validation failed: {e}", style="red")
        validation_results.append(False)
        if fix:
            console.print("💡 Fix suggestion: Start Ollama with 'ollama serve'", style="yellow")
    
    # Check Neo4j connection (optional)
    try:
        from ..core.neo4j_entity_manager import Neo4jEntityManager
        entity_manager = Neo4jEntityManager(
            uri=config.storage.neo4j.uri,
            auth=(config.storage.neo4j.username, config.storage.neo4j.password)
        )
        console.print("✅ Neo4j connection: Available")
        validation_results.append(True)
    except Exception as e:
        console.print("⚠️  Neo4j connection: Optional (for advanced features)", style="yellow")
        if verbose:
            console.print(f"   Details: {e}", style="dim")
        validation_results.append(True)  # Neo4j is optional
    
    # Check ChromaDB
    try:
        from ..core.chromadb_citation_manager import ChromaDBCitationManager
        citation_manager = ChromaDBCitationManager(
            collection_name="test_validation",
            persist_directory="test_chroma_validation"
        )
        console.print("✅ ChromaDB: Available")
        validation_results.append(True)
    except Exception as e:
        console.print(f"❌ ChromaDB validation failed: {e}", style="red")
        validation_results.append(False)
    
    # Overall result
    console.print()
    if all(validation_results):
        console.print("🎉 [bold green]System validation passed![/bold green]")
        console.print("✅ All components are working correctly")
    else:
        console.print("⚠️  [bold yellow]System validation completed with issues[/bold yellow]")
        console.print("💡 Check the errors above and install missing dependencies")


@app.command()
def quick_setup(
    project: str = typer.Argument(..., help="Project name to create"),
    documents: str = typer.Argument(..., help="Path to documents folder"),
    template: str = typer.Option("academic", "--template", "-t", help="Domain template"),
    auto_process: bool = typer.Option(True, "--auto-process/--no-process", help="Automatically process documents"),
    auto_serve: bool = typer.Option(False, "--auto-serve", help="Start MCP server after processing")
):
    """
    Quick setup: create project, add documents, and optionally process them.
    
    Examples:
    
        graphrag-mcp quick-setup research-project ./papers/
        
        graphrag-mcp quick-setup legal-docs ./contracts/ --template legal --auto-serve
    """
    console.print(f"🚀 [bold]Quick Setup: {project}[/bold]")
    console.print()
    
    # Step 1: Create project
    console.print("📁 Step 1: Creating project...")
    try:
        # Use the existing create command logic
        from pathlib import Path
        
        project_dir = cli_state.projects_dir / project
        if project_dir.exists():
            if not typer.confirm(f"Project '{project}' already exists. Overwrite?"):
                console.print("❌ Quick setup cancelled", style="red")
                return
        
        # Create project structure
        project_dir.mkdir(parents=True, exist_ok=True)
        _create_project_structure(project_dir, project, template)
        
        # Create config
        project_config = {
            "name": project,
            "template": template,
            "created_date": datetime.now().isoformat(),
            "version": "0.1.0",
            "documents": [],
            "mcp_server": {"enabled": False}
        }
        
        config_file = project_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(project_config, f, indent=2)
        
        console.print("✅ Project created successfully")
        
    except Exception as e:
        console.print(f"❌ Project creation failed: {e}", style="red")
        return
    
    # Step 2: Add documents
    console.print("📄 Step 2: Adding documents...")
    try:
        docs_dir = project_dir / "documents"
        docs_dir.mkdir(exist_ok=True)
        
        documents_path = Path(documents)
        if not documents_path.exists():
            console.print(f"❌ Documents path not found: {documents}", style="red")
            return
        
        added_files = []
        if documents_path.is_file() and documents_path.suffix.lower() == '.pdf':
            # Single PDF
            dest = docs_dir / documents_path.name
            dest.write_bytes(documents_path.read_bytes())
            added_files.append(dest)
        elif documents_path.is_dir():
            # Directory of PDFs
            for pdf_file in documents_path.glob("*.pdf"):
                dest = docs_dir / pdf_file.name
                dest.write_bytes(pdf_file.read_bytes())
                added_files.append(dest)
        
        console.print(f"✅ Added {len(added_files)} documents")
        
    except Exception as e:
        console.print(f"❌ Adding documents failed: {e}", style="red")
        return
    
    # Step 3: Process documents (if requested)
    if auto_process and added_files:
        console.print("⚙️  Step 3: Processing documents...")
        try:
            # Call the existing process command
            import subprocess
            result = subprocess.run([
                "python", "-m", "graphrag_mcp.cli.main", 
                "process", project
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ Documents processed successfully")
            else:
                console.print(f"⚠️  Processing completed with warnings", style="yellow")
                if result.stderr:
                    console.print(f"   Details: {result.stderr}", style="dim")
                    
        except Exception as e:
            console.print(f"❌ Processing failed: {e}", style="red")
            auto_serve = False  # Don't start server if processing failed
    
    # Step 4: Start MCP server (if requested)
    if auto_serve:
        console.print("🚀 Step 4: Starting MCP server...")
        console.print("💡 Use Ctrl+C to stop the server")
        try:
            # Call the existing serve command
            import subprocess
            subprocess.run([
                "python", "-m", "graphrag_mcp.cli.main", 
                "serve", project, "--transport", "stdio"
            ])
        except KeyboardInterrupt:
            console.print("\n👋 Server stopped by user")
        except Exception as e:
            console.print(f"❌ Server failed to start: {e}", style="red")
    
    # Success summary
    console.print()
    console.print("🎉 [bold green]Quick Setup Complete![/bold green]")
    console.print(f"📁 Project: {project}")
    console.print(f"📄 Documents: {len(added_files)} added")
    console.print(f"🎯 Template: {template}")
    
    if not auto_process:
        console.print(f"💡 Next: [code]graphrag-mcp process {project}[/code]")
    elif not auto_serve:
        console.print(f"💡 Next: [code]graphrag-mcp serve {project}[/code]")


if __name__ == "__main__":
    app()

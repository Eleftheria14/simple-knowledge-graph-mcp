"""
Main CLI Application for GraphRAG MCP Toolkit

Typer-based command-line interface for creating, managing, and deploying
GraphRAG MCP servers across different domains.
"""

import logging
from pathlib import Path
from typing import Optional, List
import json

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

# Core components
from ..core import DocumentProcessor, AdvancedAnalyzer, OllamaEngine

# Configuration
from pydantic import BaseModel

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
    current_project: Optional[str] = None
    config_dir: Path = Path.home() / ".graphrag-mcp"
    projects_dir: Path = Path.home() / ".graphrag-mcp" / "projects"
    templates_dir: Path = Path.home() / ".graphrag-mcp" / "templates"

cli_state = CLIState()


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    config_dir: Optional[str] = typer.Option(None, "--config-dir", help="Custom config directory")
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
    directory: Optional[str] = typer.Option(None, "--directory", "-d", help="Project directory"),
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
    info: Optional[str] = typer.Option(None, "--info", "-i", help="Show template info"),
    install: Optional[str] = typer.Option(None, "--install", help="Install template from URL/path")
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
    paths: List[str] = typer.Argument(..., help="Document paths to add"),
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
    force: bool = typer.Option(False, "--force", "-f", help="Reprocess existing documents")
):
    """
    Process documents into knowledge graphs.
    
    Examples:
    
        graphrag-mcp process literature-assistant
        
        graphrag-mcp process legal-helper --force
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
    
    # Initialize analyzer
    analyzer = AdvancedAnalyzer()
    
    # Create output directory
    output_dir = project_dir / "processed"
    output_dir.mkdir(exist_ok=True)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        for i, pdf_file in enumerate(pdf_files):
            task = progress.add_task(f"Processing {pdf_file.name}...", total=None)
            
            try:
                # Check if already processed
                output_file = output_dir / f"{pdf_file.stem}.json"
                if output_file.exists() and not force:
                    progress.update(task, description=f"⏭️  Skipping {pdf_file.name} (already processed)")
                    continue
                
                # Analyze document
                corpus_doc = analyzer.analyze_for_corpus(str(pdf_file))
                
                # Save results
                with open(output_file, 'w') as f:
                    json.dump(corpus_doc.model_dump(), f, indent=2)
                
                progress.update(task, description=f"✅ Processed {pdf_file.name}")
                
            except Exception as e:
                progress.update(task, description=f"❌ Failed {pdf_file.name}: {str(e)}")
                logger.error(f"Processing failed for {pdf_file}: {e}")
    
    console.print(f"🎉 Processing complete! Results saved to: {output_dir}")


@app.command()
def serve(
    project: str = typer.Argument(..., help="Project name to serve"),
    port: int = typer.Option(8080, "--port", "-p", help="Server port"),
    host: str = typer.Option("localhost", "--host", help="Server host"),
    transport: str = typer.Option("http", "--transport", "-t", help="Transport method (http/stdio)"),
    background: bool = typer.Option(False, "--background", "-b", help="Run in background")
):
    """
    Start MCP server for a project.
    
    Examples:
    
        graphrag-mcp serve literature-assistant
        
        graphrag-mcp serve legal-helper --port 8081 --transport stdio
    """
    console.print(f"🚀 Starting MCP server for: [bold blue]{project}[/bold blue]")
    
    project_dir = _get_project_dir(project)
    if not project_dir:
        return
    
    processed_dir = project_dir / "processed"
    if not processed_dir.exists():
        console.print("❌ No processed documents found. Run 'process' first.", style="red")
        return
    
    # Load project config
    config_file = project_dir / "config.json"
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
        template = config.get('template', 'academic')
    else:
        template = 'academic'
    
    console.print(f"📋 Server: {host}:{port} ({transport})")
    console.print(f"🎯 Template: {template}")
    console.print(f"📁 Documents: {processed_dir}")
    
    if background:
        console.print("⚠️  Background mode not yet implemented", style="yellow")
        return
    
    # Import and start server
    try:
        import asyncio
        from ..mcp.server_generator import run_universal_server_cli
        
        console.print("🚀 Starting Universal MCP Server...")
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
    console.print(f"🚀 Starting Universal MCP Server")
    console.print(f"📋 Server: {host}:{port} ({transport})")
    console.print(f"🎯 Template: {template}")
    console.print("📄 No documents loaded (use load_document_collection tool)")
    
    # Import and start server
    try:
        import asyncio
        from ..mcp.server_generator import run_universal_server_cli
        
        console.print("🚀 Starting Universal MCP Server...")
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
    project: Optional[str] = typer.Argument(None, help="Project name (optional)")
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
        ollama_engine = OllamaEngine()
        health = ollama_engine.check_health()
        if health["server_accessible"]:
            console.print("✅ Ollama server: Online")
            console.print(f"✅ LLM model ({health['config']['llm_model']}): Available")
            console.print(f"✅ Embedding model ({health['config']['embedding_model']}): Available")
        else:
            console.print("❌ Ollama server: Offline", style="red")
    except Exception as e:
        console.print(f"❌ Ollama health check failed: {e}", style="red")
    
    console.print()
    
    # Projects overview
    if project:
        _show_project_status(project)
    else:
        _show_all_projects_status()


def _get_available_templates() -> List[str]:
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


def _get_project_dir(project: str) -> Optional[Path]:
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
    console.print(f"🚀 Starting Graphiti MCP Server")
    console.print(f"📋 Server: {host}:{port}")
    console.print(f"🎯 Template: {template}")
    console.print(f"🗃️  Neo4j: {neo4j_uri}")
    console.print(f"🧠 Backend: [bold magenta]Graphiti + Neo4j[/bold magenta]")
    
    # Check Neo4j connection
    console.print("🔍 Checking Neo4j connection...")
    try:
        import asyncio
        from ..mcp.graphiti_server import GraphitiMCPServer
        
        # Create server
        server = GraphitiMCPServer(
            name=f"GraphRAG Graphiti Assistant",
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


if __name__ == "__main__":
    app()
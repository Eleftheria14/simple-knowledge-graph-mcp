"""
Simplified CLI Main - New 3-Layer Architecture

This replaces the complex main.py with a thin CLI that directly uses
the service layer. No more nested async wrappers or complex processing chains.

Key improvements:
- Direct service layer calls
- Clear error handling
- Eliminated wrapper hierarchy
- Better maintainability
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

# Import simplified interfaces
from ..interfaces.cli_interface import CLIInterface
from ..core.config import GraphRAGConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create CLI app
app = typer.Typer(
    name="graphrag-mcp",
    help="GraphRAG MCP Toolkit - Simplified Architecture",
    add_completion=False,
    rich_markup_mode="rich"
)

# Console for rich output
console = Console()

# Global CLI interface
cli_interface: Optional[CLIInterface] = None


def get_cli_interface() -> CLIInterface:
    """Get or create CLI interface."""
    global cli_interface
    if cli_interface is None:
        cli_interface = CLIInterface()
    return cli_interface


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """
    GraphRAG MCP Toolkit - Simplified 3-Layer Architecture
    
    Transform documents into domain-specific AI assistants with:
    • Direct service layer calls (no subprocess overhead)
    • Clear error handling (no wrapper confusion)
    • Better performance (eliminated wrapper layers)
    • Easier debugging (direct error propagation)
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        console.print("🔍 Verbose mode enabled", style="dim")
    
    console.print("🎯 Using simplified 3-layer architecture", style="dim")


@app.command()
def create(
    name: str = typer.Argument(..., help="Name of the assistant to create"),
    template: str = typer.Option("academic", "--template", "-t", help="Domain template to use"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing project")
):
    """
    Create a new domain-specific GraphRAG assistant.
    
    Uses direct service layer calls instead of complex wrappers.
    
    Examples:
    
        graphrag-mcp create literature-assistant --template academic
        
        graphrag-mcp create legal-helper --template legal --force
    """
    cli = get_cli_interface()
    success = cli.create_project(name, template, force)
    
    if not success:
        raise typer.Exit(1)


@app.command()
def add_documents(
    project: str = typer.Argument(..., help="Project name"),
    documents_path: str = typer.Argument(..., help="Path to documents or directory"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Search recursively for PDFs")
):
    """
    Add documents to a project.
    
    Direct service call with clear error handling.
    
    Examples:
    
        graphrag-mcp add-documents my-project ./papers/
        
        graphrag-mcp add-documents legal-project ./legal-docs/ --recursive
    """
    cli = get_cli_interface()
    success = cli.add_documents(project, documents_path, recursive)
    
    if not success:
        raise typer.Exit(1)


@app.command()
def process(
    project: str = typer.Argument(..., help="Project name to process"),
    force: bool = typer.Option(False, "--force", "-f", help="Reprocess existing documents"),
    graphiti_only: bool = typer.Option(False, "--graphiti-only", help="Only populate Graphiti, skip JSON export")
):
    """
    Process documents into persistent knowledge graphs.
    
    NEW: Direct service layer processing - no wrapper hierarchy!
    
    This command:
    1. Uses unified DocumentProcessingService (no wrappers)
    2. Provides clear progress tracking
    3. Gives detailed error messages
    4. Populates persistent Graphiti/Neo4j knowledge graph
    
    Examples:
    
        graphrag-mcp process literature-assistant
        
        graphrag-mcp process legal-helper --force
    """
    console.print(Panel.fit(
        "[bold green]🎯 NEW SIMPLIFIED ARCHITECTURE[/bold green]\\n\\n"
        "Benefits:\\n"
        "• Direct service calls (no subprocess overhead)\\n"
        "• Clear error messages (no wrapper confusion)\\n"
        "• Better resource management\\n"
        "• Easier debugging\\n\\n"
        "[dim]Processing will be faster and more reliable![/dim]",
        title="🚀 Architecture Upgrade",
        border_style="green"
    ))
    
    async def process_async():
        cli = get_cli_interface()
        success = await cli.process_project(project, force, graphiti_only)
        
        if not success:
            raise typer.Exit(1)
        
        # Clean up resources
        await cli.cleanup()
    
    # Run async processing
    try:
        asyncio.run(process_async())
    except KeyboardInterrupt:
        console.print("\\n⏸️ Processing interrupted by user", style="yellow")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Processing failed: {str(e)}", style="red")
        raise typer.Exit(1)


@app.command()
def status(
    project: str = typer.Argument(..., help="Project name")
):
    """
    Get comprehensive project status.
    
    Direct service call with detailed information.
    
    Examples:
    
        graphrag-mcp status literature-assistant
    """
    cli = get_cli_interface()
    success = cli.get_project_status(project)
    
    if not success:
        raise typer.Exit(1)


@app.command()
def list_projects():
    """
    List all projects with their status.
    
    Direct service call with formatted output.
    """
    cli = get_cli_interface()
    success = cli.list_projects()
    
    if not success:
        raise typer.Exit(1)


@app.command()
def templates(
    list_templates: bool = typer.Option(False, "--list", help="List available templates"),
    info: str = typer.Option(None, "--info", help="Get detailed template information")
):
    """
    Manage domain templates.
    
    Examples:
    
        graphrag-mcp templates --list
        
        graphrag-mcp templates --info academic
    """
    cli = get_cli_interface()
    
    if info:
        # Get specific template info
        try:
            result = cli.project_service.get_template_info(info)
            if result["status"] == "success":
                template = result["template"]
                console.print(f"🎓 Template: [bold]{template['name']}[/bold]")
                console.print(f"📝 Description: {template['description']}")
                console.print(f"🔧 Features: {', '.join(template['features'])}")
                console.print(f"🎯 Domains: {', '.join(template['domains'])}")
            else:
                console.print(f"❌ Template not found: {info}", style="red")
                raise typer.Exit(1)
        except Exception as e:
            console.print(f"❌ Failed to get template info: {str(e)}", style="red")
            raise typer.Exit(1)
    else:
        # List all templates (default behavior)
        success = cli.list_templates()
        if not success:
            raise typer.Exit(1)


@app.command()
def serve_universal(
    template: str = typer.Option("academic", "--template", "-t", help="Template to serve"),
    transport: str = typer.Option("stdio", "--transport", help="Transport protocol"),
    host: str = typer.Option("localhost", "--host", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", help="Port to bind to")
):
    """
    Start universal MCP server with simplified architecture.
    
    This will be updated to use the new service layer.
    
    Examples:
    
        graphrag-mcp serve-universal --template academic --transport stdio
    """
    console.print(Panel.fit(
        "[yellow]⚠️ MCP Server Integration[/yellow]\\n\\n"
        "The MCP server will be updated to use the new\\n"
        "simplified architecture in the next phase.\\n\\n"
        "[dim]For now, use the existing serve command.[/dim]",
        title="🔄 Coming Soon",
        border_style="yellow"
    ))
    
    # TODO: Implement simplified MCP server using service layer
    # For now, fall back to existing implementation
    console.print("💡 Use existing serve command until MCP integration is updated")


if __name__ == "__main__":
    app()
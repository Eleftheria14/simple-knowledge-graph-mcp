"""
GraphRAG MCP Prerequisites Checking

This module provides comprehensive system validation for GraphRAG MCP toolkit.
"""

import importlib
import subprocess
import sys
from pathlib import Path
from typing import Any

from ..ui.status import ValidationResult


def check_prerequisites(verbose: bool = True) -> ValidationResult:
    """
    Comprehensive check of all required services and dependencies
    
    Args:
        verbose: Whether to print status messages
        
    Returns:
        ValidationResult with status and issues
    """
    if verbose:
        print("🔍 Comprehensive Prerequisites Check")
        print("=" * 50)

    # Track overall status
    all_checks_passed = True
    failed_checks = []
    details = {}

    # 1. Check Python environment
    if verbose:
        print("\n1️⃣ Python Environment:")
        print(f"   ✅ Python version: {sys.version.split()[0]}")
        print(f"   ✅ Python path: {sys.executable}")

    details["python_version"] = sys.version.split()[0]
    details["python_path"] = sys.executable

    # 2. Check essential Python packages
    if verbose:
        print("\n2️⃣ Essential Python Packages:")

    packages = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("tqdm", "tqdm"),
        ("plotly", "plotly"),
        ("networkx", "networkx"),
        ("asyncio", "asyncio")
    ]

    missing_packages = []
    package_status = {}

    for package, import_name in packages:
        if _check_python_package(package, import_name, verbose):
            package_status[package] = "installed"
        else:
            all_checks_passed = False
            missing_packages.append(package)
            package_status[package] = "missing"

    details["packages"] = package_status

    if missing_packages:
        failed_checks.append(f"Missing Python packages: {', '.join(missing_packages)}")

    # 3. Check project structure
    if verbose:
        print("\n3️⃣ Project Structure:")

    structure_valid = _check_project_structure(verbose)
    details["project_structure"] = structure_valid

    if not structure_valid:
        all_checks_passed = False
        failed_checks.append("Project structure: Missing files or wrong directory")

    # 4. Check Ollama service
    if verbose:
        print("\n4️⃣ Ollama Service:")

    ollama_running = _check_service("Ollama Server", "http://localhost:11434/api/tags",
                                   "Running and accessible", verbose)
    details["ollama_service"] = ollama_running

    if not ollama_running:
        all_checks_passed = False
        failed_checks.append("Ollama service: Not running or accessible")
        if verbose:
            print("   💡 Start with: ollama serve")

    # 5. Check Ollama models
    if verbose:
        print("\n5️⃣ Ollama Models:")

    models_status = _check_ollama_models(verbose)
    details["ollama_models"] = models_status

    if not models_status["all_available"]:
        all_checks_passed = False
        failed_checks.append("Ollama models: Missing llama3.1:8b or nomic-embed-text")
        if verbose:
            print("   💡 Install missing models with:")
            print("      ollama pull llama3.1:8b")
            print("      ollama pull nomic-embed-text")

    # 6. Check Neo4j service
    if verbose:
        print("\n6️⃣ Neo4j Database:")

    neo4j_running = _check_service("Neo4j Database", "http://localhost:7474/",
                                  "Running and accessible", verbose)
    details["neo4j_service"] = neo4j_running

    if not neo4j_running:
        all_checks_passed = False
        failed_checks.append("Neo4j database: Not running or accessible")
        if verbose:
            print("   💡 Start with: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")

    # 7. Check GraphRAG MCP imports
    if verbose:
        print("\n7️⃣ GraphRAG MCP Components:")

    import_status = _check_graphrag_imports(verbose)
    details["graphrag_imports"] = import_status

    if not import_status["success"]:
        all_checks_passed = False
        failed_checks.append(f"GraphRAG MCP imports: {import_status['error']}")

    # Final status
    if verbose:
        print("\n" + "=" * 50)
        if all_checks_passed:
            print("🎉 All Prerequisites Check: PASSED")
            print("✅ You're ready to process documents!")
        else:
            print("❌ Prerequisites Check: FAILED")
            print("🔧 Please fix the issues above before proceeding")
            print("\n🆘 Common Solutions:")
            print("   • Install missing packages: pip install plotly networkx pandas tqdm")
            print("   • Start Ollama: ollama serve")
            print("   • Start Neo4j: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
            print("   • Install models: ollama pull llama3.1:8b && ollama pull nomic-embed-text")

    return ValidationResult(
        status="passed" if all_checks_passed else "failed",
        issues=failed_checks,
        details=details
    )


def _check_service(name: str, url: str, description: str, verbose: bool = True) -> bool:
    """Check if a service is running"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-f", url],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            if verbose:
                print(f"   ✅ {name}: {description}")
            return True
        else:
            if verbose:
                print(f"   ❌ {name}: Not accessible at {url}")
            return False
    except subprocess.TimeoutExpired:
        if verbose:
            print(f"   ❌ {name}: Connection timeout")
        return False
    except Exception as e:
        if verbose:
            print(f"   ❌ {name}: Error - {str(e)}")
        return False


def _check_python_package(package_name: str, import_name: str = None, verbose: bool = True) -> bool:
    """Check if Python package is installed"""
    import_name = import_name or package_name
    try:
        importlib.import_module(import_name)
        if verbose:
            print(f"   ✅ {package_name}: Installed")
        return True
    except ImportError:
        if verbose:
            print(f"   ❌ {package_name}: Not installed")
        return False


def _check_ollama_models(verbose: bool = True) -> dict[str, Any]:
    """Check if required Ollama models are installed"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            models = result.stdout.lower()
            required_models = ["llama3.1:8b", "nomic-embed-text"]
            missing_models = []
            available_models = []

            for model in required_models:
                if model in models:
                    available_models.append(model)
                    if verbose:
                        print(f"   ✅ {model}: Available")
                else:
                    missing_models.append(model)
                    if verbose:
                        print(f"   ❌ {model}: Not found")

            return {
                "all_available": len(missing_models) == 0,
                "available": available_models,
                "missing": missing_models
            }
        else:
            if verbose:
                print("   ❌ Could not check Ollama models")
            return {
                "all_available": False,
                "available": [],
                "missing": ["llama3.1:8b", "nomic-embed-text"],
                "error": "Could not run ollama list"
            }
    except Exception as e:
        if verbose:
            print(f"   ❌ Error checking Ollama models: {e}")
        return {
            "all_available": False,
            "available": [],
            "missing": ["llama3.1:8b", "nomic-embed-text"],
            "error": str(e)
        }


def _check_project_structure(verbose: bool = True) -> bool:
    """Check if project structure is correct"""
    current_dir = Path.cwd()

    # Check for key files
    expected_files = [
        "../../examples",
        "../../graphrag_mcp/core",
        "../../graphrag_mcp/mcp"
    ]

    missing_files = []
    for file_path in expected_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        if verbose:
            print(f"   ❌ Missing files/folders: {missing_files}")
        return False
    else:
        if verbose:
            print("   ✅ Project structure: Correct")
        return True


def _check_graphrag_imports(verbose: bool = True) -> dict[str, Any]:
    """Check GraphRAG MCP imports"""
    try:
        # Add project root to path
        project_root = Path.cwd().parent.parent
        sys.path.insert(0, str(project_root))

        if verbose:
            print("   ✅ GraphRAG MCP core imports: Working")

        # Try optional Graphiti import
        try:
            from graphrag_mcp.core.graphiti_engine import GraphitiKnowledgeGraph
            if verbose:
                print("   ✅ GraphRAG MCP Graphiti: Working")
            return {
                "success": True,
                "graphiti_available": True
            }
        except ImportError:
            if verbose:
                print("   ⚠️  GraphRAG MCP Graphiti: Not available (proceeding without persistence)")
            return {
                "success": True,
                "graphiti_available": False
            }

    except Exception as e:
        if verbose:
            print(f"   ❌ GraphRAG MCP imports: Failed - {e}")
        return {
            "success": False,
            "error": str(e),
            "graphiti_available": False
        }


def validate_environment() -> ValidationResult:
    """
    Quick environment validation without verbose output
    
    Returns:
        ValidationResult with status
    """
    return check_prerequisites(verbose=False)


def get_system_info() -> dict[str, Any]:
    """
    Get system information for debugging
    
    Returns:
        Dictionary with system information
    """
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": sys.platform,
        "cwd": str(Path.cwd()),
        "path": sys.path[:5]  # First 5 path entries
    }

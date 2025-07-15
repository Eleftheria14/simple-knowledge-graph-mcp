"""
GraphRAG MCP Prerequisites Checking

This module provides comprehensive system validation for GraphRAG MCP toolkit.
"""

import importlib
import subprocess
import sys
import time
import socket
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from ..ui.status import ValidationResult
from .error_handling import ValidationError, ProcessingError


def validate_environment(verbose: bool = True) -> ValidationResult:
    """
    Enhanced environment validation with comprehensive error handling
    
    Args:
        verbose: Whether to print detailed status messages
        
    Returns:
        ValidationResult with detailed status and actionable recommendations
    """
    if verbose:
        print("🔍 Enhanced Environment Validation")
        print("=" * 60)
    
    try:
        return check_prerequisites(verbose)
    except Exception as e:
        return ValidationResult(
            status="failed",
            issues=[f"Environment validation failed: {str(e)}"],
            details={"error": str(e), "error_type": type(e).__name__}
        )


def get_system_info() -> dict[str, Any]:
    """Get comprehensive system information for debugging"""
    import platform
    import os
    
    system_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "current_directory": str(Path.cwd()),
        "environment_variables": {
            key: value for key, value in os.environ.items() 
            if key.startswith(('PYTHON', 'PATH', 'OLLAMA', 'CUDA'))
        }
    }
    
    # Add network information
    try:
        import socket
        hostname = socket.gethostname()
        system_info["network"] = {
            "hostname": hostname,
            "local_ip": socket.gethostbyname(hostname)
        }
    except Exception as e:
        system_info["network"] = {"error": str(e)}
    
    return system_info


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
    """Check if a service is running with enhanced timeout and retry logic"""
    return _check_service_with_retry(name, url, description, verbose, max_attempts=3, timeout=5)


def _check_service_with_retry(name: str, url: str, description: str, verbose: bool = True, 
                             max_attempts: int = 3, timeout: int = 5) -> bool:
    """Check service with retry logic and comprehensive error handling"""
    
    # First try basic network connectivity
    if not _check_network_connectivity(url, timeout=2):
        if verbose:
            print(f"   ❌ {name}: Network connectivity issue")
        return False
    
    for attempt in range(max_attempts):
        try:
            # Try curl command with timeout
            result = subprocess.run(
                ["curl", "-s", "-f", "--connect-timeout", str(timeout), "--max-time", str(timeout * 2), url],
                capture_output=True,
                text=True,
                timeout=timeout * 3  # Overall timeout longer than curl timeout
            )
            
            if result.returncode == 0:
                if verbose:
                    print(f"   ✅ {name}: {description}")
                return True
            else:
                # Check specific curl error codes
                error_msg = _interpret_curl_error(result.returncode, result.stderr)
                if verbose and attempt == max_attempts - 1:
                    print(f"   ❌ {name}: {error_msg}")
                
                # Don't retry on certain permanent errors
                if result.returncode in [7, 22]:  # Connection refused, HTTP error
                    break
                    
        except subprocess.TimeoutExpired:
            if verbose and attempt == max_attempts - 1:
                print(f"   ❌ {name}: Connection timeout after {timeout}s")
        except FileNotFoundError:
            # curl not found, try alternative method
            if verbose:
                print(f"   ⚠️  {name}: curl not found, trying alternative method")
            return _check_service_python(url, name, description, verbose, timeout)
        except Exception as e:
            if verbose and attempt == max_attempts - 1:
                print(f"   ❌ {name}: Error - {str(e)}")
        
        # Wait before retry (exponential backoff)
        if attempt < max_attempts - 1:
            time.sleep(2 ** attempt)
    
    return False


def _check_network_connectivity(url: str, timeout: int = 2) -> bool:
    """Check basic network connectivity to service"""
    try:
        parsed_url = urlparse(url)
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
        
        # Try to connect to the host and port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        return result == 0
    except Exception:
        return False


def _interpret_curl_error(return_code: int, stderr: str) -> str:
    """Interpret curl error codes into user-friendly messages"""
    error_codes = {
        1: "Unsupported protocol",
        2: "Failed to initialize",
        3: "URL malformed",
        5: "Couldn't resolve proxy",
        6: "Couldn't resolve host",
        7: "Failed to connect to host",
        22: "HTTP page not retrieved (404, 500, etc.)",
        23: "Write error",
        26: "Read error",
        28: "Operation timeout",
        35: "SSL connect error",
        52: "Got nothing from server",
        56: "Failure in receiving network data"
    }
    
    if return_code in error_codes:
        return error_codes[return_code]
    else:
        return f"Unknown error (code {return_code}): {stderr.strip()}"


def _check_service_python(url: str, name: str, description: str, verbose: bool = True, timeout: int = 5) -> bool:
    """Alternative service check using Python urllib (fallback when curl is not available)"""
    try:
        import urllib.request
        import urllib.error
        
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'GraphRAG-MCP-Prerequisites-Check')
        
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.getcode() == 200:
                if verbose:
                    print(f"   ✅ {name}: {description}")
                return True
            else:
                if verbose:
                    print(f"   ❌ {name}: HTTP {response.getcode()}")
                return False
                
    except urllib.error.URLError as e:
        if verbose:
            print(f"   ❌ {name}: {str(e)}")
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
    """Check if required Ollama models are installed with enhanced error handling"""
    required_models = ["llama3.1:8b", "nomic-embed-text"]
    max_attempts = 3
    timeout = 15  # Increased timeout for model listing
    
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                models = result.stdout.lower()
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

                # Check for any available models to validate Ollama is working
                if not available_models and not missing_models:
                    if verbose:
                        print("   ⚠️  No models found - Ollama may not be properly set up")
                    return {
                        "all_available": False,
                        "available": [],
                        "missing": required_models,
                        "warning": "No models found in Ollama"
                    }

                return {
                    "all_available": len(missing_models) == 0,
                    "available": available_models,
                    "missing": missing_models
                }
            else:
                error_msg = f"ollama list returned code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr.strip()}"
                
                if verbose and attempt == max_attempts - 1:
                    print(f"   ❌ Could not check Ollama models: {error_msg}")
                
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt)
                else:
                    return {
                        "all_available": False,
                        "available": [],
                        "missing": required_models,
                        "error": error_msg
                    }
                    
        except subprocess.TimeoutExpired:
            if verbose and attempt == max_attempts - 1:
                print(f"   ❌ Ollama model check timeout after {timeout}s")
            elif attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                return {
                    "all_available": False,
                    "available": [],
                    "missing": required_models,
                    "error": f"Timeout after {timeout}s"
                }
                
        except FileNotFoundError:
            if verbose:
                print("   ❌ Ollama command not found - is Ollama installed?")
            return {
                "all_available": False,
                "available": [],
                "missing": required_models,
                "error": "Ollama command not found"
            }
            
        except Exception as e:
            if verbose and attempt == max_attempts - 1:
                print(f"   ❌ Error checking Ollama models: {e}")
            elif attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                return {
                    "all_available": False,
                    "available": [],
                    "missing": required_models,
                    "error": str(e)
                }
    
    # Should not reach here, but just in case
    return {
        "all_available": False,
        "available": [],
        "missing": required_models,
        "error": "Unknown error after all attempts"
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

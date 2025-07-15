"""
GraphRAG MCP File Discovery

This module provides utilities for discovering and validating documents.
"""

from pathlib import Path

from ..ui.status import DocumentInfo


class DocumentDiscovery:
    """Document discovery and validation utilities"""

    def __init__(self, supported_extensions: list[str] = None):
        self.supported_extensions = supported_extensions or ['.pdf']

    def discover_documents(self, folder_path: str, recursive: bool = True) -> list[DocumentInfo]:
        """
        Discover documents in a folder
        
        Args:
            folder_path: Path to search for documents
            recursive: Whether to search recursively
            
        Returns:
            List of DocumentInfo objects
        """
        documents = []
        folder = Path(folder_path)

        if not folder.exists():
            print(f"❌ Folder not found: {folder_path}")
            return documents

        print(f"🔍 Scanning: {folder_path}")

        # Choose search method based on recursive flag
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in folder.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    doc_info = DocumentInfo(
                        path=file_path,
                        name=file_path.name,
                        size_mb=round(size_mb, 2)
                    )
                    documents.append(doc_info)
                    print(f"   📄 {file_path.name} ({size_mb:.2f} MB)")
                except Exception as e:
                    print(f"   ⚠️  Error reading {file_path.name}: {e}")

        total_size = sum(doc.size_mb for doc in documents)
        print(f"📊 Found {len(documents)} documents ({total_size:.2f} MB total)")
        return documents

    def validate_document(self, file_path: Path) -> bool:
        """
        Validate a single document
        
        Args:
            file_path: Path to document
            
        Returns:
            True if valid, False otherwise
        """
        if not file_path.exists():
            return False

        if not file_path.is_file():
            return False

        if file_path.suffix.lower() not in self.supported_extensions:
            return False

        # Check file size (avoid empty files)
        if file_path.stat().st_size == 0:
            return False

        return True

    def get_document_info(self, file_path: Path) -> DocumentInfo | None:
        """
        Get information about a single document
        
        Args:
            file_path: Path to document
            
        Returns:
            DocumentInfo if valid, None otherwise
        """
        if not self.validate_document(file_path):
            return None

        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            return DocumentInfo(
                path=file_path,
                name=file_path.name,
                size_mb=round(size_mb, 2)
            )
        except Exception:
            return None


def discover_documents(folder_path: str, recursive: bool = True) -> list[DocumentInfo]:
    """
    Convenience function to discover documents
    
    Args:
        folder_path: Path to search for documents
        recursive: Whether to search recursively
        
    Returns:
        List of DocumentInfo objects
    """
    discovery = DocumentDiscovery()
    return discovery.discover_documents(folder_path, recursive)

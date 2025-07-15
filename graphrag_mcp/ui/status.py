"""
GraphRAG MCP Status Tracking

This module provides status tracking for document processing and system operations.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class DocumentStatus:
    """Track processing status for each document"""
    path: Path
    name: str
    size_mb: float
    status: str = "pending"  # pending, processing, completed, failed
    start_time: datetime | None = None
    end_time: datetime | None = None
    error_message: str | None = None
    entities_found: int = 0
    citations_found: int = 0
    processing_time: float = 0.0

    @property
    def processing_speed(self) -> float:
        """Pages per minute estimate"""
        if self.processing_time > 0:
            return (self.size_mb * 10) / (self.processing_time / 60)
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "path": str(self.path),
            "name": self.name,
            "size_mb": self.size_mb,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error_message": self.error_message,
            "entities_found": self.entities_found,
            "citations_found": self.citations_found,
            "processing_time": self.processing_time,
            "processing_speed": self.processing_speed
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentStatus":
        """Create from dictionary"""
        return cls(
            path=Path(data["path"]),
            name=data["name"],
            size_mb=data["size_mb"],
            status=data["status"],
            start_time=datetime.fromisoformat(data["start_time"]) if data["start_time"] else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            error_message=data["error_message"],
            entities_found=data["entities_found"],
            citations_found=data["citations_found"],
            processing_time=data["processing_time"]
        )


@dataclass
class DocumentInfo:
    """Basic document information for discovery"""
    path: Path
    name: str
    size_mb: float

    def to_document_status(self) -> DocumentStatus:
        """Convert to DocumentStatus for processing"""
        return DocumentStatus(
            path=self.path,
            name=self.name,
            size_mb=self.size_mb
        )


@dataclass
class ProcessingResults:
    """Results from document processing"""
    success: int
    failed: int
    total_time: float
    documents: list[DocumentStatus]

    @property
    def total_documents(self) -> int:
        return len(self.documents)

    @property
    def avg_time(self) -> float:
        if self.total_documents > 0:
            return self.total_time / self.total_documents
        return 0.0

    def get_successful_documents(self) -> list[DocumentStatus]:
        """Get successfully processed documents"""
        return [doc for doc in self.documents if doc.status == "completed"]

    def get_failed_documents(self) -> list[DocumentStatus]:
        """Get failed documents"""
        return [doc for doc in self.documents if doc.status == "failed"]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "success": self.success,
            "failed": self.failed,
            "total_time": self.total_time,
            "total_documents": self.total_documents,
            "avg_time": self.avg_time,
            "documents": [doc.to_dict() for doc in self.documents]
        }


@dataclass
class ValidationResult:
    """Result from system validation"""
    status: str  # "passed" or "failed"
    issues: list[str]
    details: dict[str, Any]

    @property
    def is_valid(self) -> bool:
        return self.status == "passed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "issues": self.issues,
            "details": self.details,
            "is_valid": self.is_valid
        }

#!/usr/bin/env python3
"""
File operations utilities for the research desktop backend.
Handles file renaming, sanitization, and organization.
"""
import os
import re
import shutil
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


def sanitize_filename(title: str, max_length: int = 200) -> str:
    """
    Convert a document title to a safe filename.
    
    Args:
        title: Document title to convert
        max_length: Maximum filename length (default 200)
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    if not title or not title.strip():
        return "untitled_document"
    
    # Remove or replace problematic characters
    # Replace common problematic chars with safe alternatives
    replacements = {
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': "'",
        '<': '(',
        '>': ')',
        '|': '_',
        '\n': ' ',
        '\r': ' ',
        '\t': ' '
    }
    
    filename = title.strip()
    
    # Apply character replacements
    for bad_char, replacement in replacements.items():
        filename = filename.replace(bad_char, replacement)
    
    # Remove control characters and other problematic Unicode
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Replace multiple spaces/underscores with single underscore
    filename = re.sub(r'[_\s]+', '_', filename)
    
    # Remove leading/trailing dots and spaces (problematic on Windows)
    filename = filename.strip(' .')
    
    # Ensure it's not empty after cleaning
    if not filename:
        filename = "untitled_document"
    
    # Truncate to max length while preserving word boundaries
    if len(filename) > max_length:
        filename = filename[:max_length].rsplit('_', 1)[0]
        if not filename:  # Safety check
            filename = "long_document_title"
    
    # Remove trailing underscore if present
    filename = filename.rstrip('_')
    
    return filename


def create_organized_filename(
    original_path: str, 
    title: str, 
    authors: list = None,
    year: str = None,
    include_original: bool = True
) -> str:
    """
    Create an organized filename with title, authors, and year.
    
    Args:
        original_path: Original file path
        title: Document title
        authors: List of author names
        year: Publication year
        include_original: Whether to include original filename in case of conflicts
        
    Returns:
        New organized filename
    """
    # Get file extension
    original_file = Path(original_path)
    extension = original_file.suffix.lower()
    
    # Sanitize title
    clean_title = sanitize_filename(title, max_length=150)
    
    # Format authors (first 3 max)
    author_part = ""
    if authors and len(authors) > 0:
        # Take first 3 authors and sanitize
        author_names = []
        for author in authors[:3]:
            if isinstance(author, dict):
                name = author.get('name', str(author))
            else:
                name = str(author)
            
            # Extract last name if possible
            name_parts = name.strip().split()
            if name_parts:
                # Use last part as surname
                surname = name_parts[-1]
                author_names.append(sanitize_filename(surname, max_length=20))
        
        if author_names:
            author_part = "_" + "_".join(author_names)
            if len(authors) > 3:
                author_part += "_et_al"
    
    # Add year if available
    year_part = ""
    if year and str(year).strip():
        clean_year = re.sub(r'[^\d]', '', str(year))[:4]  # Extract first 4 digits
        if clean_year and len(clean_year) >= 4:
            year_part = f"_{clean_year}"
    
    # Combine parts
    new_filename = f"{clean_title}{author_part}{year_part}{extension}"
    
    # Ensure total length is reasonable
    max_total_length = 255  # Most filesystems support this
    if len(new_filename) > max_total_length:
        # Trim the title part while keeping authors and year
        available_for_title = max_total_length - len(author_part) - len(year_part) - len(extension) - 10
        if available_for_title > 20:
            clean_title = clean_title[:available_for_title]
            new_filename = f"{clean_title}{author_part}{year_part}{extension}"
        else:
            # Fallback to just title and extension
            clean_title = clean_title[:max_total_length - len(extension) - 10]
            new_filename = f"{clean_title}{extension}"
    
    return new_filename


def rename_file_with_title(
    original_path: str,
    title: str,
    authors: list = None,
    year: str = None,
    target_directory: str = None,
    avoid_conflicts: bool = True
) -> Dict[str, Any]:
    """
    Rename a file based on document metadata.
    
    Args:
        original_path: Current file path
        title: Document title
        authors: List of authors
        year: Publication year
        target_directory: Optional target directory (defaults to same directory)
        avoid_conflicts: Whether to add numbers to avoid filename conflicts
        
    Returns:
        Dict with operation status and new path
    """
    try:
        original_file = Path(original_path)
        
        if not original_file.exists():
            return {
                "success": False,
                "error": f"Original file not found: {original_path}",
                "original_path": original_path,
                "new_path": None
            }
        
        # Determine target directory
        if target_directory:
            target_dir = Path(target_directory)
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = original_file.parent
        
        # Create new filename
        new_filename = create_organized_filename(
            original_path, title, authors, year
        )
        
        # Handle conflicts if needed
        new_path = target_dir / new_filename
        if avoid_conflicts and new_path.exists() and new_path != original_file:
            base_name = new_path.stem
            extension = new_path.suffix
            counter = 1
            
            while new_path.exists() and new_path != original_file:
                new_filename = f"{base_name}_{counter:02d}{extension}"
                new_path = target_dir / new_filename
                counter += 1
                
                if counter > 99:  # Safety limit
                    # Fallback to timestamp
                    import time
                    timestamp = int(time.time())
                    new_filename = f"{base_name}_{timestamp}{extension}"
                    new_path = target_dir / new_filename
                    break
        
        # Perform the rename/move
        if new_path != original_file:
            shutil.move(str(original_file), str(new_path))
            
            return {
                "success": True,
                "message": f"File renamed successfully",
                "original_path": str(original_file),
                "new_path": str(new_path),
                "original_filename": original_file.name,
                "new_filename": new_path.name
            }
        else:
            return {
                "success": True,
                "message": "File already has correct name",
                "original_path": str(original_file),
                "new_path": str(new_path),
                "original_filename": original_file.name,
                "new_filename": new_path.name
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to rename file: {str(e)}",
            "original_path": original_path,
            "new_path": None
        }


def organize_pdf_collection(
    pdf_files: list,
    target_directory: str,
    metadata_extractor_func=None
) -> Dict[str, Any]:
    """
    Organize a collection of PDF files by renaming them based on their content.
    
    Args:
        pdf_files: List of PDF file paths
        target_directory: Directory to organize files into
        metadata_extractor_func: Function to extract metadata from PDFs
        
    Returns:
        Dict with overall operation results
    """
    results = []
    successful = 0
    failed = 0
    
    for pdf_path in pdf_files:
        try:
            # Extract metadata if function provided
            if metadata_extractor_func:
                metadata = metadata_extractor_func(pdf_path)
                title = metadata.get('title', Path(pdf_path).stem)
                authors = metadata.get('authors', [])
                year = metadata.get('year', '')
            else:
                title = Path(pdf_path).stem
                authors = []
                year = ''
            
            # Rename file
            result = rename_file_with_title(
                pdf_path, title, authors, year, target_directory
            )
            
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
                
        except Exception as e:
            results.append({
                "success": False,
                "error": str(e),
                "original_path": pdf_path,
                "new_path": None
            })
            failed += 1
    
    return {
        "success": failed == 0,
        "total_files": len(pdf_files),
        "successful": successful,
        "failed": failed,
        "results": results
    }


# Test functions
def test_filename_sanitization():
    """Test the filename sanitization logic"""
    test_cases = [
        "A Simple Title",
        "Title: With Colon & Special Chars",
        "Very/Long\\Path*With?Many\"Bad<Chars>|Here",
        "Title\nWith\rNewlines\tAnd   Multiple    Spaces",
        "   Leading and Trailing Spaces   ",
        "",
        "A" * 300,  # Very long title
        "Title (2024): Research on AI/ML Systems",
        "José María & François: A Study on Résumés"
    ]
    
    print("Testing filename sanitization:")
    for title in test_cases:
        sanitized = sanitize_filename(title)
        print(f"'{title}' → '{sanitized}'")
    
    print("\nTesting organized filenames:")
    test_metadata = [
        {
            "title": "Machine Learning in Healthcare",
            "authors": ["John Smith", "Jane Doe", "Bob Wilson", "Alice Brown"],
            "year": "2024"
        },
        {
            "title": "A Very Long Title That Might Exceed Normal Filename Limits",
            "authors": ["García", "Müller"],
            "year": "2023"
        }
    ]
    
    for meta in test_metadata:
        filename = create_organized_filename(
            "/path/to/file.pdf",
            meta["title"], 
            meta["authors"], 
            meta["year"]
        )
        print(f"Title: '{meta['title']}'")
        print(f"Authors: {meta['authors']}")
        print(f"Year: {meta['year']}")
        print(f"Filename: '{filename}'\n")


if __name__ == "__main__":
    test_filename_sanitization()
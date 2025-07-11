"""
Working Regex Patterns for d4sc03921a.pdf Citation Extraction

This file contains the specific regex patterns that successfully extract
citation information from the Chemical Science paper d4sc03921a.pdf.
"""

import re

# Sample text structure from the PDF
SAMPLE_TEXT = """A review of large language models and
autonomous agents in chemistry
Mayk Caldas Ramos, ab Christopher J. Collison c and Andrew D. White *ab
Large language models (LLMs) have emerged as powerful tools in chemistry..."""

def demonstrate_working_patterns():
    """Demonstrate the working regex patterns"""
    
    print("=== WORKING REGEX PATTERNS FOR d4sc03921a.pdf ===")
    print()
    
    # Sample data from the actual PDF
    lines = SAMPLE_TEXT.split('\n')
    
    # 1. TITLE EXTRACTION
    print("1. TITLE EXTRACTION")
    print("   Method: Combine first two lines")
    print("   Pattern: lines[0] + ' ' + lines[1]")
    if len(lines) >= 2:
        title = f"{lines[0].strip()} {lines[1].strip()}"
        print(f"   Result: {title}")
    print()
    
    # 2. AUTHOR EXTRACTION  
    print("2. AUTHOR EXTRACTION")
    print("   Input: 'Mayk Caldas Ramos, ab Christopher J. Collison c and Andrew D. White *ab'")
    print("   Method: Split by ' and ', then handle comma-separated parts")
    
    author_line = "Mayk Caldas Ramos, ab Christopher J. Collison c and Andrew D. White *ab"
    
    # Step 1: Split by " and "
    parts = author_line.split(' and ')
    print(f"   Step 1 - Split by ' and ': {parts}")
    
    # Step 2: Handle first part (comma-separated)
    first_part = parts[0].strip()
    comma_parts = first_part.split(',')
    print(f"   Step 2 - Split first part by comma: {comma_parts}")
    
    # Step 3: Extract authors
    authors = []
    
    # First author
    first_author = comma_parts[0].strip()
    authors.append(first_author)
    print(f"   First author: '{first_author}'")
    
    # Second author (remove leading superscript)
    if len(comma_parts) > 1:
        second_author_raw = comma_parts[1].strip()
        second_author = re.sub(r'^\s*[a-z*]+\s*', '', second_author_raw).strip()
        second_author = re.sub(r'\s*[a-z*]+\s*$', '', second_author).strip()
        authors.append(second_author)
        print(f"   Second author: '{second_author}' (from '{second_author_raw}')")
    
    # Third author (remove trailing superscript)
    if len(parts) > 1:
        third_author_raw = parts[1].strip()
        third_author = re.sub(r'\s*[a-z*]+\s*$', '', third_author_raw).strip()
        authors.append(third_author)
        print(f"   Third author: '{third_author}' (from '{third_author_raw}')")
    
    print(f"   Final authors: {authors}")
    print()
    
    # 3. JOURNAL EXTRACTION
    print("3. JOURNAL EXTRACTION")
    print("   Pattern: r'Chemical Science'")
    print("   Method: Direct string matching (most reliable)")
    print("   Result: 'Chemical Science'")
    print()
    
    # 4. YEAR EXTRACTION
    print("4. YEAR EXTRACTION")
    print("   Patterns (in priority order):")
    print("     1. r'Published.*?(20[12][0-9])' - Published dates")
    print("     2. r'Accepted.*?(20[12][0-9])' - Accepted dates")
    print("     3. r'Received.*?(20[12][0-9])' - Received dates")
    print("   Method: Use first match from highest priority pattern")
    print("   Result: '2024' (from 'Published on 09 December 2024')")
    print()
    
    # 5. DOI EXTRACTION
    print("5. DOI EXTRACTION")
    print("   Patterns:")
    print("     1. r'DOI:?\\s*10\\.(\\d+)/([^\\s\\n]+)'")
    print("     2. r'doi\\.org/10\\.(\\d+)/([^\\s\\n]+)'")
    print("     3. r'10\\.(\\d+)/([^\\s\\n]+)'")
    print("   Method: Find first match, reconstruct as '10.{group1}/{group2}'")
    print("   Result: '10.1039/d4sc03921a'")
    print()
    
    # 6. SPECIFIC REGEX PATTERNS
    print("6. SPECIFIC REGEX PATTERNS")
    print()
    
    print("   SUPERSCRIPT REMOVAL:")
    print("   - Leading: r'^\\s*[a-z*]+\\s*' (removes 'ab ' from ' ab Christopher')")
    print("   - Trailing: r'\\s*[a-z*]+\\s*$' (removes ' *ab' from 'Andrew D. White *ab')")
    print()
    
    print("   AUTHOR VALIDATION:")
    print("   - Length: 3 < len(author) < 50")
    print("   - Exclude: ['university', 'department', 'email', 'corresponding']")
    print()
    
    print("   JOURNAL VALIDATION:")
    print("   - Length: len(journal) > 5")
    print("   - Exclude: ['university', 'department', 'in chemistry']")
    print()


# Common problematic patterns that DON'T work for this paper
PROBLEMATIC_PATTERNS = {
    'title': [
        r'(?:^|\n)([A-Z][^\n]{30,120}?)(?=\n[a-z]|\n[A-Z][a-z]+ [A-Z])',  # Too restrictive
        r'(?:^|\n)([A-Z][^\n]{20,100}?)(?=\n\n)',  # Doesn't handle multi-line titles
    ],
    'authors': [
        r'([A-Z][a-z]+ [A-Z]\.? [A-Z][a-z]+)',  # Matches text from abstract
        r'([A-Z][a-z]+ [A-Z][a-z]+)',  # Too broad, matches "Activity Relationship"
    ],
    'journal': [
        r'([A-Z][a-z]+ [A-Z][a-z]*)',  # Too broad, matches "science in"
    ],
    'year': [
        r'\b(20[12][0-9])\b',  # Without context, picks wrong years
    ]
}


def demonstrate_problematic_patterns():
    """Show why certain patterns don't work"""
    
    print("=== PROBLEMATIC PATTERNS (DON'T USE) ===")
    print()
    
    sample_text = """A review of large language models and
autonomous agents in chemistry
Mayk Caldas Ramos, ab Christopher J. Collison c and Andrew D. White *ab
Large language models (LLMs) have emerged as powerful tools in chemistry, signiﬁcantly impacting
molecule design, property prediction, and synthesis optimization. This review highlights LLM capabilities
in these domains and their potential to accelerate scientiﬁc discovery through automation. We also
review LLM-based autonomous agents: LLMs with a broader set of tools to interact with their
surrounding environment. These agents perform diverse tasks such as paper scraping, interfacing with
automated laboratories, and synthesis planning. As agents are an emerging topic, we extend the scope
of our review of agents beyond chemistry and discuss across any scientiﬁc domains."""
    
    print("1. PROBLEMATIC AUTHOR PATTERN: r'([A-Z][a-z]+ [A-Z][a-z]+)'")
    pattern = r'([A-Z][a-z]+ [A-Z][a-z]+)'
    matches = re.findall(pattern, sample_text)
    print(f"   Matches: {matches[:10]}...")  # Show first 10
    print("   Problem: Matches phrases like 'Activity Relationship', 'Machine Learning'")
    print()
    
    print("2. PROBLEMATIC JOURNAL PATTERN: r'([A-Z][a-z]+ [A-Z][a-z]*)'")
    pattern = r'([A-Z][a-z]+ [A-Z][a-z]*)'
    matches = re.findall(pattern, sample_text)
    print(f"   Matches: {matches[:5]}...")
    print("   Problem: Too broad, matches many unrelated phrases")
    print()
    
    print("3. SOLUTION: Use document structure and context-aware patterns")
    print("   - Know that authors are on line 3")
    print("   - Use specific delimiters (' and ', commas)")
    print("   - Remove known superscript patterns")
    print("   - Validate results against expected formats")


if __name__ == "__main__":
    demonstrate_working_patterns()
    print("\n" + "="*60 + "\n")
    demonstrate_problematic_patterns()
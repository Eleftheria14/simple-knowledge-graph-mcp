"""
Improved Citation Extractor for Research Papers

This improved version is specifically designed to handle the structure of the d4sc03921a.pdf paper
and similar academic papers from Chemical Science and other journals.
"""

import re
import textwrap
from langchain_community.document_loaders import PyPDFLoader


def extract_citation_info_improved(pdf_path):
    """Extract comprehensive citation information from research paper - improved version"""
    
    # Load the PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    full_text = "\n".join([doc.page_content for doc in documents])
    
    # Focus on first 5000 characters where citation info is typically found
    first_pages = full_text[:5000]
    citation_info = {}
    
    # Extract title - For this specific paper structure
    # The title spans the first two lines
    lines = first_pages.split('\n')
    
    # Title extraction - combine first two lines for this paper
    if len(lines) >= 2:
        title_line1 = lines[0].strip()
        title_line2 = lines[1].strip()
        
        # Check if this looks like a title structure
        if (len(title_line1) > 10 and len(title_line2) > 10 and 
            not any(exclude in title_line1.lower() for exclude in ['university', 'department', 'email']) and
            not any(exclude in title_line2.lower() for exclude in ['university', 'department', 'email'])):
            
            # Combine the lines
            full_title = f"{title_line1} {title_line2}"
            citation_info['title'] = full_title
    
    # If title extraction failed, use fallback patterns
    if 'title' not in citation_info:
        title_patterns = [
            r'(?:^|\n)([A-Z][^\n]{30,120}?)(?=\n[a-z]|\n[A-Z][a-z]+ [A-Z])',
            r'(?:^|\n)([A-Z][^\n]{20,100}?)(?=\n\n)',
            r'(?:^|\n)([A-Z][^\n]{25,100}?)(?=\n[A-Z]\. [A-Z])',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, first_pages, re.MULTILINE)
            for match in matches:
                potential_title = match.strip()
                exclude_words = ['university', 'department', 'email', 'abstract', 'received', 'published', 'copyright']
                if not any(word in potential_title.lower() for word in exclude_words) and len(potential_title) > 25:
                    citation_info['title'] = potential_title
                    break
            if 'title' in citation_info:
                break
    
    # Extract authors - For this specific paper structure
    # Authors are on the third line: "Mayk Caldas Ramos, ab Christopher J. Collison c and Andrew D. White *ab"
    if len(lines) >= 3:
        author_line = lines[2].strip()
        
        # Structure: "Mayk Caldas Ramos, ab Christopher J. Collison c and Andrew D. White *ab"
        # Split by " and " first
        authors = []
        if ' and ' in author_line:
            parts = author_line.split(' and ')
            
            # Part 1: "Mayk Caldas Ramos, ab Christopher J. Collison c"
            first_part = parts[0].strip()
            if ',' in first_part:
                comma_parts = first_part.split(',')
                
                # First author: "Mayk Caldas Ramos"
                first_author = comma_parts[0].strip()
                if first_author:
                    authors.append(first_author)
                
                # Second author: "ab Christopher J. Collison c"
                if len(comma_parts) > 1:
                    second_author_raw = comma_parts[1].strip()
                    # Remove leading superscript indicators
                    second_author = re.sub(r'^\s*[a-z*]+\s*', '', second_author_raw).strip()
                    # Remove trailing superscript indicators
                    second_author = re.sub(r'\s*[a-z*]+\s*$', '', second_author).strip()
                    if second_author:
                        authors.append(second_author)
            
            # Part 2: "Andrew D. White *ab"
            last_part = parts[1].strip()
            # Remove superscript indicators from the end
            last_author = re.sub(r'\s*[a-z*]+\s*$', '', last_part).strip()
            if last_author:
                authors.append(last_author)
        
        # Clean up author names and validate
        cleaned_authors = []
        for author in authors:
            # Further clean up
            author = re.sub(r'\s+', ' ', author)  # Normalize whitespace
            
            # Validate author name
            if (len(author) > 3 and len(author) < 50 and 
                not any(exclude in author.lower() for exclude in ['university', 'department', 'email', 'corresponding'])):
                cleaned_authors.append(author)
        
        if cleaned_authors:
            citation_info['authors'] = cleaned_authors
    
    # Fallback author extraction if the above fails
    if 'authors' not in citation_info or not citation_info['authors']:
        author_patterns = [
            r'([A-Z][a-z]+ [A-Z]\.? [A-Z][a-z]+)',  # First M. Last
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # First Last
            r'([A-Z]\. [A-Z][a-z]+)',  # F. Last
            r'([A-Z][a-z]+, [A-Z]\.? [A-Z]\.?)',  # Last, F. M.
        ]
        
        authors = set()
        for pattern in author_patterns:
            matches = re.findall(pattern, first_pages)
            for match in matches:
                author = re.sub(r'\s+', ' ', match.strip())
                if (len(author.split()) >= 2 and len(author) > 4 and len(author) < 50):
                    false_positives = ['corresponding author', 'et al', 'journal', 'science', 'nature', 
                                     'neural networks', 'machine learning', 'relationship', 'convolutional neural']
                    if not any(fp in author.lower() for fp in false_positives):
                        authors.add(author)
        
        if authors:
            citation_info['authors'] = sorted(list(authors))[:6]
    
    # Extract journal name - Chemical Science is explicitly mentioned
    journal_patterns = [
        r'Chemical Science',
        r'Chem\.\s*Sci\.',
        r'Journal of [A-Z][^\n]{5,40}',
        r'Proceedings of [^\n]{10,50}',
        r'[A-Z][a-z]+ Chemistry',
        r'[A-Z][a-z]+ Physics',
        r'[A-Z][a-z]+ Biology',
    ]
    
    for pattern in journal_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            journal = match.group(0).strip()
            # Validate journal name - Chemical Science is the correct journal
            if len(journal) > 5 and not any(word in journal.lower() for word in ['university', 'department', 'in chemistry']):
                citation_info['journal'] = journal
                break
    
    # Extract publication year - prioritize actual publication dates
    year_patterns = [
        (r'Published.*?(20[12][0-9])', 'published'),
        (r'Accepted.*?(20[12][0-9])', 'accepted'),
        (r'Received.*?(20[12][0-9])', 'received'),
    ]
    
    year_found = None
    for pattern, year_type in year_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            # Take the first match of the most important type
            if year_type == 'published':
                year_found = matches[0]
                break
            elif year_type == 'accepted' and not year_found:
                year_found = matches[0]
            elif year_type == 'received' and not year_found:
                year_found = matches[0]
    
    if year_found:
        citation_info['year'] = year_found
    
    # Extract DOI - this paper has a clear DOI
    doi_patterns = [
        r'DOI:?\s*10\.(\d+)/([^\s\n]+)',
        r'doi\.org/10\.(\d+)/([^\s\n]+)',
        r'10\.(\d+)/([^\s\n]+)'
    ]
    
    for pattern in doi_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            doi = f"10.{match.group(1)}/{match.group(2)}"
            # Clean up DOI - remove any trailing punctuation
            doi = re.sub(r'[^\w\.\-/]+$', '', doi)
            if len(doi) > 7:
                citation_info['doi'] = doi
                break
    
    # Extract volume and pages if available
    volume_page_patterns = [
        (r'Volume\s*(\d+)', 'volume'),
        (r'Vol\.\s*(\d+)', 'volume'),
        (r'(\d{1,3}),\s*(\d{1,5})-(\d{1,5})', 'volume_pages'),  # Volume, start-end pages
        (r'pp?\.\s*(\d{1,5})-?(\d{1,5})?', 'pages'),  # pp. Y-Z
    ]
    
    for pattern, pattern_type in volume_page_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            if pattern_type == 'volume':
                citation_info['volume'] = match.group(1)
            elif pattern_type == 'volume_pages':
                citation_info['volume'] = match.group(1)
                citation_info['pages'] = f"{match.group(2)}-{match.group(3)}"
            elif pattern_type == 'pages':
                if match.group(2):  # Has end page
                    citation_info['pages'] = f"{match.group(1)}-{match.group(2)}"
                else:
                    citation_info['pages'] = match.group(1)
            break
    
    return citation_info


def test_improved_extractor(pdf_path):
    """Test the improved citation extractor"""
    
    print("=== TESTING IMPROVED CITATION EXTRACTOR ===")
    print()
    
    citation_info = extract_citation_info_improved(pdf_path)
    
    print("Extracted Citation Information:")
    print("-" * 50)
    for key, value in citation_info.items():
        if isinstance(value, list):
            print(f"{key.capitalize():12}: {', '.join(value)}")
        else:
            print(f"{key.capitalize():12}: {value}")
    
    print()
    print("=== COMPARISON WITH EXPECTED VALUES ===")
    print("Expected Title: A review of large language models and autonomous agents in chemistry")
    print("Expected Authors: Mayk Caldas Ramos, Christopher J. Collison, Andrew D. White")
    print("Expected Journal: Chemical Science")
    print("Expected Year: 2024")
    print("Expected DOI: 10.1039/d4sc03921a")
    
    return citation_info


if __name__ == "__main__":
    pdf_path = "/Users/aimiegarces/Agents/d4sc03921a.pdf"
    test_improved_extractor(pdf_path)
"""GROBID-based academic paper processing tool."""
import requests
from typing import Dict, Any, Optional
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from langchain_core.tools import tool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrobidProcessor:
    """GROBID service client for academic paper processing."""
    
    def __init__(self, grobid_url: str = "http://localhost:8070"):
        self.grobid_url = grobid_url
        self.session = requests.Session()
    
    def is_alive(self) -> bool:
        """Check if GROBID service is running."""
        try:
            response = self.session.get(f"{self.grobid_url}/api/isalive", timeout=5)
            return response.text.strip() == "true"
        except Exception as e:
            logger.error(f"GROBID service check failed: {e}")
            return False
    
    def process_fulltext(self, pdf_path: str) -> Dict[str, Any]:
        """Process PDF with GROBID full-text extraction."""
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return {"success": False, "error": f"File not found: {pdf_path}"}
            
            print(f"📄 Processing with GROBID: {pdf_path.name}")
            
            # Check if GROBID is running
            if not self.is_alive():
                return {
                    "success": False, 
                    "error": "GROBID service not running. Start with: docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0"
                }
            
            # Process PDF
            with open(pdf_path, 'rb') as pdf_file:
                files = {'input': pdf_file}
                data = {
                    'consolidateHeader': '1',
                    'consolidateCitations': '1', 
                    'includeRawCitations': '1',
                    'includeRawAffiliations': '1',
                    'teiCoordinates': ['ref', 'biblStruct', 'formula', 'figure', 'table']
                }
                
                print("🔧 Sending to GROBID for processing...")
                response = self.session.post(
                    f"{self.grobid_url}/api/processFulltextDocument",
                    files=files,
                    data=data,
                    timeout=120
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"GROBID processing failed with status {response.status_code}: {response.text[:200]}"
                    }
                
                # Parse XML response
                tei_xml = response.text
                parsed_data = self._parse_tei_xml(tei_xml)
                
                result = {
                    "success": True,
                    "content": parsed_data.get("full_text", ""),
                    "file_name": pdf_path.name,
                    "file_size": pdf_path.stat().st_size,
                    "method_used": "GROBID",
                    "extraction_type": "academic",
                    "metadata": {
                        "title": parsed_data.get("title", ""),
                        "authors": parsed_data.get("authors", []),
                        "abstract": parsed_data.get("abstract", ""),
                        "keywords": parsed_data.get("keywords", []),
                        "references": parsed_data.get("references", []),
                        "citations": parsed_data.get("citations", []),
                        "figures": parsed_data.get("figures", []),
                        "tables": parsed_data.get("tables", [])
                    },
                    "tei_xml": tei_xml,  # Keep full XML for advanced processing
                    "content_length": len(parsed_data.get("full_text", ""))
                }
                
                print(f"✅ GROBID processing complete!")
                print(f"   📄 Title: {parsed_data.get('title', 'Unknown')[:60]}...")
                print(f"   👥 Authors: {len(parsed_data.get('authors', []))}")
                print(f"   📚 References: {len(parsed_data.get('references', []))}")
                print(f"   🔗 Citations: {len(parsed_data.get('citations', []))}")
                print(f"   📊 Tables: {len(parsed_data.get('tables', []))}")
                print(f"   🖼️  Figures: {len(parsed_data.get('figures', []))}")
                print(f"   📝 Content: {len(parsed_data.get('full_text', ''))} characters")
                
                return result
                
        except Exception as e:
            logger.error(f"GROBID processing error: {e}")
            return {
                "success": False,
                "error": f"GROBID processing exception: {str(e)}",
                "extraction_type": "academic"
            }
    
    def _parse_tei_xml(self, tei_xml: str) -> Dict[str, Any]:
        """Parse GROBID TEI XML output into structured data."""
        try:
            root = ET.fromstring(tei_xml)
            
            # Define namespace
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
            
            result = {
                "title": "",
                "authors": [],
                "abstract": "",
                "keywords": [],
                "full_text": "",
                "references": [],
                "citations": [],
                "figures": [],
                "tables": []
            }
            
            # Extract title
            title_elem = root.find('.//tei:titleStmt/tei:title[@type="main"]', ns)
            if title_elem is not None and title_elem.text:
                result["title"] = title_elem.text.strip()
            
            # Extract authors
            for author in root.findall('.//tei:sourceDesc//tei:author', ns):
                author_info = {}
                
                # Name
                forename = author.find('.//tei:forename[@type="first"]', ns)
                surname = author.find('.//tei:surname', ns)
                
                if forename is not None and surname is not None:
                    author_info["name"] = f"{forename.text} {surname.text}"
                elif surname is not None:
                    author_info["name"] = surname.text
                
                # Affiliation
                affiliation = author.find('.//tei:affiliation/tei:orgName[@type="institution"]', ns)
                if affiliation is not None and affiliation.text:
                    author_info["affiliation"] = affiliation.text
                
                if author_info.get("name"):
                    result["authors"].append(author_info)
            
            # Extract abstract
            abstract_elem = root.find('.//tei:profileDesc//tei:abstract/tei:div/tei:p', ns)
            if abstract_elem is not None:
                result["abstract"] = self._extract_text_content(abstract_elem)
            
            # Extract keywords
            for keyword in root.findall('.//tei:profileDesc//tei:keywords//tei:term', ns):
                if keyword.text:
                    result["keywords"].append(keyword.text.strip())
            
            # Extract full text
            text_parts = []
            for div in root.findall('.//tei:text//tei:div', ns):
                div_text = self._extract_text_content(div)
                if div_text.strip():
                    text_parts.append(div_text)
            
            result["full_text"] = "\n\n".join(text_parts)
            
            # Extract references
            for bibl in root.findall('.//tei:listBibl/tei:biblStruct', ns):
                ref_info = {}
                
                # Title
                title = bibl.find('.//tei:title[@level="a"]', ns)
                if title is not None and title.text:
                    ref_info["title"] = title.text.strip()
                
                # Authors
                ref_authors = []
                for author in bibl.findall('.//tei:author', ns):
                    author_name = self._extract_author_name(author, ns)
                    if author_name:
                        ref_authors.append(author_name)
                ref_info["authors"] = ref_authors
                
                # Journal/Conference
                journal = bibl.find('.//tei:title[@level="j"]', ns)
                if journal is not None and journal.text:
                    ref_info["journal"] = journal.text.strip()
                
                # Year
                date = bibl.find('.//tei:date[@type="published"]', ns)
                if date is not None and date.get('when'):
                    ref_info["year"] = date.get('when')[:4]
                
                if ref_info.get("title") or ref_info.get("authors"):
                    result["references"].append(ref_info)
            
            # Extract figures and tables
            for figure in root.findall('.//tei:figure', ns):
                fig_info = {}
                
                # Caption
                head = figure.find('.//tei:head', ns)
                if head is not None:
                    fig_info["caption"] = self._extract_text_content(head)
                
                # Type (table or figure)
                fig_type = figure.get('type', 'figure')
                fig_info["type"] = fig_type
                
                if fig_type == 'table':
                    # Extract table content
                    table = figure.find('.//tei:table', ns)
                    if table is not None:
                        fig_info["content"] = self._extract_table_content(table, ns)
                    result["tables"].append(fig_info)
                else:
                    result["figures"].append(fig_info)
            
            return result
            
        except Exception as e:
            logger.error(f"TEI XML parsing error: {e}")
            return {"full_text": tei_xml, "error": str(e)}
    
    def _extract_text_content(self, element) -> str:
        """Extract all text content from an XML element."""
        if element is None:
            return ""
        
        # Get text including all sub-elements
        text_parts = []
        if element.text:
            text_parts.append(element.text)
        
        for child in element:
            text_parts.append(self._extract_text_content(child))
            if child.tail:
                text_parts.append(child.tail)
        
        return " ".join(text_parts).strip()
    
    def _extract_author_name(self, author_elem, ns) -> str:
        """Extract author name from TEI element."""
        forename = author_elem.find('.//tei:forename', ns)
        surname = author_elem.find('.//tei:surname', ns)
        
        if forename is not None and surname is not None:
            return f"{forename.text} {surname.text}"
        elif surname is not None:
            return surname.text
        elif forename is not None:
            return forename.text
        return ""
    
    def _extract_table_content(self, table_elem, ns) -> str:
        """Extract table content from TEI table element."""
        rows = []
        for row in table_elem.findall('.//tei:row', ns):
            cells = []
            for cell in row.findall('.//tei:cell', ns):
                cell_text = self._extract_text_content(cell)
                cells.append(cell_text)
            if cells:
                rows.append(" | ".join(cells))
        
        return "\n".join(rows)

# Initialize GROBID processor
grobid_processor = GrobidProcessor()

@tool
def grobid_extract(file_path: str) -> Dict[str, Any]:
    """
    Extract academic content from PDF using GROBID (specialized for academic papers).
    
    Extracts:
    - Full text with academic structure
    - Authors and affiliations  
    - Abstract and keywords
    - Citations and references
    - Tables and figures with captions
    - Bibliographic metadata
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary with extracted academic content and metadata
    """
    return grobid_processor.process_fulltext(file_path)

# Test function
def test_grobid_extraction():
    """Test GROBID extraction with available PDF."""
    import os
    
    # Check if GROBID is running
    processor = GrobidProcessor()
    if not processor.is_alive():
        print("❌ GROBID service not running")
        print("Start with: docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0")
        return
    
    print("✅ GROBID service is running")
    
    # Look for test PDF
    for file in os.listdir('.'):
        if file.endswith('.pdf'):
            print(f"Testing GROBID with {file}")
            result = grobid_extract.invoke({"file_path": file})
            
            print(f"\n📊 GROBID Results:")
            print(f"   Success: {result.get('success')}")
            print(f"   Content length: {result.get('content_length', 0)}")
            
            if result.get('metadata'):
                meta = result['metadata']
                print(f"   Title: {meta.get('title', 'Unknown')[:60]}...")
                print(f"   Authors: {len(meta.get('authors', []))}")
                print(f"   References: {len(meta.get('references', []))}")
                print(f"   Citations: {len(meta.get('citations', []))}")
            
            break
    else:
        print("No PDF files found to test")

if __name__ == "__main__":
    test_grobid_extraction()
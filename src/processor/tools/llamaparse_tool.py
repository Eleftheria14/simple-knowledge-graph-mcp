"""LlamaParse PDF processing tool for LangGraph"""
from typing import Dict, Any
from pathlib import Path
import requests
import time

from langchain_core.tools import tool

@tool
def llamaparse_pdf(file_path: str, api_key: str) -> Dict[str, Any]:
    """
    Extract structured content from PDF using LlamaParse API.
    
    Args:
        file_path: Path to the PDF file
        api_key: LlamaParse API key
        
    Returns:
        Dictionary with extracted content, metadata, and success status
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}
        
        if not file_path.suffix.lower() == '.pdf':
            return {"success": False, "error": "File must be a PDF"}
        
        print(f"📄 Parsing PDF with LlamaParse: {file_path.name}")
        
        # LlamaParse API call
        url = "https://api.cloud.llamaindex.ai/api/parsing/upload"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        
        with open(file_path, 'rb') as f:
            files = {"file": f}
            data = {
                "parsing_instruction": "Extract all text, preserve structure, include tables and figures",
                "result_type": "markdown"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"LlamaParse API error: {response.status_code} - {response.text}"
            }
        
        job_data = response.json()
        job_id = job_data.get("id")
        
        if not job_id:
            return {"success": False, "error": "No job ID returned from LlamaParse"}
        
        # Poll for completion
        result_url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/markdown"
        max_attempts = 30  # 5 minutes max
        
        for attempt in range(max_attempts):
            result_response = requests.get(result_url, headers=headers)
            
            if result_response.status_code == 200:
                content = result_response.text
                return {
                    "success": True,
                    "content": content,
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "pages": content.count('\n---\n') + 1,  # Rough page count
                    "job_id": job_id
                }
            
            elif result_response.status_code == 400:
                # Still processing
                print(f"⏳ Processing... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(10)
            
            else:
                return {
                    "success": False,
                    "error": f"Error getting result: {result_response.status_code}"
                }
        
        return {"success": False, "error": "Timeout waiting for LlamaParse processing"}
        
    except Exception as e:
        return {"success": False, "error": f"Exception in llamaparse_pdf: {str(e)}"}

# Test function
def test_llamaparse_tool():
    """Test the LlamaParse tool with a dummy file"""
    import os
    
    # This would normally be a real PDF
    print("LlamaParse tool created successfully")
    print("Tool name:", llamaparse_pdf.name)
    print("Tool description:", llamaparse_pdf.description)

if __name__ == "__main__":
    test_llamaparse_tool()
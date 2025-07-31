#!/usr/bin/env python3
"""
Simple script to manually process PDFs in a folder
Usage: python process_pdfs.py /path/to/pdf/folder
"""
import sys
import asyncio
from pathlib import Path

from processor.document_pipeline import DocumentOrchestrator
from processor.config import ProcessorConfig

async def process_folder(folder_path: str):
    """Process all PDFs in a folder"""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Folder does not exist: {folder_path}")
        return
    
    if not folder.is_dir():
        print(f"❌ Path is not a directory: {folder_path}")
        return
    
    # Find all PDF files
    pdf_files = list(folder.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in {folder_path}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files in {folder_path}")
    print("🚀 Starting processing...")
    
    # Initialize orchestrator
    config = ProcessorConfig()
    config.validate()
    orchestrator = DocumentOrchestrator(config)
    
    # Process each PDF
    processed = 0
    failed = 0
    
    for pdf_file in pdf_files:
        try:
            print(f"\n📄 Processing: {pdf_file.name}")
            result = await orchestrator.process_document(str(pdf_file))
            
            if result.get('success'):
                processed += 1
                print(f"✅ Success: {result.get('message', 'Processed successfully')}")
            else:
                failed += 1
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            failed += 1
            print(f"❌ Error processing {pdf_file.name}: {e}")
    
    print(f"\n📊 Results: {processed} processed, {failed} failed")

def main():
    if len(sys.argv) != 2:
        print("Usage: python process_pdfs.py /path/to/pdf/folder")
        print("Example: python process_pdfs.py ~/Downloads")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    asyncio.run(process_folder(folder_path))

if __name__ == "__main__":
    main()
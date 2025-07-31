#!/usr/bin/env python3
"""
Super simple script to process PDFs
Just run: python process_now.py
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from processor.document_pipeline import DocumentOrchestrator
from processor.config import ProcessorConfig

# 📁 CONFIGURE YOUR PDF FOLDER HERE:
PDF_FOLDER = "/Users/aimiegarces/Downloads"  # Change this to where your PDFs are

async def main():
    print("🚀 Simple PDF Processor")
    print("=" * 40)
    
    # Check folder
    folder = Path(PDF_FOLDER)
    if not folder.exists():
        print(f"❌ Folder doesn't exist: {PDF_FOLDER}")
        print("📝 Edit this script and change PDF_FOLDER to your PDF location")
        return
    
    # Find PDFs
    pdf_files = list(folder.glob("*.pdf"))
    if not pdf_files:
        print(f"📁 No PDFs found in: {PDF_FOLDER}")
        print("📥 Put some PDF files in that folder and run again")
        return
    
    print(f"📁 Found {len(pdf_files)} PDFs in: {PDF_FOLDER}")
    
    # Show files and let user choose
    print("\n📋 Available PDFs:")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf.name}")
    
    print(f"\n🎯 Choose an option:")
    print(f"  1-{len(pdf_files)}: Process specific PDF")
    print(f"  'all': Process all PDFs")
    print(f"  'quit': Exit")
    
    choice = input("\n👉 Your choice: ").strip().lower()
    
    if choice == 'quit':
        print("👋 Goodbye!")
        return
    
    # Initialize processor
    try:
        config = ProcessorConfig()
        config.validate()
        orchestrator = DocumentOrchestrator(config)
    except Exception as e:
        print(f"❌ Setup error: {e}")
        print("💡 Make sure your .env file has GROQ_API_KEY and LLAMAPARSE_API_KEY")
        return
    
    # Process files
    if choice == 'all':
        print(f"\n🔄 Processing ALL {len(pdf_files)} PDFs...")
        for pdf_file in pdf_files:
            await process_single_pdf(orchestrator, pdf_file)
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(pdf_files):
                pdf_file = pdf_files[index]
                print(f"\n🔄 Processing: {pdf_file.name}")
                await process_single_pdf(orchestrator, pdf_file)
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a number or 'all'")

async def process_single_pdf(orchestrator, pdf_file):
    """Process a single PDF file"""
    try:
        result = await orchestrator.process_document(str(pdf_file))
        
        if result.get('success'):
            print(f"✅ {pdf_file.name}: SUCCESS")
            if 'entities_found' in result:
                print(f"   📊 Found {result['entities_found']} entities, {result['relationships_found']} relationships")
        else:
            print(f"❌ {pdf_file.name}: FAILED")
            print(f"   💥 Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ {pdf_file.name}: ERROR - {e}")

if __name__ == "__main__":
    asyncio.run(main())
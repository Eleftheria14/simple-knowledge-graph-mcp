"""Folder watching system for automatic document processing"""
import asyncio
import time
from pathlib import Path
from typing import List, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from processor.document_pipeline import DocumentOrchestrator
from processor.config import ProcessorConfig

class PDFHandler(FileSystemEventHandler):
    """Handle PDF file creation events"""
    
    def __init__(self, orchestrator: DocumentOrchestrator):
        self.orchestrator = orchestrator
        self.processing: Set[str] = set()  # Track files being processed
        
    def on_created(self, event):
        """Handle file creation events"""
        if isinstance(event, FileCreatedEvent) and event.src_path.endswith('.pdf'):
            pdf_path = event.src_path
            
            # Avoid duplicate processing
            if pdf_path in self.processing:
                return
                
            print(f"📁 New PDF detected: {Path(pdf_path).name}")
            
            # Schedule async processing
            asyncio.create_task(self._process_pdf(pdf_path))
    
    async def _process_pdf(self, pdf_path: str):
        """Process a PDF asynchronously"""
        try:
            self.processing.add(pdf_path)
            
            # Wait a moment for file to be fully written
            await asyncio.sleep(2)
            
            # Process through orchestrator
            result = await self.orchestrator.process_document(pdf_path)
            
            if result.get('success'):
                print(f"✅ Auto-processed: {Path(pdf_path).name}")
            else:
                print(f"❌ Failed to auto-process: {Path(pdf_path).name} - {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error in auto-processing {pdf_path}: {e}")
        
        finally:
            self.processing.discard(pdf_path)

class FolderWatcher:
    """Watch folders for new PDF files"""
    
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.orchestrator = DocumentOrchestrator(config)
        self.observer = Observer()
        self.watch_paths: List[str] = []
        
    def add_watch_path(self, path: str):
        """Add a folder to watch for PDFs"""
        watch_path = Path(path).resolve()
        
        if not watch_path.exists():
            raise ValueError(f"Watch path does not exist: {watch_path}")
        
        if not watch_path.is_dir():
            raise ValueError(f"Watch path is not a directory: {watch_path}")
        
        self.watch_paths.append(str(watch_path))
        print(f"📂 Added watch path: {watch_path}")
    
    def start_watching(self):
        """Start watching all configured paths"""
        if not self.watch_paths:
            raise ValueError("No watch paths configured. Use add_watch_path() first.")
        
        handler = PDFHandler(self.orchestrator)
        
        for watch_path in self.watch_paths:
            self.observer.schedule(handler, watch_path, recursive=True)
            print(f"👀 Watching: {watch_path}")
        
        self.observer.start()
        print("🚀 Folder watcher started! Drop PDFs into watched folders to process them.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping folder watcher...")
            self.observer.stop()
        
        self.observer.join()
        print("✅ Folder watcher stopped")

# CLI interface
async def main():
    """Main CLI for folder watching"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python folder_watcher.py <watch_folder> [additional_folders...]")
        print("Example: python folder_watcher.py /Users/user/Documents/PDFs")
        return
    
    watch_folders = sys.argv[1:]
    
    try:
        config = ProcessorConfig()
        config.validate()
        
        watcher = FolderWatcher(config)
        
        # Add all watch folders
        for folder in watch_folders:
            watcher.add_watch_path(folder)
        
        # Start watching
        watcher.start_watching()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
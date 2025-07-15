"""
GraphRAG MCP Progress Tracking

This module provides progress tracking utilities for document processing.
"""

import time


class ProgressTracker:
    """Basic progress tracker for batch operations"""

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = self.start_time

    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        self.last_update = time.time()

        # Simple progress display
        percentage = (self.current / self.total) * 100
        elapsed = self.last_update - self.start_time

        if self.current == self.total:
            print(f"✅ {self.description}: {self.current}/{self.total} ({percentage:.1f}%) - Complete in {elapsed:.1f}s")
        else:
            print(f"⏳ {self.description}: {self.current}/{self.total} ({percentage:.1f}%)")

    def finish(self):
        """Mark as finished"""
        if self.current < self.total:
            self.current = self.total
            self.update(0)


class NotebookProgressTracker(ProgressTracker):
    """Progress tracker optimized for Jupyter notebooks"""

    def __init__(self, total: int, description: str = "Processing"):
        super().__init__(total, description)
        self.use_tqdm = False

        # Try to use tqdm for notebooks
        try:
            from tqdm.notebook import tqdm
            self.progress_bar = tqdm(total=total, desc=description, unit="doc")
            self.use_tqdm = True
        except ImportError:
            self.progress_bar = None

    def update(self, increment: int = 1):
        """Update progress with tqdm if available"""
        if self.use_tqdm and self.progress_bar:
            self.progress_bar.update(increment)
        else:
            super().update(increment)

        self.current += increment
        self.last_update = time.time()

    def finish(self):
        """Mark as finished"""
        if self.use_tqdm and self.progress_bar:
            self.progress_bar.close()
        else:
            super().finish()


class DetailedProgressTracker:
    """Detailed progress tracker with metrics"""

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.items = []

    def start_item(self, item_name: str):
        """Start processing an item"""
        item_info = {
            "name": item_name,
            "start_time": time.time(),
            "end_time": None,
            "success": None,
            "error": None
        }
        self.items.append(item_info)
        return len(self.items) - 1  # Return index

    def finish_item(self, index: int, success: bool, error: str | None = None):
        """Finish processing an item"""
        if 0 <= index < len(self.items):
            self.items[index]["end_time"] = time.time()
            self.items[index]["success"] = success
            self.items[index]["error"] = error
            self.current += 1

    def get_stats(self) -> dict:
        """Get processing statistics"""
        current_time = time.time()
        elapsed = current_time - self.start_time

        successful = sum(1 for item in self.items if item["success"] is True)
        failed = sum(1 for item in self.items if item["success"] is False)

        return {
            "total": self.total,
            "current": self.current,
            "successful": successful,
            "failed": failed,
            "elapsed_time": elapsed,
            "avg_time_per_item": elapsed / max(self.current, 1),
            "percentage": (self.current / self.total) * 100 if self.total > 0 else 0
        }

    def print_summary(self):
        """Print processing summary"""
        stats = self.get_stats()

        print(f"📊 {self.description} Summary:")
        print(f"   ✅ Successful: {stats['successful']}")
        print(f"   ❌ Failed: {stats['failed']}")
        print(f"   ⏱️  Total time: {stats['elapsed_time']:.1f}s")
        print(f"   📈 Average per item: {stats['avg_time_per_item']:.1f}s")
        print(f"   📊 Completion: {stats['percentage']:.1f}%")


def create_progress_tracker(total: int, description: str = "Processing",
                          tracker_type: str = "auto") -> ProgressTracker:
    """
    Create appropriate progress tracker based on environment
    
    Args:
        total: Total number of items to process
        description: Description of the process
        tracker_type: Type of tracker (auto, basic, notebook, detailed)
        
    Returns:
        ProgressTracker instance
    """
    if tracker_type == "auto":
        # Try to detect notebook environment
        try:
            from IPython import get_ipython
            if get_ipython() is not None:
                return NotebookProgressTracker(total, description)
        except ImportError:
            pass

        # Default to basic tracker
        return ProgressTracker(total, description)

    elif tracker_type == "notebook":
        return NotebookProgressTracker(total, description)

    elif tracker_type == "detailed":
        return DetailedProgressTracker(total, description)

    else:
        return ProgressTracker(total, description)

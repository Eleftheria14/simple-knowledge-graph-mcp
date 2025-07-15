"""
GraphRAG MCP Document Processing Utilities
Simplified utilities for interactive document processing workflow
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Progress tracking

# Add project root to path (notebooks/Main -> notebooks -> Agents)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import from the new package structure
from graphrag_mcp.api import GraphRAGProcessor
from graphrag_mcp.ui import DocumentStatus

print("✅ GraphRAG MCP components imported from new package structure")


class NotebookDocumentProcessor:
    """Simplified document processing with progress tracking using new API"""

    def __init__(self, project_name: str = "my-research", template: str = "academic"):
        self.project_name = project_name
        self.template = template

        # Use the new GraphRAGProcessor
        self.processor = GraphRAGProcessor(project_name, template)
        print("✅ Processing components initialized using new GraphRAGProcessor")

    def discover_documents(self, folder_path: str) -> list[DocumentStatus]:
        """Discover PDF documents in folder using new API"""
        # Use the new GraphRAGProcessor
        document_infos = self.processor.discover_documents(folder_path)

        # Convert DocumentInfo to DocumentStatus for notebook compatibility
        documents = []
        for doc_info in document_infos:
            doc_status = doc_info.to_document_status()
            documents.append(doc_status)

        return documents

    async def process_single_document(self, doc_status: DocumentStatus) -> bool:
        """Process a single document using the new API"""
        # Delegate to the new GraphRAGProcessor
        return await self.processor._process_single_document(doc_status)

    async def process_documents(self, documents: list[DocumentStatus]) -> dict:
        """Process documents with progress tracking using new API"""
        if not documents:
            return {"success": 0, "failed": 0, "total_time": 0}

        # Use the new GraphRAGProcessor
        results = await self.processor.process_documents(documents)

        # Convert ProcessingResults to dict for notebook compatibility
        return {
            "success": results.success,
            "failed": results.failed,
            "total_time": results.total_time,
            "avg_time": results.total_time / len(documents) if documents else 0
        }

    def get_results_dataframe(self, documents: list[DocumentStatus]) -> pd.DataFrame:
        """Create results DataFrame"""
        return pd.DataFrame([
            {
                'Document': doc.name,
                'Status': doc.status,
                'Size (MB)': doc.size_mb,
                'Time (s)': doc.processing_time,
                'Entities': doc.entities_found,
                'Citations': doc.citations_found,
                'Error': doc.error_message or ''
            } for doc in documents
        ])

    def show_analytics(self, documents: list[DocumentStatus]):
        """Display processing analytics"""
        df = self.get_results_dataframe(documents)
        completed = df[df['Status'] == 'completed']

        if completed.empty:
            print("❌ No completed documents to analyze")
            return

        print("📈 Analytics:")
        print(f"   Average time: {completed['Time (s)'].mean():.1f}s")
        print(f"   Total entities: {completed['Entities'].sum()}")
        print(f"   Total citations: {completed['Citations'].sum()}")

        # Simple visualization
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # Processing time vs size
        axes[0,0].scatter(completed['Size (MB)'], completed['Time (s)'])
        axes[0,0].set_xlabel('Size (MB)')
        axes[0,0].set_ylabel('Time (s)')
        axes[0,0].set_title('Processing Time vs Size')

        # Entities per document
        axes[0,1].bar(range(len(completed)), completed['Entities'])
        axes[0,1].set_xlabel('Document')
        axes[0,1].set_ylabel('Entities')
        axes[0,1].set_title('Entities Found')

        # Time distribution
        axes[1,0].hist(completed['Time (s)'], bins=8, alpha=0.7)
        axes[1,0].set_xlabel('Time (s)')
        axes[1,0].set_ylabel('Count')
        axes[1,0].set_title('Processing Time Distribution')

        # Status summary
        status_counts = df['Status'].value_counts()
        axes[1,1].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
        axes[1,1].set_title('Status Summary')

        plt.tight_layout()
        plt.show()

    def get_failed_documents(self, documents: list[DocumentStatus]) -> list[DocumentStatus]:
        """Get failed documents for retry"""
        return [doc for doc in documents if doc.status == "failed"]

    def reset_for_retry(self, documents: list[DocumentStatus]):
        """Reset documents for retry"""
        for doc in documents:
            doc.status = "pending"
            doc.start_time = None
            doc.end_time = None
            doc.error_message = None
            doc.processing_time = 0.0

    def visualize_knowledge_graph(self, documents: list[DocumentStatus], max_nodes: int = 50):
        """Create interactive knowledge graph visualization using new API"""
        # Use the new GraphRAGProcessor
        return self.processor.visualize_knowledge_graph(documents, max_nodes)

    def print_next_steps(self):
        """Print next steps for user"""
        print("🎯 Next Steps:")
        print("1. 🚀 Start MCP Server:")
        print(f"   graphrag-mcp serve {self.project_name} --transport stdio")
        print("")
        print("2. 🔌 Connect to Claude Desktop:")
        print('   Add to ~/.config/claude-desktop/config.json:')
        print(f'   "{self.project_name}": {{')
        print('     "command": "graphrag-mcp",')
        print(f'     "args": ["serve", "{self.project_name}", "--transport", "stdio"]')
        print('   }')
        print("")
        print("3. 💬 Try these queries in Claude:")
        print('   - "Ask knowledge graph: What are the main themes?"')
        print('   - "Get facts with citations about [topic]"')
        print('   - "Generate bibliography in APA style"')


def quick_setup(project_name: str = "my-research", documents_folder: str = "../../examples") -> NotebookDocumentProcessor:
    """Quick setup for document processing"""
    processor = NotebookDocumentProcessor(project_name=project_name)
    return processor


# NOTE: check_prerequisites is now imported from the main package
# No need to redefine it here - it's already imported at the top

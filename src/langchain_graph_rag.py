"""
LangChain GraphRAG Knowledge Graph for Scientific Papers
Replaces NetworkX with scalable vector-based graph retrieval system.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import networkx as nx

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

GRAPH_RETRIEVER_AVAILABLE = True  # Using custom implementation

logger = logging.getLogger(__name__)


class LangChainGraphRAG:
    """
    LangChain GraphRAG implementation for scientific papers.
    Uses vector store with metadata-based graph traversal for scalable knowledge graphs.
    """
    
    def __init__(self, 
                 llm_model: str = "llama3.1:8b",
                 embedding_model: str = "nomic-embed-text",
                 persist_directory: str = "./chroma_graph_db"):
        """Initialize LangChain GraphRAG system"""
        
        # Custom GraphRAG implementation using standard LangChain components
        
        self.llm = ChatOllama(
            model=llm_model,
            temperature=0.1,
            num_ctx=32768,
            num_predict=2048
        )
        
        self.embeddings = OllamaEmbeddings(
            model=embedding_model
        )
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize vector store
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory)
        )
        
        # Define metadata edges for graph traversal
        self.metadata_edges = [
            ("authors", "authors"),           # Papers by same authors
            ("institutions", "institutions"), # Papers from same institutions
            ("methods", "methods"),           # Papers using same methods
            ("concepts", "concepts"),         # Papers with shared concepts
            ("technologies", "technologies"), # Papers using same technologies
            ("datasets", "datasets"),         # Papers using same datasets
        ]
        
        # Custom retriever using vector store similarity + metadata filtering
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}
        )
        
        logger.info("🕸️ LangChain GraphRAG initialized")
    
    def _graph_retrieval(self, query: str, k: int = 5) -> List[Document]:
        """Custom graph-like retrieval using metadata traversal"""
        
        # Step 1: Get initial relevant documents
        initial_docs = self.retriever.get_relevant_documents(query)
        
        # Step 2: Expand through metadata connections
        expanded_docs = []
        expanded_docs.extend(initial_docs[:k//2])  # Start with top relevant docs
        
        # Step 3: Find related documents through shared entities
        for doc in initial_docs[:2]:  # Use top 2 docs as seeds
            metadata = doc.metadata
            
            # Search for documents with shared entities
            for edge_type, _ in self.metadata_edges:
                entities_json = metadata.get(edge_type, '[]')
                entities = json.loads(entities_json) if isinstance(entities_json, str) else entities_json
                if entities:
                    # Find docs with overlapping entities
                    for entity in entities[:3]:  # Limit to avoid explosion
                        # Search by entity name directly
                        related_docs = self.vector_store.similarity_search(
                            entity, 
                            k=3
                        )
                        expanded_docs.extend(related_docs[:1])  # Add best match
        
        # Remove duplicates and limit results
        seen_ids = set()
        unique_docs = []
        for doc in expanded_docs:
            doc_id = doc.metadata.get('chunk_id', id(doc))
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_docs.append(doc)
                if len(unique_docs) >= k:
                    break
        
        return unique_docs
    
    def extract_entities_and_relationships(self, 
                                         paper_content: str, 
                                         paper_title: str = "",
                                         paper_id: str = None) -> Dict:
        """
        Extract entities and add paper to graph knowledge base
        
        Args:
            paper_content: Full text of the paper
            paper_title: Title of the paper
            paper_id: Unique identifier for the paper
            
        Returns:
            Dict with entities and processing results
        """
        logger.info(f"🔍 Processing paper: {paper_title}")
        
        if not paper_id:
            paper_id = f"paper_{len(self.get_all_papers()) + 1}"
        
        # Extract entities using LLM
        entities = self._extract_entities(paper_content[:4000], paper_title)
        
        # Create documents with rich metadata
        documents = self._create_documents_with_metadata(
            paper_content, paper_title, paper_id, entities
        )
        
        # Add to vector store
        document_ids = self.vector_store.add_documents(documents)
        
        # Update retriever with new documents
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}
        )
        
        result = {
            'paper_id': paper_id,
            'entities': entities,
            'documents_added': len(documents),
            'document_ids': document_ids,
            'total_papers': len(self.get_all_papers())
        }
        
        logger.info(f"✅ Added paper to graph: {len(documents)} documents")
        return result
    
    def _extract_entities(self, content: str, title: str) -> Dict:
        """Extract entities using LLM (same logic as NetworkX version)"""
        
        entity_prompt = ChatPromptTemplate.from_template("""
Extract key entities from this scientific paper. Return ONLY a valid JSON object:

{{
  "paper": "{title}",
  "authors": ["First Author", "Second Author"],
  "institutions": ["University Name", "Company Name"],
  "methods": ["Method 1", "Method 2"],
  "concepts": ["Key Concept 1", "Key Concept 2"],
  "technologies": ["Technology 1", "Technology 2"],
  "metrics": ["Accuracy", "Performance Metric"],
  "datasets": ["Dataset Name 1", "Dataset Name 2"]
}}

Important: 
- Extract real entities mentioned in the text
- Limit to 3-5 items per category
- Use exact names from the paper
- Return valid JSON only

Paper title: {title}

Content:
{content}

JSON:""")
        
        try:
            chain = entity_prompt | self.llm | StrOutputParser()
            result = chain.invoke({"content": content, "title": title})
            
            # Extract JSON from response
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                entities = json.loads(json_str)
                return entities
            else:
                logger.warning("⚠️ Could not extract valid JSON for entities")
                return self._fallback_entities(title)
                
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            return self._fallback_entities(title)
    
    def _create_documents_with_metadata(self, 
                                      content: str, 
                                      title: str, 
                                      paper_id: str, 
                                      entities: Dict) -> List[Document]:
        """Create documents with rich metadata for graph traversal"""
        
        # Split content into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = text_splitter.split_text(content)
        
        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            metadata = {
                'paper_id': paper_id,
                'paper_title': title,
                'chunk_id': f"{paper_id}_chunk_{i}",
                'chunk_index': i,
                'total_chunks': len(chunks),
                # Entity metadata for graph edges (stored as JSON strings for ChromaDB)
                'authors': json.dumps(entities.get('authors', [])),
                'institutions': json.dumps(entities.get('institutions', [])),
                'methods': json.dumps(entities.get('methods', [])),
                'concepts': json.dumps(entities.get('concepts', [])),
                'technologies': json.dumps(entities.get('technologies', [])),
                'datasets': json.dumps(entities.get('datasets', [])),
                'metrics': json.dumps(entities.get('metrics', []))
            }
            
            doc = Document(
                page_content=chunk,
                metadata=metadata
            )
            documents.append(doc)
        
        return documents
    
    def _fallback_entities(self, title: str) -> Dict:
        """Fallback entity structure if extraction fails"""
        return {
            "paper": title,
            "authors": [],
            "institutions": [],
            "methods": [],
            "concepts": [],
            "technologies": [],
            "metrics": [],
            "datasets": []
        }
    
    def query_graph(self, query: str, k: int = 5) -> Dict:
        """Query the knowledge graph using custom GraphRAG retrieval"""
        
        try:
            # Retrieve documents using custom graph traversal
            docs = self._graph_retrieval(query, k)
            
            # Group results by paper
            papers = {}
            for doc in docs:
                paper_id = doc.metadata.get('paper_id', 'unknown')
                if paper_id not in papers:
                    papers[paper_id] = {
                        'paper_title': doc.metadata.get('paper_title', ''),
                        'chunks': [],
                        'entities': {
                            'authors': json.loads(doc.metadata.get('authors', '[]')),
                            'methods': json.loads(doc.metadata.get('methods', '[]')),
                            'concepts': json.loads(doc.metadata.get('concepts', '[]'))
                        }
                    }
                papers[paper_id]['chunks'].append(doc.page_content)
            
            return {
                'query': query,
                'papers_found': len(papers),
                'papers': papers,
                'total_chunks': len(docs)
            }
            
        except Exception as e:
            logger.error(f"❌ Graph query failed: {e}")
            return {"error": f"Query failed: {e}"}
    
    def find_related_papers(self, paper_id: str, relation_type: str = "concepts") -> Dict:
        """Find papers related by specific entity types"""
        
        try:
            # Get the paper's entities
            paper_docs = self.vector_store.get(
                where={"paper_id": paper_id}
            )
            
            if not paper_docs['documents']:
                return {"error": f"Paper {paper_id} not found"}
            
            # Get entities from first document (decode JSON)
            target_entities_json = paper_docs['metadatas'][0].get(relation_type, '[]')
            target_entities = json.loads(target_entities_json) if isinstance(target_entities_json, str) else target_entities_json
            
            if not target_entities:
                return {"papers": []}
            
            # Find papers with overlapping entities using similarity search
            related_docs = []
            for entity in target_entities:
                docs = self.vector_store.similarity_search(entity, k=5)
                related_docs.extend(docs)
            
            # Group by paper and exclude original
            related_papers = {}
            for doc in related_docs:
                metadata = doc.metadata
                rel_paper_id = metadata.get('paper_id', '')
                
                if rel_paper_id != paper_id and rel_paper_id:
                    if rel_paper_id not in related_papers:
                        related_papers[rel_paper_id] = {
                            'paper_title': metadata.get('paper_title', ''),
                            'shared_entities': set(),
                            'relation_type': relation_type
                        }
                    
                    # Find shared entities (decode JSON)
                    rel_entities_json = metadata.get(relation_type, '[]')
                    rel_entities = json.loads(rel_entities_json) if isinstance(rel_entities_json, str) else rel_entities_json
                    shared = set(target_entities) & set(rel_entities)
                    related_papers[rel_paper_id]['shared_entities'].update(shared)
            
            # Convert sets to lists for JSON serialization
            for paper in related_papers.values():
                paper['shared_entities'] = list(paper['shared_entities'])
            
            return {
                'source_paper': paper_id,
                'relation_type': relation_type,
                'related_papers': related_papers
            }
            
        except Exception as e:
            logger.error(f"❌ Related papers search failed: {e}")
            return {"error": f"Search failed: {e}"}
    
    def get_all_papers(self) -> List[Dict]:
        """Get list of all papers in the knowledge base"""
        
        try:
            # Get all documents and extract unique papers
            all_docs = self.vector_store.get()
            
            papers = {}
            for metadata in all_docs['metadatas']:
                paper_id = metadata.get('paper_id', '')
                if paper_id and paper_id not in papers:
                    papers[paper_id] = {
                        'paper_id': paper_id,
                        'paper_title': metadata.get('paper_title', ''),
                        'authors': json.loads(metadata.get('authors', '[]')),
                        'chunk_count': 0
                    }
                
                if paper_id in papers:
                    papers[paper_id]['chunk_count'] += 1
            
            return list(papers.values())
            
        except Exception as e:
            logger.error(f"❌ Failed to get papers: {e}")
            return []
    
    def get_graph_summary(self) -> Dict:
        """Get summary of the knowledge graph"""
        
        papers = self.get_all_papers()
        
        # Aggregate entity statistics
        entity_counts = {
            'authors': set(),
            'institutions': set(),
            'methods': set(),
            'concepts': set(),
            'technologies': set(),
            'datasets': set()
        }
        
        try:
            all_docs = self.vector_store.get()
            for metadata in all_docs['metadatas']:
                for entity_type in entity_counts.keys():
                    entities_json = metadata.get(entity_type, '[]')
                    entities = json.loads(entities_json) if isinstance(entities_json, str) else entities_json
                    entity_counts[entity_type].update(entities)
            
            # Convert to counts
            entity_summary = {k: len(v) for k, v in entity_counts.items()}
            
        except Exception as e:
            logger.error(f"❌ Failed to get entity counts: {e}")
            entity_summary = {}
        
        return {
            'total_papers': len(papers),
            'total_documents': len(all_docs['documents']) if 'all_docs' in locals() else 0,
            'unique_entities': entity_summary,
            'graph_edges': self.metadata_edges,
            'retrieval_strategy': 'Eager(k=5, start_k=1, max_depth=2)'
        }
    
    def export_for_corpus(self, paper_id: str) -> Optional[Dict]:
        """Export paper data for corpus integration"""
        
        try:
            paper_docs = self.vector_store.get(
                where={"paper_id": paper_id}
            )
            
            if not paper_docs['documents']:
                return None
            
            # Combine all chunks
            full_content = "\n\n".join(paper_docs['documents'])
            metadata = paper_docs['metadatas'][0]
            
            return {
                'document_id': paper_id,
                'title': metadata.get('paper_title', ''),
                'content': full_content,
                'metadata': {
                    'authors': json.loads(metadata.get('authors', '[]')),
                    'institutions': json.loads(metadata.get('institutions', '[]')),
                    'methods': json.loads(metadata.get('methods', '[]')),
                    'concepts': json.loads(metadata.get('concepts', '[]')),
                    'technologies': json.loads(metadata.get('technologies', '[]')),
                    'datasets': json.loads(metadata.get('datasets', '[]')),
                    'chunk_count': len(paper_docs['documents'])
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return None
    
    def create_yfiles_visualization(self, **kwargs):
        """
        Create professional yFiles visualization
        
        Returns:
            Tuple of (widget, visualizer) or (None, None) if failed
        """
        try:
            from .yfiles_visualization import create_yfiles_visualization
            return create_yfiles_visualization(self, **kwargs)
        except ImportError:
            logger.warning("yFiles not available. Install with: pip install yfiles_jupyter_graphs")
            return None, None
        except Exception as e:
            logger.error(f"yFiles visualization failed: {e}")
            return None, None
    
    def create_visual_graph(self, output_file: str = "knowledge_graph.html", 
                           show_edge_labels: bool = True) -> Optional[str]:
        """
        Create an interactive visual representation of the knowledge graph
        
        Args:
            output_file: HTML file to save the visualization
            show_edge_labels: Whether to show relationship labels on edges
            
        Returns:
            Path to the generated HTML file or None if failed
        """
        try:
            # Create NetworkX graph from the data
            G = nx.Graph()
            
            # Get all papers and their entities
            all_papers = self.get_all_papers()
            
            if not all_papers:
                logger.warning("No papers found for visualization")
                return None
            
            # Track entity relationships across papers
            entity_connections = {}
            entity_papers = {}
            
            # Process each paper
            for paper in all_papers:
                paper_id = paper.get('paper_id', 'unknown')
                paper_title = paper.get('paper_title', 'Unknown Title')
                
                # Get detailed paper info
                corpus_doc = self.export_for_corpus(paper_id)
                if not corpus_doc:
                    continue
                
                metadata = corpus_doc.get('metadata', {})
                
                # Add paper node
                G.add_node(f"📄 {paper_title[:30]}...", 
                          node_type='paper',
                          paper_id=paper_id,
                          color='lightblue',
                          size=20)
                
                # Process each entity type
                for entity_type, entities in metadata.items():
                    if not entities or entity_type == 'chunk_count':
                        continue
                    
                    for entity in entities:
                        if not entity:
                            continue
                        
                        entity_key = f"{entity_type}:{entity}"
                        
                        # Add entity node if not exists
                        if entity_key not in G:
                            # Color by entity type
                            colors = {
                                'authors': 'lightgreen',
                                'institutions': 'orange', 
                                'methods': 'yellow',
                                'concepts': 'pink',
                                'technologies': 'lightcoral',
                                'datasets': 'lightgray'
                            }
                            color = colors.get(entity_type, 'white')
                            
                            G.add_node(entity_key,
                                      node_type=entity_type,
                                      entity_name=entity,
                                      color=color,
                                      size=15)
                        
                        # Connect paper to entity
                        G.add_edge(f"📄 {paper_title[:30]}...", entity_key,
                                  relationship=f"has_{entity_type}")
                        
                        # Track entity connections
                        if entity_key not in entity_papers:
                            entity_papers[entity_key] = []
                        entity_papers[entity_key].append(paper_id)
            
            # Add connections between entities that appear in multiple papers
            for entity_key, paper_list in entity_papers.items():
                if len(paper_list) > 1:
                    # This entity appears in multiple papers
                    for other_entity, other_papers in entity_papers.items():
                        if (entity_key != other_entity and 
                            len(set(paper_list) & set(other_papers)) > 0):
                            # Entities share papers
                            if not G.has_edge(entity_key, other_entity):
                                G.add_edge(entity_key, other_entity,
                                          relationship="co-occurs")
            
            logger.info(f"📊 Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
            
            # Export for different visualization options
            return self._create_interactive_html(G, output_file, show_edge_labels)
            
        except Exception as e:
            logger.error(f"❌ Visualization creation failed: {e}")
            return None
    
    def _create_interactive_html(self, G: nx.Graph, output_file: str, 
                                show_edge_labels: bool) -> str:
        """Create interactive HTML visualization using pyvis"""
        try:
            from pyvis.network import Network
            
            # Create pyvis network
            net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
            net.barnes_hut()
            
            # Add nodes
            for node, data in G.nodes(data=True):
                node_type = data.get('node_type', 'unknown')
                color = data.get('color', 'white')
                size = data.get('size', 10)
                
                # Create label
                if node_type == 'paper':
                    label = f"📄 {node.replace('📄 ', '')}"
                    title = f"Paper: {data.get('paper_id', 'Unknown')}"
                else:
                    entity_name = data.get('entity_name', node.split(':', 1)[-1])
                    label = f"{entity_name}"
                    title = f"{node_type.title()}: {entity_name}"
                
                net.add_node(node, label=label, title=title, color=color, size=size)
            
            # Add edges
            for source, target, data in G.edges(data=True):
                relationship = data.get('relationship', 'connected')
                
                if show_edge_labels:
                    net.add_edge(source, target, label=relationship, color="gray")
                else:
                    net.add_edge(source, target, color="gray")
            
            # Configure physics
            net.set_options("""
            var options = {
              "physics": {
                "enabled": true,
                "barnesHut": {
                  "gravitationalConstant": -2000,
                  "centralGravity": 0.3,
                  "springLength": 95,
                  "springConstant": 0.04,
                  "damping": 0.09
                }
              }
            }
            """)
            
            # Save to file
            net.save_graph(output_file)
            logger.info(f"✅ Interactive visualization saved to: {output_file}")
            
            return output_file
            
        except ImportError:
            logger.warning("pyvis not available, creating matplotlib visualization")
            return self._create_matplotlib_plot(G, output_file)
        except Exception as e:
            logger.error(f"❌ Interactive HTML creation failed: {e}")
            return None
    
    def _create_matplotlib_plot(self, G: nx.Graph, output_file: str) -> str:
        """Fallback matplotlib visualization"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            plt.figure(figsize=(12, 8))
            
            # Create layout
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Separate nodes by type
            paper_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'paper']
            entity_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') != 'paper']
            
            # Draw paper nodes
            if paper_nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=paper_nodes, 
                                     node_color='lightblue', node_size=300, alpha=0.8)
            
            # Draw entity nodes by type
            entity_types = {}
            for node, data in G.nodes(data=True):
                if data.get('node_type') != 'paper':
                    entity_type = data.get('node_type', 'unknown')
                    if entity_type not in entity_types:
                        entity_types[entity_type] = []
                    entity_types[entity_type].append(node)
            
            colors = ['lightgreen', 'orange', 'yellow', 'pink', 'lightcoral', 'lightgray']
            for i, (entity_type, nodes) in enumerate(entity_types.items()):
                color = colors[i % len(colors)]
                nx.draw_networkx_nodes(G, pos, nodelist=nodes, 
                                     node_color=color, node_size=200, alpha=0.7)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray')
            
            # Draw labels (simplified)
            labels = {}
            for node, data in G.nodes(data=True):
                if data.get('node_type') == 'paper':
                    labels[node] = "📄"
                else:
                    entity_name = data.get('entity_name', node.split(':', 1)[-1])
                    labels[node] = entity_name[:10] + "..." if len(entity_name) > 10 else entity_name
            
            nx.draw_networkx_labels(G, pos, labels, font_size=8)
            
            plt.title("Knowledge Graph Visualization", size=16)
            plt.axis('off')
            plt.tight_layout()
            
            # Save plot
            plot_file = output_file.replace('.html', '.png')
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Matplotlib visualization saved to: {plot_file}")
            return plot_file
            
        except Exception as e:
            logger.error(f"❌ Matplotlib visualization failed: {e}")
            return None


if __name__ == "__main__":
    # Test the LangChain GraphRAG system
    print("🧪 Testing LangChain GraphRAG...")
    
    if not GRAPH_RETRIEVER_AVAILABLE:
        print("❌ langchain-graph-retriever not installed")
        print("Install with: pip install langchain-graph-retriever")
        exit(1)
    
    graph_rag = LangChainGraphRAG()
    
    # Test with sample content
    sample_content = """
    This paper presents a review of large language models and autonomous agents in chemistry.
    The authors include Mayk Caldas Ramos, Christopher J. Collison, and Andrew D. White.
    They evaluate transformer architectures like BERT and GPT on chemical datasets.
    The models achieve 89% accuracy on molecular property prediction tasks.
    """
    
    result = graph_rag.extract_entities_and_relationships(
        sample_content, 
        "LLM Review Paper",
        "test_paper_1"
    )
    
    print("✅ Test completed!")
    print(f"📊 Results: {result}")
    
    # Test query
    query_result = graph_rag.query_graph("language models in chemistry")
    print(f"🔍 Query result: {query_result}")
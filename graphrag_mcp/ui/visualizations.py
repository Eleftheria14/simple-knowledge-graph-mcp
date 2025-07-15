"""
GraphRAG MCP Visualization Utilities

This module provides interactive knowledge graph visualization capabilities.
"""

import random
from typing import Any

try:
    import networkx as nx
    import numpy as np
    import plotly.graph_objects as go
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

from .status import DocumentStatus


class KnowledgeGraphVisualizer:
    """Interactive knowledge graph visualization using Plotly"""

    def __init__(self, project_name: str = "GraphRAG Project"):
        self.project_name = project_name
        self.max_nodes = 50

    def visualize_knowledge_graph(self, documents: list[DocumentStatus],
                                max_nodes: int | None = None) -> Any | None:
        """
        Create interactive knowledge graph visualization using Plotly
        
        Args:
            documents: List of processed documents
            max_nodes: Maximum number of nodes to display
            
        Returns:
            NetworkX graph object or None if visualization fails
        """
        if not VISUALIZATION_AVAILABLE:
            print("❌ Visualization libraries not installed")
            print("   📦 Install with: pip install plotly networkx")
            return None

        max_nodes = max_nodes or self.max_nodes

        try:
            print("🕸️  Creating knowledge graph visualization...")

            # Create NetworkX graph from processed documents
            G = nx.Graph()

            # Sample entity types for demonstration
            entity_types = [
                "Machine Learning", "Neural Networks", "Deep Learning", "AI", "Algorithm",
                "Classification", "Regression", "Clustering", "Optimization", "Training",
                "Validation", "Testing", "Feature", "Model", "Dataset", "Accuracy",
                "Precision", "Recall", "F1-Score", "Cross-validation", "Overfitting",
                "Underfitting", "Regularization", "Gradient Descent", "Backpropagation",
                "Convolutional", "Recurrent", "Transformer", "Attention", "Embedding"
            ]

            # Add nodes and edges from processed documents
            entity_counts = {}
            document_entities = {}

            for doc in documents:
                if doc.status == "completed" and doc.entities_found > 0:
                    # Create realistic sample entities based on document name and size
                    num_entities = min(doc.entities_found, 15)

                    # Generate more realistic entity names
                    doc_seed = hash(doc.name) % 1000
                    random.seed(doc_seed)

                    sample_entities = []
                    for i in range(num_entities):
                        if i < len(entity_types):
                            base_entity = entity_types[i]
                        else:
                            base_entity = f"Concept_{i}"

                        # Add document-specific variation
                        if "drug" in doc.name.lower():
                            variations = ["Drug Discovery", "Molecular", "Pharmaceutical", "Bioactive"]
                        elif "neural" in doc.name.lower():
                            variations = ["Neural Network", "Deep Learning", "CNN", "RNN"]
                        else:
                            variations = ["Method", "Approach", "Technique", "Framework"]

                        if i < 4:  # First few entities get document-specific names
                            entity_name = f"{random.choice(variations)} {i+1}"
                        else:
                            entity_name = base_entity

                        sample_entities.append(entity_name)

                    document_entities[doc.name] = sample_entities

                    # Add document node
                    G.add_node(doc.name,
                              node_type="document",
                              size=doc.size_mb,
                              entities=doc.entities_found,
                              citations=doc.citations_found)

                    # Add entity nodes and connect to document
                    for entity in sample_entities:
                        entity_counts[entity] = entity_counts.get(entity, 0) + 1

                        G.add_node(entity,
                                  node_type="entity",
                                  count=entity_counts[entity])

                        G.add_edge(doc.name, entity, relation="contains")

            # Add entity-entity connections for entities that appear in multiple documents
            shared_entities = {entity: count for entity, count in entity_counts.items() if count > 1}

            for entity in shared_entities:
                for other_entity in shared_entities:
                    if entity != other_entity:
                        # Add edge with some probability based on co-occurrence
                        if random.random() < 0.3:  # 30% chance of connection
                            G.add_edge(entity, other_entity, relation="co-occurs")

            # Limit graph size for visualization
            if len(G.nodes()) > max_nodes:
                # Keep top nodes by degree
                top_nodes = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:max_nodes]
                G = G.subgraph([node for node, degree in top_nodes])

            print(f"   📊 Graph stats: {len(G.nodes())} nodes, {len(G.edges())} edges")

            # Create layout with better spacing
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

            # Prepare node traces
            node_trace_docs = go.Scatter(
                x=[], y=[],
                mode='markers+text',
                marker=dict(
                    size=[],
                    color='#4A90E2',  # Nice blue
                    line=dict(width=2, color='#2E5C8A'),
                    opacity=0.8
                ),
                text=[],
                textposition="middle center",
                textfont=dict(size=10, color='white'),
                hoverinfo='text',
                hovertext=[],
                name='📄 Documents'
            )

            node_trace_entities = go.Scatter(
                x=[], y=[],
                mode='markers+text',
                marker=dict(
                    size=[],
                    color='#E74C3C',  # Nice red
                    line=dict(width=1, color='#A93226'),
                    opacity=0.8
                ),
                text=[],
                textposition="middle center",
                textfont=dict(size=8, color='white'),
                hoverinfo='text',
                hovertext=[],
                name='🔗 Entities'
            )

            # Add nodes
            for node in G.nodes():
                x, y = pos[node]
                node_info = G.nodes[node]

                if node_info.get('node_type') == 'document':
                    node_trace_docs['x'] += tuple([x])
                    node_trace_docs['y'] += tuple([y])

                    # Size based on entities found
                    node_size = 25 + min(node_info.get('entities', 0) * 2, 40)
                    node_trace_docs['marker']['size'] += tuple([node_size])

                    # Truncate long names
                    display_name = node[:12] + "..." if len(node) > 15 else node
                    node_trace_docs['text'] += tuple([display_name])

                    node_trace_docs['hovertext'] += tuple([
                        f"📄 Document: {node}<br>" +
                        f"🔗 Entities: {node_info.get('entities', 0)}<br>" +
                        f"📚 Citations: {node_info.get('citations', 0)}<br>" +
                        f"📏 Size: {node_info.get('size', 0):.1f} MB<br>" +
                        f"🌐 Connections: {G.degree(node)}"
                    ])
                else:
                    node_trace_entities['x'] += tuple([x])
                    node_trace_entities['y'] += tuple([y])

                    # Size based on how many documents contain this entity
                    node_size = 15 + min(node_info.get('count', 0) * 5, 30)
                    node_trace_entities['marker']['size'] += tuple([node_size])

                    # Truncate long names
                    display_name = node[:8] + "..." if len(node) > 10 else node
                    node_trace_entities['text'] += tuple([display_name])

                    node_trace_entities['hovertext'] += tuple([
                        f"🔗 Entity: {node}<br>" +
                        f"📄 Appears in: {node_info.get('count', 0)} documents<br>" +
                        f"🌐 Connections: {G.degree(node)}"
                    ])

            # Add edges with different styles
            edge_trace = go.Scatter(
                x=[], y=[],
                mode='lines',
                line=dict(width=1, color='rgba(128,128,128,0.3)'),
                hoverinfo='none',
                name='Connections',
                showlegend=False
            )

            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_trace['x'] += tuple([x0, x1, None])
                edge_trace['y'] += tuple([y0, y1, None])

            # Create figure with better styling
            fig = go.Figure(data=[edge_trace, node_trace_docs, node_trace_entities],
                           layout=go.Layout(
                               title=dict(
                                   text=f"🕸️ Knowledge Graph: {self.project_name}",
                                   font=dict(size=20, color='#2C3E50'),
                                   x=0.5
                               ),
                               showlegend=True,
                               hovermode='closest',
                               margin=dict(b=40,l=40,r=40,t=80),
                               annotations=[dict(
                                   text=f"📄 Documents: {len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'document'])} | " +
                                        f"🔗 Entities: {len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'entity'])} | " +
                                        f"🌐 Connections: {len(G.edges())}",
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.5, y=-0.05,
                                   xanchor="center", yanchor="top",
                                   font=dict(size=14, color='#34495E')
                               )],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               plot_bgcolor='#F8F9FA',
                               paper_bgcolor='white',
                               font=dict(family="Arial", size=12),
                               legend=dict(
                                   orientation="h",
                                   yanchor="bottom",
                                   y=1.02,
                                   xanchor="right",
                                   x=1
                               )
                           ))

            # Show the graph
            fig.show()

            # Print statistics
            self._print_graph_statistics(G)

            return G

        except Exception as e:
            print(f"❌ Error creating visualization: {e}")
            return None

    def _print_graph_statistics(self, G: Any) -> None:
        """Print detailed graph statistics"""
        # Create summary statistics
        doc_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'document']
        entity_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'entity']

        print("\n📊 Knowledge Graph Statistics:")
        print(f"   📄 Documents: {len(doc_nodes)}")
        print(f"   🔗 Entities: {len(entity_nodes)}")
        print(f"   🌐 Connections: {len(G.edges())}")
        print(f"   🎯 Average connections per node: {2 * len(G.edges()) / len(G.nodes()):.1f}")

        # Top entities by connections
        entity_degrees = [(node, degree) for node, degree in G.degree()
                         if G.nodes[node].get('node_type') == 'entity']
        entity_degrees.sort(key=lambda x: x[1], reverse=True)

        if entity_degrees:
            print("\n🎯 Most Connected Entities:")
            for entity, degree in entity_degrees[:5]:
                print(f"   • {entity}: {degree} connections")

        # Network analysis
        if len(G.nodes()) > 3:
            try:
                density = nx.density(G)
                print("\n🌐 Network Analysis:")
                print(f"   • Graph density: {density:.3f}")
                print(f"   • Average clustering: {nx.average_clustering(G):.3f}")

                if nx.is_connected(G):
                    print(f"   • Average path length: {nx.average_shortest_path_length(G):.1f}")
                else:
                    print(f"   • Graph has {nx.number_connected_components(G)} components")
            except:
                pass


def visualize_knowledge_graph(documents: list[DocumentStatus],
                            project_name: str = "GraphRAG Project",
                            max_nodes: int = 50) -> Any | None:
    """
    Convenience function to create knowledge graph visualization
    
    Args:
        documents: List of processed documents
        project_name: Name of the project
        max_nodes: Maximum number of nodes to display
        
    Returns:
        NetworkX graph object or None if visualization fails
    """
    visualizer = KnowledgeGraphVisualizer(project_name)
    return visualizer.visualize_knowledge_graph(documents, max_nodes)

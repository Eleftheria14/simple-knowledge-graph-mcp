"""
Standard Knowledge Graph Visualization using industry-standard libraries
This shows the most common approaches used in research and industry.
"""

import networkx as nx
import matplotlib.pyplot as plt
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class StandardKGVisualizer:
    """
    Standard knowledge graph visualization using NetworkX + multiple output formats.
    This follows industry best practices and standard formats.
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.node_attributes = {}
        self.edge_attributes = {}
    
    def from_langchain_graphrag(self, graph_rag_instance):
        """
        Convert LangChain GraphRAG to standard NetworkX format
        This is the bridge between our custom system and standard visualization
        """
        try:
            # Get all papers and entities
            all_papers = graph_rag_instance.get_all_papers()
            
            for paper in all_papers:
                paper_id = paper.get('paper_id', 'unknown')
                paper_title = paper.get('paper_title', 'Unknown Title')
                
                # Add paper node with standard attributes
                self.graph.add_node(
                    paper_id,
                    label=paper_title[:30] + "...",
                    node_type='paper',
                    size=20,
                    color='#1f77b4'  # Standard blue
                )
                
                # Get entities for this paper
                corpus_doc = graph_rag_instance.export_for_corpus(paper_id)
                if corpus_doc:
                    metadata = corpus_doc.get('metadata', {})
                    
                    # Standard entity type colors (widely used scheme)
                    entity_colors = {
                        'authors': '#ff7f0e',      # Orange
                        'institutions': '#2ca02c',  # Green  
                        'methods': '#d62728',      # Red
                        'concepts': '#9467bd',     # Purple
                        'technologies': '#8c564b', # Brown
                        'datasets': '#e377c2'     # Pink
                    }
                    
                    for entity_type, entities in metadata.items():
                        if entities and entity_type != 'chunk_count':
                            for entity in entities:
                                entity_id = f"{entity_type}:{entity}"
                                
                                # Add entity node with standard attributes
                                self.graph.add_node(
                                    entity_id,
                                    label=entity,
                                    node_type=entity_type,
                                    size=15,
                                    color=entity_colors.get(entity_type, '#gray')
                                )
                                
                                # Add edge with relationship type
                                self.graph.add_edge(
                                    paper_id,
                                    entity_id,
                                    relationship=f"has_{entity_type}",
                                    weight=1.0
                                )
            
            # Add cross-entity connections (standard community detection)
            self._add_entity_connections()
            
            logger.info(f"Standard graph created: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert GraphRAG: {e}")
            return False
    
    def _add_entity_connections(self):
        """Add connections between entities that appear in multiple papers"""
        entity_papers = {}
        
        # Group entities by paper
        for node in self.graph.nodes():
            if self.graph.nodes[node].get('node_type') != 'paper':
                entity_papers[node] = []
                for neighbor in self.graph.neighbors(node):
                    if self.graph.nodes[neighbor].get('node_type') == 'paper':
                        entity_papers[node].append(neighbor)
        
        # Connect entities that share papers
        for entity1, papers1 in entity_papers.items():
            for entity2, papers2 in entity_papers.items():
                if entity1 != entity2 and set(papers1) & set(papers2):
                    if not self.graph.has_edge(entity1, entity2):
                        self.graph.add_edge(entity1, entity2, 
                                          relationship="co_occurs",
                                          weight=len(set(papers1) & set(papers2)))
    
    def visualize_matplotlib(self, figsize=(12, 8), layout='spring'):
        """
        Standard matplotlib visualization - most common academic approach
        """
        try:
            plt.figure(figsize=figsize)
            
            # Choose layout algorithm (standard options)
            if layout == 'spring':
                pos = nx.spring_layout(self.graph, k=1, iterations=50)
            elif layout == 'circular':
                pos = nx.circular_layout(self.graph)
            elif layout == 'kamada_kawai':
                pos = nx.kamada_kawai_layout(self.graph)
            else:
                pos = nx.spring_layout(self.graph)
            
            # Extract node attributes for visualization
            node_colors = [self.graph.nodes[node].get('color', '#gray') for node in self.graph.nodes()]
            node_sizes = [self.graph.nodes[node].get('size', 10) * 20 for node in self.graph.nodes()]  # Scale for matplotlib
            
            # Draw graph with standard styling
            nx.draw_networkx_nodes(self.graph, pos, 
                                 node_color=node_colors, 
                                 node_size=node_sizes, 
                                 alpha=0.8)
            
            nx.draw_networkx_edges(self.graph, pos, 
                                 alpha=0.3, 
                                 edge_color='gray',
                                 width=1)
            
            # Labels for papers only (standard practice for readability)
            paper_nodes = [n for n in self.graph.nodes() if self.graph.nodes[n].get('node_type') == 'paper']
            paper_labels = {n: self.graph.nodes[n].get('label', n) for n in paper_nodes}
            
            nx.draw_networkx_labels(self.graph, pos, paper_labels, font_size=8)
            
            plt.title("Knowledge Graph - Standard NetworkX Visualization", size=16)
            plt.axis('off')
            plt.tight_layout()
            plt.show()
            
            return True
            
        except Exception as e:
            logger.error(f"Matplotlib visualization failed: {e}")
            return False
    
    def export_to_gephi(self, filename="knowledge_graph.gexf"):
        """
        Export to GEXF format - standard for Gephi (most common academic tool)
        """
        try:
            nx.write_gexf(self.graph, filename)
            logger.info(f"Graph exported to Gephi format: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Gephi export failed: {e}")
            return None
    
    def export_to_cytoscape(self, filename="knowledge_graph.json"):
        """
        Export to Cytoscape.js format - standard for web applications
        """
        try:
            # Convert to Cytoscape.js format
            cytoscape_data = {
                "elements": {
                    "nodes": [],
                    "edges": []
                }
            }
            
            # Add nodes
            for node in self.graph.nodes(data=True):
                node_id, attributes = node
                cytoscape_data["elements"]["nodes"].append({
                    "data": {
                        "id": node_id,
                        "label": attributes.get('label', node_id),
                        "type": attributes.get('node_type', 'unknown'),
                        "color": attributes.get('color', '#gray'),
                        "size": attributes.get('size', 10)
                    }
                })
            
            # Add edges
            for edge in self.graph.edges(data=True):
                source, target, attributes = edge
                cytoscape_data["elements"]["edges"].append({
                    "data": {
                        "id": f"{source}-{target}",
                        "source": source,
                        "target": target,
                        "relationship": attributes.get('relationship', 'connected'),
                        "weight": attributes.get('weight', 1.0)
                    }
                })
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(cytoscape_data, f, indent=2)
            
            logger.info(f"Graph exported to Cytoscape format: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Cytoscape export failed: {e}")
            return None
    
    def export_to_d3(self, filename="knowledge_graph_d3.json"):
        """
        Export to D3.js format - standard for custom web visualizations
        """
        try:
            # Convert to D3.js node-link format
            d3_data = {
                "nodes": [],
                "links": []
            }
            
            # Create node index mapping
            node_list = list(self.graph.nodes())
            node_index = {node: i for i, node in enumerate(node_list)}
            
            # Add nodes
            for node in self.graph.nodes(data=True):
                node_id, attributes = node
                d3_data["nodes"].append({
                    "id": node_id,
                    "name": attributes.get('label', node_id),
                    "group": attributes.get('node_type', 'unknown'),
                    "color": attributes.get('color', '#gray'),
                    "size": attributes.get('size', 10)
                })
            
            # Add links
            for edge in self.graph.edges(data=True):
                source, target, attributes = edge
                d3_data["links"].append({
                    "source": node_index[source],
                    "target": node_index[target],
                    "relationship": attributes.get('relationship', 'connected'),
                    "value": attributes.get('weight', 1.0)
                })
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(d3_data, f, indent=2)
            
            logger.info(f"Graph exported to D3.js format: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"D3.js export failed: {e}")
            return None
    
    def create_interactive_plotly(self):
        """
        Create interactive Plotly visualization - modern standard for dashboards
        """
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            
            # Get layout positions
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
            
            # Prepare node data
            node_x = []
            node_y = []
            node_text = []
            node_colors = []
            node_sizes = []
            
            for node in self.graph.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                attributes = self.graph.nodes[node]
                node_text.append(f"{attributes.get('label', node)}<br>Type: {attributes.get('node_type', 'unknown')}")
                node_colors.append(attributes.get('color', '#gray'))
                node_sizes.append(attributes.get('size', 10))
            
            # Prepare edge data
            edge_x = []
            edge_y = []
            
            for edge in self.graph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            # Create traces
            edge_trace = go.Scatter(x=edge_x, y=edge_y,
                                  line=dict(width=1, color='#888'),
                                  hoverinfo='none',
                                  mode='lines')
            
            node_trace = go.Scatter(x=node_x, y=node_y,
                                  mode='markers',
                                  hoverinfo='text',
                                  text=node_text,
                                  marker=dict(size=node_sizes,
                                            color=node_colors,
                                            line=dict(width=2, color='white')))
            
            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(
                                title='Interactive Knowledge Graph - Plotly Standard',
                                titlefont_size=16,
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20,l=5,r=5,t=40),
                                annotations=[ dict(
                                    text="Drag nodes to rearrange | Hover for details",
                                    showarrow=False,
                                    xref="paper", yref="paper",
                                    x=0.005, y=-0.002,
                                    xanchor='left', yanchor='bottom',
                                    font=dict(color="gray", size=12)
                                )],
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                          )
            
            fig.show()
            return fig
            
        except ImportError:
            logger.warning("Plotly not available - install with: pip install plotly")
            return None
        except Exception as e:
            logger.error(f"Plotly visualization failed: {e}")
            return None
    
    def get_graph_metrics(self):
        """
        Standard graph analysis metrics used in research
        """
        metrics = {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "connected_components": nx.number_connected_components(self.graph),
            "average_clustering": nx.average_clustering(self.graph),
            "diameter": nx.diameter(self.graph) if nx.is_connected(self.graph) else "Not connected"
        }
        
        # Centrality measures (standard in network analysis)
        if self.graph.number_of_nodes() > 0:
            degree_centrality = nx.degree_centrality(self.graph)
            betweenness_centrality = nx.betweenness_centrality(self.graph)
            
            metrics["most_central_degree"] = max(degree_centrality, key=degree_centrality.get)
            metrics["most_central_betweenness"] = max(betweenness_centrality, key=betweenness_centrality.get)
        
        return metrics


# Example usage and integration
def create_standard_visualization(graph_rag_instance):
    """
    Create standard knowledge graph visualization from our GraphRAG system
    This is the recommended way to visualize knowledge graphs
    """
    print("🎯 Creating Standard Knowledge Graph Visualization")
    print("=" * 50)
    
    # Initialize standard visualizer
    viz = StandardKGVisualizer()
    
    # Convert our GraphRAG to standard format
    if viz.from_langchain_graphrag(graph_rag_instance):
        print("✅ Successfully converted to standard NetworkX format")
        
        # Show standard metrics
        metrics = viz.get_graph_metrics()
        print(f"\n📊 Standard Graph Metrics:")
        for key, value in metrics.items():
            print(f"   • {key}: {value}")
        
        # Create standard matplotlib visualization
        print(f"\n🎨 Creating standard matplotlib visualization...")
        viz.visualize_matplotlib()
        
        # Export to standard formats
        print(f"\n📁 Exporting to standard formats:")
        
        gephi_file = viz.export_to_gephi()
        if gephi_file:
            print(f"   ✅ Gephi (GEXF): {gephi_file}")
        
        cytoscape_file = viz.export_to_cytoscape()
        if cytoscape_file:
            print(f"   ✅ Cytoscape.js: {cytoscape_file}")
        
        d3_file = viz.export_to_d3()
        if d3_file:
            print(f"   ✅ D3.js: {d3_file}")
        
        # Try interactive Plotly
        print(f"\n🚀 Creating interactive Plotly visualization...")
        plotly_fig = viz.create_interactive_plotly()
        if plotly_fig:
            print(f"   ✅ Interactive Plotly graph displayed above")
        
        return viz
    else:
        print("❌ Failed to convert GraphRAG to standard format")
        return None


if __name__ == "__main__":
    print("Standard Knowledge Graph Visualization Library")
    print("Uses industry-standard formats and practices")
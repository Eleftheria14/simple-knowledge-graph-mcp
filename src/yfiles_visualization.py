"""
yFiles Jupyter Graphs Integration for GraphRAG
Professional-grade graph visualization for knowledge graphs
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import json

logger = logging.getLogger(__name__)

class YFilesGraphRAGVisualizer:
    """
    Professional yFiles visualization for GraphRAG systems.
    Provides enterprise-grade interactive graph exploration.
    """
    
    def __init__(self):
        self.widget = None
        self.graph_data = None
        
    def visualize_graphrag(self, graph_rag_instance, 
                          title: str = "Knowledge Graph",
                          enable_sidebar: bool = True,
                          enable_search: bool = True,
                          enable_neighborhood: bool = True,
                          max_distance: int = 2):
        """
        Create yFiles visualization from GraphRAG instance
        
        Args:
            graph_rag_instance: LangChainGraphRAG instance
            title: Graph title
            enable_sidebar: Show data investigation sidebar
            enable_search: Enable node/edge search
            enable_neighborhood: Enable neighborhood highlighting
            max_distance: Maximum neighborhood distance
            
        Returns:
            GraphWidget instance or None if failed
        """
        try:
            from yfiles_jupyter_graphs import GraphWidget
            
            # Convert GraphRAG to yFiles format
            nodes, edges = self._convert_graphrag_to_yfiles(graph_rag_instance)
            
            if not nodes:
                logger.warning("No nodes found for visualization")
                return None
            
            # Create graph data structure
            self.graph_data = {'nodes': nodes, 'edges': edges}
            
            # Create yFiles widget
            self.widget = GraphWidget(graph=self.graph_data)
            
            # Configure professional features
            if enable_sidebar:
                self.widget.set_sidebar(enabled=True, start_with='Data')
            
            if enable_search:
                self.widget.search(enabled=True)
            
            if enable_neighborhood:
                self.widget.neighborhood(enabled=True, max_distance=max_distance)
            
            # Enable overview panel
            self.widget.overview(enabled=True)
            
            # Set professional styling
            self._configure_professional_styling()
            
            logger.info(f"✅ yFiles visualization created: {len(nodes)} nodes, {len(edges)} edges")
            return self.widget
            
        except ImportError:
            logger.warning("yFiles Jupyter Graphs not installed. Install with: pip install yfiles_jupyter_graphs")
            return None
        except Exception as e:
            logger.error(f"yFiles visualization failed: {e}")
            return None
    
    def _convert_graphrag_to_yfiles(self, graph_rag_instance) -> Tuple[List[Dict], List[Dict]]:
        """Convert GraphRAG data to yFiles nodes and edges format"""
        
        nodes = []
        edges = []
        node_positions = {}
        
        try:
            # Get all papers from GraphRAG
            all_papers = graph_rag_instance.get_all_papers()
            
            if not all_papers:
                logger.warning("No papers found in GraphRAG instance")
                return [], []
            
            # Track entities across papers for cross-connections
            entity_papers = {}
            
            # Process each paper
            for i, paper in enumerate(all_papers):
                paper_id = paper.get('paper_id', f'paper_{i}')
                paper_title = paper.get('paper_title', 'Unknown Title')
                
                # Create paper node with enhanced properties
                paper_node = {
                    'id': paper_id,
                    'properties': {
                        'label': paper_title[:40] + "..." if len(paper_title) > 40 else paper_title,
                        'type': 'paper',
                        'full_title': paper_title,
                        'chunk_count': paper.get('chunk_count', 0),
                        'authors': ', '.join(paper.get('authors', [])),
                        'description': f"Research Paper: {paper_title}",
                        'size': 30,
                        'color': '#2E86C1',  # Professional blue
                        'shape': 'rectangle'
                    }
                }
                nodes.append(paper_node)
                
                # Get detailed paper data for entities
                corpus_doc = graph_rag_instance.export_for_corpus(paper_id)
                if not corpus_doc:
                    continue
                
                metadata = corpus_doc.get('metadata', {})
                
                # Process each entity type
                for entity_type, entities in metadata.items():
                    if not entities or entity_type == 'chunk_count':
                        continue
                    
                    for entity in entities:
                        if not entity:
                            continue
                        
                        entity_id = f"{entity_type}:{entity}"
                        
                        # Track which papers contain this entity
                        if entity_id not in entity_papers:
                            entity_papers[entity_id] = []
                        entity_papers[entity_id].append(paper_id)
                        
                        # Create entity node if not exists
                        if not any(node['id'] == entity_id for node in nodes):
                            entity_node = {
                                'id': entity_id,
                                'properties': {
                                    'label': entity[:25] + "..." if len(entity) > 25 else entity,
                                    'type': entity_type,
                                    'full_name': entity,
                                    'entity_type': entity_type,
                                    'description': f"{entity_type.title()}: {entity}",
                                    'size': 20,
                                    'color': self._get_entity_color(entity_type),
                                    'shape': 'ellipse'
                                }
                            }
                            nodes.append(entity_node)
                        
                        # Create edge from paper to entity
                        edge = {
                            'start': paper_id,
                            'end': entity_id,
                            'properties': {
                                'relationship': f'has_{entity_type}',
                                'type': 'contains',
                                'description': f"Paper contains {entity_type}: {entity}"
                            }
                        }
                        edges.append(edge)
            
            # Add cross-entity connections for entities appearing in multiple papers
            for entity_id, paper_list in entity_papers.items():
                if len(paper_list) > 1:
                    # This entity appears in multiple papers - creates research connections
                    for other_entity, other_papers in entity_papers.items():
                        if (entity_id != other_entity and 
                            len(set(paper_list) & set(other_papers)) > 0):
                            # Entities share papers - add connection
                            if not any(e['start'] == entity_id and e['end'] == other_entity for e in edges):
                                cross_edge = {
                                    'start': entity_id,
                                    'end': other_entity,
                                    'properties': {
                                        'relationship': 'co_occurs',
                                        'type': 'cross_paper',
                                        'shared_papers': len(set(paper_list) & set(other_papers)),
                                        'description': f"Co-occurs in {len(set(paper_list) & set(other_papers))} papers"
                                    }
                                }
                                edges.append(cross_edge)
            
            logger.info(f"Converted GraphRAG: {len(nodes)} nodes, {len(edges)} edges")
            return nodes, edges
            
        except Exception as e:
            logger.error(f"GraphRAG conversion failed: {e}")
            return [], []
    
    def _get_entity_color(self, entity_type: str) -> str:
        """Get professional color scheme for entity types"""
        colors = {
            'authors': '#E74C3C',      # Red
            'institutions': '#F39C12', # Orange
            'methods': '#9B59B6',      # Purple
            'concepts': '#1ABC9C',     # Teal
            'technologies': '#34495E', # Dark blue-gray
            'datasets': '#16A085',     # Dark teal
            'metrics': '#8E44AD'       # Dark purple
        }
        return colors.get(entity_type, '#95A5A6')  # Default gray
    
    def _configure_professional_styling(self):
        """Configure professional yFiles styling"""
        if not self.widget:
            return
        
        try:
            # Set professional layout
            self.widget.set_layout('hierarchic')
            
            # Configure node styling based on type
            def node_color_mapping(node):
                return node['properties'].get('color', '#95A5A6')
            
            def node_size_mapping(node):
                return node['properties'].get('size', 20)
            
            def node_shape_mapping(node):
                return node['properties'].get('shape', 'ellipse')
            
            # Apply styling
            self.widget.node_color_mapping = node_color_mapping
            self.widget.node_size_mapping = node_size_mapping
            
            # Configure edge styling
            def edge_color_mapping(edge):
                edge_type = edge['properties'].get('type', 'default')
                if edge_type == 'contains':
                    return '#BDC3C7'  # Light gray for paper-entity connections
                elif edge_type == 'cross_paper':
                    return '#E67E22'  # Orange for cross-paper connections
                return '#95A5A6'  # Default gray
            
            self.widget.edge_color_mapping = edge_color_mapping
            
            logger.info("Professional styling applied")
            
        except Exception as e:
            logger.warning(f"Styling configuration failed: {e}")
    
    def export_to_formats(self, base_filename: str = "knowledge_graph") -> Dict[str, str]:
        """
        Export graph to multiple standard formats
        
        Returns:
            Dict of format -> filename mappings
        """
        if not self.graph_data:
            logger.warning("No graph data to export")
            return {}
        
        exported_files = {}
        
        try:
            # Export to GraphML (standard format)
            graphml_file = f"{base_filename}.graphml"
            self._export_to_graphml(graphml_file)
            exported_files['graphml'] = graphml_file
            
            # Export to JSON for web applications
            json_file = f"{base_filename}.json"
            with open(json_file, 'w') as f:
                json.dump(self.graph_data, f, indent=2)
            exported_files['json'] = json_file
            
            # Export to Cytoscape format
            cytoscape_file = f"{base_filename}_cytoscape.json"
            self._export_to_cytoscape(cytoscape_file)
            exported_files['cytoscape'] = cytoscape_file
            
            logger.info(f"Exported to formats: {list(exported_files.keys())}")
            return exported_files
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return exported_files
    
    def _export_to_graphml(self, filename: str):
        """Export to GraphML format for Gephi/yEd"""
        try:
            import xml.etree.ElementTree as ET
            
            # Create GraphML structure
            root = ET.Element("graphml")
            root.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
            
            # Define attributes
            for attr_id, attr_info in [
                ("label", {"for": "node", "type": "string"}),
                ("type", {"for": "node", "type": "string"}),
                ("color", {"for": "node", "type": "string"}),
                ("relationship", {"for": "edge", "type": "string"})
            ]:
                key_elem = ET.SubElement(root, "key")
                key_elem.set("id", attr_id)
                key_elem.set("for", attr_info["for"])
                key_elem.set("attr.name", attr_id)
                key_elem.set("attr.type", attr_info["type"])
            
            # Create graph
            graph_elem = ET.SubElement(root, "graph")
            graph_elem.set("id", "knowledge_graph")
            graph_elem.set("edgedefault", "undirected")
            
            # Add nodes
            for node in self.graph_data['nodes']:
                node_elem = ET.SubElement(graph_elem, "node")
                node_elem.set("id", node['id'])
                
                for attr_name, attr_value in node['properties'].items():
                    if attr_name in ['label', 'type', 'color']:
                        data_elem = ET.SubElement(node_elem, "data")
                        data_elem.set("key", attr_name)
                        data_elem.text = str(attr_value)
            
            # Add edges
            for i, edge in enumerate(self.graph_data['edges']):
                edge_elem = ET.SubElement(graph_elem, "edge")
                edge_elem.set("id", f"e{i}")
                edge_elem.set("source", edge['start'])
                edge_elem.set("target", edge['end'])
                
                if 'relationship' in edge['properties']:
                    data_elem = ET.SubElement(edge_elem, "data")
                    data_elem.set("key", "relationship")
                    data_elem.text = edge['properties']['relationship']
            
            # Write to file
            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            
        except Exception as e:
            logger.error(f"GraphML export failed: {e}")
    
    def _export_to_cytoscape(self, filename: str):
        """Export to Cytoscape.js format"""
        try:
            cytoscape_data = {
                "elements": {
                    "nodes": [
                        {
                            "data": {
                                "id": node['id'],
                                **node['properties']
                            }
                        }
                        for node in self.graph_data['nodes']
                    ],
                    "edges": [
                        {
                            "data": {
                                "id": f"{edge['start']}-{edge['end']}",
                                "source": edge['start'],
                                "target": edge['end'],
                                **edge['properties']
                            }
                        }
                        for edge in self.graph_data['edges']
                    ]
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(cytoscape_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Cytoscape export failed: {e}")


def create_yfiles_visualization(graph_rag_instance, 
                               title: str = "GraphRAG Knowledge Graph",
                               **kwargs):
    """
    Convenience function to create yFiles visualization
    
    Args:
        graph_rag_instance: LangChainGraphRAG instance
        title: Graph title
        **kwargs: Additional configuration options
        
    Returns:
        Tuple of (widget, visualizer) or (None, None) if failed
    """
    visualizer = YFilesGraphRAGVisualizer()
    widget = visualizer.visualize_graphrag(graph_rag_instance, title=title, **kwargs)
    
    if widget:
        print(f"✅ yFiles visualization created!")
        print(f"🎯 Professional features enabled:")
        print(f"   • Data investigation sidebar")
        print(f"   • Interactive search")
        print(f"   • Neighborhood highlighting")
        print(f"   • Overview panel")
        print(f"   • Professional layouts")
        return widget, visualizer
    else:
        print(f"❌ yFiles visualization failed")
        print(f"💡 Install with: pip install yfiles_jupyter_graphs")
        return None, None


if __name__ == "__main__":
    print("yFiles GraphRAG Visualizer")
    print("Professional graph visualization for knowledge graphs")
    print("Requires: pip install yfiles_jupyter_graphs")
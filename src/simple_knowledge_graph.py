"""
Simple Knowledge Graph for Scientific Papers
Creates basic entity relationships and visualizations for one paper at a time.
"""

import json
import networkx as nx
from typing import Dict, List, Tuple, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

logger = logging.getLogger(__name__)


class SimpleKnowledgeGraph:
    """
    Simple knowledge graph builder for a single scientific paper.
    Extracts entities and relationships, creates NetworkX graph.
    """
    
    def __init__(self, llm_model: str = "llama3.1:8b"):
        """Initialize the knowledge graph system"""
        self.llm = ChatOllama(
            model=llm_model,
            temperature=0.1,
            num_ctx=32768,
            num_predict=2048
        )
        
        self.graph = nx.Graph()
        self.entities = {}
        self.relationships = []
        
        logger.info("🕸️ SimpleKnowledgeGraph initialized")
    
    def extract_entities_and_relationships(self, paper_content: str, 
                                         paper_title: str = "") -> Dict:
        """
        Extract entities and their relationships from paper content
        
        Args:
            paper_content: Full text of the paper
            paper_title: Title of the paper
            
        Returns:
            Dict with entities and relationships
        """
        logger.info("🔍 Extracting entities and relationships...")
        
        # Use first 4000 characters to avoid token limits
        content_sample = paper_content[:4000]
        
        # Extract entities first
        entities = self._extract_entities(content_sample, paper_title)
        
        # Extract relationships between entities
        relationships = self._extract_relationships(content_sample, entities)
        
        # Build NetworkX graph
        self._build_graph(entities, relationships)
        
        result = {
            'entities': entities,
            'relationships': relationships,
            'graph_stats': {
                'nodes': self.graph.number_of_nodes(),
                'edges': self.graph.number_of_edges()
            }
        }
        
        logger.info(f"✅ Extracted {len(entities)} entities, {len(relationships)} relationships")
        return result
    
    def _extract_entities(self, content: str, title: str) -> Dict:
        """Extract entities using LLM"""
        
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
                self.entities = entities
                return entities
            else:
                logger.warning("⚠️ Could not extract valid JSON for entities")
                return self._fallback_entities(title)
                
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            return self._fallback_entities(title)
    
    def _extract_relationships(self, content: str, entities: Dict) -> List[Dict]:
        """Extract relationships between entities"""
        
        # Create a flat list of all entities for relationship extraction
        all_entities = []
        for category, entity_list in entities.items():
            if isinstance(entity_list, list):
                all_entities.extend(entity_list)
            elif isinstance(entity_list, str):
                all_entities.append(entity_list)
        
        if len(all_entities) < 2:
            return []
        
        relationship_prompt = ChatPromptTemplate.from_template("""
Identify relationships between entities mentioned in this scientific paper content.

Entities: {entities}

Return ONLY a JSON array of relationships:
[
  {{"source": "Entity 1", "target": "Entity 2", "relationship": "uses"}},
  {{"source": "Entity 3", "target": "Entity 4", "relationship": "improves"}},
  {{"source": "Entity 5", "target": "Entity 6", "relationship": "evaluates_on"}}
]

Relationship types: uses, improves, evaluates_on, compared_with, based_on, cites, developed_by

Content:
{content}

JSON:""")
        
        try:
            chain = relationship_prompt | self.llm | StrOutputParser()
            result = chain.invoke({
                "entities": ", ".join(all_entities[:10]),  # Limit to first 10 entities
                "content": content
            })
            
            # Extract JSON array
            json_start = result.find('[')
            json_end = result.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                relationships = json.loads(json_str)
                
                # Validate relationships
                valid_relationships = []
                for rel in relationships:
                    if (isinstance(rel, dict) and 
                        'source' in rel and 'target' in rel and 'relationship' in rel):
                        valid_relationships.append(rel)
                
                self.relationships = valid_relationships
                return valid_relationships
            else:
                logger.warning("⚠️ Could not extract valid JSON for relationships")
                return []
                
        except Exception as e:
            logger.error(f"❌ Relationship extraction failed: {e}")
            return []
    
    def _build_graph(self, entities: Dict, relationships: List[Dict]):
        """Build NetworkX graph from entities and relationships"""
        
        # Clear existing graph
        self.graph.clear()
        
        # Add entity nodes with categories
        for category, entity_list in entities.items():
            if isinstance(entity_list, list):
                for entity in entity_list:
                    self.graph.add_node(entity, category=category)
            elif isinstance(entity_list, str):
                self.graph.add_node(entity_list, category=category)
        
        # Add relationship edges
        for rel in relationships:
            source = rel.get('source', '')
            target = rel.get('target', '')
            relationship_type = rel.get('relationship', 'related_to')
            
            if source and target and source in self.graph and target in self.graph:
                self.graph.add_edge(source, target, relationship=relationship_type)
    
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
    
    def get_graph_summary(self) -> Dict:
        """Get summary of the knowledge graph"""
        if self.graph.number_of_nodes() == 0:
            return {"error": "No graph built. Run extract_entities_and_relationships() first."}
        
        # Calculate graph statistics
        nodes_by_category = {}
        for node, data in self.graph.nodes(data=True):
            category = data.get('category', 'unknown')
            nodes_by_category[category] = nodes_by_category.get(category, 0) + 1
        
        # Find most connected nodes
        degree_centrality = nx.degree_centrality(self.graph)
        top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'nodes_by_category': nodes_by_category,
            'most_connected': [{'node': node, 'connections': degree} for node, degree in top_nodes],
            'graph_density': nx.density(self.graph)
        }
    
    def get_node_connections(self, node_name: str) -> Dict:
        """Get connections for a specific node"""
        if node_name not in self.graph:
            return {"error": f"Node '{node_name}' not found in graph"}
        
        neighbors = list(self.graph.neighbors(node_name))
        connections = []
        
        for neighbor in neighbors:
            edge_data = self.graph.get_edge_data(node_name, neighbor)
            relationship = edge_data.get('relationship', 'related_to') if edge_data else 'related_to'
            connections.append({
                'target': neighbor,
                'relationship': relationship,
                'category': self.graph.nodes[neighbor].get('category', 'unknown')
            })
        
        return {
            'node': node_name,
            'category': self.graph.nodes[node_name].get('category', 'unknown'),
            'connections': connections,
            'total_connections': len(connections)
        }
    
    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find shortest path between two entities"""
        if source not in self.graph or target not in self.graph:
            return None
        
        try:
            path = nx.shortest_path(self.graph, source, target)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_subgraph(self, center_node: str, radius: int = 1) -> Dict:
        """Get subgraph around a central node"""
        if center_node not in self.graph:
            return {"error": f"Node '{center_node}' not found"}
        
        # Get nodes within radius
        nodes_in_radius = set([center_node])
        current_nodes = set([center_node])
        
        for _ in range(radius):
            next_nodes = set()
            for node in current_nodes:
                next_nodes.update(self.graph.neighbors(node))
            nodes_in_radius.update(next_nodes)
            current_nodes = next_nodes
        
        # Create subgraph
        subgraph = self.graph.subgraph(nodes_in_radius)
        
        return {
            'center_node': center_node,
            'radius': radius,
            'nodes': list(subgraph.nodes()),
            'edges': list(subgraph.edges()),
            'node_count': subgraph.number_of_nodes(),
            'edge_count': subgraph.number_of_edges()
        }
    
    def export_graph_data(self) -> Dict:
        """Export graph data for visualization"""
        nodes = []
        for node, data in self.graph.nodes(data=True):
            nodes.append({
                'id': node,
                'label': node,
                'category': data.get('category', 'unknown'),
                'size': self.graph.degree(node) * 5 + 10  # Size based on connections
            })
        
        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                'source': source,
                'target': target,
                'relationship': data.get('relationship', 'related_to')
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': self.get_graph_summary()
        }


if __name__ == "__main__":
    # Test the knowledge graph system
    print("🧪 Testing SimpleKnowledgeGraph...")
    
    kg = SimpleKnowledgeGraph()
    
    # Test with sample content
    sample_content = """
    This paper presents a review of large language models and autonomous agents in chemistry.
    The authors include Mayk Caldas Ramos, Christopher J. Collison, and Andrew D. White.
    They evaluate transformer architectures like BERT and GPT on chemical datasets.
    The models achieve 89% accuracy on molecular property prediction tasks.
    """
    
    result = kg.extract_entities_and_relationships(sample_content, "LLM Review Paper")
    print("✅ Test completed!")
    print(f"📊 Results: {result['graph_stats']}")
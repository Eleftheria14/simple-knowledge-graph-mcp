"""
Enhanced Knowledge Graph Extraction
Extracts comprehensive knowledge graphs from research papers with more entities and relationships
"""

import json
import logging
import networkx as nx
from typing import Dict, List, Optional, Set
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

logger = logging.getLogger(__name__)

class EnhancedKnowledgeGraph:
    """
    Enhanced Knowledge Graph builder that extracts comprehensive entities and relationships
    from research papers using multiple passes and expanded entity types
    """
    
    def __init__(self, llm_model: str = "llama3.1:8b"):
        """Initialize the enhanced knowledge graph system"""
        self.llm = Ollama(model=llm_model, temperature=0.1)
        self.graph = nx.Graph()
        self.entities = {}
        self.relationships = []
        
        # Expanded entity categories for richer graphs
        self.entity_categories = [
            "authors", "institutions", "methods", "concepts", "technologies",
            "datasets", "metrics", "tools", "frameworks", "algorithms",
            "experiments", "results", "conclusions", "applications", "domains",
            "challenges", "solutions", "innovations", "comparisons", "evaluations"
        ]
        
        logger.info("🕸️ Enhanced Knowledge Graph initialized")
    
    def extract_comprehensive_entities(self, paper_content: str, paper_title: str = "") -> Dict:
        """
        Extract comprehensive entities using multiple content sections
        
        Args:
            paper_content: Full text of the paper
            paper_title: Title of the paper
            
        Returns:
            Dict with comprehensive entities and relationships
        """
        logger.info(f"🔍 Enhanced extraction for: {paper_title}")
        
        # Split paper into sections for comprehensive extraction
        sections = self._split_into_sections(paper_content)
        
        all_entities = {}
        all_relationships = []
        
        # Extract from each section
        for section_name, section_content in sections.items():
            logger.info(f"📖 Processing {section_name} section...")
            
            # Extract entities from this section
            section_entities = self._extract_section_entities(section_content, paper_title, section_name)
            
            # Merge with global entities
            for category, entity_list in section_entities.items():
                if category not in all_entities:
                    all_entities[category] = set()
                all_entities[category].update(entity_list)
            
            # Extract relationships from this section
            section_relationships = self._extract_section_relationships(section_content, section_entities)
            all_relationships.extend(section_relationships)
        
        # Convert sets back to lists
        final_entities = {cat: list(entities) for cat, entities in all_entities.items()}
        
        # Build comprehensive graph
        self._build_comprehensive_graph(final_entities, all_relationships)
        
        result = {
            'entities': final_entities,
            'relationships': all_relationships,
            'graph_stats': {
                'nodes': self.graph.number_of_nodes(),
                'edges': self.graph.number_of_edges(),
                'sections_processed': len(sections)
            }
        }
        
        total_entities = sum(len(entities) for entities in final_entities.values())
        logger.info(f"✅ Enhanced extraction: {total_entities} entities, {len(all_relationships)} relationships")
        
        return result
    
    def _split_into_sections(self, paper_content: str) -> Dict[str, str]:
        """Split paper into logical sections for comprehensive extraction"""
        
        sections = {}
        content_length = len(paper_content)
        
        # Define section boundaries (simple approach - can be enhanced with smarter parsing)
        section_size = 6000  # Larger chunks for better context
        overlap = 1000       # Overlap to catch entities spanning boundaries
        
        current_pos = 0
        section_num = 1
        
        while current_pos < content_length:
            end_pos = min(current_pos + section_size, content_length)
            
            # Try to break at sentence boundaries
            if end_pos < content_length:
                # Look for sentence end in the last 200 characters
                sentence_end = paper_content.rfind('.', end_pos - 200, end_pos)
                if sentence_end > current_pos:
                    end_pos = sentence_end + 1
            
            section_content = paper_content[current_pos:end_pos]
            
            # Skip very short sections
            if len(section_content.strip()) > 500:
                sections[f"section_{section_num}"] = section_content
                section_num += 1
            
            # Move to next section with overlap
            current_pos = end_pos - overlap
            if current_pos >= content_length - overlap:
                break
        
        logger.info(f"📄 Split paper into {len(sections)} sections")
        return sections
    
    def _extract_section_entities(self, content: str, title: str, section_name: str) -> Dict:
        """Extract entities from a specific section with expanded categories"""
        
        entity_prompt = ChatPromptTemplate.from_template("""
Extract comprehensive entities from this section of a scientific paper. Focus on finding MORE entities per category.

Return ONLY a valid JSON object with expanded categories:

{{
  "authors": ["Author Name 1", "Author Name 2", "Author Name 3"],
  "institutions": ["University 1", "Company 1", "Institute 1"],
  "methods": ["Method 1", "Method 2", "Approach 1", "Technique 1"],
  "concepts": ["Concept 1", "Concept 2", "Theory 1", "Idea 1"],
  "technologies": ["Technology 1", "Tool 1", "System 1", "Platform 1"],
  "datasets": ["Dataset 1", "Database 1", "Corpus 1"],
  "metrics": ["Accuracy", "F1-Score", "Performance Metric"],
  "algorithms": ["Algorithm 1", "Model 1", "Neural Network Type"],
  "tools": ["Software Tool", "Library", "Framework"],
  "experiments": ["Experiment 1", "Test 1", "Evaluation 1"],
  "applications": ["Use Case 1", "Application 1", "Domain 1"],
  "challenges": ["Problem 1", "Issue 1", "Limitation 1"],
  "innovations": ["Innovation 1", "Contribution 1", "Novel Approach"]
}}

IMPORTANT:
- Extract 5-15 items per category (more comprehensive than before)
- Include variations and synonyms
- Use exact names from the text
- Focus on the most important entities in this section
- Return valid JSON only

Paper title: {title}
Section: {section_name}

Content:
{content}

JSON:""")
        
        try:
            chain = entity_prompt | self.llm | StrOutputParser()
            result = chain.invoke({
                "content": content, 
                "title": title, 
                "section_name": section_name
            })
            
            # Extract JSON from response
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                entities = json.loads(json_str)
                
                # Clean and validate entities
                cleaned_entities = {}
                for category, entity_list in entities.items():
                    if isinstance(entity_list, list):
                        # Remove duplicates and empty strings
                        cleaned_list = list(set([e.strip() for e in entity_list if e.strip()]))
                        if cleaned_list:
                            cleaned_entities[category] = cleaned_list
                
                return cleaned_entities
            else:
                logger.warning(f"⚠️ Could not extract valid JSON from {section_name}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Entity extraction failed for {section_name}: {e}")
            return {}
    
    def _extract_section_relationships(self, content: str, entities: Dict) -> List[Dict]:
        """Extract relationships between entities in this section"""
        
        # Create flat list of entities for relationship extraction
        all_entities = []
        for category, entity_list in entities.items():
            all_entities.extend(entity_list)
        
        if len(all_entities) < 2:
            return []
        
        # Limit entities for relationship extraction to avoid token limits
        entity_sample = all_entities[:30]  # Top 30 entities
        
        relationship_prompt = ChatPromptTemplate.from_template("""
Identify relationships between entities in this research paper section.

Entities: {entities}

Return ONLY a JSON array of relationships (aim for 10-20 relationships):
[
  {{"source": "Entity 1", "target": "Entity 2", "relationship": "uses"}},
  {{"source": "Entity 3", "target": "Entity 4", "relationship": "improves"}},
  {{"source": "Entity 5", "target": "Entity 6", "relationship": "evaluates_on"}}
]

Relationship types: uses, improves, evaluates_on, compared_with, based_on, cites, developed_by, 
                   implements, extends, applies_to, measures, validates, enables, requires

Focus on the most important relationships mentioned in the text.

Content:
{content}

JSON:""")
        
        try:
            chain = relationship_prompt | self.llm | StrOutputParser()
            result = chain.invoke({
                "entities": ", ".join(entity_sample),
                "content": content[:3000]  # Limit content for relationships
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
                        # Check if entities exist in our extracted entities
                        source_exists = any(rel['source'] in entity_list 
                                          for entity_list in entities.values())
                        target_exists = any(rel['target'] in entity_list 
                                          for entity_list in entities.values())
                        
                        if source_exists and target_exists:
                            valid_relationships.append(rel)
                
                return valid_relationships
            else:
                logger.warning("⚠️ Could not extract valid JSON for relationships")
                return []
                
        except Exception as e:
            logger.error(f"❌ Relationship extraction failed: {e}")
            return []
    
    def _build_comprehensive_graph(self, entities: Dict, relationships: List[Dict]):
        """Build comprehensive NetworkX graph from entities and relationships"""
        
        # Clear existing graph
        self.graph.clear()
        
        # Add entity nodes with categories and enhanced attributes
        for category, entity_list in entities.items():
            for entity in entity_list:
                self.graph.add_node(entity, 
                                   category=category,
                                   type='entity',
                                   importance=1.0)  # Can be enhanced with importance scoring
        
        # Add relationship edges
        for rel in relationships:
            source = rel.get('source', '')
            target = rel.get('target', '')
            relationship_type = rel.get('relationship', 'related_to')
            
            if source and target and source in self.graph and target in self.graph:
                self.graph.add_edge(source, target, 
                                   relationship=relationship_type,
                                   weight=1.0)
        
        # Store entities and relationships
        self.entities = entities
        self.relationships = relationships
        
        logger.info(f"📊 Built graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
    
    def get_comprehensive_summary(self) -> Dict:
        """Get comprehensive summary of the knowledge graph"""
        if self.graph.number_of_nodes() == 0:
            return {"error": "No graph built. Run extract_comprehensive_entities() first."}
        
        # Calculate comprehensive statistics
        nodes_by_category = {}
        for node, data in self.graph.nodes(data=True):
            category = data.get('category', 'unknown')
            nodes_by_category[category] = nodes_by_category.get(category, 0) + 1
        
        # Find most connected nodes (hubs)
        degree_centrality = nx.degree_centrality(self.graph)
        top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Relationship type distribution
        relationship_types = {}
        for _, _, edge_data in self.graph.edges(data=True):
            rel_type = edge_data.get('relationship', 'unknown')
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'nodes_by_category': nodes_by_category,
            'top_connected_entities': [{'entity': node, 'connections': degree} 
                                     for node, degree in top_nodes],
            'relationship_types': relationship_types,
            'graph_density': nx.density(self.graph),
            'connected_components': nx.number_connected_components(self.graph)
        }

def create_enhanced_knowledge_graph(paper_content: str, paper_title: str = "") -> Dict:
    """
    Convenience function to create enhanced knowledge graph
    
    Args:
        paper_content: Full text of the paper
        paper_title: Title of the paper
        
    Returns:
        Enhanced knowledge graph results
    """
    ekg = EnhancedKnowledgeGraph()
    return ekg.extract_comprehensive_entities(paper_content, paper_title)
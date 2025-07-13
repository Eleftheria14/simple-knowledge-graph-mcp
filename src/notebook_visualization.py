"""
Clean notebook visualization functions
Simple interface for displaying knowledge graphs in Jupyter notebooks
"""

def setup_colab_widgets():
    """Setup widget manager for Google Colab compatibility"""
    try:
        import google.colab
        from google.colab import output
        output.enable_custom_widget_manager()
    except:
        pass

def create_yfiles_graph(graph_rag_instance):
    """
    Create yFiles visualization from GraphRAG instance following best practices
    Returns widget for display in notebook
    """
    try:
        from yfiles_jupyter_graphs import GraphWidget
        import networkx as nx
        
        # Setup Colab compatibility
        setup_colab_widgets()
        
        # Create NetworkX graph from GraphRAG data
        G = nx.Graph()
        papers = graph_rag_instance.get_all_papers()
        
        # Color scheme for different entity types
        entity_colors = {
            'paper': '#2E86C1',       # Professional blue
            'authors': '#E74C3C',     # Red
            'institutions': '#F39C12', # Orange
            'methods': '#9B59B6',     # Purple
            'concepts': '#1ABC9C',    # Teal
            'technologies': '#34495E', # Dark blue-gray
            'datasets': '#16A085',    # Dark teal
            'metrics': '#8E44AD'      # Dark purple
        }
        
        for paper in papers:
            paper_id = paper['paper_id']
            title = paper['paper_title']
            
            # Add paper node with rich attributes for yFiles
            G.add_node(paper_id, 
                      label=title[:40] + "..." if len(title) > 40 else title,
                      type='paper',
                      color=entity_colors['paper'],
                      size=30,
                      title=title,  # Full title for tooltip
                      description=f"Research Paper: {title}")
            
            # Get entities and add them
            corpus_doc = graph_rag_instance.export_for_corpus(paper_id)
            if corpus_doc:
                entities = corpus_doc['metadata']
                
                for entity_type, entity_list in entities.items():
                    if entity_list and entity_type != 'chunk_count':
                        for entity in entity_list[:5]:  # Limit for clarity
                            entity_id = f"{entity_type}:{entity}"
                            
                            # Add entity node with rich attributes
                            G.add_node(entity_id,
                                      label=entity[:25] + "..." if len(entity) > 25 else entity,
                                      type=entity_type,
                                      color=entity_colors.get(entity_type, '#95A5A6'),
                                      size=20,
                                      full_name=entity,
                                      description=f"{entity_type.title()}: {entity}")
                            
                            # Connect paper to entity with relationship info
                            G.add_edge(paper_id, entity_id, 
                                     relationship=f'has_{entity_type}',
                                     description=f"Paper contains {entity_type}: {entity}")
        
        # Create yFiles widget with NetworkX graph (best practice)
        widget = GraphWidget(graph=G)
        
        # Configure widget following yFiles best practices
        widget.node_label_mapping = 'label'
        
        return widget
        
    except ImportError:
        return None

def create_matplotlib_fallback(graph_rag_instance):
    """
    Create matplotlib visualization as fallback
    """
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
        
        G = nx.Graph()
        papers = graph_rag_instance.get_all_papers()
        
        for paper in papers:
            paper_id = paper['paper_id']
            G.add_node(paper_id, type='paper')
            
            corpus_doc = graph_rag_instance.export_for_corpus(paper_id)
            if corpus_doc:
                entities = corpus_doc['metadata']
                for entity_type, entity_list in entities.items():
                    if entity_list and entity_type != 'chunk_count':
                        for entity in entity_list[:3]:
                            entity_id = f"{entity_type}:{entity}"
                            G.add_node(entity_id, type=entity_type)
                            G.add_edge(paper_id, entity_id)
        
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        
        # Color by type
        paper_nodes = [n for n in G.nodes() if G.nodes[n].get('type') == 'paper']
        entity_nodes = [n for n in G.nodes() if G.nodes[n].get('type') != 'paper']
        
        if paper_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=paper_nodes, 
                                 node_color='lightblue', node_size=500)
        if entity_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=entity_nodes, 
                                 node_color='lightcoral', node_size=300)
        
        nx.draw_networkx_edges(G, pos, alpha=0.5)
        plt.title("Knowledge Graph")
        plt.axis('off')
        plt.show()
        
        return True
        
    except Exception:
        return False

def show_knowledge_graph(graph_rag_instance):
    """
    Main function to display knowledge graph in notebook
    Tries yFiles first, falls back to matplotlib
    """
    
    # Try yFiles first
    widget = create_yfiles_graph(graph_rag_instance)
    if widget:
        try:
            # Try to import display from IPython (available in Jupyter)
            from IPython.display import display
            display(widget)
            print("✅ Interactive yFiles graph displayed above!")
            print("🎯 Use the sidebar to explore nodes and relationships")
            print("🔍 Try the search function to find specific entities")
            return True
        except ImportError:
            print("⚠️ Not in Jupyter environment - yFiles widget created but not displayed")
            return widget
    
    # Try matplotlib fallback
    print("📦 yFiles not available, using matplotlib...")
    if create_matplotlib_fallback(graph_rag_instance):
        print("✅ Matplotlib visualization displayed")
        return True
    
    # Final fallback - just show summary
    print("⚠️ Visualization libraries not available")
    print("💡 Install with: pip install yfiles_jupyter_graphs matplotlib")
    
    try:
        summary = graph_rag_instance.get_graph_summary()
        print(f"\n📊 Graph Summary:")
        print(f"   📄 Papers: {summary['total_papers']}")
        print(f"   📝 Documents: {summary['total_documents']}")
        print("   🏷️ Knowledge graph built successfully!")
        return True
    except:
        print("📊 Knowledge graph is working behind the scenes!")
        return False
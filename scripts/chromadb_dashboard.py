#!/usr/bin/env python3
"""
ChromaDB Web Dashboard
Creates a simple HTML dashboard to visualize your knowledge graph's vector database.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage.chroma.client import get_shared_chromadb_client
from collections import Counter
import json
import webbrowser
from datetime import datetime

def create_html_dashboard():
    """Create an HTML dashboard for ChromaDB visualization."""
    
    # Get ChromaDB data
    client, collection = get_shared_chromadb_client()
    total_docs = collection.count()
    
    if total_docs == 0:
        print("❌ No documents found in ChromaDB")
        return
    
    # Get all documents with metadata
    results = collection.get(include=['documents', 'metadatas'])
    documents = results['documents']
    metadatas = results['metadatas']
    
    # Analyze data
    types = [meta.get('type', 'unknown') for meta in metadatas]
    sections = [meta.get('section', 'unknown') for meta in metadatas]
    titles = [meta.get('document_title', 'Unknown') for meta in metadatas]
    
    type_counts = Counter(types)
    section_counts = Counter(sections)
    title_counts = Counter(titles)
    
    # Word count analysis
    word_counts = [len(doc.split()) for doc in documents]
    avg_words = sum(word_counts) / len(word_counts)
    
    # Create HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChromaDB Knowledge Graph Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .charts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .chart-container {{ background: white; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; }}
        .documents {{ margin-top: 30px; }}
        .document {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 8px; }}
        .document-title {{ font-weight: bold; color: #495057; }}
        .document-meta {{ color: #6c757d; font-size: 0.9em; margin: 5px 0; }}
        .document-content {{ color: #212529; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 ChromaDB Knowledge Graph Dashboard</h1>
        <p>Chemistry AI Research Papers Analysis</p>
        <p><small>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</small></p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{total_docs}</div>
            <div>Total Chunks</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(title_counts)}</div>
            <div>Source Papers</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{avg_words:.0f}</div>
            <div>Avg Words/Chunk</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(section_counts)}</div>
            <div>Unique Sections</div>
        </div>
    </div>
    
    <div class="charts">
        <div class="chart-container">
            <h3>📊 Content by Section</h3>
            <canvas id="sectionChart"></canvas>
        </div>
        <div class="chart-container">
            <h3>📚 Chunks per Paper</h3>
            <canvas id="paperChart"></canvas>
        </div>
    </div>
    
    <div class="documents">
        <h3>📄 Sample Documents</h3>
    """
    
    # Add sample documents
    for i, (doc, meta) in enumerate(zip(documents[:10], metadatas[:10])):
        section = meta.get('section', 'Unknown')
        title = meta.get('document_title', 'Unknown Document')
        word_count = meta.get('word_count', len(doc.split()))
        
        html_content += f"""
        <div class="document">
            <div class="document-title">Chunk {i+1}</div>
            <div class="document-meta">
                📖 Section: {section} | 📄 Paper: {title[:50]}{'...' if len(title) > 50 else ''} | 📏 {word_count} words
            </div>
            <div class="document-content">{doc[:300]}{'...' if len(doc) > 300 else ''}</div>
        </div>
        """
    
    # Add JavaScript for charts
    section_labels = list(section_counts.keys())
    section_data = list(section_counts.values())
    
    paper_labels = [title[:30] + '...' if len(title) > 30 else title for title in title_counts.keys()]
    paper_data = list(title_counts.values())
    
    html_content += f"""
    </div>
    
    <script>
        // Section distribution chart
        const sectionCtx = document.getElementById('sectionChart').getContext('2d');
        new Chart(sectionCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(section_labels)},
                datasets: [{{
                    data: {json.dumps(section_data)},
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // Papers distribution chart
        const paperCtx = document.getElementById('paperChart').getContext('2d');
        new Chart(paperCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(paper_labels)},
                datasets: [{{
                    label: 'Text Chunks',
                    data: {json.dumps(paper_data)},
                    backgroundColor: '#36A2EB'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """
    
    # Save HTML file
    output_file = '/Users/aimiegarces/Agents/chromadb_dashboard.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard created: {output_file}")
    print(f"🌐 Opening in browser...")
    
    # Open in browser
    webbrowser.open(f'file://{output_file}')
    
    return output_file

if __name__ == "__main__":
    create_html_dashboard()
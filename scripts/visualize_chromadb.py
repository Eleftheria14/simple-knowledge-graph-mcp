#!/usr/bin/env python3
"""
ChromaDB Visualization Tool
Analyzes and visualizes the contents of your knowledge graph's vector database.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage.chroma.client import get_shared_chromadb_client
from collections import Counter
import json

def analyze_chromadb():
    """Analyze ChromaDB contents and generate insights."""
    print("🔍 ChromaDB Knowledge Graph Analysis")
    print("=" * 50)
    
    # Get ChromaDB connection
    client, collection = get_shared_chromadb_client()
    total_docs = collection.count()
    
    print(f"📚 Total Documents: {total_docs}")
    print(f"🆔 Collection ID: {collection.id}")
    print(f"📛 Collection Name: {collection.name}")
    print()
    
    if total_docs == 0:
        print("❌ No documents found in ChromaDB")
        return
    
    # Get all documents with metadata
    results = collection.get(include=['documents', 'metadatas'])
    documents = results['documents']
    metadatas = results['metadatas']
    
    # Analyze document types
    print("📊 Document Analysis:")
    types = [meta.get('type', 'unknown') for meta in metadatas]
    type_counts = Counter(types)
    for doc_type, count in type_counts.most_common():
        percentage = (count / total_docs) * 100
        print(f"   {doc_type}: {count} ({percentage:.1f}%)")
    print()
    
    # Analyze sections
    print("📖 Section Distribution:")
    sections = [meta.get('section', 'unknown') for meta in metadatas]
    section_counts = Counter(sections)
    for section, count in section_counts.most_common():
        percentage = (count / total_docs) * 100
        print(f"   {section}: {count} ({percentage:.1f}%)")
    print()
    
    # Analyze word counts
    print("📏 Content Length Analysis:")
    word_counts = []
    for doc in documents:
        word_count = len(doc.split())
        word_counts.append(word_count)
    
    avg_words = sum(word_counts) / len(word_counts)
    min_words = min(word_counts)
    max_words = max(word_counts)
    
    print(f"   Average words per chunk: {avg_words:.1f}")
    print(f"   Shortest chunk: {min_words} words")
    print(f"   Longest chunk: {max_words} words")
    print()
    
    # Show document titles/sources
    print("📄 Source Documents:")
    titles = set()
    for meta in metadatas:
        title = meta.get('document_title', 'Unknown Document')
        titles.add(title)
    
    for i, title in enumerate(sorted(titles), 1):
        chunks_for_title = sum(1 for meta in metadatas if meta.get('document_title') == title)
        print(f"   {i}. {title} ({chunks_for_title} chunks)")
    print()
    
    # Show sample content from each section
    print("🔍 Sample Content by Section:")
    unique_sections = list(section_counts.keys())[:5]  # Top 5 sections
    
    for section in unique_sections:
        section_docs = [(doc, meta) for doc, meta in zip(documents, metadatas) 
                       if meta.get('section') == section]
        if section_docs:
            doc, meta = section_docs[0]  # First example
            print(f"\n   📖 {section.upper()}:")
            print(f"      {doc[:200]}...")
            if 'word_count' in meta:
                print(f"      Words: {meta['word_count']}")
    
    print("\n" + "=" * 50)
    print("✅ Analysis complete!")

def search_content(query, limit=5):
    """Search ChromaDB content using semantic search."""
    print(f"\n🔍 Searching for: '{query}'")
    print("-" * 30)
    
    from storage.chroma.query import ChromaDBQuery
    query_engine = ChromaDBQuery()
    
    results = query_engine.query_similar_text(query, n_results=limit)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Relevance: {1 - result['distance']:.3f}")
        print(f"   Section: {result.get('metadata', {}).get('section', 'Unknown')}")
        print(f"   Content: {result['text'][:300]}...")

if __name__ == "__main__":
    analyze_chromadb()
    
    # Optional: Interactive search
    print("\n" + "=" * 50)
    while True:
        query = input("\n🔍 Enter search query (or 'quit' to exit): ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break
        if query:
            search_content(query)
        print()
# GraphRAG MCP Tools Reference

This document provides comprehensive documentation for all **MCP tools** available in the GraphRAG MCP Toolkit. These tools enable Claude and other AI assistants to interact with your processed documents through the Model Context Protocol (MCP).

## 🚀 Overview

The GraphRAG MCP Toolkit provides **10+ specialized tools** organized into three categories:

- **Chat Tools** - For conversational exploration and discovery
- **Literature Review Tools** - For formal academic writing with citations
- **Core Tools** - For document management and system control

## 📋 Table of Contents

1. [Chat Tools (Conversational Mode)](#chat-tools-conversational-mode)
2. [Literature Review Tools (Formal Writing Mode)](#literature-review-tools-formal-writing-mode)
3. [Core Tools (Document Management)](#core-tools-document-management)
4. [Usage Examples](#usage-examples)
5. [Claude Desktop Integration](#claude-desktop-integration)
6. [Tool Response Formats](#tool-response-formats)

## 💬 Chat Tools (Conversational Mode)

Tools for natural exploration and discovery. These tools return conversational responses with follow-up suggestions.

### ask_knowledge_graph

**Purpose**: Natural Q&A with the knowledge graph  
**Mode**: Conversational  
**Response**: ChatResponse with follow-up suggestions

```python
# Tool signature
ask_knowledge_graph(query: str) -> ChatResponse

# Example usage in Claude
"Use ask_knowledge_graph to answer: What are the main themes in transformer research?"
```

**Parameters**:
- `query` (string): Natural language question about the research content

**Response Format**:
```json
{
  "answer": "The main themes in transformer research include...",
  "confidence": 0.85,
  "sources_count": 12,
  "related_topics": ["attention mechanisms", "neural networks", "NLP"],
  "follow_up_suggestions": [
    "Would you like to explore attention mechanisms in detail?",
    "Should I find connections between transformers and other architectures?"
  ],
  "entities_mentioned": ["transformer", "attention", "BERT", "GPT"],
  "processing_time": 1.2
}
```

### explore_topic

**Purpose**: Structured topic exploration with different detail levels  
**Mode**: Conversational  
**Response**: TopicExploration with multiple aspects

```python
# Tool signature
explore_topic(topic: str, scope: str = "broad") -> TopicExploration

# Example usage in Claude
"Use explore_topic with topic='machine learning' and scope='detailed'"
```

**Parameters**:
- `topic` (string): Topic to explore
- `scope` (string): "broad", "detailed", or "focused"

**Response Format**:
```json
{
  "topic": "machine learning",
  "overview": "Machine learning is a subset of artificial intelligence...",
  "key_aspects": [
    {
      "aspect": "supervised learning",
      "description": "Learning from labeled data..."
    },
    {
      "aspect": "unsupervised learning", 
      "description": "Finding patterns in unlabeled data..."
    }
  ],
  "relationships": [
    {
      "from": "machine learning",
      "to": "deep learning",
      "relationship": "includes"
    }
  ],
  "gaps_identified": [
    "Limited coverage of reinforcement learning applications"
  ]
}
```

### find_connections

**Purpose**: Discover relationships between concepts  
**Mode**: Conversational  
**Response**: ConnectionAnalysis with relationship details

```python
# Tool signature
find_connections(entity1: str, entity2: str) -> ConnectionAnalysis

# Example usage in Claude
"Use find_connections to explore relationships between 'neural networks' and 'computer vision'"
```

**Parameters**:
- `entity1` (string): First entity/concept
- `entity2` (string): Second entity/concept

**Response Format**:
```json
{
  "entity1": "neural networks",
  "entity2": "computer vision",
  "direct_connections": [
    {
      "relationship": "enables",
      "description": "Neural networks enable advanced computer vision...",
      "strength": 0.9,
      "evidence_count": 15
    }
  ],
  "indirect_connections": [
    {
      "path": ["neural networks", "deep learning", "CNNs", "computer vision"],
      "description": "Connected through convolutional architectures"
    }
  ],
  "shared_contexts": [
    "Both appear frequently in image processing literature"
  ]
}
```

### what_do_we_know_about

**Purpose**: Comprehensive knowledge summaries  
**Mode**: Conversational  
**Response**: KnowledgeSummary with multi-faceted overview

```python
# Tool signature
what_do_we_know_about(topic: str) -> KnowledgeSummary

# Example usage in Claude
"Use what_do_we_know_about to get a comprehensive overview of 'attention mechanisms'"
```

**Parameters**:
- `topic` (string): Topic for comprehensive summary

**Response Format**:
```json
{
  "topic": "attention mechanisms",
  "summary": "Attention mechanisms are neural network components...",
  "key_facts": [
    "Introduced in neural machine translation",
    "Core component of transformer architecture",
    "Enables selective focus on input parts"
  ],
  "applications": [
    "Machine translation",
    "Text summarization", 
    "Image captioning"
  ],
  "related_concepts": ["transformer", "self-attention", "multi-head attention"],
  "current_research": [
    "Efficient attention mechanisms",
    "Sparse attention patterns"
  ],
  "knowledge_gaps": [
    "Limited understanding of attention interpretability"
  ]
}
```

## 📚 Literature Review Tools (Formal Writing Mode)

Tools for formal academic writing with proper citations. These tools integrate with the citation manager and return citation-ready content.

### gather_sources_for_topic

**Purpose**: Collect and organize sources for literature review sections  
**Mode**: Formal writing  
**Response**: SourceCollection with organized references

```python
# Tool signature
gather_sources_for_topic(topic: str) -> SourceCollection

# Example usage in Claude
"Use gather_sources_for_topic to collect sources about 'transformer architecture' for my background section"
```

**Parameters**:
- `topic` (string): Topic for source gathering

**Response Format**:
```json
{
  "topic": "transformer architecture",
  "primary_sources": [
    {
      "citation_key": "vaswani2017attention",
      "title": "Attention Is All You Need",
      "relevance_score": 0.95,
      "key_contributions": ["Introduced transformer architecture", "Self-attention mechanism"]
    }
  ],
  "supporting_sources": [
    {
      "citation_key": "devlin2019bert",
      "title": "BERT: Pre-training of Deep Bidirectional Transformers",
      "relevance_score": 0.85,
      "key_contributions": ["Bidirectional transformer training"]
    }
  ],
  "source_organization": {
    "foundational_papers": ["vaswani2017attention"],
    "applications": ["devlin2019bert", "radford2019gpt2"],
    "improvements": ["shaw2018self", "kitaev2020reformer"]
  }
}
```

### get_facts_with_citations

**Purpose**: Get citation-ready factual statements  
**Mode**: Formal writing  
**Response**: CitedFacts with proper academic formatting

```python
# Tool signature
get_facts_with_citations(topic: str, style: str = "APA") -> CitedFacts

# Example usage in Claude
"Use get_facts_with_citations to get APA-formatted facts about 'deep learning' for my literature review"
```

**Parameters**:
- `topic` (string): Topic for fact extraction
- `style` (string): Citation style - "APA", "IEEE", "Nature", "MLA"

**Response Format**:
```json
{
  "topic": "deep learning",
  "citation_style": "APA",
  "cited_facts": [
    {
      "fact": "Deep learning has revolutionized computer vision through convolutional neural networks (LeCun et al., 2015).",
      "citations": ["lecun2015deep"],
      "confidence": 0.92,
      "section_suggestion": "background"
    },
    {
      "fact": "The transformer architecture introduced self-attention mechanisms that eliminated the need for recurrent layers (Vaswani et al., 2017).",
      "citations": ["vaswani2017attention"],
      "confidence": 0.98,
      "section_suggestion": "methodology"
    }
  ],
  "citation_count": 2,
  "facts_by_section": {
    "background": 1,
    "methodology": 1
  }
}
```

### verify_claim_with_sources

**Purpose**: Verify claims with supporting evidence  
**Mode**: Formal writing  
**Response**: ClaimVerification with evidence assessment

```python
# Tool signature
verify_claim_with_sources(claim: str) -> ClaimVerification

# Example usage in Claude
"Use verify_claim_with_sources to verify: 'Transformers are more efficient than RNNs for long sequences'"
```

**Parameters**:
- `claim` (string): Claim to verify with sources

**Response Format**:
```json
{
  "claim": "Transformers are more efficient than RNNs for long sequences",
  "verification_status": "supported",
  "confidence": 0.88,
  "supporting_evidence": [
    {
      "citation_key": "vaswani2017attention",
      "evidence": "Transformers reduce sequential computation and enable better parallelization",
      "relevance": 0.95
    }
  ],
  "contradicting_evidence": [],
  "nuanced_view": "Transformers are generally more efficient for long sequences due to parallelization, but RNNs may be more memory-efficient for very long sequences",
  "suggested_revision": "Transformers generally outperform RNNs on long sequences due to better parallelization capabilities (Vaswani et al., 2017)."
}
```

### get_topic_outline

**Purpose**: Generate structured literature review outlines  
**Mode**: Formal writing  
**Response**: LiteratureOutline with hierarchical structure

```python
# Tool signature
get_topic_outline(topic: str) -> LiteratureOutline

# Example usage in Claude
"Use get_topic_outline to create a structure for my 'neural machine translation' literature review"
```

**Parameters**:
- `topic` (string): Topic for outline generation

**Response Format**:
```json
{
  "topic": "neural machine translation",
  "outline": {
    "1. Introduction": {
      "subsections": ["Problem definition", "Historical context"],
      "key_sources": ["bahdanau2015neural", "sutskever2014sequence"]
    },
    "2. Background": {
      "subsections": ["Traditional approaches", "Neural network foundations"],
      "key_sources": ["brown1990statistical", "bengio2003neural"]
    },
    "3. Attention Mechanisms": {
      "subsections": ["Attention introduction", "Self-attention"],
      "key_sources": ["bahdanau2015neural", "vaswani2017attention"]
    },
    "4. Modern Architectures": {
      "subsections": ["Transformer models", "BERT and derivatives"],
      "key_sources": ["vaswani2017attention", "devlin2019bert"]
    }
  },
  "estimated_sections": 4,
  "suggested_length": "2000-3000 words"
}
```

### track_citations_used

**Purpose**: Track which citations have been used  
**Mode**: Formal writing  
**Response**: CitationUsage with tracking information

```python
# Tool signature
track_citations_used() -> CitationUsage

# Example usage in Claude
"Use track_citations_used to see which papers I've referenced so far"
```

**Parameters**: None

**Response Format**:
```json
{
  "total_citations": 15,
  "used_citations": [
    {
      "citation_key": "vaswani2017attention",
      "usage_count": 3,
      "contexts": ["background", "methodology", "results"],
      "confidence_scores": [0.95, 0.92, 0.88]
    },
    {
      "citation_key": "devlin2019bert",
      "usage_count": 2,
      "contexts": ["background", "related_work"],
      "confidence_scores": [0.90, 0.85]
    }
  ],
  "unused_citations": [
    {
      "citation_key": "radford2019gpt2",
      "reason": "not_yet_referenced"
    }
  ],
  "suggestions": [
    "Consider referencing GPT-2 in the applications section"
  ]
}
```

### generate_bibliography

**Purpose**: Generate formatted bibliography  
**Mode**: Formal writing  
**Response**: Bibliography with proper formatting

```python
# Tool signature
generate_bibliography(style: str = "APA", used_only: bool = True) -> Bibliography

# Example usage in Claude
"Use generate_bibliography to create an APA bibliography of only the papers I've cited"
```

**Parameters**:
- `style` (string): Citation style - "APA", "IEEE", "Nature", "MLA"
- `used_only` (boolean): Include only used citations

**Response Format**:
```json
{
  "style": "APA",
  "citation_count": 8,
  "bibliography": [
    "Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL-HLT.",
    "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... & Polosukhin, I. (2017). Attention is all you need. Advances in neural information processing systems, 30."
  ],
  "used_only": true,
  "alphabetical_order": true
}
```

## 🔧 Core Tools (Document Management)

Tools for managing document collections and system configuration.

### list_templates

**Purpose**: List available domain templates  
**Response**: List of template names

```python
# Tool signature
list_templates() -> List[str]

# Example usage in Claude
"Use list_templates to see what domain templates are available"
```

**Response Format**:
```json
[
  "academic",
  "legal",
  "medical",
  "financial",
  "engineering"
]
```

### switch_template

**Purpose**: Change the active domain template  
**Response**: Success status

```python
# Tool signature
switch_template(template_name: str) -> bool

# Example usage in Claude
"Use switch_template to change to the 'legal' template"
```

**Parameters**:
- `template_name` (string): Name of template to activate

**Response Format**:
```json
{
  "success": true,
  "previous_template": "academic",
  "new_template": "legal",
  "message": "Template switched successfully"
}
```

### load_document_collection

**Purpose**: Load and process a collection of documents  
**Response**: Processing results

```python
# Tool signature
load_document_collection(path: str) -> ProcessingResults

# Example usage in Claude
"Use load_document_collection to process all PDFs in './papers/'"
```

**Parameters**:
- `path` (string): Path to document collection

**Response Format**:
```json
{
  "total_documents": 10,
  "processed_successfully": 8,
  "failed_processing": 2,
  "total_entities": 245,
  "total_citations": 89,
  "processing_time": 125.5,
  "status": "completed_with_warnings"
}
```

### search_documents

**Purpose**: Search across processed documents  
**Response**: Search results with relevance scores

```python
# Tool signature
search_documents(query: str) -> SearchResults

# Example usage in Claude
"Use search_documents to find information about 'attention mechanisms'"
```

**Parameters**:
- `query` (string): Search query

**Response Format**:
```json
{
  "query": "attention mechanisms",
  "results": [
    {
      "document_title": "Attention Is All You Need",
      "relevance_score": 0.95,
      "excerpt": "The attention mechanism allows the model to focus on different parts...",
      "entities_mentioned": ["attention", "transformer", "self-attention"]
    }
  ],
  "total_results": 5,
  "search_time": 0.3
}
```

## 📖 Usage Examples

### Conversational Research Session

```
Claude: I'd like to explore the research on transformers. What are the main themes?

User: ask_knowledge_graph: What are the main themes in transformer research?

Claude: Based on the knowledge graph, the main themes in transformer research include:

1. **Attention Mechanisms**: The core innovation that allows models to focus on relevant parts of input sequences
2. **Architectural Improvements**: Variations like BERT, GPT, and T5 that build on the base transformer
3. **Efficiency Optimizations**: Work on reducing computational complexity and memory usage
4. **Applications**: Extending transformers beyond NLP to computer vision, speech, and multimodal tasks

Would you like me to explore any of these themes in more detail?

User: explore_topic: topic="attention mechanisms" scope="detailed"

Claude: Here's a detailed exploration of attention mechanisms...
```

### Literature Review Writing Session

```
Claude: I'm writing a literature review on neural machine translation. Let me gather sources and create an outline.

User: gather_sources_for_topic: neural machine translation

Claude: I've collected relevant sources for neural machine translation, organized into:

**Foundational Papers:**
- Sutskever et al. (2014) - Sequence to sequence learning
- Bahdanau et al. (2015) - Neural machine translation with attention

**Modern Architectures:**
- Vaswani et al. (2017) - Attention is all you need
- Devlin et al. (2019) - BERT

Let me create an outline for your literature review:

User: get_topic_outline: neural machine translation

Claude: Here's a structured outline for your neural machine translation literature review:

1. **Introduction**
   - Problem definition and motivation
   - Evolution from statistical to neural approaches

2. **Background**
   - Traditional machine translation approaches
   - Neural network foundations

3. **Attention Mechanisms**
   - Introduction of attention in NMT
   - Self-attention and transformer architecture

4. **Modern Architectures**
   - Transformer models and variants
   - Pre-trained models (BERT, GPT)

Now let me get citation-ready facts for your background section:

User: get_facts_with_citations: topic="neural machine translation" style="APA"

Claude: Here are APA-formatted facts for your literature review:

1. Neural machine translation systems have significantly outperformed traditional statistical methods on standard benchmarks (Sutskever et al., 2014).

2. The introduction of attention mechanisms addressed the bottleneck problem in sequence-to-sequence models (Bahdanau et al., 2015).

3. The transformer architecture eliminated the need for recurrent layers while achieving superior performance (Vaswani et al., 2017).
```

### Citation Management Session

```
Claude: Let me check which citations I've used so far and generate a bibliography.

User: track_citations_used

Claude: You've used 8 citations so far:
- Vaswani et al. (2017): Used 3 times in background, methodology, and results
- Devlin et al. (2019): Used 2 times in background and related work
- Sutskever et al. (2014): Used 1 time in introduction

You have 3 unused citations that might be relevant for your applications section.

User: generate_bibliography: style="APA" used_only=true

Claude: Here's your APA bibliography for the citations you've used:

Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL-HLT.

Sutskever, I., Vinyals, O., & Le, Q. V. (2014). Sequence to sequence learning with neural networks. Advances in neural information processing systems, 27.

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... & Polosukhin, I. (2017). Attention is all you need. Advances in neural information processing systems, 30.
```

## 🖥️ Claude Desktop Integration

### Configuration

Add to your Claude Desktop configuration (`~/.config/claude-desktop/config.json`):

```json
{
  "mcpServers": {
    "graphrag-research": {
      "command": "python3",
      "args": [
        "-m", "graphrag_mcp.cli.main", 
        "serve-universal", 
        "--template", "academic", 
        "--transport", "stdio"
      ],
      "cwd": "/path/to/your/project"
    }
  }
}
```

### Usage in Claude Desktop

Once configured, you can use MCP tools directly in Claude Desktop:

```
# Load your documents
load_document_collection: ./research_papers/

# Explore topics conversationally
ask_knowledge_graph: What are the key findings about attention mechanisms?

# Get citation-ready facts for writing
get_facts_with_citations: topic="transformer architecture" style="APA"

# Generate bibliography
generate_bibliography: style="APA" used_only=true
```

## 🔍 Tool Response Formats

### Common Response Fields

All tools return structured responses with these common fields:

```json
{
  "tool_name": "ask_knowledge_graph",
  "execution_time": 1.2,
  "success": true,
  "metadata": {
    "template": "academic",
    "document_count": 15,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Handling

When tools encounter errors, they return:

```json
{
  "tool_name": "ask_knowledge_graph",
  "success": false,
  "error_type": "ProcessingError",
  "error_message": "No documents loaded. Use load_document_collection first.",
  "suggestions": [
    "Load documents with load_document_collection",
    "Check that your document path is correct"
  ]
}
```

### Confidence Scores

Most tools include confidence scores to help you assess result quality:

- **0.9-1.0**: High confidence, reliable results
- **0.7-0.9**: Good confidence, likely accurate
- **0.5-0.7**: Moderate confidence, verify if critical
- **0.0-0.5**: Low confidence, use with caution

## 🎯 Best Practices

### For Chat Tools
1. **Ask specific questions** for better responses
2. **Use follow-up suggestions** to explore deeply
3. **Combine tools** for comprehensive understanding
4. **Check confidence scores** for result quality

### For Literature Review Tools
1. **Specify citation style** early in your workflow
2. **Use gather_sources_for_topic** before writing
3. **Verify claims** with verify_claim_with_sources
4. **Track citations** to avoid over/under-citing
5. **Generate bibliography** at the end

### For All Tools
1. **Load documents first** with load_document_collection
2. **Choose appropriate template** for your domain
3. **Use search_documents** to find specific information
4. **Monitor processing times** for performance

## 🆘 Troubleshooting

### Common Issues

1. **"No documents loaded"**: Use `load_document_collection` first
2. **"Template not found"**: Check available templates with `list_templates`
3. **"Low confidence results"**: Try more specific queries
4. **"Citation not found"**: Verify the citation exists in your documents

### Performance Tips

1. **Load documents once** per session
2. **Use specific queries** instead of broad ones
3. **Batch similar requests** together
4. **Monitor response times** and adjust accordingly

---

This MCP Tools reference provides everything you need to effectively use the GraphRAG MCP Toolkit with Claude Desktop. For API usage, see [API_REFERENCE.md](API_REFERENCE.md). For CLI commands, see [CLI_REFERENCE.md](CLI_REFERENCE.md).
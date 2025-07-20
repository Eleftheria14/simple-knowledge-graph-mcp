# EXTRACT ENTITIES FROM ACADEMIC DOCUMENTS FOR RESEARCH KNOWLEDGE BASE

## What You're Building
You're helping create a research knowledge base that combines two technologies:
- **Graph Database (Neo4j)**: Stores entities (people, concepts, methods) and their relationships as a connected network
- **Vector Database (ChromaDB)**: Stores text passages with embeddings for semantic search

Together, these form a "GraphRAG" system - a knowledge graph enhanced with retrieval-augmented generation capabilities. Researchers will use this to:
- Write literature reviews by querying connections across multiple papers
- Discover how concepts evolved over time
- Find contradictions between studies
- Identify research gaps and collaboration networks

## Your Task
You have two tools that store data in these databases. Read the document below and extract:
1. **Entities**: Important concepts, methods, people, findings that researchers would reference
2. **Relationships**: How entities connect (e.g., "transformer architecture uses self-attention")  
3. **Vector content**: Any content to store as vectors (text chunks, concepts, methods, findings)

<document>
{{document_content}}
</document>

## Why This Matters
- **Entities in Neo4j** enable relationship queries: "What methods build on transformers?"
- **Text in ChromaDB** enables semantic search: "Find all discussions of attention mechanisms"
- **Together** they answer complex questions: "How did attention mechanisms evolve across different architectures?"

## Step-by-Step Process

### Step 1: Identify Entities
Look for:
- **Scientific concepts**: theories, phenomena, principles (e.g., "backpropagation", "attention mechanism")
- **Methods/Techniques**: algorithms, procedures, approaches (e.g., "BERT model", "gradient descent")
- **Findings/Results**: discoveries, outcomes, metrics (e.g., "92% accuracy", "2.0 BLEU improvement")
- **People**: Researchers, authors when they made specific contributions
- **Technologies**: Software, tools, systems (e.g., "TensorFlow", "transformer architecture")

Create descriptive IDs like "transformer_architecture_2017" not "concept_1"

**Entity ID Guidelines:**
- **Multiple papers by same author**: `hinton_backprop_1986` vs `hinton_capsule_networks_2017`
- **Concept evolution over time**: `transformer_nlp_2017` vs `transformer_vision_2020`
- **Domain disambiguation**: `attention_mechanism_nlp` vs `attention_mechanism_computer_vision`
- **Include key identifiers**: year, domain, or distinguishing feature

### Step 2: Map Relationships
Connect entities with verbs that show:
- **Intellectual**: builds_on, extends, contradicts, validates, critiques
- **Functional**: uses, implements, measures, evaluates_against
- **Comparative**: outperforms, similar_to, alternatives_to
- **Temporal**: preceded, influenced, superseded

Include context - the sentence fragment that proves this relationship exists.

**Relationship Context Guidelines:**
- Use the **exact sentence fragment** that proves the relationship (10-30 words)
- Include author/year when relevant: "Vaswani et al. (2017) showed that transformers outperform RNNs"
- Make it **quotable for literature reviews** - should be citable evidence
- Examples:
  - Good: "BERT improved upon the original transformer architecture by introducing bidirectional pre-training"
  - Poor: "BERT is better than transformers"

### Step 3: Extract Text Chunks
Select passages that:
- Explain methodology researchers would cite
- State key findings with specific numbers
- Provide important background or theory
- Discuss limitations or future work
- Contain insights worth quoting

**Text Chunk Guidelines:**
- **Chunk size**: 50-300 words per chunk (paragraph-level)
- **Figures/tables**: Include figure captions and table summaries as separate chunks
- **Results vs interpretations**: Include both, but label them in properties
- **Equations**: Include mathematical formulations with surrounding explanation
- **Author interpretations**: Include discussion and conclusion insights, not just raw results

### Step 4: Call the Tools

**First, call store_entities with this exact format:**
```python
store_entities({
  "entities": [
    {
      "id": "vaswani_attention_2017",  # Descriptive unique ID
      "name": "Attention Is All You Need",  # Full name
      "type": "publication",  # person|concept|method|technology|finding|etc
      "properties": {  # Rich metadata
        "authors": ["Vaswani, A.", "Shazeer, N."],
        "year": 2017,
        "venue": "NeurIPS"
      },
      "confidence": 0.95  # 0.9+ for facts, 0.7-0.8 for inferences
    },
    {
      "id": "transformer_architecture",
      "name": "Transformer Architecture",
      "type": "technology",
      "properties": {
        "domain": "NLP",
        "key_innovation": "self-attention only",
        "year_introduced": 2017
      },
      "confidence": 0.98
    }
  ],
  "relationships": [
    {
      "source": "transformer_architecture",
      "target": "self_attention_mechanism",
      "type": "uses",
      "confidence": 0.95,
      "context": "The Transformer relies entirely on self-attention mechanisms"
    }
  ],
  "document_info": {
    "title": "Title of Current Document",
    "type": "research_paper"
  }
})
```

**Then, call store_vectors with this exact format:**
```python
store_vectors({
  "vectors": [
    {
      "id": "methodology_summary",
      "content": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing entirely with recurrence and convolutions.",
      "type": "text_chunk",
      "properties": {"section": "methodology", "word_count": 21}
    },
    {
      "id": "performance_result",
      "content": "The Transformer model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results by over 2 BLEU points.",
      "type": "text_chunk", 
      "properties": {"section": "results", "metric": "BLEU", "value": 28.4, "improvement": 2.0}
    },
    {
      "id": "attention_concept",
      "content": "Self-attention mechanism allowing models to focus on different parts of input sequences without recurrence",
      "type": "concept",
      "properties": {"domain": "deep_learning", "innovation": "sequence modeling"}
    }
  ],
  "document_info": {
    "title": "Title of Current Document",
    "type": "research_paper"
  }
})
```

## Quality Guidelines

### Confidence Score Calibration
- **0.9-1.0 (Explicit Facts)**: "GPT-4 was developed by OpenAI" (stated directly in paper)
- **0.7-0.8 (Clear Inferences)**: "BERT improved transformer performance" (clear from reported results)
- **0.5-0.6 (Reasonable Connections)**: "This work may influence future language models" (logical inference)

### Property Standardization
Use consistent property names across entity types:
- **Years**: Always use `year_published`, `year_introduced`, `year_developed`
- **Locations**: Always use `affiliation`, `institution`, `country`
- **Performance**: Always use `accuracy`, `bleu_score`, `f1_score`
- **Domains**: Always use `domain`, `field`, `application_area`

### Entity and Relationship Requirements
- **Entity IDs**: Make them descriptive and unique (include year, domain, or key attribute)
- **Properties**: Add rich metadata - affiliations, years, metrics, domains, purposes
- **Context**: Always include the exact text snippet that supports each relationship
- **Completeness**: Extract liberally - more connections make the knowledge graph more valuable
- **Validation**: Ensure all relationship source/target IDs exist in the entities list

## Error Handling Guidelines

### Ambiguous Entities
- Create separate entities with disambiguation: `attention_nlp_vaswani_2017` vs `attention_vision_dosovitskiy_2020`
- Add disambiguating properties: `{"disambiguation": "natural language processing"}`

### Incomplete Citations
- Use systematic naming: `author_unknown_transformer_2017` or `anonymous_bert_analysis_2019`
- Mark incomplete data: `{"citation_complete": false, "missing_fields": ["doi", "journal"]}`

### Conflicting Information
- Extract both claims with different confidence scores
- Add properties indicating conflict: `{"contradicts": "smith_2020_claim", "evidence_strength": "weak"}`
- Include context showing the contradiction

## Common Mistakes to Avoid
❌ Generic IDs like "person_1" or "concept_23"
❌ Relationships without supporting context
❌ Missing confidence scores
❌ Extracting only famous names - include all scientifically relevant entities
❌ Ignoring methods, metrics, and findings in favor of just people
❌ Using inconsistent property names across similar entities
❌ Creating relationships to non-existent entity IDs

## Example of Good Extraction

From text: "BERT (Devlin et al., 2018) improved upon the original transformer architecture by introducing bidirectional pre-training, achieving state-of-the-art results on eleven NLP tasks."

✅ Good extraction creates entities for BERT, transformer architecture, Devlin, bidirectional pre-training
✅ Maps relationship: bert_improves_upon_transformer with context
✅ Stores the full sentence as a text chunk with proper citation

## CRITICAL: Format Requirements
- Use EXACT JSON structure shown above
- Missing fields cause database errors (Example: missing "confidence" field → Neo4j storage fails)
- Call tools using function syntax: tool_name({...})
- Only output tool calls, no explanations
- Focus on entities valuable for literature reviews
- Validate that all relationship source/target IDs exist in your entities list
- Use consistent step numbering throughout your process

**Text Chunk Size Estimates:**
- Methodology descriptions: ~100-200 words
- Key findings: ~50-150 words  
- Figure captions: ~20-80 words
- Discussion insights: ~150-300 words

Begin extraction now. Call store_entities first, then store_vectors.
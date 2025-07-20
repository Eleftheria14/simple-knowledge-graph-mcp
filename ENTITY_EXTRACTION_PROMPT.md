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
You have two tools that store data in these databases. Read the documents in the project folder and extract:
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

### Step 0: Extract Complete Citation (FIRST - MANDATORY)

**CRITICAL**: For EVERY academic paper, you MUST create a complete citation entity BEFORE extracting any concepts.

**Required Citation Entity:**
```json
{
  "id": "citation_[year]_[first_author_lastname]",
  "name": "[Paper Title] - Citation",
  "type": "publication", 
  "confidence": 0.99,
  "properties": {
    "doi": "10.xxx/xxx (REQUIRED)",
    "journal": "Journal Name (REQUIRED)",
    "volume": "number (REQUIRED)",
    "issue": "issue info",
    "pages": "start-end (REQUIRED)", 
    "year": "YYYY (REQUIRED)",
    "authors_all": "comma-separated full author list",
    "corresponding_author": "name with affiliation",
    "received_date": "YYYY-MM-DD",
    "accepted_date": "YYYY-MM-DD", 
    "published_date": "YYYY-MM-DD",
    "funding": "funding sources from acknowledgments",
    "open_access": "true/false",
    "impact_factor": "if known",
    "citation_preview": "Author et al. (2025). Title. Journal, vol(issue), pages."
  }
}
```

**Citation Extraction Process:**
1. **Find DOI** (usually in header/footer or first page)
2. **Extract journal metadata** (volume, issue, pages from header/first page)
3. **Capture ALL authors** (complete list, not just first author)
4. **Get publication timeline** (received/accepted/published dates from footnotes)
5. **Note funding information** (from acknowledgments section)
6. **Assess open access status** (look for CC licenses or open access statements)

**Mandatory Citation Relationships:**
Every extracted entity must link back to the citation:
- concept_entity **published_in** → citation_entity
- finding_entity **reported_in** → citation_entity  
- author_entity **authored** → citation_entity
- method_entity **described_in** → citation_entity

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

### Step 3: Extract Complete Text Coverage (CRITICAL)

**🚨 MANDATORY: Store 100% of paper content, not cherry-picked highlights**

Systematic chunking is REQUIRED for complete semantic search capabilities:

**Systematic Chunking Requirements:**
- **Chunk Size**: 200-400 words per chunk (optimal for search)
- **Overlap**: 50-100 words between adjacent chunks for continuity
- **Coverage**: Every paragraph must be included systematically
- **Target**: 40-60 chunks per typical research paper
- **Exclusions**: Only skip references list and acknowledgments

**Sequential Processing Rules:**
1. **Page-by-page**: Process paper sequentially from start to finish
2. **Section preservation**: Keep chunks within logical sections when possible
3. **Overlap strategy**: End each chunk mid-sentence, start next chunk 2-3 sentences before
4. **No gaps**: Every sentence must appear in at least one chunk

**Section Coverage Requirements:**
- ✅ **Abstract**: Complete text as first chunk
- ✅ **Introduction**: All background and motivation
- ✅ **Methods**: Every procedural detail
- ✅ **Results**: All findings, figures, tables
- ✅ **Discussion**: Complete analysis and interpretation
- ✅ **Conclusion**: All summary points
- ✅ **Figure captions**: Each as separate chunk with section context
- ✅ **Table data**: Summaries as separate chunks

### Step 4: Call the Tools

**First, call store_entities with this exact format:**
```python
store_entities({
  "entities": [
    {
      "id": "vaswani_attention_2017",  # Descriptive unique ID
      "name": "Attention Is All You Need",  # Full name
      "type": "publication",  # person|concept|method|technology|finding|etc
      "properties": {  # Rich metadata - prefer simple values over arrays/objects when possible
        "authors": "Vaswani, A.; Shazeer, N.",  # Use semicolon-separated string instead of array
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
    "type": "research_paper",
    "doi": "10.xxx/xxx",
    "journal": "Journal Name",
    "year": 2025,
    "citation_preview": "Author et al. (2025). Title. Journal, vol(issue), pages."
  }
})
```

**Then, call store_vectors with COMPLETE TEXT COVERAGE:**
```python
store_vectors({
  "vectors": [
    # SYSTEMATIC CHUNKS - Every part of paper covered
    {
      "id": "page1_chunk1_abstract",
      "content": "[Complete abstract text 200-400 words...]",
      "type": "text_chunk",
      "properties": {
        "page": 1,
        "section": "abstract", 
        "chunk_sequence": 1,
        "word_count": 287,
        "overlap_with_previous": false
      }
    },
    {
      "id": "page1_chunk2_introduction",
      "content": "[Sequential introduction text with 75-word overlap from previous chunk...]",
      "type": "text_chunk",
      "properties": {
        "page": 1,
        "section": "introduction",
        "chunk_sequence": 2, 
        "word_count": 324,
        "overlap_with_previous": true
      }
    },
    {
      "id": "page2_chunk3_methods",
      "content": "[Sequential methods text with overlap...]",
      "type": "text_chunk",
      "properties": {
        "page": 2,
        "section": "methods",
        "chunk_sequence": 3,
        "word_count": 356,
        "overlap_with_previous": true
      }
    },
    # Continue for ALL content - aim for 40-60 chunks total
    {
      "id": "page3_chunk4_figure1",
      "content": "Figure 1: [Complete caption and description]",
      "type": "text_chunk",
      "properties": {
        "page": 3,
        "section": "results",
        "chunk_sequence": 4,
        "content_type": "figure_caption",
        "figure_number": 1
      }
    }
    # ... Continue until 100% of paper is covered
  ],
  "document_info": {
    "title": "Title of Current Document",
    "type": "research_paper",
    "doi": "10.xxx/xxx",
    "journal": "Journal Name",
    "year": 2025,
    "citation_preview": "Author et al. (2025). Title. Journal, vol(issue), pages."
  }
})
```

**Coverage Validation:**
For a typical 12-page research paper, you should generate:
- **40-60 systematic chunks** covering 95%+ of content
- **Sequential chunk IDs** (page1_chunk1, page1_chunk2, etc.)
- **Section tracking** for all major paper sections
- **Overlap preservation** between adjacent chunks

## Quality Guidelines

### Citation Quality Requirements
**CRITICAL**: Missing complete citations reduces research credibility to ZERO.

**Required Citation Fields (all mandatory for academic papers):**
- DOI (Digital Object Identifier)
- Journal name and volume/issue/pages
- Complete author list (not just first author)
- Publication year
- At minimum: title, authors, journal, year, pages

**Citation Quality Scoring:**
- Complete citation with DOI: confidence 0.99
- Missing 1-2 non-critical fields: confidence 0.9
- Missing DOI or journal info: confidence 0.7
- Incomplete author list: confidence 0.8

**If citation info is incomplete:**
- Mark missing fields clearly: `"doi": "NOT_FOUND"`
- Note in properties: `"citation_complete": false, "missing_fields": ["doi", "pages"]`
- Still create the citation entity - partial citations are better than none

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

### Property Value Guidelines
**IMPORTANT**: Keep property values simple to avoid database errors:
- ✅ **Use strings instead of arrays**: `"authors": "Smith, J.; Jones, M."` (not `["Smith, J.", "Jones, M."]`)
- ✅ **Use simple values**: `"year": 2023`, `"accuracy": 0.95`, `"domain": "NLP"`
- ✅ **Convert lists to strings**: `"question_types": "multiple_choice; open_ended"` (not `["multiple_choice", "open_ended"]`)
- ❌ **Avoid nested objects**: Don't use `{"stats": {"mean": 0.8, "std": 0.1}}`
- ❌ **Avoid complex arrays**: Don't use `[{"name": "test1", "score": 0.9}]`

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
❌ **CRITICAL**: Not creating complete citation entity first
❌ **CRITICAL**: Missing DOI, journal, or author information
❌ **CRITICAL**: Incomplete author lists (only listing first author)
❌ Generic IDs like "person_1" or "concept_23"
❌ Relationships without supporting context
❌ Missing confidence scores
❌ Extracting only famous names - include all scientifically relevant entities
❌ Ignoring methods, metrics, and findings in favor of just people
❌ Using inconsistent property names across similar entities
❌ Creating relationships to non-existent entity IDs
❌ Not linking extracted concepts back to the publication citation

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

**Systematic Chunking Size Standards:**
- **Standard chunks**: 200-400 words (optimal for semantic search)
- **Overlap regions**: 50-100 words between chunks
- **Figure/table chunks**: 50-200 words (captions + descriptions)
- **Coverage target**: 95%+ of original paper content
- **Total chunks expected**: 40-60 for typical research paper

**Critical Success Metrics:**
- ✅ **No content gaps**: Every paragraph represented
- ✅ **Complete coverage**: All sections systematically chunked  
- ✅ **Searchable depth**: Can find ANY concept mentioned in paper
- ✅ **Research integrity**: Comprehensive, not selective extraction

## MANDATORY EXTRACTION ORDER

1. **FIRST**: Create complete citation entity with all bibliographic metadata
2. **SECOND**: Extract concepts, methods, findings, people
3. **THIRD**: Map relationships between entities AND back to citation
4. **FOURTH**: 🚨 **SYSTEMATIC TEXT COVERAGE** - Chunk entire paper sequentially

**Every academic paper MUST include:**
- 1 complete citation entity (type: "publication")
- All concepts linked to citation via relationships
- Complete author information in citation properties
- DOI and journal metadata for professional credibility
- **40-60 systematic text chunks covering 95%+ of paper content**

**🚨 CRITICAL REMINDER:**
- **NOT** selective highlights - **COMPLETE** systematic coverage
- **NOT** cherry-picked passages - **EVERY** paragraph included
- **NOT** ~14 chunks - **40-60** comprehensive chunks
- This enables searching **EVERYTHING**, not just "important" parts

Begin extraction now. Call store_entities first, then store_vectors with COMPLETE coverage.

**BOTTOM LINE**: We're building a research database, not a highlights reel. Researchers need to search across EVERYTHING, not just what seems important.
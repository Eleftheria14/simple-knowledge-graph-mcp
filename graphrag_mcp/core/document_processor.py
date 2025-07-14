"""
Document Processing Engine for GraphRAG MCP Toolkit

Domain-agnostic document processing with RAG capabilities.
Extracted and refactored from SimplePaperRAG to support multiple domains.
"""

import re
import json
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import logging

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ML imports
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Configuration
from pydantic import BaseModel, Field
from typing_extensions import Annotated

logger = logging.getLogger(__name__)


class ProcessingConfig(BaseModel):
    """Configuration for document processing"""
    embedding_model: str = Field(default="nomic-embed-text", description="Ollama embedding model")
    llm_model: str = Field(default="llama3.1:8b", description="Ollama LLM model")
    chunk_size: int = Field(default=800, description="Text chunk size")
    chunk_overlap: int = Field(default=100, description="Overlap between chunks")
    temperature: float = Field(default=0.1, description="LLM temperature")
    max_context: int = Field(default=32768, description="Maximum context length")
    max_predict: int = Field(default=2048, description="Maximum prediction length")


class DocumentData(BaseModel):
    """Structured document data"""
    title: str = Field(description="Document title")
    content: str = Field(description="Full document content")
    chunks: List[str] = Field(description="Text chunks")
    embeddings: Optional[Any] = Field(default=None, description="Chunk embeddings")
    entities: Dict[str, List[str]] = Field(default_factory=dict, description="Extracted entities")
    relationships: List[Dict] = Field(default_factory=list, description="Entity relationships")
    citation: str = Field(description="Document citation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DocumentProcessor:
    """
    Domain-agnostic document processing engine with RAG capabilities.
    
    Supports configurable entity extraction and relationship mapping
    through domain templates.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """Initialize the document processor"""
        self.config = config or ProcessingConfig()
        
        # Initialize LLM components
        self.embeddings = OllamaEmbeddings(model=self.config.embedding_model)
        self.llm = ChatOllama(
            model=self.config.llm_model,
            temperature=self.config.temperature,
            num_ctx=self.config.max_context,
            num_predict=self.config.max_predict
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\\n\\n", "\\n", ". ", " ", ""]
        )
        
        # Current document data
        self.document_data: Optional[DocumentData] = None
        
        # Chat history
        self.chat_history: List[Dict[str, Any]] = []
        
        logger.info(f"🤖 DocumentProcessor initialized with {self.config.llm_model}")
    
    def load_document(self, pdf_path: str) -> DocumentData:
        """
        Load and process a document
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Structured document data
        """
        logger.info(f"📄 Loading document: {pdf_path}")
        
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        full_text = "\\n".join([doc.page_content for doc in documents])
        
        # Extract basic metadata
        title = self._extract_title(full_text)
        citation = self._extract_citation(full_text, Path(pdf_path).name)
        
        # Create chunks
        chunks = self.text_splitter.split_text(full_text)
        
        # Generate embeddings
        logger.info("🧠 Creating embeddings...")
        chunk_embeddings = self.embeddings.embed_documents(chunks)
        embeddings_array = np.array(chunk_embeddings)
        
        # Create document data
        self.document_data = DocumentData(
            title=title,
            content=full_text,
            chunks=chunks,
            embeddings=embeddings_array,
            entities={},
            relationships=[],
            citation=citation,
            metadata={
                "pdf_path": pdf_path,
                "chunk_count": len(chunks),
                "character_count": len(full_text),
                "processing_config": self.config.model_dump()
            }
        )
        
        logger.info(f"✅ Document loaded: {len(chunks)} chunks, {len(full_text):,} characters")
        return self.document_data
    
    def extract_entities(self, domain_guidance: Optional[Dict[str, str]] = None) -> Dict[str, List[str]]:
        """
        Extract ALL entities from document without artificial constraints
        
        Args:
            domain_guidance: Optional hints about what might be important in this domain
            
        Returns:
            Comprehensive entity extraction organized by discovered categories
        """
        if not self.document_data:
            raise ValueError("No document loaded. Call load_document() first.")
        
        logger.info("🔍 Extracting entities (unconstrained discovery)...")
        
        # Use first 4000 characters for entity extraction
        content_sample = self.document_data.content[:4000]
        
        # Build open-ended entity extraction prompt
        guidance_text = ""
        if domain_guidance:
            guidance_text = f"""
Domain context: This appears to be a {list(domain_guidance.keys())[0] if domain_guidance else 'general'} document.
Some entities that might be particularly important: {', '.join(domain_guidance.values()) if domain_guidance else 'any significant entities'}.
However, extract ALL important entities you find, not just these suggestions.
"""
        
        entity_prompt = ChatPromptTemplate.from_template(f"""
Extract ALL important entities from this document. Discover and categorize them naturally based on what you find.

{guidance_text}

Instructions:
1. Read through the document carefully
2. Identify ALL significant entities (people, places, concepts, methods, tools, organizations, etc.)
3. Group them into logical categories that emerge from the content
4. Don't limit yourself to predefined categories - create whatever categories make sense
5. Include specific names, technical terms, concepts, and any other important information

Return a JSON object where categories are discovered from the content:

Example format (but use categories that fit THIS document):
{{
  "people": ["Specific names of people"],
  "organizations": ["Companies, institutions, groups"],
  "concepts": ["Key ideas, theories, principles"],
  "technologies": ["Tools, software, systems, methods"],
  "locations": ["Places, regions, facilities"],
  "measurements": ["Metrics, numbers, quantities"],
  "processes": ["Procedures, methods, workflows"],
  "products": ["Specific products, systems, outputs"],
  "events": ["Important events, meetings, incidents"],
  "documents": ["Referenced papers, standards, guidelines"],
  "other_important": ["Anything else significant that doesn't fit above"]
}}

Document excerpt:
{{content}}

JSON:""")
        
        chain = entity_prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({"content": content_sample})
            # Clean up the result and parse JSON
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                entities = json.loads(json_str)
                
                # Clean up empty categories
                entities = {k: v for k, v in entities.items() if v and len(v) > 0}
                
            else:
                # Fallback if JSON extraction fails - try simple extraction
                logger.warning("JSON parsing failed, attempting simple extraction")
                entities = self._fallback_entity_extraction(content_sample)
            
            self.document_data.entities = entities
            total_entities = sum(len(v) for v in entities.values())
            categories = len(entities)
            logger.info(f"✅ Extracted {total_entities} entities across {categories} discovered categories")
            return entities
            
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            # Return simple fallback extraction
            return self._fallback_entity_extraction(content_sample)
    
    def _fallback_entity_extraction(self, content: str) -> Dict[str, List[str]]:
        """Fallback entity extraction using simple patterns"""
        import re
        
        entities = {
            "proper_nouns": [],
            "technical_terms": [],
            "numbers_and_metrics": []
        }
        
        # Extract capitalized words (likely proper nouns)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        entities["proper_nouns"] = list(set(proper_nouns))[:10]
        
        # Extract technical terms (words with underscores, hyphens, or camelCase)
        technical_terms = re.findall(r'\b(?:[a-z]+(?:_[a-z]+)+|[a-z]+(?:-[a-z]+)+|[a-z]+[A-Z][a-z]*)\b', content)
        entities["technical_terms"] = list(set(technical_terms))[:10]
        
        # Extract numbers with units
        numbers = re.findall(r'\b\d+(?:\.\d+)?\s*(?:km|kg|mb|gb|%|seconds?|minutes?|hours?)\b', content, re.IGNORECASE)
        entities["numbers_and_metrics"] = list(set(numbers))[:5]
        
        # Clean up empty categories
        entities = {k: v for k, v in entities.items() if v}
        
        logger.info(f"🔄 Fallback extraction: {sum(len(v) for v in entities.values())} entities")
        return entities
    
    def query(self, question: str, top_k: int = 5) -> str:
        """
        Query the document using RAG
        
        Args:
            question: Natural language question
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Generated answer
        """
        if not self.document_data:
            raise ValueError("No document loaded. Call load_document() first.")
        
        logger.info(f"❓ Query: {question}")
        
        # Create embedding for question
        question_embedding = self.embeddings.embed_query(question)
        question_array = np.array([question_embedding])
        
        # Find most similar chunks
        similarities = cosine_similarity(question_array, self.document_data.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Get relevant chunks
        relevant_chunks = [self.document_data.chunks[i] for i in top_indices]
        context = "\\n\\n".join(relevant_chunks)
        
        # Generate answer
        qa_prompt = ChatPromptTemplate.from_template("""
You are an expert researcher. Answer the question based ONLY on the provided context from the document.

Context from document:
{context}

Question: {question}

Provide a clear, accurate answer based on the context. If the context doesn't contain enough information to answer the question, say so.

Answer:""")
        
        chain = qa_prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})
        
        # Store in chat history
        self.chat_history.append({
            'question': question,
            'answer': answer,
            'relevant_chunks': len(relevant_chunks),
            'similarity_scores': [similarities[i] for i in top_indices],
            'timestamp': Path(__file__).stat().st_mtime  # Simple timestamp
        })
        
        logger.info(f"✅ Answer generated ({len(answer)} chars)")
        return answer
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Get summary of current document"""
        if not self.document_data:
            return {"error": "No document loaded"}
        
        return {
            'title': self.document_data.title,
            'citation': self.document_data.citation,
            'chunks': len(self.document_data.chunks),
            'entities': {k: len(v) for k, v in self.document_data.entities.items()},
            'chat_history': len(self.chat_history),
            'metadata': self.document_data.metadata
        }
    
    def _extract_title(self, text: str) -> str:
        """Extract document title from text"""
        lines = text.split('\\n')[:10]  # Look in first 10 lines
        
        for line in lines:
            line = line.strip()
            # Look for title-like line (long, capitalized, not author-like)
            if (len(line) > 20 and 
                len(line) < 200 and 
                not any(word in line.lower() for word in ['university', 'department', '@', 'email']) and
                sum(1 for c in line if c.isupper()) > 3):
                return line
        
        return "Unknown Title"
    
    def _extract_citation(self, text: str, filename: str) -> str:
        """Extract basic citation information"""
        title = self.document_data.title if self.document_data else self._extract_title(text)
        
        # Look for year
        year_match = re.search(r'\\b(20[0-2][0-9])\\b', text[:2000])
        year = year_match.group(1) if year_match else "Unknown Year"
        
        # Look for DOI
        doi_match = re.search(r'(?:doi|DOI)[:.\\s]*(10\\.\\d+/[^\\s]+)', text[:3000])
        doi = doi_match.group(1) if doi_match else ""
        
        # Simple citation format
        citation = f"{title}. {year}"
        if doi:
            citation += f". DOI: {doi}"
        
        return citation


# Convenience function for backwards compatibility
def create_document_processor(embedding_model: str = "nomic-embed-text", 
                            llm_model: str = "llama3.1:8b") -> DocumentProcessor:
    """Create a DocumentProcessor with specified models"""
    config = ProcessingConfig(
        embedding_model=embedding_model,
        llm_model=llm_model
    )
    return DocumentProcessor(config)
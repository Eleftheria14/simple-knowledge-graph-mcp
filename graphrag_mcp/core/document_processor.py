"""
Document Processing Engine for GraphRAG MCP Toolkit

Domain-agnostic document processing with RAG capabilities.
Extracted and refactored from SimplePaperRAG to support multiple domains.
"""

import json
import logging
import re
import time
import asyncio
from pathlib import Path
from typing import Any, Optional
from contextlib import contextmanager

# ML imports
import numpy as np

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
from pydantic import BaseModel, Field, validator

# Import our error handling
from ..utils.error_handling import ProcessingError, ValidationError

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    # Fallback implementation
    def cosine_similarity(a, b):
        return [[0.5]]  # Simple fallback

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
    
    # Enhanced validation and timeout settings
    max_file_size_mb: int = Field(default=50, description="Maximum file size in MB")
    entity_extraction_timeout: int = Field(default=60, description="Timeout for entity extraction in seconds")
    max_retry_attempts: int = Field(default=3, description="Maximum retry attempts for failed operations")
    validation_enabled: bool = Field(default=True, description="Enable comprehensive validation")
    
    @validator('chunk_size')
    def validate_chunk_size(cls, v):
        if v < 100 or v > 4000:
            raise ValueError('chunk_size must be between 100 and 4000')
        return v
    
    @validator('chunk_overlap')
    def validate_chunk_overlap(cls, v, values):
        if 'chunk_size' in values and v >= values['chunk_size']:
            raise ValueError('chunk_overlap must be less than chunk_size')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('temperature must be between 0.0 and 1.0')
        return v
    
    @validator('max_file_size_mb')
    def validate_max_file_size(cls, v):
        if v < 1 or v > 500:
            raise ValueError('max_file_size_mb must be between 1 and 500')
        return v


class DocumentData(BaseModel):
    """Structured document data"""
    title: str = Field(description="Document title")
    content: str = Field(description="Full document content")
    chunks: list[str] = Field(description="Text chunks")
    embeddings: Any | None = Field(default=None, description="Chunk embeddings")
    entities: dict[str, list[str]] = Field(default_factory=dict, description="Extracted entities")
    relationships: list[dict] = Field(default_factory=list, description="Entity relationships")
    citation: str = Field(description="Document citation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DocumentProcessor:
    """
    Domain-agnostic document processing engine with RAG capabilities.
    
    Supports configurable entity extraction and relationship mapping
    through domain templates.
    """

    def __init__(self, config: ProcessingConfig | None = None):
        """Initialize the document processor with comprehensive validation"""
        self.config = config or ProcessingConfig()
        
        # Validate configuration
        self._validate_configuration()

        # Initialize LLM components with error handling
        try:
            self.embeddings = OllamaEmbeddings(model=self.config.embedding_model)
            self.llm = ChatOllama(
                model=self.config.llm_model,
                temperature=self.config.temperature,
                num_ctx=self.config.max_context,
                num_predict=self.config.max_predict
            )
        except Exception as e:
            raise ProcessingError(
                f"Failed to initialize LLM components: {str(e)}",
                {"embedding_model": self.config.embedding_model, "llm_model": self.config.llm_model}
            )

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\\n\\n", "\\n", ". ", " ", ""]
        )

        # Current document data
        self.document_data: DocumentData | None = None

        # Chat history
        self.chat_history: list[dict[str, Any]] = []
        
        # Processing state
        self._processing_active = False
        self._last_error: Optional[str] = None

        logger.info(f"🤖 DocumentProcessor initialized with {self.config.llm_model}")
    
    def _validate_configuration(self):
        """Validate the processor configuration"""
        if not self.config.embedding_model or not self.config.llm_model:
            raise ValidationError(
                "Both embedding_model and llm_model must be specified",
                {"embedding_model": self.config.embedding_model, "llm_model": self.config.llm_model}
            )
        
        # Validate model format (should contain colon for Ollama models)
        if ":" not in self.config.llm_model:
            logger.warning(f"LLM model '{self.config.llm_model}' may not be in correct Ollama format (model:tag)")
    
    @contextmanager
    def _processing_context(self, operation_name: str):
        """Context manager for processing operations with proper cleanup"""
        if self._processing_active:
            raise ProcessingError(
                f"Cannot start {operation_name}: another operation is in progress",
                {"current_operation": operation_name}
            )
        
        self._processing_active = True
        self._last_error = None
        start_time = time.time()
        
        try:
            logger.info(f"🔄 Starting {operation_name}")
            yield
            processing_time = time.time() - start_time
            logger.info(f"✅ Completed {operation_name} in {processing_time:.2f}s")
        except Exception as e:
            processing_time = time.time() - start_time
            self._last_error = str(e)
            logger.error(f"❌ Failed {operation_name} after {processing_time:.2f}s: {e}")
            raise
        finally:
            self._processing_active = False
    
    def _validate_file_input(self, file_path: str) -> Path:
        """Validate file input with comprehensive checks"""
        if not file_path:
            raise ValidationError("File path cannot be empty", {"file_path": file_path})
        
        path = Path(file_path)
        
        # Check file existence
        if not path.exists():
            raise ValidationError(f"File does not exist: {file_path}", {"file_path": file_path})
        
        # Check if it's a file (not directory)
        if not path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}", {"file_path": file_path})
        
        # Check file extension
        if path.suffix.lower() != '.pdf':
            raise ValidationError(
                f"Only PDF files are supported, got: {path.suffix}",
                {"file_path": file_path, "file_extension": path.suffix}
            )
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise ValidationError(
                f"File too large: {file_size_mb:.1f}MB exceeds limit of {self.config.max_file_size_mb}MB",
                {"file_path": file_path, "file_size_mb": file_size_mb, "max_size_mb": self.config.max_file_size_mb}
            )
        
        # Check file permissions
        if not path.stat().st_mode & 0o444:  # Check read permission
            raise ValidationError(
                f"File is not readable: {file_path}",
                {"file_path": file_path}
            )
        
        return path

    def _generate_embeddings_with_retry(self, chunks: list[str], pdf_path: str) -> np.ndarray:
        """Generate embeddings with retry logic and error handling"""
        for attempt in range(self.config.max_retry_attempts):
            try:
                logger.info(f"🧠 Creating embeddings (attempt {attempt + 1}/{self.config.max_retry_attempts})...")
                chunk_embeddings = self.embeddings.embed_documents(chunks)
                
                if not chunk_embeddings:
                    raise ProcessingError(
                        f"No embeddings generated for chunks: {pdf_path}",
                        {"pdf_path": pdf_path, "chunk_count": len(chunks)}
                    )
                
                embeddings_array = np.array(chunk_embeddings)
                
                # Validate embeddings dimensions
                if embeddings_array.shape[0] != len(chunks):
                    raise ProcessingError(
                        f"Embeddings count mismatch: {embeddings_array.shape[0]} vs {len(chunks)} chunks",
                        {"pdf_path": pdf_path, "embeddings_shape": embeddings_array.shape}
                    )
                
                return embeddings_array
                
            except Exception as e:
                if attempt == self.config.max_retry_attempts - 1:
                    # Last attempt failed
                    raise ProcessingError(
                        f"Failed to generate embeddings after {self.config.max_retry_attempts} attempts: {str(e)}",
                        {"pdf_path": pdf_path, "chunk_count": len(chunks), "final_error": str(e)}
                    )
                
                logger.warning(f"Embedding generation attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff

    def load_document(self, pdf_path: str) -> DocumentData:
        """
        Load and process a document with comprehensive validation and error handling
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Structured document data
            
        Raises:
            ValidationError: If file validation fails
            ProcessingError: If document processing fails
        """
        # Validate input file
        path = self._validate_file_input(pdf_path)
        
        with self._processing_context("document_loading"):
            try:
                # Load PDF with error handling
                loader = PyPDFLoader(str(path))
                documents = loader.load()
                
                if not documents:
                    raise ProcessingError(
                        f"No content extracted from PDF: {pdf_path}",
                        {"pdf_path": pdf_path}
                    )
                
                # Extract text content
                full_text = "\\n".join([doc.page_content for doc in documents])
                
                # Validate extracted content
                if not full_text.strip():
                    raise ProcessingError(
                        f"PDF contains no readable text: {pdf_path}",
                        {"pdf_path": pdf_path}
                    )
                
                # Check content length
                if len(full_text) < 100:
                    logger.warning(f"Document is very short ({len(full_text)} characters): {pdf_path}")
                elif len(full_text) > 500000:  # 500KB of text
                    logger.warning(f"Document is very long ({len(full_text)} characters): {pdf_path}")
                
                # Extract metadata with error handling
                try:
                    title = self._extract_title(full_text)
                    citation = self._extract_citation(full_text, path.name)
                except Exception as e:
                    logger.warning(f"Failed to extract metadata: {e}")
                    title = path.stem  # Fallback to filename
                    citation = f"Unknown. {path.name}"
                
                # Create chunks with validation
                try:
                    chunks = self.text_splitter.split_text(full_text)
                    if not chunks:
                        raise ProcessingError(
                            f"Text splitting produced no chunks: {pdf_path}",
                            {"pdf_path": pdf_path, "text_length": len(full_text)}
                        )
                except Exception as e:
                    raise ProcessingError(
                        f"Text splitting failed: {str(e)}",
                        {"pdf_path": pdf_path, "text_length": len(full_text)}
                    )
                
                # Generate embeddings with retry logic
                embeddings_array = self._generate_embeddings_with_retry(chunks, pdf_path)
                
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
                        "pdf_path": str(path),
                        "file_size_mb": path.stat().st_size / (1024 * 1024),
                        "processing_time": time.time(),
                        "chunk_count": len(chunks),
                        "character_count": len(full_text),
                        "processing_config": self.config.model_dump()
                    }
                )

                logger.info(f"✅ Document loaded: {len(chunks)} chunks, {len(full_text):,} characters")
                return self.document_data
                
            except (ValidationError, ProcessingError):
                raise
            except Exception as e:
                raise ProcessingError(
                    f"Unexpected error loading document: {str(e)}",
                    {"pdf_path": pdf_path, "error_type": type(e).__name__}
                )

    def extract_entities(self, domain_guidance: dict[str, str] | None = None) -> dict[str, list[str]]:
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

        template_text = f"""
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
{content}

JSON:"""

        entity_prompt = ChatPromptTemplate.from_template(template_text)

        chain = entity_prompt | self.llm | StrOutputParser()

        try:
            # Add robust timeout and retry handling for entity extraction
            import signal
            import time

            def timeout_handler(signum, frame):
                raise TimeoutError("Entity extraction timed out")

            max_attempts = 3
            timeout_seconds = 45  # Reduced timeout per attempt
            entities = None

            for attempt in range(max_attempts):
                try:
                    logger.info(f"🔍 Entity extraction attempt {attempt + 1}/{max_attempts}")

                    # Set timeout for this attempt
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(timeout_seconds)

                    # Invoke the chain with explicit termination
                    result = chain.invoke({"content": content_sample})
                    signal.alarm(0)  # Cancel the alarm - SUCCESS

                    # Validate we got a non-empty result
                    if not result or len(result.strip()) == 0:
                        raise ValueError("Empty result from LLM")

                    # Clean up the result and parse JSON
                    json_start = result.find('{')
                    json_end = result.rfind('}') + 1

                    if json_start != -1 and json_end != -1:
                        json_str = result[json_start:json_end]
                        entities = json.loads(json_str)

                        # Validate entities is a dictionary with content
                        if isinstance(entities, dict) and entities:
                            # Clean up empty categories
                            entities = {k: v for k, v in entities.items() if v and len(v) > 0}

                            # Ensure we have at least some entities
                            if entities:
                                logger.info(f"✅ Successfully extracted entities on attempt {attempt + 1}")
                                break
                            else:
                                raise ValueError("No valid entities extracted")
                        else:
                            raise ValueError("Invalid entity structure")
                    else:
                        raise ValueError("No valid JSON found in response")

                except (TimeoutError, ValueError, json.JSONDecodeError) as e:
                    signal.alarm(0)  # Cancel the alarm
                    logger.warning(f"❌ Attempt {attempt + 1} failed: {e}")

                    if attempt == max_attempts - 1:
                        # Final attempt failed - use fallback
                        logger.error("All entity extraction attempts failed, using fallback")
                        entities = self._fallback_entity_extraction(content_sample)
                        break
                    else:
                        # Wait before retry with exponential backoff
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.info(f"⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)

                except Exception as e:
                    signal.alarm(0)  # Cancel the alarm
                    logger.error(f"❌ Unexpected error on attempt {attempt + 1}: {e}")
                    if attempt == max_attempts - 1:
                        entities = self._fallback_entity_extraction(content_sample)
                        break
                    else:
                        time.sleep(2 ** attempt)

            # Final validation - ensure we have entities
            if not entities:
                logger.error("No entities extracted, using empty fallback")
                entities = {"general": ["document_processed"]}

            self.document_data.entities = entities
            total_entities = sum(len(v) for v in entities.values())
            categories = len(entities)
            logger.info(f"✅ Extracted {total_entities} entities across {categories} discovered categories")
            return entities

        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            # Return simple fallback extraction
            return self._fallback_entity_extraction(content_sample)

    def _fallback_entity_extraction(self, content: str) -> dict[str, list[str]]:
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

    def get_document_summary(self) -> dict[str, Any]:
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

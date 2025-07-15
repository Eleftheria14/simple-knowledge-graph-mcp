"""
Ollama Integration Engine for GraphRAG MCP Toolkit

Centralized Ollama LLM and embedding integration with configuration management.
Provides consistent local AI processing across all domain templates.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

# LangChain Ollama imports
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

# Configuration
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OllamaConfig(BaseModel):
    """Configuration for Ollama integration"""
    embedding_model: str = Field(default="nomic-embed-text", description="Ollama embedding model")
    llm_model: str = Field(default="llama3.1:8b", description="Ollama LLM model")
    temperature: float = Field(default=0.1, description="LLM temperature for consistency")
    max_context: int = Field(default=32768, description="Maximum context length")
    max_predict: int = Field(default=2048, description="Maximum prediction length")
    base_url: str = Field(default="http://localhost:11434", description="Ollama server URL")
    timeout: int = Field(default=120, description="Request timeout in seconds")


class OllamaEngine:
    """
    Centralized Ollama integration engine for consistent local AI processing.
    
    Provides embeddings, chat completion, and prompt management across all
    domain templates while maintaining privacy and local processing.
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """Initialize Ollama engine with configuration"""
        self.config = config or OllamaConfig()
        
        # Initialize embeddings
        try:
            self.embeddings = OllamaEmbeddings(
                model=self.config.embedding_model,
                base_url=self.config.base_url
            )
            logger.info(f"🔗 Embedding model initialized: {self.config.embedding_model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize embeddings: {e}")
            raise
        
        # Initialize LLM
        try:
            self.llm = ChatOllama(
                model=self.config.llm_model,
                base_url=self.config.base_url,
                temperature=self.config.temperature,
                num_ctx=self.config.max_context,
                num_predict=self.config.max_predict,
                timeout=self.config.timeout
            )
            logger.info(f"🤖 LLM initialized: {self.config.llm_model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise
        
        # Track usage for monitoring
        self.usage_stats = {
            "embedding_calls": 0,
            "llm_calls": 0,
            "total_tokens": 0,
            "errors": 0
        }
        
        logger.info("✅ OllamaEngine initialized successfully")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents
        
        Args:
            texts: List of text documents
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embeddings.embed_documents(texts)
            self.usage_stats["embedding_calls"] += 1
            logger.debug(f"📊 Generated embeddings for {len(texts)} documents")
            return embeddings
        except Exception as e:
            self.usage_stats["errors"] += 1
            logger.error(f"❌ Embedding generation failed: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.embeddings.embed_query(text)
            self.usage_stats["embedding_calls"] += 1
            logger.debug(f"📊 Generated query embedding")
            return embedding
        except Exception as e:
            self.usage_stats["errors"] += 1
            logger.error(f"❌ Query embedding failed: {e}")
            raise
    
    def chat_completion(self, messages: Union[str, List[Dict[str, str]]], 
                       system_prompt: Optional[str] = None) -> str:
        """
        Generate chat completion
        
        Args:
            messages: Single message string or list of message dicts
            system_prompt: Optional system prompt
            
        Returns:
            Generated response
        """
        try:
            if isinstance(messages, str):
                # Simple string message
                if system_prompt:
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", system_prompt),
                        ("human", messages)
                    ])
                else:
                    prompt = ChatPromptTemplate.from_template(messages)
                
                chain = prompt | self.llm | StrOutputParser()
                response = chain.invoke({})
            else:
                # Structured message format
                prompt_messages = []
                if system_prompt:
                    prompt_messages.append(("system", system_prompt))
                
                for msg in messages:
                    role = msg.get("role", "human")
                    content = msg.get("content", "")
                    prompt_messages.append((role, content))
                
                prompt = ChatPromptTemplate.from_messages(prompt_messages)
                chain = prompt | self.llm | StrOutputParser()
                response = chain.invoke({})
            
            self.usage_stats["llm_calls"] += 1
            logger.debug(f"💬 Generated chat completion ({len(response)} chars)")
            return response
            
        except Exception as e:
            self.usage_stats["errors"] += 1
            logger.error(f"❌ Chat completion failed: {e}")
            raise
    
    def create_chain(self, prompt_template: str, 
                    input_variables: Optional[List[str]] = None) -> Runnable:
        """
        Create a reusable LangChain chain
        
        Args:
            prompt_template: Template string with variables
            input_variables: List of input variable names
            
        Returns:
            Configured LangChain chain
        """
        try:
            # In modern LangChain, input_variables are automatically inferred
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            chain = prompt | self.llm | StrOutputParser()
            logger.debug("🔗 Created LangChain chain")
            return chain
            
        except Exception as e:
            logger.error(f"❌ Chain creation failed: {e}")
            raise
    
    def extract_entities(self, text: str, entity_schema: Dict[str, str], 
                        max_entities_per_type: int = 5) -> Dict[str, List[str]]:
        """
        Extract entities using domain-specific schema
        
        Args:
            text: Input text
            entity_schema: Dict mapping entity types to descriptions
            max_entities_per_type: Maximum entities per category
            
        Returns:
            Extracted entities by category
        """
        entity_categories = list(entity_schema.keys())
        schema_description = {cat: desc for cat, desc in entity_schema.items()}
        
        prompt_template = f"""
Extract key entities from this text. Return ONLY a JSON object with these categories:

{{
{', '.join([f'  "{cat}": ["Item 1", "Item 2"]' for cat in entity_categories])}
}}

Entity Definitions:
{chr(10).join([f"- {cat}: {desc}" for cat, desc in schema_description.items()])}

Focus on the most important entities. Limit to {max_entities_per_type} items per category.

Text:
{{text}}

JSON:"""
        
        try:
            chain = self.create_chain(prompt_template, ["text"])
            result = chain.invoke({"text": text})
            
            # Parse JSON response
            import json
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                entities = json.loads(json_str)
                logger.debug(f"🔍 Extracted {sum(len(v) for v in entities.values())} entities")
                return entities
            else:
                # Fallback if JSON extraction fails
                logger.warning("⚠️ JSON extraction failed, returning empty entities")
                return {cat: [] for cat in entity_categories}
                
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            return {cat: [] for cat in entity_categories}
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check Ollama server health and model availability
        
        Returns:
            Health status and diagnostics
        """
        health_status = {
            "server_accessible": False,
            "embedding_model_available": False,
            "llm_model_available": False,
            "models": [],
            "config": self.config.model_dump(),
            "usage_stats": self.usage_stats
        }
        
        try:
            # Test embedding model
            test_embedding = self.embeddings.embed_query("test")
            if test_embedding:
                health_status["embedding_model_available"] = True
                health_status["server_accessible"] = True
        except Exception as e:
            logger.error(f"❌ Embedding model test failed: {e}")
        
        try:
            # Test LLM model
            test_response = self.llm.invoke("Say 'OK' if you can respond.")
            if test_response:
                health_status["llm_model_available"] = True
                health_status["server_accessible"] = True
        except Exception as e:
            logger.error(f"❌ LLM model test failed: {e}")
        
        return health_status
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get engine usage statistics"""
        return {
            **self.usage_stats,
            "config": self.config.model_dump(),
            "models": {
                "embedding": self.config.embedding_model,
                "llm": self.config.llm_model
            }
        }


# Factory function for easy initialization
def create_ollama_engine(embedding_model: str = "nomic-embed-text",
                        llm_model: str = "llama3.1:8b",
                        temperature: float = 0.1) -> OllamaEngine:
    """
    Factory function to create OllamaEngine with common configurations
    
    Args:
        embedding_model: Ollama embedding model name
        llm_model: Ollama LLM model name  
        temperature: LLM temperature setting
        
    Returns:
        Configured OllamaEngine instance
    """
    config = OllamaConfig(
        embedding_model=embedding_model,
        llm_model=llm_model,
        temperature=temperature
    )
    return OllamaEngine(config)
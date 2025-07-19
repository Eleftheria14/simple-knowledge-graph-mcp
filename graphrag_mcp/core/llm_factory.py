"""
Multi-Provider LLM Factory for GraphRAG

Provides unified interface for different LLM providers:
- Local: Ollama, LM Studio, LocalAI
- Cloud: OpenAI, Anthropic, Groq, Together AI
- Custom: Any OpenAI-compatible API
"""

import os
import logging
from typing import Optional, Dict, Any
from langchain_core.language_models import BaseLLM

from .config import ModelConfig

logger = logging.getLogger(__name__)


class UnsupportedProviderError(Exception):
    """Raised when an unsupported provider is requested"""
    pass


class LLMFactory:
    """Factory for creating LLM instances from different providers"""
    
    @staticmethod
    def create_llm(config: ModelConfig) -> BaseLLM:
        """
        Create LLM instance based on provider configuration.
        
        Args:
            config: Model configuration
            
        Returns:
            Configured LLM instance
            
        Raises:
            UnsupportedProviderError: If provider is not supported
            ImportError: If required packages are not installed
        """
        provider = config.provider.lower()
        
        logger.info(f"🤖 Creating LLM with provider: {provider}")
        logger.info(f"   📝 Model: {config.llm_model}")
        
        if provider == "ollama":
            return LLMFactory._create_ollama_llm(config)
        elif provider == "openai":
            return LLMFactory._create_openai_llm(config)
        elif provider == "anthropic":
            return LLMFactory._create_anthropic_llm(config)
        elif provider == "groq":
            return LLMFactory._create_groq_llm(config)
        elif provider == "together":
            return LLMFactory._create_together_llm(config)
        elif provider == "local_api":
            return LLMFactory._create_local_api_llm(config)
        else:
            raise UnsupportedProviderError(f"Provider '{provider}' is not supported")
    
    @staticmethod
    def _create_ollama_llm(config: ModelConfig) -> BaseLLM:
        """Create Ollama LLM instance"""
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError("langchain-ollama is required for Ollama support. Install with: pip install langchain-ollama")
        
        return ChatOllama(
            model=config.llm_model,
            base_url=config.ollama_base_url,
            temperature=config.temperature,
            num_ctx=config.max_context,
            num_predict=config.max_predict,
            timeout=config.timeout,
            keep_alive="1m"
        )
    
    @staticmethod
    def _create_openai_llm(config: ModelConfig) -> BaseLLM:
        """Create OpenAI LLM instance"""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai is required for OpenAI support. Install with: pip install langchain-openai")
        
        # Use API key from config or environment
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required. Set GRAPHRAG_API_KEY or OPENAI_API_KEY environment variable")
        
        kwargs = {
            "model": config.llm_model,
            "temperature": config.temperature,
            "max_tokens": config.max_predict,
            "timeout": config.timeout,
            "api_key": api_key
        }
        
        # Add custom base URL if provided
        if config.base_url:
            kwargs["base_url"] = config.base_url
        
        return ChatOpenAI(**kwargs)
    
    @staticmethod
    def _create_anthropic_llm(config: ModelConfig) -> BaseLLM:
        """Create Anthropic Claude LLM instance"""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("langchain-anthropic is required for Anthropic support. Install with: pip install langchain-anthropic")
        
        # Use API key from config or environment
        api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key required. Set GRAPHRAG_API_KEY or ANTHROPIC_API_KEY environment variable")
        
        return ChatAnthropic(
            model=config.llm_model,
            temperature=config.temperature,
            max_tokens=config.max_predict,
            timeout=config.timeout,
            anthropic_api_key=api_key
        )
    
    @staticmethod
    def _create_groq_llm(config: ModelConfig) -> BaseLLM:
        """Create Groq LLM instance"""
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            raise ImportError("langchain-groq is required for Groq support. Install with: pip install langchain-groq")
        
        # Use API key from config or environment
        api_key = config.api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Groq API key required. Set GRAPHRAG_API_KEY or GROQ_API_KEY environment variable")
        
        return ChatGroq(
            model=config.llm_model,
            temperature=config.temperature,
            max_tokens=config.max_predict,
            timeout=config.timeout,
            groq_api_key=api_key
        )
    
    @staticmethod
    def _create_together_llm(config: ModelConfig) -> BaseLLM:
        """Create Together AI LLM instance"""
        try:
            from langchain_together import ChatTogether
        except ImportError:
            raise ImportError("langchain-together is required for Together AI support. Install with: pip install langchain-together")
        
        # Use API key from config or environment
        api_key = config.api_key or os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("Together API key required. Set GRAPHRAG_API_KEY or TOGETHER_API_KEY environment variable")
        
        return ChatTogether(
            model=config.llm_model,
            temperature=config.temperature,
            max_tokens=config.max_predict,
            timeout=config.timeout,
            together_api_key=api_key
        )
    
    @staticmethod
    def _create_local_api_llm(config: ModelConfig) -> BaseLLM:
        """Create LLM instance for local OpenAI-compatible API (LM Studio, vLLM, etc.)"""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai is required for local API support. Install with: pip install langchain-openai")
        
        if not config.base_url:
            raise ValueError("base_url is required for local API provider")
        
        return ChatOpenAI(
            model=config.llm_model,
            base_url=config.base_url,
            api_key="dummy",  # Local APIs often don't need real keys
            temperature=config.temperature,
            max_tokens=config.max_predict,
            timeout=config.timeout
        )
    
    @staticmethod
    def get_supported_providers() -> Dict[str, Dict[str, Any]]:
        """Get information about supported providers"""
        return {
            "ollama": {
                "name": "Ollama",
                "description": "Local Ollama server",
                "requires_api_key": False,
                "example_models": ["llama3.1:8b", "llama3.1:70b", "codellama:13b", "mistral:7b"],
                "setup_url": "https://ollama.ai/"
            },
            "openai": {
                "name": "OpenAI",
                "description": "OpenAI GPT models",
                "requires_api_key": True,
                "example_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "setup_url": "https://platform.openai.com/"
            },
            "anthropic": {
                "name": "Anthropic Claude",
                "description": "Anthropic Claude models",
                "requires_api_key": True,
                "example_models": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
                "setup_url": "https://console.anthropic.com/"
            },
            "groq": {
                "name": "Groq",
                "description": "Fast inference with Groq",
                "requires_api_key": True,
                "example_models": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
                "setup_url": "https://console.groq.com/"
            },
            "together": {
                "name": "Together AI",
                "description": "Together AI hosted models",
                "requires_api_key": True,
                "example_models": ["meta-llama/Llama-3-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
                "setup_url": "https://api.together.xyz/"
            },
            "local_api": {
                "name": "Local API",
                "description": "OpenAI-compatible local server (LM Studio, vLLM, etc.)",
                "requires_api_key": False,
                "example_models": ["llama-3.1-8b", "custom-model"],
                "setup_url": "Configure base_url to your local server"
            }
        }


def validate_provider_config(config: ModelConfig) -> tuple[bool, str]:
    """
    Validate provider configuration.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    providers_info = LLMFactory.get_supported_providers()
    
    if config.provider not in providers_info:
        return False, f"Unsupported provider: {config.provider}"
    
    provider_info = providers_info[config.provider]
    
    # Check API key requirement
    if provider_info["requires_api_key"]:
        api_key = config.api_key or os.getenv(f"{config.provider.upper()}_API_KEY")
        if not api_key and config.provider != "openai":  # OpenAI has multiple env var options
            return False, f"API key required for {config.provider}. Set GRAPHRAG_API_KEY environment variable"
    
    # Check base URL for local API
    if config.provider == "local_api" and not config.base_url:
        return False, "base_url is required for local_api provider"
    
    return True, ""
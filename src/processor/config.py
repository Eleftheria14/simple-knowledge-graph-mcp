from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ProcessorConfig:
    # Required API keys
    groq_api_key: str = os.getenv('GROQ_API_KEY', '')
    llamaparse_api_key: str = os.getenv('LLAMAPARSE_API_KEY', '')
    
    # LLM Configuration
    model_name: str = "llama-3.1-8b-instant"
    temperature: float = 0.1
    
    # Processing limits
    max_concurrent_docs: int = 3
    
    # Neo4j connection (reuse from existing system)
    neo4j_uri: str = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_username: str = os.getenv('NEO4J_USERNAME', 'neo4j')
    neo4j_password: str = os.getenv('NEO4J_PASSWORD', 'password')
    
    # LangSmith (optional)
    langsmith_api_key: Optional[str] = os.getenv('LANGCHAIN_API_KEY')
    langsmith_project: str = os.getenv('LANGCHAIN_PROJECT', 'document-orchestrator')
    
    def validate(self) -> None:
        """Validate required configuration"""
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required")
        if not self.llamaparse_api_key:
            raise ValueError("LLAMAPARSE_API_KEY is required")
        print("✅ Configuration validated")

# Test your config
if __name__ == "__main__":
    config = ProcessorConfig()
    config.validate()
    print(f"Model: {config.model_name}")
    print(f"Neo4j URI: {config.neo4j_uri}")
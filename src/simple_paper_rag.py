"""
Simple Paper RAG + Knowledge Graph System
A streamlined tool for analyzing one scientific paper with RAG and basic knowledge graph extraction.
"""

import re
import json
from typing import List, Dict, Tuple, Optional
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimplePaperRAG:
    """
    Simple RAG system for analyzing one scientific paper at a time.
    No complex database setup - everything in memory for simplicity.
    """
    
    def __init__(self, embedding_model: str = "nomic-embed-text", 
                 llm_model: str = "llama3.1:8b"):
        """Initialize the RAG system"""
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.llm = ChatOllama(
            model=llm_model,
            temperature=0.1,
            num_ctx=32768,
            num_predict=2048
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Storage for current paper
        self.paper_data = {
            'title': '',
            'content': '',
            'chunks': [],
            'embeddings': None,
            'entities': {},
            'relationships': [],
            'citation': ''
        }
        
        # Chat history
        self.chat_history = []
        
        logger.info("🤖 SimplePaperRAG initialized")
    
    def load_paper(self, pdf_path: str) -> Dict:
        """
        Load and process a single paper
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with paper information
        """
        logger.info(f"📄 Loading paper: {pdf_path}")
        
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        full_text = "\n".join([doc.page_content for doc in documents])
        
        # Extract basic metadata
        title = self._extract_title(full_text)
        citation = self._extract_citation(full_text, Path(pdf_path).name)
        
        # Create chunks
        chunks = self.text_splitter.split_text(full_text)
        
        # Generate embeddings
        logger.info("🧠 Creating embeddings...")
        chunk_embeddings = self.embeddings.embed_documents(chunks)
        embeddings_array = np.array(chunk_embeddings)
        
        # Store paper data
        self.paper_data = {
            'title': title,
            'content': full_text,
            'chunks': chunks,
            'embeddings': embeddings_array,
            'entities': {},
            'relationships': [],
            'citation': citation,
            'pdf_path': pdf_path
        }
        
        logger.info(f"✅ Paper loaded: {len(chunks)} chunks, {len(full_text):,} characters")
        return {
            'title': title,
            'chunks': len(chunks),
            'characters': len(full_text),
            'citation': citation
        }
    
    def extract_entities(self) -> Dict:
        """
        Extract basic entities from the paper using LLM
        """
        if not self.paper_data['content']:
            raise ValueError("No paper loaded. Call load_paper() first.")
        
        logger.info("🔍 Extracting entities...")
        
        # Use first 3000 characters for entity extraction to stay within limits
        content_sample = self.paper_data['content'][:3000]
        
        entity_prompt = ChatPromptTemplate.from_template("""
Extract key entities from this scientific paper excerpt. Return ONLY a JSON object with these categories:

{{
  "authors": ["Author Name 1", "Author Name 2"],
  "methods": ["Method 1", "Method 2"],
  "concepts": ["Concept 1", "Concept 2"],
  "metrics": ["Metric 1", "Metric 2"],
  "tools": ["Tool 1", "Tool 2"]
}}

Focus on the most important entities. Limit to 5 items per category.

Paper excerpt:
{content}

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
            else:
                # Fallback if JSON extraction fails
                entities = {"authors": [], "methods": [], "concepts": [], "metrics": [], "tools": []}
            
            self.paper_data['entities'] = entities
            logger.info(f"✅ Extracted entities: {sum(len(v) for v in entities.values())} total")
            return entities
            
        except Exception as e:
            logger.error(f"❌ Entity extraction failed: {e}")
            # Return empty structure on failure
            entities = {"authors": [], "methods": [], "concepts": [], "metrics": [], "tools": []}
            self.paper_data['entities'] = entities
            return entities
    
    def query(self, question: str, top_k: int = 5) -> str:
        """
        Query the paper using RAG
        
        Args:
            question: Natural language question
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Generated answer
        """
        if not self.paper_data['content']:
            raise ValueError("No paper loaded. Call load_paper() first.")
        
        logger.info(f"❓ Query: {question}")
        
        # Create embedding for question
        question_embedding = self.embeddings.embed_query(question)
        question_array = np.array([question_embedding])
        
        # Find most similar chunks
        similarities = cosine_similarity(question_array, self.paper_data['embeddings'])[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Get relevant chunks
        relevant_chunks = [self.paper_data['chunks'][i] for i in top_indices]
        context = "\n\n".join(relevant_chunks)
        
        # Generate answer
        qa_prompt = ChatPromptTemplate.from_template("""
You are an expert scientific researcher. Answer the question based ONLY on the provided context from the research paper.

Context from paper:
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
            'similarity_scores': [similarities[i] for i in top_indices]
        })
        
        logger.info(f"✅ Answer generated ({len(answer)} chars)")
        return answer
    
    def chat(self, message: str) -> str:
        """
        Simple chat interface
        """
        return self.query(message)
    
    def get_entities_summary(self) -> str:
        """
        Get a formatted summary of extracted entities
        """
        if not self.paper_data['entities']:
            return "No entities extracted. Run extract_entities() first."
        
        summary = "🔍 **EXTRACTED ENTITIES**\n\n"
        
        for category, items in self.paper_data['entities'].items():
            if items:
                summary += f"**{category.title()}:**\n"
                for item in items:
                    summary += f"  • {item}\n"
                summary += "\n"
        
        return summary
    
    def get_paper_summary(self) -> Dict:
        """
        Get summary of current paper
        """
        if not self.paper_data['content']:
            return {"error": "No paper loaded"}
        
        return {
            'title': self.paper_data['title'],
            'citation': self.paper_data['citation'],
            'chunks': len(self.paper_data['chunks']),
            'entities': {k: len(v) for k, v in self.paper_data['entities'].items()},
            'chat_history': len(self.chat_history)
        }
    
    def _extract_title(self, text: str) -> str:
        """Extract paper title from text"""
        lines = text.split('\n')[:10]  # Look in first 10 lines
        
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
        title = self.paper_data.get('title', self._extract_title(text))
        
        # Look for year
        year_match = re.search(r'\b(20[0-2][0-9])\b', text[:2000])
        year = year_match.group(1) if year_match else "Unknown Year"
        
        # Look for DOI
        doi_match = re.search(r'(?:doi|DOI)[:.\s]*(10\.\d+/[^\s]+)', text[:3000])
        doi = doi_match.group(1) if doi_match else ""
        
        # Simple citation format
        citation = f"{title}. {year}"
        if doi:
            citation += f". DOI: {doi}"
        
        return citation


# Convenience function for quick use
def analyze_paper(pdf_path: str, questions: List[str] = None) -> Dict:
    """
    Quick function to analyze a paper
    
    Args:
        pdf_path: Path to PDF
        questions: Optional list of questions to ask
        
    Returns:
        Analysis results
    """
    rag = SimplePaperRAG()
    
    # Load paper
    paper_info = rag.load_paper(pdf_path)
    
    # Extract entities
    entities = rag.extract_entities()
    
    # Answer questions if provided
    qa_results = []
    if questions:
        for q in questions:
            answer = rag.query(q)
            qa_results.append({'question': q, 'answer': answer})
    
    return {
        'paper_info': paper_info,
        'entities': entities,
        'qa_results': qa_results,
        'rag_system': rag  # Return the system for interactive use
    }


if __name__ == "__main__":
    # Test the system
    test_pdf = "../examples/d4sc03921a.pdf"
    
    if Path(test_pdf).exists():
        print("🧪 Testing SimplePaperRAG...")
        results = analyze_paper(test_pdf, [
            "What are the main findings?",
            "What methods were used?"
        ])
        
        print("✅ Test completed successfully!")
        print(f"📊 Results: {len(results['qa_results'])} questions answered")
    else:
        print("❌ Test PDF not found")
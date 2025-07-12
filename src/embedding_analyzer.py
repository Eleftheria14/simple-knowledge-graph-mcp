"""
Embedding-Based Document Analyzer
Uses semantic embeddings for intelligent content selection and summarization
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging
from sklearn.metrics.pairwise import cosine_similarity
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingAnalyzer:
    """
    Advanced document analyzer using semantic embeddings for intelligent content selection
    """
    
    def __init__(self, embedding_model: str = "nomic-embed-text", 
                 llm_model: str = "llama3.1:8b"):
        """
        Initialize the embedding analyzer
        
        Args:
            embedding_model: Ollama embedding model name
            llm_model: Ollama LLM model for analysis
        """
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.llm = ChatOllama(
            model=llm_model,
            temperature=0.1,
            num_ctx=32768,
            num_predict=4096
        )
        
        # Text splitter for semantic chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        logger.info(f"🤖 EmbeddingAnalyzer initialized with {embedding_model} + {llm_model}")
    
    def load_and_chunk_document(self, pdf_path: str) -> Tuple[str, List[str], List[str]]:
        """
        Load PDF and create semantic chunks
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (full_text, chunks, section_headers)
        """
        logger.info(f"📄 Loading and chunking document: {pdf_path}")
        
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        full_text = "\n".join([doc.page_content for doc in documents])
        
        # Detect section headers
        section_headers = self._extract_section_headers(full_text)
        
        # Create semantic chunks
        chunks = self.text_splitter.split_text(full_text)
        
        logger.info(f"📊 Document stats: {len(full_text):,} chars, {len(chunks)} chunks, {len(section_headers)} sections")
        
        return full_text, chunks, section_headers
    
    def _extract_section_headers(self, text: str) -> List[str]:
        """Extract section headers from document"""
        # Common academic paper section patterns
        section_patterns = [
            r'\n\d+\.?\s+([A-Z][A-Za-z\s]+)(?=\n)',
            r'\n([A-Z][A-Z\s]+)(?=\n)',
            r'\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\n)',
        ]
        
        sections = []
        for pattern in section_patterns:
            matches = re.findall(pattern, text)
            sections.extend(matches)
        
        # Filter for common academic sections
        academic_keywords = [
            'abstract', 'introduction', 'methods', 'methodology', 'results', 
            'discussion', 'conclusion', 'references', 'acknowledgments',
            'background', 'related work', 'experimental', 'analysis'
        ]
        
        filtered_sections = []
        for section in sections:
            if any(keyword in section.lower() for keyword in academic_keywords):
                filtered_sections.append(section.strip())
        
        return list(set(filtered_sections))  # Remove duplicates
    
    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        """
        Create embeddings for document chunks
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Numpy array of embeddings
        """
        logger.info(f"🧠 Creating embeddings for {len(chunks)} chunks...")
        
        try:
            # Create embeddings using Ollama
            embeddings_list = self.embeddings.embed_documents(chunks)
            embeddings_array = np.array(embeddings_list)
            
            logger.info(f"✅ Created embeddings: {embeddings_array.shape}")
            return embeddings_array
            
        except Exception as e:
            logger.error(f"❌ Embedding creation failed: {e}")
            raise
    
    def find_relevant_chunks(self, chunks: List[str], embeddings: np.ndarray, 
                           analysis_goals: List[str], top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Find most relevant chunks for analysis goals using semantic similarity
        
        Args:
            chunks: Document chunks
            embeddings: Chunk embeddings
            analysis_goals: List of analysis objectives
            top_k: Number of top chunks to return
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        logger.info(f"🔍 Finding relevant chunks for {len(analysis_goals)} analysis goals...")
        
        # Create embeddings for analysis goals
        goal_embeddings = self.embeddings.embed_documents(analysis_goals)
        goal_embeddings_array = np.array(goal_embeddings)
        
        # Calculate similarities
        similarities = cosine_similarity(embeddings, goal_embeddings_array)
        
        # Get max similarity for each chunk across all goals
        max_similarities = np.max(similarities, axis=1)
        
        # Get top-k most relevant chunks
        top_indices = np.argsort(max_similarities)[-top_k:][::-1]
        
        relevant_chunks = [
            (chunks[i], max_similarities[i]) 
            for i in top_indices
        ]
        
        logger.info(f"✅ Found {len(relevant_chunks)} relevant chunks (avg similarity: {np.mean([s for _, s in relevant_chunks]):.3f})")
        
        return relevant_chunks
    
    def create_smart_summary(self, relevant_chunks: List[Tuple[str, float]], 
                           analysis_type: str = "comprehensive") -> str:
        """
        Create intelligent summary from most relevant chunks
        
        Args:
            relevant_chunks: List of (chunk, similarity_score) tuples
            analysis_type: Type of analysis to perform
            
        Returns:
            Generated summary
        """
        logger.info(f"📝 Creating {analysis_type} summary from {len(relevant_chunks)} relevant chunks...")
        
        # Combine relevant chunks with similarity scores
        context = "\n\n".join([
            f"[Relevance: {score:.3f}] {chunk}" 
            for chunk, score in relevant_chunks
        ])
        
        # Create analysis prompt
        analysis_prompt = ChatPromptTemplate.from_template("""
You are an expert in scientific research analysis. You have been provided with the most semantically relevant sections from a research paper, ranked by relevance to key analysis objectives.

RELEVANT CONTENT (ranked by semantic similarity):
{context}

Generate a comprehensive {analysis_type} analysis focusing on:

**Executive Summary**
- Core scientific advancement and its impact
- Primary research domain and applications
- Key quantitative improvements demonstrated

**Technical Architecture & Methodology**
- Technical approach and implementation details
- Experimental setup and validation methods
- Performance metrics and benchmarks

**Scientific Applications & Impact**
- Demonstrated use cases and applications
- Comparison with existing approaches
- Research acceleration potential

**Strategic Implications**
- Impact on research productivity
- Implementation considerations
- Future research directions

Focus on extracting actionable insights and technical details from the provided relevant sections. Prioritize content with higher relevance scores.

ANALYSIS:
""")
        
        # Generate analysis
        analysis_chain = analysis_prompt | self.llm | StrOutputParser()
        
        try:
            summary = analysis_chain.invoke({
                "context": context,
                "analysis_type": analysis_type
            })
            
            logger.info(f"✅ Generated {len(summary):,} character summary")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Summary generation failed: {e}")
            raise
    
    def analyze_document(self, pdf_path: str, analysis_goals: Optional[List[str]] = None,
                        top_k_chunks: int = 10) -> Dict:
        """
        Complete embedding-based document analysis
        
        Args:
            pdf_path: Path to PDF file
            analysis_goals: List of analysis objectives (defaults to scientific R&D goals)
            top_k_chunks: Number of most relevant chunks to use
            
        Returns:
            Dictionary with analysis results
        """
        # Default analysis goals for scientific papers
        if analysis_goals is None:
            analysis_goals = [
                "technical methodology and experimental approach",
                "key results and performance metrics", 
                "scientific applications and use cases",
                "research implications and future directions",
                "implementation and deployment considerations"
            ]
        
        logger.info(f"🔬 Starting embedding-based analysis of {pdf_path}")
        
        # Load and chunk document
        full_text, chunks, section_headers = self.load_and_chunk_document(pdf_path)
        
        # Create embeddings
        embeddings = self.create_embeddings(chunks)
        
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(chunks, embeddings, analysis_goals, top_k_chunks)
        
        # Generate analysis
        summary = self.create_smart_summary(relevant_chunks, "comprehensive scientific")
        
        # Calculate metrics
        total_chars = len(full_text)
        relevant_chars = sum(len(chunk) for chunk, _ in relevant_chunks)
        coverage_percent = (relevant_chars / total_chars) * 100
        
        avg_relevance = np.mean([score for _, score in relevant_chunks])
        
        return {
            'summary': summary,
            'metrics': {
                'total_chunks': len(chunks),
                'relevant_chunks': len(relevant_chunks),
                'total_chars': total_chars,
                'relevant_chars': relevant_chars,
                'coverage_percent': coverage_percent,
                'avg_relevance_score': avg_relevance,
                'section_headers': section_headers
            },
            'relevant_chunks': relevant_chunks
        }


# Convenience function for quick analysis
def analyze_paper_with_embeddings(pdf_path: str, analysis_goals: Optional[List[str]] = None) -> Dict:
    """
    Quick function to analyze a paper using embeddings
    
    Args:
        pdf_path: Path to PDF file
        analysis_goals: Optional list of analysis objectives
        
    Returns:
        Analysis results dictionary
    """
    analyzer = EmbeddingAnalyzer()
    return analyzer.analyze_document(pdf_path, analysis_goals)


if __name__ == "__main__":
    # Test the embedding analyzer
    test_pdf = "../examples/d4sc03921a.pdf"
    logger.info("🧪 Testing EmbeddingAnalyzer...")
    
    try:
        results = analyze_paper_with_embeddings(test_pdf)
        print(f"✅ Analysis completed successfully!")
        print(f"📊 Coverage: {results['metrics']['coverage_percent']:.1f}% of document")
        print(f"🎯 Avg relevance: {results['metrics']['avg_relevance_score']:.3f}")
        print(f"📝 Summary length: {len(results['summary']):,} characters")
    except Exception as e:
        print(f"❌ Test failed: {e}")
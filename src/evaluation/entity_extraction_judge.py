"""LLM-as-a-Judge evaluation system for entity extraction quality assessment."""
from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass
from langchain_groq import ChatGroq
import os

@dataclass
class EntityExtractionResult:
    """Results from entity extraction to be evaluated"""
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    source_text: str
    extraction_config: Dict[str, Any]

@dataclass
class EvaluationCriteria:
    """Criteria for evaluating entity extraction"""
    entity_accuracy: float = 0.0  # 0-1 score
    relationship_accuracy: float = 0.0  # 0-1 score
    completeness: float = 0.0  # 0-1 score
    overall_score: float = 0.0  # 0-1 score
    feedback: str = ""
    
class EntityExtractionJudge:
    """LLM-as-a-Judge for evaluating entity extraction quality"""
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.model_name = model_name
        self.llm = ChatGroq(
            model=model_name,
            temperature=0.1,  # Low temperature for consistent evaluation
            groq_api_key=os.getenv('GROQ_API_KEY')
        )
    
    def evaluate_extraction(self, 
                          extraction_result: EntityExtractionResult,
                          ground_truth: Optional[Dict[str, Any]] = None) -> EvaluationCriteria:
        """
        Evaluate entity extraction results using LLM-as-a-judge
        
        Args:
            extraction_result: The extraction results to evaluate
            ground_truth: Optional ground truth for comparison (if available)
            
        Returns:
            EvaluationCriteria with scores and feedback
        """
        
        # Build evaluation prompt
        evaluation_prompt = self._build_evaluation_prompt(extraction_result, ground_truth)
        
        # Get LLM evaluation
        response = self.llm.invoke(evaluation_prompt)
        
        # Parse evaluation results
        return self._parse_evaluation_response(response.content)
    
    def _build_evaluation_prompt(self, 
                                extraction_result: EntityExtractionResult,
                                ground_truth: Optional[Dict[str, Any]] = None) -> str:
        """Build the evaluation prompt for the LLM judge"""
        
        entities_json = json.dumps(extraction_result.entities, indent=2)
        relationships_json = json.dumps(extraction_result.relationships, indent=2)
        
        base_prompt = f"""You are an expert evaluator for entity extraction systems. Evaluate the quality of the following entity extraction results.

SOURCE TEXT:
{extraction_result.source_text[:2000]}

EXTRACTED ENTITIES:
{entities_json}

EXTRACTED RELATIONSHIPS:
{relationships_json}

EVALUATION CRITERIA:
1. Entity Accuracy (0-1): Are the extracted entities correct and well-identified?
   - Check if entities are actual concepts/people/organizations from the text
   - Verify entity types are appropriate
   - Assess if confidence scores are reasonable

2. Relationship Accuracy (0-1): Are the relationships between entities valid?
   - Check if relationships actually exist in the text
   - Verify relationship types are appropriate
   - Assess if relationship contexts are accurate

3. Completeness (0-1): How complete is the extraction?
   - Are important entities missing?
   - Are key relationships overlooked?
   - Is the extraction comprehensive for the text length?

4. Overall Quality (0-1): General assessment of extraction quality

EVALUATION GUIDELINES:
- Be strict but fair in your evaluation
- Consider the complexity of the source text
- Look for hallucinated entities or relationships
- Check for missed obvious entities/relationships
- Assess whether confidence scores align with actual quality

"""

        if ground_truth:
            base_prompt += f"""
GROUND TRUTH (for comparison):
{json.dumps(ground_truth, indent=2)}

Compare the extraction results against this ground truth for more accurate scoring.
"""

        base_prompt += """
Return your evaluation in JSON format:
{
  "entity_accuracy": 0.85,
  "relationship_accuracy": 0.75,
  "completeness": 0.80,
  "overall_score": 0.80,
  "feedback": "Detailed feedback explaining the scores and areas for improvement..."
}

JSON Response:"""

        return base_prompt
    
    def _parse_evaluation_response(self, response_content: str) -> EvaluationCriteria:
        """Parse the LLM evaluation response into structured criteria"""
        
        try:
            # Extract JSON from response
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_content[json_start:json_end]
                eval_data = json.loads(json_str)
                
                return EvaluationCriteria(
                    entity_accuracy=eval_data.get("entity_accuracy", 0.0),
                    relationship_accuracy=eval_data.get("relationship_accuracy", 0.0),
                    completeness=eval_data.get("completeness", 0.0),
                    overall_score=eval_data.get("overall_score", 0.0),
                    feedback=eval_data.get("feedback", "No feedback provided")
                )
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"Error parsing evaluation response: {e}")
            return EvaluationCriteria(
                feedback=f"Failed to parse evaluation: {str(e)}"
            )
    
    def batch_evaluate(self, 
                      extraction_results: List[EntityExtractionResult],
                      ground_truths: Optional[List[Dict[str, Any]]] = None) -> List[EvaluationCriteria]:
        """Evaluate multiple extraction results"""
        
        evaluations = []
        ground_truths = ground_truths or [None] * len(extraction_results)
        
        for i, (result, gt) in enumerate(zip(extraction_results, ground_truths)):
            print(f"Evaluating extraction {i+1}/{len(extraction_results)}...")
            evaluation = self.evaluate_extraction(result, gt)
            evaluations.append(evaluation)
            
        return evaluations
    
    def generate_evaluation_report(self, evaluations: List[EvaluationCriteria]) -> Dict[str, Any]:
        """Generate a comprehensive evaluation report"""
        
        if not evaluations:
            return {"error": "No evaluations provided"}
        
        # Calculate aggregate metrics
        entity_scores = [e.entity_accuracy for e in evaluations if e.entity_accuracy > 0]
        relationship_scores = [e.relationship_accuracy for e in evaluations if e.relationship_accuracy > 0]
        completeness_scores = [e.completeness for e in evaluations if e.completeness > 0]
        overall_scores = [e.overall_score for e in evaluations if e.overall_score > 0]
        
        report = {
            "total_evaluations": len(evaluations),
            "metrics": {
                "entity_accuracy": {
                    "mean": sum(entity_scores) / len(entity_scores) if entity_scores else 0,
                    "min": min(entity_scores) if entity_scores else 0,
                    "max": max(entity_scores) if entity_scores else 0
                },
                "relationship_accuracy": {
                    "mean": sum(relationship_scores) / len(relationship_scores) if relationship_scores else 0,
                    "min": min(relationship_scores) if relationship_scores else 0,
                    "max": max(relationship_scores) if relationship_scores else 0
                },
                "completeness": {
                    "mean": sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0,
                    "min": min(completeness_scores) if completeness_scores else 0,
                    "max": max(completeness_scores) if completeness_scores else 0
                },
                "overall_score": {
                    "mean": sum(overall_scores) / len(overall_scores) if overall_scores else 0,
                    "min": min(overall_scores) if overall_scores else 0,
                    "max": max(overall_scores) if overall_scores else 0
                }
            },
            "detailed_feedback": [e.feedback for e in evaluations]
        }
        
        return report

# Example usage for integration with existing system
def evaluate_entity_extraction_tool():
    """Example function showing how to integrate with existing extraction system"""
    
    # This would be called after running extract_and_store_entities
    judge = EntityExtractionJudge()
    
    # Sample extraction result (would come from your actual extraction)
    sample_result = EntityExtractionResult(
        entities=[
            {"id": "ent1", "name": "Machine Learning", "type": "concept", "confidence": 0.9},
            {"id": "ent2", "name": "Neural Networks", "type": "concept", "confidence": 0.85}
        ],
        relationships=[
            {"source": "ent1", "target": "ent2", "type": "INCLUDES", "context": "ML includes neural networks", "confidence": 0.8}
        ],
        source_text="Machine learning is a subset of artificial intelligence that includes neural networks...",
        extraction_config={"model": "llama-3.1-8b-instant", "confidence_threshold": 0.7}
    )
    
    # Evaluate the extraction
    evaluation = judge.evaluate_extraction(sample_result)
    
    print(f"Entity Accuracy: {evaluation.entity_accuracy}")
    print(f"Relationship Accuracy: {evaluation.relationship_accuracy}")
    print(f"Completeness: {evaluation.completeness}")
    print(f"Overall Score: {evaluation.overall_score}")
    print(f"Feedback: {evaluation.feedback}")
    
    return evaluation

if __name__ == "__main__":
    # Test the evaluation system
    evaluate_entity_extraction_tool()
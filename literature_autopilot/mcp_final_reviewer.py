import json
import os
from typing import Dict, Tuple
from llm_utils import RotatableModel

class MCPFinalReviewer:
    """
    Uses Manus MCP to perform final review of the paper.
    Iteratively improves the paper until A+ quality is achieved.
    """
    
    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        self.model = RotatableModel(model_name)
        self.max_iterations = 5
        self.quality_threshold = 90  # 0-100 scale
    
    def review_paper_via_mcp(self, paper_text: str, focus_areas: list = None) -> Dict:
        """
        Send paper to Manus via MCP for comprehensive review.
        
        Args:
            paper_text: Full paper content
            focus_areas: List of areas to focus on (e.g., ["PRISMA compliance", "depth of analysis"])
        
        Returns:
            Review result with quality score and feedback
        """
        
        focus_instruction = ""
        if focus_areas:
            focus_instruction = f"\n\nPLEASE FOCUS ON: {', '.join(focus_areas)}"
        
        prompt = f"""
        You are an expert academic reviewer and editor. You are reviewing a 50-page 
        Systematic Literature Review on "LLM Self-Improvement".
        
        **EVALUATION CRITERIA**:
        1. PRISMA 2020 Compliance (27-item checklist)
        2. A+ Publication Standards (top-tier venue)
        3. Depth of Analysis (not just summarization)
        4. Methodological Rigor
        5. Academic Writing Quality
        6. Structure and Flow
        7. Citation Quality and Completeness
        8. Clarity and Precision
        
        **PAPER TO REVIEW**:
        {paper_text}
        
        {focus_instruction}
        
        **YOUR TASK**:
        Provide a comprehensive review in the following JSON format:
        
        {{
          "overall_quality_score": 0-100,  // 0=Reject, 50=Acceptable, 75=Good, 90+=A+
          "strengths": [
            "Strength 1 with specific examples",
            "Strength 2 with specific examples"
          ],
          "weaknesses": [
            {{
              "area": "Area name (e.g., 'PRISMA Compliance')",
              "severity": "CRITICAL / MAJOR / MINOR",
              "issue": "Specific issue description",
              "impact": "How this affects quality",
              "suggestion": "Specific improvement suggestion"
            }}
          ],
          "detailed_feedback": {{
            "prisma_compliance": "Assessment of PRISMA 2020 compliance",
            "depth_of_analysis": "Assessment of analytical depth",
            "methodological_rigor": "Assessment of rigor",
            "writing_quality": "Assessment of writing",
            "structure_and_flow": "Assessment of structure",
            "citation_quality": "Assessment of citations"
          }},
          "convergence_assessment": {{
            "is_converged": true/false,
            "reason": "Why the paper has/hasn't converged to A+ quality",
            "next_steps": "What should be done next"
          }},
          "priority_improvements": [
            "Top improvement 1",
            "Top improvement 2",
            "Top improvement 3"
          ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            review_text = response.text.strip()
            
            # Parse JSON from response
            if "```json" in review_text:
                review_text = review_text.split("```json")[1].split("```")[0]
            
            review_data = json.loads(review_text)
            return review_data
            
        except Exception as e:
            print(f"Error in MCP review: {e}")
            return {
                "overall_quality_score": 0,
                "error": str(e)
            }
    
    def iterative_improvement_loop(self, paper_text: str, initial_focus_areas: list = None) -> Tuple[str, Dict]:
        """
        Iteratively improves the paper until A+ quality is achieved.
        
        Returns:
            (improved_paper_text, final_review)
        """
        
        current_paper = paper_text
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"ITERATION {iteration}/{self.max_iterations}")
            print(f"{'='*60}")
            
            # Get review from Manus
            print("Sending paper to Manus for review...")
            review = self.review_paper_via_mcp(
                current_paper,
                focus_areas=initial_focus_areas if iteration == 1 else None
            )
            
            quality_score = review.get("overall_quality_score", 0)
            print(f"Quality Score: {quality_score}/100")
            
            # Check convergence
            if quality_score >= self.quality_threshold:
                print(f"\n✅ A+ QUALITY ACHIEVED! (Score: {quality_score}/100)")
                return current_paper, review
            
            # Extract improvements needed
            weaknesses = review.get("weaknesses", [])
            priority_improvements = review.get("priority_improvements", [])
            
            print(f"\nWeaknesses identified: {len(weaknesses)}")
            print("Priority improvements:")
            for i, improvement in enumerate(priority_improvements[:3], 1):
                print(f"  {i}. {improvement}")
            
            # Prepare rewriting prompt
            print("\nRewriting paper to address feedback...")
            rewrite_prompt = f"""
            You are a world-class academic writer. You are revising a 50-page SLR paper.
            
            **ORIGINAL PAPER**:
            {current_paper}
            
            **REVIEW FEEDBACK**:
            Quality Score: {quality_score}/100
            
            Weaknesses:
            {json.dumps(weaknesses, indent=2)}
            
            Priority Improvements:
            {json.dumps(priority_improvements, indent=2)}
            
            **YOUR TASK**:
            Rewrite the paper to address ALL feedback points. Specifically:
            1. Address each weakness mentioned above
            2. Implement all priority improvements
            3. Maintain the overall structure and citations
            4. Improve clarity, depth, and rigor
            5. Ensure PRISMA 2020 compliance
            
            Output ONLY the revised paper in Markdown format.
            Do not include commentary or explanations.
            """
            
            try:
                response = self.model.generate_content(rewrite_prompt)
                current_paper = response.text.strip()
                print("Paper revised successfully.")
            except Exception as e:
                print(f"Error during rewriting: {e}")
                return current_paper, review
        
        # Max iterations reached
        print(f"\n⚠️ Max iterations ({self.max_iterations}) reached.")
        print(f"Final quality score: {quality_score}/100")
        final_review = self.review_paper_via_mcp(current_paper)
        
        return current_paper, final_review

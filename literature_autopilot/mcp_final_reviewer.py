import json
import os
from typing import Dict, Tuple
from llm_utils import RotatableModel

class MCPFinalReviewer:
    """
    Uses Manus MCP to perform final review of the paper.
    Iteratively improves the paper until A+ quality is achieved.
    Now includes convergence analysis and targeted patching.
    """
    
    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        self.model = RotatableModel(model_name)
        self.max_iterations = 5
        self.quality_threshold = 90  # 0-100 scale
        self.quality_history = []  # Track scores over iterations
    
    def review_paper_via_mcp(self, paper_text: str, focus_areas: list = None) -> Dict:
        """
        Send paper to Manus via MCP for comprehensive review.
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
        {paper_text[:50000]} ... (truncated for context limit if needed)
        
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
            # Note: In a real scenario, we would chunk the paper or use a model with huge context.
            # Gemini 1.5 Pro has 1M+ context, so passing the full paper is usually fine.
            # The truncation above is just a placeholder safeguard in the prompt string construction.
            # We pass the full text to the model.
            full_prompt = prompt.replace(f"{paper_text[:50000]} ... (truncated for context limit if needed)", paper_text)
            
            response = self.model.generate_content(full_prompt)
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

    def analyze_convergence(self) -> Dict:
        """Analyze if the paper is converging or stuck."""
        if len(self.quality_history) < 2:
            return {"status": "insufficient_data"}
        
        scores = self.quality_history
        recent_trend = scores[-2:] if len(scores) >= 2 else scores
        
        # Check if improving
        is_improving = recent_trend[-1] > recent_trend[0]
        improvement_rate = recent_trend[-1] - recent_trend[0]
        
        # Check if stuck
        is_stuck = improvement_rate < 2  # Less than 2 points improvement
        
        return {
            "status": "improving" if is_improving else "stuck",
            "improvement_rate": improvement_rate,
            "is_stuck": is_stuck,
            "scores": scores
        }
    
    def targeted_patch_strategy(self, review: Dict) -> str:
        """Generate a targeted patching strategy instead of full rewrite."""
        
        weaknesses = review.get("weaknesses", [])
        critical_issues = [w for w in weaknesses if w.get("severity") == "CRITICAL"]
        major_issues = [w for w in weaknesses if w.get("severity") == "MAJOR"]
        
        if not critical_issues and not major_issues:
            return "POLISH"  # Only minor issues, just polish
        
        if len(critical_issues) <= 2:
            return "TARGETED_PATCH"  # Fix specific sections
        
        return "FULL_REWRITE"  # Too many issues, rewrite

    def iterative_improvement_loop(self, paper_text: str, initial_focus_areas: list = None) -> Tuple[str, Dict]:
        """
        Iteratively improves the paper until A+ quality is achieved.
        Now uses convergence analysis and targeted patching.
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
            self.quality_history.append(quality_score)
            print(f"Quality Score: {quality_score}/100")
            
            # Check convergence
            if quality_score >= self.quality_threshold:
                print(f"\n✅ A+ QUALITY ACHIEVED! (Score: {quality_score}/100)")
                return current_paper, review
            
            # Analyze convergence
            convergence = self.analyze_convergence()
            if convergence.get("is_stuck"):
                print(f"⚠️ STUCK: Improvement rate is low. Trying different strategy...")
                # Could try different approach here, but for now we proceed
            
            # Determine patching strategy
            strategy = self.targeted_patch_strategy(review)
            print(f"Patching Strategy: {strategy}")
            
            # Apply strategy
            if strategy == "POLISH":
                print("  Applying Polish...")
                current_paper = self._polish_paper(current_paper, review)
            elif strategy == "TARGETED_PATCH":
                print("  Applying Targeted Patch...")
                current_paper = self._targeted_patch(current_paper, review)
            else:
                print("  Applying Full Rewrite...")
                current_paper = self._full_rewrite(current_paper, review)
        
        # Max iterations reached
        print(f"\n⚠️ Max iterations ({self.max_iterations}) reached.")
        print(f"Final quality score: {quality_score}/100")
        final_review = self.review_paper_via_mcp(current_paper)
        
        return current_paper, final_review

    def _full_rewrite(self, paper: str, review: Dict) -> str:
        """Rewrite the entire paper based on feedback."""
        weaknesses = review.get("weaknesses", [])
        priority_improvements = review.get("priority_improvements", [])
        
        rewrite_prompt = f"""
        You are a world-class academic writer. You are revising a 50-page SLR paper.
        
        **ORIGINAL PAPER**:
        {paper}
        
        **REVIEW FEEDBACK**:
        Quality Score: {review.get('overall_quality_score')}/100
        
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
            return response.text.strip()
        except Exception as e:
            print(f"Error during rewriting: {e}")
            return paper

    def _targeted_patch(self, paper: str, review: Dict) -> str:
        """Patch only specific sections instead of rewriting entire paper."""
        
        weaknesses = review.get("weaknesses", [])
        critical_issues = [w for w in weaknesses if w.get("severity") == "CRITICAL"]
        
        current_paper = paper
        
        # For each critical issue, identify the section and patch it
        for issue in critical_issues[:3]:  # Max 3 patches per iteration
            area = issue.get("area")
            suggestion = issue.get("suggestion")
            print(f"    Patching area: {area}...")
            
            patch_prompt = f"""
            You are an expert editor. The paper has an issue in the '{area}' section:
            
            **Issue**: {issue.get('issue')}
            **Suggestion**: {suggestion}
            
            **Original Paper**:
            {current_paper}
            
            **Your Task**: 
            Find the relevant section in the paper and apply the fix.
            Output ONLY the corrected paper.
            """
            
            try:
                response = self.model.generate_content(patch_prompt)
                current_paper = response.text.strip()
            except Exception as e:
                print(f"    Patch failed: {e}")
        
        return current_paper

    def _polish_paper(self, paper: str, review: Dict) -> str:
        """Polish the paper for final submission (minor edits)."""
        polish_prompt = f"""
        You are an expert copyeditor. Polish the following paper for final submission.
        Focus on flow, clarity, and academic tone. Fix any minor issues identified in the review.
        
        **Review Feedback**:
        {json.dumps(review.get('weaknesses', []), indent=2)}
        
        **Paper**:
        {paper}
        
        Output ONLY the polished paper.
        """
        try:
            response = self.model.generate_content(polish_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"    Polish failed: {e}")
            return paper

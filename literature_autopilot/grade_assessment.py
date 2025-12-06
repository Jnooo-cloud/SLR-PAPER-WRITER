from typing import Dict, Any

class GRADEAssessment:
    """Assess certainty of evidence using GRADE framework."""
    
    @staticmethod
    def assess_certainty(study_quality: str, consistency: str = "CONSISTENT", 
                        directness: str = "DIRECT", precision: str = "PRECISE") -> Dict[str, Any]:
        """
        GRADE Framework:
        - HIGH: Further research very unlikely to change confidence
        - MODERATE: Further research may change confidence
        - LOW: Further research very likely to change confidence
        - VERY LOW: Any estimate is very uncertain
        
        Args:
            study_quality: HIGH, MEDIUM, LOW (from AMSTAR 2 Lite)
            consistency: CONSISTENT, INCONSISTENT (across studies)
            directness: DIRECT, INDIRECT (applicability to RQ)
            precision: PRECISE, IMPRECISE (confidence intervals/sample size)
        """
        
        downgrades = 0
        reasons = []
        
        # 1. Risk of Bias (Study Quality)
        if study_quality == "LOW":
            downgrades += 2
            reasons.append("High risk of bias (Low study quality)")
        elif study_quality == "MEDIUM":
            downgrades += 1
            reasons.append("Moderate risk of bias")
            
        # 2. Inconsistency
        if consistency == "INCONSISTENT":
            downgrades += 1
            reasons.append("Inconsistent results across studies")
            
        # 3. Indirectness
        if directness == "INDIRECT":
            downgrades += 1
            reasons.append("Indirect evidence (population/intervention mismatch)")
            
        # 4. Imprecision
        if precision == "IMPRECISE":
            downgrades += 1
            reasons.append("Imprecise results (small sample/wide CI)")
            
        # Determine Final Grade
        if downgrades == 0:
            grade = "HIGH"
        elif downgrades == 1:
            grade = "MODERATE"
        elif downgrades == 2:
            grade = "LOW"
        else:
            grade = "VERY LOW"
            
        return {
            "grade": grade,
            "downgrades": downgrades,
            "reasons": reasons
        }

    @staticmethod
    def generate_grade_summary(assessments: list) -> str:
        """Generate a summary table of GRADE assessments."""
        if not assessments:
            return "No GRADE assessments available."
            
        summary = "### GRADE Certainty of Evidence\n\n"
        summary += "| Outcome | Certainty | Reasons for Downgrading |\n"
        summary += "| :--- | :--- | :--- |\n"
        
        for a in assessments:
            outcome = a.get("outcome", "Overall")
            grade = a.get("grade", "N/A")
            reasons = ", ".join(a.get("reasons", [])) or "None"
            summary += f"| {outcome} | **{grade}** | {reasons} |\n"
            
        return summary

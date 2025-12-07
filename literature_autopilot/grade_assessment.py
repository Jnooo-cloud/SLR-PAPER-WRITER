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

    @classmethod
    def assess_certainty_comprehensive(cls, studies_data: list) -> Dict[str, Any]:
        """
        Comprehensive GRADE assessment based on a list of studies.
        """
        rob = cls.assess_risk_of_bias(studies_data)
        inconsistency = cls.assess_inconsistency(studies_data)
        indirectness = cls.assess_indirectness(studies_data)
        imprecision = cls.assess_imprecision(studies_data)
        
        # Map to assess_certainty args
        # Risk of Bias HIGH -> Low Quality
        quality_map = {"HIGH": "LOW", "LOW": "HIGH", "UNKNOWN": "MEDIUM"}
        
        return cls.assess_certainty(
            study_quality=quality_map.get(rob, "MEDIUM"),
            consistency="INCONSISTENT" if inconsistency == "HIGH" else "CONSISTENT",
            directness="INDIRECT" if indirectness == "HIGH" else "DIRECT",
            precision="IMPRECISE" if imprecision == "HIGH" else "PRECISE"
        )

    @staticmethod
    def assess_risk_of_bias(studies_data):
        low_quality_count = 0
        for s in studies_data:
            score = s.get("amstar_2_assessment", {}).get("overall_score", "UNKNOWN")
            if score in ["LOW", "CRITICALLY LOW"]:
                low_quality_count += 1
        
        if not studies_data: return "UNKNOWN"
        if low_quality_count / len(studies_data) > 0.5:
            return "HIGH"
        return "LOW"

    @staticmethod
    def assess_inconsistency(studies_data):
        # Placeholder: Check for conflicting results if available
        return "LOW"

    @staticmethod
    def assess_indirectness(studies_data):
        # Placeholder
        return "LOW"

    @staticmethod
    def assess_imprecision(studies_data):
        # Placeholder
        return "LOW"

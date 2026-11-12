"""
Skill Gap Analyzer Module for SkillMatch AI
Performs deep-dive gap analysis between candidate skills and job requirements,
classifying missing skills into priority tiers (Critical, High, Medium) with actionable recommendations.
"""
import json
import os
from typing import Dict, List, Optional

class SkillGapAnalyzer:
    def __init__(self, learning_resources_path: str = "data/learning_resources.json"):
        self.learning_resources_path = learning_resources_path
        self.resources_catalog = self._load_resources()

    def _load_resources(self) -> dict:
        if os.path.exists(self.learning_resources_path):
            with open(self.learning_resources_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def analyze_gaps(
        self,
        candidate_skills: List[str],
        required_tech: List[str],
        required_soft: List[str],
        preferred_skills: Optional[List[str]] = None
    ) -> dict:
        """
        Conducts comprehensive gap analysis, prioritizing missing skills and generating
        actionable learning recommendations.
        """
        cand_set = set(candidate_skills)
        tech_set = set(required_tech or [])
        soft_set = set(required_soft or [])
        pref_set = set(preferred_skills or [])

        possessed_tech = sorted(list(cand_set.intersection(tech_set)))
        missing_tech = sorted(list(tech_set - cand_set))

        possessed_soft = sorted(list(cand_set.intersection(soft_set)))
        missing_soft = sorted(list(soft_set - cand_set))

        missing_preferred = sorted(list(pref_set - cand_set))

        total_required = len(tech_set) + len(soft_set)
        total_possessed = len(possessed_tech) + len(possessed_soft)
        coverage_pct = round((total_possessed / total_required * 100.0), 1) if total_required > 0 else 100.0

        # Prioritize missing skills
        # Critical: Required technical skills marked critical in catalog, or first 3 primary tech skills
        prioritized_gaps = []
        
        for skill in missing_tech:
            res_meta = self.resources_catalog.get(skill, {})
            importance = res_meta.get("importance", "High")
            
            # If skill is in core tech requirements, ensure it's at least High
            if importance not in ["Critical", "High"]:
                importance = "High"
                
            prioritized_gaps.append({
                "skill": skill,
                "category": "Technical",
                "importance": importance,
                "urgency": "Immediate Priority" if importance == "Critical" else "Secondary Priority",
                "rationale": f"Core requirement for this role. Lacking {skill} reduces technical match score significantly."
            })

        for skill in missing_soft:
            prioritized_gaps.append({
                "skill": skill,
                "category": "Soft Skill",
                "importance": "Medium",
                "urgency": "Moderate Priority",
                "rationale": f"Enhances team collaboration, stakeholder interaction, and professional readiness."
            })

        for skill in missing_preferred:
            if skill not in missing_tech:
                prioritized_gaps.append({
                    "skill": skill,
                    "category": "Preferred / Bonus",
                    "importance": "Low / Bonus",
                    "urgency": "Bonus Enhancement",
                    "rationale": f"Differentiator skill that sets top candidates apart in competitive pools."
                })

        # Sort: Critical first, then High, then Medium, then Low
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low / Bonus": 3}
        prioritized_gaps.sort(key=lambda x: priority_order.get(x["importance"], 9))

        # Actionable recommendations
        action_recommendations = []
        if len(missing_tech) == 0:
            action_recommendations.append("Outstanding technical coverage! Focus on project portfolio demonstration and system design.")
        elif len(missing_tech) <= 2:
            action_recommendations.append(f"Targeted sprint needed: Close the remaining gaps in {', '.join(missing_tech)} to become a top-tier candidate.")
        else:
            top_3 = [g["skill"] for g in prioritized_gaps[:3]]
            action_recommendations.append(f"Phased learning suggested: Focus immediately on foundational missing skills: {', '.join(top_3)}.")

        if missing_soft:
            action_recommendations.append("Highlight collaborative project experiences and cross-functional deliverables to demonstrate soft skill competencies.")

        return {
            "coverage_percentage": coverage_pct,
            "total_required": total_required,
            "total_possessed": total_possessed,
            "possessed_skills": {
                "technical": possessed_tech,
                "soft": possessed_soft
            },
            "missing_skills": {
                "technical": missing_tech,
                "soft": missing_soft,
                "preferred": missing_preferred
            },
            "prioritized_gaps": prioritized_gaps,
            "top_missing_skills": [g["skill"] for g in prioritized_gaps if g["importance"] in ["Critical", "High"]][:5],
            "action_recommendations": action_recommendations
        }


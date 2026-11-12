"""
Roadmap Generator Module for SkillMatch AI
Constructs personalized, sequenced learning paths with Beginner, Intermediate, and Advanced stages
paired with authentic, verified learning documentation and courses.
"""
import json
import os
from typing import List, Dict, Optional

class RoadmapGenerator:
    def __init__(self, catalog_path: str = "data/learning_resources.json"):
        self.catalog_path = catalog_path
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> dict:
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate_roadmap(self, missing_skills: List[str]) -> List[dict]:
        """
        Creates a structured, sequenced roadmap for missing skills.
        Sequence: Critical skills first (Weeks 1-4), High importance (Weeks 5-8), Medium (Weeks 9-12).
        """
        default_res = self.catalog.get("Default_Resource", {
            "importance": "Medium",
            "description": "Fundamental core concepts and practical real-world exercises.",
            "stages": {
                "Beginner": {
                    "topics": "Fundamentals, syntax, architecture overview, hands-on getting started guide",
                    "resources": [{"title": "Roadmap.sh Developer Guide", "url": "https://roadmap.sh/", "type": "Interactive Guide", "free": True}]
                },
                "Intermediate": {
                    "topics": "Design patterns, intermediate tooling, best practices, modular implementations",
                    "resources": [{"title": "freeCodeCamp Curriculum", "url": "https://www.freecodecamp.org/", "type": "Interactive Course", "free": True}]
                },
                "Advanced": {
                    "topics": "Scalability, optimization, monitoring, security, enterprise production deployment",
                    "resources": [{"title": "MDN / Official Documentation", "url": "https://developer.mozilla.org/", "type": "Documentation", "free": True}]
                }
            }
        })

        roadmap_items = []
        
        # Sort skills by priority: Known catalog skills first, critical first
        priority_map = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
        
        indexed_skills = []
        for skill in missing_skills:
            meta = self.catalog.get(skill, default_res)
            importance = meta.get("importance", "Medium")
            indexed_skills.append((priority_map.get(importance, 3), skill, meta))

        indexed_skills.sort(key=lambda x: (x[0], x[1]))

        current_week_start = 1
        for step_idx, (_, skill, meta) in enumerate(indexed_skills, 1):
            importance = meta.get("importance", "Medium")
            description = meta.get("description", f"Practical proficiency and implementation of {skill}.")
            stages = meta.get("stages", default_res["stages"])
            
            duration_weeks = 4 if importance == "Critical" else (3 if importance == "High" else 2)
            timeframe = f"Weeks {current_week_start} – {current_week_start + duration_weeks - 1}"
            current_week_start += duration_weeks

            roadmap_items.append({
                "step_number": step_idx,
                "skill": skill,
                "importance": importance,
                "timeframe": timeframe,
                "description": description,
                "stages": {
                    "Beginner": stages.get("Beginner", default_res["stages"]["Beginner"]),
                    "Intermediate": stages.get("Intermediate", default_res["stages"]["Intermediate"]),
                    "Advanced": stages.get("Advanced", default_res["stages"]["Advanced"])
                }
            })

        return roadmap_items


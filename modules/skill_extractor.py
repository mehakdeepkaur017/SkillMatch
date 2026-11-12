"""
Skill Extractor Module for SkillMatch AI
Performs robust taxonomy-based skill extraction, alias resolution, and categorization
for both technical and soft skills.
"""
import re
import json
import os
from typing import Dict, List, Set, Tuple

class SkillExtractor:
    def __init__(self, taxonomy_path: str = "data/skills_taxonomy.json"):
        self.taxonomy_path = taxonomy_path
        self.taxonomy = self._load_taxonomy()
        
        # Build canonical maps and lookup indexes
        self.canonical_tech_skills = {}  # {canonical_name: subcategory}
        self.canonical_soft_skills = {}  # {canonical_name: subcategory}
        self.all_canonical_skills = set()
        
        for subcat, skills in self.taxonomy.get("technical_skills", {}).items():
            for skill in skills:
                self.canonical_tech_skills[skill] = subcat
                self.all_canonical_skills.add(skill)
                
        for subcat, skills in self.taxonomy.get("soft_skills", {}).items():
            for skill in skills:
                self.canonical_soft_skills[skill] = subcat
                self.all_canonical_skills.add(skill)
                
        self.aliases = self.taxonomy.get("aliases", {})
        
        # Compile regex patterns for fast, boundary-aware matching
        self._compile_patterns()

    def _load_taxonomy(self) -> dict:
        if os.path.exists(self.taxonomy_path):
            with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"technical_skills": {}, "soft_skills": {}, "aliases": {}}

    def _compile_patterns(self):
        """
        Pre-compiles regex patterns for skills and aliases.
        Short or ambiguous skills like 'C', 'R', 'Go' are handled with special boundary rules.
        """
        self.phrase_patterns = []  # List of (pattern, canonical_name, is_tech)
        
        # Single-letter and short ambiguous skills
        self.special_short_skills = {
            "c": r'(?:\bC\b(?!\+\+|\#))',
            "r": r'(?:\bR\b(?=\s*(?:programming|language|studio|script|data|analysis)))',
            "go": r'(?:\bGo\b(?=\s*(?:lang|programming|developer|code)))|(?:\bGolang\b)'
        }
        
        # 1. Aliases
        for alias, canonical in self.aliases.items():
            is_tech = canonical in self.canonical_tech_skills
            # Escape regex characters in alias
            escaped_alias = re.escape(alias)
            pattern = re.compile(rf'(?<!\w){escaped_alias}(?!\w)', re.IGNORECASE)
            self.phrase_patterns.append((pattern, canonical, is_tech))
            
        # 2. Canonical skills (sorted by length descending so longer phrases match first)
        all_skills_sorted = sorted(list(self.all_canonical_skills), key=len, reverse=True)
        
        for skill in all_skills_sorted:
            lower_skill = skill.lower()
            is_tech = skill in self.canonical_tech_skills
            
            if lower_skill in self.special_short_skills:
                # Use strict pattern
                pattern = re.compile(self.special_short_skills[lower_skill])
                self.phrase_patterns.append((pattern, skill, is_tech))
            elif skill in ["C++", "C#", ".NET"]:
                escaped = re.escape(skill)
                pattern = re.compile(rf'(?<!\w){escaped}(?!\w)', re.IGNORECASE)
                self.phrase_patterns.append((pattern, skill, is_tech))
            else:
                escaped = re.escape(skill)
                pattern = re.compile(rf'\b{escaped}\b', re.IGNORECASE)
                self.phrase_patterns.append((pattern, skill, is_tech))

    def standardize_skill_name(self, raw_skill: str) -> str:
        """
        Normalizes a raw skill string to its canonical taxonomy form.
        """
        stripped = raw_skill.strip()
        lower = stripped.lower()
        if lower in self.aliases:
            return self.aliases[lower]
        for canonical in self.all_canonical_skills:
            if lower == canonical.lower():
                return canonical
        return stripped

    def extract_skills(self, text: str) -> dict:
        """
        Scans input text and returns structured dictionary of detected skills:
        - technical_skills: list of canonical names
        - soft_skills: list of canonical names
        - all_skills: combined list
        - technical_by_category: dict of {category: [skills]}
        - soft_by_category: dict of {category: [skills]}
        - total_count: int
        """
        if not text:
            return {
                "technical_skills": [],
                "soft_skills": [],
                "all_skills": [],
                "technical_by_category": {},
                "soft_by_category": {},
                "total_count": 0
            }

        found_tech: Set[str] = set()
        found_soft: Set[str] = set()
        
        for pattern, canonical, is_tech in self.phrase_patterns:
            if pattern.search(text):
                if is_tech:
                    found_tech.add(canonical)
                else:
                    found_soft.add(canonical)

        # Categorize technical skills
        tech_by_cat = {}
        for skill in sorted(found_tech):
            subcat = self.canonical_tech_skills.get(skill, "Other Technical")
            if subcat not in tech_by_cat:
                tech_by_cat[subcat] = []
            tech_by_cat[subcat].append(skill)

        # Categorize soft skills
        soft_by_cat = {}
        for skill in sorted(found_soft):
            subcat = self.canonical_soft_skills.get(skill, "Other Soft Skills")
            if subcat not in soft_by_cat:
                soft_by_cat[subcat] = []
            soft_by_cat[subcat].append(skill)

        all_skills = sorted(list(found_tech.union(found_soft)))

        return {
            "technical_skills": sorted(list(found_tech)),
            "soft_skills": sorted(list(found_soft)),
            "all_skills": all_skills,
            "technical_by_category": tech_by_cat,
            "soft_by_category": soft_by_cat,
            "technical_count": len(found_tech),
            "soft_count": len(found_soft),
            "total_count": len(all_skills)
        }

    def extract_skills_from_list(self, skill_items: List[str]) -> List[str]:
        """
        Normalizes and filters a list of user-provided skill strings.
        """
        result = set()
        for item in skill_items:
            norm = self.standardize_skill_name(item)
            if norm:
                result.add(norm)
        return sorted(list(result))


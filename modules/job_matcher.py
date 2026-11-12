"""
Job Matcher Module for SkillMatch AI
Calculates resume-job compatibility using a transparent hybrid approach:
TF-IDF vectorization + Cosine Similarity + Exact & Taxonomy-based Skill Overlap.
"""
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from modules.skill_extractor import SkillExtractor
from modules.text_preprocessing import TextPreprocessor

class JobMatcher:
    def __init__(
        self,
        vectorizer_path: str = "models/tfidf_vectorizer.pkl",
        roles_csv_path: str = "data/job_roles.csv"
    ):
        self.skill_extractor = SkillExtractor()
        self.preprocessor = TextPreprocessor()
        self.vectorizer_path = vectorizer_path
        self.roles_csv_path = roles_csv_path
        
        self.tfidf_vectorizer = self._load_vectorizer()
        self.df_roles = self._load_roles()

    def _load_vectorizer(self):
        if os.path.exists(self.vectorizer_path):
            return joblib.load(self.vectorizer_path)
        # Fallback if not yet trained
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', sublinear_tf=True)
        return vec

    def _load_roles(self) -> pd.DataFrame:
        if os.path.exists(self.roles_csv_path):
            return pd.read_csv(self.roles_csv_path)
        return pd.DataFrame()

    def get_predefined_roles(self) -> List[str]:
        if not self.df_roles.empty and 'job_title' in self.df_roles.columns:
            return sorted(self.df_roles['job_title'].tolist())
        return []

    def get_role_details(self, job_title: str) -> Optional[dict]:
        if self.df_roles.empty:
            return None
        match = self.df_roles[self.df_roles['job_title'] == job_title]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    def calculate_compatibility(
        self,
        resume_text: str,
        candidate_skills: List[str],
        job_description: str,
        required_tech: Optional[List[str]] = None,
        required_soft: Optional[List[str]] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> dict:
        """
        Computes transparent compatibility score between candidate resume and a job description.
        
        Default Weights:
        - Technical Skill Overlap: 50%
        - TF-IDF Cosine Similarity: 35%
        - Soft Skill Overlap: 15%
        """
        if weights is None:
            weights = {"tech": 0.50, "tfidf": 0.35, "soft": 0.15}

        # 1. If explicit required skills aren't provided, extract them from job description
        if required_tech is None or required_soft is None:
            jd_skills_extracted = self.skill_extractor.extract_skills(job_description)
            if required_tech is None:
                required_tech = jd_skills_extracted["technical_skills"]
            if required_soft is None:
                required_soft = jd_skills_extracted["soft_skills"]

        # Standardize candidate skills
        candidate_skills_set = set(
            self.skill_extractor.standardize_skill_name(s) for s in candidate_skills
        )
        required_tech_set = set(
            self.skill_extractor.standardize_skill_name(s) for s in (required_tech or [])
        )
        required_soft_set = set(
            self.skill_extractor.standardize_skill_name(s) for s in (required_soft or [])
        )

        # 2. Skill Overlap Calculation
        matched_tech = sorted(list(candidate_skills_set.intersection(required_tech_set)))
        missing_tech = sorted(list(required_tech_set - candidate_skills_set))

        matched_soft = sorted(list(candidate_skills_set.intersection(required_soft_set)))
        missing_soft = sorted(list(required_soft_set - candidate_skills_set))

        all_required = required_tech_set.union(required_soft_set)
        all_matched = set(matched_tech).union(set(matched_soft))
        
        # Additional candidate skills not strictly requested in JD
        additional_skills = sorted(list(candidate_skills_set - all_required))

        # Technical Score (0 - 100)
        if len(required_tech_set) > 0:
            tech_score = (len(matched_tech) / len(required_tech_set)) * 100.0
        else:
            tech_score = 100.0 if len(candidate_skills_set) > 0 else 50.0

        # Soft Score (0 - 100)
        if len(required_soft_set) > 0:
            soft_score = (len(matched_soft) / len(required_soft_set)) * 100.0
        else:
            soft_score = 100.0  # Not penalized if job didn't specify soft skills

        # 3. TF-IDF & Cosine Similarity
        clean_resume = self.preprocessor.clean_text(resume_text)
        clean_jd = self.preprocessor.clean_text(job_description)
        
        tfidf_similarity = 0.0
        try:
            vectors = self.tfidf_vectorizer.transform([clean_resume, clean_jd])
            cos_sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            tfidf_similarity = float(np.clip(cos_sim * 100.0, 0.0, 100.0))
        except Exception:
            # Fallback in case TF-IDF calculation encounters unexpected tokenization issue
            tfidf_similarity = (tech_score * 0.7) + (soft_score * 0.3)

        # 4. Bonus for Additional Relevant Skills (up to 5% bonus)
        bonus = min(5.0, len(additional_skills) * 0.5)

        # 5. Weighted Final Score
        raw_score = (
            (weights["tech"] * tech_score) +
            (weights["tfidf"] * tfidf_similarity) +
            (weights["soft"] * soft_score) +
            bonus
        )
        final_score = float(np.clip(round(raw_score, 1), 0.0, 100.0))

        # Coverage Ratio
        total_req_count = len(all_required)
        coverage_pct = round((len(all_matched) / total_req_count * 100.0), 1) if total_req_count > 0 else 100.0

        return {
            "overall_compatibility_score": final_score,
            "coverage_percentage": coverage_pct,
            "breakdown": {
                "technical_score": round(tech_score, 1),
                "tfidf_similarity_score": round(tfidf_similarity, 1),
                "soft_score": round(soft_score, 1),
                "bonus_points": round(bonus, 1),
                "weights": weights
            },
            "skills": {
                "matched_technical": matched_tech,
                "missing_technical": missing_tech,
                "matched_soft": matched_soft,
                "missing_soft": missing_soft,
                "additional_skills": additional_skills,
                "total_matched_count": len(all_matched),
                "total_required_count": total_req_count
            },
            "scoring_formula": {
                "formula": "Score = (0.50 × TechOverlap) + (0.35 × TF-IDF_Similarity) + (0.15 × SoftOverlap) + Bonus",
                "notes": (
                    "Weights prioritize core technical competencies (50%) and semantic context alignment (35%), "
                    "with soft skills contributing 15% and bonus points (up to 5%) awarded for broader technical breadth."
                )
            },
            "disclaimer": (
                "The compatibility score evaluates semantic and skill alignment against the specified job requirements. "
                "It is a benchmark of profile readiness, not a statistical likelihood or guarantee of hiring."
            )
        }

    def compare_multiple_roles(
        self,
        resume_text: str,
        candidate_skills: List[str],
        roles_list: List[str]
    ) -> List[dict]:
        """
        Calculates compatibility metrics for multiple roles simultaneously
        to power side-by-side comparative analytics.
        """
        comparisons = []
        for role_name in roles_list:
            details = self.get_role_details(role_name)
            if not details:
                continue
            req_tech = [s.strip() for s in str(details['required_technical_skills']).split(';') if s.strip()]
            req_soft = [s.strip() for s in str(details['required_soft_skills']).split(';') if s.strip()]
            
            res = self.calculate_compatibility(
                resume_text=resume_text,
                candidate_skills=candidate_skills,
                job_description=details['job_description'],
                required_tech=req_tech,
                required_soft=req_soft
            )
            comparisons.append({
                "job_title": role_name,
                "category": details.get("category", "Technology"),
                "overall_score": res["overall_compatibility_score"],
                "technical_score": res["breakdown"]["technical_score"],
                "semantic_score": res["breakdown"]["tfidf_similarity_score"],
                "soft_score": res["breakdown"]["soft_score"],
                "coverage_percentage": res["coverage_percentage"],
                "matched_count": res["skills"]["total_matched_count"],
                "required_count": res["skills"]["total_required_count"],
                "matched_skills": res["skills"]["matched_technical"] + res["skills"]["matched_soft"],
                "missing_skills": res["skills"]["missing_technical"] + res["skills"]["missing_soft"],
                "salary": details.get("typical_salary_range", "N/A"),
                "growth": details.get("industry_growth_outlook", "N/A")
            })
        comparisons.sort(key=lambda x: x["overall_score"], reverse=True)
        return comparisons


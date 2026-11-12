"""
Career Recommender Module for SkillMatch AI
Ranks candidate career compatibility across all known roles and leverages
the supervised classification model to provide multi-perspective career paths.
"""
import os
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from modules.job_matcher import JobMatcher

class CareerRecommender:
    def __init__(
        self,
        roles_csv_path: str = "data/job_roles.csv",
        category_clf_path: str = "models/category_classifier.pkl",
        category_encoder_path: str = "models/category_label_encoder.pkl"
    ):
        self.roles_csv_path = roles_csv_path
        self.job_matcher = JobMatcher()
        self.df_roles = pd.read_csv(roles_csv_path) if os.path.exists(roles_csv_path) else pd.DataFrame()
        
        self.cat_clf = joblib.load(category_clf_path) if os.path.exists(category_clf_path) else None
        self.cat_encoder = joblib.load(category_encoder_path) if os.path.exists(category_encoder_path) else None

    def predict_domain_affinity(self, resume_text: str) -> List[Dict[str, float]]:
        """
        Uses the trained supervised classifier to compute domain/category affinity probabilities.
        """
        if not self.cat_clf or not self.cat_encoder or not resume_text:
            return []
            
        try:
            X = self.job_matcher.tfidf_vectorizer.transform([resume_text])
            probs = self.cat_clf.predict_proba(X)[0]
            classes = self.cat_encoder.classes_
            
            affinities = []
            for cls, prob in zip(classes, probs):
                affinities.append({
                    "category": cls,
                    "probability_pct": round(float(prob * 100), 1)
                })
            affinities.sort(key=lambda x: x["probability_pct"], reverse=True)
            return affinities
        except Exception:
            return []

    def recommend_roles(
        self,
        resume_text: str,
        candidate_skills: List[str],
        top_n: int = 10
    ) -> List[dict]:
        """
        Scores candidate against all roles in the catalog, generating ranked recommendations
        with matched skills, missing skills, and detailed explanations.
        """
        if self.df_roles.empty:
            return []

        recommendations = []
        
        for _, row in self.df_roles.iterrows():
            role_title = row['job_title']
            category = row['category']
            job_desc = row['job_description']
            req_tech = [s.strip() for s in str(row['required_technical_skills']).split(';') if s.strip()]
            req_soft = [s.strip() for s in str(row['required_soft_skills']).split(';') if s.strip()]
            pref = [s.strip() for s in str(row['preferred_skills']).split(';') if s.strip()]
            
            match_res = self.job_matcher.calculate_compatibility(
                resume_text=resume_text,
                candidate_skills=candidate_skills,
                job_description=job_desc,
                required_tech=req_tech,
                required_soft=req_soft
            )
            
            score = match_res["overall_compatibility_score"]
            matched_tech = match_res["skills"]["matched_technical"]
            missing_tech = match_res["skills"]["missing_technical"]
            matched_soft = match_res["skills"]["matched_soft"]
            missing_soft = match_res["skills"]["missing_soft"]
            
            # Formulate tailored explanation
            if score >= 75:
                explanation = (
                    f"Strong alignment! You possess {len(matched_tech)} core technical skills "
                    f"({', '.join(matched_tech[:3])}) highly sought after for {role_title}."
                )
            elif score >= 50:
                explanation = (
                    f"Viable transition target. Your foundation in {', '.join(matched_tech[:2]) if matched_tech else 'technology'} "
                    f"is transferable; acquiring {', '.join(missing_tech[:2])} would make you competitive."
                )
            else:
                explanation = (
                    f"Emerging pathway. Substantial upskilling in {', '.join(missing_tech[:3])} "
                    f"is required to meet standard entry criteria for {role_title}."
                )
                
            recommendations.append({
                "role_id": row["role_id"],
                "job_title": role_title,
                "category": category,
                "compatibility_score": score,
                "coverage_percentage": match_res["coverage_percentage"],
                "technical_score": match_res["breakdown"]["technical_score"],
                "semantic_score": match_res["breakdown"]["tfidf_similarity_score"],
                "matching_skills": matched_tech + matched_soft,
                "matched_technical": matched_tech,
                "missing_skills": missing_tech + missing_soft,
                "missing_technical": missing_tech,
                "explanation": explanation,
                "experience_level": row.get("experience_level", "Mid-Level"),
                "salary_range": row.get("typical_salary_range", "Industry Standard"),
                "growth_outlook": row.get("industry_growth_outlook", "High Growth")
            })

        # Sort descending by compatibility score
        recommendations.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return recommendations[:top_n]


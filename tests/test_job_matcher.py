"""
Unit Tests for JobMatcher and CareerRecommender
"""
import pytest
from modules.job_matcher import JobMatcher
from modules.career_recommender import CareerRecommender

@pytest.fixture
def matcher():
    return JobMatcher()

@pytest.fixture
def recommender():
    return CareerRecommender()

def test_job_matcher_compatibility_range(matcher):
    resume = "Data scientist experienced in Python, SQL, Machine Learning, Scikit-learn, and Pandas."
    skills = ["Python", "SQL", "Machine Learning", "Scikit-learn", "Pandas"]
    jd = "Seeking a Data Scientist with Python, SQL, Machine Learning, and Tableau."
    req_tech = ["Python", "SQL", "Machine Learning", "Tableau"]
    req_soft = ["Analytical Skills"]

    result = matcher.calculate_compatibility(
        resume_text=resume,
        candidate_skills=skills,
        job_description=jd,
        required_tech=req_tech,
        required_soft=req_soft
    )

    score = result["overall_compatibility_score"]
    assert 0.0 <= score <= 100.0
    assert score >= 50.0  # Strong overlap
    assert "Python" in result["skills"]["matched_technical"]
    assert "Tableau" in result["skills"]["missing_technical"]
    assert "breakdown" in result
    assert "scoring_formula" in result

def test_career_recommender_ranking(recommender):
    resume = "Machine Learning Engineer with PyTorch, TensorFlow, Docker, Python, FastAPI, and Deep Learning."
    skills = ["Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Docker", "Python", "FastAPI"]
    
    recs = recommender.recommend_roles(resume, skills, top_n=5)
    assert len(recs) == 5
    # Verify sorted descending
    for i in range(len(recs) - 1):
        assert recs[i]["compatibility_score"] >= recs[i + 1]["compatibility_score"]
    
    top_titles = [r["job_title"] for r in recs]
    assert "Machine Learning Engineer" in top_titles or "AI Engineer" in top_titles or "Data Scientist" in top_titles


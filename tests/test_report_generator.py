"""
Unit Tests for ReportGenerator
"""
import io
import pytest
from modules.report_generator import ReportGenerator

@pytest.fixture
def generator():
    return ReportGenerator()

def test_generate_pdf_report(generator):
    candidate_data = {
        "contact_info": {
            "email": "sarah.chen@example.com",
            "phone": "+1 555-0199",
            "linkedin": "linkedin.com/in/sarahchen",
            "github": "github.com/sarahchen"
        },
        "education": [{"degree_type": "Master's Degree", "estimated_year": "2020"}],
        "experience": {"has_experience": True, "estimated_years": 3.0, "seniority_level": "Mid-Level"},
        "all_skills": ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-learn"],
        "technical_skills": ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-learn"],
        "soft_skills": ["Critical Thinking", "Teamwork"]
    }

    match_data = {
        "overall_compatibility_score": 82.5,
        "coverage_percentage": 75.0,
        "breakdown": {
            "technical_score": 80.0,
            "tfidf_similarity_score": 85.0,
            "soft_score": 80.0
        },
        "skills": {
            "matched_technical": ["Python", "SQL", "Machine Learning"],
            "missing_technical": ["Tableau"],
            "matched_soft": ["Teamwork"],
            "missing_soft": ["Written Communication"],
            "additional_skills": ["Pandas", "Scikit-learn"]
        }
    }

    recommendations = [
        {
            "job_title": "Data Scientist",
            "category": "Data & Analytics",
            "compatibility_score": 85.0,
            "missing_technical": ["Tableau"]
        }
    ]

    roadmap = [
        {
            "step_number": 1,
            "skill": "Tableau",
            "importance": "High",
            "timeframe": "Weeks 1 - 3",
            "description": "Visual analytics dashboard creation.",
            "stages": {
                "Beginner": {
                    "topics": "Connecting to data, charts",
                    "resources": [{"title": "Tableau Tutorial", "url": "https://www.tableau.com/learn"}]
                }
            }
        }
    ]

    pdf_stream = generator.generate_pdf(
        candidate_data=candidate_data,
        match_data=match_data,
        target_role="Data Scientist",
        recommendations=recommendations,
        roadmap=roadmap
    )

    assert isinstance(pdf_stream, io.BytesIO)
    pdf_bytes = pdf_stream.getvalue()
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


"""
Unit Tests for SkillExtractor
"""
import pytest
from modules.skill_extractor import SkillExtractor

@pytest.fixture
def extractor():
    return SkillExtractor()

def test_extract_technical_skills(extractor):
    text = "Proficient in Python, SQL, Docker, React, and Scikit-learn with experience in FastAPI."
    res = extractor.extract_skills(text)
    assert "Python" in res["technical_skills"]
    assert "SQL" in res["technical_skills"]
    assert "Docker" in res["technical_skills"]
    assert "React" in res["technical_skills"]
    assert "Scikit-learn" in res["technical_skills"]
    assert "FastAPI" in res["technical_skills"]

def test_extract_soft_skills(extractor):
    text = "Demonstrated strong Critical Thinking, Team Leadership, and Cross-functional Collaboration."
    res = extractor.extract_skills(text)
    assert "Critical Thinking" in res["soft_skills"]
    assert "Team Leadership" in res["soft_skills"]
    assert "Cross-functional Collaboration" in res["soft_skills"]

def test_alias_resolution(extractor):
    # Test k8s -> Kubernetes, postgres -> PostgreSQL, js -> JavaScript
    text = "Managed k8s clusters with postgres db and wrote js scripts."
    res = extractor.extract_skills(text)
    assert "Kubernetes" in res["technical_skills"]
    assert "PostgreSQL" in res["technical_skills"]
    assert "JavaScript" in res["technical_skills"]

def test_c_and_cpp_boundaries(extractor):
    text_c = "Developed systems in C and C++."
    res_c = extractor.extract_skills(text_c)
    assert "C++" in res_c["technical_skills"]
    assert "C" in res_c["technical_skills"]

def test_empty_text_handling(extractor):
    res = extractor.extract_skills("")
    assert res["total_count"] == 0
    assert len(res["technical_skills"]) == 0
    assert len(res["soft_skills"]) == 0


"""
Unit Tests for ResumeParser
"""
import os
import pytest
from modules.resume_parser import ResumeParser

@pytest.fixture
def parser():
    return ResumeParser()

@pytest.fixture
def sample_pdf_path():
    path = "assets/samples/Sample_Data_Scientist.pdf"
    assert os.path.exists(path), f"Sample file not found at {path}"
    return path

def test_extract_text_from_valid_pdf(parser, sample_pdf_path):
    result = parser.extract_text_from_pdf(sample_pdf_path)
    assert result["success"] is True
    assert result["page_count"] >= 1
    assert len(result["text"]) > 100
    assert "Sarah Chen" in result["text"]
    assert "Python" in result["text"]

def test_extract_contact_info(parser):
    sample_text = """
    John Doe
    Email: john.doe@example.com
    Phone: +1 (555) 123-4567
    LinkedIn: linkedin.com/in/johndoe-dev
    GitHub: github.com/johndoe
    """
    contacts = parser.extract_contact_info(sample_text)
    assert contacts["email"] == "john.doe@example.com"
    assert "555" in contacts["phone"]
    assert "linkedin.com/in/johndoe-dev" in contacts["linkedin"]
    assert "github.com/johndoe" in contacts["github"]

def test_extract_education(parser):
    sample_text = """
    EDUCATION
    Master of Science in Data Science | Stanford University (2021)
    Bachelor of Technology in Computer Science (2019)
    """
    edu = parser.extract_education(sample_text)
    assert len(edu) >= 1
    degree_types = [e["degree_type"] for e in edu]
    assert "Master's Degree" in degree_types or "Bachelor's Degree" in degree_types

def test_extract_experience_summary(parser):
    sample_text = """
    Software Engineer with 4.5 years of experience in backend development.
    Senior Backend Developer at Horizon Tech.
    """
    exp = parser.extract_experience_summary(sample_text)
    assert exp["has_experience"] is True
    assert exp["estimated_years"] == 4.5
    assert exp["seniority_level"] in ["Mid-Level", "Senior-Level"]

def test_parse_invalid_file(parser):
    result = parser.extract_text_from_pdf(b"not a valid pdf content")
    assert result["success"] is False
    assert result["error"] is not None


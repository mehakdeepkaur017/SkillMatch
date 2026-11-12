"""
Unit Tests for DatabaseManager (SQLite Persistence)
"""
import os
import pytest
from modules.database import DatabaseManager

TEST_DB = "database/test_skillmatch.db"

@pytest.fixture
def db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    manager = DatabaseManager(TEST_DB)
    yield manager
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_database_initialization(db):
    conn = db.get_connection()
    cursor = conn.cursor()
    # Check all 7 tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
    conn.close()

    expected_tables = [
        "candidates", "resume_profiles", "analysis_history",
        "job_matches", "skill_gaps", "career_recommendations", "learning_roadmaps"
    ]
    for tbl in expected_tables:
        assert tbl in tables, f"Table {tbl} was not created."

def test_save_and_retrieve_candidate_and_profile(db):
    cand_id = db.save_or_update_candidate(
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        linkedin="linkedin.com/in/johndoe",
        github="github.com/johndoe"
    )
    assert cand_id is not None

    prof_id = db.save_resume_profile(
        candidate_id=cand_id,
        filename="John_Doe_Resume.pdf",
        summary="Experienced Developer",
        education=[{"degree_type": "B.Tech", "year": "2020"}],
        experience={"years": 3.0},
        all_skills=["Python", "SQL", "Docker"],
        technical_skills=["Python", "SQL", "Docker"],
        soft_skills=["Teamwork"],
        raw_text="Sample resume raw text"
    )
    assert prof_id is not None

    latest = db.get_latest_profile()
    assert latest is not None
    assert latest["filename"] == "John_Doe_Resume.pdf"
    assert "Python" in latest["candidate_skills"]
    assert latest["contact_info"]["email"] == "john@example.com"

def test_save_retrieve_and_delete_analysis(db):
    cand_id = db.save_or_update_candidate("Jane Smith", "jane@example.com")
    prof_id = db.save_resume_profile(
        cand_id, "Jane_Resume.pdf", "Summary", [], {},
        ["Python", "FastAPI"], ["Python", "FastAPI"], [], "Text"
    )

    match_result = {
        "overall_compatibility_score": 85.5,
        "coverage_percentage": 90.0,
        "breakdown": {
            "technical_score": 88.0,
            "tfidf_similarity_score": 82.0,
            "soft_score": 90.0,
            "weights": {"tech": 0.5, "tfidf": 0.35, "soft": 0.15}
        },
        "skills": {
            "matched_technical": ["Python", "FastAPI"],
            "missing_technical": [],
            "matched_soft": [],
            "missing_soft": [],
            "additional_skills": []
        }
    }

    gap_result = {
        "prioritized_gaps": [],
        "action_recommendations": ["Great job!"]
    }

    recommendations = [{"job_title": "Python Developer", "compatibility_score": 85.5}]
    roadmap = [{"step_number": 1, "skill": "Docker", "stages": {}}]

    analysis_id = db.save_full_analysis(
        candidate_id=cand_id,
        profile_id=prof_id,
        target_role="Python Developer",
        job_source="predefined",
        job_description="Sample Job Description",
        match_result=match_result,
        gap_result=gap_result,
        recommendations=recommendations,
        roadmap=roadmap
    )

    assert analysis_id is not None

    # Retrieve all
    all_analyses = db.get_all_analyses()
    assert len(all_analyses) == 1
    assert all_analyses[0]["target_role"] == "Python Developer"
    assert all_analyses[0]["overall_score"] == 85.5

    # Retrieve details
    details = db.get_analysis_details(analysis_id)
    assert details is not None
    assert details["target_role"] == "Python Developer"
    assert details["match_result"]["overall_compatibility_score"] == 85.5
    assert len(details["roadmap"]) == 1

    # Update roadmap progress
    db.update_roadmap_progress(analysis_id, [1])
    completed = db.get_completed_roadmap_steps(analysis_id)
    assert 1 in completed

    # Delete analysis
    deleted = db.delete_analysis(analysis_id)
    assert deleted is True
    assert len(db.get_all_analyses()) == 0


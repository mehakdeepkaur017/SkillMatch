"""
Unit Tests for SkillGapAnalyzer and RoadmapGenerator
"""
import pytest
from modules.skill_gap_analyzer import SkillGapAnalyzer
from modules.roadmap_generator import RoadmapGenerator

@pytest.fixture
def gap_analyzer():
    return SkillGapAnalyzer()

@pytest.fixture
def roadmap_gen():
    return RoadmapGenerator()

def test_gap_analyzer_coverage(gap_analyzer):
    candidate = ["Python", "SQL", "Pandas"]
    required_tech = ["Python", "SQL", "Docker", "Kubernetes"]
    required_soft = ["Critical Thinking"]

    res = gap_analyzer.analyze_gaps(candidate, required_tech, required_soft)
    assert res["total_required"] == 5
    assert res["total_possessed"] == 2
    assert "Docker" in res["missing_skills"]["technical"]
    assert "Kubernetes" in res["missing_skills"]["technical"]
    assert len(res["prioritized_gaps"]) >= 2
    assert len(res["action_recommendations"]) >= 1

def test_roadmap_generation_stages(roadmap_gen):
    missing = ["Docker", "Kubernetes", "Power BI"]
    roadmap = roadmap_gen.generate_roadmap(missing)
    assert len(roadmap) == 3
    for item in roadmap:
        assert "skill" in item
        assert "timeframe" in item
        assert "stages" in item
        assert "Beginner" in item["stages"]
        assert "Intermediate" in item["stages"]
        assert "Advanced" in item["stages"]
        # Verify resources have real URLs
        beg_res = item["stages"]["Beginner"]["resources"]
        assert len(beg_res) >= 1
        assert beg_res[0]["url"].startswith("http")


"""
End-to-End Functional & Persistence Verification Script for SkillMatch AI
Simulates the critical workflow requested by the user:
Upload Resume -> Extract Skills -> Select Job Role -> Calculate Compatibility
-> Analyse Skill Gaps -> Generate Recommendations -> Save Analysis -> Simulate Browser Refresh
-> Retrieve Previous Analysis from SQLite.
"""
import os
import io
import json
import pandas as pd
from modules.resume_parser import ResumeParser
from modules.skill_extractor import SkillExtractor
from modules.job_matcher import JobMatcher
from modules.skill_gap_analyzer import SkillGapAnalyzer
from modules.career_recommender import CareerRecommender
from modules.roadmap_generator import RoadmapGenerator
from modules.report_generator import ReportGenerator
from modules.database import DatabaseManager

def run_critical_workflow_verification():
    print("=" * 70)
    print("SKILLMATCH AI — COMPLETE WORKFLOW & SQLITE PERSISTENCE VERIFICATION")
    print("=" * 70)

    # 1. Initialize components & database
    db_test_path = "database/skillmatch.db"
    db = DatabaseManager(db_test_path)
    parser = ResumeParser()
    extractor = SkillExtractor()
    matcher = JobMatcher()
    gap_analyzer = SkillGapAnalyzer()
    recommender = CareerRecommender()
    roadmap_gen = RoadmapGenerator()
    report_gen = ReportGenerator()

    sample_pdf = "assets/samples/Sample_Data_Scientist.pdf"
    assert os.path.exists(sample_pdf), f"File missing: {sample_pdf}"

    print("\n[Step 1] Upload Resume & PDF Extraction...")
    parse_res = parser.parse(sample_pdf)
    assert parse_res["success"], "PDF parsing failed"
    print(f"  ✓ PDF Extracted: {parse_res['page_count']} page(s), {len(parse_res['raw_text'])} chars")
    print(f"  ✓ Candidate Contact: {parse_res['contact_info']['email']}, Phone: {parse_res['contact_info']['phone']}")

    print("\n[Step 2] Skill Extraction & Taxonomy Mapping...")
    skills_res = extractor.extract_skills(parse_res["raw_text"])
    assert skills_res["total_count"] > 0
    print(f"  ✓ Skills Identified: {skills_res['total_count']} (Tech: {skills_res['technical_count']}, Soft: {skills_res['soft_count']})")

    print("\n[Step 3 & 4] Select Job Role & Calculate Compatibility...")
    target_role = "Data Scientist"
    role_info = matcher.get_role_details(target_role)
    req_tech = [s.strip() for s in str(role_info['required_technical_skills']).split(';') if s.strip()]
    req_soft = [s.strip() for s in str(role_info['required_soft_skills']).split(';') if s.strip()]

    match_res = matcher.calculate_compatibility(
        resume_text=parse_res["raw_text"],
        candidate_skills=skills_res["all_skills"],
        job_description=role_info['job_description'],
        required_tech=req_tech,
        required_soft=req_soft
    )
    score = match_res["overall_compatibility_score"]
    assert 0.0 <= score <= 100.0
    print(f"  ✓ Compatibility Score: {score}% (Coverage: {match_res['coverage_percentage']}%)")
    print(f"    Matched: {match_res['skills']['matched_technical'][:4]}")
    print(f"    Missing: {match_res['skills']['missing_technical'][:4]}")

    print("\n[Step 5] Analyse Skill Gaps...")
    gap_res = gap_analyzer.analyze_gaps(
        candidate_skills=skills_res["all_skills"],
        required_tech=req_tech,
        required_soft=req_soft
    )
    assert "coverage_percentage" in gap_res
    print(f"  ✓ Gap Analysis: Possessed={gap_res['total_possessed']}, Missing={len(gap_res['missing_skills']['technical'])}")

    print("\n[Step 6] Generate Recommendations & Roadmaps...")
    recs = recommender.recommend_roles(
        parse_res["raw_text"],
        skills_res["all_skills"],
        top_n=5
    )
    assert len(recs) == 5
    print(f"  ✓ Top Recommendation: #{1} {recs[0]['job_title']} ({recs[0]['compatibility_score']}%)")

    missing_tech = match_res["skills"]["missing_technical"]
    roadmap = roadmap_gen.generate_roadmap(missing_tech)
    print(f"  ✓ Learning Roadmap: {len(roadmap)} sequenced steps")

    print("\n[Step 7] Save Analysis to Permanent SQLite Database...")
    cand_id = db.save_or_update_candidate(
        name=parse_res["contact_info"].get("name") or "Sarah Chen",
        email=parse_res["contact_info"].get("email") or "",
        phone=parse_res["contact_info"].get("phone") or "",
        linkedin=parse_res["contact_info"].get("linkedin") or "",
        github=parse_res["contact_info"].get("github") or ""
    )
    prof_id = db.save_resume_profile(
        candidate_id=cand_id,
        filename=os.path.basename(sample_pdf),
        summary="Data Scientist Profile",
        education=parse_res["education"],
        experience=parse_res["experience"],
        all_skills=skills_res["all_skills"],
        technical_skills=skills_res["technical_skills"],
        soft_skills=skills_res["soft_skills"],
        raw_text=parse_res["raw_text"]
    )
    analysis_id = db.save_full_analysis(
        candidate_id=cand_id,
        profile_id=prof_id,
        target_role=target_role,
        job_source="predefined",
        job_description=role_info['job_description'],
        match_result=match_res,
        gap_result=gap_res,
        recommendations=recs,
        roadmap=roadmap
    )
    assert analysis_id is not None
    print(f"  ✓ Saved Analysis with UUID: {analysis_id}")

    print("\n[Step 8] Simulate Browser Refresh / Server Restart (Clearing Volatile State)...")
    # Simulate a fresh session by instantiating new objects and querying SQLite directly
    fresh_db = DatabaseManager(db_test_path)
    
    print("\n[Step 9] Retrieve Saved Profile & Analysis from SQLite...")
    restored_profile = fresh_db.get_latest_profile()
    assert restored_profile is not None
    assert restored_profile["filename"] == "Sample_Data_Scientist.pdf"
    assert "Python" in restored_profile["candidate_skills"]
    print(f"  ✓ Restored Candidate Profile: {restored_profile['filename']} with {len(restored_profile['candidate_skills'])} skills")

    restored_analysis = fresh_db.get_analysis_details(analysis_id)
    assert restored_analysis is not None
    assert restored_analysis["target_role"] == target_role
    assert restored_analysis["overall_score"] == score
    print(f"  ✓ Restored Analysis: Target '{restored_analysis['target_role']}', Score = {restored_analysis['overall_score']}%")
    print(f"  ✓ Restored Matched Skills: {restored_analysis['match_result']['skills']['matched_technical'][:4]}")

    print("\n[Step 10] Multi-Role Comparison Feature...")
    comp_roles = ["Data Scientist", "Data Analyst", "Machine Learning Engineer"]
    comparisons = matcher.compare_multiple_roles(
        resume_text=parse_res["raw_text"],
        candidate_skills=skills_res["all_skills"],
        roles_list=comp_roles
    )
    assert len(comparisons) == 3
    print(f"  ✓ Multi-Role Comparison Successful: {[c['job_title'] + ': ' + str(c['overall_score']) + '%' for c in comparisons]}")

    print("\n[Step 11] PDF Report Generation from Restored Record...")
    cand_dict = {
        "contact_info": restored_analysis["contact_info"],
        "education": restored_analysis["education"],
        "experience": restored_analysis["experience"],
        "all_skills": restored_analysis["candidate_skills"],
        "technical_skills": restored_analysis["technical_skills"],
        "soft_skills": restored_analysis["soft_skills"]
    }
    pdf_buffer = report_gen.generate_pdf(
        candidate_data=cand_dict,
        match_data=restored_analysis["match_result"],
        target_role=restored_analysis["target_role"],
        recommendations=restored_analysis["career_recommendations"],
        roadmap=restored_analysis["roadmap"]
    )
    assert len(pdf_buffer.getvalue()) > 2000
    print(f"  ✓ ReportLab PDF successfully generated from SQLite data ({len(pdf_buffer.getvalue()):,} bytes)")

    print("\n" + "=" * 70)
    print("CRITICAL WORKFLOW & PERMANENT RETRIEVAL VERIFIED 100% OPERATIONAL!")
    print("=" * 70)

if __name__ == "__main__":
    run_critical_workflow_verification()

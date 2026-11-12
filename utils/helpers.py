"""
UI and Session State Helper Utilities for SkillMatch AI
Provides modern SaaS design tokens, responsive cards, circular meters,
and SQLite persistence synchronization across Streamlit multi-page apps.
"""
import streamlit as st
import json
import os
from typing import List, Dict, Optional
from modules.database import DatabaseManager

def apply_custom_styles():
    """
    Applies an executive SaaS UI theme with a vibrant purple & electric-blue palette,
    crisp white cards, subtle borders, polished typography, and responsive component badges.
    """
    custom_css = """
    <style>
        /* Import Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #0F172A;
            background-color: #F8FAFC;
        }

        /* Top header bar accent */
        header[data-testid="stHeader"] {
            background: linear-gradient(90deg, rgba(79, 70, 229, 0.08) 0%, rgba(37, 99, 235, 0.08) 100%);
            border-bottom: 1px solid rgba(226, 232, 240, 0.8);
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }

        /* Hero Container */
        .hero-banner {
            background: linear-gradient(135deg, #1E1B4B 0%, #312E81 30%, #4F46E5 70%, #2563EB 100%);
            border-radius: 16px;
            padding: 38px 32px;
            color: white;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .hero-banner h1 {
            color: #FFFFFF !important;
            font-size: 2.3rem;
            font-weight: 800;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }
        .hero-banner p {
            color: #E0E7FF;
            font-size: 1.05rem;
            max-width: 780px;
            line-height: 1.6;
            margin-bottom: 0;
        }

        /* Modern White Cards */
        .clean-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 22px 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease-in-out;
        }
        .clean-card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
            border-color: #CBD5E1;
        }

        /* Metric Highlights */
        .metric-badge-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 18px 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: transform 0.15s ease;
        }
        .metric-badge-box:hover {
            transform: translateY(-2px);
            border-color: #C7D2FE;
        }
        .metric-val {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #4F46E5, #2563EB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }
        .metric-lbl {
            font-size: 0.82rem;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Skill Badges / Tags */
        .skill-tag {
            display: inline-block;
            background-color: #EEF2FF;
            color: #4338CA;
            border: 1px solid #C7D2FE;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            margin: 3px 4px 3px 0;
            transition: all 0.15s ease;
        }
        .skill-tag:hover {
            background-color: #E0E7FF;
        }
        .skill-tag-matched {
            background-color: #ECFDF5;
            color: #065F46;
            border-color: #A7F3D0;
        }
        .skill-tag-missing {
            background-color: #FEF2F2;
            color: #991B1B;
            border-color: #FECACA;
        }
        .skill-tag-soft {
            background-color: #FDF4FF;
            color: #86198F;
            border-color: #F5D0FE;
        }
        .skill-tag-bonus {
            background-color: #F0FDF4;
            color: #166534;
            border-color: #BBF7D0;
        }

        /* Button Styling */
        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            border: 1px solid #CBD5E1;
            padding: 8px 18px;
            transition: all 0.2s ease;
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4F46E5 0%, #2563EB 100%);
            color: white;
            border: none;
            box-shadow: 0 4px 10px rgba(79, 70, 229, 0.28);
        }
        div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 6px 14px rgba(79, 70, 229, 0.45);
            transform: translateY(-1px);
        }

        /* Section Title Headers */
        .section-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #0F172A;
            margin-top: 14px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Subtle Info & Alert Bars */
        .saas-callout {
            background-color: #F8FAFC;
            border-left: 4px solid #4F46E5;
            border-radius: 6px;
            padding: 12px 16px;
            margin: 12px 0;
            font-size: 0.88rem;
            color: #334155;
        }

        /* Footer */
        .footer-text {
            text-align: center;
            color: #94A3B8;
            font-size: 0.85rem;
            margin-top: 48px;
            padding-top: 20px;
            border-top: 1px solid #E2E8F0;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def init_session_state():
    """
    Initializes session state and automatically reloads saved candidate profile
    and latest analysis from the SQLite database if memory was cleared by a page refresh.
    """
    db = DatabaseManager()

    # Base defaults
    defaults = {
        "candidate_id": None,
        "profile_id": None,
        "current_analysis_id": None,
        "resume_parsed": False,
        "resume_text": "",
        "resume_name": "No resume uploaded",
        "candidate_skills": [],
        "technical_skills": [],
        "soft_skills": [],
        "technical_by_cat": {},
        "soft_by_cat": {},
        "contact_info": {},
        "education": [],
        "experience": {},
        "selected_job_title": "Data Scientist",
        "custom_job_description": "",
        "use_custom_job": False,
        "last_match_result": None,
        "last_target_role": "Data Scientist",
        "career_recommendations": [],
        "domain_affinities": [],
        "generated_roadmap": [],
        "completed_roadmap_steps": [],
        "active_tab": "Single Role Match"
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # AUTO-RELOAD FROM SQLITE IF VOLATILE STATE WAS CLEARED BY REFRESH
    if not st.session_state.resume_parsed:
        latest_profile = db.get_latest_profile()
        if latest_profile:
            st.session_state.candidate_id = latest_profile["candidate_id"]
            st.session_state.profile_id = latest_profile["profile_id"]
            st.session_state.resume_parsed = True
            st.session_state.resume_name = latest_profile["filename"]
            st.session_state.resume_text = latest_profile["raw_text"]
            st.session_state.candidate_skills = latest_profile["candidate_skills"]
            st.session_state.technical_skills = latest_profile["technical_skills"]
            st.session_state.soft_skills = latest_profile["soft_skills"]
            st.session_state.contact_info = latest_profile["contact_info"]
            st.session_state.education = latest_profile["education"]
            st.session_state.experience = latest_profile["experience"]

            # Also check if an analysis exists to auto-restore
            analyses = db.get_all_analyses(limit=1)
            if analyses:
                latest_analysis = db.get_analysis_details(analyses[0]["id"])
                if latest_analysis:
                    st.session_state.current_analysis_id = latest_analysis["id"]
                    st.session_state.last_target_role = latest_analysis["target_role"]
                    st.session_state.last_match_result = latest_analysis["match_result"]
                    st.session_state.career_recommendations = latest_analysis["career_recommendations"]
                    st.session_state.domain_affinities = latest_analysis["domain_affinities"]
                    st.session_state.generated_roadmap = latest_analysis["roadmap"]
                    st.session_state.completed_roadmap_steps = latest_analysis["completed_steps"]


def save_current_analysis_to_db(target_role: str, match_result: dict, gap_result: Optional[dict] = None) -> str:
    """
    Saves the currently active analysis session into SQLite, preventing duplicates.
    """
    db = DatabaseManager()

    # Ensure candidate and profile exist in DB
    candidate_id = st.session_state.candidate_id
    profile_id = st.session_state.profile_id

    if not candidate_id:
        ci = st.session_state.contact_info or {}
        candidate_id = db.save_or_update_candidate(
            name=ci.get("name") or "Candidate",
            email=ci.get("email") or "",
            phone=ci.get("phone") or "",
            linkedin=ci.get("linkedin") or "",
            github=ci.get("github") or ""
        )
        st.session_state.candidate_id = candidate_id

    if not profile_id:
        profile_id = db.save_resume_profile(
            candidate_id=candidate_id,
            filename=st.session_state.resume_name,
            summary=st.session_state.contact_info.get("name", "Resume Profile"),
            education=st.session_state.education,
            experience=st.session_state.experience,
            all_skills=st.session_state.candidate_skills,
            technical_skills=st.session_state.technical_skills,
            soft_skills=st.session_state.soft_skills,
            raw_text=st.session_state.resume_text
        )
        st.session_state.profile_id = profile_id

    analysis_id = db.save_full_analysis(
        candidate_id=candidate_id,
        profile_id=profile_id,
        target_role=target_role,
        job_source="custom" if st.session_state.get("use_custom_job") else "predefined",
        job_description=st.session_state.get("custom_job_description") or "",
        match_result=match_result,
        gap_result=gap_result,
        recommendations=st.session_state.get("career_recommendations"),
        domain_affinities=st.session_state.get("domain_affinities"),
        roadmap=st.session_state.get("generated_roadmap")
    )
    st.session_state.current_analysis_id = analysis_id
    return analysis_id


def render_circular_score_component(score: float, label: str = "Overall Match"):
    """
    Renders an eye-catching circular compatibility gauge using SVG & HTML.
    """
    score_clamped = max(0.0, min(100.0, float(score)))
    circumference = 2 * 3.14159 * 54
    stroke_dashoffset = circumference - (score_clamped / 100.0) * circumference

    if score_clamped >= 75:
        stroke_color = "#10B981"  # Emerald
        tier_text = "High Compatibility"
    elif score_clamped >= 50:
        stroke_color = "#3B82F6"  # Blue
        tier_text = "Moderate Fit"
    else:
        stroke_color = "#F59E0B"  # Amber
        tier_text = "Upskilling Needed"

    html = f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:15px;">
        <div style="position:relative; width:140px; height:140px;">
            <svg viewBox="0 0 120 120" style="width:100%; height:100%; transform: rotate(-90deg);">
                <circle cx="60" cy="60" r="54" fill="none" stroke="#E2E8F0" stroke-width="10" />
                <circle cx="60" cy="60" r="54" fill="none" stroke="{stroke_color}" stroke-width="10"
                        stroke-linecap="round"
                        stroke-dasharray="{circumference:.2f}"
                        stroke-dashoffset="{stroke_dashoffset:.2f}"
                        style="transition: stroke-dashoffset 0.8s ease;" />
            </svg>
            <div style="position:absolute; top:0; left:0; width:100%; height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                <span style="font-size:2rem; font-weight:800; color:#0F172A; font-family:'Inter', sans-serif;">{score_clamped:.1f}%</span>
                <span style="font-size:0.7rem; font-weight:700; color:#64748B; text-transform:uppercase;">{label}</span>
            </div>
        </div>
        <div style="margin-top:10px; font-size:0.85rem; font-weight:700; color:{stroke_color}; text-transform:uppercase; letter-spacing:0.04em;">
            {tier_text}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_skill_badges(skills: list[str], badge_type: str = "default"):
    """
    Renders styled HTML skill badges.
    badge_type: 'default', 'matched', 'missing', 'soft', 'bonus'
    """
    if not skills:
        st.markdown("<span style='color:#94A3B8; font-style:italic;'>None identified</span>", unsafe_allow_html=True)
        return

    type_class_map = {
        "default": "skill-tag",
        "matched": "skill-tag skill-tag-matched",
        "missing": "skill-tag skill-tag-missing",
        "soft": "skill-tag skill-tag-soft",
        "bonus": "skill-tag skill-tag-bonus"
    }
    css_class = type_class_map.get(badge_type, "skill-tag")
    html_badges = " ".join([f"<span class='{css_class}'>{skill}</span>" for skill in skills])
    st.markdown(html_badges, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, subtext: str = ""):
    """
    Renders a clean white card containing a prominent metric value.
    """
    html = f"""
    <div class="metric-badge-box">
        <div class="metric-val">{value}</div>
        <div class="metric-lbl">{label}</div>
        {f'<div style="font-size:0.75rem; color:#64748B; margin-top:4px;">{subtext}</div>' if subtext else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

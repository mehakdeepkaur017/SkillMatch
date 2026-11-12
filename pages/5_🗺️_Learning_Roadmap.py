"""
SkillMatch AI – Personalized Learning Roadmap (PAGE 6)
Generates structured, sequenced learning paths with Beginner, Intermediate, and Advanced stages,
complete with verified documentation, authentic course links, and SQLite milestone progress tracking.
"""
import streamlit as st
from utils.helpers import apply_custom_styles, init_session_state, render_skill_badges, render_metric_card
from modules.roadmap_generator import RoadmapGenerator
from modules.job_matcher import JobMatcher
from modules.database import DatabaseManager

st.set_page_config(
    page_title="Learning Roadmap | SkillMatch AI",
    page_icon="🗺️",
    layout="wide"
)

apply_custom_styles()
init_session_state()

db = DatabaseManager()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="font-weight:800; color:#0F172A; margin-bottom:4px;">🗺️ Personalized Skill Improvement Roadmap</h2>
    <p style="color:#64748B; font-size:1rem;">
        Turn identified skill gaps into a structured, step-by-step learning curriculum with authentic documentation, tutorials, and persistent milestone tracking.
    </p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.resume_parsed:
    st.warning("⚠️ No candidate profile loaded yet. Please upload a resume or load a demo sample.")
    if st.button("📄 Go to Resume Analyzer", type="primary"):
        st.switch_page("pages/1_📄_Resume_Analyzer.py")
    st.stop()

matcher = JobMatcher()
roadmap_gen = RoadmapGenerator()

target_role = st.session_state.last_target_role or "Data Scientist"

# Retrieve missing skills for target role
role_info = matcher.get_role_details(target_role)
if role_info:
    req_tech = [s.strip() for s in str(role_info['required_technical_skills']).split(';') if s.strip()]
    req_soft = [s.strip() for s in str(role_info['required_soft_skills']).split(';') if s.strip()]
else:
    match_res = st.session_state.last_match_result or {}
    skills_meta = match_res.get("skills", {})
    req_tech = skills_meta.get("missing_technical", [])
    req_soft = skills_meta.get("missing_soft", [])

cand_skills_set = set(st.session_state.candidate_skills)
missing_to_learn = [s for s in req_tech if s not in cand_skills_set]

# Retrieve saved progress if analysis_id exists
completed_steps = []
if st.session_state.current_analysis_id:
    completed_steps = db.get_completed_roadmap_steps(st.session_state.current_analysis_id)
elif "completed_roadmap_steps" in st.session_state:
    completed_steps = st.session_state.completed_roadmap_steps

# Generate or reuse roadmap
roadmap = getattr(st.session_state, "generated_roadmap", None)
if not roadmap:
    roadmap = roadmap_gen.generate_roadmap(missing_to_learn)
    st.session_state.generated_roadmap = roadmap

total_steps = len(roadmap)
completed_count = len(completed_steps)
progress_ratio = (completed_count / total_steps) if total_steps > 0 else 1.0

# ----------------------------------------------------
# CURRICULUM HEADER & PROGRESS BAR
# ----------------------------------------------------
st.markdown(f"""
<div class="clean-card" style="background: linear-gradient(135deg, #EEF2FF 0%, #FAF5FF 100%); border-color:#C7D2FE; margin-bottom:20px;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <span style="font-size:0.78rem; font-weight:700; color:#6366F1; text-transform:uppercase;">Curriculum Target</span>
            <h3 style="color:#0F172A; margin-top:2px; margin-bottom:4px; font-weight:800;">{target_role}</h3>
            <p style="font-size:0.88rem; color:#475569; margin-bottom:0;">
                Personalized roadmap addressing <b>{len(missing_to_learn)} missing core technical competencies</b> required for this role.
            </p>
        </div>
        <div style="text-align:right;">
            <span style="font-size:0.85rem; color:#64748B;">Roadmap Progress</span>
            <div style="font-size:1.6rem; font-weight:800; color:#4F46E5;">{int(progress_ratio * 100)}% Complete</div>
            <span style="font-size:0.8rem; color:#64748B;">{completed_count} of {total_steps} milestones checked</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Streamlit Progress Indicator
st.progress(progress_ratio)

if not missing_to_learn:
    st.success("🎉 You already possess all mandatory technical competencies for this role! Focus on system design, portfolio projects, and interview preparation.")
    st.markdown("#### Suggested Next Steps:")
    st.markdown("""
    - Build a capstone portfolio project deploying an end-to-end architecture on GitHub.
    - Write a technical writeup or blog post breaking down your implementation tradeoffs.
    - Practice behavioral storytelling (STAR method) to highlight your soft skills and team collaboration.
    """)
else:
    st.markdown("<div class='section-title'>🎯 Phased Learning Sequence & Milestone Tracker</div>", unsafe_allow_html=True)
    st.caption("Check off milestones as you master them. Progress is saved automatically to your local SQLite database.")

    updated_completed_steps = list(completed_steps)
    has_progress_changed = False

    for item in roadmap:
        step = item["step_number"]
        skill = item["skill"]
        importance = item["importance"]
        timeframe = item["timeframe"]
        desc = item["description"]
        stages = item["stages"]

        is_completed = step in completed_steps

        if importance == "Critical":
            imp_color = "#DC2626"
            imp_bg = "#FEE2E2"
        elif importance == "High":
            imp_color = "#D97706"
            imp_bg = "#FEF3C7"
        else:
            imp_color = "#2563EB"
            imp_bg = "#DBEAFE"

        with st.container():
            st.markdown(f"""
            <div class="clean-card" style="margin-bottom:20px; border-left: 5px solid {imp_color}; background: {'#F0FDF4' if is_completed else '#FFFFFF'};">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:12px;">
                    <div>
                        <span style="background:{'#10B981' if is_completed else '#312E81'}; color:white; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:999px;">
                            {'✓ DONE' if is_completed else f'STEP {step}'}
                        </span>
                        <span style="font-size:1.3rem; font-weight:800; color:#0F172A; margin-left:10px;">{skill}</span>
                        <span style="background:{imp_bg}; color:{imp_color}; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:6px; margin-left:8px;">
                            {importance.upper()} IMPORTANCE
                        </span>
                    </div>
                    <div style="font-size:0.85rem; font-weight:600; color:#64748B;">
                        ⏱️ {timeframe}
                    </div>
                </div>
                <p style="font-size:0.88rem; color:#475569; margin-bottom:14px;">{desc}</p>
            """, unsafe_allow_html=True)

            # 3 Stage Columns: Beginner -> Intermediate -> Advanced
            col_b, col_i, col_a = st.columns(3)

            with col_b:
                beg = stages.get("Beginner", {})
                st.markdown("""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; height:100%;">
                    <div style="font-size:0.8rem; font-weight:700; color:#0284C7; text-transform:uppercase;">🌱 Stage 1: Beginner</div>
                    <div style="font-size:0.82rem; font-weight:600; color:#0F172A; margin-top:4px;">Core Concepts:</div>
                    <p style="font-size:0.78rem; color:#64748B; margin-bottom:8px;">""" + beg.get("topics", "Basics") + """</p>
                    <div style="font-size:0.8rem; font-weight:600; color:#0F172A;">Verified Resources:</div>
                """, unsafe_allow_html=True)
                for res in beg.get("resources", []):
                    st.markdown(f"• <a href='{res.get('url')}' target='_blank' style='font-size:0.78rem; color:#4F46E5; font-weight:600;'>{res.get('title')}</a>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_i:
                inter = stages.get("Intermediate", {})
                st.markdown("""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; height:100%;">
                    <div style="font-size:0.8rem; font-weight:700; color:#D97706; text-transform:uppercase;">🌿 Stage 2: Intermediate</div>
                    <div style="font-size:0.82rem; font-weight:600; color:#0F172A; margin-top:4px;">Applied Tooling:</div>
                    <p style="font-size:0.78rem; color:#64748B; margin-bottom:8px;">""" + inter.get("topics", "Practices") + """</p>
                    <div style="font-size:0.8rem; font-weight:600; color:#0F172A;">Verified Resources:</div>
                """, unsafe_allow_html=True)
                for res in inter.get("resources", []):
                    st.markdown(f"• <a href='{res.get('url')}' target='_blank' style='font-size:0.78rem; color:#4F46E5; font-weight:600;'>{res.get('title')}</a>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_a:
                adv = stages.get("Advanced", {})
                st.markdown("""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; height:100%;">
                    <div style="font-size:0.8rem; font-weight:700; color:#7C3AED; text-transform:uppercase;">🌳 Stage 3: Advanced</div>
                    <div style="font-size:0.82rem; font-weight:600; color:#0F172A; margin-top:4px;">Scale & Production:</div>
                    <p style="font-size:0.78rem; color:#64748B; margin-bottom:8px;">""" + adv.get("topics", "Advanced topics") + """</p>
                    <div style="font-size:0.8rem; font-weight:600; color:#0F172A;">Verified Resources:</div>
                """, unsafe_allow_html=True)
                for res in adv.get("resources", []):
                    st.markdown(f"• <a href='{res.get('url')}' target='_blank' style='font-size:0.78rem; color:#4F46E5; font-weight:600;'>{res.get('title')}</a>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Interactive milestone completion checkbox
            checked = st.checkbox(f"Mark Step {step} ({skill}) as Completed", value=is_completed, key=f"step_chk_{step}")
            if checked and step not in updated_completed_steps:
                updated_completed_steps.append(step)
                has_progress_changed = True
            elif not checked and step in updated_completed_steps:
                updated_completed_steps.remove(step)
                has_progress_changed = True

    # Save milestone changes to SQLite
    if has_progress_changed:
        st.session_state.completed_roadmap_steps = updated_completed_steps
        if st.session_state.current_analysis_id:
            db.update_roadmap_progress(st.session_state.current_analysis_id, updated_completed_steps)
        st.rerun()

# Navigation
st.markdown("<br/>", unsafe_allow_html=True)
c_nav1, c_nav2 = st.columns([1.5, 3.5])
with c_nav1:
    if st.button("➡️ Explore Analytics Dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/6_📊_Analytics_Dashboard.py")

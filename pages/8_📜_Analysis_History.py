"""
SkillMatch AI – Analysis History & Audit Trails (PAGE 9)
Displays all permanently stored analyses from SQLite, with 1-click restoration,
record inspection, individual deletion, and history clearing.
"""
import streamlit as st
import pandas as pd
from utils.helpers import (
    apply_custom_styles, init_session_state, render_skill_badges, render_metric_card
)
from modules.database import DatabaseManager

st.set_page_config(
    page_title="Analysis History | SkillMatch AI",
    page_icon="📜",
    layout="wide"
)

apply_custom_styles()
init_session_state()

db = DatabaseManager()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="font-weight:800; color:#0F172A; margin-bottom:4px;">📜 Analysis History & Saved Profiles</h2>
    <p style="color:#64748B; font-size:1rem;">
        Review previous career compatibility analyses saved in your local SQLite database, reopen historical evaluations, or manage stored records.
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch all analyses from SQLite
analyses = db.get_all_analyses(limit=100)

# Quick summary metrics
m1, m2, m3 = st.columns(3)
with m1:
    render_metric_card("Total Saved Analyses", f"{len(analyses)}", "Stored in SQLite Database")
with m2:
    avg_score = round(sum(a["overall_score"] for a in analyses) / len(analyses), 1) if analyses else 0.0
    render_metric_card("Historical Mean Score", f"{avg_score}%", "Across All Evaluations")
with m3:
    latest_date = analyses[0]["created_at"][:10] if analyses else "No records"
    render_metric_card("Latest Assessment", f"{latest_date}", "Most Recent Run")

st.markdown("<br/>", unsafe_allow_html=True)

if not analyses:
    st.info("ℹ️ No historical analyses found in your database yet. Complete an analysis in **Job Matching** to save it here.")
    if st.button("🎯 Go to Job Matching", type="primary"):
        st.switch_page("pages/2_🎯_Job_Matching.py")
else:
    # ----------------------------------------------------
    # SAVED ANALYSES LIST & ACTIONS
    # ----------------------------------------------------
    st.markdown("<div class='section-title'>📂 Stored Evaluation Records</div>", unsafe_allow_html=True)

    for idx, item in enumerate(analyses, 1):
        score = item["overall_score"]
        score_color = "#10B981" if score >= 70 else ("#3B82F6" if score >= 50 else "#F59E0B")

        with st.container():
            st.markdown(f"""
            <div class="clean-card" style="border-left: 6px solid {score_color}; margin-bottom:14px; padding:18px 22px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                    <div>
                        <span style="font-size:0.78rem; background:#F1F5F9; color:#475569; padding:2px 8px; border-radius:6px; font-weight:700;">#{idx}</span>
                        <span style="font-size:1.25rem; font-weight:800; color:#0F172A; margin-left:8px;">{item['target_role']}</span>
                        <span style="font-size:0.85rem; color:#64748B; margin-left:10px;">• {item['filename']}</span>
                        <span style="font-size:0.8rem; color:#94A3B8; margin-left:8px;">(Saved: {item['created_at'][:16]})</span>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:1.5rem; font-weight:900; color:{score_color};">{score:.1f}%</span>
                        <span style="display:block; font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase;">Overall Fit</span>
                    </div>
                </div>
                <div style="display:flex; gap:20px; font-size:0.84rem; color:#475569; margin-top:8px;">
                    <div><b>Technical Match:</b> {item['technical_score']:.1f}%</div>
                    <div><b>Skill Coverage:</b> {item['coverage_percentage']:.1f}%</div>
                    <div><b>Opportunity Source:</b> {item['job_source'].capitalize()}</div>
                </div>
            """, unsafe_allow_html=True)

            c_btn_load, c_btn_del, c_spacer = st.columns([1.5, 1.2, 3.3])
            
            with c_btn_load:
                if st.button("📂 Reopen Analysis", key=f"reopen_hist_{item['id']}", use_container_width=True):
                    full_details = db.get_analysis_details(item["id"])
                    if full_details:
                        st.session_state.current_analysis_id = full_details["id"]
                        st.session_state.resume_parsed = True
                        st.session_state.resume_name = full_details["filename"]
                        st.session_state.resume_text = full_details["raw_text"]
                        st.session_state.candidate_skills = full_details["candidate_skills"]
                        st.session_state.technical_skills = full_details["technical_skills"]
                        st.session_state.soft_skills = full_details["soft_skills"]
                        st.session_state.contact_info = full_details["contact_info"]
                        st.session_state.education = full_details["education"]
                        st.session_state.experience = full_details["experience"]
                        st.session_state.last_target_role = full_details["target_role"]
                        st.session_state.last_match_result = full_details["match_result"]
                        st.session_state.career_recommendations = full_details["career_recommendations"]
                        st.session_state.domain_affinities = full_details["domain_affinities"]
                        st.session_state.generated_roadmap = full_details["roadmap"]
                        st.session_state.completed_roadmap_steps = full_details["completed_steps"]
                        st.success(f"Restored session for {item['target_role']}!")
                        st.switch_page("pages/2_🎯_Job_Matching.py")

            with c_btn_del:
                if st.button("🗑️ Delete", key=f"del_hist_{item['id']}", use_container_width=True):
                    db.delete_analysis(item["id"])
                    st.success("Record deleted successfully.")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # BULK MANAGEMENT & CLEAR HISTORY
    # ----------------------------------------------------
    st.markdown("<br/>", unsafe_allow_html=True)
    with st.expander("⚠️ Danger Zone: Clear Analysis History"):
        st.warning("Clearing your analysis history permanently deletes all saved match sessions, skill gaps, and roadmap records. Candidate profiles remain intact for re-analysis.")
        confirm_clear = st.checkbox("I understand that this action cannot be undone.", key="confirm_clear_chk")
        if st.button("🚨 Clear All Saved History", type="secondary", disabled=not confirm_clear):
            count = db.clear_all_history()
            st.success(f"Cleared {count} historical records from database.")
            st.rerun()


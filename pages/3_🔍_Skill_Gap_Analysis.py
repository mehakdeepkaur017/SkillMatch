"""
SkillMatch AI – Skill Gap Analysis (PAGE 4)
Performs deep-dive gap analysis, prioritizing missing skills into Critical, High, and Medium tiers,
with interactive visual comparison charts and concrete recommendations.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.helpers import (
    apply_custom_styles, init_session_state, render_skill_badges,
    render_metric_card, save_current_analysis_to_db
)
from modules.skill_gap_analyzer import SkillGapAnalyzer
from modules.job_matcher import JobMatcher

st.set_page_config(
    page_title="Skill Gap Analysis | SkillMatch AI",
    page_icon="🔍",
    layout="wide"
)

apply_custom_styles()
init_session_state()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="font-weight:800; color:#0F172A; margin-bottom:4px;">🔍 Skill Gap Analysis & Priority Diagnostics</h2>
    <p style="color:#64748B; font-size:1rem;">
        Understand exactly which technical and interpersonal gaps separate your current profile from your target role requirements.
    </p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.resume_parsed:
    st.warning("⚠️ No resume parsed yet. Please upload a resume or load a sample resume first.")
    if st.button("📄 Go to Resume Analyzer", type="primary"):
        st.switch_page("pages/1_📄_Resume_Analyzer.py")
    st.stop()

matcher = JobMatcher()
gap_analyzer = SkillGapAnalyzer()

target_role = st.session_state.last_target_role or "Data Scientist"

# Fetch details of target role
role_details = matcher.get_role_details(target_role)
if role_details:
    req_tech = [s.strip() for s in str(role_details['required_technical_skills']).split(';') if s.strip()]
    req_soft = [s.strip() for s in str(role_details['required_soft_skills']).split(';') if s.strip()]
    pref_skills = [s.strip() for s in str(role_details['preferred_skills']).split(';') if s.strip()]
else:
    match_res = st.session_state.last_match_result or {}
    skills_meta = match_res.get("skills", {})
    req_tech = skills_meta.get("matched_technical", []) + skills_meta.get("missing_technical", [])
    req_soft = skills_meta.get("matched_soft", []) + skills_meta.get("missing_soft", [])
    pref_skills = []

# Execute Gap Analysis
gap_res = gap_analyzer.analyze_gaps(
    candidate_skills=st.session_state.candidate_skills,
    required_tech=req_tech,
    required_soft=req_soft,
    preferred_skills=pref_skills
)

# ----------------------------------------------------
# SUMMARY KPI METRICS
# ----------------------------------------------------
st.markdown(f"#### Target Role: <span style='color:#4F46E5;'><b>{target_role}</b></span>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

with m1:
    render_metric_card("Coverage Rate", f"{gap_res['coverage_percentage']}%", "Required Skills Possessed")
with m2:
    render_metric_card("Skills Possessed", f"{gap_res['total_possessed']}", f"Out of {gap_res['total_required']} Required")
with m3:
    render_metric_card("Technical Gaps", f"{len(gap_res['missing_skills']['technical'])}", "Core Skills Missing")
with m4:
    render_metric_card("Critical Priorities", f"{len(gap_res['top_missing_skills'])}", "Immediate Upskilling Focus")

st.markdown("<br/>", unsafe_allow_html=True)

# ----------------------------------------------------
# VISUAL COMPARISON CHARTS
# ----------------------------------------------------
st.markdown("<div class='section-title'>📊 Visual Gap Comparison</div>", unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns([1.5, 1.5])

with col_chart1:
    cat_summary = [
        {"Category": "Technical Skills", "Status": "Possessed", "Count": len(gap_res["possessed_skills"]["technical"])},
        {"Category": "Technical Skills", "Status": "Missing", "Count": len(gap_res["missing_skills"]["technical"])},
        {"Category": "Soft Skills", "Status": "Possessed", "Count": len(gap_res["possessed_skills"]["soft"])},
        {"Category": "Soft Skills", "Status": "Missing", "Count": len(gap_res["missing_skills"]["soft"])}
    ]
    df_cat = pd.DataFrame(cat_summary)
    
    fig_bar = px.bar(
        df_cat,
        x="Category",
        y="Count",
        color="Status",
        barmode="group",
        color_discrete_map={"Possessed": "#10B981", "Missing": "#EF4444"},
        text="Count",
        title="<b>Required Competencies: Possessed vs. Missing</b>"
    )
    fig_bar.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_chart2:
    labels = ["Possessed Skills", "Missing Technical", "Missing Soft"]
    values = [
        gap_res["total_possessed"],
        len(gap_res["missing_skills"]["technical"]),
        len(gap_res["missing_skills"]["soft"])
    ]
    if sum(values) == 0:
        values = [1, 0, 0]
        
    fig_donut = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=["#10B981", "#EF4444", "#F59E0B"]),
        textinfo='label+percent',
        insidetextorientation='radial'
    )])
    fig_donut.update_layout(
        title="<b>Total Skill Composition Ratio</b>",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'},
        showlegend=False
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ----------------------------------------------------
# PRIORITIZED GAP BREAKDOWN
# ----------------------------------------------------
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🎯 Prioritized Missing Skills Matrix</div>", unsafe_allow_html=True)
st.caption("Skills are ordered by industry criticality for this specific role, guiding where your learning time yields highest ROI.")

gaps = gap_res.get("prioritized_gaps", [])

if gaps:
    for gap in gaps:
        importance = gap["importance"]
        if importance == "Critical":
            border_color = "#DC2626"
            badge_bg = "#FEE2E2"
            badge_fg = "#991B1B"
        elif importance == "High":
            border_color = "#F59E0B"
            badge_bg = "#FEF3C7"
            badge_fg = "#B45309"
        else:
            border_color = "#3B82F6"
            badge_bg = "#DBEAFE"
            badge_fg = "#1D4ED8"

        st.markdown(f"""
        <div class="clean-card" style="border-left: 5px solid {border_color}; padding:16px 20px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <span style="font-size:1.1rem; font-weight:700; color:#0F172A;">{gap['skill']}</span>
                    <span style="font-size:0.8rem; background:{badge_bg}; color:{badge_fg}; padding:2px 10px; border-radius:999px; font-weight:700; margin-left:10px;">
                        {gap['importance'].upper()}
                    </span>
                    <span style="font-size:0.8rem; color:#64748B; margin-left:8px;">• {gap['category']}</span>
                </div>
                <div style="font-size:0.85rem; font-weight:600; color:{border_color};">
                    {gap['urgency']}
                </div>
            </div>
            <p style="font-size:0.86rem; color:#475569; margin-top:8px; margin-bottom:0;">
                💡 <b>Impact:</b> {gap['rationale']}
            </p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("🎉 No missing skill gaps identified! You have 100% prerequisite alignment for this role.")

# ----------------------------------------------------
# ACTION RECOMMENDATIONS
# ----------------------------------------------------
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>💡 Strategic Recommendations for Improvement</div>", unsafe_allow_html=True)

for rec in gap_res.get("action_recommendations", []):
    st.info(f"📌 **Recommendation:** {rec}")

# Navigation
st.markdown("<br/>", unsafe_allow_html=True)
c_nav1, c_nav2 = st.columns([1.5, 3.5])
with c_nav1:
    if st.button("➡️ View Career Recommendations", type="primary", use_container_width=True):
        st.switch_page("pages/4_🚀_Career_Recommendations.py")

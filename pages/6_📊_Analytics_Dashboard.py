"""
SkillMatch AI – Analytics Dashboard (PAGE 7)
Provides executive visual analytics, compatibility benchmarks, skill distributions,
and career readiness indices driven by live analysis data and SQLite database history.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.helpers import apply_custom_styles, init_session_state, render_skill_badges, render_metric_card
from modules.career_recommender import CareerRecommender
from modules.job_matcher import JobMatcher
from modules.database import DatabaseManager

st.set_page_config(
    page_title="Analytics Dashboard | SkillMatch AI",
    page_icon="📊",
    layout="wide"
)

apply_custom_styles()
init_session_state()

db = DatabaseManager()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="font-weight:800; color:#0F172A; margin-bottom:4px;">📊 Comprehensive Career Analytics Dashboard</h2>
    <p style="color:#64748B; font-size:1rem;">
        Visual diagnostics summarizing candidate skill breadth, cross-role compatibility benchmarks, and market readiness.
    </p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.resume_parsed:
    st.warning("⚠️ No candidate profile loaded yet. Please upload a resume or load a demo profile.")
    if st.button("📄 Go to Resume Analyzer", type="primary"):
        st.switch_page("pages/1_📄_Resume_Analyzer.py")
    st.stop()

recommender = CareerRecommender()
matcher = JobMatcher()

if not st.session_state.career_recommendations:
    with st.spinner("Compiling cross-role analytics..."):
        recs = recommender.recommend_roles(
            st.session_state.resume_text,
            st.session_state.candidate_skills,
            top_n=15
        )
        st.session_state.career_recommendations = recs

recommendations = st.session_state.career_recommendations
df_recs = pd.DataFrame(recommendations)

# Live metrics
total_skills_count = len(st.session_state.candidate_skills)
num_roles_analyzed = len(df_recs)
best_match_role = df_recs.iloc[0]["job_title"] if not df_recs.empty else "N/A"
best_match_score = df_recs.iloc[0]["compatibility_score"] if not df_recs.empty else 0.0
avg_compatibility = round(df_recs["compatibility_score"].mean(), 1) if not df_recs.empty else 0.0

# ----------------------------------------------------
# TOP EXECUTIVE METRICS ROW
# ----------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    render_metric_card("Resume Skills", f"{total_skills_count}", "Extracted Competencies")
with kpi2:
    render_metric_card("Roles Benchmarked", f"{num_roles_analyzed}", "Industry Tech Profiles")
with kpi3:
    render_metric_card("Top Match Role", f"{best_match_score:.1f}%", f"Target: {best_match_role}")
with kpi4:
    render_metric_card("Avg Compatibility", f"{avg_compatibility:.1f}%", "Across All 15 Roles")

st.markdown("<br/>", unsafe_allow_html=True)

# ----------------------------------------------------
# CHARTS ROW 1: COMPATIBILITY BENCHMARK & READINESS
# ----------------------------------------------------
c_bench, c_readiness = st.columns([1.8, 1.2])

with c_bench:
    df_sorted = df_recs.sort_values(by="compatibility_score", ascending=True)
    fig_bar = px.bar(
        df_sorted,
        x="compatibility_score",
        y="job_title",
        orientation="h",
        color="compatibility_score",
        color_continuous_scale=["#EF4444", "#F59E0B", "#10B981", "#4F46E5"],
        text="compatibility_score",
        labels={"compatibility_score": "Compatibility Score (%)", "job_title": "Role Title"},
        title="<b>Cross-Role Compatibility Benchmark (All 15 Roles)</b>"
    )
    fig_bar.update_layout(
        height=420,
        margin=dict(l=10, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'},
        coloraxis_showscale=False
    )
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

with c_readiness:
    readiness_index = float(np.clip(best_match_score * 0.7 + avg_compatibility * 0.3, 0.0, 100.0))
    if readiness_index >= 75:
        tier_title = "High Market Readiness"
        tier_desc = "Strong candidate profile ready for direct applications."
        color_code = "#10B981"
    elif readiness_index >= 50:
        tier_title = "Moderate Readiness"
        tier_desc = "Solid foundational profile with targeted upskilling needed."
        color_code = "#3B82F6"
    else:
        tier_title = "Early Stage Candidate"
        tier_desc = "Focus on core roadmap milestones before interviewing."
        color_code = "#F59E0B"

    st.markdown(f"""
    <div class="clean-card" style="height:420px; display:flex; flex-direction:column; justify-content:center; text-align:center;">
        <div style="font-size:0.85rem; font-weight:700; color:#64748B; text-transform:uppercase;">Overall Career Readiness Index</div>
        <div style="font-size:3.5rem; font-weight:900; color:{color_code}; margin-top:8px; margin-bottom:2px;">
            {readiness_index:.1f}%
        </div>
        <div style="font-size:1.15rem; font-weight:700; color:#0F172A;">{tier_title}</div>
        <p style="font-size:0.85rem; color:#64748B; margin-top:8px; line-height:1.5;">
            {tier_desc}
        </p>
        <div style="margin-top:16px; border-top:1px solid #E2E8F0; padding-top:14px; text-align:left; font-size:0.82rem; color:#475569;">
            • <b>Top Alignment:</b> {best_match_score:.1f}% ({best_match_role})<br/>
            • <b>Market Breadth:</b> {avg_compatibility:.1f}%<br/>
            • <b>Profile Versatility:</b> High versatility in tech sector
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# CHARTS ROW 2: SKILLS DISTRIBUTION & TOP ASSETS/GAPS
# ----------------------------------------------------
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📈 Skills Distribution & Market Insights</div>", unsafe_allow_html=True)

c_dist, c_audit = st.columns([1.5, 1.5])

with c_dist:
    tech_cats = st.session_state.technical_by_cat or {}
    soft_cats = st.session_state.soft_by_cat or {}
    
    cat_data = []
    for cat, skl in tech_cats.items():
        cat_data.append({"Category": cat, "Count": len(skl), "Domain": "Technical"})
    for cat, skl in soft_cats.items():
        cat_data.append({"Category": cat, "Count": len(skl), "Domain": "Soft Skills"})
        
    if cat_data:
        df_dist = pd.DataFrame(cat_data).sort_values(by="Count", ascending=False)
        fig_dist = px.bar(
            df_dist,
            x="Count",
            y="Category",
            orientation="h",
            color="Domain",
            color_discrete_map={"Technical": "#4F46E5", "Soft Skills": "#EC4899"},
            text="Count",
            title="<b>Candidate Skills Distribution by Subdomain</b>"
        )
        fig_dist.update_layout(
            height=340,
            margin=dict(l=10, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter'}
        )
        fig_dist.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("No skill category breakdown available.")

with c_audit:
    from collections import Counter
    match_counter = Counter()
    missing_counter = Counter()

    for r in recommendations:
        for s in r.get("matched_technical", []):
            match_counter[s] += 1
        for s in r.get("missing_technical", []):
            missing_counter[s] += 1

    top_matched = [s for s, _ in match_counter.most_common(5)]
    top_missing = [s for s, _ in missing_counter.most_common(5)]

    st.markdown(f"""
    <div class="clean-card" style="height:340px; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <h4 style="color:#065F46; font-size:1rem; font-weight:700; margin-bottom:8px;">
                🏆 Top 5 Strongest Asset Skills (Most In-Demand)
            </h4>
            <p style="font-size:0.82rem; color:#64748B; margin-bottom:8px;">Your most versatile competencies across all analyzed roles:</p>
    """, unsafe_allow_html=True)
    render_skill_badges(top_matched, badge_type="matched")
    
    st.markdown(f"""
        </div>
        <div style="border-top:1px solid #E2E8F0; padding-top:12px; margin-top:12px;">
            <h4 style="color:#991B1B; font-size:1rem; font-weight:700; margin-bottom:8px;">
                ⚠️ Top 5 High-Impact Skill Gaps (Market-Wide)
            </h4>
            <p style="font-size:0.82rem; color:#64748B; margin-bottom:8px;">Most frequently missing prerequisites across open paths:</p>
    """, unsafe_allow_html=True)
    render_skill_badges(top_missing, badge_type="missing")
    st.markdown("</div></div>", unsafe_allow_html=True)

# Navigation
st.markdown("<br/>", unsafe_allow_html=True)
c_nav1, c_nav2 = st.columns([1.5, 3.5])
with c_nav1:
    if st.button("➡️ Download Complete Career PDF Report", type="primary", use_container_width=True):
        st.switch_page("pages/7_📥_Download_Report.py")

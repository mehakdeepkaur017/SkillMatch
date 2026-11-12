"""
SkillMatch AI – Job Matching & Compatibility Analysis (PAGE 3)
Calculates transparent compatibility between candidate skills/resume and target roles
using TF-IDF Cosine Similarity, Weighted Skill Overlap, and Multi-Role Comparison.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.helpers import (
    apply_custom_styles, init_session_state, render_skill_badges,
    render_metric_card, render_circular_score_component, save_current_analysis_to_db
)
from modules.job_matcher import JobMatcher
from modules.skill_extractor import SkillExtractor
from modules.skill_gap_analyzer import SkillGapAnalyzer
from modules.career_recommender import CareerRecommender
from modules.roadmap_generator import RoadmapGenerator
from modules.database import DatabaseManager

st.set_page_config(
    page_title="Job Matching | SkillMatch AI",
    page_icon="🎯",
    layout="wide"
)

apply_custom_styles()
init_session_state()

db = DatabaseManager()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="font-weight:800; color:#0F172A; margin-bottom:4px;">🎯 Job Matching & Compatibility Analysis</h2>
    <p style="color:#64748B; font-size:1rem;">
        Compare your profile against benchmark tech roles, paste custom requirements, or compare multiple roles side-by-side.
    </p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.resume_parsed:
    st.warning("⚠️ No candidate profile loaded yet. Please upload a resume or load a demo profile first.")
    if st.button("📄 Go to Resume Analyzer", type="primary"):
        st.switch_page("pages/1_📄_Resume_Analyzer.py")
    st.stop()

matcher = JobMatcher()
extractor = SkillExtractor()
gap_analyzer = SkillGapAnalyzer()
recommender = CareerRecommender()
roadmap_gen = RoadmapGenerator()

predefined_roles = matcher.get_predefined_roles()

# Tabs: Single Role Match vs Multi-Role Comparison
tab_single, tab_compare = st.tabs(["🎯 Single Role Matching", "⚖️ Compare Multiple Job Roles"])

# ====================================================
# TAB 1: SINGLE ROLE MATCHING
# ====================================================
with tab_single:
    st.markdown("<div class='section-title'>💼 Select or Input Target Job</div>", unsafe_allow_html=True)

    mode = st.radio(
        "Job Opportunity Source:",
        ["Select Predefined Industry Benchmark", "Paste Custom Job Posting"],
        horizontal=True,
        key="matching_job_source_radio"
    )

    target_role_title = ""
    job_description_text = ""
    required_tech = []
    required_soft = []
    preferred_skills = []

    if mode == "Select Predefined Industry Benchmark":
        default_idx = predefined_roles.index(st.session_state.last_target_role) if st.session_state.last_target_role in predefined_roles else 0
        selected_role = st.selectbox(
            "Choose benchmark role:",
            predefined_roles,
            index=default_idx,
            key="single_match_role_select"
        )
        target_role_title = selected_role
        role_details = matcher.get_role_details(selected_role)
        
        if role_details:
            job_description_text = role_details['job_description']
            required_tech = [s.strip() for s in str(role_details['required_technical_skills']).split(';') if s.strip()]
            required_soft = [s.strip() for s in str(role_details['required_soft_skills']).split(';') if s.strip()]
            preferred_skills = [s.strip() for s in str(role_details['preferred_skills']).split(';') if s.strip()]
            
            with st.expander(f"📋 View Full Benchmark Details for {selected_role}"):
                st.markdown(f"**Domain:** {role_details.get('category')} | **Experience Level:** {role_details.get('experience_level')}")
                st.markdown(f"**Typical Salary:** {role_details.get('typical_salary_range')} | **Market Outlook:** {role_details.get('industry_growth_outlook')}")
                st.markdown(f"**Required Education:** {role_details.get('education_required')}")
                st.markdown(f"**Description:**\n{job_description_text}")

    else:
        target_role_title = st.text_input("Custom Job Title:", value="Custom Target Opportunity", key="custom_job_title_input")
        job_description_text = st.text_area(
            "Paste Job Description & Requirements:",
            height=160,
            placeholder="Paste complete job requirements, qualifications, and responsibilities here...",
            key="custom_job_desc_input"
        )
        if not job_description_text.strip():
            st.info("Paste a job description above to calculate compatibility.")
            st.stop()
        
        extracted_from_jd = extractor.extract_skills(job_description_text)
        required_tech = extracted_from_jd["technical_skills"]
        required_soft = extracted_from_jd["soft_skills"]

    # Advanced scoring weights expander
    with st.expander("⚙️ Fine-Tune Compatibility Scoring Weights"):
        cw1, cw2, cw3 = st.columns(3)
        with cw1:
            w_tech = st.slider("Technical Skills Weight", 0.1, 0.8, 0.50, 0.05, key="w_tech_slider")
        with cw2:
            w_tfidf = st.slider("TF-IDF Semantic Match Weight", 0.1, 0.8, 0.35, 0.05, key="w_tfidf_slider")
        with cw3:
            w_soft = st.slider("Soft Skills Alignment Weight", 0.0, 0.5, 0.15, 0.05, key="w_soft_slider")
        
        total_w = w_tech + w_tfidf + w_soft
        weights = {"tech": w_tech / total_w, "tfidf": w_tfidf / total_w, "soft": w_soft / total_w}

    # RUN MATCHING CALCULATION
    match_result = matcher.calculate_compatibility(
        resume_text=st.session_state.resume_text,
        candidate_skills=st.session_state.candidate_skills,
        job_description=job_description_text,
        required_tech=required_tech,
        required_soft=required_soft,
        weights=weights
    )

    # Calculate gap & roadmap
    gap_res = gap_analyzer.analyze_gaps(
        candidate_skills=st.session_state.candidate_skills,
        required_tech=required_tech,
        required_soft=required_soft,
        preferred_skills=preferred_skills
    )
    missing_tech = match_result["skills"].get("missing_technical", [])
    roadmap = roadmap_gen.generate_roadmap(missing_tech)

    # Update session state
    st.session_state.last_match_result = match_result
    st.session_state.last_target_role = target_role_title
    st.session_state.generated_roadmap = roadmap

    overall_score = match_result["overall_compatibility_score"]
    breakdown = match_result["breakdown"]
    skills = match_result["skills"]

    st.markdown("---")

    # SAVE ANALYSIS BUTTON ROW
    col_act1, col_act2 = st.columns([1.5, 2.5])
    with col_act1:
        if st.button("💾 Save Analysis to Database", type="primary", use_container_width=True, key="save_analysis_btn"):
            saved_id = save_current_analysis_to_db(
                target_role=target_role_title,
                match_result=match_result,
                gap_result=gap_res
            )
            st.success(f"✅ Analysis saved to local SQLite (ID: {saved_id[:8]}...)!")
    with col_act2:
        if st.session_state.current_analysis_id:
            st.caption(f"💾 Active Record ID: `{st.session_state.current_analysis_id}` (Stored in `database/skillmatch.db`)")

    st.markdown("<br/>", unsafe_allow_html=True)

    # COMPATIBILITY SCORE DISPLAY WITH CIRCULAR GAUGE
    col_circle, col_breakdown = st.columns([1.2, 1.8])

    with col_circle:
        render_circular_score_component(overall_score, label="Match Score")

    with col_breakdown:
        st.markdown("<div style='font-size:1.1rem; font-weight:700; color:#0F172A; margin-bottom:10px;'>Scoring Component Breakdown</div>", unsafe_allow_html=True)
        cb1, cb2 = st.columns(2)
        with cb1:
            render_metric_card("Technical Match", f"{breakdown['technical_score']}%", f"Weight: {int(weights['tech']*100)}%")
        with cb2:
            render_metric_card("Semantic TF-IDF Fit", f"{breakdown['tfidf_similarity_score']}%", f"Weight: {int(weights['tfidf']*100)}%")
        
        cb3, cb4 = st.columns(2)
        with cb3:
            render_metric_card("Soft Skills Alignment", f"{breakdown['soft_score']}%", f"Weight: {int(weights['soft']*100)}%")
        with cb4:
            render_metric_card("Skill Coverage", f"{match_result['coverage_percentage']}%", f"{skills['total_matched_count']} of {skills['total_required_count']} Required")

    # GRANULAR SKILLS AUDIT
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 Granular Skills Audit</div>", unsafe_allow_html=True)

    c_sk1, c_sk2, c_sk3 = st.columns(3)

    with c_sk1:
        st.markdown(f"""
        <div class="clean-card" style="border-top: 4px solid #10B981; min-height: 270px;">
            <h4 style="color:#065F46; font-weight:700; margin-bottom:10px;">
                ✅ Matching Skills ({len(skills['matched_technical']) + len(skills['matched_soft'])})
            </h4>
            <p style="font-size:0.84rem; color:#64748B;">Skills in your profile that satisfy requirements:</p>
        """, unsafe_allow_html=True)
        if skills['matched_technical']:
            st.markdown("<b style='font-size:0.8rem; color:#065F46;'>Technical:</b>", unsafe_allow_html=True)
            render_skill_badges(skills['matched_technical'], badge_type="matched")
        if skills['matched_soft']:
            st.markdown("<b style='font-size:0.8rem; color:#065F46; margin-top:6px;'>Soft Skills:</b>", unsafe_allow_html=True)
            render_skill_badges(skills['matched_soft'], badge_type="soft")
        if not skills['matched_technical'] and not skills['matched_soft']:
            st.write("No direct required matches found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c_sk2:
        st.markdown(f"""
        <div class="clean-card" style="border-top: 4px solid #EF4444; min-height: 270px;">
            <h4 style="color:#991B1B; font-weight:700; margin-bottom:10px;">
                ❌ Missing Skills ({len(skills['missing_technical']) + len(skills['missing_soft'])})
            </h4>
            <p style="font-size:0.84rem; color:#64748B;">Core job prerequisites not found in your resume:</p>
        """, unsafe_allow_html=True)
        if skills['missing_technical']:
            st.markdown("<b style='font-size:0.8rem; color:#991B1B;'>Technical to Acquire:</b>", unsafe_allow_html=True)
            render_skill_badges(skills['missing_technical'], badge_type="missing")
        if skills['missing_soft']:
            st.markdown("<b style='font-size:0.8rem; color:#991B1B; margin-top:6px;'>Soft Skills:</b>", unsafe_allow_html=True)
            render_skill_badges(skills['missing_soft'], badge_type="missing")
        if not skills['missing_technical'] and not skills['missing_soft']:
            st.success("🎉 Complete 100% prerequisite match!")
        st.markdown("</div>", unsafe_allow_html=True)

    with c_sk3:
        st.markdown(f"""
        <div class="clean-card" style="border-top: 4px solid #3B82F6; min-height: 270px;">
            <h4 style="color:#1D4ED8; font-weight:700; margin-bottom:10px;">
                🌟 Additional Candidate Skills ({len(skills['additional_skills'])})
            </h4>
            <p style="font-size:0.84rem; color:#64748B;">Competencies in your profile outside target JD:</p>
        """, unsafe_allow_html=True)
        if skills['additional_skills']:
            render_skill_badges(skills['additional_skills'][:14], badge_type="bonus")
            if len(skills['additional_skills']) > 14:
                st.caption(f"+{len(skills['additional_skills']) - 14} additional skills")
        else:
            st.write("No additional unlisted skills found.")
        st.markdown("</div>", unsafe_allow_html=True)

    # METHODOLOGY & DISCLAIMER
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("""
    <div class="clean-card" style="background:#F8FAFC; border-left: 4px solid #4F46E5;">
        <h4 style="color:#0F172A; font-weight:700; margin-bottom:6px;">📐 Transparent Scoring Methodology</h4>
        <p style="font-size:0.86rem; color:#475569; margin-bottom:6px;">
            <code>Compatibility Score = (0.50 × TechMatch%) + (0.35 × TFIDF_CosineSim%) + (0.15 × SoftMatch%) + BonusBreadth</code>
        </p>
        <p style="font-size:0.82rem; color:#64748B; margin-bottom:0;">
            <b>⚠️ Formal Disclaimer:</b> The compatibility score measures keyword alignment and natural language semantic similarity against target criteria.
            It provides a quantitative skill benchmark and is <b>NOT a statistical probability or guarantee of employment</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Next steps navigation
    c_nav1, c_nav2 = st.columns([1.5, 3.5])
    with c_nav1:
        if st.button("➡️ Deep Dive into Skill Gap Analysis", type="primary", use_container_width=True, key="single_nav_gap_btn"):
            st.switch_page("pages/3_🔍_Skill_Gap_Analysis.py")

# ====================================================
# TAB 2: MULTI-ROLE SIDE-BY-SIDE COMPARISON
# ====================================================
with tab_compare:
    st.markdown("<div class='section-title'>⚖️ Side-by-Side Job Role Comparison</div>", unsafe_allow_html=True)
    st.caption("Select 2 to 4 roles to benchmark your compatibility scores, technical coverage, and missing gaps simultaneously.")

    default_compare_roles = [r for r in ["Data Scientist", "Machine Learning Engineer", "Data Analyst"] if r in predefined_roles]
    selected_compare_roles = st.multiselect(
        "Select benchmark roles to compare (2 to 4 recommended):",
        options=predefined_roles,
        default=default_compare_roles,
        max_selections=4,
        key="multi_compare_roles_select"
    )

    if len(selected_compare_roles) < 2:
        st.info("Please select at least 2 roles to generate a side-by-side comparison.")
    else:
        comparisons = matcher.compare_multiple_roles(
            resume_text=st.session_state.resume_text,
            candidate_skills=st.session_state.candidate_skills,
            roles_list=selected_compare_roles
        )
        df_comp = pd.DataFrame(comparisons)

        # Comparative Bar Chart
        fig_comp = px.bar(
            df_comp,
            x="job_title",
            y=["overall_score", "technical_score", "coverage_percentage"],
            barmode="group",
            labels={"value": "Score (%)", "job_title": "Role Title", "variable": "Metric"},
            color_discrete_map={
                "overall_score": "#4F46E5",
                "technical_score": "#2563EB",
                "coverage_percentage": "#10B981"
            },
            title="<b>Side-by-Side Compatibility Comparison</b>"
        )
        fig_comp.update_layout(
            height=340,
            margin=dict(l=10, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter'}
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        # Comparative Cards
        comp_cols = st.columns(len(comparisons))
        for idx, comp in enumerate(comparisons):
            with comp_cols[idx]:
                score_color = "#10B981" if comp["overall_score"] >= 70 else ("#3B82F6" if comp["overall_score"] >= 50 else "#F59E0B")
                st.markdown(f"""
                <div class="clean-card" style="border-top: 4px solid {score_color}; min-height: 380px;">
                    <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{comp['job_title']}</div>
                    <div style="font-size:0.8rem; color:#64748B; margin-bottom:8px;">{comp['category']}</div>
                    <div style="font-size:2.2rem; font-weight:900; color:{score_color};">{comp['overall_score']:.1f}%</div>
                    <div style="font-size:0.78rem; color:#64748B; margin-bottom:12px;">Overall Match</div>
                    <hr style="margin:8px 0; border-color:#E2E8F0;"/>
                    <div style="font-size:0.82rem; color:#334155; line-height:1.6;">
                        • <b>Technical Match:</b> {comp['technical_score']:.1f}%<br/>
                        • <b>Skill Coverage:</b> {comp['coverage_percentage']:.1f}%<br/>
                        • <b>Matched Count:</b> {comp['matched_count']} / {comp['required_count']}<br/>
                        • <b>Salary:</b> {comp['salary']}
                    </div>
                    <div style="margin-top:10px;">
                        <b style="font-size:0.8rem; color:#991B1B;">Key Missing:</b><br/>
                        <span style="font-size:0.8rem; color:#475569;">{', '.join(comp['missing_skills'][:3]) or 'None'}</span>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🎯 Select as Active Target", key=f"set_active_{comp['job_title']}", use_container_width=True):
                    st.session_state.last_target_role = comp['job_title']
                    st.success(f"Switched active target to {comp['job_title']}!")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

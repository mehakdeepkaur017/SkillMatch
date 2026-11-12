"""
SkillMatch AI – Download Report (PAGE 8)
Generates and downloads a complete, professional, multi-page career analysis PDF report using ReportLab.
"""
import streamlit as st
import datetime
from utils.helpers import (
    apply_custom_styles, init_session_state, render_skill_badges, render_metric_card
)
from modules.report_generator import ReportGenerator
from modules.job_matcher import JobMatcher

st.set_page_config(
    page_title="Download Career Report | SkillMatch AI",
    page_icon="📥",
    layout="wide"
)

apply_custom_styles()
init_session_state()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="font-weight:800; color:#0F172A; margin-bottom:4px;">📥 Download Complete Career Compatibility Report</h2>
    <p style="color:#64748B; font-size:1rem;">
        Generate an executive-grade, publication-quality PDF career assessment dossier containing all candidate diagnostics, gap matrices, recommendations, and roadmaps.
    </p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.resume_parsed:
    st.warning("⚠️ No resume has been parsed yet. Please upload a resume or load a demo sample.")
    if st.button("📄 Go to Resume Analyzer", type="primary"):
        st.switch_page("pages/1_📄_Resume_Analyzer.py")
    st.stop()

matcher = JobMatcher()
report_gen = ReportGenerator()

target_role = st.session_state.last_target_role or "Data Scientist"

# Ensure match result exists
if not st.session_state.last_match_result:
    role_info = matcher.get_role_details(target_role)
    if role_info:
        req_t = [s.strip() for s in str(role_info['required_technical_skills']).split(';') if s.strip()]
        req_s = [s.strip() for s in str(role_info['required_soft_skills']).split(';') if s.strip()]
        st.session_state.last_match_result = matcher.calculate_compatibility(
            st.session_state.resume_text,
            st.session_state.candidate_skills,
            role_info['job_description'],
            required_tech=req_t,
            required_soft=req_s
        )

match_result = st.session_state.last_match_result
recommendations = st.session_state.career_recommendations
roadmap = getattr(st.session_state, "generated_roadmap", None)

if not roadmap:
    from modules.roadmap_generator import RoadmapGenerator
    rg = RoadmapGenerator()
    missing_tech = match_result["skills"].get("missing_technical", [])
    roadmap = rg.generate_roadmap(missing_tech)
    st.session_state.generated_roadmap = roadmap

# ----------------------------------------------------
# REPORT PREVIEW CHECKLIST
# ----------------------------------------------------
c_prev1, c_prev2 = st.columns([1.5, 1.5])

with c_prev1:
    st.markdown("<div class='section-title'>📋 Report Content Checklist</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="clean-card">
        <ul style="font-size:0.9rem; color:#334155; line-height:2.0; padding-left:20px; margin-bottom:0;">
            <li>✅ <b>Candidate Dossier:</b> Email, Phone, Academic Degree, Experience</li>
            <li>✅ <b>Skills Inventory:</b> Possessed Technical & Soft Skills Breakdown</li>
            <li>✅ <b>Target Opportunity:</b> Detailed Benchmark against <b>""" + target_role + """</b></li>
            <li>✅ <b>Compatibility Rating:</b> Overall Score (""" + str(match_result['overall_compatibility_score']) + """%) + Mathematical Formula Breakdown</li>
            <li>✅ <b>Skills Alignment Audit:</b> Matched vs Missing vs Bonus Competencies</li>
            <li>✅ <b>Cross-Domain Career Paths:</b> Top 5 Ranked Alternative Recommendations</li>
            <li>✅ <b>Sequenced Upskilling Roadmap:</b> Step-by-Step Curriculum & Verified Resources</li>
            <li>✅ <b>Compliance & Ethics:</b> Transparent Non-Hiring Probability Disclaimer</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with c_prev2:
    st.markdown("<div class='section-title'>⚡ PDF Generation & Download</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="clean-card" style="text-align:center; padding:30px;">
        <div style="font-size:3rem; margin-bottom:8px;">📄</div>
        <h3 style="font-weight:800; color:#0F172A; margin-bottom:6px;">Ready to Export</h3>
        <p style="font-size:0.88rem; color:#64748B; margin-bottom:20px;">
            The PDF is dynamically rendered in memory using Python ReportLab.
        </p>
    """, unsafe_allow_html=True)

    candidate_data = {
        "contact_info": st.session_state.contact_info,
        "education": st.session_state.education,
        "experience": st.session_state.experience,
        "all_skills": st.session_state.candidate_skills,
        "technical_skills": st.session_state.technical_skills,
        "soft_skills": st.session_state.soft_skills
    }

    try:
        pdf_buffer = report_gen.generate_pdf(
            candidate_data=candidate_data,
            match_data=match_result,
            target_role=target_role,
            gap_data=None,
            recommendations=recommendations,
            roadmap=roadmap
        )
        
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_role_name = target_role.replace(" ", "_").replace("/", "_")
        file_download_name = f"SkillMatch_AI_Report_{safe_role_name}_{timestamp_str}.pdf"

        st.download_button(
            label="📥 Download PDF Career Report",
            data=pdf_buffer,
            file_name=file_download_name,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        st.success("✅ PDF Report successfully prepared and ready for download!")
    except Exception as e:
        st.error(f"Failed to generate PDF: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# LIVE SUMMARY SNAPSHOT
# ----------------------------------------------------
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>👁️ Live Executive Summary Snapshot</div>", unsafe_allow_html=True)

s_c1, s_c2, s_c3 = st.columns(3)
with s_c1:
    render_metric_card("Overall Match Score", f"{match_result['overall_compatibility_score']}%", f"Target: {target_role}")
with s_c2:
    render_metric_card("Core Tech Alignment", f"{match_result['breakdown']['technical_score']}%", "Prerequisite Skills Met")
with s_c3:
    render_metric_card("Semantic TF-IDF Fit", f"{match_result['breakdown']['tfidf_similarity_score']}%", "Natural Language Correlation")

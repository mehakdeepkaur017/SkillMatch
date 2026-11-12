"""
SkillMatch AI – Smart Career Compatibility Analyzer
Main Landing Page (PAGE 1)
"""
import streamlit as st
import os
import json
import pandas as pd
from utils.helpers import (
    apply_custom_styles, init_session_state, render_metric_card, save_current_analysis_to_db
)
from modules.resume_parser import ResumeParser
from modules.skill_extractor import SkillExtractor
from modules.job_matcher import JobMatcher
from modules.career_recommender import CareerRecommender
from modules.skill_gap_analyzer import SkillGapAnalyzer
from modules.roadmap_generator import RoadmapGenerator
from modules.database import DatabaseManager

st.set_page_config(
    page_title="SkillMatch AI | Smart Career Compatibility Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply unified SaaS theme and initialize session state with SQLite sync
apply_custom_styles()
init_session_state()

db = DatabaseManager()

# Sidebar Navigation & Quick Status
with st.sidebar:
    st.markdown("### ⚡ **SkillMatch AI**")
    st.caption("Intelligent Career Analytics & NLP Engine")
    st.markdown("---")
    
    st.markdown("#### 👤 **Current Session**")
    if st.session_state.resume_parsed:
        st.success(f"✅ **{st.session_state.resume_name}**")
        st.write(f"• **Skills Inventory:** {len(st.session_state.candidate_skills)}")
        st.write(f"• **Active Target:** {st.session_state.last_target_role}")
        if st.session_state.candidate_id:
            st.caption(f"💾 *Saved locally in SQLite database*")
    else:
        st.info("ℹ️ No active profile loaded.")
        st.caption("Upload your PDF in the **Resume Analyzer** or load a sample below.")
    
    st.markdown("---")
    st.markdown("#### 📁 **Quick Load Demo Profile**")
    sample_files = {
        "Data Scientist": "assets/samples/Sample_Data_Scientist.pdf",
        "Full Stack Web Developer": "assets/samples/Sample_FullStack_Developer.pdf",
        "Cloud & DevOps Engineer": "assets/samples/Sample_DevOps_Engineer.pdf",
        "Fresh Graduate": "assets/samples/Sample_Fresh_Graduate.pdf"
    }
    selected_sample = st.selectbox("Select demo candidate:", list(sample_files.keys()), key="sidebar_sample_select")
    if st.button("🚀 Load Demo Profile", key="load_sample_btn", use_container_width=True):
        sample_path = sample_files[selected_sample]
        if os.path.exists(sample_path):
            with st.spinner("Extracting, analyzing, and persisting demo profile..."):
                parser = ResumeParser()
                extractor = SkillExtractor()
                matcher = JobMatcher()
                gap_analyzer = SkillGapAnalyzer()
                recommender = CareerRecommender()
                roadmap_gen = RoadmapGenerator()
                
                parse_res = parser.parse(sample_path)
                if parse_res["success"]:
                    skills_res = extractor.extract_skills(parse_res["raw_text"])
                    
                    # 1. Update session state
                    st.session_state.resume_parsed = True
                    st.session_state.resume_name = os.path.basename(sample_path)
                    st.session_state.resume_text = parse_res["raw_text"]
                    st.session_state.candidate_skills = skills_res["all_skills"]
                    st.session_state.technical_skills = skills_res["technical_skills"]
                    st.session_state.soft_skills = skills_res["soft_skills"]
                    st.session_state.technical_by_cat = skills_res["technical_by_category"]
                    st.session_state.soft_by_cat = skills_res["soft_by_category"]
                    st.session_state.contact_info = parse_res["contact_info"]
                    st.session_state.education = parse_res["education"]
                    st.session_state.experience = parse_res["experience"]
                    
                    # 2. Persist Candidate & Resume Profile to SQLite
                    cand_id = db.save_or_update_candidate(
                        name=parse_res["contact_info"].get("name") or selected_sample,
                        email=parse_res["contact_info"].get("email") or "",
                        phone=parse_res["contact_info"].get("phone") or "",
                        linkedin=parse_res["contact_info"].get("linkedin") or "",
                        github=parse_res["contact_info"].get("github") or ""
                    )
                    st.session_state.candidate_id = cand_id
                    
                    prof_id = db.save_resume_profile(
                        candidate_id=cand_id,
                        filename=os.path.basename(sample_path),
                        summary=f"{selected_sample} Profile",
                        education=parse_res["education"],
                        experience=parse_res["experience"],
                        all_skills=skills_res["all_skills"],
                        technical_skills=skills_res["technical_skills"],
                        soft_skills=skills_res["soft_skills"],
                        raw_text=parse_res["raw_text"]
                    )
                    st.session_state.profile_id = prof_id
                    
                    # 3. Calculate recommendations
                    recs = recommender.recommend_roles(
                        parse_res["raw_text"],
                        skills_res["all_skills"],
                        top_n=10
                    )
                    st.session_state.career_recommendations = recs
                    st.session_state.domain_affinities = recommender.predict_domain_affinity(parse_res["raw_text"])
                    
                    # 4. Target Role matching & saving to SQLite
                    target_role = selected_sample if selected_sample in matcher.get_predefined_roles() else "Data Scientist"
                    st.session_state.last_target_role = target_role
                    role_info = matcher.get_role_details(target_role)
                    if role_info:
                        req_t = [s.strip() for s in str(role_info['required_technical_skills']).split(';') if s.strip()]
                        req_s = [s.strip() for s in str(role_info['required_soft_skills']).split(';') if s.strip()]
                        match_res = matcher.calculate_compatibility(
                            parse_res["raw_text"],
                            skills_res["all_skills"],
                            role_info['job_description'],
                            required_tech=req_t,
                            required_soft=req_s
                        )
                        st.session_state.last_match_result = match_res

                        # Gap Analysis
                        gap_res = gap_analyzer.analyze_gaps(
                            candidate_skills=skills_res["all_skills"],
                            required_tech=req_t,
                            required_soft=req_s
                        )

                        # Roadmap
                        missing_tech = match_res["skills"]["missing_technical"]
                        roadmap = roadmap_gen.generate_roadmap(missing_tech)
                        st.session_state.generated_roadmap = roadmap

                        # Save full analysis to SQLite
                        analysis_id = db.save_full_analysis(
                            candidate_id=cand_id,
                            profile_id=prof_id,
                            target_role=target_role,
                            job_source="predefined",
                            job_description=role_info['job_description'],
                            match_result=match_res,
                            gap_result=gap_res,
                            recommendations=recs,
                            domain_affinities=st.session_state.domain_affinities,
                            roadmap=roadmap
                        )
                        st.session_state.current_analysis_id = analysis_id

                    st.rerun()

    st.markdown("---")
    st.caption("🔒 **Local SQLite Persistence**: Zero external API transmission.")

# ----------------------------------------------------
# HERO SECTION
# ----------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <span style="background:rgba(255,255,255,0.18); padding:4px 14px; border-radius:999px; font-size:0.82rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em;">
                ⚡ AI-POWERED CAREER COMPATIBILITY ANALYZER
            </span>
            <h1 style="margin-top:12px;">Discover Your Career Compatibility</h1>
            <p>
                SkillMatch AI uses natural language processing, TF-IDF vectorization, and curated skill taxonomies
                to measure how closely your resume aligns with tech roles, identify critical skill gaps, and generate sequenced learning roadmaps.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Primary & Secondary Call-to-Action Buttons
col_cta1, col_cta2, col_cta3 = st.columns([1.2, 1.4, 2.4])
with col_cta1:
    if st.button("🚀 Get Started", type="primary", use_container_width=True):
        st.switch_page("pages/1_📄_Resume_Analyzer.py")
with col_cta2:
    show_features = st.button("🔍 Explore Platform Features", use_container_width=True)

# ----------------------------------------------------
# RECENT ANALYSIS HISTORY (SQLITE SOURCE OF TRUTH)
# ----------------------------------------------------
recent_analyses = db.get_all_analyses(limit=3)
if recent_analyses:
    st.markdown("<div class='section-title'>🕒 Recent Saved Analyses</div>", unsafe_allow_html=True)
    st.caption("Your previous evaluations are stored permanently in local SQLite and remain available across browser sessions.")
    
    rec_cols = st.columns(min(len(recent_analyses), 3))
    for idx, analysis in enumerate(recent_analyses[:3]):
        with rec_cols[idx]:
            score_color = "#10B981" if analysis["overall_score"] >= 70 else ("#3B82F6" if analysis["overall_score"] >= 50 else "#F59E0B")
            st.markdown(f"""
            <div class="clean-card" style="border-top: 4px solid {score_color}; padding:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.78rem; color:#64748B; font-weight:600;">{analysis['created_at'][:10]}</span>
                    <span style="font-size:1.1rem; font-weight:800; color:{score_color};">{analysis['overall_score']:.1f}%</span>
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#0F172A; margin:6px 0;">{analysis['target_role']}</div>
                <div style="font-size:0.8rem; color:#64748B; margin-bottom:12px;">Profile: {analysis['filename']}</div>
            """, unsafe_allow_html=True)
            if st.button(f"📂 Reopen Analysis", key=f"reopen_home_{analysis['id']}", use_container_width=True):
                full_details = db.get_analysis_details(analysis["id"])
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
                    st.success(f"Loaded {analysis['target_role']} analysis!")
                    st.switch_page("pages/2_🎯_Job_Matching.py")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# LIVE PROJECT STATISTICS
# ----------------------------------------------------
st.markdown("<div class='section-title'>📊 Platform Analytics & Capabilities</div>", unsafe_allow_html=True)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)

try:
    with open("data/skills_taxonomy.json", "r", encoding="utf-8") as f:
        tax_data = json.load(f)
        total_tech = sum(len(v) for v in tax_data.get("technical_skills", {}).values())
        total_soft = sum(len(v) for v in tax_data.get("soft_skills", {}).values())
        total_aliases = len(tax_data.get("aliases", {}))
        total_skills_count = total_tech + total_soft + total_aliases
except Exception:
    total_skills_count = 500

try:
    df_roles_stat = pd.read_csv("data/job_roles.csv")
    roles_count = len(df_roles_stat)
    categories_count = df_roles_stat['category'].nunique()
except Exception:
    roles_count = 15
    categories_count = 5

all_analyses_count = len(db.get_all_analyses(limit=500))

with col_s1:
    render_metric_card("Skills Taxonomy", f"{total_skills_count}+", "Tech & Soft Skills")
with col_s2:
    render_metric_card("Benchmark Roles", f"{roles_count}", f"{categories_count} Industry Domains")
with col_s3:
    render_metric_card("Saved Analyses", f"{all_analyses_count}", "SQLite Source of Truth")
with col_s4:
    render_metric_card("Local Privacy", "100% On-Device", "Zero Paid API Transmission")

st.markdown("<br/>", unsafe_allow_html=True)

# ----------------------------------------------------
# HOW IT WORKS
# ----------------------------------------------------
st.markdown("<div class='section-title'>⚙️ How It Works</div>", unsafe_allow_html=True)

w1, w2, w3, w4 = st.columns(4)

with w1:
    st.markdown("""
    <div class="clean-card" style="text-align:center; min-height:210px;">
        <div style="font-size:2rem; margin-bottom:8px;">📄</div>
        <h4 style="margin-bottom:6px; font-weight:700;">1. Upload Resume</h4>
        <p style="font-size:0.86rem; color:#64748B;">
            Upload PDF resume. PyMuPDF extracts text, contact, education, and years of experience locally.
        </p>
    </div>
    """, unsafe_allow_html=True)

with w2:
    st.markdown("""
    <div class="clean-card" style="text-align:center; min-height:210px;">
        <div style="font-size:2rem; margin-bottom:8px;">🧠</div>
        <h4 style="margin-bottom:6px; font-weight:700;">2. NLP Skill Extraction</h4>
        <p style="font-size:0.86rem; color:#64748B;">
            Identifies technical competencies and soft skills using boundary regex and alias resolution.
        </p>
    </div>
    """, unsafe_allow_html=True)

with w3:
    st.markdown("""
    <div class="clean-card" style="text-align:center; min-height:210px;">
        <div style="font-size:2rem; margin-bottom:8px;">🎯</div>
        <h4 style="margin-bottom:6px; font-weight:700;">3. Hybrid Matching</h4>
        <p style="font-size:0.86rem; color:#64748B;">
            Transparent mathematical scoring combining 50% tech overlap, 35% TF-IDF, and 15% soft skills.
        </p>
    </div>
    """, unsafe_allow_html=True)

with w4:
    st.markdown("""
    <div class="clean-card" style="text-align:center; min-height:210px;">
        <div style="font-size:2rem; margin-bottom:8px;">🗺️</div>
        <h4 style="margin-bottom:6px; font-weight:700;">4. Roadmap & Reports</h4>
        <p style="font-size:0.86rem; color:#64748B;">
            Track milestone completion, explore multi-role paths, and export executive ReportLab PDF reports.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# FEATURE SHOWCASE CARDS
# ----------------------------------------------------
st.markdown("<div class='section-title'>💎 Core Application Capabilities</div>", unsafe_allow_html=True)

f1, f2 = st.columns(2)

with f1:
    st.markdown("""
    <div class="clean-card">
        <h4 style="color:#4F46E5; margin-bottom:8px; font-weight:700;">🎯 Transparent Compatibility Scoring</h4>
        <p style="font-size:0.88rem; color:#475569; line-height:1.5;">
            Unlike opaque ATS algorithms, SkillMatch AI makes every calculation explicit.
            Scores reflect <b>50% core technical match</b>, <b>35% TF-IDF semantic alignment</b>,
            and <b>15% soft skills</b>, with explicit non-guarantee disclosures.
        </p>
        <span class="skill-tag">TF-IDF Vectorizer</span>
        <span class="skill-tag">Cosine Similarity</span>
        <span class="skill-tag">Weighted Overlap</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="clean-card">
        <h4 style="color:#4F46E5; margin-bottom:8px; font-weight:700;">🚀 Multi-Role Career Recommendations & Compare</h4>
        <p style="font-size:0.88rem; color:#475569; line-height:1.5;">
            Benchmark your profile across all 15 industry roles or compare multiple roles side-by-side. Our trained supervised classifier provides domain affinity confidence distributions.
        </p>
        <span class="skill-tag">Supervised Classifier</span>
        <span class="skill-tag">Side-by-Side Compare</span>
        <span class="skill-tag">Domain Affinity</span>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="clean-card">
        <h4 style="color:#4F46E5; margin-bottom:8px; font-weight:700;">🔍 Granular Skill Gap Prioritization</h4>
        <p style="font-size:0.88rem; color:#475569; line-height:1.5;">
            Pinpoints exact missing prerequisites and prioritizes them into <b>Critical</b>, <b>High</b>, and <b>Medium</b> importance tiers with actionable learning rationales.
        </p>
        <span class="skill-tag">Priority Ranking</span>
        <span class="skill-tag">Coverage Ratio</span>
        <span class="skill-tag">Targeted Upskilling</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="clean-card">
        <h4 style="color:#4F46E5; margin-bottom:8px; font-weight:700;">💾 Permanent SQLite Persistence & Milestones</h4>
        <p style="font-size:0.88rem; color:#475569; line-height:1.5;">
            All analysis history, candidate profiles, and learning milestone progress are permanently saved in local SQLite. Refresh your browser anytime without losing your work.
        </p>
        <span class="skill-tag">SQLite Database</span>
        <span class="skill-tag">Roadmap Tracking</span>
        <span class="skill-tag">ReportLab PDF Export</span>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer-text">
    SkillMatch AI — Smart Career Compatibility Analyzer • Developed with Python, Scikit-learn, PyMuPDF, Streamlit, SQLite, and ReportLab.
</div>
""", unsafe_allow_html=True)

"""
SkillMatch AI – Resume Analyzer (PAGE 2)
Uploads PDF resume, extracts candidate details, technical & soft skills,
and synchronizes candidate profiles directly with the SQLite database.
"""
import streamlit as st
import os
from utils.helpers import (
    apply_custom_styles, init_session_state, render_skill_badges, render_metric_card
)
from modules.resume_parser import ResumeParser
from modules.skill_extractor import SkillExtractor
from modules.career_recommender import CareerRecommender
from modules.job_matcher import JobMatcher
from modules.database import DatabaseManager

st.set_page_config(
    page_title="Resume Analyzer | SkillMatch AI",
    page_icon="📄",
    layout="wide"
)

apply_custom_styles()
init_session_state()

db = DatabaseManager()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="font-weight:800; color:#0F172A; margin-bottom:4px;">📄 Resume Analyzer & Information Extraction</h2>
    <p style="color:#64748B; font-size:1rem;">
        Upload a PDF resume to extract candidate contact details, academic credentials, work experience indicators, and categorized technical & soft skills.
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# UPLOAD SECTION
# ----------------------------------------------------
col_up1, col_up2 = st.columns([2.6, 1.4])

with col_up1:
    uploaded_file = st.file_uploader(
        "Upload Candidate Resume (PDF format only):",
        type=["pdf"],
        help="Upload a standard PDF resume. Files are processed entirely locally in memory and saved to your local SQLite database."
    )

with col_up2:
    st.markdown("<div style='font-size:0.9rem; font-weight:700; color:#334155; margin-bottom:8px;'>Or Load Sample Demo Profile:</div>", unsafe_allow_html=True)
    sample_files = {
        "Data Scientist": "assets/samples/Sample_Data_Scientist.pdf",
        "Full Stack Web Developer": "assets/samples/Sample_FullStack_Developer.pdf",
        "Cloud & DevOps Engineer": "assets/samples/Sample_DevOps_Engineer.pdf",
        "Fresh Graduate": "assets/samples/Sample_Fresh_Graduate.pdf"
    }
    selected_sample = st.selectbox("Select demo profile:", list(sample_files.keys()), key="analyzer_sample_select")
    if st.button("📥 Load Selected Sample", key="analyzer_load_sample_btn", use_container_width=True):
        sample_path = sample_files[selected_sample]
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                uploaded_file = f.read()
                st.session_state.resume_name = os.path.basename(sample_path)

parser = ResumeParser()
extractor = SkillExtractor()
recommender = CareerRecommender()
matcher = JobMatcher()

# Process uploaded file if provided
if uploaded_file is not None:
    file_bytes = uploaded_file if isinstance(uploaded_file, (bytes, bytearray)) else uploaded_file.getvalue()
    file_name = getattr(uploaded_file, "name", st.session_state.resume_name)
    
    with st.spinner("Extracting text and identifying skills via NLP..."):
        parse_result = parser.parse(file_bytes)
        
        if not parse_result["success"]:
            st.error(f"❌ **Resume Extraction Error:** {parse_result.get('error')}")
            st.info("💡 **Tip:** Ensure the PDF is not password-protected and contains selectable text rather than scanned images.")
        else:
            skills_res = extractor.extract_skills(parse_result["raw_text"])
            
            # Store into session state
            st.session_state.resume_parsed = True
            st.session_state.resume_name = file_name
            st.session_state.resume_text = parse_result["raw_text"]
            st.session_state.candidate_skills = skills_res["all_skills"]
            st.session_state.technical_skills = skills_res["technical_skills"]
            st.session_state.soft_skills = skills_res["soft_skills"]
            st.session_state.technical_by_cat = skills_res["technical_by_category"]
            st.session_state.soft_by_cat = skills_res["soft_by_category"]
            st.session_state.contact_info = parse_result["contact_info"]
            st.session_state.education = parse_result["education"]
            st.session_state.experience = parse_result["experience"]
            
            # Persist to SQLite
            cand_id = db.save_or_update_candidate(
                name=parse_result["contact_info"].get("name") or "Candidate",
                email=parse_result["contact_info"].get("email") or "",
                phone=parse_result["contact_info"].get("phone") or "",
                linkedin=parse_result["contact_info"].get("linkedin") or "",
                github=parse_result["contact_info"].get("github") or "",
                candidate_id=st.session_state.candidate_id
            )
            st.session_state.candidate_id = cand_id
            
            prof_id = db.save_resume_profile(
                candidate_id=cand_id,
                filename=file_name,
                summary=f"Profile for {file_name}",
                education=parse_result["education"],
                experience=parse_result["experience"],
                all_skills=skills_res["all_skills"],
                technical_skills=skills_res["technical_skills"],
                soft_skills=skills_res["soft_skills"],
                raw_text=parse_result["raw_text"]
            )
            st.session_state.profile_id = prof_id

            # Pre-compute recommendations
            st.session_state.career_recommendations = recommender.recommend_roles(
                parse_result["raw_text"],
                skills_res["all_skills"],
                top_n=10
            )
            st.session_state.domain_affinities = recommender.predict_domain_affinity(parse_result["raw_text"])

            if parse_result.get("warning"):
                st.warning(f"⚠️ {parse_result['warning']}")
            else:
                st.success(f"✅ Successfully analyzed & saved **{file_name}** ({parse_result['page_count']} page(s)) to local database.")

# ----------------------------------------------------
# DISPLAY EXTRACTED RESULTS
# ----------------------------------------------------
if st.session_state.resume_parsed:
    st.markdown("---")
    
    # Overview Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Total Skills Found", f"{len(st.session_state.candidate_skills)}", "Identified in Resume")
    with m2:
        render_metric_card("Technical Skills", f"{len(st.session_state.technical_skills)}", "Languages, Tools & Frameworks")
    with m3:
        render_metric_card("Soft Skills", f"{len(st.session_state.soft_skills)}", "Interpersonal & Leadership")
    with m4:
        exp = st.session_state.experience
        exp_txt = f"{exp.get('estimated_years', 0)} Years" if exp.get('has_experience') else "Entry-Level"
        render_metric_card("Experience Profile", exp_txt, exp.get('seniority_level', 'Fresher'))

    # Candidate Profile Cards
    st.markdown("<br/>", unsafe_allow_html=True)
    c_info1, c_info2 = st.columns([1.2, 1.8])
    
    with c_info1:
        st.markdown("<div class='section-title'>👤 Candidate Information</div>", unsafe_allow_html=True)
        ci = st.session_state.contact_info
        email_str = ci.get('email') or "Not detected"
        phone_str = ci.get('phone') or "Not detected"
        linkedin_str = ci.get('linkedin') or "Not detected"
        github_str = ci.get('github') or "Not detected"

        st.markdown(f"""
        <div class="clean-card">
            <div style="font-size:0.9rem; line-height:2.0;">
                <b>📧 Email:</b> {email_str}<br/>
                <b>📱 Phone:</b> {phone_str}<br/>
                <b>💼 LinkedIn:</b> {f'<a href="{linkedin_str}" target="_blank">{linkedin_str}</a>' if ci.get('linkedin') else linkedin_str}<br/>
                <b>🐙 GitHub:</b> {f'<a href="{github_str}" target="_blank">{github_str}</a>' if ci.get('github') else github_str}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-title'>🎓 Education & Academics</div>", unsafe_allow_html=True)
        edu_items = st.session_state.education
        if edu_items:
            for edu in edu_items:
                st.markdown(f"""
                <div class="clean-card" style="padding:14px 18px; margin-bottom:10px;">
                    <b style="color:#4F46E5;">{edu.get('degree_type')}</b><br/>
                    <span style="font-size:0.84rem; color:#64748B;">Mention: {edu.get('raw_mention')}</span><br/>
                    <span style="font-size:0.8rem; font-weight:700; color:#0F172A;">Year: {edu.get('estimated_year')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific academic degree pattern explicitly detected.")

    with c_info2:
        st.markdown("<div class='section-title'>🏷️ Identified Skills by Category</div>", unsafe_allow_html=True)
        
        tab_tech, tab_soft, tab_manage = st.tabs(["💻 Technical Skills", "🤝 Soft Skills", "✏️ Edit / Add Skills"])
        
        with tab_tech:
            if st.session_state.technical_by_cat:
                for subcat, skills in st.session_state.technical_by_cat.items():
                    st.markdown(f"<div style='font-weight:700; font-size:0.88rem; color:#4338CA; margin-top:10px; margin-bottom:4px;'>{subcat} ({len(skills)})</div>", unsafe_allow_html=True)
                    render_skill_badges(skills, badge_type="default")
            else:
                render_skill_badges(st.session_state.technical_skills, badge_type="default")

        with tab_soft:
            if st.session_state.soft_by_cat:
                for subcat, skills in st.session_state.soft_by_cat.items():
                    st.markdown(f"<div style='font-weight:700; font-size:0.88rem; color:#86198F; margin-top:10px; margin-bottom:4px;'>{subcat} ({len(skills)})</div>", unsafe_allow_html=True)
                    render_skill_badges(skills, badge_type="soft")
            else:
                render_skill_badges(st.session_state.soft_skills, badge_type="soft")

        with tab_manage:
            st.markdown("<p style='font-size:0.88rem; color:#475569;'>Review and fine-tune your extracted skills. Added or removed skills are permanently updated in SQLite.</p>", unsafe_allow_html=True)
            
            all_tax_skills = sorted(list(extractor.all_canonical_skills))
            new_skills_to_add = st.multiselect(
                "Add skills from taxonomy:",
                options=[s for s in all_tax_skills if s not in st.session_state.candidate_skills],
                key="multiselect_add_skills"
            )
            
            c_add1, c_add2 = st.columns([1.2, 0.8])
            with c_add1:
                custom_skill_input = st.text_input("Or type custom skill name:", placeholder="e.g., PyTorch, GraphQL, Tableau")
            with c_add2:
                st.write("")
                st.write("")
                if st.button("➕ Add to Profile", use_container_width=True):
                    added_count = 0
                    if new_skills_to_add:
                        for s in new_skills_to_add:
                            if s not in st.session_state.candidate_skills:
                                st.session_state.candidate_skills.append(s)
                                added_count += 1
                    if custom_skill_input.strip():
                        norm_custom = extractor.standardize_skill_name(custom_skill_input.strip())
                        if norm_custom not in st.session_state.candidate_skills:
                            st.session_state.candidate_skills.append(norm_custom)
                            added_count += 1
                    
                    if added_count > 0:
                        st.session_state.candidate_skills = sorted(list(set(st.session_state.candidate_skills)))
                        st.session_state.technical_skills = [
                            s for s in st.session_state.candidate_skills if s in extractor.canonical_tech_skills or s not in extractor.canonical_soft_skills
                        ]
                        st.session_state.soft_skills = [
                            s for s in st.session_state.candidate_skills if s in extractor.canonical_soft_skills
                        ]
                        # Sync update to SQLite
                        if st.session_state.candidate_id and st.session_state.profile_id:
                            db.save_resume_profile(
                                candidate_id=st.session_state.candidate_id,
                                filename=st.session_state.resume_name,
                                summary="Updated Profile",
                                education=st.session_state.education,
                                experience=st.session_state.experience,
                                all_skills=st.session_state.candidate_skills,
                                technical_skills=st.session_state.technical_skills,
                                soft_skills=st.session_state.soft_skills,
                                raw_text=st.session_state.resume_text
                            )
                        st.success(f"Added {added_count} skill(s) and saved to database!")
                        st.rerun()

            st.markdown("---")
            st.markdown("<div style='font-weight:700; font-size:0.85rem; color:#64748B;'>Active Skills (Remove if misidentified):</div>", unsafe_allow_html=True)
            skills_to_remove = st.multiselect(
                "Select skills to remove:",
                options=st.session_state.candidate_skills,
                key="multiselect_remove_skills"
            )
            if st.button("🗑️ Remove Selected Skills", type="secondary"):
                if skills_to_remove:
                    st.session_state.candidate_skills = [s for s in st.session_state.candidate_skills if s not in skills_to_remove]
                    st.session_state.technical_skills = [s for s in st.session_state.technical_skills if s not in skills_to_remove]
                    st.session_state.soft_skills = [s for s in st.session_state.soft_skills if s not in skills_to_remove]
                    # Sync update to SQLite
                    if st.session_state.candidate_id and st.session_state.profile_id:
                        db.save_resume_profile(
                            candidate_id=st.session_state.candidate_id,
                            filename=st.session_state.resume_name,
                            summary="Updated Profile",
                            education=st.session_state.education,
                            experience=st.session_state.experience,
                            all_skills=st.session_state.candidate_skills,
                            technical_skills=st.session_state.technical_skills,
                            soft_skills=st.session_state.soft_skills,
                            raw_text=st.session_state.resume_text
                        )
                    st.success(f"Removed {len(skills_to_remove)} skill(s) and updated database.")
                    st.rerun()

    # Raw Text Expander
    st.markdown("<br/>", unsafe_allow_html=True)
    with st.expander("👁️ View Full Extracted Resume Text"):
        st.text_area("Raw Text Content", st.session_state.resume_text, height=240, disabled=True)

    # Next steps action button
    st.markdown("<br/>", unsafe_allow_html=True)
    col_nav1, col_nav2 = st.columns([1.5, 3.5])
    with col_nav1:
        if st.button("➡️ Proceed to Job Matching", type="primary", use_container_width=True):
            st.switch_page("pages/2_🎯_Job_Matching.py")

else:
    st.info("👆 Please upload a PDF resume or load a demo sample above to begin analysis.")

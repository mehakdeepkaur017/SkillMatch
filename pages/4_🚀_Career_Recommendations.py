"""
SkillMatch AI – Career Recommendations (PAGE 5)
Evaluates candidate compatibility across all industry roles and uses the supervised ML model
to recommend the strongest matching and adjacent career tracks.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from utils.helpers import apply_custom_styles, init_session_state, render_skill_badges, render_metric_card
from modules.career_recommender import CareerRecommender

st.set_page_config(
    page_title="Career Recommendations | SkillMatch AI",
    page_icon="🚀",
    layout="wide"
)

apply_custom_styles()
init_session_state()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h2 style="font-weight:800; color:#0F172A; margin-bottom:4px;">🚀 Smart Career Path Recommendations</h2>
    <p style="color:#64748B; font-size:1rem;">
        Discover which tech roles offer the highest immediate synergy with your current skill set, and explore realistic adjacent career pivots.
    </p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.resume_parsed:
    st.warning("⚠️ No resume has been parsed yet. Please upload a resume or load a sample resume first.")
    if st.button("📄 Go to Resume Analyzer", type="primary"):
        st.switch_page("pages/1_📄_Resume_Analyzer.py")
    st.stop()

recommender = CareerRecommender()

# Ensure recommendations exist in state
if not st.session_state.career_recommendations:
    with st.spinner("Calculating recommendations across all industry roles..."):
        recs = recommender.recommend_roles(
            st.session_state.resume_text,
            st.session_state.candidate_skills,
            top_n=15
        )
        st.session_state.career_recommendations = recs
        st.session_state.domain_affinities = recommender.predict_domain_affinity(st.session_state.resume_text)

recommendations = st.session_state.career_recommendations
affinities = st.session_state.domain_affinities

# ----------------------------------------------------
# SUPERVISED DOMAIN CLASSIFIER INSIGHTS
# ----------------------------------------------------
st.markdown("<div class='section-title'>🧠 Machine Learning Domain Affinity</div>", unsafe_allow_html=True)

c_ml1, c_ml2 = st.columns([1.2, 1.8])

with c_ml1:
    st.markdown("""
    <div class="clean-card" style="min-height: 250px;">
        <h4 style="color:#4F46E5; font-weight:700; margin-bottom:6px;">Supervised Role Classifier</h4>
        <p style="font-size:0.86rem; color:#475569; line-height:1.5;">
            Our trained Logistic Regression classifier predicts the software/data subdomain that most naturally aligns with your resume text patterns and vocabulary.
        </p>
    """, unsafe_allow_html=True)
    if affinities:
        top_cat = affinities[0]
        st.markdown(f"""
        <div style="background:#EEF2FF; border-radius:10px; padding:14px 16px; margin-top:8px;">
            <div style="font-size:0.78rem; color:#6366F1; font-weight:700; text-transform:uppercase;">Primary Predicted Domain</div>
            <div style="font-size:1.35rem; font-weight:800; color:#312E81;">{top_cat['category']}</div>
            <div style="font-size:0.85rem; color:#475569; margin-top:2px;">Model Confidence: <b>{top_cat['probability_pct']}%</b></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c_ml2:
    if affinities:
        df_aff = pd.DataFrame(affinities)
        fig_aff = px.bar(
            df_aff,
            x="probability_pct",
            y="category",
            orientation="h",
            color="probability_pct",
            color_continuous_scale="Purples",
            text="probability_pct",
            labels={"probability_pct": "Confidence (%)", "category": "Tech Domain"},
            title="<b>Predicted Domain Alignment Probability Distribution</b>"
        )
        fig_aff.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter'},
            coloraxis_showscale=False
        )
        fig_aff.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_aff.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_aff, use_container_width=True)

# ----------------------------------------------------
# RANKED CAREER ROLES LIST
# ----------------------------------------------------
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🏆 Ranked Job Role Matches</div>", unsafe_allow_html=True)

# Filtering and Sorting controls
c_filt1, c_filt2 = st.columns([1.5, 1.5])
categories = ["All Domains"] + sorted(list(set(r["category"] for r in recommendations)))
with c_filt1:
    selected_cat = st.selectbox("Filter by Domain / Field:", categories)
with c_filt2:
    sort_option = st.selectbox("Sort By:", ["Compatibility Score (High to Low)", "Coverage % (High to Low)", "Technical Match (High to Low)"])

filtered_recs = recommendations
if selected_cat != "All Domains":
    filtered_recs = [r for r in filtered_recs if r["category"] == selected_cat]

if sort_option == "Coverage % (High to Low)":
    filtered_recs = sorted(filtered_recs, key=lambda x: x["coverage_percentage"], reverse=True)
elif sort_option == "Technical Match (High to Low)":
    filtered_recs = sorted(filtered_recs, key=lambda x: x["technical_score"], reverse=True)
else:
    filtered_recs = sorted(filtered_recs, key=lambda x: x["compatibility_score"], reverse=True)

# Display Recommendation Cards
for idx, rec in enumerate(filtered_recs, 1):
    score = rec["compatibility_score"]
    
    if score >= 75:
        tier_color = "#10B981"
        badge_lbl = "High Match"
    elif score >= 50:
        tier_color = "#3B82F6"
        badge_lbl = "Moderate Match"
    else:
        tier_color = "#F59E0B"
        badge_lbl = "Upskilling Needed"

    with st.container():
        st.markdown(f"""
        <div class="clean-card" style="border-left: 6px solid {tier_color}; margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; margin-bottom:8px;">
                <div>
                    <span style="font-size:0.78rem; background:#F1F5F9; color:#475569; padding:2px 8px; border-radius:6px; font-weight:700;">#{idx} RANK</span>
                    <span style="font-size:1.3rem; font-weight:800; color:#0F172A; margin-left:8px;">{rec['job_title']}</span>
                    <span style="font-size:0.85rem; color:#64748B; margin-left:8px;">• {rec['category']} ({rec['experience_level']})</span>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:1.6rem; font-weight:800; color:{tier_color};">{score}%</span>
                    <span style="display:block; font-size:0.75rem; color:#64748B; font-weight:600; text-transform:uppercase;">{badge_lbl}</span>
                </div>
            </div>
            <p style="font-size:0.88rem; color:#334155; line-height:1.5; margin-bottom:12px;">
                💡 <b>Analysis:</b> {rec['explanation']}
            </p>
        """, unsafe_allow_html=True)
        
        # Skills columns inside card
        c_m, c_g, c_meta = st.columns([1.5, 1.5, 1])
        with c_m:
            st.markdown("<b style='font-size:0.82rem; color:#065F46;'>Matching Competencies:</b>", unsafe_allow_html=True)
            render_skill_badges(rec["matching_skills"][:6], badge_type="matched")
            if len(rec["matching_skills"]) > 6:
                st.caption(f"+{len(rec['matching_skills']) - 6} more")
        with c_g:
            st.markdown("<b style='font-size:0.82rem; color:#991B1B;'>Missing to Acquire:</b>", unsafe_allow_html=True)
            render_skill_badges(rec["missing_skills"][:5], badge_type="missing")
        with c_meta:
            st.markdown(f"""
            <div style="font-size:0.8rem; color:#64748B; line-height:1.6; border-left:1px solid #E2E8F0; padding-left:12px;">
                <b>Salary:</b> {rec['salary_range']}<br/>
                <b>Growth:</b> {rec['growth_outlook']}
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🎯 Target this role", key=f"target_btn_{rec['role_id']}", use_container_width=True):
                st.session_state.last_target_role = rec['job_title']
                st.success(f"Selected {rec['job_title']} as primary target!")
                st.switch_page("pages/2_🎯_Job_Matching.py")

        st.markdown("</div>", unsafe_allow_html=True)

# Navigation
st.markdown("<br/>", unsafe_allow_html=True)
c_nav1, c_nav2 = st.columns([1.5, 3.5])
with c_nav1:
    if st.button("➡️ Generate Personalized Learning Roadmap", type="primary", use_container_width=True):
        st.switch_page("pages/5_🗺️_Learning_Roadmap.py")

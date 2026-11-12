"""
Report Generator Module for SkillMatch AI
Generates an executive-grade, multi-page PDF career compatibility report using ReportLab.
"""
import io
import datetime
from typing import Optional, List, Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw total page numbers and running header/footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "SkillMatch AI — Career Compatibility Analysis Report")
            self.drawRightString(558, 755, "Confidential Candidate Assessment")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        
        gen_date = datetime.datetime.now().strftime("%B %d, %Y")
        self.drawString(54, 32, f"SkillMatch AI Analysis • Generated on {gen_date}")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()

    def _init_custom_styles(self):
        # Color palette: Royal Purple #4F46E5, Deep Indigo #3730A3, Slate Dark #1E293B
        self.styles.add(ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#3730A3'),
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            'ReportSubtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        ))
        self.styles.add(ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=12,
            spaceAfter=8,
            keepWithNext=True
        ))
        self.styles.add(ParagraphStyle(
            'SubSectionHeader',
            parent=self.styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#4F46E5'),
            spaceBefore=6,
            spaceAfter=4,
            keepWithNext=True
        ))
        self.styles.add(ParagraphStyle(
            'BodyRegular',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#334155')
        ))
        self.styles.add(ParagraphStyle(
            'BodyMuted',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#64748B')
        ))
        self.styles.add(ParagraphStyle(
            'ScoreHero',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=28,
            leading=32,
            textColor=colors.HexColor('#4F46E5'),
            alignment=1  # Centered
        ))
        self.styles.add(ParagraphStyle(
            'BadgeSkill',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#1E293B')
        ))

    def generate_pdf(
        self,
        candidate_data: dict,
        match_data: dict,
        target_role: str,
        gap_data: Optional[dict] = None,
        recommendations: Optional[list] = None,
        roadmap: Optional[list] = None
    ) -> io.BytesIO:
        """
        Builds the complete PDF document and returns an in-memory BytesIO stream.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        story = []

        # ----------------------------------------------------
        # 1. HEADER & BRANDING
        # ----------------------------------------------------
        story.append(Paragraph("SkillMatch AI", self.styles['ReportTitle']))
        story.append(Paragraph(
            "Smart Career Compatibility & Skill Gap Analysis Report",
            self.styles['ReportSubtitle']
        ))
        story.append(HRFlowable(
            width="100%", thickness=1.5, color=colors.HexColor("#4F46E5"),
            spaceBefore=0, spaceAfter=14
        ))

        # ----------------------------------------------------
        # 2. CANDIDATE PROFILE SUMMARY
        # ----------------------------------------------------
        story.append(Paragraph("1. Candidate Assessment Overview", self.styles['SectionHeader']))
        
        contact = candidate_data.get("contact_info", {})
        education_list = candidate_data.get("education", [])
        experience = candidate_data.get("experience", {})

        email = contact.get("email") or "Not detected"
        phone = contact.get("phone") or "Not detected"
        exp_years = f"{experience.get('estimated_years', 0)} years" if experience.get('has_experience') else "Entry-level / Fresher"
        seniority = experience.get("seniority_level", "Entry-Level")

        edu_summary = "Not explicitly stated"
        if education_list:
            edu_summary = ", ".join([f"{e.get('degree_type')} ({e.get('estimated_year')})" for e in education_list[:2]])

        cand_table_data = [
            [
                Paragraph("<b>Email:</b>", self.styles['BodyRegular']),
                Paragraph(email, self.styles['BodyRegular']),
                Paragraph("<b>Experience:</b>", self.styles['BodyRegular']),
                Paragraph(f"{exp_years} ({seniority})", self.styles['BodyRegular'])
            ],
            [
                Paragraph("<b>Phone:</b>", self.styles['BodyRegular']),
                Paragraph(phone, self.styles['BodyRegular']),
                Paragraph("<b>Education:</b>", self.styles['BodyRegular']),
                Paragraph(edu_summary, self.styles['BodyRegular'])
            ]
        ]
        
        cand_table = Table(cand_table_data, colWidths=[65, 185, 80, 174])
        cand_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(cand_table)
        story.append(Spacer(1, 14))

        # ----------------------------------------------------
        # 3. TARGET ROLE COMPATIBILITY SCORE CARD
        # ----------------------------------------------------
        story.append(Paragraph(f"2. Compatibility Analysis for: <b>{target_role}</b>", self.styles['SectionHeader']))
        
        overall_score = match_data.get("overall_compatibility_score", 0.0)
        coverage_pct = match_data.get("coverage_percentage", 0.0)
        breakdown = match_data.get("breakdown", {})
        tech_score = breakdown.get("technical_score", 0.0)
        tfidf_score = breakdown.get("tfidf_similarity_score", 0.0)
        soft_score = breakdown.get("soft_score", 0.0)

        # Rating tier badge
        if overall_score >= 80:
            rating_text = "EXCELLENT MATCH"
            badge_color = colors.HexColor("#10B981")
        elif overall_score >= 60:
            rating_text = "COMPETITIVE MATCH"
            badge_color = colors.HexColor("#3B82F6")
        elif overall_score >= 40:
            rating_text = "POTENTIAL WITH UPSKILLING"
            badge_color = colors.HexColor("#F59E0B")
        else:
            rating_text = "EMERGING CANDIDATE"
            badge_color = colors.HexColor("#EF4444")

        score_card_data = [
            [
                Paragraph(f"<b>Overall Compatibility</b><br/><font size='24'><b>{overall_score}%</b></font><br/><font color='{badge_color}'><b>{rating_text}</b></font>", self.styles['BodyRegular']),
                Paragraph(
                    f"<b>Component Breakdown:</b><br/>"
                    f"• Technical Skills Overlap: <b>{tech_score}%</b> (Weight: 50%)<br/>"
                    f"• TF-IDF Semantic Similarity: <b>{tfidf_score}%</b> (Weight: 35%)<br/>"
                    f"• Soft Skills Alignment: <b>{soft_score}%</b> (Weight: 15%)<br/>"
                    f"• Required Skills Coverage: <b>{coverage_pct}%</b>",
                    self.styles['BodyRegular']
                )
            ]
        ]
        score_table = Table(score_card_data, colWidths=[200, 304])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#EEF2FF')),
            ('BACKGROUND', (1,0), (1,0), colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#C7D2FE')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 14))

        # ----------------------------------------------------
        # 4. SKILLS OVERVIEW (MATCHED VS MISSING)
        # ----------------------------------------------------
        story.append(Paragraph("3. Skills Audit & Alignment", self.styles['SectionHeader']))

        skills_dict = match_data.get("skills", {})
        matched_tech = skills_dict.get("matched_technical", [])
        missing_tech = skills_dict.get("missing_technical", [])
        matched_soft = skills_dict.get("matched_soft", [])
        missing_soft = skills_dict.get("missing_soft", [])
        extra_skills = skills_dict.get("additional_skills", [])

        matched_str = ", ".join(matched_tech + matched_soft) if (matched_tech or matched_soft) else "None detected"
        missing_str = ", ".join(missing_tech + missing_soft) if (missing_tech or missing_soft) else "None — complete match!"
        extra_str = ", ".join(extra_skills[:12]) if extra_skills else "None"

        skills_audit_data = [
            [
                Paragraph("<b>Matching Skills (Possessed):</b>", self.styles['BodyRegular']),
                Paragraph(f"<font color='#059669'><b>{matched_str}</b></font>", self.styles['BodyRegular'])
            ],
            [
                Paragraph("<b>Missing Skills (To Acquire):</b>", self.styles['BodyRegular']),
                Paragraph(f"<font color='#DC2626'><b>{missing_str}</b></font>", self.styles['BodyRegular'])
            ],
            [
                Paragraph("<b>Additional Skills in Resume:</b>", self.styles['BodyRegular']),
                Paragraph(extra_str, self.styles['BodyRegular'])
            ]
        ]
        audit_table = Table(skills_audit_data, colWidths=[150, 354])
        audit_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(audit_table)
        story.append(Spacer(1, 16))

        # ----------------------------------------------------
        # 5. CAREER RECOMMENDATIONS TABLE
        # ----------------------------------------------------
        if recommendations:
            story.append(Paragraph("4. Alternative & Adjacent Career Recommendations", self.styles['SectionHeader']))
            story.append(Paragraph(
                "Ranked career recommendations derived from candidate skill taxonomy and supervised role categorization:",
                self.styles['BodyMuted']
            ))
            story.append(Spacer(1, 6))

            rec_table_data = [
                [
                    Paragraph("<b>Rank</b>", self.styles['SubSectionHeader']),
                    Paragraph("<b>Role Title</b>", self.styles['SubSectionHeader']),
                    Paragraph("<b>Category</b>", self.styles['SubSectionHeader']),
                    Paragraph("<b>Match Score</b>", self.styles['SubSectionHeader']),
                    Paragraph("<b>Key Missing Skills</b>", self.styles['SubSectionHeader'])
                ]
            ]
            for idx, rec in enumerate(recommendations[:5], 1):
                missing_preview = ", ".join(rec.get("missing_technical", [])[:2]) or "None"
                rec_table_data.append([
                    Paragraph(f"#{idx}", self.styles['BodyRegular']),
                    Paragraph(f"<b>{rec['job_title']}</b>", self.styles['BodyRegular']),
                    Paragraph(rec['category'], self.styles['BodyRegular']),
                    Paragraph(f"<b>{rec['compatibility_score']}%</b>", self.styles['BodyRegular']),
                    Paragraph(missing_preview, self.styles['BodyRegular'])
                ])
            
            rec_table = Table(rec_table_data, colWidths=[40, 140, 110, 80, 134])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 5),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(rec_table)
            story.append(Spacer(1, 16))

        # ----------------------------------------------------
        # 6. ACTIONABLE LEARNING ROADMAP
        # ----------------------------------------------------
        if roadmap:
            story.append(KeepTogether([
                Paragraph("5. Phased Skill Improvement Roadmap", self.styles['SectionHeader']),
                Paragraph(
                    "Sequenced upskilling path targeting priority missing competencies:",
                    self.styles['BodyMuted']
                ),
                Spacer(1, 6)
            ]))
            
            for item in roadmap[:3]:
                skill = item["skill"]
                importance = item["importance"]
                timeframe = item["timeframe"]
                stages = item.get("stages", {})
                
                beg_topics = stages.get("Beginner", {}).get("topics", "Core concepts")
                beg_res = stages.get("Beginner", {}).get("resources", [{}])[0].get("title", "Online tutorial")
                
                road_card_data = [
                    [
                        Paragraph(f"<b>Step {item['step_number']}: {skill}</b> ({importance})<br/><font color='#64748B'>{timeframe}</font>", self.styles['BodyRegular']),
                        Paragraph(
                            f"• <b>Beginner:</b> {beg_topics}<br/>"
                            f"• <b>Recommended:</b> {beg_res}<br/>"
                            f"• <b>Intermediate:</b> {stages.get('Intermediate', {}).get('topics', 'Applied exercises')}",
                            self.styles['BodyRegular']
                        )
                    ]
                ]
                r_table = Table(road_card_data, colWidths=[150, 354])
                r_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('PADDING', (0,0), (-1,-1), 6),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                story.append(r_table)
                story.append(Spacer(1, 6))

        # ----------------------------------------------------
        # 7. METHODOLOGY & DISCLAIMER
        # ----------------------------------------------------
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Methodology & Transparency Notice:</b>", self.styles['SubSectionHeader']))
        story.append(Paragraph(
            "This report applies Natural Language Processing (TF-IDF vectorization, Cosine Similarity) and "
            "domain-specific skill taxonomy extraction. Compatibility scores represent semantic and keyword alignment with "
            "the provided role requirements. <b>This score is an informational readiness metric, not a hiring guarantee or statistical probability.</b>",
            self.styles['BodyMuted']
        ))

        # Build PDF
        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer

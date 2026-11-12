"""
Resume Parser Module for SkillMatch AI
Extracts text, contact details, education, experience, and structured sections from PDF resumes.
"""
import re
import io
from typing import Union, BinaryIO, Optional
import fitz  # PyMuPDF
from modules.text_preprocessing import TextPreprocessor

class ResumeParser:
    def __init__(self):
        self.preprocessor = TextPreprocessor()

    def extract_text_from_pdf(self, pdf_source: Union[str, bytes, BinaryIO]) -> dict:
        """
        Extracts raw text and metadata from a PDF file or bytes buffer using PyMuPDF.
        Returns a dict with success flag, extracted text, page count, and potential errors.
        """
        result = {
            "success": False,
            "text": "",
            "page_count": 0,
            "error": None,
            "warning": None
        }
        
        try:
            doc = None
            if isinstance(pdf_source, str):
                doc = fitz.open(pdf_source)
            elif isinstance(pdf_source, (bytes, bytearray)):
                doc = fitz.open(stream=pdf_source, filetype="pdf")
            elif hasattr(pdf_source, "read"):
                content = pdf_source.read()
                # Reset pointer if possible
                if hasattr(pdf_source, "seek"):
                    pdf_source.seek(0)
                doc = fitz.open(stream=content, filetype="pdf")
            else:
                result["error"] = "Unsupported PDF source format."
                return result

            if doc.is_encrypted:
                result["error"] = "The uploaded PDF is password protected. Please provide an unencrypted PDF."
                return result

            result["page_count"] = len(doc)
            if result["page_count"] == 0:
                result["error"] = "The PDF contains no pages."
                return result

            extracted_pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text("text")
                if page_text:
                    extracted_pages.append(page_text)

            full_text = "\n\n".join(extracted_pages).strip()
            
            if not full_text or len(full_text.strip()) < 20:
                result["error"] = (
                    "Could not extract readable text from this PDF. "
                    "It might be a scanned image or empty. "
                    "Please upload a standard text-based PDF resume."
                )
                return result

            result["success"] = True
            result["text"] = full_text
            
            if len(full_text.split()) < 30:
                result["warning"] = "The resume text is very brief. Extraction results may be limited."

        except Exception as e:
            result["error"] = f"Failed to parse PDF: {str(e)}"
        finally:
            if doc:
                doc.close()

        return result

    def extract_contact_info(self, text: str) -> dict:
        """
        Extracts email, phone number, LinkedIn, GitHub, and personal portfolio links.
        """
        contacts = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "links": []
        }
        
        # Email pattern
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_pattern, text)
        if emails:
            contacts["email"] = emails[0].lower()

        # Phone pattern (handles international formats, dashes, dots, spaces)
        phone_pattern = r'(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contacts["phone"] = phones[0].strip()

        # LinkedIn pattern
        linkedin_pattern = r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            contacts["linkedin"] = linkedin_matches[0]

        # GitHub pattern
        github_pattern = r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            contacts["github"] = github_matches[0]

        # General links
        general_url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        all_links = re.findall(general_url_pattern, text)
        contacts["links"] = list(set(all_links))

        return contacts

    def extract_education(self, text: str) -> list[dict]:
        """
        Extracts academic degrees, institutions, and graduation years.
        """
        degrees_found = []
        
        degree_patterns = [
            (r"\b(Ph\.?D|Doctor of Philosophy)\b", "Doctorate (Ph.D.)"),
            (r"\b(M\.?S|M\.?Tech|Master of Science|Master of Technology|MCA|MBA|Master'?s)\b", "Master's Degree"),
            (r"\b(B\.?S|B\.?Tech|B\.?E|Bachelor of Science|Bachelor of Technology|Bachelor of Engineering|BCA|BBA|Bachelor'?s)\b", "Bachelor's Degree"),
            (r"\b(Diploma|Associate Degree|Associate of Science|Associate of Arts)\b", "Diploma / Associate")
        ]
        
        lines = text.split('\n')
        year_pattern = r'\b(19\d{2}|20[0-2]\d)\b'
        
        for i, line in enumerate(lines):
            for pattern, deg_name in degree_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Look nearby for years and university/college names
                    context_window = " ".join(lines[max(0, i-1):min(len(lines), i+3)])
                    years = re.findall(year_pattern, context_window)
                    year_str = " - ".join(years[:2]) if years else "Not specified"
                    
                    degrees_found.append({
                        "degree_type": deg_name,
                        "raw_mention": line.strip(),
                        "estimated_year": year_str
                    })
                    break  # One degree classification per matched line
                    
        # Deduplicate by degree_type
        seen_types = set()
        deduped = []
        for deg in degrees_found:
            if deg["degree_type"] not in seen_types:
                seen_types.add(deg["degree_type"])
                deduped.append(deg)
                
        return deduped

    def extract_experience_summary(self, text: str) -> dict:
        """
        Estimates total work experience and identifies career progression markers.
        """
        experience_info = {
            "estimated_years": 0.0,
            "has_experience": False,
            "seniority_level": "Fresher / Entry-Level",
            "experience_snippets": []
        }
        
        # Regex for explicit mentions like "X years of experience"
        years_exp_pattern = r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s*of)?\s*(?:experience|exp)'
        matches = re.findall(years_exp_pattern, text, re.IGNORECASE)
        if matches:
            try:
                exp_vals = [float(m) for m in matches if float(m) <= 40]
                if exp_vals:
                    experience_info["estimated_years"] = max(exp_vals)
                    experience_info["has_experience"] = True
            except ValueError:
                pass

        # Identify seniority keywords
        lower_text = text.lower()
        if experience_info["estimated_years"] >= 5 or "senior" in lower_text or "lead" in lower_text or "principal" in lower_text:
            experience_info["seniority_level"] = "Senior-Level"
        elif experience_info["estimated_years"] >= 2 or "mid-level" in lower_text or "intermediate" in lower_text:
            experience_info["seniority_level"] = "Mid-Level"
        elif experience_info["estimated_years"] > 0:
            experience_info["seniority_level"] = "Junior-Level"
        else:
            experience_info["seniority_level"] = "Fresher / Entry-Level"

        # Extract lines mentioning work titles or dates
        title_keywords = [
            "engineer", "developer", "analyst", "scientist", "intern",
            "specialist", "consultant", "architect", "manager", "administrator"
        ]
        snippets = []
        for line in text.split('\n'):
            line_str = line.strip()
            if 15 <= len(line_str) <= 120 and any(kw in line_str.lower() for kw in title_keywords):
                snippets.append(line_str)
                if len(snippets) >= 4:
                    break
        experience_info["experience_snippets"] = snippets

        return experience_info

    def parse(self, pdf_source: Union[str, bytes, BinaryIO]) -> dict:
        """
        Full parse pipeline: reads PDF, extracts text, cleans text,
        extracts contact info, education, experience, and segments into sections.
        """
        extraction_res = self.extract_text_from_pdf(pdf_source)
        if not extraction_res["success"]:
            return extraction_res
            
        raw_text = extraction_res["text"]
        cleaned_text = self.preprocessor.clean_text(raw_text)
        normalized_text = self.preprocessor.get_normalized_string(raw_text)
        sections = self.preprocessor.extract_sections(raw_text)
        contact_info = self.extract_contact_info(raw_text)
        education = self.extract_education(raw_text)
        experience = self.extract_experience_summary(raw_text)
        
        return {
            "success": True,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "normalized_text": normalized_text,
            "page_count": extraction_res["page_count"],
            "warning": extraction_res.get("warning"),
            "contact_info": contact_info,
            "education": education,
            "experience": experience,
            "sections": sections
        }


"""
Text Preprocessing Module for SkillMatch AI
Handles cleaning, tokenization, lemmatization, and section extraction for resumes and job descriptions.
"""
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Ensure NLTK resources are available
try:
    _ = stopwords.words('english')
except LookupError:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)

class TextPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        
        # Base English stopwords
        base_stops = set(stopwords.words('english'))
        
        # Tech tokens that must NEVER be removed as stopwords
        self.tech_whitelist = {
            'c', 'r', 'go', 'ai', 'ml', 'dl', 'nlp', 'cv', 'bi', 'db', 'os', 'it', 'ui', 'ux',
            'net', 'git', 'sql', 'aws', 'gcp', 'qa', 'ci', 'cd'
        }
        self.stop_words = base_stops - self.tech_whitelist

    def clean_text(self, text: str) -> str:
        """
        Cleans raw text while preserving technology tokens like C++, C#, .NET, CI/CD, Node.js.
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Replace non-breaking spaces and line break variants
        text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
        
        # Preserve specific patterns before general punctuation stripping
        # Protect C++, C#, .NET, CI/CD
        text = re.sub(r'\bC\+\+\b', 'cpp_token', text, flags=re.IGNORECASE)
        text = re.sub(r'\bC\#\b', 'csharp_token', text, flags=re.IGNORECASE)
        text = re.sub(r'\.NET\b', 'dotnet_token', text, flags=re.IGNORECASE)
        text = re.sub(r'\bCI/CD\b', 'cicd_token', text, flags=re.IGNORECASE)
        text = re.sub(r'\bNode\.js\b', 'nodejs_token', text, flags=re.IGNORECASE)
        text = re.sub(r'\bVue\.js\b', 'vuejs_token', text, flags=re.IGNORECASE)
        
        # Remove URLs and email addresses from general text (we extract them separately)
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        text = re.sub(r'\S+@\S+\.\S+', ' ', text)
        
        # Remove excessive punctuation but keep alphanumerics, hyphens, and spaces
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Restore protected tokens
        text = text.replace('cpp_token', 'C++')
        text = text.replace('csharp_token', 'C#')
        text = text.replace('dotnet_token', '.NET')
        text = text.replace('cicd_token', 'CI/CD')
        text = text.replace('nodejs_token', 'Node.js')
        text = text.replace('vuejs_token', 'Vue.js')
        
        # Collapse multiple whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def tokenize_and_lemmatize(self, text: str) -> list[str]:
        """
        Tokenizes and lemmatizes text, filtering out standard non-tech stopwords.
        """
        cleaned = self.clean_text(text)
        tokens = cleaned.split()
        
        processed_tokens = []
        for token in tokens:
            lower_token = token.lower()
            if lower_token not in self.stop_words and len(lower_token) > 1:
                # Lemmatize
                lemmatized = self.lemmatizer.lemmatize(lower_token)
                processed_tokens.append(lemmatized)
            elif lower_token in self.tech_whitelist:
                processed_tokens.append(token)
                
        return processed_tokens

    def get_normalized_string(self, text: str) -> str:
        """
        Returns a normalized, space-separated string of processed tokens.
        """
        tokens = self.tokenize_and_lemmatize(text)
        return " ".join(tokens)

    def extract_sections(self, raw_text: str) -> dict[str, str]:
        """
        Segments a resume into major standard sections (Summary, Experience, Education, Skills, Projects).
        """
        sections = {
            "summary": "",
            "experience": "",
            "education": "",
            "skills": "",
            "projects": "",
            "other": ""
        }
        
        if not raw_text:
            return sections
            
        header_patterns = {
            "summary": r'(summary|professional summary|objective|profile|about me)',
            "experience": r'(work experience|experience|employment history|work history|professional experience)',
            "education": r'(education|academic background|qualifications|academic history)',
            "skills": r'(skills|technical skills|core competencies|technologies|expertise)',
            "projects": r'(projects|personal projects|academic projects|key projects)'
        }
        
        lines = raw_text.split('\n')
        current_section = "other"
        section_lines = {sec: [] for sec in sections}
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
                
            matched_header = False
            # Check if this line looks like a section header (short, title-like)
            if len(stripped.split()) <= 4:
                cleaned_line = re.sub(r'[^a-zA-Z\s]', '', stripped).strip().lower()
                for sec, pattern in header_patterns.items():
                    if re.fullmatch(pattern, cleaned_line):
                        current_section = sec
                        matched_header = True
                        break
            
            if not matched_header:
                section_lines[current_section].append(stripped)
                
        for sec in sections:
            sections[sec] = "\n".join(section_lines[sec])
            
        return sections


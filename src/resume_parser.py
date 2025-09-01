"""
Resume Parser Module for PMIS-AI Engine
Handles text extraction from various file formats and skill parsing using NLP
"""

import PyPDF2
import docx
import re
import os
from typing import List, Dict, Set

class ResumeParser:
    def __init__(self):
        # Comprehensive skills database for matching
        self.SKILLS_DB = [
            # Programming Languages
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift',
            'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'typescript',
            
            # Web Development
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
            'laravel', 'bootstrap', 'jquery', 'webpack', 'npm', 'yarn',
            
            # Data Science & AI
            'machine learning', 'deep learning', 'artificial intelligence', 'data science',
            'data analysis', 'statistics', 'pandas', 'numpy', 'scikit-learn', 'tensorflow',
            'pytorch', 'keras', 'opencv', 'nlp', 'computer vision', 'neural networks',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra',
            'elasticsearch', 'neo4j', 'firebase',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
            'gitlab', 'ci/cd', 'terraform', 'ansible', 'linux', 'bash',
            
            # Finance & Business
            'financial modeling', 'risk assessment', 'portfolio management', 'investment banking',
            'corporate finance', 'market research', 'bloomberg terminal', 'excel', 'vba',
            'tableau', 'power bi', 'spss', 'econometrics', 'cfa', 'frm',
            
            # Environmental & Energy
            'environmental analysis', 'sustainability', 'renewable energy', 'solar energy',
            'wind energy', 'gis', 'arcgis', 'qgis', 'remote sensing', 'environmental modeling',
            'air quality monitoring', 'water treatment', 'energy auditing',
            
            # Project Management
            'project management', 'agile', 'scrum', 'kanban', 'waterfall', 'pmp', 'jira',
            'confluence', 'trello', 'asana', 'slack', 'microsoft project',
            
            # Marketing & Analytics
            'digital marketing', 'seo', 'sem', 'social media marketing', 'content marketing',
            'google analytics', 'facebook ads', 'google ads', 'email marketing', 'crm',
            
            # Healthcare & Biotech
            'healthcare analytics', 'medical research', 'clinical trials', 'biostatistics',
            'epidemiology', 'public health', 'medical imaging', 'bioinformatics'
        ]
        
        # Education keywords for parsing
        self.EDUCATION_KEYWORDS = [
            'b.tech', 'btech', 'b.e.', 'be', 'bachelor', 'b.sc', 'bsc', 'b.com', 'bcom',
            'm.tech', 'mtech', 'm.e.', 'me', 'master', 'm.sc', 'msc', 'm.com', 'mcom',
            'mba', 'phd', 'doctorate', 'diploma', 'certification', 'degree'
        ]

    def read_resume_text(self, file_path: str) -> str:
        """
        Extract text from resume files (PDF, DOCX, TXT)
        
        Args:
            file_path (str): Path to the resume file
            
        Returns:
            str: Extracted text content
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            text = ""
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                text = self._read_pdf(file_path)
            elif file_extension == 'docx':
                text = self._read_docx(file_path)
            elif file_extension == 'txt':
                text = self._read_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
            return text.strip()
            
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return ""

    def _read_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {str(e)}")
        return text

    def _read_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {str(e)}")
        return text

    def _read_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading TXT {file_path}: {str(e)}")
            return ""

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume text using keyword matching
        
        Args:
            text (str): Resume text content
            
        Returns:
            List[str]: List of identified skills
        """
        found_skills = set()
        text_lower = text.lower()
        
        for skill in self.SKILLS_DB:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return list(found_skills)

    def extract_education(self, text: str) -> List[str]:
        """
        Extract education information from resume text
        
        Args:
            text (str): Resume text content
            
        Returns:
            List[str]: List of identified education qualifications
        """
        found_education = set()
        text_lower = text.lower()
        
        for edu in self.EDUCATION_KEYWORDS:
            pattern = r'\b' + re.escape(edu.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_education.add(edu)
        
        return list(found_education)

    def extract_experience_years(self, text: str) -> int:
        """
        Extract years of experience from resume text
        
        Args:
            text (str): Resume text content
            
        Returns:
            int: Estimated years of experience
        """
        # Look for patterns like "2 years", "3+ years", "5-7 years"
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)-\d+\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'experience\s*:?\s*(\d+)\+?\s*years?'
        ]
        
        text_lower = text.lower()
        max_years = 0
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years = int(match)
                    max_years = max(max_years, years)
                except ValueError:
                    continue
        
        return max_years

    def parse_resume(self, file_path: str) -> Dict:
        """
        Complete resume parsing pipeline
        
        Args:
            file_path (str): Path to resume file
            
        Returns:
            Dict: Parsed resume data including text, skills, education, experience
        """
        try:
            # Extract text
            text = self.read_resume_text(file_path)
            
            if not text:
                return {
                    "file_path": file_path,
                    "text": "",
                    "skills": [],
                    "education": [],
                    "experience_years": 0,
                    "parsing_success": False,
                    "error": "Failed to extract text from file"
                }
            
            # Extract structured information
            skills = self.extract_skills(text)
            education = self.extract_education(text)
            experience_years = self.extract_experience_years(text)
            
            return {
                "file_path": file_path,
                "text": text,
                "skills": skills,
                "education": education,
                "experience_years": experience_years,
                "parsing_success": True,
                "error": None
            }
            
        except Exception as e:
            return {
                "file_path": file_path,
                "text": "",
                "skills": [],
                "education": [],
                "experience_years": 0,
                "parsing_success": False,
                "error": str(e)
            }


# Test function
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Test with sample resume
    test_file = "data/candidate1.txt"
    if os.path.exists(test_file):
        result = parser.parse_resume(test_file)
        print("=== Resume Parsing Test ===")
        print(f"File: {result['file_path']}")
        print(f"Success: {result['parsing_success']}")
        print(f"Skills Found: {result['skills']}")
        print(f"Education: {result['education']}")
        print(f"Experience: {result['experience_years']} years")
        if result['error']:
            print(f"Error: {result['error']}")
    else:
        print(f"Test file {test_file} not found")

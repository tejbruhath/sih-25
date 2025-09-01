"""
Resume Parser Module for PMIS-AI Engine
=========================================

This module handles the ingestion and parsing of resume files to extract
structured information including skills, experience, and education details.

Author: PMIS-AI Team
Created: 2025-01-01
Last Modified: 2025-01-01
"""

import PyPDF2
import docx
import re
import os
from typing import Dict, List, Set
import nltk
from collections import Counter

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class ResumeParser:
    """
    A comprehensive resume parser that extracts structured information
    from resume files in various formats (PDF, TXT, DOCX).
    """
    
    def __init__(self):
        # Comprehensive skills database categorized by domain
        self.SKILLS_DB = {
            'programming': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css'
            ],
            'web_development': [
                'react', 'angular', 'vue.js', 'node.js', 'express.js', 'django', 'flask',
                'spring boot', 'asp.net', 'laravel', 'bootstrap', 'jquery', 'webpack'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'data analysis', 'data science',
                'artificial intelligence', 'natural language processing', 'computer vision',
                'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'tensorflow',
                'pytorch', 'keras', 'tableau', 'power bi', 'excel', 'spss', 'sas'
            ],
            'cloud_devops': [
                'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins',
                'terraform', 'ansible', 'git', 'gitlab', 'github', 'ci/cd'
            ],
            'mobile_development': [
                'android', 'ios', 'react native', 'flutter', 'ionic', 'xamarin'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'oracle', 'redis', 'cassandra',
                'elasticsearch', 'firebase'
            ],
            'business': [
                'project management', 'business analysis', 'product management',
                'digital marketing', 'seo', 'social media marketing', 'content marketing',
                'market research', 'financial analysis', 'accounting'
            ]
        }
        
        # Flatten skills for easy searching
        self.all_skills = []
        for category, skills in self.SKILLS_DB.items():
            self.all_skills.extend(skills)
        
        # Stop words for text cleaning
        self.stop_words = set(stopwords.words('english'))
    
    def read_resume_text(self, file_path: str) -> str:
        """
        Extract text content from resume files of various formats.
        
        Args:
            file_path (str): Path to the resume file
            
        Returns:
            str: Extracted text content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        text = ""
        file_extension = file_path.lower().split('.')[-1]
        
        try:
            if file_extension == "pdf":
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                        
            elif file_extension == "txt":
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    
            elif file_extension == "docx":
                doc = docx.Document(file_path)
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                    
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return ""
        
        return text.strip()
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills from resume text using keyword matching.
        
        Args:
            text (str): Resume text content
            
        Returns:
            Dict[str, List[str]]: Dictionary with skill categories and found skills
        """
        text_lower = text.lower()
        found_skills = {category: [] for category in self.SKILLS_DB.keys()}
        
        for category, skills in self.SKILLS_DB.items():
            for skill in skills:
                # Use word boundary regex to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)
        
        # Remove empty categories
        found_skills = {k: v for k, v in found_skills.items() if v}
        
        return found_skills
    
    def extract_education(self, text: str) -> Dict[str, str]:
        """
        Extract education information from resume text.
        
        Args:
            text (str): Resume text content
            
        Returns:
            Dict[str, str]: Education details including degree and institution
        """
        education_info = {
            'degree': '',
            'institution': '',
            'year': '',
            'cgpa': ''
        }
        
        # Common degree patterns
        degree_patterns = [
            r'bachelor.*?(?:of|in)\s+(.*?)(?:\n|,|from)',
            r'b\.?tech.*?(?:in|of)\s+(.*?)(?:\n|,|from)',
            r'b\.?e\.?.*?(?:in|of)\s+(.*?)(?:\n|,|from)',
            r'master.*?(?:of|in)\s+(.*?)(?:\n|,|from)',
            r'm\.?tech.*?(?:in|of)\s+(.*?)(?:\n|,|from)'
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, text.lower())
            if match:
                education_info['degree'] = match.group(1).strip()
                break
        
        # Extract CGPA
        cgpa_pattern = r'cgpa[:\s]*(\d+\.?\d*)[/\s]*(?:10|4)'
        cgpa_match = re.search(cgpa_pattern, text.lower())
        if cgpa_match:
            education_info['cgpa'] = cgpa_match.group(1)
        
        return education_info
    
    def extract_experience_keywords(self, text: str) -> List[str]:
        """
        Extract experience-related keywords and phrases.
        
        Args:
            text (str): Resume text content
            
        Returns:
            List[str]: List of experience keywords
        """
        experience_keywords = [
            'intern', 'internship', 'project', 'developed', 'built', 'implemented',
            'designed', 'created', 'managed', 'led', 'collaborated', 'optimized',
            'achieved', 'improved', 'analyzed', 'research', 'published', 'certified'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in experience_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def calculate_skill_score(self, skills_dict: Dict[str, List[str]]) -> float:
        """
        Calculate a composite skill score based on number and diversity of skills.
        
        Args:
            skills_dict (Dict[str, List[str]]): Categorized skills dictionary
            
        Returns:
            float: Skill score between 0 and 1
        """
        total_skills = sum(len(skills) for skills in skills_dict.values())
        category_diversity = len(skills_dict.keys())
        
        # Weight: 70% for total skills, 30% for diversity
        skill_score = (total_skills * 0.7 + category_diversity * 0.3) / 20
        return min(skill_score, 1.0)  # Cap at 1.0
    
    def parse_resume(self, file_path: str) -> Dict:
        """
        Complete resume parsing pipeline that extracts all relevant information.
        
        Args:
            file_path (str): Path to the resume file
            
        Returns:
            Dict: Structured resume data including text, skills, education, and scores
        """
        try:
            # Extract raw text
            text = self.read_resume_text(file_path)
            if not text:
                return {"error": "Could not extract text from resume"}
            
            # Extract structured information
            skills = self.extract_skills(text)
            education = self.extract_education(text)
            experience_keywords = self.extract_experience_keywords(text)
            skill_score = self.calculate_skill_score(skills)
            
            # Count total words for text complexity measure
            word_count = len(word_tokenize(text))
            
            return {
                "raw_text": text,
                "skills": skills,
                "education": education,
                "experience_keywords": experience_keywords,
                "skill_score": skill_score,
                "word_count": word_count,
                "total_skills": sum(len(skills_list) for skills_list in skills.values()),
                "skill_categories": len(skills.keys())
            }
            
        except Exception as e:
            return {"error": f"Error parsing resume: {str(e)}"}

# Test function for development
def test_parser():
    """Test the resume parser with sample data."""
    parser = ResumeParser()
    
    # Test with our mock resumes
    test_files = [
        "data/candidate1.txt",
        "data/candidate2.txt", 
        "data/candidate3.txt",
        "data/candidate4.txt"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n=== Parsing {file_path} ===")
            result = parser.parse_resume(file_path)
            
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Total Skills Found: {result['total_skills']}")
                print(f"Skill Categories: {result['skill_categories']}")
                print(f"Skill Score: {result['skill_score']:.2f}")
                print(f"Skills by Category:")
                for category, skills in result['skills'].items():
                    print(f"  {category}: {', '.join(skills)}")

if __name__ == "__main__":
    test_parser()

import PyPDF2
import os
import re
from typing import List, Dict, Any

class ResumeParser:
    def __init__(self):
        # Predefined list of common skills
        self.skills_list = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
            'machine learning', 'ai', 'data analysis', 'statistics', 'algorithms',
            'system design', 'database', 'web development', 'computer vision',
            'html', 'css', 'git', 'docker', 'kubernetes', 'aws', 'azure',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib'
        ]
    
    def read_text_from_file(self, file_path: str) -> str:
        """
        Read text content from different file types (.pdf, .txt)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._read_pdf(file_path)
        elif file_extension == '.txt':
            return self._read_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _read_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}")
    
    def _read_txt(self, file_path: str) -> str:
        """
        Read text from TXT file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text using predefined skill list
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_list:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Parse resume file and extract structured information
        """
        text = self.read_text_from_file(file_path)
        skills = self.extract_skills(text)
        
        # Extract basic information using regex patterns
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        education = self._extract_education(text)
        
        return {
            'text': text,
            'skills': skills,
            'email': email,
            'phone': phone,
            'education': education
        }
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group() if match else ""
    
    def _extract_education(self, text: str) -> str:
        """Extract education information from text"""
        # Simple extraction - look for common university names
        universities = ['MIT', 'Stanford', 'Harvard', 'UC Berkeley', 'CMU', 'University']
        for uni in universities:
            if uni in text:
                return uni
        return ""

# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Test with sample resume
    try:
        result = parser.parse_resume("data/candidate1.txt")
        print("Parsed Resume:")
        print(f"Skills: {result['skills']}")
        print(f"Email: {result['email']}")
        print(f"Phone: {result['phone']}")
        print(f"Education: {result['education']}")
    except Exception as e:
        print(f"Error: {e}")

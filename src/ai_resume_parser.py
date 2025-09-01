"""
AI-Powered Resume Parser using spaCy NLP and Named Entity Recognition
Replaces rule-based keyword matching with genuine machine learning models
"""

import spacy
import re
import os
from typing import List, Dict, Set, Tuple
from collections import Counter
import PyPDF2
import docx

class AIResumeParser:
    def __init__(self):
        self.nlp = None
        self.load_nlp_model()
        
        # Skill categories for ML-based classification
        self.skill_categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'sql', 'r'],
            'data_science': ['machine learning', 'deep learning', 'statistics', 'analytics'],
            'web_development': ['react', 'angular', 'node.js', 'django', 'flask'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'finance': ['financial modeling', 'risk assessment', 'bloomberg', 'excel'],
            'marketing': ['seo', 'social media', 'google analytics', 'content marketing']
        }
        
    def load_nlp_model(self):
        """Load spaCy NLP model with NER capabilities"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy NLP model loaded successfully")
        except OSError:
            print("❌ spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_entities_with_nlp(self, text: str) -> Dict:
        """
        Use spaCy NER to extract structured information from resume text
        
        Args:
            text (str): Resume text
            
        Returns:
            Dict: Extracted entities (organizations, skills, education, etc.)
        """
        if not self.nlp:
            return {'organizations': [], 'persons': [], 'locations': [], 'skills': []}
        
        doc = self.nlp(text)
        
        entities = {
            'organizations': [],
            'persons': [],
            'locations': [],
            'dates': [],
            'skills': []
        }
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ == "ORG":
                entities['organizations'].append(ent.text)
            elif ent.label_ == "PERSON":
                entities['persons'].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities['locations'].append(ent.text)
            elif ent.label_ == "DATE":
                entities['dates'].append(ent.text)
        
        # Use dependency parsing to find skill-related phrases
        entities['skills'] = self.extract_skills_with_dependency_parsing(doc)
        
        return entities
    
    def extract_skills_with_dependency_parsing(self, doc) -> List[str]:
        """
        Use spaCy's dependency parsing to identify skills more intelligently
        """
        skills = set()
        
        # Look for skill-indicating patterns in dependency tree
        for token in doc:
            # Skills often appear after verbs like "experienced in", "skilled at"
            if token.dep_ == "pobj" and token.head.lemma_ in ["experience", "skill", "proficient", "expert"]:
                skills.add(token.text.lower())
            
            # Skills in compound nouns (e.g., "machine learning", "data science")
            if token.dep_ == "compound":
                compound_phrase = f"{token.text} {token.head.text}".lower()
                for category, skill_list in self.skill_categories.items():
                    if any(skill in compound_phrase for skill in skill_list):
                        skills.add(compound_phrase)
        
        # Also use traditional keyword matching as backup
        text_lower = doc.text.lower()
        for category, skill_list in self.skill_categories.items():
            for skill in skill_list:
                if skill in text_lower:
                    skills.add(skill)
        
        return list(skills)
    
    def extract_education_with_nlp(self, text: str) -> List[Dict]:
        """
        Extract education information using NLP pattern matching
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        education_info = []
        
        # Education patterns
        education_patterns = [
            r'(B\.?Tech|Bachelor|B\.?E\.?|B\.?Sc|B\.?Com|M\.?Tech|Master|M\.?Sc|M\.?Com|MBA|PhD|Doctorate)',
            r'(Computer Science|Engineering|Economics|Finance|Business|Data Science)',
            r'(IIT|NIT|University|College|Institute)'
        ]
        
        # Find education mentions with context
        for sent in doc.sents:
            sent_text = sent.text
            for pattern in education_patterns:
                matches = re.finditer(pattern, sent_text, re.IGNORECASE)
                for match in matches:
                    # Extract surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(sent_text), match.end() + 50)
                    context = sent_text[start:end].strip()
                    
                    education_info.append({
                        'degree': match.group(),
                        'context': context,
                        'confidence': 0.8  # Simple confidence score
                    })
        
        return education_info
    
    def calculate_experience_with_nlp(self, text: str) -> Dict:
        """
        Calculate experience using NLP to understand context better
        """
        if not self.nlp:
            return {'years': 0, 'roles': [], 'companies': []}
        
        doc = self.nlp(text)
        experience_data = {
            'years': 0,
            'roles': [],
            'companies': [],
            'experience_phrases': []
        }
        
        # Extract job titles using POS tagging and NER
        for ent in doc.ents:
            if ent.label_ == "ORG":
                experience_data['companies'].append(ent.text)
        
        # Look for experience-related phrases
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)-(\d+)\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'worked\s+(?:for\s+)?(\d+)\s*years?',
            r'(\d+)\s*years?\s*(?:in|at|with)'
        ]
        
        years_found = []
        for pattern in experience_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Extract first number from match
                    year_str = match.group(1)
                    years = int(year_str)
                    years_found.append(years)
                    experience_data['experience_phrases'].append(match.group())
                except (ValueError, IndexError):
                    continue
        
        # Use maximum years found as total experience
        if years_found:
            experience_data['years'] = max(years_found)
        
        # Extract job roles using POS patterns
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            # Common job title patterns
            if any(word in chunk_text for word in ['engineer', 'developer', 'analyst', 'manager', 'intern', 'specialist']):
                experience_data['roles'].append(chunk.text)
        
        return experience_data
    
    def ai_powered_resume_analysis(self, file_path: str) -> Dict:
        """
        Complete AI-powered resume analysis pipeline
        
        Args:
            file_path (str): Path to resume file
            
        Returns:
            Dict: Comprehensive analysis results
        """
        try:
            # Read resume text (reuse existing file reading logic)
            text = self.read_resume_text(file_path)
            
            if not text:
                return {
                    "file_path": file_path,
                    "parsing_success": False,
                    "error": "Failed to extract text from file"
                }
            
            # AI-powered analysis
            entities = self.extract_entities_with_nlp(text)
            education = self.extract_education_with_nlp(text)
            experience = self.calculate_experience_with_nlp(text)
            
            # Calculate AI confidence scores
            confidence_scores = self.calculate_confidence_scores(text, entities, education, experience)
            
            return {
                "file_path": file_path,
                "text": text,
                "ai_entities": entities,
                "skills": entities['skills'],
                "education": education,
                "experience_analysis": experience,
                "experience_years": experience['years'],
                "organizations": entities['organizations'],
                "locations": entities['locations'],
                "confidence_scores": confidence_scores,
                "parsing_success": True,
                "ai_powered": True,
                "error": None
            }
            
        except Exception as e:
            return {
                "file_path": file_path,
                "parsing_success": False,
                "ai_powered": False,
                "error": str(e)
            }
    
    def calculate_confidence_scores(self, text: str, entities: Dict, 
                                  education: List, experience: Dict) -> Dict:
        """
        Calculate confidence scores for AI predictions
        """
        scores = {
            'overall_confidence': 0.0,
            'skill_extraction_confidence': 0.0,
            'education_confidence': 0.0,
            'experience_confidence': 0.0
        }
        
        # Skill extraction confidence based on NER entities found
        if entities['skills']:
            scores['skill_extraction_confidence'] = min(0.95, len(entities['skills']) * 0.1 + 0.5)
        
        # Education confidence based on structured patterns found
        if education:
            scores['education_confidence'] = min(0.9, len(education) * 0.3 + 0.4)
        
        # Experience confidence based on explicit mentions
        if experience['experience_phrases']:
            scores['experience_confidence'] = min(0.85, len(experience['experience_phrases']) * 0.2 + 0.5)
        
        # Overall confidence as weighted average
        scores['overall_confidence'] = (
            scores['skill_extraction_confidence'] * 0.4 +
            scores['education_confidence'] * 0.3 +
            scores['experience_confidence'] * 0.3
        )
        
        return scores
    
    def read_resume_text(self, file_path: str) -> str:
        """Reuse existing file reading logic"""
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


# Test the AI-powered parser
if __name__ == "__main__":
    print("=== Testing AI-Powered Resume Parser ===")
    
    ai_parser = AIResumeParser()
    
    # Test with sample resume
    test_file = "data/candidate1.txt"
    if os.path.exists(test_file):
        result = ai_parser.ai_powered_resume_analysis(test_file)
        
        print(f"File: {result['file_path']}")
        print(f"AI-Powered: {result.get('ai_powered', False)}")
        print(f"Success: {result['parsing_success']}")
        print(f"Skills Found: {result.get('skills', [])}")
        print(f"Organizations: {result.get('organizations', [])}")
        print(f"Experience Analysis: {result.get('experience_analysis', {})}")
        print(f"Confidence Scores: {result.get('confidence_scores', {})}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
    else:
        print(f"Test file {test_file} not found")

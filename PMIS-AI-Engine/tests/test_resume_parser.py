#!/usr/bin/env python3
"""
Unit tests for the resume_parser module.

Tests the functionality of the resume parsing pipeline including text extraction,
skill detection, education extraction, and skill scoring.

Run with:
    pytest -v tests/test_resume_parser.py
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_parser import ResumeParser

# Create fixtures for test data
@pytest.fixture
def sample_resume_text():
    """Return sample resume text for testing parser functions."""
    return """
    John Doe
    Software Engineer
    john.doe@example.com
    
    EDUCATION
    B.Tech in Computer Science, IIT Delhi
    CGPA: 8.5/10
    
    SKILLS
    Programming: Python, JavaScript, Java
    Web Development: React, Node.js, Express
    Data Science: Pandas, NumPy, Machine Learning
    
    EXPERIENCE
    Software Developer Intern at TechCorp
    - Developed a web application using React and Node.js
    - Implemented RESTful APIs for data management
    - Optimized database queries improving performance by 30%
    
    Research Assistant at AI Lab
    - Created machine learning models for natural language processing
    - Published a paper on sentiment analysis
    """

@pytest.fixture
def temp_resume_file(sample_resume_text):
    """Create a temporary resume file for testing file reading functions."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(sample_resume_text.encode('utf-8'))
        tmp_path = tmp.name
    
    yield tmp_path
    
    # Cleanup after test
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

# Test cases
class TestResumeParser:
    """Test cases for the ResumeParser class."""
    
    def setup_method(self):
        """Set up a ResumeParser instance before each test."""
        self.parser = ResumeParser()
    
    def test_initialization(self):
        """Test that the parser initializes with the correct skills database."""
        assert isinstance(self.parser, ResumeParser)
        assert "programming" in self.parser.SKILLS_DB
        assert "python" in self.parser.SKILLS_DB["programming"]
        assert len(self.parser.all_skills) > 0
    
    def test_read_resume_text(self, temp_resume_file):
        """Test that resume text can be read from a file."""
        text = self.parser.read_resume_text(temp_resume_file)
        assert "John Doe" in text
        assert "Software Engineer" in text
        assert "EDUCATION" in text
    
    def test_read_resume_nonexistent_file(self):
        """Test that an appropriate error is raised for nonexistent files."""
        with pytest.raises(FileNotFoundError):
            self.parser.read_resume_text("nonexistent_file.txt")
    
    def test_extract_skills(self, sample_resume_text):
        """Test skill extraction from resume text."""
        skills = self.parser.extract_skills(sample_resume_text)
        
        # Check that skills were detected from different categories
        assert "python" in skills.get("programming", [])
        assert "javascript" in skills.get("programming", [])
        assert "react" in skills.get("web_development", [])
        assert "machine learning" in skills.get("data_science", [])
        
        # Check that non-mentioned skills are not detected
        assert "docker" not in sum(skills.values(), [])
    
    def test_extract_education(self, sample_resume_text):
        """Test education information extraction."""
        education = self.parser.extract_education(sample_resume_text)
        
        # Should extract degree and CGPA
        assert "computer science" in education.get("degree", "").lower()
        assert education.get("cgpa") == "8.5"
    
    def test_extract_experience_keywords(self, sample_resume_text):
        """Test experience keyword extraction."""
        keywords = self.parser.extract_experience_keywords(sample_resume_text)
        
        # Common experience-related keywords that should be detected
        assert "developed" in keywords
        assert "implemented" in keywords
        assert "optimized" in keywords
    
    def test_calculate_skill_score(self):
        """Test skill score calculation."""
        # Create a test skills dictionary
        skills = {
            "programming": ["python", "javascript", "java"],
            "web_development": ["react", "node.js"],
            "data_science": ["pandas", "numpy"]
        }
        
        score = self.parser.calculate_skill_score(skills)
        
        # Check score is calculated and within range
        assert 0 <= score <= 1
        
        # More skills and categories should give a higher score
        skills_fewer = {"programming": ["python"]}
        score_fewer = self.parser.calculate_skill_score(skills_fewer)
        
        assert score > score_fewer
    
    def test_parse_resume(self, temp_resume_file):
        """Test complete resume parsing pipeline."""
        result = self.parser.parse_resume(temp_resume_file)
        
        # Should contain all expected keys
        assert "raw_text" in result
        assert "skills" in result
        assert "education" in result
        assert "experience_keywords" in result
        assert "skill_score" in result
        
        # Skill score should be between 0 and 1
        assert 0 <= result["skill_score"] <= 1
        
        # Should have detected skills
        assert len(result["skills"]) > 0
        
        # Should have detected experience keywords
        assert len(result["experience_keywords"]) > 0

# Run tests if file is executed directly
if __name__ == "__main__":
    pytest.main(["-v", __file__])

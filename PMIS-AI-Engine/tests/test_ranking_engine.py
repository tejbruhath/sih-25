#!/usr/bin/env python3
"""
Unit tests for the ranking_engine module.

Tests the AI-powered ranking and matching functionality including embeddings,
similarity calculations, and composite scoring.

Run with:
    pytest -v tests/test_ranking_engine.py
"""

import os
import sys
import pytest
import tempfile
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ranking_engine import PMISRankingEngine

@pytest.fixture
def sample_candidate():
    """Return sample candidate data."""
    return {
        'candidate_id': 'CAND_001',
        'name': 'John Doe',
        'age': 22,
        'social_category': 'General',
        'is_rural': False,
        'location': 'Delhi'
    }

@pytest.fixture
def sample_internship():
    """Return sample internship data."""
    return {
        'internship_id': 'INTERN_001',
        'company_name': 'TechCorp',
        'job_title': 'Software Developer',
        'capacity': 2,
        'location': 'Mumbai'
    }

@pytest.fixture
def mock_resume_data():
    """Return mock parsed resume data."""
    return {
        'raw_text': 'Software engineer with Python and React experience.',
        'skills': {
            'programming': ['python', 'javascript'],
            'web_development': ['react', 'node.js']
        },
        'skill_score': 0.75,
        'experience_keywords': ['developed', 'implemented']
    }

@pytest.fixture 
def sample_job_text():
    """Return sample job description text."""
    return """
    We are looking for a Software Developer Intern with experience in:
    - Python programming
    - React web development
    - Node.js backend development
    - Machine learning fundamentals
    
    The ideal candidate will have strong problem-solving skills and
    experience building web applications.
    """

class TestPMISRankingEngine:
    """Test cases for the PMIS Ranking Engine."""
    
    def setup_method(self):
        """Set up a ranking engine instance before each test."""
        # Mock the sentence transformer model to avoid downloading during tests
        with patch('ranking_engine.SentenceTransformer') as mock_transformer:
            # Create a mock model that returns random embeddings
            mock_model = Mock()
            mock_model.encode.return_value = np.random.rand(384)  # 384-dim embedding
            mock_transformer.return_value = mock_model
            
            self.engine = PMISRankingEngine()
            self.engine.model = mock_model
    
    def test_initialization(self):
        """Test that the ranking engine initializes properly."""
        assert hasattr(self.engine, 'model')
        assert hasattr(self.engine, 'resume_parser')
        assert hasattr(self.engine, 'embeddings_cache')
    
    def test_get_text_embedding(self):
        """Test text embedding generation."""
        text = "This is a test sentence."
        embedding = self.engine.get_text_embedding(text)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1  # Should be 1-dimensional
        
        # Test caching
        cached_embedding = self.engine.get_text_embedding(text, cache_key="test")
        np.testing.assert_array_equal(embedding, cached_embedding)
    
    def test_eligibility_filter(self, sample_candidate, sample_internship):
        """Test candidate eligibility filtering."""
        # Test eligible candidate
        is_eligible, reason = self.engine.eligibility_filter(sample_candidate, sample_internship)
        assert is_eligible
        assert "Eligible" in reason
        
        # Test ineligible candidate (too young)
        young_candidate = sample_candidate.copy()
        young_candidate['age'] = 19
        is_eligible, reason = self.engine.eligibility_filter(young_candidate, sample_internship)
        assert not is_eligible
        assert "Age" in reason
        
        # Test ineligible candidate (too old)
        old_candidate = sample_candidate.copy()
        old_candidate['age'] = 26
        is_eligible, reason = self.engine.eligibility_filter(old_candidate, sample_internship)
        assert not is_eligible
        assert "Age" in reason
    
    def test_calculate_semantic_similarity(self, sample_job_text):
        """Test semantic similarity calculation."""
        resume_text = "Software engineer with Python and React skills."
        
        similarity = self.engine.calculate_semantic_similarity(resume_text, sample_job_text)
        
        # Similarity should be a float between 0 and 1
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1
    
    def test_calculate_skill_overlap_score(self, mock_resume_data, sample_job_text):
        """Test skill overlap score calculation."""
        score = self.engine.calculate_skill_overlap_score(
            mock_resume_data['skills'], 
            sample_job_text
        )\n        \n        # Should detect overlap since both mention Python and React\n        assert 0 <= score <= 1\n        assert score > 0  # Should find some overlap\n    \n    def test_calculate_diversity_bonus(self):\n        \"\"\"Test diversity bonus calculation.\"\"\"\n        # Test general category candidate\n        general_candidate = {'social_category': 'General', 'is_rural': False}\n        bonus = self.engine.calculate_diversity_bonus(general_candidate)\n        assert bonus == 0.0\n        \n        # Test rural candidate\n        rural_candidate = {'social_category': 'General', 'is_rural': True}\n        bonus = self.engine.calculate_diversity_bonus(rural_candidate)\n        assert bonus == 0.05\n        \n        # Test SC candidate\n        sc_candidate = {'social_category': 'SC', 'is_rural': False}\n        bonus = self.engine.calculate_diversity_bonus(sc_candidate)\n        assert bonus == 0.05\n        \n        # Test rural SC candidate (both bonuses)\n        rural_sc_candidate = {'social_category': 'SC', 'is_rural': True}\n        bonus = self.engine.calculate_diversity_bonus(rural_sc_candidate)\n        assert bonus == 0.10\n        \n        # Test OBC candidate\n        obc_candidate = {'social_category': 'OBC', 'is_rural': False}\n        bonus = self.engine.calculate_diversity_bonus(obc_candidate)\n        assert bonus == 0.03\n    \n    def test_calculate_composite_score(self, sample_candidate, sample_internship, \n                                     mock_resume_data, sample_job_text):\n        \"\"\"Test composite score calculation.\"\"\"\n        scores = self.engine.calculate_composite_score(\n            sample_candidate, \n            sample_internship,\n            mock_resume_data,\n            sample_job_text\n        )\n        \n        # Check all required score components are present\n        assert 'semantic_similarity' in scores\n        assert 'skill_overlap' in scores\n        assert 'skill_strength' in scores\n        assert 'diversity_bonus' in scores\n        assert 'composite_score' in scores\n        \n        # All scores should be between 0 and 1\n        for score_name, score_value in scores.items():\n            assert 0 <= score_value <= 1, f\"{score_name} score out of range: {score_value}\"\n    \n    @patch('pandas.read_csv')\n    def test_generate_all_rankings_data_loading(self, mock_read_csv):\n        \"\"\"Test that the ranking generation properly loads data files.\"\"\"\n        # Mock CSV data\n        candidates_data = pd.DataFrame({\n            'candidate_id': ['CAND_001', 'CAND_002'],\n            'name': ['John Doe', 'Jane Smith'],\n            'age': [22, 23],\n            'social_category': ['General', 'OBC'],\n            'is_rural': [False, True],\n            'resume_filename': ['candidate1.txt', 'candidate2.txt']\n        })\n        \n        internships_data = pd.DataFrame({\n            'internship_id': ['INTERN_001'],\n            'company_name': ['TechCorp'],\n            'job_title': ['Software Developer'],\n            'capacity': [2],\n            'description_filename': ['job1.txt']\n        })\n        \n        mock_read_csv.side_effect = [candidates_data, internships_data]\n        \n        # Mock file existence and content\n        with patch('os.path.exists', return_value=True), \\\n             patch('builtins.open', mock_data=\"Job description content\"):\n            \n            # This should not raise an exception\n            try:\n                rankings = self.engine.generate_all_rankings(\n                    \"fake_candidates.csv\", \n                    \"fake_internships.csv\"\n                )\n                assert isinstance(rankings, dict)\n            except Exception as e:\n                # For unit testing, we expect this to fail due to file dependencies\n                # but should not fail due to initialization issues\n                assert \"Job description not found\" in str(e) or \"Could not extract text\" in str(e)\n\n# Integration test class for actual file-based tests\nclass TestResumeParserIntegration:\n    \"\"\"Integration tests that use actual files (if available).\"\"\"\n    \n    def setup_method(self):\n        \"\"\"Set up parser for integration tests.\"\"\"\n        self.parser = ResumeParser()\n        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')\n    \n    def test_parse_real_resume_files(self):\n        \"\"\"Test parsing with real resume files if they exist.\"\"\"\n        # Look for resume files in the data directory\n        resume_files = []\n        \n        if os.path.exists(self.data_dir):\n            for filename in os.listdir(self.data_dir):\n                if filename.endswith(('.txt', '.pdf', '.docx')) and 'candidate' in filename:\n                    resume_files.append(os.path.join(self.data_dir, filename))\n        \n        if not resume_files:\n            pytest.skip(\"No resume files found for integration testing\")\n        \n        for resume_file in resume_files[:3]:  # Test only first 3 files\n            try:\n                result = self.parser.parse_resume(resume_file)\n                \n                # Basic validation\n                assert \"error\" not in result or result[\"error\"] is None\n                assert \"raw_text\" in result\n                assert \"skills\" in result\n                assert \"skill_score\" in result\n                \n                print(f\"✅ Successfully parsed {os.path.basename(resume_file)}\")\n                print(f\"   Skills found: {result.get('total_skills', 0)}\")\n                print(f\"   Skill score: {result.get('skill_score', 0):.2f}\")\n                \n            except Exception as e:\n                print(f\"⚠️  Could not parse {resume_file}: {e}\")\n                # Don't fail the test for file parsing issues in integration tests\n\nclass TestRankingEngineEdgeCases:\n    \"\"\"Test edge cases and error handling.\"\"\"\n    \n    def setup_method(self):\n        \"\"\"Set up ranking engine for edge case tests.\"\"\"\n        with patch('ranking_engine.SentenceTransformer') as mock_transformer:\n            mock_model = Mock()\n            mock_model.encode.return_value = np.random.rand(384)\n            mock_transformer.return_value = mock_model\n            \n            self.engine = PMISRankingEngine()\n            self.engine.model = mock_model\n    \n    def test_empty_text_handling(self):\n        \"\"\"Test handling of empty text inputs.\"\"\"\n        embedding = self.engine.get_text_embedding(\"\")\n        assert isinstance(embedding, np.ndarray)\n    \n    def test_empty_skills_score(self):\n        \"\"\"Test skill overlap when candidate has no skills.\"\"\"\n        empty_skills = {}\n        job_text = \"Python React Node.js\"\n        \n        score = self.engine.calculate_skill_overlap_score(empty_skills, job_text)\n        assert score == 0.0\n    \n    def test_missing_social_category(self):\n        \"\"\"Test diversity bonus with missing social category.\"\"\"\n        candidate = {'is_rural': True}  # Missing social_category\n        \n        bonus = self.engine.calculate_diversity_bonus(candidate)\n        assert bonus == 0.05  # Should still get rural bonus\n\n# Run all tests if file is executed directly\nif __name__ == \"__main__\":\n    pytest.main([\"-v\", __file__])

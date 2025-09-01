"""
AI Ranking Engine for PMIS-AI System
====================================

This module implements the core AI ranking algorithm that calculates semantic
similarity between candidates and internships using transformer-based embeddings.

Features:
- Resume2Vec: Convert resumes to high-dimensional vectors
- Job2Vec: Convert job descriptions to embeddings  
- Cosine similarity scoring
- Rule-based eligibility filtering
- Composite scoring with multiple factors

Author: PMIS-AI Team
Created: 2025-01-01
Last Modified: 2025-01-01
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Any
import os
import pickle
import json
from resume_parser import ResumeParser

class PMISRankingEngine:
    """
    Advanced ranking engine that uses AI to match candidates with internships
    based on semantic similarity and rule-based constraints.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the ranking engine with a pre-trained sentence transformer model.
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        print("Loading AI model for semantic matching...")
        # Use a lightweight, fast model perfect for hackathons
        self.model = SentenceTransformer(model_name)
        self.resume_parser = ResumeParser()
        
        # Cache for embeddings to avoid recomputation
        self.embeddings_cache = {}
        self.cache_file = "data/embeddings_cache.pkl"
        self.load_cache()
        
        print("✅ AI Ranking Engine initialized successfully!")
    
    def load_cache(self):
        """Load previously computed embeddings from cache file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"Loaded {len(self.embeddings_cache)} cached embeddings")
            except Exception as e:
                print(f"Could not load cache: {e}")
                self.embeddings_cache = {}
    
    def save_cache(self):
        """Save computed embeddings to cache file."""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            print("✅ Embeddings cache saved")
        except Exception as e:
            print(f"Could not save cache: {e}")
    
    def get_text_embedding(self, text: str, cache_key: str = None) -> np.ndarray:
        """
        Convert text to high-dimensional vector representation using transformers.
        
        Args:
            text (str): Input text to embed
            cache_key (str): Optional key for caching the embedding
            
        Returns:
            np.ndarray: Dense vector representation of the text
        """
        # Check cache first
        if cache_key and cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Store in cache
        if cache_key:
            self.embeddings_cache[cache_key] = embedding
        
        return embedding
    
    def eligibility_filter(self, candidate: Dict, internship: Dict) -> Tuple[bool, str]:
        """
        Apply rule-based eligibility filters before AI ranking.
        
        Args:
            candidate (Dict): Candidate information
            internship (Dict): Internship information
            
        Returns:
            Tuple[bool, str]: (is_eligible, reason)
        """
        # Age requirement (21-24 for PM Internship Scheme)
        if not (21 <= candidate['age'] <= 24):
            return False, f"Age {candidate['age']} not in eligible range (21-24)"
        
        # All other basic eligibility criteria can be added here
        # For now, assume all candidates who meet age requirement are eligible
        
        return True, "Eligible"
    
    def calculate_semantic_similarity(self, resume_text: str, job_text: str, 
                                    candidate_id: str = None, job_id: str = None) -> float:
        """
        Calculate semantic similarity between resume and job description.
        
        Args:
            resume_text (str): Resume text content
            job_text (str): Job description text
            candidate_id (str): ID for caching
            job_id (str): ID for caching
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Generate embeddings with caching
        resume_embedding = self.get_text_embedding(
            resume_text, 
            cache_key=f"resume_{candidate_id}" if candidate_id else None
        )
        job_embedding = self.get_text_embedding(
            job_text,
            cache_key=f"job_{job_id}" if job_id else None
        )
        
        # Calculate cosine similarity
        similarity = cosine_similarity(
            resume_embedding.reshape(1, -1),
            job_embedding.reshape(1, -1)
        )[0][0]
        
        return float(similarity)
    
    def calculate_skill_overlap_score(self, candidate_skills: Dict, job_text: str) -> float:
        """
        Calculate skill overlap score based on extracted skills and job requirements.
        
        Args:
            candidate_skills (Dict): Candidate's categorized skills
            job_text (str): Job description text
            
        Returns:
            float: Skill overlap score between 0 and 1
        """
        job_text_lower = job_text.lower()
        
        # Count how many candidate skills appear in job description
        matching_skills = 0
        total_candidate_skills = 0
        
        for category, skills in candidate_skills.items():
            for skill in skills:
                total_candidate_skills += 1
                if skill.lower() in job_text_lower:
                    matching_skills += 1
        
        if total_candidate_skills == 0:
            return 0.0
        
        return matching_skills / total_candidate_skills
    
    def calculate_diversity_bonus(self, candidate: Dict) -> float:
        """
        Calculate diversity bonus for affirmative action compliance.
        
        Args:
            candidate (Dict): Candidate information
            
        Returns:
            float: Diversity bonus score (0.0 to 0.1)
        """
        bonus = 0.0
        
        # Rural background bonus
        if candidate.get('is_rural', False):
            bonus += 0.05
        
        # Social category bonus (as per government guidelines)
        social_category = candidate.get('social_category', 'General')
        if social_category in ['SC', 'ST']:
            bonus += 0.05
        elif social_category == 'OBC':
            bonus += 0.03
        
        return min(bonus, 0.1)  # Cap at 0.1
    
    def calculate_composite_score(self, candidate: Dict, internship: Dict, 
                                resume_parsed: Dict, job_text: str) -> Dict[str, float]:
        """
        Calculate comprehensive matching score using multiple factors.
        
        Args:
            candidate (Dict): Candidate information
            internship (Dict): Internship information
            resume_parsed (Dict): Parsed resume data
            job_text (str): Job description text
            
        Returns:
            Dict[str, float]: Breakdown of all scoring components
        """
        # 1. Semantic similarity (40% weight)
        semantic_score = self.calculate_semantic_similarity(
            resume_parsed['raw_text'], 
            job_text,
            candidate['candidate_id'],
            internship['internship_id']
        )
        
        # 2. Skill overlap (35% weight)
        skill_score = self.calculate_skill_overlap_score(
            resume_parsed['skills'], 
            job_text
        )
        
        # 3. Candidate skill strength (15% weight)
        skill_strength = resume_parsed['skill_score']
        
        # 4. Diversity bonus (10% weight)
        diversity_bonus = self.calculate_diversity_bonus(candidate)
        
        # Calculate weighted composite score
        composite_score = (
            semantic_score * 0.40 +
            skill_score * 0.35 +
            skill_strength * 0.15 +
            diversity_bonus * 0.10
        )
        
        return {
            'semantic_similarity': semantic_score,
            'skill_overlap': skill_score,
            'skill_strength': skill_strength,
            'diversity_bonus': diversity_bonus,
            'composite_score': composite_score
        }
    
    def rank_candidates_for_job(self, candidates_df: pd.DataFrame, 
                               internship: Dict, job_text: str) -> List[Dict]:
        """
        Rank all eligible candidates for a specific internship.
        
        Args:
            candidates_df (pd.DataFrame): All candidates data
            internship (Dict): Internship information
            job_text (str): Job description text
            
        Returns:
            List[Dict]: Ranked list of candidates with scores
        """
        ranked_candidates = []
        
        for _, candidate in candidates_df.iterrows():
            candidate_dict = candidate.to_dict()
            
            # Check eligibility first
            is_eligible, reason = self.eligibility_filter(candidate_dict, internship)
            if not is_eligible:
                continue
            
            # Parse resume
            resume_path = f"data/{candidate['resume_filename']}"
            if not os.path.exists(resume_path):
                continue
                
            resume_parsed = self.resume_parser.parse_resume(resume_path)
            if "error" in resume_parsed:
                continue
            
            # Calculate all scores
            scores = self.calculate_composite_score(
                candidate_dict, internship, resume_parsed, job_text
            )
            
            # Compile candidate result
            result = {
                'candidate_id': candidate['candidate_id'],
                'name': candidate['name'],
                'age': candidate['age'],
                'social_category': candidate['social_category'],
                'is_rural': candidate['is_rural'],
                'scores': scores,
                'resume_data': resume_parsed
            }
            
            ranked_candidates.append(result)
        
        # Sort by composite score (highest first)
        ranked_candidates.sort(key=lambda x: x['scores']['composite_score'], reverse=True)
        
        return ranked_candidates
    
    def generate_all_rankings(self, candidates_file: str, internships_file: str) -> Dict[str, List]:
        """
        Generate rankings for all internships against all candidates.
        
        Args:
            candidates_file (str): Path to candidates CSV file
            internships_file (str): Path to internships CSV file
            
        Returns:
            Dict[str, List]: Rankings for each internship
        """
        print("\n🚀 Starting AI-powered ranking generation...")
        
        # Load data
        candidates_df = pd.read_csv(candidates_file)
        internships_df = pd.read_csv(internships_file)
        
        all_rankings = {}
        
        for _, internship in internships_df.iterrows():
            internship_dict = internship.to_dict()
            
            # Read job description
            job_file_path = f"data/{internship['description_filename']}"
            if not os.path.exists(job_file_path):
                print(f"⚠️  Job description not found: {job_file_path}")
                continue
                
            with open(job_file_path, 'r', encoding='utf-8') as f:
                job_text = f.read()
            
            print(f"📊 Ranking candidates for {internship['company_name']} - {internship['job_title']}")
            
            # Generate rankings for this internship
            ranked_candidates = self.rank_candidates_for_job(
                candidates_df, internship_dict, job_text
            )
            
            all_rankings[internship['internship_id']] = ranked_candidates
            
            print(f"   ✅ {len(ranked_candidates)} eligible candidates ranked")
        
        # Save embeddings cache after processing
        self.save_cache()
        
        print("\n🎯 AI ranking generation complete!")
        return all_rankings

# Test function
def test_ranking_engine():
    """Test the ranking engine with sample data."""
    print("🧪 Testing AI Ranking Engine...\n")
    
    engine = PMISRankingEngine()
    
    # Test with our mock data
    rankings = engine.generate_all_rankings(
        "data/candidates.csv",
        "data/internships.csv"
    )
    
    # Display sample results
    for internship_id, candidates in rankings.items():
        print(f"\n=== Top 3 candidates for {internship_id} ===")
        for i, candidate in enumerate(candidates[:3]):
            scores = candidate['scores']
            print(f"{i+1}. {candidate['name']} (ID: {candidate['candidate_id']})")
            print(f"   Composite Score: {scores['composite_score']:.3f}")
            print(f"   Semantic: {scores['semantic_similarity']:.3f} | "
                  f"Skills: {scores['skill_overlap']:.3f} | "
                  f"Diversity: {scores['diversity_bonus']:.3f}")
    
    return rankings

if __name__ == "__main__":
    test_ranking_engine()

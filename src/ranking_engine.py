"""
AI Ranking Engine for PMIS-AI System
Implements semantic matching using transformer models and rule-based filtering
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Any
import json
import os

class RankingEngine:
    def __init__(self):
        self.feature_extractor = None
        self.model_loaded = False
        
    def load_transformer_model(self):
        """
        Load transformer model for text embeddings
        Using a lightweight model for hackathon compatibility
        """
        try:
            from transformers import pipeline
            # Using distilbert for faster processing
            self.feature_extractor = pipeline(
                'feature-extraction', 
                model='distilbert-base-uncased',
                return_tensors='np'
            )
            self.model_loaded = True
            print("✅ Transformer model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading transformer model: {str(e)}")
            print("💡 Falling back to TF-IDF for text similarity")
            self.model_loaded = False

    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to numerical embedding vector
        
        Args:
            text (str): Input text
            
        Returns:
            np.ndarray: Text embedding vector
        """
        if not self.model_loaded:
            # Fallback to simple TF-IDF if transformer fails
            return self._get_tfidf_embedding(text)
        
        try:
            # Clean and truncate text for transformer
            clean_text = self._clean_text(text)
            
            # Get embeddings from transformer
            embeddings = self.feature_extractor(clean_text)
            
            # Average token embeddings to get document embedding
            if isinstance(embeddings, list):
                embeddings = np.array(embeddings[0])
            
            # Handle different output shapes and convert to numpy
            if hasattr(embeddings, 'numpy'):
                embeddings = embeddings.numpy()
            elif hasattr(embeddings, 'detach'):
                embeddings = embeddings.detach().numpy()
            
            # Ensure it's a numpy array
            embeddings = np.array(embeddings)
            
            # Handle different output shapes
            if len(embeddings.shape) == 3:
                # Shape: (1, seq_len, hidden_size)
                document_embedding = np.mean(embeddings[0], axis=0)
            elif len(embeddings.shape) == 2:
                # Shape: (seq_len, hidden_size)
                document_embedding = np.mean(embeddings, axis=0)
            else:
                document_embedding = embeddings.flatten()
            
            return document_embedding
            
        except Exception as e:
            print(f"Error in transformer embedding: {str(e)}")
            return self._get_tfidf_embedding(text)

    def _clean_text(self, text: str, max_length: int = 512) -> str:
        """Clean and truncate text for processing"""
        # Remove extra whitespace and truncate
        clean_text = ' '.join(text.split())
        
        # Truncate to avoid transformer limits
        words = clean_text.split()
        if len(words) > max_length:
            clean_text = ' '.join(words[:max_length])
        
        return clean_text

    def _get_tfidf_embedding(self, text: str) -> np.ndarray:
        """
        Fallback TF-IDF based embedding for compatibility
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Simple TF-IDF on character n-grams for basic similarity
        vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4),
            max_features=100,
            lowercase=True
        )
        
        try:
            # Fit and transform the text
            tfidf_matrix = vectorizer.fit_transform([text])
            return tfidf_matrix.toarray().flatten()
        except:
            # Ultimate fallback: simple character frequency
            return np.array([hash(text) % 100 for _ in range(100)], dtype=float)

    def calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1, vec2: Input vectors
            
        Returns:
            float: Similarity score (0-1)
        """
        try:
            # Ensure vectors are 2D for sklearn
            v1 = vec1.reshape(1, -1)
            v2 = vec2.reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(v1, v2)[0][0]
            
            # Ensure score is between 0 and 1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0

    def eligibility_filter(self, candidate: Dict, internship: Dict) -> Tuple[bool, str]:
        """
        Apply rule-based eligibility filtering
        
        Args:
            candidate: Candidate information
            internship: Internship information
            
        Returns:
            Tuple[bool, str]: (is_eligible, reason)
        """
        # Age requirement (21-24 for PM Internship Scheme)
        age = candidate.get('age', 0)
        if not (21 <= age <= 24):
            return False, f"Age {age} not in eligible range (21-24)"
        
        # Add more eligibility rules as needed
        # Location preferences, education requirements, etc.
        
        return True, "Eligible"

    def calculate_match_score(self, candidate_data: Dict, internship_data: Dict) -> Dict:
        """
        Calculate comprehensive match score between candidate and internship
        
        Args:
            candidate_data: Parsed candidate information
            internship_data: Parsed internship information
            
        Returns:
            Dict: Match score details
        """
        try:
            # Check eligibility first
            is_eligible, eligibility_reason = self.eligibility_filter(
                candidate_data, internship_data
            )
            
            if not is_eligible:
                return {
                    'overall_score': 0.0,
                    'semantic_score': 0.0,
                    'skill_match_score': 0.0,
                    'eligible': False,
                    'reason': eligibility_reason
                }
            
            # Semantic similarity using text embeddings
            candidate_text = candidate_data.get('text', '')
            internship_text = internship_data.get('text', '')
            
            if candidate_text and internship_text:
                candidate_embedding = self.get_text_embedding(candidate_text)
                internship_embedding = self.get_text_embedding(internship_text)
                semantic_score = self.calculate_similarity(candidate_embedding, internship_embedding)
            else:
                semantic_score = 0.0
            
            # Skill-based matching
            candidate_skills = set(candidate_data.get('skills', []))
            internship_skills = set(internship_data.get('required_skills', []))
            
            if candidate_skills and internship_skills:
                skill_overlap = len(candidate_skills.intersection(internship_skills))
                skill_match_score = skill_overlap / len(internship_skills) if internship_skills else 0.0
            else:
                skill_match_score = 0.0
            
            # Weighted overall score
            overall_score = (
                0.6 * semantic_score +  # 60% semantic similarity
                0.4 * skill_match_score  # 40% skill matching
            )
            
            return {
                'overall_score': round(overall_score, 4),
                'semantic_score': round(semantic_score, 4),
                'skill_match_score': round(skill_match_score, 4),
                'eligible': True,
                'reason': 'Match calculated successfully'
            }
            
        except Exception as e:
            return {
                'overall_score': 0.0,
                'semantic_score': 0.0,
                'skill_match_score': 0.0,
                'eligible': False,
                'reason': f'Error calculating match: {str(e)}'
            }

    def generate_preference_lists(self, candidates: List[Dict], internships: List[Dict]) -> Tuple[Dict, Dict]:
        """
        Generate preference lists for stable matching algorithm
        
        Args:
            candidates: List of candidate data
            internships: List of internship data
            
        Returns:
            Tuple[Dict, Dict]: (candidate_preferences, internship_preferences)
        """
        print("🔄 Generating preference lists...")
        
        # Initialize preference dictionaries
        candidate_preferences = {}
        internship_preferences = {}
        
        # Calculate all pairwise match scores
        match_scores = {}
        
        for candidate in candidates:
            candidate_id = candidate['candidate_id']
            candidate_scores = []
            
            for internship in internships:
                internship_id = internship['internship_id']
                
                # Calculate match score
                score_data = self.calculate_match_score(candidate, internship)
                score = score_data['overall_score']
                
                # Store for internship preferences
                if internship_id not in match_scores:
                    match_scores[internship_id] = []
                
                match_scores[internship_id].append({
                    'candidate_id': candidate_id,
                    'score': score,
                    'eligible': score_data['eligible']
                })
                
                # Add to candidate preferences if eligible
                if score_data['eligible']:
                    candidate_scores.append({
                        'internship_id': internship_id,
                        'score': score
                    })
            
            # Sort candidate preferences by score (highest first)
            candidate_scores.sort(key=lambda x: x['score'], reverse=True)
            candidate_preferences[candidate_id] = [item['internship_id'] for item in candidate_scores]
        
        # Generate internship preferences
        for internship_id, candidate_scores in match_scores.items():
            # Filter eligible candidates and sort by score
            eligible_candidates = [
                item for item in candidate_scores 
                if item['eligible'] and item['score'] > 0
            ]
            eligible_candidates.sort(key=lambda x: x['score'], reverse=True)
            
            internship_preferences[internship_id] = [
                item['candidate_id'] for item in eligible_candidates
            ]
        
        print(f"✅ Generated preferences for {len(candidate_preferences)} candidates and {len(internship_preferences)} internships")
        
        return candidate_preferences, internship_preferences


# Test function
if __name__ == "__main__":
    print("=== Testing Ranking Engine ===")
    
    engine = RankingEngine()
    engine.load_transformer_model()
    
    # Test text similarity
    text1 = "Python machine learning data science artificial intelligence"
    text2 = "Software development Python programming AI ML algorithms"
    
    emb1 = engine.get_text_embedding(text1)
    emb2 = engine.get_text_embedding(text2)
    similarity = engine.calculate_similarity(emb1, emb2)
    
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Similarity Score: {similarity:.4f}")
    
    # Test match scoring
    candidate = {
        'candidate_id': 1,
        'age': 22,
        'text': text1,
        'skills': ['python', 'machine learning', 'data science']
    }
    
    internship = {
        'internship_id': 1,
        'text': text2,
        'required_skills': ['python', 'programming', 'ai']
    }
    
    match_result = engine.calculate_match_score(candidate, internship)
    print(f"\nMatch Score Result: {match_result}")

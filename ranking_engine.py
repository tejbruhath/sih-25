import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Dict, Any
import pandas as pd

class RankingEngine:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the ranking engine with a pre-trained transformer model
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        # Set model to evaluation mode
        self.model.eval()
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to numerical vector using transformer model
        """
        try:
            # Tokenize the text
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # Get model outputs
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Use mean pooling to get sentence embedding
            embeddings = outputs.last_hidden_state
            attention_mask = inputs['attention_mask']
            
            # Apply attention mask and take mean
            masked_embeddings = embeddings * attention_mask.unsqueeze(-1)
            summed = torch.sum(masked_embeddings, dim=1)
            counts = torch.clamp(attention_mask.sum(dim=1, keepdim=True), min=1e-9)
            mean_pooled = summed / counts
            
            return mean_pooled.squeeze().numpy()
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(384)  # Default embedding size for all-MiniLM-L6-v2
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        try:
            # Reshape embeddings for sklearn
            emb1_reshaped = embedding1.reshape(1, -1)
            emb2_reshaped = embedding2.reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(emb1_reshaped, emb2_reshaped)[0][0]
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def calculate_skill_match_score(self, candidate_skills: List[str], job_skills: List[str]) -> float:
        """
        Calculate skill match score based on overlapping skills
        """
        if not candidate_skills or not job_skills:
            return 0.0
        
        # Convert to sets for easier comparison
        candidate_skill_set = set(skill.lower() for skill in candidate_skills)
        job_skill_set = set(skill.lower() for skill in job_skills)
        
        # Calculate intersection and union
        intersection = candidate_skill_set.intersection(job_skill_set)
        union = candidate_skill_set.union(job_skill_set)
        
        # Jaccard similarity
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def calculate_comprehensive_score(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """
        Calculate comprehensive matching score combining multiple factors
        """
        # Extract relevant information
        candidate_text = candidate_data.get('text', '')
        job_description = job_data.get('description', '')
        candidate_skills = candidate_data.get('skills', [])
        job_skills = job_data.get('required_skills', [])
        
        # Calculate different scores
        text_similarity = self._calculate_text_similarity(candidate_text, job_description)
        skill_match = self.calculate_skill_match_score(candidate_skills, job_skills)
        
        # Weighted combination (can be adjusted)
        text_weight = 0.6
        skill_weight = 0.4
        
        comprehensive_score = (text_weight * text_similarity) + (skill_weight * skill_match)
        
        return comprehensive_score
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate text similarity using embeddings
        """
        try:
            embedding1 = self.get_text_embedding(text1)
            embedding2 = self.get_text_embedding(text2)
            return self.calculate_similarity(embedding1, embedding2)
        except Exception as e:
            print(f"Error calculating text similarity: {e}")
            return 0.0
    
    def rank_candidates_for_job(self, candidates: List[Dict[str, Any]], job: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank candidates for a specific job based on comprehensive scores
        """
        ranked_candidates = []
        
        for candidate in candidates:
            score = self.calculate_comprehensive_score(candidate, job)
            ranked_candidates.append({
                'candidate': candidate,
                'score': score
            })
        
        # Sort by score in descending order
        ranked_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return ranked_candidates

# Example usage
if __name__ == "__main__":
    # Initialize ranking engine
    ranking_engine = RankingEngine()
    
    # Test with sample data
    candidate_text = "Experienced Python developer with machine learning skills"
    job_description = "Looking for a Python developer with data analysis experience"
    
    # Calculate similarity
    similarity = ranking_engine._calculate_text_similarity(candidate_text, job_description)
    print(f"Text similarity: {similarity:.4f}")
    
    # Test skill matching
    candidate_skills = ["python", "machine learning", "data analysis"]
    job_skills = ["python", "data analysis", "statistics"]
    
    skill_score = ranking_engine.calculate_skill_match_score(candidate_skills, job_skills)
    print(f"Skill match score: {skill_score:.4f}")

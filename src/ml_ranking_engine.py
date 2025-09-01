"""
ML-Powered Ranking Engine for PMIS-AI System
Implements XGBoost/LightGBM models to learn complex candidate-internship suitability patterns
"""

import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score, precision_recall_curve
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class MLRankingEngine:
    def __init__(self, model_type='xgboost'):
        """
        Initialize ML-Powered Ranking Engine
        
        Args:
            model_type: 'xgboost' or 'lightgbm'
        """
        self.model_type = model_type
        self.model = None
        self.feature_columns = []
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.sentence_transformer = None
        self.is_trained = False
        
        # Initialize sentence transformer for Resume2Vec
        self.load_sentence_transformer()
        
    def load_sentence_transformer(self):
        """Load sentence transformer for advanced embeddings"""
        try:
            # Using all-MiniLM-L6-v2 for better semantic understanding
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Sentence transformer loaded successfully")
        except Exception as e:
            print(f"❌ Error loading sentence transformer: {str(e)}")
            self.sentence_transformer = None
    
    def generate_resume2vec_embeddings(self, text: str) -> np.ndarray:
        """
        Generate advanced Resume2Vec embeddings using sentence transformers
        
        Args:
            text: Resume or job description text
            
        Returns:
            np.ndarray: High-dimensional semantic embedding
        """
        if not self.sentence_transformer:
            # Fallback to simple TF-IDF if sentence transformer fails
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            try:
                tfidf_matrix = vectorizer.fit_transform([text])
                return tfidf_matrix.toarray().flatten()
            except:
                return np.zeros(100)
        
        try:
            # Clean and truncate text
            clean_text = ' '.join(text.split()[:512])  # Limit to 512 words
            embedding = self.sentence_transformer.encode(clean_text)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return np.zeros(384)  # Default embedding size for all-MiniLM-L6-v2
    
    def extract_advanced_features(self, candidate: Dict, internship: Dict) -> Dict:
        """
        Extract comprehensive features for ML model
        
        Args:
            candidate: Candidate information
            internship: Internship information
            
        Returns:
            Dict: Engineered features
        """
        features = {}
        
        # === Semantic Similarity Features ===
        candidate_text = candidate.get('text', '')
        internship_text = internship.get('text', '')
        
        if candidate_text and internship_text:
            candidate_embedding = self.generate_resume2vec_embeddings(candidate_text)
            internship_embedding = self.generate_resume2vec_embeddings(internship_text)
            
            # Cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(
                candidate_embedding.reshape(1, -1),
                internship_embedding.reshape(1, -1)
            )[0][0]
            features['semantic_similarity'] = similarity
            
            # Euclidean distance (normalized)
            euclidean_dist = np.linalg.norm(candidate_embedding - internship_embedding)
            features['semantic_distance'] = euclidean_dist / (np.linalg.norm(candidate_embedding) + 1e-8)
        else:
            features['semantic_similarity'] = 0.0
            features['semantic_distance'] = 1.0
        
        # === Structured Data Features ===
        features['candidate_age'] = candidate.get('age', 22)
        features['is_rural'] = int(candidate.get('is_rural', False))
        features['social_category_general'] = int(candidate.get('social_category', 'General') == 'General')
        features['social_category_obc'] = int(candidate.get('social_category', 'General') == 'OBC')
        features['social_category_sc'] = int(candidate.get('social_category', 'General') == 'SC')
        features['social_category_st'] = int(candidate.get('social_category', 'General') == 'ST')
        
        # Internship features
        features['internship_capacity'] = internship.get('capacity', 1)
        features['sector_technology'] = int(internship.get('sector', '').lower() == 'technology')
        features['sector_finance'] = int(internship.get('sector', '').lower() == 'finance')
        features['sector_healthcare'] = int(internship.get('sector', '').lower() == 'healthcare')
        features['sector_energy'] = int(internship.get('sector', '').lower() == 'energy')
        features['sector_agriculture'] = int(internship.get('sector', '').lower() == 'agriculture')
        features['sector_education'] = int(internship.get('sector', '').lower() == 'education')
        features['sector_government'] = int(internship.get('sector', '').lower() == 'government')
        features['sector_marketing'] = int(internship.get('sector', '').lower() == 'marketing')
        
        # === Skill Match Features ===
        candidate_skills = set(candidate.get('skills', []))
        internship_skills = set(internship.get('required_skills', []))
        
        if candidate_skills and internship_skills:
            skill_overlap = len(candidate_skills.intersection(internship_skills))
            features['skill_overlap_count'] = skill_overlap
            features['skill_match_ratio'] = skill_overlap / len(internship_skills) if internship_skills else 0
            features['candidate_skill_coverage'] = skill_overlap / len(candidate_skills) if candidate_skills else 0
        else:
            features['skill_overlap_count'] = 0
            features['skill_match_ratio'] = 0
            features['candidate_skill_coverage'] = 0
        
        features['total_candidate_skills'] = len(candidate_skills)
        features['total_required_skills'] = len(internship_skills)
        
        # === Experience Features ===
        features['experience_years'] = candidate.get('experience_years', 0)
        features['has_experience'] = int(candidate.get('experience_years', 0) > 0)
        
        # === Education Features ===
        education = candidate.get('education', [])
        features['has_btech'] = int(any('tech' in str(edu).lower() for edu in education))
        features['has_masters'] = int(any('master' in str(edu).lower() or 'mtech' in str(edu).lower() for edu in education))
        features['has_mba'] = int(any('mba' in str(edu).lower() for edu in education))
        
        # === Location Preference Features ===
        # This would be enhanced with actual location data
        features['location_preference_match'] = 0.8  # Placeholder
        
        # === Advanced Interaction Features ===
        features['age_rural_interaction'] = features['candidate_age'] * features['is_rural']
        features['skill_semantic_interaction'] = features['skill_match_ratio'] * features['semantic_similarity']
        features['experience_sector_match'] = features['experience_years'] * features['sector_technology']  # Example
        
        return features
    
    def generate_synthetic_training_data(self, candidates: List[Dict], 
                                       internships: List[Dict], n_samples: int = 1000) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Generate synthetic training data for supervised learning
        
        Args:
            candidates: List of candidate profiles
            internships: List of internship opportunities
            n_samples: Number of training samples to generate
            
        Returns:
            Tuple[pd.DataFrame, np.ndarray]: Features and labels
        """
        print(f"🔄 Generating {n_samples} synthetic training samples...")
        
        features_list = []
        labels = []
        
        np.random.seed(42)  # For reproducibility
        
        for _ in range(n_samples):
            # Randomly sample candidate and internship
            candidate = np.random.choice(candidates)
            internship = np.random.choice(internships)
            
            # Extract features
            features = self.extract_advanced_features(candidate, internship)
            features_list.append(features)
            
            # Generate synthetic label based on heuristics
            # This simulates what would be "successful matches" in real data
            label = self._generate_synthetic_label(features, candidate, internship)
            labels.append(label)
        
        # Convert to DataFrame
        features_df = pd.DataFrame(features_list)
        labels_array = np.array(labels)
        
        print(f"✅ Generated training data: {features_df.shape[0]} samples, {features_df.shape[1]} features")
        print(f"📊 Positive samples: {np.sum(labels_array)} ({np.mean(labels_array)*100:.1f}%)")
        
        return features_df, labels_array
    
    def _generate_synthetic_label(self, features: Dict, candidate: Dict, internship: Dict) -> int:
        """
        Generate synthetic success labels based on realistic heuristics
        This simulates what would be actual success metrics in production
        """
        score = 0.0
        
        # High semantic similarity is good
        score += features['semantic_similarity'] * 0.3
        
        # Good skill match is important
        score += features['skill_match_ratio'] * 0.25
        
        # Age appropriateness (21-24 is ideal for internships)
        age = features['candidate_age']
        if 21 <= age <= 24:
            score += 0.2
        elif age < 21 or age > 26:
            score -= 0.1
        
        # Sector-specific preferences
        if features['sector_technology'] and features['total_candidate_skills'] > 5:
            score += 0.15  # Tech roles prefer more skills
        
        if features['sector_finance'] and features['has_mba']:
            score += 0.2  # Finance prefers MBA
        
        # Rural quota considerations
        if features['is_rural']:
            score += 0.1  # Slight boost for rural candidates
        
        # Experience considerations
        if features['has_experience']:
            score += 0.1
        
        # Add some randomness to simulate real-world variability
        noise = np.random.normal(0, 0.1)
        score += noise
        
        # Convert to binary label (threshold at 0.6)
        return int(score > 0.6)
    
    def train_model(self, features_df: pd.DataFrame, labels: np.ndarray):
        """
        Train the ML ranking model
        
        Args:
            features_df: Feature matrix
            labels: Target labels (1 for successful match, 0 for unsuccessful)
        """
        print(f"🔄 Training {self.model_type} model...")
        
        # Store feature columns
        self.feature_columns = features_df.columns.tolist()
        
        # Handle categorical encoding if needed
        features_processed = features_df.copy()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features_processed, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if self.model_type == 'xgboost':
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='logloss'
            )
        elif self.model_type == 'lightgbm':
            self.model = lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbose=-1
            )
        
        # Fit model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_pred = self.model.predict_proba(X_train_scaled)[:, 1]
        test_pred = self.model.predict_proba(X_test_scaled)[:, 1]
        
        train_auc = roc_auc_score(y_train, train_pred)
        test_auc = roc_auc_score(y_test, test_pred)
        
        print(f"✅ Model training completed!")
        print(f"📊 Training AUC: {train_auc:.4f}")
        print(f"📊 Test AUC: {test_auc:.4f}")
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\n🔍 Top 10 Most Important Features:")
            print(feature_importance.head(10).to_string(index=False))
        
        self.is_trained = True
    
    def predict_suitability_score(self, candidate: Dict, internship: Dict) -> float:
        """
        Predict suitability score for candidate-internship pair
        
        Args:
            candidate: Candidate information
            internship: Internship information
            
        Returns:
            float: Suitability score (0-1, higher is better)
        """
        if not self.is_trained:
            print("❌ Model not trained yet!")
            return 0.0
        
        try:
            # Extract features
            features = self.extract_advanced_features(candidate, internship)
            
            # Convert to DataFrame with same columns as training
            features_df = pd.DataFrame([features])
            
            # Ensure all training columns are present
            for col in self.feature_columns:
                if col not in features_df.columns:
                    features_df[col] = 0
            
            # Reorder columns to match training
            features_df = features_df[self.feature_columns]
            
            # Scale features
            features_scaled = self.scaler.transform(features_df)
            
            # Predict probability
            suitability_score = self.model.predict_proba(features_scaled)[0, 1]
            
            return float(suitability_score)
            
        except Exception as e:
            print(f"Error predicting suitability: {str(e)}")
            return 0.0
    
    def generate_ml_preference_lists(self, candidates: List[Dict], 
                                   internships: List[Dict]) -> Tuple[Dict, Dict]:
        """
        Generate preference lists using ML model predictions
        Enhanced to ensure valid matches by filtering low-confidence scores
        
        Args:
            candidates: List of candidate profiles
            internships: List of internship profiles
            
        Returns:
            Tuple[Dict, Dict]: (candidate_preferences, internship_preferences)
        """
        print("🔄 Generating ML-powered preference lists...")
        
        candidate_preferences = {}
        internship_preferences = {}
        
        # Set minimum confidence threshold for valid matches
        MIN_CONFIDENCE_THRESHOLD = 0.3
        
        # Generate candidate preferences (candidates ranking internships)
        for candidate in candidates:
            candidate_id = candidate['candidate_id']
            internship_scores = []
            
            for internship in internships:
                score = self.predict_suitability_score(candidate, internship)
                
                # Only include internships above confidence threshold
                if score >= MIN_CONFIDENCE_THRESHOLD:
                    internship_scores.append((internship['internship_id'], score))
            
            if internship_scores:
                # Sort by score (descending) and convert to ranking (ascending)
                internship_scores.sort(key=lambda x: x[1], reverse=True)
                candidate_preferences[candidate_id] = {
                    internship_id: rank + 1 
                    for rank, (internship_id, _) in enumerate(internship_scores)
                }
            else:
                # If no valid matches, include top 3 internships with lower threshold
                fallback_scores = []
                for internship in internships:
                    score = self.predict_suitability_score(candidate, internship)
                    fallback_scores.append((internship['internship_id'], score))
                
                fallback_scores.sort(key=lambda x: x[1], reverse=True)
                candidate_preferences[candidate_id] = {
                    internship_id: rank + 1 
                    for rank, (internship_id, _) in enumerate(fallback_scores[:3])
                }
        
        # Generate internship preferences (internships ranking candidates)
        for internship in internships:
            internship_id = internship['internship_id']
            candidate_scores = []
            
            for candidate in candidates:
                score = self.predict_suitability_score(candidate, internship)
                
                # Only include candidates above confidence threshold
                if score >= MIN_CONFIDENCE_THRESHOLD:
                    candidate_scores.append((candidate['candidate_id'], score))
            
            if candidate_scores:
                # Sort by score (descending) and convert to ranking (ascending)
                candidate_scores.sort(key=lambda x: x[1], reverse=True)
                internship_preferences[internship_id] = {
                    candidate_id: rank + 1 
                    for rank, (candidate_id, _) in enumerate(candidate_scores)
                }
            else:
                # If no valid matches, include all candidates with lower threshold
                fallback_scores = []
                for candidate in candidates:
                    score = self.predict_suitability_score(candidate, internship)
                    fallback_scores.append((candidate['candidate_id'], score))
                
                fallback_scores.sort(key=lambda x: x[1], reverse=True)
                internship_preferences[internship_id] = {
                    candidate_id: rank + 1 
                    for rank, (candidate_id, _) in enumerate(fallback_scores)
                }
        
        # Debug information
        valid_candidate_prefs = sum(1 for prefs in candidate_preferences.values() if prefs)
        valid_internship_prefs = sum(1 for prefs in internship_preferences.values() if prefs)
        
        print(f"✅ Generated ML preferences for {len(candidates)} candidates and {len(internships)} internships")
        print(f"📊 Valid candidate preferences: {valid_candidate_prefs}/{len(candidates)}")
        print(f"📊 Valid internship preferences: {valid_internship_prefs}/{len(internships)}")
        
        return candidate_preferences, internship_preferences
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if not self.is_trained:
            print("❌ No trained model to save!")
            return
        
        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.feature_columns = model_data['feature_columns']
            self.scaler = model_data['scaler']
            self.model_type = model_data['model_type']
            self.is_trained = model_data['is_trained']
            
            print(f"✅ Model loaded from {filepath}")
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")


# Test the ML Ranking Engine
if __name__ == "__main__":
    print("=== Testing ML-Powered Ranking Engine ===")
    
    # Create test data
    candidates = [
        {
            'candidate_id': 1,
            'age': 22,
            'is_rural': False,
            'social_category': 'General',
            'text': 'Python machine learning data science artificial intelligence',
            'skills': ['python', 'machine learning', 'data science'],
            'education': ['b.tech'],
            'experience_years': 0
        },
        {
            'candidate_id': 2,
            'age': 23,
            'is_rural': True,
            'social_category': 'OBC',
            'text': 'Environmental engineering renewable energy sustainability',
            'skills': ['environmental analysis', 'renewable energy'],
            'education': ['b.tech'],
            'experience_years': 1
        }
    ]
    
    internships = [
        {
            'internship_id': 1,
            'sector': 'Technology',
            'capacity': 3,
            'text': 'Software development Python programming AI ML algorithms',
            'required_skills': ['python', 'programming', 'ai']
        },
        {
            'internship_id': 2,
            'sector': 'Energy',
            'capacity': 2,
            'text': 'Renewable energy analysis solar wind power sustainability',
            'required_skills': ['renewable energy', 'environmental analysis']
        }
    ]
    
    # Test ML engine
    ml_engine = MLRankingEngine(model_type='xgboost')
    
    # Generate training data and train model
    features_df, labels = ml_engine.generate_synthetic_training_data(candidates, internships, n_samples=500)
    ml_engine.train_model(features_df, labels)
    
    # Test prediction
    score = ml_engine.predict_suitability_score(candidates[0], internships[0])
    print(f"\n🎯 Suitability Score (Candidate 1 -> Internship 1): {score:.4f}")
    
    # Generate ML preferences
    candidate_prefs, internship_prefs = ml_engine.generate_ml_preference_lists(candidates, internships)
    print(f"\n📋 ML-Generated Preferences:")
    print(f"Candidate preferences: {candidate_prefs}")
    print(f"Internship preferences: {internship_prefs}")

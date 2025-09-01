"""
Unified AI-Native PMIS Engine
Integrates ML-Powered Ranking, Custom NER, and Stable Matching as per blueprint
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import os
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our AI components
from ml_ranking_engine import MLRankingEngine
from custom_ner_model import CustomNERModel
from resume_parser import ResumeParser

class UnifiedAIEngine:
    def __init__(self):
        """
        Initialize the unified AI-native PMIS engine
        Following the blueprint's ML-first approach
        """
        self.ml_ranking_engine = MLRankingEngine(model_type='xgboost')
        self.custom_ner_model = CustomNERModel()
        self.resume_parser = ResumeParser()  # Fallback for file reading
        
        self.candidates_processed = []
        self.internships_processed = []
        self.ml_model_trained = False
        
        print("🚀 Unified AI-Native PMIS Engine Initialized")
        print("📋 Components: ML Ranking Engine + Custom NER + Stable Matching")
    
    def process_candidate_data_ai_native(self, candidates_file: str) -> List[Dict]:
        """
        AI-native candidate data processing pipeline
        Uses custom NER instead of rule-based extraction
        
        Args:
            candidates_file: Path to candidates CSV
            
        Returns:
            List[Dict]: AI-processed candidate profiles
        """
        print("🔄 Processing candidates with AI-native pipeline...")
        
        # Load raw candidate data
        candidates_df = pd.read_csv(candidates_file)
        processed_candidates = []
        
        for _, candidate in candidates_df.iterrows():
            resume_file = f"data/{candidate['resume_filename']}"
            
            # Read resume text
            resume_text = ""
            if os.path.exists(resume_file):
                resume_text = self.resume_parser.read_resume_text(resume_file)
            
            if resume_text:
                # AI-powered entity extraction using custom NER
                if self.custom_ner_model.nlp:
                    ai_entities = self.custom_ner_model.create_enhanced_resume_parser(resume_text)
                    
                    processed_candidate = {
                        'candidate_id': candidate['candidate_id'],
                        'name': candidate['name'],
                        'age': candidate['age'],
                        'social_category': candidate['social_category'],
                        'is_rural': candidate['is_rural'],
                        'text': resume_text,
                        
                        # AI-extracted features
                        'skills': ai_entities['skills'],
                        'universities': ai_entities['universities'],
                        'degrees': ai_entities['degrees'],
                        'job_titles': ai_entities['job_titles'],
                        'companies': ai_entities['companies'],
                        'experience_years': ai_entities['experience_years'],
                        
                        # AI metadata
                        'ner_confidence': ai_entities['ner_confidence'],
                        'parsing_method': ai_entities['parsing_method'],
                        'ai_processed': True
                    }
                else:
                    # Fallback to rule-based if NER fails
                    fallback_data = self.resume_parser.parse_resume(resume_file)
                    processed_candidate = {
                        **candidate.to_dict(),
                        'text': resume_text,
                        'skills': fallback_data['skills'],
                        'education': fallback_data['education'],
                        'experience_years': fallback_data['experience_years'],
                        'ai_processed': False,
                        'parsing_method': 'fallback_rules'
                    }
            else:
                # No resume text available
                processed_candidate = {
                    **candidate.to_dict(),
                    'text': '',
                    'skills': [],
                    'experience_years': 0,
                    'ai_processed': False,
                    'parsing_method': 'no_resume'
                }
            
            processed_candidates.append(processed_candidate)
        
        self.candidates_processed = processed_candidates
        
        ai_processed_count = sum(1 for c in processed_candidates if c.get('ai_processed', False))
        print(f"✅ Processed {len(processed_candidates)} candidates")
        print(f"🤖 AI-processed: {ai_processed_count} ({ai_processed_count/len(processed_candidates)*100:.1f}%)")
        
        return processed_candidates
    
    def process_internship_data_ai_native(self, internships_file: str) -> List[Dict]:
        """
        AI-native internship data processing pipeline
        
        Args:
            internships_file: Path to internships CSV
            
        Returns:
            List[Dict]: AI-processed internship profiles
        """
        print("🔄 Processing internships with AI-native pipeline...")
        
        # Load raw internship data
        internships_df = pd.read_csv(internships_file)
        processed_internships = []
        
        for _, internship in internships_df.iterrows():
            desc_file = f"data/{internship['description_filename']}"
            
            # Read job description
            job_text = ""
            if os.path.exists(desc_file):
                with open(desc_file, 'r', encoding='utf-8') as f:
                    job_text = f.read()
            
            if job_text:
                # AI-powered skill extraction from job descriptions
                if self.custom_ner_model.nlp:
                    ai_entities = self.custom_ner_model.extract_entities_with_custom_ner(job_text)
                    required_skills = ai_entities['skills']
                else:
                    # Fallback skill extraction
                    required_skills = self.resume_parser.extract_skills(job_text)
                
                processed_internship = {
                    'internship_id': internship['internship_id'],
                    'company_name': internship['company_name'],
                    'job_title': internship['job_title'],
                    'sector': internship['sector'],
                    'location': internship['location'],
                    'capacity': internship['capacity'],
                    'text': job_text,
                    'required_skills': required_skills,
                    'ai_processed': self.custom_ner_model.nlp is not None
                }
            else:
                processed_internship = {
                    **internship.to_dict(),
                    'text': '',
                    'required_skills': [],
                    'ai_processed': False
                }
            
            processed_internships.append(processed_internship)
        
        self.internships_processed = processed_internships
        
        ai_processed_count = sum(1 for i in processed_internships if i.get('ai_processed', False))
        print(f"✅ Processed {len(processed_internships)} internships")
        print(f"🤖 AI-processed: {ai_processed_count} ({ai_processed_count/len(processed_internships)*100:.1f}%)")
        
        return processed_internships
    
    def train_ml_ranking_model(self, n_samples: int = 2000):
        """
        Train the ML-powered ranking model on processed data
        
        Args:
            n_samples: Number of synthetic training samples
        """
        if not self.candidates_processed or not self.internships_processed:
            print("❌ No processed data available for training!")
            return
        
        print(f"🔄 Training ML ranking model with {n_samples} synthetic samples...")
        
        # Generate synthetic training data
        features_df, labels = self.ml_ranking_engine.generate_synthetic_training_data(
            self.candidates_processed, 
            self.internships_processed, 
            n_samples=n_samples
        )
        
        # Train the model
        self.ml_ranking_engine.train_model(features_df, labels)
        self.ml_model_trained = True
        
        print("✅ ML ranking model training completed!")
    
    def run_ai_native_allocation(self) -> Dict:
        """
        Execute the complete AI-native allocation pipeline
        Following the blueprint's unified ML approach
        
        Returns:
            Dict: Complete allocation results with ML insights
        """
        if not self.ml_model_trained:
            print("🔄 ML model not trained, training now...")
            self.train_ml_ranking_model()
        
        print("🚀 Running AI-native allocation pipeline...")
        
        # Step 1: Generate ML-powered preference lists
        candidate_prefs_dict, internship_prefs_dict = self.ml_ranking_engine.generate_ml_preference_lists(
            self.candidates_processed, 
            self.internships_processed
        )
        
        # Convert ML rankings to ordered preference lists for stable matching
        candidate_preferences = {}
        internship_preferences = {}
        
        # Convert candidate preferences from rankings to ordered lists
        for candidate_id, rankings in candidate_prefs_dict.items():
            # Sort internships by rank (ascending) to get preference order
            sorted_prefs = sorted(rankings.items(), key=lambda x: x[1])
            candidate_preferences[candidate_id] = [internship_id for internship_id, _ in sorted_prefs]
        
        # Convert internship preferences from rankings to ordered lists  
        for internship_id, rankings in internship_prefs_dict.items():
            # Sort candidates by rank (ascending) to get preference order
            sorted_prefs = sorted(rankings.items(), key=lambda x: x[1])
            internship_preferences[internship_id] = [candidate_id for candidate_id, _ in sorted_prefs]
        
        # Step 2: Run stable matching with ML scores
        from matching_algorithm import StableMatchingAlgorithm
        matcher = StableMatchingAlgorithm()
        
        matching_results = matcher.run_stable_matching(
            candidate_preferences,
            internship_preferences,
            self.candidates_processed,
            apply_quotas=True
        )
        
        # Step 3: Enhanced analysis with ML insights
        ml_insights = self.generate_ml_insights(matching_results)
        
        # Combine results
        final_results = {
            **matching_results,
            'ml_insights': ml_insights,
            'ai_native_processing': True,
            'processing_timestamp': datetime.now().isoformat(),
            'model_performance': {
                'candidates_ai_processed': sum(1 for c in self.candidates_processed if c.get('ai_processed', False)),
                'internships_ai_processed': sum(1 for i in self.internships_processed if i.get('ai_processed', False)),
                'ml_model_trained': self.ml_model_trained
            }
        }
        
        return final_results
    
    def generate_ml_insights(self, matching_results: Dict) -> Dict:
        """
        Generate ML-powered insights from allocation results
        
        Args:
            matching_results: Results from stable matching
            
        Returns:
            Dict: ML insights and analytics
        """
        insights = {
            'feature_importance': {},
            'skill_gap_analysis': {},
            'sector_preferences': {},
            'ml_confidence_scores': {}
        }
        
        # Feature importance from trained model
        if hasattr(self.ml_ranking_engine.model, 'feature_importances_'):
            feature_importance = dict(zip(
                self.ml_ranking_engine.feature_columns,
                self.ml_ranking_engine.model.feature_importances_
            ))
            
            # Top 10 most important features
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            insights['feature_importance'] = dict(sorted_features[:10])
        
        # Skill gap analysis
        all_candidate_skills = set()
        all_required_skills = set()
        
        for candidate in self.candidates_processed:
            all_candidate_skills.update(candidate.get('skills', []))
        
        for internship in self.internships_processed:
            all_required_skills.update(internship.get('required_skills', []))
        
        skill_gaps = all_required_skills - all_candidate_skills
        skill_surplus = all_candidate_skills - all_required_skills
        
        insights['skill_gap_analysis'] = {
            'missing_skills': list(skill_gaps)[:10],  # Top 10 gaps
            'surplus_skills': list(skill_surplus)[:10],  # Top 10 surplus
            'skill_match_rate': len(all_candidate_skills & all_required_skills) / len(all_required_skills) if all_required_skills else 0
        }
        
        # Sector preference analysis
        sector_matches = {}
        matches = matching_results.get('matches', {})
        
        for candidate_id, internship_id in matches.items():
            # Find internship sector
            internship = next((i for i in self.internships_processed if i['internship_id'] == internship_id), None)
            if internship:
                sector = internship.get('sector', 'Unknown')
                sector_matches[sector] = sector_matches.get(sector, 0) + 1
        
        insights['sector_preferences'] = sector_matches
        
        # ML confidence scores for matches
        confidence_scores = []
        for candidate_id, internship_id in matches.items():
            candidate = next((c for c in self.candidates_processed if c['candidate_id'] == candidate_id), None)
            internship = next((i for i in self.internships_processed if i['internship_id'] == internship_id), None)
            
            if candidate and internship:
                score = self.ml_ranking_engine.predict_suitability_score(candidate, internship)
                confidence_scores.append(score)
        
        insights['ml_confidence_scores'] = {
            'average_confidence': np.mean(confidence_scores) if confidence_scores else 0,
            'min_confidence': np.min(confidence_scores) if confidence_scores else 0,
            'max_confidence': np.max(confidence_scores) if confidence_scores else 0,
            'confidence_distribution': {
                'high_confidence': sum(1 for s in confidence_scores if s > 0.7),
                'medium_confidence': sum(1 for s in confidence_scores if 0.4 <= s <= 0.7),
                'low_confidence': sum(1 for s in confidence_scores if s < 0.4)
            }
        }
        
        return insights
    
    def export_ai_results(self, results: Dict, output_file: str = None):
        """
        Export AI-native results with enhanced analytics
        
        Args:
            results: Complete allocation results
            output_file: Output filename
        """
        if not output_file:
            output_file = f"ai_allocation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Prepare enhanced export data
        export_data = []
        matches = results.get('matches', {})
        
        for candidate_id, internship_id in matches.items():
            candidate = next((c for c in self.candidates_processed if c['candidate_id'] == candidate_id), None)
            internship = next((i for i in self.internships_processed if i['internship_id'] == internship_id), None)
            
            if candidate and internship:
                # Calculate ML suitability score
                ml_score = self.ml_ranking_engine.predict_suitability_score(candidate, internship)
                
                export_data.append({
                    'candidate_id': candidate_id,
                    'candidate_name': candidate.get('name', 'Unknown'),
                    'age': candidate.get('age', 'N/A'),
                    'social_category': candidate.get('social_category', 'General'),
                    'is_rural': candidate.get('is_rural', False),
                    'candidate_skills_count': len(candidate.get('skills', [])),
                    'internship_id': internship_id,
                    'company_name': internship.get('company_name', 'Unknown'),
                    'job_title': internship.get('job_title', 'Unknown'),
                    'sector': internship.get('sector', 'Unknown'),
                    'location': internship.get('location', 'Unknown'),
                    'required_skills_count': len(internship.get('required_skills', [])),
                    'ml_suitability_score': round(ml_score, 4),
                    'ai_processed_candidate': candidate.get('ai_processed', False),
                    'ai_processed_internship': internship.get('ai_processed', False)
                })
        
        # Export to CSV
        df = pd.DataFrame(export_data)
        df.to_csv(output_file, index=False)
        
        print(f"✅ AI-native results exported to {output_file}")
        print(f"📊 Enhanced with ML suitability scores and AI processing flags")
        
        return output_file


# Test the unified AI engine
if __name__ == "__main__":
    print("=== Testing Unified AI-Native PMIS Engine ===")
    
    # Initialize the unified engine
    ai_engine = UnifiedAIEngine()
    
    # Process data with AI-native pipeline
    candidates = ai_engine.process_candidate_data_ai_native("data/candidates.csv")
    internships = ai_engine.process_internship_data_ai_native("data/internships.csv")
    
    if candidates and internships:
        # Run complete AI-native allocation
        results = ai_engine.run_ai_native_allocation()
        
        print("\n🎯 AI-Native Allocation Results:")
        print(f"   Total matches: {len(results.get('matches', {}))}")
        print(f"   Quota compliance: {results.get('quota_stats', {}).get('meets_rural_quota', False)}")
        print(f"   ML model trained: {results.get('model_performance', {}).get('ml_model_trained', False)}")
        
        # Display ML insights
        ml_insights = results.get('ml_insights', {})
        if ml_insights.get('feature_importance'):
            print(f"\n🔍 Top ML Features:")
            for feature, importance in list(ml_insights['feature_importance'].items())[:5]:
                print(f"   {feature}: {importance:.4f}")
        
        if ml_insights.get('ml_confidence_scores'):
            conf_scores = ml_insights['ml_confidence_scores']
            print(f"\n📊 ML Confidence Analysis:")
            print(f"   Average confidence: {conf_scores.get('average_confidence', 0):.4f}")
            print(f"   High confidence matches: {conf_scores.get('confidence_distribution', {}).get('high_confidence', 0)}")
        
        # Export results
        output_file = ai_engine.export_ai_results(results)
        print(f"\n✅ Complete AI-native allocation pipeline executed successfully!")
    else:
        print("❌ Failed to process data files")

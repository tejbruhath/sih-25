"""
Custom Named Entity Recognition Model for PMIS-AI System
Implements spaCy-based NER for skill, education, and experience extraction
"""

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
import json
import os
from typing import List, Dict, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class CustomNERModel:
    def __init__(self, model_name="en_core_web_sm"):
        """
        Initialize custom NER model for resume parsing
        
        Args:
            model_name: Base spaCy model to extend
        """
        self.nlp = None
        self.model_name = model_name
        self.custom_labels = ["SKILL", "UNIVERSITY", "DEGREE", "JOB_TITLE", "COMPANY", "EXPERIENCE"]
        self.load_base_model()
        
    def load_base_model(self):
        """Load base spaCy model and add custom NER component"""
        try:
            self.nlp = spacy.load(self.model_name)
            
            # Add custom labels to NER component
            ner = self.nlp.get_pipe("ner")
            for label in self.custom_labels:
                ner.add_label(label)
                
            print(f"✅ Base model '{self.model_name}' loaded with custom NER labels")
        except OSError:
            print(f"❌ Model '{self.model_name}' not found. Install with: python -m spacy download {self.model_name}")
            self.nlp = None
    
    def create_training_data(self) -> List[Tuple[str, Dict]]:
        """
        Create comprehensive training data for custom NER model
        This would typically be done with a tool like doccano in production
        
        Returns:
            List[Tuple[str, Dict]]: Training examples with annotations
        """
        training_data = [
            # Technology/Programming Skills
            ("I have experience with Python, Java, and machine learning algorithms.", {
                "entities": [(25, 31, "SKILL"), (33, 37, "SKILL"), (43, 70, "SKILL")]
            }),
            ("Proficient in React, Node.js, and database management systems.", {
                "entities": [(14, 19, "SKILL"), (21, 28, "SKILL"), (34, 62, "SKILL")]
            }),
            ("Worked with TensorFlow, PyTorch for deep learning projects.", {
                "entities": [(12, 22, "SKILL"), (24, 31, "SKILL"), (36, 49, "SKILL")]
            }),
            ("Expert in data science, statistical analysis, and visualization.", {
                "entities": [(10, 22, "SKILL"), (24, 44, "SKILL"), (50, 63, "SKILL")]
            }),
            
            # Education
            ("B.Tech Computer Science from IIT Delhi, graduated in 2024.", {
                "entities": [(0, 23, "DEGREE"), (29, 38, "UNIVERSITY")]
            }),
            ("Master of Business Administration from Harvard Business School.", {
                "entities": [(0, 36, "DEGREE"), (42, 63, "UNIVERSITY")]
            }),
            ("PhD in Environmental Engineering, University of California Berkeley.", {
                "entities": [(0, 32, "DEGREE"), (34, 68, "UNIVERSITY")]
            }),
            ("Bachelor of Commerce from Delhi University with 85% marks.", {
                "entities": [(0, 20, "DEGREE"), (26, 42, "UNIVERSITY")]
            }),
            
            # Job Titles and Companies
            ("Software Engineer at Google, leading AI research initiatives.", {
                "entities": [(0, 17, "JOB_TITLE"), (21, 27, "COMPANY")]
            }),
            ("Data Scientist at Microsoft, working on machine learning models.", {
                "entities": [(0, 14, "JOB_TITLE"), (18, 27, "COMPANY"), (40, 65, "SKILL")]
            }),
            ("Financial Analyst at Goldman Sachs, specialized in risk management.", {
                "entities": [(0, 17, "JOB_TITLE"), (21, 34, "COMPANY"), (50, 67, "SKILL")]
            }),
            ("Product Manager at Amazon, responsible for e-commerce platform.", {
                "entities": [(0, 15, "JOB_TITLE"), (19, 25, "COMPANY")]
            }),
            
            # Experience
            ("3 years of experience in software development and project management.", {
                "entities": [(0, 21, "EXPERIENCE"), (25, 45, "SKILL"), (50, 68, "SKILL")]
            }),
            ("Over 5 years working in financial services and investment banking.", {
                "entities": [(0, 24, "EXPERIENCE"), (28, 46, "SKILL"), (51, 67, "SKILL")]
            }),
            ("2+ years of hands-on experience with cloud computing and DevOps.", {
                "entities": [(0, 35, "EXPERIENCE"), (41, 56, "SKILL"), (61, 67, "SKILL")]
            }),
            
            # Finance-specific
            ("CFA Level 2 candidate with expertise in portfolio optimization.", {
                "entities": [(0, 15, "SKILL"), (37, 62, "SKILL")]
            }),
            ("Bloomberg Terminal certified, experienced in equity research.", {
                "entities": [(0, 28, "SKILL"), (46, 61, "SKILL")]
            }),
            ("Risk management specialist with derivatives trading experience.", {
                "entities": [(0, 26, "SKILL"), (32, 51, "SKILL")]
            }),
            
            # Environmental/Energy
            ("Environmental impact assessment and renewable energy systems.", {
                "entities": [(0, 31, "SKILL"), (36, 61, "SKILL")]
            }),
            ("Solar panel design and wind energy optimization expertise.", {
                "entities": [(0, 18, "SKILL"), (23, 47, "SKILL")]
            }),
            ("GIS mapping and remote sensing for environmental monitoring.", {
                "entities": [(0, 11, "SKILL"), (16, 30, "SKILL"), (35, 59, "SKILL")]
            }),
            
            # Healthcare
            ("Medical data analysis and healthcare informatics background.", {
                "entities": [(0, 21, "SKILL"), (26, 48, "SKILL")]
            }),
            ("Clinical research experience with biostatistics knowledge.", {
                "entities": [(0, 28, "EXPERIENCE"), (34, 58, "SKILL")]
            }),
            
            # Marketing
            ("Digital marketing campaigns and SEO optimization strategies.", {
                "entities": [(0, 26, "SKILL"), (31, 59, "SKILL")]
            }),
            ("Social media management and content creation for brands.", {
                "entities": [(0, 23, "SKILL"), (28, 44, "SKILL")]
            }),
            
            # Complex sentences with multiple entities
            ("Senior Software Engineer at TechCorp with 5 years Python experience, B.Tech from IIT Bombay.", {
                "entities": [(0, 24, "JOB_TITLE"), (28, 36, "COMPANY"), (42, 65, "EXPERIENCE"), 
                           (59, 65, "SKILL"), (78, 84, "DEGREE"), (90, 100, "UNIVERSITY")]
            }),
            ("Data Science Manager at StartupXYZ, PhD Machine Learning from Stanford, expert in TensorFlow.", {
                "entities": [(0, 20, "JOB_TITLE"), (24, 34, "COMPANY"), (36, 56, "DEGREE"), 
                           (62, 70, "UNIVERSITY"), (81, 91, "SKILL")]
            })
        ]
        
        return training_data
    
    def train_custom_ner(self, training_data: List[Tuple[str, Dict]], n_iter: int = 30):
        """
        Train the custom NER model
        
        Args:
            training_data: List of training examples
            n_iter: Number of training iterations
        """
        if not self.nlp:
            print("❌ Base model not loaded!")
            return
        
        print(f"🔄 Training custom NER model with {len(training_data)} examples...")
        
        # Get the NER component
        ner = self.nlp.get_pipe("ner")
        
        # Disable other components during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        
        with self.nlp.disable_pipes(*other_pipes):
            # Initialize the model
            self.nlp.initialize()
            
            # Training loop
            for iteration in range(n_iter):
                random.shuffle(training_data)
                losses = {}
                
                # Create training examples
                examples = []
                for text, annotations in training_data:
                    doc = self.nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    examples.append(example)
                
                # Update the model
                self.nlp.update(examples, losses=losses, drop=0.5)
                
                if iteration % 10 == 0:
                    print(f"Iteration {iteration}, Losses: {losses}")
        
        print("✅ Custom NER model training completed!")
    
    def extract_entities_with_custom_ner(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities using the trained custom NER model
        
        Args:
            text: Input text (resume or job description)
            
        Returns:
            Dict: Extracted entities by category
        """
        if not self.nlp:
            return {"skills": [], "universities": [], "degrees": [], "job_titles": [], "companies": [], "experience": []}
        
        doc = self.nlp(text)
        
        entities = {
            "skills": [],
            "universities": [],
            "degrees": [],
            "job_titles": [],
            "companies": [],
            "experience": []
        }
        
        for ent in doc.ents:
            entity_text = ent.text.strip()
            if ent.label_ == "SKILL":
                entities["skills"].append(entity_text)
            elif ent.label_ == "UNIVERSITY":
                entities["universities"].append(entity_text)
            elif ent.label_ == "DEGREE":
                entities["degrees"].append(entity_text)
            elif ent.label_ == "JOB_TITLE":
                entities["job_titles"].append(entity_text)
            elif ent.label_ == "COMPANY":
                entities["companies"].append(entity_text)
            elif ent.label_ == "EXPERIENCE":
                entities["experience"].append(entity_text)
        
        # Remove duplicates while preserving order
        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))
        
        return entities
    
    def evaluate_model(self, test_data: List[Tuple[str, Dict]]) -> Dict[str, float]:
        """
        Evaluate the custom NER model performance
        
        Args:
            test_data: Test examples
            
        Returns:
            Dict: Evaluation metrics
        """
        if not self.nlp:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
        print("🔄 Evaluating custom NER model...")
        
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for text, annotations in test_data:
            # Get predictions
            doc = self.nlp(text)
            predicted_entities = set((ent.start_char, ent.end_char, ent.label_) for ent in doc.ents)
            
            # Get ground truth
            true_entities = set((start, end, label) for start, end, label in annotations["entities"])
            
            # Calculate metrics
            true_positives += len(predicted_entities.intersection(true_entities))
            false_positives += len(predicted_entities - true_entities)
            false_negatives += len(true_entities - predicted_entities)
        
        # Calculate precision, recall, F1
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives
        }
        
        print(f"📊 NER Model Evaluation:")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall: {recall:.4f}")
        print(f"   F1-Score: {f1:.4f}")
        
        return metrics
    
    def save_model(self, output_dir: str):
        """Save the trained custom NER model"""
        if not self.nlp:
            print("❌ No model to save!")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        self.nlp.to_disk(output_dir)
        print(f"✅ Custom NER model saved to {output_dir}")
    
    def load_model(self, model_dir: str):
        """Load a saved custom NER model"""
        try:
            self.nlp = spacy.load(model_dir)
            print(f"✅ Custom NER model loaded from {model_dir}")
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
    
    def create_enhanced_resume_parser(self, text: str) -> Dict:
        """
        Enhanced resume parsing using custom NER + rule-based extraction
        
        Args:
            text: Resume text
            
        Returns:
            Dict: Comprehensive parsed information
        """
        # Extract entities with custom NER
        ner_entities = self.extract_entities_with_custom_ner(text)
        
        # Additional rule-based extraction for robustness
        additional_skills = self._extract_additional_skills(text)
        experience_years = self._extract_experience_years(text)
        
        # Combine NER and rule-based results
        all_skills = list(set(ner_entities["skills"] + additional_skills))
        
        return {
            "skills": all_skills,
            "universities": ner_entities["universities"],
            "degrees": ner_entities["degrees"],
            "job_titles": ner_entities["job_titles"],
            "companies": ner_entities["companies"],
            "experience_mentions": ner_entities["experience"],
            "experience_years": experience_years,
            "ner_confidence": len(ner_entities["skills"]) / max(1, len(all_skills)),  # Simple confidence metric
            "parsing_method": "custom_ner_enhanced"
        }
    
    def _extract_additional_skills(self, text: str) -> List[str]:
        """Fallback rule-based skill extraction for robustness"""
        additional_skills = []
        text_lower = text.lower()
        
        # Common skill patterns not caught by NER
        skill_patterns = [
            "excel", "powerpoint", "word", "outlook", "sql server", "mysql", "postgresql",
            "javascript", "html", "css", "bootstrap", "jquery", "angular", "vue.js",
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github",
            "agile", "scrum", "kanban", "jira", "confluence", "slack", "trello"
        ]
        
        for skill in skill_patterns:
            if skill in text_lower:
                additional_skills.append(skill)
        
        return additional_skills
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract years of experience using regex patterns"""
        import re
        
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)-\d+\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'experience\s*:?\s*(\d+)\+?\s*years?'
        ]
        
        years_found = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    years = int(match.group(1))
                    years_found.append(years)
                except (ValueError, IndexError):
                    continue
        
        return max(years_found) if years_found else 0


# Test the custom NER model
if __name__ == "__main__":
    print("=== Testing Custom NER Model ===")
    
    # Initialize custom NER model
    ner_model = CustomNERModel()
    
    if ner_model.nlp:
        # Create training data
        training_data = ner_model.create_training_data()
        print(f"📊 Created {len(training_data)} training examples")
        
        # Split data for training and testing
        split_idx = int(0.8 * len(training_data))
        train_data = training_data[:split_idx]
        test_data = training_data[split_idx:]
        
        # Train the model
        ner_model.train_custom_ner(train_data, n_iter=20)
        
        # Evaluate the model
        metrics = ner_model.evaluate_model(test_data)
        
        # Test on sample resume
        sample_resume = """
        John Doe, Software Engineer at Google with 5 years of Python experience.
        B.Tech Computer Science from IIT Delhi. Expert in machine learning,
        TensorFlow, and data science. Previously worked as Data Scientist at Microsoft.
        """
        
        print(f"\n🧪 Testing on sample resume:")
        print(f"Text: {sample_resume}")
        
        entities = ner_model.extract_entities_with_custom_ner(sample_resume)
        print(f"\n📋 Extracted Entities:")
        for category, items in entities.items():
            if items:
                print(f"   {category.upper()}: {items}")
        
        # Enhanced parsing
        enhanced_result = ner_model.create_enhanced_resume_parser(sample_resume)
        print(f"\n🚀 Enhanced Parsing Result:")
        print(f"   Skills: {enhanced_result['skills']}")
        print(f"   Experience Years: {enhanced_result['experience_years']}")
        print(f"   NER Confidence: {enhanced_result['ner_confidence']:.2f}")
    else:
        print("❌ Cannot test without base spaCy model")

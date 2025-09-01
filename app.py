"""
PMIS-AI Engine Flask Application
Main web server for the AI-powered internship matching system
"""

from flask import Flask, request, jsonify, render_template, send_file
import os
import sys
import json
import pandas as pd
from datetime import datetime
import traceback

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from resume_parser import ResumeParser
from ranking_engine import RankingEngine
from matching_algorithm import StableMatchingAlgorithm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pmis-ai-engine-2025'

# Initialize components
parser = ResumeParser()
engine = RankingEngine()
matcher = StableMatchingAlgorithm()

# Global variables for storing processed data
processed_candidates = []
processed_internships = []
allocation_results = {}

@app.route('/')
def home():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API health check"""
    return jsonify({
        'status': 'active',
        'message': 'PMIS-AI Engine is running',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'resume_parser': 'ready',
            'ranking_engine': 'ready',
            'matching_algorithm': 'ready'
        }
    })

@app.route('/api/load_data', methods=['POST'])
def load_data():
    """Load and process candidate and internship data"""
    try:
        global processed_candidates, processed_internships
        
        print("🔄 Loading and processing data...")
        
        # Load raw data
        candidates, internships = matcher.load_data(
            'data/candidates.csv',
            'data/internships.csv'
        )
        
        if not candidates or not internships:
            return jsonify({
                'success': False,
                'error': 'Failed to load data files'
            }), 400
        
        # Process candidate resumes
        processed_candidates = []
        for candidate in candidates:
            resume_file = f"data/{candidate['resume_filename']}"
            
            if os.path.exists(resume_file):
                # Parse resume
                parsed_resume = parser.parse_resume(resume_file)
                
                # Combine candidate info with parsed resume data
                processed_candidate = {
                    **candidate,
                    'text': parsed_resume['text'],
                    'skills': parsed_resume['skills'],
                    'education': parsed_resume['education'],
                    'experience_years': parsed_resume['experience_years'],
                    'parsing_success': parsed_resume['parsing_success']
                }
                processed_candidates.append(processed_candidate)
            else:
                print(f"⚠️ Resume file not found: {resume_file}")
                # Add candidate with empty resume data
                processed_candidates.append({
                    **candidate,
                    'text': '',
                    'skills': [],
                    'education': [],
                    'experience_years': 0,
                    'parsing_success': False
                })
        
        # Process internship descriptions
        processed_internships = []
        for internship in internships:
            desc_file = f"data/{internship['description_filename']}"
            
            if os.path.exists(desc_file):
                # Read job description
                with open(desc_file, 'r', encoding='utf-8') as f:
                    job_text = f.read()
                
                # Extract required skills from job description
                job_skills = parser.extract_skills(job_text)
                
                processed_internship = {
                    **internship,
                    'text': job_text,
                    'required_skills': job_skills
                }
                processed_internships.append(processed_internship)
            else:
                print(f"⚠️ Job description file not found: {desc_file}")
                processed_internships.append({
                    **internship,
                    'text': '',
                    'required_skills': []
                })
        
        return jsonify({
            'success': True,
            'message': 'Data loaded and processed successfully',
            'stats': {
                'candidates_loaded': len(processed_candidates),
                'internships_loaded': len(processed_internships),
                'resumes_parsed': sum(1 for c in processed_candidates if c['parsing_success']),
                'total_skills_found': sum(len(c['skills']) for c in processed_candidates)
            }
        })
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/run_allocation', methods=['POST'])
def run_allocation():
    """Execute the complete allocation algorithm"""
    try:
        global allocation_results
        
        if not processed_candidates or not processed_internships:
            return jsonify({
                'success': False,
                'error': 'Data not loaded. Please load data first.'
            }), 400
        
        print("🚀 Starting allocation process...")
        
        # Load transformer model if not already loaded
        if not engine.model_loaded:
            engine.load_transformer_model()
        
        # Generate preference lists
        candidate_preferences, internship_preferences = engine.generate_preference_lists(
            processed_candidates, processed_internships
        )
        
        # Run stable matching algorithm
        matching_results = matcher.run_stable_matching(
            candidate_preferences, 
            internship_preferences, 
            processed_candidates,
            apply_quotas=True
        )
        
        # Verify stability
        is_stable = matcher.verify_stability(
            matching_results['matches'],
            candidate_preferences,
            internship_preferences
        )
        
        # Export results
        output_file = f"allocation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        matcher.export_results(matching_results, processed_candidates, processed_internships, output_file)
        
        # Store results globally
        allocation_results = {
            **matching_results,
            'is_stable': is_stable,
            'output_file': output_file,
            'timestamp': datetime.now().isoformat()
        }
        
        # Prepare response data
        response_data = {
            'success': True,
            'message': 'Allocation completed successfully',
            'results': {
                'total_matches': len(matching_results['matches']),
                'quota_stats': matching_results['quota_stats'],
                'is_stable': is_stable,
                'iterations': matching_results['iterations'],
                'output_file': output_file
            },
            'matches': matching_results['matches']
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in allocation: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_results')
def get_results():
    """Get the latest allocation results"""
    if not allocation_results:
        return jsonify({
            'success': False,
            'error': 'No allocation results available'
        }), 404
    
    return jsonify({
        'success': True,
        'results': allocation_results
    })

@app.route('/api/download_results')
def download_results():
    """Download allocation results as CSV"""
    if not allocation_results or 'output_file' not in allocation_results:
        return jsonify({
            'success': False,
            'error': 'No results file available'
        }), 404
    
    output_file = allocation_results['output_file']
    if os.path.exists(output_file):
        return send_file(output_file, as_attachment=True)
    else:
        return jsonify({
            'success': False,
            'error': 'Results file not found'
        }), 404

@app.route('/api/blockchain_hash', methods=['POST'])
def generate_blockchain_hash():
    """Generate blockchain hash for allocation results"""
    try:
        if not allocation_results:
            return jsonify({
                'success': False,
                'error': 'No allocation results to hash'
            }), 400
        
        import hashlib
        import json
        
        # Create hash of the allocation results
        hash_data = {
            'matches': allocation_results['matches'],
            'quota_stats': allocation_results['quota_stats'],
            'timestamp': allocation_results['timestamp'],
            'total_matches': len(allocation_results['matches'])
        }
        
        # Convert to JSON string and hash
        data_string = json.dumps(hash_data, sort_keys=True).encode('utf-8')
        allocation_hash = hashlib.sha256(data_string).hexdigest()
        
        # Store hash in results
        allocation_results['blockchain_hash'] = allocation_hash
        
        return jsonify({
            'success': True,
            'message': 'Blockchain hash generated successfully',
            'hash': allocation_hash,
            'hash_data': hash_data
        })
        
    except Exception as e:
        print(f"❌ Error generating hash: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting PMIS-AI Engine...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔗 API Status: http://localhost:5000/api/status")
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

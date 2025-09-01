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

from src.resume_parser import ResumeParser
from src.ranking_engine import RankingEngine
from src.matching_algorithm import StableMatchingAlgorithm
from src.blockchain_layer import BlockchainTrustLayer
from src.unified_ai_engine import UnifiedAIEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pmis-ai-engine-2025'

# Initialize components
parser = ResumeParser()
engine = RankingEngine()
matcher = StableMatchingAlgorithm()
ai_engine = UnifiedAIEngine()  # New unified AI-native engine

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
    """Load and process candidate and internship data using AI-native pipeline"""
    global processed_candidates, processed_internships
    
    try:
        # Use AI-native data processing pipeline
        candidates_file = "data/candidates.csv"
        internships_file = "data/internships.csv"
        
        if not os.path.exists(candidates_file) or not os.path.exists(internships_file):
            return jsonify({
                'success': False,
                'message': 'Data files not found. Please ensure candidates.csv and internships.csv exist in data/ directory'
            })
        
        # Process data with AI-native pipeline
        processed_candidates = ai_engine.process_candidate_data_ai_native(candidates_file)
        processed_internships = ai_engine.process_internship_data_ai_native(internships_file)
        
        # Calculate AI processing statistics
        ai_candidates = sum(1 for c in processed_candidates if c.get('ai_processed', False))
        ai_internships = sum(1 for i in processed_internships if i.get('ai_processed', False))
        
        return jsonify({
            'success': True,
            'message': f'AI-native data loaded: {len(processed_candidates)} candidates, {len(processed_internships)} internships',
            'stats': {
                'candidates_loaded': len(processed_candidates),
                'internships_loaded': len(processed_internships),
                'resumes_parsed': ai_candidates,
                'total_skills_found': sum(len(c.get('skills', [])) for c in processed_candidates)
            },
            'ai_stats': {
                'candidates_ai_processed': ai_candidates,
                'internships_ai_processed': ai_internships,
                'ai_processing_rate_candidates': round(ai_candidates/len(processed_candidates)*100, 1) if processed_candidates else 0,
                'ai_processing_rate_internships': round(ai_internships/len(processed_internships)*100, 1) if processed_internships else 0
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
    """Run the complete AI-native allocation algorithm"""
    global processed_candidates, processed_internships, allocation_results
    
    try:
        if not processed_candidates or not processed_internships:
            return jsonify({
                'success': False,
                'message': 'Please load candidate and internship data first'
            })
        
        # Use unified AI-native engine for allocation
        results = ai_engine.run_ai_native_allocation()
        allocation_results = results
        
        # Extract ML insights for response
        ml_insights = results.get('ml_insights', {})
        feature_importance = ml_insights.get('feature_importance', {})
        confidence_scores = ml_insights.get('ml_confidence_scores', {})
        
        return jsonify({
            'success': True,
            'message': 'AI-native allocation completed successfully',
            'results': {
                'total_matches': len(results['matches']),
                'quota_compliance': results['quota_stats']['meets_rural_quota'],
                'rural_percentage': results['quota_stats']['rural_percentage'],
                'iterations': results['iterations'],
                'ai_native_processing': results.get('ai_native_processing', True),
                'ml_model_trained': results.get('model_performance', {}).get('ml_model_trained', False),
                'average_confidence': confidence_scores.get('average_confidence', 0),
                'top_features': list(feature_importance.keys())[:5] if feature_importance else [],
                'candidates_ai_processed': results.get('model_performance', {}).get('candidates_ai_processed', 0),
                'internships_ai_processed': results.get('model_performance', {}).get('internships_ai_processed', 0)
            }
        })
        
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

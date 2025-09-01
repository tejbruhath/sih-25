"""
PMIS-AI Smart Allocation Engine - Web Application
================================================

Flask web application providing RESTful API and dashboard interface
for the PM Internship Scheme AI-powered allocation system.

Features:
- RESTful API endpoints for allocation operations
- Simple web dashboard for visualization
- Real-time allocation processing
- Results export and download
- System status monitoring

Author: PMIS-AI Team
Created: 2025-01-01
Last Modified: 2025-01-01
"""

from flask import Flask, request, jsonify, render_template, send_file
import json
import os
from datetime import datetime
import traceback
from dotenv import load_dotenv
from matching_algorithm import StableMatchingEngine

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configure Flask from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'pmis-ai-hackathon-fallback-key')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'

# Initialize the matching engine
matching_engine = StableMatchingEngine()

@app.route('/')
def home():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """Get system status and configuration."""
    try:
        # Check if data files exist
        candidates_exists = os.path.exists('data/candidates.csv')
        internships_exists = os.path.exists('data/internships.csv')
        
        # Count files
        candidate_resumes = len([f for f in os.listdir('data/') if f.startswith('candidate') and f.endswith('.txt')])
        job_descriptions = len([f for f in os.listdir('data/') if f.startswith('job') and f.endswith('.txt')])
        
        return jsonify({
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'data_status': {
                'candidates_file': candidates_exists,
                'internships_file': internships_exists,
                'candidate_resumes': candidate_resumes,
                'job_descriptions': job_descriptions
            },
            'system_info': {
                'algorithm': 'Gale-Shapley Stable Matching',
                'ai_model': 'Sentence Transformers (all-MiniLM-L6-v2)',
                'version': '1.0.0'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run_allocation', methods=['POST'])
def run_allocation():
    """Execute the complete allocation algorithm."""
    try:
        print(f"\\n{'='*60}")
        print("🚀 ALLOCATION REQUEST RECEIVED")
        print(f"{'='*60}")
        
        # Check if required files exist
        if not os.path.exists('data/candidates.csv'):
            return jsonify({'error': 'Candidates data file not found'}), 400
        
        if not os.path.exists('data/internships.csv'):
            return jsonify({'error': 'Internships data file not found'}), 400
        
        # Run the allocation
        results = matching_engine.run_complete_allocation(
            'data/candidates.csv',
            'data/internships.csv'
        )
        
        # Export results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f'data/allocation_results_{timestamp}.json'
        matching_engine.export_results(results, results_file)
        
        # Prepare response data
        response_data = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'allocation_summary': results['allocation_summary'],
            'final_matches': results['final_matches'],
            'results_file': results_file
        }
        
        print(f"\\n✅ ALLOCATION COMPLETED SUCCESSFULLY")
        print(f"📊 Results: {results['allocation_summary']['total_placed']} candidates placed")
        print(f"📁 Results saved to: {results_file}")
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Allocation failed: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

@app.route('/api/allocation_history')
def allocation_history():
    """Get history of previous allocations."""
    try:
        history = []
        
        # Find all allocation result files
        for filename in os.listdir('data/'):
            if filename.startswith('allocation_results_') and filename.endswith('.json'):
                file_path = f'data/{filename}'
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        history.append({
                            'filename': filename,
                            'timestamp': data.get('timestamp', 'Unknown'),
                            'total_placed': len([c for candidates in data['final_allocation'].values() for c in candidates]),
                            'algorithm': data.get('algorithm', 'Unknown')
                        })
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'history': history,
            'total_runs': len(history)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_results/<filename>')
def download_results(filename):
    """Download allocation results file."""
    try:
        file_path = f'data/{filename}'
        if os.path.exists(file_path) and filename.endswith('.json'):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/candidates')
def get_candidates():
    """Get list of all candidates."""
    try:
        import pandas as pd
        candidates_df = pd.read_csv('data/candidates.csv')
        return jsonify({
            'candidates': candidates_df.to_dict('records'),
            'total': len(candidates_df)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/internships')
def get_internships():
    """Get list of all internships."""
    try:
        import pandas as pd
        internships_df = pd.read_csv('data/internships.csv')
        return jsonify({
            'internships': internships_df.to_dict('records'),
            'total': len(internships_df),
            'total_capacity': internships_df['capacity'].sum()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🌟 Starting PMIS-AI Smart Allocation Engine Web Server...")
    print("🔗 Dashboard will be available at: http://localhost:8080")
    print("📖 API endpoints:")
    print("   GET  /api/status - System status")
    print("   POST /api/run_allocation - Execute allocation")
    print("   GET  /api/allocation_history - Previous runs")
    print("   GET  /api/candidates - List candidates")
    print("   GET  /api/internships - List internships")
    print("\\n🚀 Ready to process allocations!")
    
    # Get configuration from environment
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '8080'))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)

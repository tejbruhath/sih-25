from flask import Flask, jsonify, render_template, request, flash, redirect, url_for
from matching_algorithm import MatchingAlgorithm
import hashlib
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Initialize the matching algorithm
matcher = MatchingAlgorithm()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS_CSV = {'csv'}
ALLOWED_EXTENSIONS_RESUME = {'txt', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'resumes'), exist_ok=True)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/test')
def test():
    """Test route"""
    return "Test route working!"

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    """Handle file uploads"""
    if request.method == 'POST':
        # Check if files were uploaded
        if 'candidates_file' not in request.files or 'internships_file' not in request.files:
            flash('Please upload both candidates.csv and internships.csv files', 'error')
            return redirect(request.url)
        
        candidates_file = request.files['candidates_file']
        internships_file = request.files['internships_file']
        resume_files = request.files.getlist('resume_files')
        
        # Check if files are selected
        if candidates_file.filename == '' or internships_file.filename == '':
            flash('Please select files to upload', 'error')
            return redirect(request.url)
        
        # Validate file types
        if not allowed_file(candidates_file.filename, ALLOWED_EXTENSIONS_CSV):
            flash('Candidates file must be a CSV file', 'error')
            return redirect(request.url)
        
        if not allowed_file(internships_file.filename, ALLOWED_EXTENSIONS_CSV):
            flash('Internships file must be a CSV file', 'error')
            return redirect(request.url)
        
        try:
            # Save uploaded files
            candidates_path = os.path.join(app.config['UPLOAD_FOLDER'], 'candidates.csv')
            internships_path = os.path.join(app.config['UPLOAD_FOLDER'], 'internships.csv')
            
            candidates_file.save(candidates_path)
            internships_file.save(internships_path)
            
            # Save resume files
            resume_paths = []
            for resume_file in resume_files:
                if resume_file.filename != '':
                    if allowed_file(resume_file.filename, ALLOWED_EXTENSIONS_RESUME):
                        filename = secure_filename(resume_file.filename)
                        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', filename)
                        resume_file.save(resume_path)
                        resume_paths.append(resume_path)
                    else:
                        flash(f'Resume file {resume_file.filename} has invalid extension. Use .txt or .pdf', 'error')
            
            # Validate CSV files
            try:
                candidates_df = pd.read_csv(candidates_path)
                internships_df = pd.read_csv(internships_path)
                
                # Check required columns
                required_candidate_cols = ['id', 'name', 'email', 'skills', 'experience_years', 'gpa', 'university']
                required_internship_cols = ['id', 'title', 'company', 'description', 'required_skills', 'spots_available', 'salary']
                
                missing_candidate_cols = [col for col in required_candidate_cols if col not in candidates_df.columns]
                missing_internship_cols = [col for col in required_internship_cols if col not in internships_df.columns]
                
                if missing_candidate_cols:
                    flash(f'Missing columns in candidates.csv: {", ".join(missing_candidate_cols)}', 'error')
                    return redirect(request.url)
                
                if missing_internship_cols:
                    flash(f'Missing columns in internships.csv: {", ".join(missing_internship_cols)}', 'error')
                    return redirect(request.url)
                
                flash(f'Files uploaded successfully! Found {len(candidates_df)} candidates and {len(internships_df)} internships', 'success')
                
            except Exception as e:
                flash(f'Error reading CSV files: {str(e)}', 'error')
                return redirect(request.url)
            
        except Exception as e:
            flash(f'Error saving files: {str(e)}', 'error')
            return redirect(request.url)
        
        return redirect(url_for('index'))
    
    return render_template('upload.html')

@app.route('/run_allocation', methods=['POST'])
def run_allocation():
    """
    Main API endpoint that runs the complete allocation process
    """
    try:
        # Check if uploaded files exist, otherwise use default data
        candidates_path = os.path.join(app.config['UPLOAD_FOLDER'], 'candidates.csv')
        internships_path = os.path.join(app.config['UPLOAD_FOLDER'], 'internships.csv')
        
        if not os.path.exists(candidates_path) or not os.path.exists(internships_path):
            # Use default data
            candidates_path = "data/candidates.csv"
            internships_path = "data/internships.csv"
        
        # Run the complete matching process
        results = matcher.run_complete_matching(candidates_path, internships_path)
        
        # Generate blockchain hash of the results
        results_json = json.dumps(results, sort_keys=True, default=str)
        blockchain_hash = hashlib.sha256(results_json.encode()).hexdigest()
        
        # Add timestamp and hash to results
        results['timestamp'] = datetime.now().isoformat()
        results['blockchain_hash'] = blockchain_hash
        
        # Save results to file for audit trail
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"results/allocation_results_{timestamp_str}.json"
        
        with open(results_filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        results['results_file'] = results_filename
        
        return jsonify({
            'success': True,
            'message': 'Allocation completed successfully',
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error during allocation: {str(e)}',
            'data': None
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'PMIS AI Allocation Engine'
    })

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates"""
    try:
        # Check if uploaded file exists, otherwise use default
        candidates_path = os.path.join(app.config['UPLOAD_FOLDER'], 'candidates.csv')
        if not os.path.exists(candidates_path):
            candidates_path = "data/candidates.csv"
        
        candidates_df = pd.read_csv(candidates_path)
        return jsonify({
            'success': True,
            'data': candidates_df.to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading candidates: {str(e)}'
        }), 500

@app.route('/api/internships', methods=['GET'])
def get_internships():
    """Get all internships"""
    try:
        # Check if uploaded file exists, otherwise use default
        internships_path = os.path.join(app.config['UPLOAD_FOLDER'], 'internships.csv')
        if not os.path.exists(internships_path):
            internships_path = "data/internships.csv"
        
        internships_df = pd.read_csv(internships_path)
        return jsonify({
            'success': True,
            'data': internships_df.to_dict('records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading internships: {str(e)}'
        }), 500

@app.route('/api/verify_hash', methods=['POST'])
def verify_hash():
    """Verify blockchain hash of results"""
    try:
        data = request.get_json()
        results_data = data.get('results_data')
        provided_hash = data.get('hash')
        
        if not results_data or not provided_hash:
            return jsonify({
                'success': False,
                'message': 'Missing required data'
            }), 400
        
        # Calculate hash from provided data
        calculated_hash = hashlib.sha256(json.dumps(results_data, sort_keys=True).encode()).hexdigest()
        
        # Verify hash
        is_valid = calculated_hash == provided_hash
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'calculated_hash': calculated_hash,
            'provided_hash': provided_hash
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error verifying hash: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("Starting PMIS AI Allocation Engine...")
    print("Server will be available at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

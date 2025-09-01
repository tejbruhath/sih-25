#!/usr/bin/env python3
"""
Simple Flask App for Testing
"""

from flask import Flask, jsonify, render_template_string
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Simple home page."""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PMIS-AI Engine - Demo</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .btn { background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px; }
            .btn:hover { background: #0056b3; }
            .result { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 PMIS-AI Smart Allocation Engine</h1>
            <p><strong>Status:</strong> ✅ System Online</p>
            
            <h3>🎯 Demo Actions</h3>
            <button class="btn" onclick="runDemo()">⚡ Run Smart Allocation Demo</button>
            <button class="btn" onclick="showStatus()">📊 System Status</button>
            <button class="btn" onclick="showResults()">📋 View Results</button>
            
            <div id="results"></div>
        </div>
        
        <script>
            async function runDemo() {
                document.getElementById('results').innerHTML = '<div class="result">🤖 Running AI allocation...</div>';
                
                try {
                    const response = await fetch('/api/demo_allocation');
                    const data = await response.json();
                    
                    document.getElementById('results').innerHTML = `
                        <div class="result">
                            <h4>✅ Allocation Complete!</h4>
                            <p><strong>Candidates Placed:</strong> ${data.total_placed}</p>
                            <p><strong>Diversity Stats:</strong> ${data.diversity_stats}</p>
                            <p><strong>Blockchain Hash:</strong> ${data.blockchain_hash}</p>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('results').innerHTML = `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function showStatus() {
                try {
                    const response = await fetch('/api/simple_status');
                    const data = await response.json();
                    
                    document.getElementById('results').innerHTML = `
                        <div class="result">
                            <h4>📊 System Status</h4>
                            <p><strong>AI Model:</strong> ${data.ai_model}</p>
                            <p><strong>Algorithm:</strong> ${data.algorithm}</p>
                            <p><strong>Candidates:</strong> ${data.candidates}</p>
                            <p><strong>Internships:</strong> ${data.internships}</p>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('results').innerHTML = `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }
            
            async function showResults() {
                if (!window.confirm('This will run the complete AI allocation. Continue?')) return;
                
                document.getElementById('results').innerHTML = '<div class="result">🚀 Running complete allocation pipeline...</div>';
                
                try {
                    const response = await fetch('/api/run_allocation', { method: 'POST' });
                    const data = await response.json();
                    
                    let html = '<div class="result"><h4>🎯 Final Allocation Results</h4>';
                    
                    for (const [internship, candidates] of Object.entries(data.final_matches)) {
                        if (candidates.length > 0) {
                            html += `<p><strong>${internship}:</strong> ${candidates.join(', ')}</p>`;
                        }
                    }
                    
                    html += `<p><strong>Summary:</strong> ${data.allocation_summary.total_placed} placed, ${(data.allocation_summary.placement_rate * 100).toFixed(1)}% rate</p>`;
                    html += '</div>';
                    
                    document.getElementById('results').innerHTML = html;
                } catch (error) {
                    document.getElementById('results').innerHTML = `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/api/simple_status')
def simple_status():
    """Simple status endpoint."""
    return jsonify({
        'status': 'online',
        'ai_model': 'Sentence Transformers (all-MiniLM-L6-v2)',
        'algorithm': 'Gale-Shapley Stable Matching',
        'candidates': 15,
        'internships': 7
    })

@app.route('/api/demo_allocation')
def demo_allocation():
    """Quick demo allocation."""
    return jsonify({
        'total_placed': 5,
        'diversity_stats': '60% rural, 40% SC/ST (quotas exceeded)',
        'blockchain_hash': 'c8a2f5993330be42...8dbdad8f4390ecf1'
    })

@app.route('/api/run_allocation', methods=['POST'])
def run_allocation():
    """Run the actual allocation."""
    try:
        from matching_algorithm import StableMatchingEngine
        engine = StableMatchingEngine()
        
        results = engine.run_complete_allocation(
            'data/candidates.csv',
            'data/internships.csv'
        )
        
        return jsonify({
            'success': True,
            'final_matches': results['final_matches'],
            'allocation_summary': results['allocation_summary']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌟 Starting PMIS-AI Demo Server...")
    print("🔗 Open: http://localhost:8080")
    print("🚀 Ready!")
    
    app.run(debug=True, host='0.0.0.0', port=8080)

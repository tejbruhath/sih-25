# 🎯 PMIS AI Allocation Engine

An intelligent candidate-internship matching system that uses AI to optimize allocation decisions with blockchain verification.

## 🚀 Features

- **AI-Powered Matching**: Uses transformer models for semantic text similarity
- **Skill-Based Scoring**: Jaccard similarity for skill matching
- **Greedy Allocation**: Optimal candidate-job assignment algorithm
- **Blockchain Verification**: SHA-256 hash generation for result integrity
- **Modern Web Interface**: Beautiful, responsive frontend
- **Audit Trail**: Automatic result logging with timestamps

## 📋 MVP v1.0 Components

### 1. Environment Setup ✅
- Python virtual environment
- Required dependencies installed
- Project structure created

### 2. Mock Data ✅
- `data/candidates.csv` - Sample candidate profiles
- `data/internships.csv` - Sample job descriptions
- `data/candidate1.txt` - Sample resume text
- `data/job1.txt` - Sample job description

### 3. File Parser (`resume_parser.py`) ✅
- PDF and TXT file reading
- Skill extraction from predefined list
- Email, phone, and education extraction
- Structured data output

### 4. AI Scoring Engine (`ranking_engine.py`) ✅
- Text embedding using transformers
- Cosine similarity calculation
- Skill matching with Jaccard similarity
- Comprehensive scoring algorithm

### 5. Matching Algorithm (`matching_algorithm.py`) ✅
- Greedy allocation algorithm
- Score calculation for all candidate-job pairs
- Optimal assignment logic
- Result analysis and reporting

### 6. Flask API (`app.py`) ✅
- `/run_allocation` - Main allocation endpoint
- `/api/health` - Health check
- `/api/candidates` - Get candidates
- `/api/internships` - Get internships
- `/api/verify_hash` - Hash verification

### 7. Frontend (`templates/index.html`) ✅
- Modern, responsive design
- Real-time allocation execution
- Results visualization
- Blockchain hash display

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Start

1. **Clone and Setup**
```bash
# Navigate to project directory
cd sih-25

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2. **Run the Application**
```bash
python app.py
```

3. **Access the Web Interface**
- Open browser and go to: `http://localhost:5000`
- Click "Run AI Allocation" to start the matching process

## 📊 How It Works

### 1. Data Loading
- Reads candidate and internship data from CSV files
- Parses resume files for additional information

### 2. AI Scoring
- Converts text to embeddings using transformer models
- Calculates semantic similarity between candidates and jobs
- Computes skill overlap using Jaccard similarity
- Combines scores with weighted algorithm

### 3. Matching Algorithm
- Sorts all candidate-job pairs by score
- Implements greedy allocation for optimal assignment
- Ensures one candidate per job (respecting job capacity)

### 4. Blockchain Verification
- Generates SHA-256 hash of final results
- Provides audit trail with timestamps
- Enables result integrity verification

## 🎨 API Endpoints

### POST `/run_allocation`
Main endpoint that executes the complete allocation process.

**Response:**
```json
{
  "success": true,
  "message": "Allocation completed successfully",
  "data": {
    "allocations": [...],
    "total_allocations": 5,
    "matching_efficiency": 0.8,
    "blockchain_hash": "abc123...",
    "timestamp": "2025-01-01T12:00:00"
  }
}
```

### GET `/api/health`
Health check endpoint.

### GET `/api/candidates`
Returns all candidate data.

### GET `/api/internships`
Returns all internship data.

### POST `/api/verify_hash`
Verifies blockchain hash integrity.

## 📁 Project Structure

```
sih-25/
├── app.py                 # Main Flask application
├── resume_parser.py       # File parsing and skill extraction
├── ranking_engine.py      # AI scoring and similarity calculation
├── matching_algorithm.py  # Greedy allocation algorithm
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── data/                 # Mock data files
│   ├── candidates.csv
│   ├── internships.csv
│   ├── candidate1.txt
│   └── job1.txt
├── results/              # Allocation results
│   ├── README.md
│   └── allocation_results_*.json
├── uploads/              # User uploaded files
│   ├── .gitkeep
│   ├── candidates.csv
│   ├── internships.csv
│   └── resumes/
├── sample_data/          # Sample data for testing
│   ├── candidates.csv
│   ├── internships.csv
│   └── resumes/
└── templates/            # Frontend templates
    └── index.html
```

## 🔧 Configuration

### Model Configuration
- Default transformer model: `sentence-transformers/all-MiniLM-L6-v2`
- Embedding dimension: 384
- Max text length: 512 tokens

### Scoring Weights
- Text similarity: 60%
- Skill matching: 40%

### File Paths
- Candidates CSV: `data/candidates.csv`
- Internships CSV: `data/internships.csv`
- Results output: `results/allocation_results_YYYYMMDD_HHMMSS.json`

## 🧪 Testing

### Manual Testing
```bash
# Test resume parser
python resume_parser.py

# Test ranking engine
python ranking_engine.py

# Test matching algorithm
python matching_algorithm.py
```

### Web Interface Testing
1. Start the server: `python app.py`
2. Open browser to `http://localhost:5000`
3. Click "Run AI Allocation"
4. Verify results and blockchain hash

## 📈 Performance Metrics

The system tracks several key metrics:
- **Total Allocations**: Number of successful matches
- **Matching Efficiency**: Percentage of candidates placed
- **Score Range**: Min/max matching scores
- **Average Score**: Mean matching quality

## 🔒 Security Features

- **Blockchain Verification**: SHA-256 hash generation
- **Audit Trail**: Timestamped result logging
- **Input Validation**: File format and data validation
- **Error Handling**: Comprehensive exception management
- **Version Control**: Secure .gitignore excludes sensitive data

## 🔧 Version Control & Security

### Git Configuration
- **`.gitignore`**: Excludes result files, uploads, and sensitive data
- **`.gitkeep` files**: Maintains folder structure while excluding content
- **Results Directory**: All allocation results excluded from version control
- **Uploads**: User data excluded for privacy and security

### Security Measures
- **Data Privacy**: User uploads not tracked in git
- **Result Confidentiality**: Allocation results excluded from version control
- **Environment Variables**: Sensitive config excluded
- **Clean Repository**: Only source code and documentation tracked

## 🚀 Future Enhancements

### MVP v2.0 Planned Features
- Advanced NLP for better text understanding
- Machine learning model training on historical data
- Multi-objective optimization algorithms
- Real-time candidate/job updates
- Advanced analytics dashboard
- Email notifications
- API rate limiting and authentication

### Scalability Improvements
- Database integration (PostgreSQL/MongoDB)
- Redis caching for performance
- Microservices architecture
- Docker containerization
- Kubernetes deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the PMIS (Project Management Information System) initiative.

## 📞 Support

For questions or support, please contact the development team.

---

**Built with ❤️ using Python, Flask, Transformers, and modern web technologies**

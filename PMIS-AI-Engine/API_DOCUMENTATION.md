# 📡 PMIS-AI API Documentation

**RESTful API for Smart Allocation Engine**

---

## 📖 **Table of Contents**

- [🚀 Getting Started](#getting-started)
- [🔗 Base Configuration](#base-configuration)
- [📍 API Endpoints](#api-endpoints)
- [💡 Usage Examples](#usage-examples)
- [🚨 Error Handling](#error-handling)
- [🔐 Authentication](#authentication)
- [📊 Response Formats](#response-formats)
- [🧪 Testing the API](#testing-the-api)

---

## 🚀 **Getting Started**

The PMIS-AI API provides programmatic access to all allocation engine features. The API is built with Flask and follows RESTful design principles.

### **Base URL**
```
http://localhost:8080/api
```

### **Content Type**
All requests and responses use JSON format:
```
Content-Type: application/json
```

### **Start the Server**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Start Flask application
python app.py

# Server will start on http://localhost:8080
```

---

## 🔗 **Base Configuration**

### **Environment Variables**
```bash
PORT=8080                    # Server port
SECRET_KEY=your-secret-key   # Flask session key
LOG_LEVEL=INFO              # Logging level
AI_MODEL_NAME=all-MiniLM-L6-v2  # AI model name
```

### **Required Data Files**
```
data/
├── candidates.csv          # Candidate information
├── internships.csv         # Available internships
├── resumes/               # Resume files (PDF/DOCX/TXT)
└── job_descriptions/      # Job description files
```

---

## 📍 **API Endpoints**

### **🩺 1. System Status**

#### **GET /api/status**

**Description**: Get system health, statistics, and configuration

**Request**:
```bash
curl -X GET http://localhost:8080/api/status
```

**Response**:
```json
{
  "status": "running",
  "timestamp": "2025-01-27T10:30:15Z",
  "system_info": {
    "candidates_loaded": 25,
    "internships_loaded": 15,
    "ai_model": "all-MiniLM-L6-v2",
    "last_allocation": "2025-01-27T09:15:30Z",
    "total_allocations": 3
  },
  "health_checks": {
    "data_files": "✅ OK",
    "ai_model": "✅ OK",
    "blockchain": "✅ OK",
    "memory_usage": "240MB"
  }
}
```

**Status Codes**:
- `200`: System operational
- `503`: System error or maintenance

---

### **🎯 2. Run Allocation**

#### **POST /api/allocate** (or **POST /api/run_allocation**)

**Description**: Execute complete allocation process using AI matching and stable allocation

**Request**:
```bash
curl -X POST http://localhost:8080/api/allocate \
  -H "Content-Type: application/json"
```

**Optional Request Body** (for custom parameters):
```json
{
  "max_candidates_per_internship": 3,
  "enable_diversity_bonus": true,
  "rural_quota": 0.27,
  "sc_st_quota": 0.225,
  "algorithm_weights": {
    "semantic_similarity": 0.4,
    "skill_overlap": 0.3,
    "skill_strength": 0.2,
    "diversity_bonus": 0.1
  }
}
```

**Response**:
```json
{
  "success": true,
  "allocation_id": "alloc_20250127_103015",
  "timestamp": "2025-01-27T10:30:15Z",
  "summary": {
    "total_candidates": 25,
    "total_internships": 15,
    "successful_matches": 18,
    "unmatched_candidates": 7,
    "match_rate": 0.72
  },
  "diversity_stats": {
    "rural_placed": 8,
    "rural_percentage": 0.44,
    "sc_st_placed": 4,
    "sc_st_percentage": 0.22,
    "quota_compliance": true
  },
  "blockchain": {
    "allocation_hash": "0x7d865e959b2466918c9863afca942d0fb89d7c9ac0c99bafc3749504ded97730",
    "transaction_id": "tx_20250127_103015_a7d8",
    "verification_url": "/api/verify/0x7d865e..."
  },
  "results_files": {
    "csv_export": "results/allocation_20250127_103015.csv",
    "json_export": "results/allocation_20250127_103015.json",
    "summary_report": "results/allocation_summary_20250127_103015.txt"
  }
}
```

**Status Codes**:
- `200`: Allocation completed successfully
- `400`: Invalid request parameters
- `422`: Data validation errors (missing candidates/internships)
- `500`: Internal server error during processing

---

### **👥 3. Candidates Management**

#### **GET /api/candidates**

**Description**: List all candidates with their information

**Request**:
```bash
curl -X GET http://localhost:8080/api/candidates
```

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 50)
- `category` (optional): Filter by social category (General/OBC/SC/ST)
- `location` (optional): Filter by location

**Example with filters**:
```bash
curl -X GET "http://localhost:8080/api/candidates?category=Rural&limit=10"
```

**Response**:
```json
{
  "candidates": [
    {
      "candidate_id": "CAND_001",
      "name": "John Doe",
      "email": "john@example.com",
      "age": 22,
      "location": "Delhi",
      "social_category": "General",
      "is_rural": false,
      "skills_summary": {
        "total_skills": 12,
        "categories": ["programming", "web_development", "data_science"],
        "skill_score": 0.85,
        "top_skills": ["Python", "React", "Machine Learning"]
      },
      "education": {
        "degree": "computer science",
        "cgpa": "8.5"
      },
      "resume_filename": "candidate1.txt"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 25,
    "total_pages": 1
  },
  "summary": {
    "total_candidates": 25,
    "by_category": {
      "General": 12,
      "OBC": 6,
      "SC": 4,
      "ST": 3
    },
    "rural_candidates": 8
  }
}
```

#### **GET /api/candidates/{candidate_id}**

**Description**: Get detailed information about a specific candidate

**Request**:
```bash
curl -X GET http://localhost:8080/api/candidates/CAND_001
```

**Response**:
```json
{
  "candidate": {
    "candidate_id": "CAND_001",
    "name": "John Doe",
    "email": "john@example.com",
    "detailed_skills": {
      "programming": ["Python", "JavaScript", "SQL"],
      "web_development": ["React", "Node.js", "Express"],
      "data_science": ["Machine Learning", "Pandas", "NumPy"]
    },
    "resume_analysis": {
      "raw_text": "Full resume text...",
      "word_count": 450,
      "experience_keywords": ["developed", "implemented", "optimized"],
      "skill_score": 0.85
    }
  }
}
```

---

### **🏢 4. Internships Management**

#### **GET /api/internships**

**Description**: List all available internships

**Request**:
```bash
curl -X GET http://localhost:8080/api/internships
```

**Query Parameters**:
- `company` (optional): Filter by company name
- `location` (optional): Filter by location
- `available_only` (optional): Show only internships with available slots

**Response**:
```json
{
  "internships": [
    {
      "internship_id": "INTERN_001",
      "company_name": "TechCorp",
      "job_title": "Software Developer Intern",
      "location": "Mumbai",
      "capacity": 3,
      "required_skills": ["Python", "Flask", "React"],
      "description_filename": "job1_software_developer.txt",
      "job_summary": {
        "key_requirements": ["Programming", "Web Development"],
        "experience_level": "Entry Level",
        "duration": "6 months"
      },
      "allocation_status": {
        "slots_filled": 0,
        "slots_available": 3,
        "is_available": true
      }
    }
  ],
  "summary": {
    "total_internships": 15,
    "total_capacity": 35,
    "available_slots": 35,
    "companies": 10
  }
}
```

#### **GET /api/internships/{internship_id}**

**Description**: Get detailed information about a specific internship

**Request**:
```bash
curl -X GET http://localhost:8080/api/internships/INTERN_001
```

**Response**:
```json
{
  "internship": {
    "internship_id": "INTERN_001",
    "company_name": "TechCorp",
    "job_title": "Software Developer Intern",
    "full_description": "Complete job description text...",
    "requirements": {
      "technical_skills": ["Python", "Flask", "React"],
      "soft_skills": ["Communication", "Teamwork"],
      "education": "Bachelor's in Computer Science or related",
      "experience": "0-1 years"
    },
    "benefits": {
      "stipend": "₹25,000/month",
      "duration": "6 months",
      "location": "Mumbai",
      "mentorship": true,
      "certificate": true
    }
  }
}
```

---

### **📊 5. Results and History**

#### **GET /api/results** (or **GET /api/allocation_history**)

**Description**: Get allocation history and results

**Request**:
```bash
curl -X GET http://localhost:8080/api/results
```

**Response**:
```json
{
  "allocations": [
    {
      "allocation_id": "alloc_20250127_103015",
      "timestamp": "2025-01-27T10:30:15Z",
      "summary": {
        "total_matches": 18,
        "match_rate": 0.72,
        "processing_time": "45.2 seconds"
      },
      "diversity_stats": {
        "rural_percentage": 0.44,
        "sc_st_percentage": 0.22,
        "quota_compliance": true
      },
      "blockchain": {
        "hash": "0x7d865e959b2466918c9863afca942d0fb89d7c9ac0c99bafc3749504ded97730",
        "verified": true
      },
      "files": {
        "csv": "results/allocation_20250127_103015.csv",
        "json": "results/allocation_20250127_103015.json"
      }
    }
  ],
  "statistics": {
    "total_allocations": 3,
    "average_match_rate": 0.68,
    "best_match_rate": 0.72,
    "last_run": "2025-01-27T10:30:15Z"
  }
}
```

#### **GET /api/results/{allocation_id}**

**Description**: Get detailed results for a specific allocation

**Request**:
```bash
curl -X GET http://localhost:8080/api/results/alloc_20250127_103015
```

**Response**:
```json
{
  "allocation_id": "alloc_20250127_103015",
  "detailed_matches": [
    {
      "candidate_id": "CAND_001",
      "candidate_name": "John Doe",
      "internship_id": "INTERN_001",
      "company": "TechCorp",
      "position": "Software Developer Intern",
      "match_scores": {
        "composite_score": 0.847,
        "semantic_similarity": 0.823,
        "skill_overlap": 0.750,
        "skill_strength": 0.850,
        "diversity_bonus": 0.000
      },
      "justification": "Strong semantic match with 75% skill overlap"
    }
  ],
  "unmatched_candidates": [
    {
      "candidate_id": "CAND_008",
      "name": "Alice Kumar",
      "reason": "No suitable matches above threshold"
    }
  ]
}
```

---

### **📥 6. File Downloads**

#### **GET /api/download/{filename}**

**Description**: Download allocation results in various formats

**Request**:
```bash
curl -X GET http://localhost:8080/api/download/allocation_20250127_103015.csv \
  -o allocation_results.csv
```

**Available File Types**:
- **CSV**: `allocation_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- **JSON**: `allocation_YYYYMMDD_HHMMSS.json` - Structured data
- **TXT**: `allocation_summary_YYYYMMDD_HHMMSS.txt` - Human-readable summary

**Response**: File download with appropriate MIME type

---

### **🔗 7. Blockchain Verification**

#### **POST /api/verify**

**Description**: Verify blockchain allocation proof

**Request**:
```bash
curl -X POST http://localhost:8080/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "allocation_hash": "0x7d865e959b2466918c9863afca942d0fb89d7c9ac0c99bafc3749504ded97730"
  }'
```

**Response**:
```json
{
  "verified": true,
  "allocation_id": "alloc_20250127_103015",
  "timestamp": "2025-01-27T10:30:15Z",
  "integrity": "valid",
  "blockchain_record": {
    "transaction_id": "tx_20250127_103015_a7d8",
    "block_hash": "0x7d865e959b2466918c9863afca942d0fb89d7c9ac0c99bafc3749504ded97730",
    "algorithm_used": "Gale-Shapley Stable Matching with AI Ranking"
  },
  "verification_details": {
    "hash_algorithm": "SHA-256",
    "data_integrity": "intact",
    "tampering_detected": false
  }
}
```

#### **GET /api/verify/{allocation_hash}**

**Description**: Quick verification of allocation hash

**Request**:
```bash
curl -X GET http://localhost:8080/api/verify/0x7d865e959b2466918c9863afca942d0fb89d7c9ac0c99bafc3749504ded97730
```

**Response**:
```json
{
  "verified": true,
  "allocation_id": "alloc_20250127_103015",
  "timestamp": "2025-01-27T10:30:15Z"
}
```

---

### **📊 8. Analytics and Statistics**

#### **GET /api/analytics**

**Description**: Get comprehensive system analytics

**Request**:
```bash
curl -X GET http://localhost:8080/api/analytics
```

**Response**:
```json
{
  "overall_stats": {
    "total_candidates": 25,
    "total_internships": 15,
    "total_capacity": 45,
    "historical_match_rate": 0.68,
    "system_efficiency": "94.2%"
  },
  "candidate_analysis": {
    "by_location": {
      "Delhi": 8,
      "Mumbai": 6,
      "Bangalore": 5,
      "Others": 6
    },
    "by_category": {
      "General": 12,
      "OBC": 6,
      "SC": 4,
      "ST": 3
    },
    "skill_distribution": {
      "programming": 20,
      "web_development": 15,
      "data_science": 8,
      "business": 5
    }
  },
  "internship_analysis": {
    "by_sector": {
      "Technology": 8,
      "Finance": 4,
      "Consulting": 3
    },
    "by_location": {
      "Mumbai": 6,
      "Delhi": 4,
      "Bangalore": 3,
      "Others": 2
    },
    "capacity_distribution": {
      "1": 8,
      "2": 4,
      "3": 2,
      "5": 1
    }
  }
}
```

---

### **⚙️ 9. Configuration**

#### **GET /api/config**

**Description**: Get current system configuration

**Request**:
```bash
curl -X GET http://localhost:8080/api/config
```

**Response**:
```json
{
  "ai_settings": {
    "model_name": "all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "cache_enabled": true
  },
  "algorithm_settings": {
    "matching_algorithm": "Gale-Shapley",
    "diversity_quotas": {
      "rural_target": 0.27,
      "sc_st_target": 0.225
    },
    "scoring_weights": {
      "semantic_similarity": 0.4,
      "skill_overlap": 0.3,
      "skill_strength": 0.2,
      "diversity_bonus": 0.1
    }
  },
  "system_limits": {
    "max_file_size": "16MB",
    "max_candidates": 10000,
    "max_processing_time": "300 seconds"
  }
}
```

#### **POST /api/config**

**Description**: Update system configuration (admin only)

**Request**:
```bash
curl -X POST http://localhost:8080/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "scoring_weights": {
      "semantic_similarity": 0.5,
      "skill_overlap": 0.3,
      "skill_strength": 0.15,
      "diversity_bonus": 0.05
    }
  }'
```

---

## 💡 **Usage Examples**

### **Complete Allocation Workflow**

```bash
#!/bin/bash
# Complete API workflow example

# 1. Check system status
echo "1. Checking system status..."
curl -s http://localhost:8080/api/status | jq '.status'

# 2. View candidates summary
echo "2. Getting candidates overview..."
curl -s http://localhost:8080/api/candidates | jq '.summary'

# 3. View internships summary  
echo "3. Getting internships overview..."
curl -s http://localhost:8080/api/internships | jq '.summary'

# 4. Run allocation
echo "4. Running smart allocation..."
ALLOCATION_RESULT=$(curl -s -X POST http://localhost:8080/api/allocate)
echo $ALLOCATION_RESULT | jq '.summary'

# 5. Get allocation ID
ALLOCATION_ID=$(echo $ALLOCATION_RESULT | jq -r '.allocation_id')
echo "Allocation ID: $ALLOCATION_ID"

# 6. Download CSV results
echo "5. Downloading CSV results..."
curl -o allocation_results.csv \
  http://localhost:8080/api/download/allocation_${ALLOCATION_ID}.csv

# 7. Verify blockchain proof
HASH=$(echo $ALLOCATION_RESULT | jq -r '.blockchain.allocation_hash')
echo "6. Verifying blockchain proof..."
curl -s http://localhost:8080/api/verify/$HASH | jq '.verified'

echo "✅ Complete allocation workflow finished!"
```

### **Python API Client Example**

```python path=null start=null
import requests
import json

class PMISAPIClient:
    def __init__(self, base_url="http://localhost:8080/api"):
        self.base_url = base_url
    
    def get_system_status(self):
        """Get system status and health."""
        response = requests.get(f"{self.base_url}/status")
        return response.json()
    
    def run_allocation(self, custom_params=None):
        """Run a new allocation with optional parameters."""
        url = f"{self.base_url}/allocate"
        data = custom_params or {}
        response = requests.post(url, json=data)
        return response.json()
    
    def get_candidates(self, filters=None):
        """Get list of candidates with optional filters."""
        url = f"{self.base_url}/candidates"
        params = filters or {}
        response = requests.get(url, params=params)
        return response.json()
    
    def verify_allocation(self, allocation_hash):
        """Verify blockchain proof of allocation."""
        url = f"{self.base_url}/verify/{allocation_hash}"
        response = requests.get(url)
        return response.json()
    
    def download_results(self, filename, save_path):
        """Download allocation results file."""
        url = f"{self.base_url}/download/{filename}"
        response = requests.get(url)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return save_path

# Usage example
client = PMISAPIClient()

# Check system
status = client.get_system_status()
print(f"System status: {status['status']}")

# Run allocation
result = client.run_allocation()
print(f"Matches: {result['summary']['successful_matches']}")

# Verify result
verified = client.verify_allocation(result['blockchain']['allocation_hash'])
print(f"Blockchain verified: {verified['verified']}")
```

---

## 🚨 **Error Handling**

### **Error Response Format**
```json
{
  "error": true,
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid request parameters",
  "details": {
    "field": "rural_quota",
    "issue": "Value must be between 0 and 1",
    "provided_value": 1.5
  },
  "timestamp": "2025-01-27T10:30:15Z",
  "request_id": "req_7d865e959b24"
}
```

### **Common Error Codes**

| Code | Description | Status | Solution |
|------|-------------|--------|----------|
| `SYSTEM_NOT_READY` | Data files missing | 503 | Check data directory |
| `VALIDATION_ERROR` | Invalid parameters | 400 | Check request format |
| `MODEL_LOAD_ERROR` | AI model unavailable | 503 | Restart system |
| `PROCESSING_ERROR` | Allocation failed | 500 | Check logs |
| `FILE_NOT_FOUND` | Resume/job file missing | 404 | Verify file paths |
| `BLOCKCHAIN_ERROR` | Trust layer issue | 500 | Check blockchain service |

### **Error Handling Examples**

```bash
# Handle API errors in bash
RESPONSE=$(curl -s -X POST http://localhost:8080/api/allocate)
ERROR_STATUS=$(echo $RESPONSE | jq -r '.error // false')

if [ "$ERROR_STATUS" = "true" ]; then
    echo "❌ Error: $(echo $RESPONSE | jq -r '.message')"
    exit 1
else
    echo "✅ Success: $(echo $RESPONSE | jq -r '.summary.successful_matches') matches"
fi
```

```python path=null start=null
# Handle API errors in Python
import requests

def safe_api_call(url, method='GET', **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
        data = response.json()
        
        if data.get('error'):
            print(f"API Error: {data['message']}")
            return None
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except json.JSONDecodeError:
        print("Invalid JSON response")
        return None

# Usage
result = safe_api_call("http://localhost:8080/api/status")
if result:
    print(f"System status: {result['status']}")
```

---

## 🔐 **Authentication**

### **Current Setup (Development)**
- No authentication required for demo/development
- All endpoints are publicly accessible
- Suitable for hackathon demonstration

### **Production Authentication (Future)**

For production deployment, implement:

#### **API Key Authentication**
```bash
# Add API key header to all requests
curl -X GET http://localhost:8080/api/candidates \
  -H "X-API-Key: your-api-key-here"
```

#### **JWT Token Authentication**
```bash
# 1. Login to get token
TOKEN=$(curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secure_password"}' | jq -r '.token')

# 2. Use token for API calls
curl -X POST http://localhost:8080/api/allocate \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 **Response Formats**

### **Success Response Structure**
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-01-27T10:30:15Z",
  "request_id": "req_7d865e959b24"
}
```

### **Pagination Structure**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 247,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### **Validation Error Structure**
```json
{
  "error": true,
  "error_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "validation_errors": [
    {
      "field": "rural_quota",
      "message": "Must be between 0 and 1",
      "provided": 1.5
    }
  ]
}
```

---

## 🧪 **Testing the API**

### **Manual Testing with cURL**

```bash
# Test script for all endpoints
#!/bin/bash

echo "🧪 PMIS-AI API Test Suite"
echo "=========================="

# 1. System Status
echo "1. Testing system status..."
curl -s http://localhost:8080/api/status | jq '.status'

# 2. Candidates endpoint
echo "2. Testing candidates endpoint..."
CANDIDATE_COUNT=$(curl -s http://localhost:8080/api/candidates | jq '.summary.total_candidates')
echo "   Candidates loaded: $CANDIDATE_COUNT"

# 3. Internships endpoint
echo "3. Testing internships endpoint..."
INTERNSHIP_COUNT=$(curl -s http://localhost:8080/api/internships | jq '.summary.total_internships')
echo "   Internships loaded: $INTERNSHIP_COUNT"

# 4. Run allocation
echo "4. Testing allocation..."
RESULT=$(curl -s -X POST http://localhost:8080/api/allocate)
SUCCESS=$(echo $RESULT | jq '.success')
if [ "$SUCCESS" = "true" ]; then
    MATCHES=$(echo $RESULT | jq '.summary.successful_matches')
    echo "   ✅ Allocation successful: $MATCHES matches"
else
    echo "   ❌ Allocation failed"
fi

# 5. Verification
echo "5. Testing blockchain verification..."
HASH=$(echo $RESULT | jq -r '.blockchain.allocation_hash')
VERIFIED=$(curl -s http://localhost:8080/api/verify/$HASH | jq '.verified')
echo "   Blockchain verified: $VERIFIED"

echo "🎉 API test suite completed!"
```

### **Automated Testing with Python**

```python path=null start=null
import requests
import json
import time

def test_api_endpoints():
    base_url = "http://localhost:8080/api"
    
    tests = [
        {
            'name': 'System Status',
            'method': 'GET',
            'endpoint': '/status',
            'expected_status': 200,
            'validate': lambda r: r.json()['status'] == 'running'
        },
        {
            'name': 'Candidates List',
            'method': 'GET', 
            'endpoint': '/candidates',
            'expected_status': 200,
            'validate': lambda r: 'candidates' in r.json()
        },
        {
            'name': 'Internships List',
            'method': 'GET',
            'endpoint': '/internships', 
            'expected_status': 200,
            'validate': lambda r: 'internships' in r.json()
        },
        {
            'name': 'Run Allocation',
            'method': 'POST',
            'endpoint': '/allocate',
            'expected_status': 200,
            'validate': lambda r: r.json()['success'] == True
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            print(f"Testing {test['name']}...")
            
            url = f"{base_url}{test['endpoint']}"
            response = requests.request(test['method'], url, timeout=30)
            
            # Check status code
            status_ok = response.status_code == test['expected_status']
            
            # Check content validation
            content_ok = test['validate'](response) if 'validate' in test else True
            
            success = status_ok and content_ok
            results.append({
                'test': test['name'],
                'success': success,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            })
            
            print(f"   {'✅' if success else '❌'} {test['name']}")
            
        except Exception as e:
            results.append({
                'test': test['name'],
                'success': False,
                'error': str(e)
            })
            print(f"   ❌ {test['name']} - Error: {e}")
    
    # Summary
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    return results

if __name__ == "__main__":
    test_api_endpoints()
```

---

## 🔧 **Rate Limiting & Performance**

### **Current Limits (Development)**
- **Requests per minute**: No limit (development only)
- **Allocation frequency**: 1 per minute recommended
- **File upload size**: 16MB maximum
- **Concurrent users**: 10 recommended

### **Production Recommendations**
```python path=null start=null
# Flask-Limiter configuration for production
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Specific endpoint limits
@app.route("/api/allocate", methods=["POST"])
@limiter.limit("5 per hour")  # Allocation is resource-intensive
def run_allocation():
    # ... allocation logic
```

### **Performance Optimization**

#### **Caching Strategy**
- **AI Embeddings**: Cached in `data/embeddings_cache.pkl`
- **API Responses**: Consider Redis for response caching
- **Static Data**: Candidates/internships cached in memory

#### **Monitoring**
```bash
# Monitor API performance
curl -s http://localhost:8080/api/status | jq '.system_info.memory_usage'

# Check response times
time curl -s http://localhost:8080/api/candidates > /dev/null
```

---

## 🐛 **Debugging & Troubleshooting**

### **Enable Debug Mode**
```bash
export FLASK_DEBUG=1
export LOG_LEVEL=DEBUG
python app.py
```

### **Common Issues**

#### **1. Model Loading Error**
```bash
# Error: Cannot load sentence transformer model
# Solution: Clear cache and redownload
rm -rf ~/.cache/torch/sentence_transformers/
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

#### **2. File Not Found Errors**
```bash
# Error: Resume or job description files missing
# Solution: Check file paths and permissions
ls -la data/resumes/
ls -la data/job_descriptions/
```

#### **3. Memory Issues**
```bash
# Error: Out of memory during processing  
# Solution: Use smaller batch sizes or lighter model
export AI_MODEL_NAME=all-MiniLM-L6-v2  # Lighter model
```

#### **4. Port Already in Use**
```bash
# Error: Port 8080 already in use
# Solution: Use different port or kill existing process
export PORT=5000
# OR
lsof -ti:8080 | xargs kill
```

### **API Health Check**
```bash
# Quick health check script
#!/bin/bash
API_URL="http://localhost:8080/api"

echo "🩺 PMIS-AI API Health Check"
echo "==========================="

# Test connectivity
if curl -s "$API_URL/status" > /dev/null; then
    echo "✅ API server is running"
else
    echo "❌ API server not responding"
    exit 1
fi

# Check status
STATUS=$(curl -s "$API_URL/status" | jq -r '.status')
echo "📊 System status: $STATUS"

# Check data
CANDIDATES=$(curl -s "$API_URL/candidates" | jq '.summary.total_candidates')
INTERNSHIPS=$(curl -s "$API_URL/internships" | jq '.summary.total_internships')
echo "📋 Data loaded: $CANDIDATES candidates, $INTERNSHIPS internships"

echo "🎉 Health check completed successfully!"
```

---

## 📈 **API Metrics & Monitoring**

### **Key Performance Indicators**
- **Response Time**: Target <2 seconds for most endpoints
- **Allocation Time**: Target <60 seconds for 1000 candidates
- **Success Rate**: Target >95% for allocation completion
- **Memory Usage**: Target <1GB for normal operations

### **Monitoring Endpoints**
```bash
# System metrics
curl -s http://localhost:8080/api/status | jq '.system_info'

# Performance metrics
curl -s http://localhost:8080/api/analytics | jq '.overall_stats.system_efficiency'

# Error rates (future enhancement)
curl -s http://localhost:8080/api/metrics/errors
```

---

## 🚀 **Integration Examples**

### **Government Portal Integration**

```javascript path=null start=null
// JavaScript frontend integration
class PMISAllocationWidget {
    constructor(apiUrl = 'http://localhost:8080/api') {
        this.apiUrl = apiUrl;
    }
    
    async runAllocation() {
        try {
            const response = await fetch(`${this.apiUrl}/allocate`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayResults(result);
                return result;
            } else {
                this.showError(result.message);
                return null;
            }
        } catch (error) {
            this.showError(`Network error: ${error.message}`);
            return null;
        }
    }
    
    displayResults(result) {
        const widget = document.getElementById('allocation-results');
        widget.innerHTML = `
            <h3>Allocation Complete</h3>
            <p>Matches: ${result.summary.successful_matches}</p>
            <p>Match Rate: ${(result.summary.match_rate * 100).toFixed(1)}%</p>
            <p>Verification Hash: ${result.blockchain.allocation_hash}</p>
            <button onclick="downloadResults('${result.allocation_id}')">
                Download Results
            </button>
        `;
    }
}

// Usage
const widget = new PMISAllocationWidget();
widget.runAllocation();
```

### **Database Integration**

```python path=null start=null
# Example: Integrate with existing government database
import sqlite3
import requests

class PMISIntegration:
    def __init__(self, db_path, api_url):
        self.db_path = db_path
        self.api_url = api_url
    
    def sync_candidates_to_api(self):
        """Export candidates from government DB to PMIS-AI format."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT name, email, skills, location, category 
            FROM government_candidates 
            WHERE status = 'active'
        """)
        
        candidates = []
        for row in cursor.fetchall():
            candidates.append({
                'name': row[0],
                'email': row[1], 
                'skills': row[2],
                'location': row[3],
                'category': row[4]
            })
        
        # Convert to CSV format expected by API
        # ... conversion logic
        
        return candidates
    
    def run_allocation_and_store_results(self):
        """Run allocation via API and store results in government DB."""
        # Run allocation
        response = requests.post(f"{self.api_url}/allocate")
        result = response.json()
        
        if result['success']:
            # Store results in government database
            conn = sqlite3.connect(self.db_path)
            for match in result['detailed_matches']:
                conn.execute("""
                    INSERT INTO allocation_results 
                    (candidate_id, internship_id, allocation_date, blockchain_hash)
                    VALUES (?, ?, ?, ?)
                """, (
                    match['candidate_id'],
                    match['internship_id'], 
                    result['timestamp'],
                    result['blockchain']['allocation_hash']
                ))
            conn.commit()
            
        return result
```

---

## 📚 **Additional Resources**

### **Related Documentation**
- [README.md](README.md) - Complete project overview
- [SECURITY.md](SECURITY.md) - Security guidelines and best practices
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide

### **External Dependencies**
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Sentence Transformers](https://sentence-transformers.net/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Gale-Shapley Algorithm](https://en.wikipedia.org/wiki/Gale%E2%80%93Shapley_algorithm)

### **Government Guidelines**
- [PM Internship Scheme Official Guidelines](https://www.pminternship.gov.in)
- [Affirmative Action Policies](https://www.reservation.gov.in)
- [Digital India Framework](https://digitalindia.gov.in)

---

**Built with ❤️ for Smart India Hackathon 2025**

*Empowering transparent governance through AI innovation*

---

*Last Updated: January 27, 2025*  
*API Version: 1.0.0*  
*Compatible with PMIS-AI Engine v1.0.0*

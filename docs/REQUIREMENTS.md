# PMIS-AI Engine Requirements

## Project Overview
**PMIS-AI Smart Allocation Engine** - An AI-powered system to automate the PM Internship Scheme allocation process, handling 6.2 lakh applications with fair, efficient, and transparent matching.

## Functional Requirements

### Core Features
1. **Resume Ingestion Pipeline**
   - Parse PDF, DOCX, and TXT resume files
   - Extract skills, education, and experience using NLP
   - Support batch processing of thousands of resumes

2. **AI-Powered Matching Engine**
   - Semantic similarity matching using transformer models (Resume2Vec)
   - Rule-based eligibility filtering (age, location, category)
   - Cosine similarity scoring between candidates and internships

3. **Stable Matching Algorithm**
   - Implement Gale-Shapley algorithm for optimal allocation
   - Respect company capacity constraints
   - Ensure affirmative action quotas (30% rural, social categories)
   - Prevent unstable matches where both parties prefer alternatives

4. **Web Dashboard & API**
   - Flask-based REST API for allocation processing
   - Simple web interface for running allocations
   - Results visualization with match statistics

5. **Blockchain Trust Layer**
   - Generate cryptographic hash of final allocation
   - Immutable proof of allocation results
   - Transparency and auditability features

### User Stories
- **As an administrator**, I want to upload candidate resumes and internship descriptions in bulk
- **As an administrator**, I want to run the allocation algorithm and see fair matches
- **As a stakeholder**, I want to verify allocation results are tamper-proof via blockchain
- **As a candidate**, I want assurance that matching is fair and unbiased

## Non-Functional Requirements

### Performance
- Process 6.2 lakh applications efficiently
- Resume parsing: <5 seconds per document
- Matching algorithm: Complete allocation in <30 minutes
- API response time: <10 seconds for allocation requests

### Security
- No personal data stored on blockchain (privacy protection)
- Secure file upload handling for resumes
- Hash-based result verification
- Input validation for all user data

### Reliability
- Graceful handling of corrupted resume files
- Fallback mechanisms for failed NLP processing
- Comprehensive error logging and reporting
- Data backup and recovery procedures

### Usability
- Simple web interface requiring minimal training
- Clear progress indicators during processing
- Intuitive results visualization
- Mobile-responsive design

## Technical Requirements

### Platform Requirements
- **Operating System**: Linux/Windows/macOS
- **Runtime Environment**: Python 3.9+
- **Database**: CSV files for mock data, scalable to PostgreSQL
- **Web Framework**: Flask with Jinja2 templates

### Core Dependencies
- **NLP Processing**: spaCy, transformers, torch
- **Data Processing**: pandas, numpy, scikit-learn
- **File Handling**: PyPDF2, python-docx
- **Web Framework**: Flask
- **Blockchain**: hashlib for cryptographic hashing

### Integration Requirements
- **File Formats**: PDF, DOCX, TXT for resumes
- **Data Exchange**: JSON API responses
- **Export Formats**: CSV for final allocations

## Implementation Phases

### Phase 0: Foundation (2-3 hours)
- Environment setup and virtual environment
- Mock data creation (candidates.csv, internships.csv)
- Basic project structure

### Phase 1: Resume Pipeline (4-5 hours)
- File reading functions (PDF, DOCX, TXT)
- NLP-based skill extraction using spaCy
- Resume parsing and data structuring

### Phase 2: AI Matching Engine (5-6 hours)
- Transformer-based text embeddings (Resume2Vec)
- Cosine similarity calculations
- Rule-based eligibility filtering

### Phase 3: Stable Matching (4-5 hours)
- Gale-Shapley algorithm implementation
- Capacity and quota constraint handling
- Preference list generation and optimization

### Phase 4: Web Interface (4-5 hours)
- Flask API development
- HTML dashboard with JavaScript
- Results visualization and export

### Phase 5: Blockchain Layer (2-3 hours)
- Cryptographic hash generation
- Result verification system
- Immutable proof creation

## Acceptance Criteria

### Core Functionality
- ✅ System processes mock resumes and extracts skills
- ✅ Matching algorithm produces stable allocations
- ✅ Web interface allows running allocations
- ✅ Results respect capacity and quota constraints
- ✅ Blockchain hash provides tamper-proof verification

### Quality Standards
- Code follows Python best practices
- Comprehensive error handling implemented
- Results are reproducible and auditable
- Documentation covers all major components

---

**Status**: Draft  
**Last Updated**: 2025-09-01  
**Next Review**: TBD

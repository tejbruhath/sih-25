# 📊 Sample Data for PMIS AI Allocation Engine

This folder contains comprehensive sample data for testing the PMIS AI Allocation Engine with 50 candidates and 50 internships.

## 📁 File Structure

```
sample_data/
├── candidates.csv          # 50 diverse candidates with various skills
├── internships.csv         # 50 internship opportunities across industries
├── resumes/                # Sample resume files (TXT format)
│   ├── resume_alex_johnson.txt
│   └── resume_sarah_chen.txt
└── README.md              # This file
```

## 👥 Candidates Dataset (candidates.csv)

**50 Realistic Candidates** with diverse backgrounds:

### Key Features:
- **Diverse Universities**: MIT, Stanford, Harvard, UC Berkeley, CMU, and many others
- **Varied Experience**: 1-4 years of experience
- **Multiple Skills**: Python, Java, JavaScript, C++, AI/ML, Web Development, etc.
- **Realistic GPAs**: 3.5-3.9 range
- **Industry Coverage**: Data Science, Software Engineering, AI Research, Cybersecurity, etc.

### Sample Candidates:
1. **Alex Johnson** - Data Science (MIT, Python, ML)
2. **Sarah Chen** - Backend Development (Stanford, Java, Microservices)
3. **Mike Rodriguez** - Frontend Development (Harvard, JavaScript, React)
4. **Emily Davis** - Computer Vision (UC Berkeley, Python, AI)
5. **David Kim** - Systems Engineering (CMU, C++, Algorithms)

## 🏢 Internships Dataset (internships.csv)

**50 Diverse Internship Opportunities** across various industries:

### Key Features:
- **Multiple Industries**: Tech, Finance, Healthcare, Education, Entertainment, etc.
- **Varied Positions**: Data Science, Software Engineering, AI Research, DevOps, etc.
- **Realistic Salaries**: $4,000-$8,000 monthly stipends
- **Different Spot Capacities**: 1-4 spots per internship
- **Comprehensive Descriptions**: Detailed job descriptions and requirements

### Sample Internships:
1. **Data Science Intern** - TechCorp ($5,000/month, 3 spots)
2. **Software Engineer Intern** - StartupXYZ ($4,500/month, 2 spots)
3. **AI Research Intern** - AI Labs ($6,000/month, 2 spots)
4. **Backend Developer Intern** - BigTech ($5,500/month, 4 spots)
5. **Frontend Developer Intern** - WebSolutions ($4,000/month, 2 spots)

## 📄 Resume Files

Sample resume files in TXT format demonstrating:
- Professional formatting
- Skill descriptions
- Project portfolios
- Work experience
- Educational background

## 🎯 How to Use

### 1. Upload via Web Interface:
1. Go to `http://localhost:5000/upload`
2. Upload `candidates.csv` and `internships.csv`
3. Optionally upload resume files
4. Click "Upload & Process Data"

### 2. Direct File Usage:
1. Copy files to `uploads/` directory
2. Rename to `candidates.csv` and `internships.csv`
3. Run allocation from main page

### 3. API Testing:
```bash
# Test with sample data
curl -X POST http://localhost:5000/run_allocation \
  -H "Content-Type: application/json" \
  -d "{}"
```

## 📊 Data Statistics

### Candidates:
- **Total**: 50 candidates
- **Universities**: 50 different institutions
- **Skills**: 200+ unique skill combinations
- **Experience Range**: 1-4 years
- **GPA Range**: 3.5-3.9

### Internships:
- **Total**: 50 internships
- **Companies**: 50 different companies
- **Industries**: 15+ different sectors
- **Salary Range**: $4,000-$8,000/month
- **Total Spots**: 120+ available positions

## 🔍 Data Quality Features

### Realistic Matching Scenarios:
- **Skill Alignment**: Candidates and jobs have overlapping skills
- **Experience Matching**: Entry-level to senior positions
- **Industry Relevance**: Tech-focused with diverse applications
- **Geographic Diversity**: Various university locations

### Comprehensive Coverage:
- **Programming Languages**: Python, Java, JavaScript, C++, C#
- **Frameworks**: React, Angular, Spring Boot, TensorFlow, PyTorch
- **Technologies**: AWS, Docker, Kubernetes, SQL, NoSQL
- **Domains**: AI/ML, Web Development, Mobile, Data Science, Cybersecurity

## 🚀 Expected Results

With this dataset, you should see:
- **High Matching Efficiency**: 80-90% of candidates placed
- **Diverse Allocations**: Various skill combinations matched
- **Realistic Scores**: 0.3-0.8 range for match quality
- **Industry Distribution**: Spread across different sectors

## 📈 Performance Metrics

The AI engine will calculate:
- **Total Allocations**: Expected 40-45 successful matches
- **Matching Efficiency**: 80-90% placement rate
- **Average Score**: 0.4-0.6 range
- **Score Distribution**: Normal distribution with outliers

## 🔧 Customization

Feel free to modify the data:
- **Add/Remove Candidates**: Update skills, experience, universities
- **Modify Internships**: Change requirements, salaries, descriptions
- **Create New Resumes**: Add more detailed candidate profiles
- **Adjust Matching**: Modify skill requirements for better alignment

## 📝 Notes

- All data is fictional and for testing purposes
- Email addresses are placeholder formats
- Skills are industry-standard terminology
- Salaries are realistic for internship positions
- Universities are real institutions for authenticity

---

**Ready to test your PMIS AI Allocation Engine with comprehensive, realistic data!** 🎯

#!/bin/bash

# PMIS AI Allocation Engine - Setup Script
# This script sets up the environment for the PMIS AI Allocation Engine

echo "🎯 PMIS AI Allocation Engine Setup"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip found: $(pip --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing required packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads/resumes
mkdir -p results
mkdir -p templates
mkdir -p sample_data/resumes

# Copy sample data if it doesn't exist
if [ ! -f "sample_data/candidates.csv" ]; then
    echo "📊 Sample data not found. Creating basic sample data..."
    echo "id,name,email,skills,experience_years,gpa,university" > sample_data/candidates.csv
    echo "1,John Doe,john.doe@email.com,\"Python, Machine Learning, Data Analysis\",2,3.8,MIT" >> sample_data/candidates.csv
    
    echo "id,title,company,description,required_skills,spots_available,salary" > sample_data/internships.csv
    echo "1,Data Science Intern,TechCorp,\"Build machine learning models\",\"Python, Machine Learning, Statistics\",2,5000" >> sample_data/internships.csv
fi

# Test installation
echo "🧪 Testing installation..."
if python -c "import flask, pandas, transformers, sklearn" 2>/dev/null; then
    echo "✅ All required packages installed successfully"
else
    echo "❌ Some packages failed to install. Please check requirements.txt"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Start the server: ./start_server.sh"
echo "   2. Restart the server: ./restart_server.sh"
echo "   3. Access the application: http://localhost:5000"
echo ""
echo "📁 Project structure:"
echo "   - app.py: Main Flask application"
echo "   - sample_data/: Sample candidates and internships data"
echo "   - uploads/: User uploaded files"
echo "   - results/: Allocation results"
echo "   - templates/: Web interface templates"
echo ""
echo "🚀 Ready to run PMIS AI Allocation Engine!"

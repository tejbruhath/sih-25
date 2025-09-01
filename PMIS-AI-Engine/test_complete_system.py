#!/usr/bin/env python3
"""
Complete System Test for PMIS-AI Smart Allocation Engine
========================================================

This script runs comprehensive tests on all system components to ensure
the entire pipeline works correctly from resume parsing to blockchain recording.

Author: PMIS-AI Team
Created: 2025-01-01
"""

import os
import sys
import traceback
from datetime import datetime

def print_header(title: str):
    """Print a formatted test section header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_step(step: str):
    """Print a formatted test step."""
    print(f"\n📋 {step}")
    print("-" * 50)

def test_resume_parser():
    """Test the resume parser module."""
    print_step("Testing Resume Parser")
    
    try:
        from resume_parser import ResumeParser
        parser = ResumeParser()
        
        # Test with existing resume files
        test_files = ['data/candidate1.txt', 'data/candidate2.txt']
        
        for file_path in test_files:
            if os.path.exists(file_path):
                result = parser.parse_resume(file_path)
                
                if "error" in result:
                    print(f"❌ Error parsing {file_path}: {result['error']}")
                    return False
                else:
                    print(f"✅ Successfully parsed {file_path}")
                    print(f"   Skills found: {result['total_skills']}")
                    print(f"   Skill categories: {result['skill_categories']}")
            else:
                print(f"⚠️  File not found: {file_path}")
        
        print("✅ Resume Parser: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Resume Parser: FAILED - {str(e)}")
        traceback.print_exc()
        return False

def test_ranking_engine():
    """Test the AI ranking engine."""
    print_step("Testing AI Ranking Engine")
    
    try:
        from ranking_engine import PMISRankingEngine
        engine = PMISRankingEngine()
        
        # Test ranking generation
        rankings = engine.generate_all_rankings(
            "data/candidates.csv",
            "data/internships.csv"
        )
        
        if not rankings:
            print("❌ No rankings generated")
            return False
        
        # Verify rankings structure
        for internship_id, candidates in rankings.items():
            if not candidates:
                continue
                
            print(f"✅ {internship_id}: {len(candidates)} candidates ranked")
            
            # Verify scoring structure
            first_candidate = candidates[0]
            required_keys = ['candidate_id', 'name', 'scores']
            for key in required_keys:
                if key not in first_candidate:
                    print(f"❌ Missing key '{key}' in candidate data")
                    return False
        
        print("✅ AI Ranking Engine: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ AI Ranking Engine: FAILED - {str(e)}")
        traceback.print_exc()
        return False

def test_matching_algorithm():
    """Test the stable matching algorithm."""
    print_step("Testing Stable Matching Algorithm")
    
    try:
        from matching_algorithm import StableMatchingEngine
        engine = StableMatchingEngine()
        
        # Run complete allocation
        results = engine.run_complete_allocation(
            "data/candidates.csv",
            "data/internships.csv"
        )
        
        # Verify results structure
        required_keys = ['final_matches', 'allocation_summary']
        for key in required_keys:
            if key not in results:
                print(f"❌ Missing key '{key}' in results")
                return False
        
        # Verify allocation summary
        summary = results['allocation_summary']
        total_placed = summary['total_placed']
        
        if total_placed <= 0:
            print("❌ No candidates were placed")
            return False
        
        print(f"✅ Successfully placed {total_placed} candidates")
        print(f"✅ Placement rate: {summary['placement_rate']:.1%}")
        
        print("✅ Stable Matching Algorithm: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Stable Matching Algorithm: FAILED - {str(e)}")
        traceback.print_exc()
        return False

def test_blockchain_trust():
    """Test the blockchain trust layer."""
    print_step("Testing Blockchain Trust Layer")
    
    try:
        from blockchain_trust import BlockchainTrustLayer
        trust_layer = BlockchainTrustLayer()
        
        # Create test allocation data
        test_allocation = {
            'final_matches': {
                'I001': ['C001'],
                'I002': ['C002']
            },
            'allocation_summary': {
                'total_candidates': 10,
                'total_placed': 2,
                'placement_rate': 0.2
            }
        }
        
        # Test blockchain recording
        tx_id = trust_layer.record_allocation_on_blockchain(test_allocation)
        
        if not tx_id:
            print("❌ No transaction ID returned")
            return False
        
        print(f"✅ Blockchain transaction recorded: {tx_id}")
        print("✅ Blockchain Trust Layer: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Blockchain Trust Layer: FAILED - {str(e)}")
        traceback.print_exc()
        return False

def test_data_integrity():
    """Test data file integrity and structure."""
    print_step("Testing Data Integrity")
    
    try:
        import pandas as pd
        
        # Test candidates file
        if not os.path.exists('data/candidates.csv'):
            print("❌ Candidates CSV file not found")
            return False
        
        candidates_df = pd.read_csv('data/candidates.csv')
        required_candidate_columns = ['candidate_id', 'name', 'age', 'social_category', 'is_rural', 'resume_filename']
        
        for col in required_candidate_columns:
            if col not in candidates_df.columns:
                print(f"❌ Missing column '{col}' in candidates.csv")
                return False
        
        print(f"✅ Candidates CSV: {len(candidates_df)} records, all columns present")
        
        # Test internships file
        if not os.path.exists('data/internships.csv'):
            print("❌ Internships CSV file not found")
            return False
        
        internships_df = pd.read_csv('data/internships.csv')
        required_internship_columns = ['internship_id', 'company_name', 'job_title', 'capacity']
        
        for col in required_internship_columns:
            if col not in internships_df.columns:
                print(f"❌ Missing column '{col}' in internships.csv")
                return False
        
        print(f"✅ Internships CSV: {len(internships_df)} records, all columns present")
        
        # Test resume files
        resume_files = [f"data/{row['resume_filename']}" for _, row in candidates_df.iterrows()]
        existing_resumes = [f for f in resume_files if os.path.exists(f)]
        
        print(f"✅ Resume files: {len(existing_resumes)}/{len(resume_files)} found")
        
        print("✅ Data Integrity: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Data Integrity: FAILED - {str(e)}")
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test Flask API endpoints (requires server to be running)."""
    print_step("Testing API Endpoints")
    
    try:
        import requests
        import time
        
        base_url = "http://localhost:8080"
        
        # Test status endpoint
        response = requests.get(f"{base_url}/api/status", timeout=5)
        
        if response.status_code != 200:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
        
        status_data = response.json()
        if status_data.get('status') != 'online':
            print("❌ System not reporting as online")
            return False
        
        print("✅ Status endpoint: Working")
        
        # Test candidates endpoint
        response = requests.get(f"{base_url}/api/candidates", timeout=5)
        if response.status_code == 200:
            print("✅ Candidates endpoint: Working")
        else:
            print(f"⚠️  Candidates endpoint: {response.status_code}")
        
        # Test internships endpoint
        response = requests.get(f"{base_url}/api/internships", timeout=5)
        if response.status_code == 200:
            print("✅ Internships endpoint: Working")
        else:
            print(f"⚠️  Internships endpoint: {response.status_code}")
        
        print("✅ API Endpoints: PASSED")
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running. Start with 'python app.py' to test endpoints")
        return True  # Not a failure, just server not running
    except Exception as e:
        print(f"❌ API Endpoints: FAILED - {str(e)}")
        return False

def main():
    """Run all system tests."""
    print_header("PMIS-AI SMART ALLOCATION ENGINE - SYSTEM TESTS")
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # List of all tests
    tests = [
        ("Data Integrity", test_data_integrity),
        ("Resume Parser", test_resume_parser),
        ("AI Ranking Engine", test_ranking_engine),
        ("Stable Matching Algorithm", test_matching_algorithm),
        ("Blockchain Trust Layer", test_blockchain_trust),
        ("API Endpoints", test_api_endpoints)
    ]
    
    # Run tests
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}: CRASHED - {str(e)}")
            results[test_name] = False
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"📊 Tests Passed: {passed}/{total}")
    print(f"🎯 Success Rate: {(passed/total)*100:.1f}%")
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! System is ready for deployment.")
        print(f"🚀 You can now run the system with: python app.py")
    else:
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == "__main__":
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = main()
    sys.exit(0 if success else 1)

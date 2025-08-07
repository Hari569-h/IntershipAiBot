#!/usr/bin/env python3
"""
Test Skill Matching

This script tests the skill matching functionality for all supported skills.
"""

from skill_matcher import SkillMatcher
from typing import List, Dict, Tuple

# Define test cases for each skill
TEST_CASES = [
    # Format: (skill, job_description, should_match)
    # Java
    ("Java", "Experience with Java programming language", True),
    ("Java", "JavaScript developer needed", False),  # Should not match JavaScript
    
    # Web Development
    ("Web Development", "Experience with web development (HTML, CSS)", True),
    ("Web Development", "Frontend development skills required", True),
    
    # Firebase/Firestore
    ("Firebase", "Experience with Firebase and Firestore", True),
    ("Firebase", "Knowledge of cloud databases", False),
    
    # React
    ("React", "Experience with React.js framework", True),
    ("React", "Knowledge of ReactJS required", True),
    ("React", "Frontend frameworks like Angular or Vue", False),
    
    # AI/ML
    ("AI/ML", "Experience with artificial intelligence", True),
    ("AI/ML", "Machine learning knowledge required", True),
    ("AI/ML", "Deep learning and neural networks", True),
    ("AI/ML", "Data analysis skills", False),
    
    # Git & GitHub
    ("Git", "Experience with Git version control", True),
    ("Git", "GitHub repository management", True),
    ("Git", "Version control systems", True),
    
    # Razorpay
    ("Razorpay", "Experience with Razorpay integration", True),
    ("Razorpay", "Payment gateway integration", True),
    ("Razorpay", "E-commerce experience", False),
    
    # Google Apps Script
    ("Google Apps Script", "Experience with Google Apps Script", True),
    ("Google Apps Script", "Google Script automation", True),
    ("Google Apps Script", "Google Workspace", False),
    
    # PDF and report generation
    ("PDF", "Experience with PDF generation", True),
    ("PDF", "Report generation using jsPDF", True),
    ("PDF", "Document management", False)
]

def run_tests():
    """
    Run all test cases and report results.
    """
    matcher = SkillMatcher()
    
    passed = 0
    failed = 0
    
    print("Running skill matching tests...\n")
    
    for skill, job_description, should_match in TEST_CASES:
        # Test with a single skill
        result = matcher.filter_internship_by_skills([skill], job_description)
        
        # Check if the result matches the expected outcome
        actual_match = result["status"] == "MATCH"
        
        if actual_match == should_match:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1
        
        print(f"[{status}] Skill: {skill}")
        print(f"  Description: {job_description}")
        print(f"  Expected: {'MATCH' if should_match else 'NO MATCH'}")
        print(f"  Actual: {result['status']}")
        if status == "FAIL":
            print(f"  ❌ Test failed!")
        print()
    
    # Print summary
    total = passed + failed
    print(f"Test Summary: {passed}/{total} passed ({passed/total*100:.1f}%)")
    if failed > 0:
        print(f"❌ {failed} tests failed")
    else:
        print("✅ All tests passed!")

if __name__ == "__main__":
    run_tests()
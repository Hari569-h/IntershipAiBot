#!/usr/bin/env python3
"""
Internship Filter CLI

A command-line interface for filtering internship descriptions based on user skills.
"""

import argparse
import sys
from typing import List, Dict
from skill_matcher import SkillMatcher

# Define user skills
DEFAULT_SKILLS = [
    "Java",
    "Web Development",  # HTML, CSS
    "Firebase",  # Also matches Firestore
    "React",  # Basic knowledge
    "AI/ML",  # Fundamentals
    "Git",  # Also matches GitHub
    "Razorpay",  # Integration
    "Google Apps Script",
    "PDF"  # PDF and report generation (jsPDF)
]

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Filter internship descriptions based on user skills")
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-t", "--text", help="Job description text to filter")
    input_group.add_argument("-f", "--file", help="File containing job description to filter")
    
    # Skill options
    parser.add_argument("-s", "--skills", help="Comma-separated list of skills (default: use predefined skills)")
    
    # Output options
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output including matched skills")
    
    return parser.parse_args()

def get_job_description(args) -> str:
    """
    Get job description from command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Job description text
    """
    if args.text:
        return args.text
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    return ""

def get_user_skills(args) -> List[str]:
    """
    Get user skills from command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        List of user skills
    """
    if args.skills:
        return [skill.strip() for skill in args.skills.split(',')]
    return DEFAULT_SKILLS

def main():
    """
    Main function for the CLI.
    """
    args = parse_arguments()
    
    # Get job description and user skills
    job_description = get_job_description(args)
    user_skills = get_user_skills(args)
    
    # Initialize skill matcher
    matcher = SkillMatcher()
    
    # Filter the internship
    result = matcher.filter_internship_by_skills(user_skills, job_description)
    
    # Display results
    if args.verbose:
        print(f"Status: {result['status']}")
        if result['matched_skills']:
            print(f"Matched Skills: {', '.join(result['matched_skills'])}")
        else:
            print("No skills matched.")
    else:
        print(result['status'])

if __name__ == "__main__":
    main()
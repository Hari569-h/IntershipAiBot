#!/usr/bin/env python3
"""
Internship Filter Script

This script uses the SkillMatcher class to filter internship descriptions
based on user skills. It determines if at least one of the user's skills
is mentioned in the job description.
"""

from skill_matcher import SkillMatcher
from typing import List, Dict

# Define user skills
USER_SKILLS = [
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

def filter_internship(job_description: str) -> str:
    """
    Filter an internship description based on user skills.
    
    Args:
        job_description: The job description text
        
    Returns:
        String with "MATCH" or "NO MATCH" status
    """
    # Initialize the skill matcher
    matcher = SkillMatcher()
    
    # Filter the internship
    result = matcher.filter_internship_by_skills(USER_SKILLS, job_description)
    
    # Return the status
    return result["status"]

def filter_with_details(job_description: str) -> Dict:
    """
    Filter an internship description and return detailed results.
    
    Args:
        job_description: The job description text
        
    Returns:
        Dictionary with status and matched skills
    """
    # Initialize the skill matcher
    matcher = SkillMatcher()
    
    # Filter the internship
    return matcher.filter_internship_by_skills(USER_SKILLS, job_description)

# Example usage
if __name__ == "__main__":
    # Example job descriptions
    job_descriptions = [
        """
        Software Developer Intern
        
        Requirements:
        - Strong knowledge of Java programming
        - Experience with web development (HTML, CSS, JavaScript)
        - Familiarity with version control systems like Git
        
        Responsibilities:
        - Develop and maintain web applications
        - Collaborate with team members using GitHub
        - Write clean, efficient code
        """,
        
        """
        Data Science Intern
        
        Requirements:
        - Python programming skills
        - Knowledge of data analysis libraries (Pandas, NumPy)
        - Experience with SQL databases
        
        Responsibilities:
        - Analyze large datasets
        - Create data visualizations
        - Develop machine learning models
        """,
        
        """
        UI/UX Design Intern
        
        Requirements:
        - Proficiency in design tools (Figma, Adobe XD)
        - Understanding of user-centered design principles
        - Portfolio showcasing previous work
        
        Responsibilities:
        - Create wireframes and prototypes
        - Conduct user research
        - Collaborate with development team
        """
    ]
    
    # Filter each job description
    for i, description in enumerate(job_descriptions):
        result = filter_with_details(description)
        print(f"\nJob {i+1}:")
        print(f"Status: {result['status']}")
        if result['matched_skills']:
            print(f"Matched Skills: {', '.join(result['matched_skills'])}")
        print("-" * 50)
        print(description[:200] + "..." if len(description) > 200 else description)
        print("=" * 80)
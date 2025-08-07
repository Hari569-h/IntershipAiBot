# Internship Filter

A tool for filtering internship descriptions based on user skills. This tool analyzes job descriptions and determines if at least one of the user's skills is mentioned in the required or preferred qualifications, responsibilities, tools, or technologies.

## Features

- Simple skill matching against job descriptions
- Support for common skill variations and synonyms
- Command-line interface for easy filtering
- Detailed output showing which skills matched

## Installation

No additional installation is required beyond the existing dependencies in the AIBot project.

## Usage

### Using the Python Module

```python
from skill_matcher import SkillMatcher

# Define your skills
my_skills = [
    "Java",
    "Web Development",
    "Firebase",
    "React",
    "AI/ML",
    "Git",
    "Razorpay",
    "Google Apps Script",
    "PDF"
]

# Initialize the skill matcher
matcher = SkillMatcher()

# Filter a job description
job_description = """Software Developer Intern

Requirements:
- Strong knowledge of Java programming
- Experience with web development (HTML, CSS, JavaScript)
- Familiarity with version control systems like Git
"""

result = matcher.filter_internship_by_skills(my_skills, job_description)

# Check the result
print(f"Status: {result['status']}")
print(f"Matched Skills: {', '.join(result['matched_skills'])}")
```

### Using the Command-Line Interface

The `filter_cli.py` script provides a simple command-line interface for filtering job descriptions.

```bash
# Filter a job description from a file
python filter_cli.py --file job_description.txt

# Filter a job description provided as text
python filter_cli.py --text "Software Developer Intern with Java and React experience"

# Use custom skills
python filter_cli.py --file job_description.txt --skills "Python,Django,SQL,AWS"

# Show detailed output
python filter_cli.py --file job_description.txt --verbose
```

### Example Script

The `internship_filter.py` script provides example usage of the filtering functionality.

```bash
python internship_filter.py
```

## How It Works

The internship filter works by:

1. Converting both user skills and job descriptions to lowercase for case-insensitive matching
2. Checking for exact mentions of skills in the job description
3. Checking for common variations of skills (e.g., "React" matching "ReactJS" or "React.js")
4. Determining if at least one skill matches

## Supported Skill Variations

The filter supports the following skill variations:

- **Java**: Matches "Java" but not "JavaScript"
- **Web Development**: Matches "web development", "HTML", "CSS", "frontend development", "front-end development", "website development"
- **React**: Matches "React", "ReactJS", "React.js"
- **HTML**: Matches "HTML", "HTML5"
- **CSS**: Matches "CSS", "CSS3"
- **Firebase**: Matches "Firebase", "Firestore"
- **Git**: Matches "Git", "GitHub", "version control"
- **AI/ML**: Matches "AI", "ML", "artificial intelligence", "machine learning", "deep learning", "neural network"
- **Google Apps Script**: Matches "Google Apps Script", "Apps Script", "Google Script"
- **Razorpay**: Matches "Razorpay", "payment gateway", "payment integration"
- **PDF**: Matches "PDF", "report generation", "jsPDF"

## Customization

You can customize the skill matching by modifying the `filter_internship_by_skills` method in the `SkillMatcher` class. Add additional skill variations or synonyms as needed.
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Optional
import re
import json
from datetime import datetime

class SkillMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the skill matcher with AI model for semantic similarity."""
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = 0.85
        
        # Skill categories for better matching
        self.skill_categories = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
                'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl'
            ],
            'frameworks': [
                'react', 'angular', 'vue.js', 'node.js', 'express', 'django', 'flask',
                'spring', 'asp.net', 'laravel', 'rails', 'fastapi', 'gin', 'echo'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'sql server',
                'dynamodb', 'cassandra', 'elasticsearch', 'neo4j', 'firebase'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'heroku', 'netlify', 'vercel', 'digitalocean',
                'linode', 'vultr', 'ibm cloud', 'oracle cloud'
            ],
            'devops_tools': [
                'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions', 'circleci',
                'travis ci', 'ansible', 'terraform', 'prometheus', 'grafana'
            ],
            'machine_learning': [
                'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
                'seaborn', 'jupyter', 'keras', 'xgboost', 'lightgbm', 'opencv'
            ],
            'design_tools': [
                'figma', 'adobe xd', 'sketch', 'photoshop', 'illustrator', 'invision',
                'framer', 'principle', 'protopie', 'zeplin'
            ],
            'project_management': [
                'jira', 'confluence', 'trello', 'asana', 'monday.com', 'notion',
                'slack', 'microsoft teams', 'zoom', 'google meet'
            ]
        }
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching and AI."""
        text_lower = text.lower()
        found_skills = []
        
        # Extract skills from all categories
        for category, skills in self.skill_categories.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.append(skill)
        
        # Extract skills from common patterns
        skill_patterns = [
            r'skills?:?\s*([^•\n]+)',
            r'technologies?:?\s*([^•\n]+)',
            r'tools?:?\s*([^•\n]+)',
            r'programming\s+languages?:?\s*([^•\n]+)',
            r'frameworks?:?\s*([^•\n]+)',
            r'libraries?:?\s*([^•\n]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split by common delimiters
                skills = re.split(r'[,•\n\t]+', match)
                for skill in skills:
                    skill = skill.strip()
                    if skill and len(skill) > 2:
                        found_skills.append(skill)
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def calculate_similarity_score(self, resume_text: str, job_description: str) -> float:
        """Calculate semantic similarity between resume and job description."""
        try:
            # Create embeddings
            resume_embedding = self.model.encode(resume_text)
            job_embedding = self.model.encode(job_description)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                [resume_embedding], 
                [job_embedding]
            )[0][0]
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def match_skills(self, resume_skills: List[str], job_skills: List[str]) -> Dict:
        """Match skills between resume and job requirements."""
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Exact matches
        exact_matches = []
        for job_skill in job_skills_lower:
            if job_skill in resume_skills_lower:
                exact_matches.append(job_skill)
        
        # Partial matches (substring matching)
        partial_matches = []
        for job_skill in job_skills_lower:
            for resume_skill in resume_skills_lower:
                if job_skill in resume_skill or resume_skill in job_skill:
                    if job_skill not in exact_matches:
                        partial_matches.append(job_skill)
        
        # Category-based matches
        category_matches = []
        for category, skills in self.skill_categories.items():
            category_skills = [skill.lower() for skill in skills]
            for job_skill in job_skills_lower:
                if job_skill in category_skills:
                    for resume_skill in resume_skills_lower:
                        if resume_skill in category_skills:
                            if job_skill not in exact_matches and job_skill not in partial_matches:
                                category_matches.append(job_skill)
        
        # Calculate match percentages
        total_job_skills = len(job_skills)
        exact_match_percentage = (len(exact_matches) / total_job_skills * 100) if total_job_skills > 0 else 0
        partial_match_percentage = (len(partial_matches) / total_job_skills * 100) if total_job_skills > 0 else 0
        category_match_percentage = (len(category_matches) / total_job_skills * 100) if total_job_skills > 0 else 0
        
        total_match_percentage = exact_match_percentage + partial_match_percentage + category_match_percentage
        
        return {
            'exact_matches': exact_matches,
            'partial_matches': partial_matches,
            'category_matches': category_matches,
            'exact_match_percentage': exact_match_percentage,
            'partial_match_percentage': partial_match_percentage,
            'category_match_percentage': category_match_percentage,
            'total_match_percentage': total_match_percentage,
            'missing_skills': [skill for skill in job_skills if skill.lower() not in [m.lower() for m in exact_matches + partial_matches + category_matches]]
        }
    
    def evaluate_job_fit(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Evaluate overall job fit using multiple criteria."""
        resume_text = resume_data.get('raw_text', '')
        resume_skills = resume_data.get('skills', [])
        
        job_description = job_data.get('description', '')
        job_title = job_data.get('title', '')
        job_company = job_data.get('company', '')
        
        # Extract skills from job description
        job_skills = self.extract_skills_from_text(job_description)
        
        # Calculate semantic similarity
        semantic_similarity = self.calculate_similarity_score(resume_text, job_description)
        
        # Match skills
        skill_match_result = self.match_skills(resume_skills, job_skills)
        
        # Calculate overall score
        skill_score = skill_match_result['total_match_percentage'] / 100
        overall_score = (semantic_similarity + skill_score) / 2
        
        # Determine if application should proceed
        should_apply = overall_score >= (self.similarity_threshold / 100)
        
        # Generate detailed analysis
        analysis = {
            'job_title': job_title,
            'company': job_company,
            'semantic_similarity': semantic_similarity,
            'skill_match': skill_match_result,
            'overall_score': overall_score,
            'should_apply': should_apply,
            'reasoning': self._generate_reasoning(semantic_similarity, skill_match_result, should_apply),
            'evaluated_at': datetime.now().isoformat()
        }
        
        return analysis
    
    def _generate_reasoning(self, semantic_similarity: float, skill_match: Dict, should_apply: bool) -> str:
        """Generate reasoning for the application decision."""
        reasons = []
        
        if semantic_similarity >= 0.85:
            reasons.append("High semantic similarity with job description")
        elif semantic_similarity >= 0.70:
            reasons.append("Good semantic similarity with job description")
        else:
            reasons.append("Low semantic similarity with job description")
        
        if skill_match['total_match_percentage'] >= 80:
            reasons.append("Excellent skill match")
        elif skill_match['total_match_percentage'] >= 60:
            reasons.append("Good skill match")
        elif skill_match['total_match_percentage'] >= 40:
            reasons.append("Moderate skill match")
        else:
            reasons.append("Poor skill match")
        
        if should_apply:
            reasons.append("RECOMMENDED: Overall score meets threshold for application")
        else:
            reasons.append("NOT RECOMMENDED: Overall score below threshold")
        
        return " | ".join(reasons)
    
    def batch_evaluate_jobs(self, resume_data: Dict, jobs: List[Dict]) -> List[Dict]:
        """Evaluate multiple jobs against a resume."""
        evaluations = []
        
        for job in jobs:
            evaluation = self.evaluate_job_fit(resume_data, job)
            evaluations.append(evaluation)
        
        # Sort by overall score (descending)
        evaluations.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return evaluations
    
    def get_recommended_jobs(self, resume_data: Dict, jobs: List[Dict], 
                           min_score: float = 0.85) -> List[Dict]:
        """Get jobs that meet the minimum score threshold."""
        evaluations = self.batch_evaluate_jobs(resume_data, jobs)
        
        recommended_jobs = [
            eval for eval in evaluations 
            if eval['overall_score'] >= min_score
        ]
        
        return recommended_jobs
    
    def analyze_skill_gaps(self, resume_skills: List[str], job_skills: List[str]) -> Dict:
        """Analyze skill gaps between resume and job requirements."""
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        missing_skills = []
        for job_skill in job_skills_lower:
            if job_skill not in resume_skills_lower:
                missing_skills.append(job_skill)
        
        # Categorize missing skills
        categorized_gaps = {}
        for category, skills in self.skill_categories.items():
            category_gaps = []
            for missing_skill in missing_skills:
                if missing_skill in [skill.lower() for skill in skills]:
                    category_gaps.append(missing_skill)
            if category_gaps:
                categorized_gaps[category] = category_gaps
        
        return {
            'missing_skills': missing_skills,
            'categorized_gaps': categorized_gaps,
            'total_missing': len(missing_skills),
            'gap_percentage': (len(missing_skills) / len(job_skills) * 100) if job_skills else 0
        }
    
    def suggest_skill_improvements(self, resume_data: Dict, target_jobs: List[Dict]) -> Dict:
        """Suggest skills to improve based on target jobs."""
        all_required_skills = set()
        
        # Collect all skills from target jobs
        for job in target_jobs:
            job_description = job.get('description', '')
            job_skills = self.extract_skills_from_text(job_description)
            all_required_skills.update(job_skills)
        
        # Find missing skills
        resume_skills = set(resume_data.get('skills', []))
        missing_skills = all_required_skills - resume_skills
        
        # Categorize missing skills by frequency
        skill_frequency = {}
        for job in target_jobs:
            job_description = job.get('description', '')
            job_skills = self.extract_skills_from_text(job_description)
            for skill in job_skills:
                if skill in missing_skills:
                    skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        # Sort by frequency
        sorted_missing_skills = sorted(
            skill_frequency.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {
            'missing_skills': sorted_missing_skills,
            'top_priority_skills': [skill for skill, freq in sorted_missing_skills[:5]],
            'total_missing_skills': len(missing_skills),
            'skill_improvement_plan': self._generate_skill_plan(sorted_missing_skills[:10])
        }
    
    def _generate_skill_plan(self, missing_skills: List[Tuple[str, int]]) -> Dict:
        """Generate a learning plan for missing skills."""
        plan = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        for skill, frequency in missing_skills:
            if frequency >= 5:
                plan['high_priority'].append(skill)
            elif frequency >= 3:
                plan['medium_priority'].append(skill)
            else:
                plan['low_priority'].append(skill)
        
        return plan
    
    def save_evaluation_results(self, evaluations: List[Dict], filename: str = "job_evaluations.json"):
        """Save evaluation results to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(evaluations, f, indent=2, ensure_ascii=False)
            print(f"Evaluation results saved to {filename}")
        except Exception as e:
            print(f"Error saving evaluation results: {e}")
    
    def load_evaluation_results(self, filename: str = "job_evaluations.json") -> List[Dict]:
        """Load evaluation results from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Evaluation results file {filename} not found")
            return []
        except Exception as e:
            print(f"Error loading evaluation results: {e}")
            return [] 
    
    def filter_internship_by_skills(self, user_skills: List[str], job_description: str) -> Dict:
        """Filter internship based on user skills.
        
        Args:
            user_skills: List of user's skills
            job_description: The job description text
            
        Returns:
            Dict with match status and matched skills
        """
        # Convert user skills to lowercase for case-insensitive matching
        user_skills_lower = [skill.lower() for skill in user_skills]
        job_description_lower = job_description.lower()
        
        # Check for direct mentions of skills in the job description
        matched_skills = []
        for skill in user_skills_lower:
            # Check for exact skill mention (with word boundaries)
            if re.search(r'\b' + re.escape(skill) + r'\b', job_description_lower):
                matched_skills.append(skill)
            # Special case for Web Development
            elif skill.lower() == "web development" and re.search(r'\b(frontend|front-end|front\s+end|web\s+app|website)\s*(development|developer|programming)\b', job_description_lower):
                matched_skills.append(skill)
            # Check for common variations (e.g., "React" matching "ReactJS" or "React.js")
            elif skill == "react" and re.search(r'\b(react\.?js|react\s+js)\b', job_description_lower):
                matched_skills.append(skill)
            elif skill == "java" and not re.search(r'\b(javascript)\b', job_description_lower) and re.search(r'\bjava\b', job_description_lower):
                matched_skills.append(skill)
            elif skill == "html" and re.search(r'\b(html5|html\s+5)\b', job_description_lower):
                matched_skills.append(skill)
            elif skill == "css" and re.search(r'\b(css3|css\s+3)\b', job_description_lower):
                matched_skills.append(skill)
            elif skill == "firebase" and re.search(r'\b(firebase|firestore)\b', job_description_lower):
                matched_skills.append(skill)
            elif skill == "git" and re.search(r'\b(git|github|version\s+control)\b', job_description_lower):
                matched_skills.append(skill)
            elif skill in ["ai", "ai/ml", "ml"] and re.search(r'\b(artificial\s+intelligence|machine\s+learning|ml|ai|deep\s+learning|neural\s+network)\b', job_description_lower):
                matched_skills.append(skill)
            elif skill == "google apps script" and re.search(r'\b(google\s+apps\s+script|apps\s+script|google\s+script)\b', job_description_lower):
                matched_skills.append(skill)
            elif skill == "razorpay" and re.search(r'\b(razorpay|payment\s+gateway|payment\s+integration)\b', job_description_lower):
                matched_skills.append(skill)
            elif skill == "pdf" and re.search(r'\b(pdf|report\s+generation|jspdf)\b', job_description_lower):
                matched_skills.append(skill)
        
        # Determine match status
        is_match = len(matched_skills) > 0
        
        return {
            "status": "MATCH" if is_match else "NO MATCH",
            "matched_skills": matched_skills
        }
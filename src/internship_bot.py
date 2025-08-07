import os
import sys
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import json
from dotenv import load_dotenv
import config

config.get_config()

# Add parent directory to path for config import
sys.path.append('..')
from config import get_config, update_config

from .resume_parser import ResumeParser
from .job_scraper import JobScraper
from .skill_matcher import SkillMatcher
from .application_automator import ApplicationAutomator
from .application_tracker import ApplicationTracker
from .ai_agents import MultiAgentAI

class InternshipBot:
    def __init__(self, config: Dict = None):
        """Initialize the LinkedIn internship bot with multi-agent AI support."""
        load_dotenv()
        
        # Load configuration from config.py
        user_config = get_config()
        self.config = config or self._load_default_config()
        
        # Update config with user credentials
        self.config.update({
            'similarity_threshold': user_config['similarity_threshold'],
            'application_delay': user_config['application_delay'],
            'max_applications_per_run': user_config['max_applications_per_run'],
            'run_interval_hours': user_config['run_interval_hours'],
            'internship_titles': user_config['internship_titles'],
            'user_name': user_config['user_name'],
            'user_email': user_config['user_email'],
            'user_phone': user_config['user_phone'],
            'user_location': user_config['user_location'],
            'user_skills': user_config['user_skills'],
            'resume_path': user_config['resume_path']
        })
        
        self.setup_logging()
        
        # Initialize multi-agent AI system
        self.ai_agents = MultiAgentAI(user_config)
        
        # Initialize components
        self.resume_parser = ResumeParser(user_config)
        self.job_scraper = JobScraper()
        self.skill_matcher = SkillMatcher()
        self.application_automator = ApplicationAutomator(
            openai_api_key=user_config['openai_api_key']
        )
        self.application_tracker = ApplicationTracker(
            applications_file="applications.txt"
        )
        
        # Load resume data
        self.resume_data = None
        self.candidate_info = None
        
        # Store LinkedIn credentials for login
        self.linkedin_credentials = {
            'email': user_config['linkedin_email'],
            'password': user_config['linkedin_password']
        }
        
        self.logger.info("LinkedIn Internship Bot initialized successfully")
        self.logger.info(f"Configured with LinkedIn: {user_config['linkedin_email']}")
        self.logger.info(f"Resume path: {user_config['resume_path']}")
        self.logger.info("🤖 Multi-agent AI system initialized")
    
    def _load_default_config(self) -> Dict:
        """Load default configuration."""
        return {
            'similarity_threshold': float(os.getenv('SIMILARITY_THRESHOLD', 0.85)),
            'application_delay': int(os.getenv('APPLICATION_DELAY', 30)),
            'max_applications_per_run': int(os.getenv('MAX_APPLICATIONS_PER_RUN', 10)),
            'run_interval_hours': int(os.getenv('RUN_INTERVAL_HOURS', 6)),
            'internship_titles': os.getenv('INTERNSHIP_TITLES', '').split(','),
            'user_name': os.getenv('USER_NAME', ''),
            'user_email': os.getenv('USER_EMAIL', ''),
            'user_phone': os.getenv('USER_PHONE', ''),
            'user_location': os.getenv('USER_LOCATION', 'Remote'),
            'user_skills': os.getenv('USER_SKILLS', '').split(','),
            'resume_path': os.getenv('RESUME_PATH', '')
        }
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('internship_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_resume(self, resume_path: str) -> bool:
        """Load and parse resume using multi-agent AI."""
        try:
            self.logger.info(f"Loading resume from: {resume_path}")
            
            # Parse resume using multi-agent AI
            self.resume_data = self.resume_parser.parse_resume(resume_path)
            
            if not self.resume_data:
                self.logger.error("❌ Failed to parse resume")
                return False
            
            # Extract candidate information
            self.candidate_info = {
                'name': self._extract_name_from_resume(),
                'email': self.resume_data.get('contact_info', {}).get('email', ''),
                'phone': self.resume_data.get('contact_info', {}).get('phone', ''),
                'linkedin': self.resume_data.get('contact_info', {}).get('linkedin', ''),
                'github': self.resume_data.get('contact_info', {}).get('github', ''),
                'location': self.resume_data.get('contact_info', {}).get('location', ''),
                'skills': self.resume_data.get('skills', []),
                'soft_skills': self.resume_data.get('soft_skills', []),
                'education': self.resume_data.get('education', ''),
                'experience': self.resume_data.get('experience', []),
                'certifications': self.resume_data.get('certifications', []),
                'domains': self.resume_data.get('domains', [])
            }
            
            self.logger.info(f"✅ Resume loaded successfully. Found {len(self.candidate_info['skills'])} skills")
            self.logger.info(f"📋 Skills: {', '.join(self.candidate_info['skills'][:5])}...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error loading resume: {e}")
            return False
    
    def _extract_name_from_resume(self) -> str:
        """Extract name from resume data."""
        try:
            # Try to extract name from contact info or resume text
            contact_info = self.resume_data.get('contact_info', {})
            
            # Look for name patterns in the raw text
            raw_text = self.resume_data.get('raw_text', '')
            if raw_text:
                # Simple name extraction (first few words that look like a name)
                lines = raw_text.split('\n')
                for line in lines[:5]:  # Check first 5 lines
                    line = line.strip()
                    if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
                        # This might be a name
                        return line
            
            return "Candidate"
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting name: {e}")
            return "Candidate"
    
    def scrape_internships(self, keywords: List[str] = None, location: str = None) -> List[Dict]:
        """Scrape internships from LinkedIn only."""
        keywords = keywords or self.config['internship_titles']
        
        self.logger.info(f"Starting LinkedIn internship scraping for keywords: {keywords}")
        
        # Get resume embedding for smart filtering
        resume_embedding = self.resume_data.get('embedding') if self.resume_data else None
        
        try:
            # Login to LinkedIn before scraping
            self.logger.info("🔑 LOGGING IN TO LINKEDIN BEFORE SCRAPING 🔑")
            self._login_to_linkedin()
            self.logger.info("✅ LOGIN PROCESS COMPLETED, PROCEEDING TO SCRAPING")
            
            # Scrape from LinkedIn
            self.logger.info("Scraping internships from LinkedIn...")
            try:
                linkedin_internships = self.job_scraper.scrape_linkedin_internships(
                    keywords=keywords, 
                    location=location
                )
                
                # Apply filtering with AI agents after scraping
                if linkedin_internships and resume_embedding:
                    internships = self.job_scraper.filter_jobs(
                        linkedin_internships, 
                        keywords, 
                        resume_embedding, 
                        self.ai_agents
                    )
                else:
                    internships = linkedin_internships
                    
                if internships is None:
                    internships = []
                    
                # Save scraped internships
                self.job_scraper.save_internships_to_json(internships)
                
                self.logger.info(f"Scraped {len(internships)} LinkedIn internships")
                return internships
                
            except Exception as e:
                self.logger.error(f"Error scraping LinkedIn: {e}")
                return []
            
        except Exception as e:
            self.logger.error(f"Error scraping internships: {e}")
            return []
            
    def _login_to_linkedin(self) -> None:
        """Login to LinkedIn before scraping."""
        self.logger.info("🔐 STARTING LINKEDIN LOGIN PROCESS 🔐")
        
        # Login to LinkedIn
        try:
            self.logger.info("Logging in to LinkedIn...")
            linkedin_login_success = self.job_scraper.login_to_linkedin(
                email=self.linkedin_credentials['email'],
                password=self.linkedin_credentials['password']
            )
            if linkedin_login_success:
                self.logger.info("✅ Successfully logged in to LinkedIn")
            else:
                self.logger.warning("⚠️ Failed to login to LinkedIn, will try to use existing cookies")
        except Exception as e:
            self.logger.error(f"❌ Error logging in to LinkedIn: {e}")
            raise Exception("Failed to login to LinkedIn. Please check your credentials.")
            
        self.logger.info("🔐 LINKEDIN LOGIN PROCESS COMPLETED 🔐")
    
    def evaluate_internships(self, internships: List[Dict]) -> List[Dict]:
        """Evaluate internships against resume using AI matching."""
        if not self.resume_data:
            self.logger.error("No resume data loaded. Please load resume first.")
            return []
        
        self.logger.info(f"Evaluating {len(internships)} internships")
        
        try:
            evaluations = self.skill_matcher.batch_evaluate_jobs(self.resume_data, internships)
            
            # Save evaluation results
            self.skill_matcher.save_evaluation_results(evaluations)
            
            # Filter recommended jobs
            recommended_jobs = self.skill_matcher.get_recommended_jobs(
                self.resume_data, 
                internships, 
                self.config['similarity_threshold']
            )
            
            self.logger.info(f"Found {len(recommended_jobs)} recommended internships")
            return recommended_jobs
            
        except Exception as e:
            self.logger.error(f"Error evaluating internships: {e}")
            return []
    
    def run_full_cycle(self, keywords: List[str] = None, location: str = None) -> Dict:
        """Run the complete internship application cycle with multi-agent AI, focusing only on LinkedIn."""
        self.logger.info("Starting full LinkedIn internship application cycle")
        
        # Use improved keywords if none provided
        if keywords is None:
            keywords = [
                "internship", "software", "data", "engineering", "development",
                "python", "javascript", "react", "node", "machine learning",
                "frontend", "backend", "full stack", "web development", "programming",
                "computer science", "information technology", "software engineering",
                "data science", "artificial intelligence", "mobile development",
                "cloud computing", "cybersecurity", "database", "devops"
            ]
        
        # We're not filtering by location as per user request
        # Location parameter is already None from run_automation.py
        
        results = {
            'scraped_internships': 0,
            'evaluated_internships': 0,
            'recommended_internships': 0,
            'applications_made': 0,
            'successful_applications': 0,
            'failed_applications': 0,
            'errors': []
        }
        
        try:
            # Step 1: Scrape internships from LinkedIn only
            self.logger.info("Step 1: Scraping LinkedIn internships")
            self.logger.info(f"Starting LinkedIn internship scraping for keywords: {keywords}")
            resume_embedding = self.resume_data.get('embedding') if self.resume_data else None
            try:
                # Only scrape from LinkedIn
                self.logger.info("Scraping from LinkedIn...")
                try:
                    linkedin_internships = self.job_scraper.scrape_linkedin_internships(
                        keywords=keywords, 
                        location=location
                    )
                    
                    # Apply filtering with AI agents after scraping
                    if linkedin_internships and resume_embedding:
                        internships = self.job_scraper.filter_jobs(
                            linkedin_internships, 
                            keywords, 
                            resume_embedding, 
                            self.ai_agents
                        )
                    else:
                        internships = linkedin_internships
                except Exception as e:
                    self.logger.error(f"Error scraping LinkedIn: {e}")
                    internships = []
                
                if internships is None:
                    internships = []
                results['scraped_internships'] = len(internships)
                self.logger.info(f"Scraped {len(internships)} LinkedIn internships")
            except Exception as e:
                self.logger.error(f"Error during LinkedIn internship scraping: {e}")
                results['errors'].append(f"LinkedIn scraping error: {str(e)}")
                internships = []
            
            if not internships:
                self.logger.warning("No LinkedIn internships found. Ending cycle.")
                return results
            
            # Step 2: Evaluate and filter internships using multi-agent AI
            self.logger.info("Step 2: Evaluating and filtering internships with AI")
            recommended_internships = []
            
            for internship in internships:
                try:
                    # Use multi-agent AI for advanced analysis
                    similarity_score = self._calculate_ai_similarity_score(internship)
                    internship['similarity_score'] = similarity_score
                    
                    # Only recommend if similarity is above threshold
                    if similarity_score >= self.config['similarity_threshold']:
                        recommended_internships.append(internship)
                        self.logger.info(f"✅ AI Recommended: {internship['title']} at {internship['company']} (Score: {similarity_score:.2f})")
                    else:
                        self.logger.debug(f"❌ AI Rejected: {internship['title']} at {internship['company']} (Score: {similarity_score:.2f})")
                        
                except Exception as e:
                    self.logger.error(f"Error evaluating internship {internship.get('title', 'Unknown')}: {e}")
                    results['errors'].append(f"Evaluation error: {e}")
                    continue
            
            results['evaluated_internships'] = len(internships)
            results['recommended_internships'] = len(recommended_internships)
            
            if not recommended_internships:
                self.logger.warning("No internships met the AI similarity threshold. Ending cycle.")
                return results
            
            # Step 3: Apply to recommended internships
            self.logger.info(f"Step 3: Applying to {len(recommended_internships)} AI-recommended internships")
            
            for internship in recommended_internships:
                try:
                    self.logger.info(f"Applying to: {internship['title']} at {internship['company']}")
                    
                    # Generate cover letter using multi-agent AI
                    cover_letter = self._generate_ai_cover_letter(internship)
                    
                    # Apply to the internship
                    application_result = self.application_automator.apply_to_job(
                        internship, 
                        self.candidate_info,
                        self.resume_data,
                        cover_letter=cover_letter
                    )
                    
                    results['applications_made'] += 1
                    
                    # Send email notification if application was successful
                    if application_result.get('status') == 'success':
                        try:
                            # Extract matching skills for this internship
                            matching_skills = self._get_matching_skills(internship)
                            
                            # Send email notification
                            self.email_notifier.send_application_notification(
                                job_title=internship['title'],
                                company_name=internship['company'],
                                platform=internship['platform'],
                                matching_skills=matching_skills,
                                resume_file=self.candidate_info.get('resume_path', 'Not specified'),
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                additional_info={
                                    'Job Link': internship.get('link', 'Not available'),
                                    'Similarity Score': f"{internship.get('similarity_score', 0):.2f}",
                                    'Location': internship.get('location', 'Not specified')
                                }
                            )
                        except Exception as e:
                            self.logger.error(f"Failed to send email notification: {e}")
                            # Continue with the application process even if email fails
                    
                    if application_result.get('status') == 'success':
                        results['successful_applications'] += 1
                        self.logger.info(f"✅ Successfully applied to: {internship['title']} at {internship['company']}")
                        
                        # Track the application
                        self.application_tracker.add_application(
                            title=internship['title'],
                            company=internship['company'],
                            platform=internship['platform'],
                            link=internship.get('link', ''),
                            similarity_score=internship.get('similarity_score', 0),
                            status='Applied',
                            applied_at=datetime.now().isoformat()
                        )
                    else:
                        results['failed_applications'] += 1
                        self.logger.warning(f"❌ Failed to apply to: {internship['title']} at {internship['company']}")
                        
                        # Track the failed application
                        self.application_tracker.add_application(
                            title=internship['title'],
                            company=internship['company'],
                            platform=internship['platform'],
                            link=internship.get('link', ''),
                            similarity_score=internship.get('similarity_score', 0),
                            status='Failed',
                            applied_at=datetime.now().isoformat()
                        )
                    
                    # Add delay between applications
                    time.sleep(self.config['application_delay'])
                    
                except Exception as e:
                    self.logger.error(f"Error applying to {internship.get('title', 'Unknown')}: {e}")
                    results['errors'].append(f"Application error: {e}")
                    results['failed_applications'] += 1
                    continue
            
            self.logger.info("Full cycle completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in full cycle: {e}")
            results['errors'].append(f"Cycle error: {e}")
        
        return results
    
    def _calculate_ai_similarity_score(self, internship: Dict) -> float:
        """Calculate similarity score using multi-agent AI with dimension validation."""
        try:
            # Get job description
            job_description = internship.get('description', '')
            if not job_description:
                return 0.5  # Default score if no description
            
            resume_text = self.resume_data.get('raw_text', '')
            if not resume_text.strip():
                self.logger.error("❌ Empty resume text provided for similarity calculation")
                return 0.5
            
            # Use sentence transformer as primary method for consistency
            if self.resume_parser.sentence_transformer:
                try:
                    # Ensure we use the same model for both embeddings
                    resume_embedding = self.resume_parser.sentence_transformer.encode(resume_text)
                    job_embedding = self.resume_parser.sentence_transformer.encode(job_description)
                    
                    # Debug embedding dimensions
                    self.logger.debug(f"🔍 Resume embedding dim: {len(resume_embedding)}")
                    self.logger.debug(f"🧾 Job embedding dim: {len(job_embedding)}")
                    
                    # Check if resume embedding is 1024 dimensions (Cohere standard)
                    if len(resume_embedding) != 1024:
                        self.logger.warning(f"⚠️ Resume embedding dimension is {len(resume_embedding)}, not 1024 (Cohere standard)")
                        self.logger.info("🔄 Regenerating embeddings with Cohere to ensure 1024 dimensions")
                        # Regenerate resume embedding with Cohere to get 1024 dimensions
                        cohere_embeddings = self.ai_agents.get_embeddings([resume_text], provider="cohere", 
                                                                       fallback_provider="openai", force_dimension=1024)
                        if cohere_embeddings and len(cohere_embeddings) > 0 and len(cohere_embeddings[0]) == 1024:
                            self.logger.info(f"✅ Successfully regenerated resume embedding with Cohere: {len(cohere_embeddings[0])} dimensions")
                            resume_embedding = cohere_embeddings[0]
                            # Also regenerate job embedding with Cohere for consistency
                            job_cohere_embeddings = self.ai_agents.get_embeddings([job_description], provider="cohere", 
                                                                               fallback_provider="openai", force_dimension=1024)
                            if job_cohere_embeddings and len(job_cohere_embeddings) > 0 and len(job_cohere_embeddings[0]) == 1024:
                                job_embedding = job_cohere_embeddings[0]
                            else:
                                # Skip to Cohere generation for both
                                raise ValueError("Failed to regenerate job embedding with Cohere")
                        else:
                            # Skip to Cohere generation for both
                            raise ValueError("Failed to regenerate resume embedding with Cohere")
                    
                    # Check for dimension mismatch between resume and job
                    if len(resume_embedding) != len(job_embedding):
                        self.logger.error(f"❌ Embedding dimension mismatch: resume={len(resume_embedding)}, job={len(job_embedding)}")
                        self.logger.info("🔄 Falling back to Cohere for consistent dimensions")
                        # Skip to Cohere fallback
                        raise ValueError("Embedding dimension mismatch")
                    
                    similarity = self.resume_parser.calculate_similarity(resume_embedding, job_embedding)
                    self.logger.info(f"✅ Calculated similarity using {'SentenceTransformer' if len(resume_embedding) != 1024 else 'Cohere'}: {similarity:.4f}")
                    return similarity
                except Exception as e:
                    self.logger.error(f"❌ Error with embeddings: {e}, falling back to Cohere for both embeddings")
            
            # Only use Cohere as fallback, ensuring both embeddings come from the same source
            self.logger.info("🔄 Using Cohere for embeddings with forced 1024 dimensions")
            
            # Use get_embeddings with force_dimension to ensure 1024 dimensions
            embeddings = self.ai_agents.get_embeddings([resume_text, job_description], 
                                                     provider="cohere", 
                                                     fallback_provider="openai", 
                                                     force_dimension=1024)
            
            if len(embeddings) >= 2:
                # Verify dimensions before calculating similarity
                if len(embeddings[0]) != 1024 or len(embeddings[1]) != 1024:
                    self.logger.error(f"❌ Cohere embedding dimension error: resume={len(embeddings[0])}, job={len(embeddings[1])}")
                    # Try one more time with OpenAI as last resort
                    self.logger.info("🔄 Trying OpenAI embeddings as last resort with forced 1536 dimensions")
                    openai_embeddings = self.ai_agents.get_embeddings([resume_text, job_description], 
                                                                   provider="openai", 
                                                                   fallback_provider=None, 
                                                                   force_dimension=1536)
                    if len(openai_embeddings) >= 2 and len(openai_embeddings[0]) == len(openai_embeddings[1]):
                        similarity_score = self.ai_agents.calculate_similarity_score(openai_embeddings[0], openai_embeddings[1])
                        self.logger.info(f"✅ Calculated similarity using OpenAI (1536 dimensions): {similarity_score:.4f}")
                        return similarity_score
                    self.logger.error("❌ All embedding methods failed to produce consistent dimensions")
                    return 0.5  # Default if all methods fail
                
                similarity_score = self.ai_agents.calculate_similarity_score(embeddings[0], embeddings[1])
                self.logger.info(f"✅ Calculated similarity using Cohere (1024 dimensions): {similarity_score:.4f}")
                return similarity_score
            
            self.logger.error("❌ Failed to generate embeddings with any provider")
            return 0.5  # Default if all methods fail
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating AI similarity score: {e}")
            return 0.5
    
    def _generate_ai_cover_letter(self, internship: Dict) -> str:
        """Generate cover letter using multi-agent AI."""
        try:
            job_description = internship.get('description', '')
            company = internship.get('company', '')
            position = internship.get('title', '')
            
            # Use OpenRouter (Claude) for cover letter generation
            cover_letter = self.ai_agents.generate_cover_letter_with_openrouter(
                job_description, 
                self.resume_data, 
                company, 
                position
            )
            
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"❌ Error generating AI cover letter: {e}")
            return ""
    
    def schedule_daily_run(self, time: str = "09:00"):
        """Schedule daily automated runs."""
        schedule.every().day.at(time).do(self.run_full_cycle)
        self.logger.info(f"Scheduled daily run at {time}")
    
    def schedule_weekly_run(self, day: str = "monday", time: str = "09:00"):
        """Schedule weekly automated runs."""
        getattr(schedule.every(), day).at(time).do(self.run_full_cycle)
        self.logger.info(f"Scheduled weekly run on {day} at {time}")
    
    def start_scheduler(self):
        """Start the scheduler to run automated jobs."""
        self.logger.info("Starting scheduler...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about the bot's performance."""
        tracker_stats = self.application_tracker.get_statistics()
        
        return {
            'resume_loaded': self.resume_data is not None,
            'skills_extracted': len(self.resume_data['skills']) if self.resume_data else 0,
            'application_tracker_stats': tracker_stats,
            'config': self.config
        }
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive report of the bot's activities."""
        stats = self.get_statistics()
        weekly_report = self.application_tracker.generate_weekly_report()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'weekly_report': weekly_report,
            'resume_info': {
                'skills': self.resume_data['skills'] if self.resume_data else [],
                'contact_info': self.resume_data['contact_info'] if self.resume_data else {},
                'education': self.resume_data['education'] if self.resume_data else [],
                'experience': self.resume_data['experience'] if self.resume_data else []
            } if self.resume_data else None
        }
    
    def export_data(self, export_type: str = "excel"):
        """Export application data in various formats."""
        if export_type == "excel":
            self.application_tracker.export_to_excel()
        elif export_type == "csv":
            # CSV is already updated automatically
            print("CSV file updated automatically")
        elif export_type == "json":
            self.application_tracker.save_applications()
        else:
            self.logger.error(f"Unsupported export type: {export_type}")
    
    def _get_matching_skills(self, internship: Dict[str, Any]) -> List[str]:
        """Extract matching skills for an internship.
        
        Args:
            internship: The internship data dictionary
            
        Returns:
            List of matching skills
        """
        matching_skills = []
        
        # If the internship has a 'matched_skills' key, use it directly
        if 'matched_skills' in internship:
            return internship['matched_skills']
            
        # Otherwise, try to extract from the description using candidate skills
        if self.candidate_info and 'skills' in self.candidate_info and 'description' in internship:
            candidate_skills = self.candidate_info['skills']
            for skill in candidate_skills:
                # Simple case-insensitive check
                if skill.lower() in internship['description'].lower():
                    matching_skills.append(skill)
        
        return matching_skills
    
    def cleanup_duplicates(self):
        """Clean up duplicate applications."""
        self.application_tracker.clean_duplicates()
    
    def get_recent_applications(self, days: int = 7) -> List[Dict]:
        """Get recent applications from the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.application_tracker.get_applications_by_date_range(start_date, end_date)
    
    def update_config(self, new_config: Dict):
        """Update bot configuration."""
        self.config.update(new_config)
        self.logger.info("Configuration updated")
    
    def save_config(self, filename: str = "bot_config.json"):
        """Save current configuration to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info(f"Configuration saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def load_config(self, filename: str = "bot_config.json"):
        """Load configuration from file."""
        try:
            with open(filename, 'r') as f:
                self.config = json.load(f)
            self.logger.info(f"Configuration loaded from {filename}")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")

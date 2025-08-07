import time
import random
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright, Page
import os
from datetime import datetime
import json
import re
from openai import OpenAI
import logging

class ApplicationAutomator:
    def __init__(self, openai_api_key: str = None):
        """Initialize the application automator with OpenAI for cover letter generation."""
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.application_log = []
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for application tracking."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('application_log.txt'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def generate_cover_letter(self, job_title: str, company: str, job_description: str, 
                            candidate_info: Dict) -> str:
        """Generate personalized cover letter using OpenAI GPT."""
        if not self.openai_client:
            return self._generate_basic_cover_letter(job_title, company, candidate_info)
        
        try:
            prompt = f"""
            Generate a professional cover letter for the following internship position:
            
            Job Title: {job_title}
            Company: {company}
            Job Description: {job_description[:500]}...
            
            Candidate Information:
            - Skills: {', '.join(candidate_info.get('skills', []))}
            - Education: {candidate_info.get('education', [])}
            - Experience: {candidate_info.get('experience', [])}
            
            Please write a compelling cover letter that:
            1. Shows enthusiasm for the role and company
            2. Highlights relevant skills and experience
            3. Explains why the candidate is a good fit
            4. Is professional and well-structured
            5. Is around 200-300 words
            
            Cover Letter:
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional career advisor helping students write compelling cover letters for internships."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating cover letter with OpenAI: {e}")
            return self._generate_basic_cover_letter(job_title, company, candidate_info)
    
    def _generate_basic_cover_letter(self, job_title: str, company: str, candidate_info: Dict) -> str:
        """Generate a basic cover letter template."""
        skills = ', '.join(candidate_info.get('skills', [])[:5])
        
        cover_letter = f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} internship position at {company}. As a passionate student with skills in {skills}, I am excited about the opportunity to contribute to your team and gain valuable experience in the industry.

My academic background and hands-on projects have equipped me with the technical skills and problem-solving abilities needed for this role. I am particularly drawn to {company}'s innovative approach and the opportunity to work on meaningful projects that make a real impact.

I am confident that my combination of technical skills, enthusiasm for learning, and collaborative mindset would make me a valuable addition to your team. I am eager to bring my energy and fresh perspective to {company} and contribute to your continued success.

Thank you for considering my application. I look forward to discussing how I can contribute to your team.

Best regards,
[Your Name]
        """
        
        return cover_letter.strip()
    
    def apply_to_linkedin_job(self, page: Page, job_url: str, candidate_info: Dict) -> Dict:
        """Apply to a LinkedIn job posting."""
        try:
            page.goto(job_url)
            page.wait_for_load_state('networkidle')
            
            # Check if already applied
            already_applied = page.query_selector('[data-testid="already-applied"]')
            if already_applied:
                return {
                    'status': 'already_applied',
                    'message': 'Already applied to this position'
                }
            
            # Click apply button
            apply_button = page.query_selector('[data-testid="apply-button"]')
            if not apply_button:
                apply_button = page.query_selector('button:has-text("Apply")')
            
            if apply_button:
                apply_button.click()
                page.wait_for_load_state('networkidle')
                
                # Fill application form
                self._fill_linkedin_form(page, candidate_info)
                
                # Submit application
                submit_button = page.query_selector('button:has-text("Submit")')
                if submit_button:
                    submit_button.click()
                    page.wait_for_load_state('networkidle')
                    
                    return {
                        'status': 'success',
                        'message': 'Application submitted successfully'
                    }
            
            return {
                'status': 'error',
                'message': 'Could not find apply button or complete application'
            }
            
        except Exception as e:
            self.logger.error(f"Error applying to LinkedIn job: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _fill_linkedin_form(self, page: Page, candidate_info: Dict):
        """Fill LinkedIn application form fields."""
        try:
            # Fill personal information
            self._fill_text_field(page, 'input[name="firstName"]', candidate_info.get('first_name', ''))
            self._fill_text_field(page, 'input[name="lastName"]', candidate_info.get('last_name', ''))
            self._fill_text_field(page, 'input[name="email"]', candidate_info.get('email', ''))
            self._fill_text_field(page, 'input[name="phone"]', candidate_info.get('phone', ''))
            
            # Fill address if required
            self._fill_text_field(page, 'input[name="address"]', candidate_info.get('address', ''))
            self._fill_text_field(page, 'input[name="city"]', candidate_info.get('city', ''))
            self._fill_text_field(page, 'input[name="state"]', candidate_info.get('state', ''))
            self._fill_text_field(page, 'input[name="zip"]', candidate_info.get('zip', ''))
            
            # Fill education
            self._fill_text_field(page, 'input[name="school"]', candidate_info.get('school', ''))
            self._fill_text_field(page, 'input[name="degree"]', candidate_info.get('degree', ''))
            self._fill_text_field(page, 'input[name="fieldOfStudy"]', candidate_info.get('field_of_study', ''))
            
            # Fill experience
            self._fill_textarea_field(page, 'textarea[name="experience"]', candidate_info.get('experience_summary', ''))
            
            # Upload resume if field exists
            resume_field = page.query_selector('input[type="file"]')
            if resume_field and candidate_info.get('resume_path'):
                resume_field.set_input_files(candidate_info['resume_path'])
            
            # Add random delay to appear human
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            self.logger.error(f"Error filling LinkedIn form: {e}")
    
    def apply_to_internshala_job(self, page: Page, job_url: str, candidate_info: Dict) -> Dict:
        """This method has been removed as the application now focuses exclusively on LinkedIn.
        
        This is a placeholder method that returns an error status to maintain API compatibility.
        """
        self.logger.warning("ℹ️ Internshala application has been disabled. The application now focuses exclusively on LinkedIn.")
        return {
            'status': 'error',
            'message': 'Internshala application has been disabled. The application now focuses exclusively on LinkedIn.'
        }
    
    def _fill_internshala_form(self, page: Page, candidate_info: Dict):
        """This method has been removed as the application now focuses exclusively on LinkedIn.
        
        This is a placeholder method to maintain API compatibility.
        """
        self.logger.warning("ℹ️ Internshala form filling has been disabled. The application now focuses exclusively on LinkedIn.")
        pass
    
    def _fill_text_field(self, page: Page, selector: str, value: str):
        """Fill a text input field."""
        try:
            field = page.query_selector(selector)
            if field:
                field.fill(value)
                time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            self.logger.warning(f"Could not fill field {selector}: {e}")
    
    def _fill_textarea_field(self, page: Page, selector: str, value: str):
        """Fill a textarea field."""
        try:
            field = page.query_selector(selector)
            if field:
                field.fill(value)
                time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            self.logger.warning(f"Could not fill textarea {selector}: {e}")
    
    def handle_captcha(self, page: Page) -> bool:
        """Handle CAPTCHA if encountered."""
        try:
            # Check for common CAPTCHA elements
            captcha_selectors = [
                '.captcha',
                '#captcha',
                '[data-testid="captcha"]',
                'iframe[src*="captcha"]'
            ]
            
            for selector in captcha_selectors:
                captcha_element = page.query_selector(selector)
                if captcha_element:
                    self.logger.warning("CAPTCHA detected! Manual intervention required.")
                    # Wait for manual intervention
                    page.wait_for_timeout(30000)  # Wait 30 seconds
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling CAPTCHA: {e}")
            return False
    
    def apply_to_job(self, job_url: str, platform: str, candidate_info: Dict, 
                    job_description: str = "") -> Dict:
        """Apply to a job posting on any platform."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)  # Set to True for production
                page = browser.new_page()
                
                # Generate cover letter
                cover_letter = self.generate_cover_letter(
                    candidate_info.get('job_title', ''),
                    candidate_info.get('company', ''),
                    job_description,
                    candidate_info
                )
                candidate_info['cover_letter'] = cover_letter
                
                # Apply based on platform
                if platform.lower() == 'linkedin':
                    result = self.apply_to_linkedin_job(page, job_url, candidate_info)
                elif platform.lower() == 'internshala':
                    result = self.apply_to_internshala_job(page, job_url, candidate_info)
                else:
                    result = self.apply_to_generic_job(page, job_url, candidate_info)
                
                browser.close()
                
                # Log application
                application_log = {
                    'job_url': job_url,
                    'platform': platform,
                    'status': result['status'],
                    'message': result['message'],
                    'applied_at': datetime.now().isoformat(),
                    'cover_letter': cover_letter
                }
                
                self.application_log.append(application_log)
                self.logger.info(f"Application result: {result}")
                
                return result
                
        except Exception as e:
            self.logger.error(f"Error applying to job: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def apply_to_generic_job(self, page: Page, job_url: str, candidate_info: Dict) -> Dict:
        """Apply to a generic job posting with intelligent form detection."""
        try:
            page.goto(job_url)
            page.wait_for_load_state('networkidle')
            
            # Look for common apply button patterns
            apply_selectors = [
                'button:has-text("Apply")',
                'button:has-text("Apply Now")',
                'a:has-text("Apply")',
                '[data-testid="apply-button"]',
                '.apply-button',
                '#apply-button'
            ]
            
            apply_button = None
            for selector in apply_selectors:
                apply_button = page.query_selector(selector)
                if apply_button:
                    break
            
            if apply_button:
                apply_button.click()
                page.wait_for_load_state('networkidle')
                
                # Fill common form fields
                self._fill_generic_form(page, candidate_info)
                
                # Submit application
                submit_selectors = [
                    'button:has-text("Submit")',
                    'button:has-text("Send")',
                    'button[type="submit"]',
                    '.submit-button'
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    submit_button = page.query_selector(selector)
                    if submit_button:
                        break
                
                if submit_button:
                    submit_button.click()
                    page.wait_for_load_state('networkidle')
                    
                    return {
                        'status': 'success',
                        'message': 'Application submitted successfully'
                    }
            
            return {
                'status': 'error',
                'message': 'Could not find apply button or complete application'
            }
            
        except Exception as e:
            self.logger.error(f"Error applying to generic job: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _fill_generic_form(self, page: Page, candidate_info: Dict):
        """Fill generic form fields based on common patterns."""
        try:
            # Common field mappings
            field_mappings = {
                'name': ['input[name*="name"]', 'input[placeholder*="name"]'],
                'email': ['input[name*="email"]', 'input[type="email"]'],
                'phone': ['input[name*="phone"]', 'input[type="tel"]'],
                'address': ['input[name*="address"]', 'textarea[name*="address"]'],
                'city': ['input[name*="city"]'],
                'state': ['input[name*="state"]'],
                'zip': ['input[name*="zip"]', 'input[name*="postal"]'],
                'school': ['input[name*="school"]', 'input[name*="college"]', 'input[name*="university"]'],
                'degree': ['input[name*="degree"]', 'input[name*="course"]'],
                'experience': ['textarea[name*="experience"]', 'textarea[name*="background"]']
            }
            
            # Fill each field type
            for field_type, selectors in field_mappings.items():
                value = candidate_info.get(field_type, '')
                if value:
                    for selector in selectors:
                        field = page.query_selector(selector)
                        if field:
                            field.fill(value)
                            time.sleep(random.uniform(0.5, 1.5))
                            break
            
            # Handle file uploads
            file_inputs = page.query_selector_all('input[type="file"]')
            for file_input in file_inputs:
                if candidate_info.get('resume_path'):
                    file_input.set_input_files(candidate_info['resume_path'])
            
            # Add random delay
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            self.logger.error(f"Error filling generic form: {e}")
    
    def save_application_log(self, filename: str = "application_log.json"):
        """Save application log to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.application_log, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Application log saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving application log: {e}")
    
    def load_application_log(self, filename: str = "application_log.json") -> List[Dict]:
        """Load application log from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.info(f"Application log file {filename} not found")
            return []
        except Exception as e:
            self.logger.error(f"Error loading application log: {e}")
            return []
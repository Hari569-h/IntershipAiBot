import pdfplumber
import docx2txt
import re
import json
from typing import Dict, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from .ai_agents import MultiAgentAI

class ResumeParser:
    def __init__(self, config: Dict = None):
        """Initialize the resume parser with multi-agent AI support."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize multi-agent AI system
        self.ai_agents = MultiAgentAI(self.config)
        
        # Initialize sentence transformer for embeddings
        try:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("✅ Sentence transformer loaded successfully")
        except Exception as e:
            self.logger.error(f"❌ Error loading sentence transformer: {e}")
            self.sentence_transformer = None
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            self.logger.info(f"✅ Extracted {len(text)} characters from PDF")
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            text = docx2txt.process(docx_path)
            self.logger.info(f"✅ Extracted {len(text)} characters from DOCX")
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting text from DOCX: {e}")
            return ""
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume using multi-agent AI system."""
        try:
            # Extract text based on file type
            if file_path.lower().endswith('.pdf'):
                text = self.extract_text_from_pdf(file_path)
            elif file_path.lower().endswith('.docx'):
                text = self.extract_text_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
            
            if not text:
                raise ValueError("No text extracted from resume")
            
            # Use multi-agent AI to parse resume
            self.logger.info("🤖 Using multi-agent AI to parse resume...")
            
            # Try Groq first (primary model)
            parsed_data = self.ai_agents.parse_resume_with_groq(text)
            
            # If Groq fails, fallback to Gemini
            if not parsed_data or not parsed_data.get('skills'):
                self.logger.info("🔄 Falling back to Gemini for resume parsing...")
                parsed_data = self.ai_agents.parse_resume_with_gemini(text)
            
            # Add raw text to parsed data
            parsed_data['raw_text'] = text
            
            # Generate embeddings for the resume
            if self.sentence_transformer:
                try:
                    resume_embedding = self.sentence_transformer.encode(text)
                    parsed_data['embedding'] = resume_embedding.tolist()
                    self.logger.info("✅ Generated resume embedding")
                except Exception as e:
                    self.logger.error(f"❌ Error generating resume embedding: {e}")
            
            # Extract contact information
            contact_info = self.extract_contact_info(text)
            parsed_data['contact_info'] = contact_info
            
            self.logger.info(f"✅ Resume parsed successfully. Found {len(parsed_data.get('skills', []))} skills")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing resume: {e}")
            return self._default_resume_data()
    
    def extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from resume text."""
        contact_info = {
            'email': '',
            'phone': '',
            'linkedin': '',
            'github': '',
            'location': ''
        }
        
        try:
            # Extract email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, text)
            if email_match:
                contact_info['email'] = email_match.group()
            
            # Extract phone number
            phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
            phone_match = re.search(phone_pattern, text)
            if phone_match:
                contact_info['phone'] = ''.join(phone_match.groups())
            
            # Extract LinkedIn URL
            linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9-]+'
            linkedin_match = re.search(linkedin_pattern, text)
            if linkedin_match:
                contact_info['linkedin'] = f"https://www.{linkedin_match.group()}"
            
            # Extract GitHub URL
            github_pattern = r'github\.com/[a-zA-Z0-9-]+'
            github_match = re.search(github_pattern, text)
            if github_match:
                contact_info['github'] = f"https://www.{github_match.group()}"
            
            # Extract location (basic pattern)
            location_patterns = [
                r'([A-Z][a-z]+(?:[\s,]+[A-Z][a-z]+)*),\s*([A-Z]{2})',
                r'([A-Z][a-z]+(?:[\s,]+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)'
            ]
            
            for pattern in location_patterns:
                location_match = re.search(pattern, text)
                if location_match:
                    contact_info['location'] = location_match.group()
                    break
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting contact info: {e}")
        
        return contact_info
    
    def _default_resume_data(self) -> Dict:
        """Return default resume data structure."""
        return {
            'skills': [],
            'soft_skills': [],
            'education': '',
            'experience': [],
            'certifications': [],
            'domains': [],
            'contact_info': {},
            'raw_text': '',
            'embedding': []
        }
    
    def calculate_similarity(self, resume_embedding: np.ndarray, job_embedding: np.ndarray) -> float:
        """Calculate cosine similarity between resume and job embeddings with dimension checking."""
        try:
            # Check for None embeddings
            if resume_embedding is None or job_embedding is None:
                self.logger.error("❌ Null embeddings provided for similarity calculation")
                return 0.0
            
            # Ensure both are numpy arrays
            resume_vec = np.array(resume_embedding) if not isinstance(resume_embedding, np.ndarray) else resume_embedding
            job_vec = np.array(job_embedding) if not isinstance(job_embedding, np.ndarray) else job_embedding
            
            # Check for dimension mismatch
            if resume_vec.shape != job_vec.shape:
                self.logger.error(f"❌ Embedding dimension mismatch: resume={resume_vec.shape}, job={job_vec.shape}")
                return 0.0
            
            # Debug embedding dimensions
            self.logger.debug(f"🔍 Resume embedding dim: {len(resume_vec)}")
            self.logger.debug(f"🧾 Job embedding dim: {len(job_vec)}")
            
            # Calculate cosine similarity
            dot_product = np.dot(resume_vec, job_vec)
            norm_resume = np.linalg.norm(resume_vec)
            norm_job = np.linalg.norm(job_vec)
            
            # Check for zero vectors
            if norm_resume == 0 or norm_job == 0:
                self.logger.warning("⚠️ Zero vector detected in similarity calculation")
                return 0.0
            
            similarity = dot_product / (norm_resume * norm_job)
            
            # Ensure the result is within [-1, 1] range
            similarity = max(-1.0, min(1.0, similarity))
            
            # Convert to a 0-1 range for easier interpretation
            normalized_similarity = (similarity + 1) / 2
            
            self.logger.debug(f"✅ Calculated similarity score: {normalized_similarity:.4f}")
            return float(normalized_similarity)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    def get_skills_summary(self, resume_data: Dict) -> Dict:
        """Get a summary of skills from parsed resume data."""
        try:
            skills = resume_data.get('skills', [])
            soft_skills = resume_data.get('soft_skills', [])
            experience = resume_data.get('experience', [])
            education = resume_data.get('education', '')
            certifications = resume_data.get('certifications', [])
            domains = resume_data.get('domains', [])
            
            return {
                'technical_skills_count': len(skills),
                'soft_skills_count': len(soft_skills),
                'experience_count': len(experience),
                'certifications_count': len(certifications),
                'domains_count': len(domains),
                'education': education,
                'skills_list': skills,
                'soft_skills_list': soft_skills,
                'experience_list': experience,
                'certifications_list': certifications,
                'domains_list': domains
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting skills summary: {e}")
            return {}
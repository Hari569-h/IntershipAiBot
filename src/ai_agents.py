import json
import requests
import openai
import google.generativeai as genai
import cohere
from typing import Dict, List, Optional, Any
import logging

class MultiAgentAI:
    """Multi-agent AI system using different models for specialized tasks."""
    
    def __init__(self, config: Dict):
        """Initialize the multi-agent AI system."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize API clients
        self._setup_apis()
        
    def _setup_apis(self):
        """Setup all API clients."""
        try:
            # OpenAI
            openai.api_key = self.config['openai_api_key']
            
            # Gemini
            genai.configure(api_key=self.config['gemini_api_key'])
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Cohere
            self.cohere_client = cohere.Client(self.config['cohere_api_key'])
            
            # Groq (using requests for now)
            self.groq_api_key = self.config['groq_api_key']
            self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
            
            # OpenRouter
            self.openrouter_api_key = self.config['openrouter_api_key']
            self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
            
        except Exception as e:
            self.logger.error(f"Error setting up APIs: {e}")
    
    def parse_resume_with_groq(self, resume_text: str) -> Dict:
        """Parse resume using Groq (LLaMA 3) for structured extraction."""
        try:
            prompt = f"""
            Analyze the following resume and extract structured information in JSON format.
            
            Resume:
            {resume_text}
            
            Extract and return ONLY a JSON object with the following structure:
            {{
                "skills": ["skill1", "skill2", "skill3"],
                "soft_skills": ["soft_skill1", "soft_skill2"],
                "education": "degree and institution",
                "experience": ["experience1", "experience2"],
                "certifications": ["cert1", "cert2"],
                "domains": ["domain1", "domain2"]
            }}
            
            Rules:
            - Only return valid JSON
            - Extract technical skills (programming languages, tools, frameworks)
            - Extract soft skills (communication, leadership, etc.)
            - Include education level and institution
            - List relevant work/internship experiences
            - Include certifications and courses
            - Identify career domains of interest
            """
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 1000
            }
            
            response = requests.post(self.groq_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            try:
                # Find JSON in the response
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                parsed_data = json.loads(json_str)
                
                self.logger.info("✅ Resume parsed successfully with Groq")
                return parsed_data
                
            except json.JSONDecodeError:
                self.logger.warning("⚠️ Failed to parse JSON from Groq response, trying Gemini")
                return self.parse_resume_with_gemini(resume_text)
                
        except Exception as e:
            self.logger.error(f"❌ Error parsing resume with Groq: {e}")
            return self.parse_resume_with_gemini(resume_text)
    
    def parse_resume_with_gemini(self, resume_text: str) -> Dict:
        """Parse resume using Gemini Pro 2.5 as fallback."""
        try:
            prompt = f"""
            Analyze this resume and extract structured information:
            
            {resume_text}
            
            Return ONLY a JSON object with this exact structure:
            {{
                "skills": ["skill1", "skill2", "skill3"],
                "soft_skills": ["soft_skill1", "soft_skill2"],
                "education": "degree and institution",
                "experience": ["experience1", "experience2"],
                "certifications": ["cert1", "cert2"],
                "domains": ["domain1", "domain2"]
            }}
            """
            
            response = self.gemini_model.generate_content(prompt)
            content = response.text
            
            # Extract JSON from response
            try:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                parsed_data = json.loads(json_str)
                
                self.logger.info("✅ Resume parsed successfully with Gemini")
                return parsed_data
                
            except json.JSONDecodeError:
                self.logger.error("❌ Failed to parse JSON from Gemini response")
                return self._default_resume_structure()
                
        except Exception as e:
            self.logger.error(f"❌ Error parsing resume with Gemini: {e}")
            return self._default_resume_structure()
    
    def _default_resume_structure(self) -> Dict:
        """Return default resume structure if parsing fails."""
        return {
            "skills": [],
            "soft_skills": [],
            "education": "",
            "experience": [],
            "certifications": [],
            "domains": []
        }
    
    def get_embeddings(self, texts: List[str], provider: str = "cohere", fallback_provider: str = "openai", force_dimension: int = 1024) -> List[List[float]]:
        """Get embeddings for a list of texts using specified provider with dimension enforcement.
        
        Args:
            texts: List of text strings to embed
            provider: Primary embedding provider ("cohere" or "openai")
            fallback_provider: Provider to use if primary fails
            force_dimension: Force embeddings to have this dimension (1024 for Cohere, 1536 for OpenAI)
                             Set to None to disable dimension enforcement
        
        Returns:
            List of embedding vectors with consistent dimensions
        """
        try:
            # Check for empty input
            if not texts or all(not text.strip() for text in texts):
                self.logger.error("❌ Empty texts provided for embedding generation")
                return []
                
            self.logger.info(f"Generating embeddings for {len(texts)} texts using {provider}")
            
            # If force_dimension is set, select the appropriate provider
            if force_dimension == 1024 and provider != "cohere" and self.cohere_client:
                self.logger.info(f"🔄 Switching to Cohere to enforce {force_dimension} dimensions")
                provider = "cohere"
            elif force_dimension == 1536 and provider != "openai" and self.openai_client:
                self.logger.info(f"🔄 Switching to OpenAI to enforce {force_dimension} dimensions")
                provider = "openai"
            
            # Always use the same provider for all texts in a batch to ensure consistent dimensions
            if provider == "cohere" and self.cohere_client:
                embeddings = self.generate_embeddings_with_cohere(texts)
                # Verify dimensions
                if embeddings and len(embeddings[0]) != 1024 and force_dimension == 1024:
                    self.logger.warning(f"⚠️ Cohere returned unexpected dimensions: {len(embeddings[0])}")
                    if fallback_provider:
                        return self.get_embeddings(texts, provider=fallback_provider, fallback_provider=None, force_dimension=force_dimension)
                return embeddings
                
            elif provider == "openai" and self.openai_client:
                embeddings = self.generate_embeddings_with_openai(texts)
                # Verify dimensions
                if embeddings and len(embeddings[0]) != 1536 and force_dimension == 1536:
                    self.logger.warning(f"⚠️ OpenAI returned unexpected dimensions: {len(embeddings[0])}")
                    if fallback_provider:
                        return self.get_embeddings(texts, provider=fallback_provider, fallback_provider=None, force_dimension=force_dimension)
                return embeddings
                
            else:
                # Fallback to available provider
                if self.cohere_client:
                    self.logger.info("🔄 Using Cohere as fallback embedding provider")
                    return self.generate_embeddings_with_cohere(texts)
                elif self.openai_client:
                    self.logger.info("🔄 Using OpenAI as fallback embedding provider")
                    return self.generate_embeddings_with_openai(texts)
                else:
                    raise ValueError("No embedding provider available")
                    
        except Exception as e:
            self.logger.error(f"❌ Embedding provider {provider} failed: {e}")
            if fallback_provider:
                self.logger.warning(f"🔄 Falling back to {fallback_provider} for all embeddings")
                return self.get_embeddings(texts, provider=fallback_provider, fallback_provider=None, force_dimension=force_dimension)
            else:
                self.logger.error("❌ All embedding providers failed")
                return []

    def generate_embeddings_with_cohere(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Cohere Embed v3 with enforced dimension check."""
        try:
            # Filter out empty texts
            filtered_texts = [text for text in texts if text and text.strip()]
            
            # Check if we have any valid texts after filtering
            if not filtered_texts:
                self.logger.warning("❌ Empty texts provided for Cohere embedding, returning empty list")
                return []
                
            # Log the number of texts being processed
            self.logger.info(f"Generating Cohere embeddings for {len(filtered_texts)} texts")
            
            # Initialize Cohere client and generate embeddings
            try:
                response = self.cohere_client.embed(
                    texts=filtered_texts,
                    model="embed-english-v3.0",
                    input_type="search_document"
                )
                embeddings = response.embeddings
                
                # Verify all embeddings have the expected dimension - STRICT enforcement
                expected_dim = 1024  # Cohere embed-english-v3.0 should be 1024 dimensions
                
                for i, emb in enumerate(embeddings):
                    if len(emb) != expected_dim:
                        self.logger.warning(f"⚠️ Cohere returned unexpected dimension: {len(emb)}, expected {expected_dim}")
                        # Instead of raising error, try to pad or truncate to expected dimension
                        if len(emb) > expected_dim:
                            embeddings[i] = emb[:expected_dim]  # Truncate
                        else:
                            # Pad with zeros
                            embeddings[i] = emb + [0.0] * (expected_dim - len(emb))
                
                self.logger.info(f"✅ Generated {len(embeddings)} Cohere embeddings with dimension {expected_dim}")
                return embeddings
            except Exception as cohere_error:
                self.logger.error(f"❌ Cohere API error: {cohere_error}")
                # Fall back to OpenAI
                return self.generate_embeddings_with_openai(filtered_texts)
                
        except Exception as e:
            self.logger.error(f"❌ Error in generate_embeddings_with_cohere: {e}")
            # If all else fails, return empty list
            return []

    def generate_embeddings_with_openai(self, texts: List[str]) -> List[List[float]]:
        try:
            # Check for empty texts
            if not texts or all(not text.strip() for text in texts):
                self.logger.error("❌ Empty texts provided for OpenAI embedding")
                return []
                
            # Log the number of texts being processed
            self.logger.info(f"Generating OpenAI embeddings for {len(texts)} texts")
            
            embeddings = []
            expected_dim = 1536  # OpenAI text-embedding-ada-002 should be 1536 dimensions
            
            for i, text in enumerate(texts):
                try:
                    response = openai.Embedding.create(
                        input=text,
                        model="text-embedding-ada-002"
                    )
                    emb = response['data'][0]['embedding']
                    
                    # Verify embedding dimension
                    if len(emb) != expected_dim:
                        self.logger.error(
                            f"❌ OpenAI embedding dimension mismatch for text {i}: got {len(emb)}, expected {expected_dim}"
                        )
                        continue
                        
                    embeddings.append(emb)
                except Exception as text_error:
                    self.logger.error(f"❌ OpenAI embedding failed for text {i}: {text_error}")
            
            # Check if we got embeddings for all texts
            if len(embeddings) != len(texts):
                self.logger.warning(f"⚠️ Only generated {len(embeddings)}/{len(texts)} OpenAI embeddings")
                
            # If we didn't get any embeddings, return empty list
            if not embeddings:
                self.logger.error("❌ Failed to generate any OpenAI embeddings")
                return []
                
            self.logger.info(f"✅ Generated {len(embeddings)} OpenAI embeddings with dimension {expected_dim}")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"❌ OpenAI embedding failed: {e}")
            return []

    def generate_cover_letter_with_openrouter(self, job_description: str, resume_data: Dict, company: str, position: str) -> str:
        """Generate professional cover letter using OpenRouter (Claude/Mistral)."""
        try:
            prompt = f"""
            Create a professional, personalized cover letter for the following position:
            
            Position: {position}
            Company: {company}
            Job Description: {job_description}
            
            Candidate Information:
            - Skills: {', '.join(resume_data.get('skills', []))}
            - Experience: {', '.join(resume_data.get('experience', []))}
            - Education: {resume_data.get('education', '')}
            - Certifications: {', '.join(resume_data.get('certifications', []))}
            
            Requirements:
            - Professional and engaging tone
            - Highlight relevant skills and experience
            - Show enthusiasm for the role and company
            - Keep it concise (200-300 words)
            - Include specific examples from experience
            - Address how you can contribute to the company
            """
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(self.openrouter_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            cover_letter = result['choices'][0]['message']['content']
            
            self.logger.info("✅ Cover letter generated successfully with OpenRouter")
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"❌ Error generating cover letter with OpenRouter: {e}")
            return self.generate_cover_letter_with_openai(job_description, resume_data, company, position)
    
    def generate_cover_letter_with_openai(self, job_description: str, resume_data: Dict, company: str, position: str) -> str:
        """Generate cover letter using OpenAI as fallback."""
        try:
            prompt = f"""
            Create a professional cover letter for:
            Position: {position}
            Company: {company}
            
            Job Description: {job_description}
            
            My Background:
            - Skills: {', '.join(resume_data.get('skills', []))}
            - Experience: {', '.join(resume_data.get('experience', []))}
            - Education: {resume_data.get('education', '')}
            
            Make it professional, engaging, and tailored to the role.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            cover_letter = response.choices[0].message.content
            self.logger.info("✅ Cover letter generated successfully with OpenAI")
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"❌ Error generating cover letter with OpenAI: {e}")
            return self._default_cover_letter(company, position)
    
    def _default_cover_letter(self, company: str, position: str) -> str:
        """Return a default cover letter if generation fails."""
        return f"""
        Dear Hiring Manager,
        
        I am writing to express my interest in the {position} position at {company}. I am excited about the opportunity to contribute to your team and believe my skills and experience align well with your requirements.
        
        I am a motivated and detail-oriented individual with a strong background in technology and problem-solving. I am eager to learn and grow in a dynamic environment like {company}.
        
        Thank you for considering my application. I look forward to discussing how I can contribute to your team.
        
        Best regards,
        [Your Name]
        """
    
    def calculate_similarity_score(self, resume_embedding: List[float], job_embedding: List[float]) -> float:
        import numpy as np
        try:
            # Check if embeddings are empty
            if not resume_embedding or not job_embedding:
                self.logger.error(f"❌ Empty embeddings detected: resume={bool(resume_embedding)}, job={bool(job_embedding)}")
                return 0.0
                
            # Check for dimension mismatch
            if len(resume_embedding) != len(job_embedding):
                self.logger.error(
                    f"❌ Embedding dimension mismatch: resume={len(resume_embedding)}, job={len(job_embedding)}"
                )
                # If dimensions don't match, we need to regenerate both embeddings using the same model
                # This is handled by the calling method, so we just return 0 here
                return 0.0
            
            # Log the embedding dimensions for debugging
            self.logger.debug(f"✅ Embeddings have matching dimensions: {len(resume_embedding)}")
            
            # Convert to numpy arrays and calculate cosine similarity
            v1, v2 = np.array(resume_embedding), np.array(job_embedding)
            
            # Check for zero vectors
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                self.logger.warning("⚠️ Zero vector detected in similarity calculation")
                return 0.0
                
            # Calculate cosine similarity
            similarity = float(np.dot(v1, v2) / (norm1 * norm2))
            
            # Ensure the result is within [-1, 1] range
            similarity = max(-1.0, min(1.0, similarity))
            
            # Convert to a 0-1 range for easier interpretation
            normalized_similarity = (similarity + 1) / 2
            
            self.logger.debug(f"✅ Calculated similarity score: {normalized_similarity:.4f}")
            return normalized_similarity
        except Exception as e:
            self.logger.error(f"❌ Error calculating similarity score: {e}")
            return 0.0
    
    def analyze_job_description(self, job_description: str) -> Dict:
        """Analyze job description to extract key requirements and skills."""
        try:
            prompt = f"""
            Analyze this job description and extract key information:
            
            {job_description}
            
            Return ONLY a JSON object with this structure:
            {{
                "required_skills": ["skill1", "skill2"],
                "preferred_skills": ["skill1", "skill2"],
                "experience_level": "entry/mid/senior",
                "job_type": "internship/full-time/part-time",
                "location": "remote/onsite/hybrid",
                "key_responsibilities": ["responsibility1", "responsibility2"]
            }}
            """
            
            # Try Groq first
            try:
                headers = {
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "llama3-70b-8192",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
                
                response = requests.post(self.groq_url, headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Extract JSON
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                parsed_data = json.loads(json_str)
                
                self.logger.info("✅ Job description analyzed successfully with Groq")
                return parsed_data
                
            except Exception:
                # Fallback to Gemini
                response = self.gemini_model.generate_content(prompt)
                content = response.text
                
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                parsed_data = json.loads(json_str)
                
                self.logger.info("✅ Job description analyzed successfully with Gemini")
                return parsed_data
                
        except Exception as e:
            self.logger.error(f"❌ Error analyzing job description: {e}")
            return {
                "required_skills": [],
                "preferred_skills": [],
                "experience_level": "entry",
                "job_type": "internship",
                "location": "remote",
                "key_responsibilities": []
            }
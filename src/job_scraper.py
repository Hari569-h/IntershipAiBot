import requests
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright
import re
from datetime import datetime, timedelta
import os
from fake_useragent import UserAgent
import random
from .job_cache import JobCache
import json
import pathlib
from typing import Dict, List, Optional, Union, Any

class JobScraper:
    def __init__(self):
        """Initialize the job scraper with browser automation."""
        self.ua = UserAgent()
        self.job_cache = JobCache()
        self.session = requests.Session()
        self.session.headers.update(self.get_random_headers())
        
        # Create cookies directory if it doesn't exist
        self.cookies_dir = pathlib.Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies'))
        self.cookies_dir.mkdir(exist_ok=True)
        
        # Cookie storage paths for LinkedIn
        self.storage_paths = {
            'linkedin': os.path.join(self.cookies_dir, 'linkedin_storage.json')
            # Internshala and Indeed paths removed as the scraper now focuses exclusively on LinkedIn
        }
        
        # Default to non-headless mode for first run or when CAPTCHA is detected
        self.non_headless_mode = os.environ.get('NON_HEADLESS_MODE', 'false').lower() == 'true'
        
    def get_random_headers(self):
        """Get random headers with realistic browser fingerprints to avoid detection."""
        # List of common browsers and their user agents
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }

    def human_delay(self, min_sec=7, max_sec=15):
        """Add a random delay to simulate human behavior."""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        
    def save_storage_state(self, context, platform: str):
        """Save browser storage state (cookies, localStorage) to a file.
        This method is intentionally disabled to prevent storage state saving.
        """
        print(f"ℹ️ Storage state saving is disabled for {platform}")
        return True
    
    def load_storage_state(self, platform: str) -> Optional[Dict]:
        """Load browser storage state from a file if it exists."""
        try:
            if platform in self.storage_paths:
                storage_path = self.storage_paths[platform]
                if os.path.exists(storage_path):
                    with open(storage_path, 'r') as f:
                        storage_state = json.load(f)
                    print(f"✅ Loaded {platform} storage state from {storage_path}")
                    return storage_state
        except Exception as e:
            print(f"❌ Error loading storage state: {e}")


        
    def login_to_linkedin(self, email: str, password: str) -> bool:
        """Login to LinkedIn and save cookies for future use.
        
        Args:
            email: LinkedIn account email
            password: LinkedIn account password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        platform = 'linkedin'
        login_success = False
        
        try:
            with sync_playwright() as p:
                # Configure browser with anti-detection measures
                browser = p.chromium.launch(
                    headless=not self.non_headless_mode,  # Use non-headless mode if enabled
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-site-isolation-trials',
                        '--disable-web-security',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )
                
                # Set random viewport size to appear more human-like
                viewport_width = random.randint(1366, 1920)
                viewport_height = random.randint(768, 1080)
                
                # Create browser context with enhanced anti-detection measures
                context = browser.new_context(
                    viewport={'width': viewport_width, 'height': viewport_height},
                    locale="en-US",
                    timezone_id="America/New_York",
                    java_script_enabled=True,
                    user_agent=random.choice([
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
                    ])
                )
                
                # Add init script to override navigator properties
                context.add_init_script('''
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                Object.defineProperty(navigator, 'plugins', { get: () => [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format' },
                    { name: 'Native Client', filename: 'internal-nacl-plugin', description: 'Native Client' }
                ]});
                ''')
                
                page = context.new_page()
                page.set_extra_http_headers(self.get_random_headers())
                
                # Navigate to login page
                print("🔐 Navigating to LinkedIn login page...")
                page.goto("https://www.linkedin.com/login")
                page.wait_for_load_state('networkidle')
                self.human_delay(3, 5)
                
                # Check for CAPTCHA
                if self.handle_captcha(page, context, platform):
                    print("CAPTCHA handled, continuing with login...")
                    # If we've switched to non-headless mode, save state and exit to restart
                    if self.non_headless_mode:
                        print("🔄 Exiting to restart in non-headless mode...")
                        return False
                
                # Fill login form
                try:
                    # Check if already logged in
                    if page.query_selector('.feed-identity-module__actor-meta') or \
                       page.query_selector('.global-nav__me-photo') or \
                       page.url.startswith("https://www.linkedin.com/feed/"):
                        print("✅ Already logged in to LinkedIn")
                        self.save_storage_state(context, platform)
                        browser.close()
                        return True
                    
                    # Fill email field
                    email_field = page.query_selector('#username')
                    if not email_field:
                        email_field = page.query_selector('input[name="session_key"]')
                    
                    if email_field:
                        email_field.fill(email)
                        self.human_delay(1, 2)
                    else:
                        print("❌ Could not find email field")
                        browser.close()
                        return False
                    
                    # Fill password field
                    password_field = page.query_selector('#password')
                    if not password_field:
                        password_field = page.query_selector('input[name="session_password"]')
                        
                    if password_field:
                        password_field.fill(password)
                        self.human_delay(1, 2)
                    else:
                        print("❌ Could not find password field")
                        browser.close()
                        return False
                    
                    # Click sign in button
                    sign_in_button = page.query_selector('button[type="submit"]')
                    if sign_in_button:
                        sign_in_button.click()
                        page.wait_for_load_state('networkidle')
                        self.human_delay(3, 5)
                    else:
                        print("❌ Could not find sign in button")
                        browser.close()
                        return False
                    
                    # Handle potential verification challenges
                    if page.url.startswith("https://www.linkedin.com/checkpoint/"):
                        print("⚠️ LinkedIn security verification required")
                        print("🔄 Waiting for manual verification in non-headless mode...")
                        
                        # If in headless mode, we need to restart in non-headless mode
                        if not self.non_headless_mode:
                            print("🔄 Please restart with non-headless mode to complete verification")
                            return False
                        
                        # Wait for manual verification (3 minutes)
                        print("⏳ Waiting for manual verification (3 minutes)...")
                        for i in range(36):  # 36 * 5 seconds = 180 seconds = 3 minutes
                            if page.url.startswith("https://www.linkedin.com/feed/"):
                                print("✅ Manual verification completed")
                                break
                            self.human_delay(4, 6)
                    
                    # Verify successful login
                    if page.url.startswith("https://www.linkedin.com/feed/") or \
                       page.query_selector('.feed-identity-module__actor-meta') or \
                       page.query_selector('.global-nav__me-photo'):
                        print("✅ Successfully logged in to LinkedIn")
                        login_success = True
                    else:
                        print("❌ Login verification failed")
                        # Debug page content to understand the issue
                        self.debug_page_content(page)
                        browser.close()
                        return False
                    
                    # Save cookies for future use
                    if login_success:
                        self.save_storage_state(context, platform)
                    
                except Exception as e:
                    print(f"❌ Error during login form submission: {e}")
                    browser.close()
                    return False
                
                # Close browser
                browser.close()
                
        except Exception as e:
            print(f"❌ Critical error in login_to_linkedin: {e}")
            return False
        
        return login_success

    def handle_captcha(self, page, context=None, platform=None):
        """Enhanced CAPTCHA detection and handling with manual intervention option."""
        # Check for standard CAPTCHA elements
        captcha_selectors = ['.captcha', '#captcha', '[data-testid="captcha"]', 'iframe[src*="captcha"]', '.g-recaptcha', 
                            'iframe[title*="recaptcha"]', 'div[class*="captcha"]', '#recaptcha', '.recaptcha']
        
        # Check for Cloudflare protection elements
        cloudflare_selectors = [
            '#challenge-running', 
            '#challenge-form',
            '#cf-challenge-running',
            '[class*="cf-"]',
            'iframe[src*="cloudflare"]',
            'h1:has-text("Additional security verification")',
            'h1:has-text("Checking if the site connection is secure")',
            'title:has-text("Just a moment")',
            'title:has-text("Attention Required")',
            'title:has-text("Security check")',
            'div:has-text("Please turn JavaScript on and reload the page")',
            'div:has-text("Please enable Cookies and reload the page")',
            'div:has-text("Please complete the security check to access")',
            'div:has-text("Verifying you are human")',
            'div:has-text("Additional Verification Required")',
            'div:has-text("Cloudflare")',
            'div:has-text("DDoS protection")',
            'div:has-text("Ray ID:")',
            'div:has-text("CF-RAY:")',
            'div:has-text("cf-")',
            'div:has-text("Please wait while we verify")',
            'div:has-text("This process is automatic")',
            'div:has-text("Your browser will redirect")',
            'div:has-text("Please stand by")',
            'div:has-text("This challenge must be embedded")',
            'div:has-text("Checking your browser")',
            'div:has-text("Browser check")',
            'div:has-text("Please complete the security check")',
            'div:has-text("Please complete this security check")',
            'div:has-text("Please wait...")',
            'div:has-text("Checking if the site connection is secure")',
            'div:has-text("Just a moment")',
            'div:has-text("Attention Required")',
            'div:has-text("Security check")',
            'div:has-text("Cloudflare is checking your browser")',
            'div:has-text("Cloudflare is currently checking your browser")',
            'div:has-text("Cloudflare is currently checking your browser for malicious activity")',
            'div:has-text("Cloudflare is currently checking your browser for malicious activity. Please wait while we verify")',
            'div:has-text("Cloudflare is currently checking your browser for malicious activity. Please wait while we verify your browser")',
            'div:has-text("Cloudflare is currently checking your browser for malicious activity. Please wait while we verify your browser. This process is automatic")',
            'div:has-text("Cloudflare is currently checking your browser for malicious activity. Please wait while we verify your browser. This process is automatic. Your browser will redirect")',
            'div:has-text("Cloudflare is currently checking your browser for malicious activity. Please wait while we verify your browser. This process is automatic. Your browser will redirect to your requested content shortly")',
            'div:has-text("Cloudflare is currently checking your browser for malicious activity. Please wait while we verify your browser. This process is automatic. Your browser will redirect to your requested content shortly. Please allow up to 5 seconds")',
            'div:has-text("Cloudflare is currently checking your browser for malicious activity. Please wait while we verify your browser. This process is automatic. Your browser will redirect to your requested content shortly. Please allow up to 5 seconds...")',
            'div:has-text("Cloudflare is currently checking your browser for malicious activity. Please wait while we verify your browser. This process is automatic. Your browser will redirect to your requested content shortly. Please allow up to 5 seconds...")'
        ]
        
        # Check for standard CAPTCHA
        for selector in captcha_selectors:
            if page.query_selector(selector):
                print("⚠️ CAPTCHA detected! Attempting to handle...")
                
                # Try to interact with the page to appear more human-like
                try:
                    # Simulate human-like behavior - move mouse randomly
                    page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                    
                    # Scroll down and up slightly to trigger any JavaScript events
                    page.mouse.wheel(0, 100)
                    time.sleep(random.uniform(1, 2))
                    page.mouse.wheel(0, -50)
                    
                    # Wait with progressive timeouts
                    for wait_time in [5, 10, 15, 30, 60]:
                        print(f"Waiting {wait_time} seconds for CAPTCHA to resolve...")
                        page.wait_for_timeout(wait_time * 1000)
                        
                        # Check if CAPTCHA is still present
                        if not any(page.query_selector(s) for s in captcha_selectors):
                            print("CAPTCHA appears to be resolved, continuing...")
                            return True
                    
                    # If we've waited and still have CAPTCHA, try manual intervention
                    print("⚠️ CAPTCHA detected! Switching to non-headless mode for manual solving...")
                    
                    # If we're in headless mode and have a context, save the current state and return
                    # to trigger a restart in non-headless mode
                    if context and platform:
                        self.non_headless_mode = True
                        print("🔄 Please restart the scraper with NON_HEADLESS_MODE=true to manually solve the CAPTCHA")
                        return True
                    
                    # If we're already in non-headless mode, wait for manual intervention
                    print("👤 Please solve the CAPTCHA manually. You have 3 minutes...")
                    page.wait_for_timeout(180000)  # Wait 3 minutes for manual intervention
                    
                    # Check if we're still on a CAPTCHA page
                    if any(page.query_selector(s) for s in captcha_selectors):
                        print("⚠️ CAPTCHA still present after timeout. Skipping this page.")
                        return True
                    else:
                        # CAPTCHA solved successfully, save the storage state
                        if context and platform:
                            print("✅ CAPTCHA solved successfully! Saving cookies...")
                            self.save_storage_state(context, platform)
                    
                    # If CAPTCHA is solved and we have a context, save the storage state
                    if context and platform:
                        print("✅ CAPTCHA solved manually! Saving cookies and storage state...")
                        self.save_storage_state(context, platform)
                        self.non_headless_mode = False  # Reset to headless mode for future runs
                    
                    print("CAPTCHA handled, continuing...")
                    return True
                except Exception as e:
                    print(f"Error during CAPTCHA handling: {e}")
                    return True
        
        # Check for Cloudflare protection
        for selector in cloudflare_selectors:
            try:
                if page.query_selector(selector):
                    print(f"⚠️ Cloudflare protection detected! ({selector})")
                    # Check page title for additional confirmation
                    title = page.title()
                    if any(phrase in title for phrase in ["Just a moment", "Attention Required", "Security check", "Cloudflare"]):
                        print(f"⚠️ Confirmed Cloudflare protection via title: {title}")
                    
                    # Try to interact with the page to appear more human-like
                    try:
                        # Simulate human-like behavior - move mouse randomly
                        page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                        
                        # Scroll down and up slightly to trigger any JavaScript events
                        page.mouse.wheel(0, 100)
                        time.sleep(random.uniform(1, 2))
                        page.mouse.wheel(0, -50)
                        
                        # Wait with progressive timeouts
                        for wait_time in [5, 10, 15, 30, 45]:
                            print(f"Waiting {wait_time} seconds for Cloudflare challenge to resolve...")
                            page.wait_for_timeout(wait_time * 1000)
                            
                            # Check if Cloudflare is still present
                            if not any(page.query_selector(s) for s in cloudflare_selectors):
                                print("Cloudflare challenge appears to be resolved, continuing...")
                                # Save the storage state if Cloudflare was successfully bypassed
                                if context and platform:
                                    print("✅ Cloudflare challenge solved! Saving cookies...")
                                    self.save_storage_state(context, platform)
                                return True
                        
                        # If we've waited and still have Cloudflare, try manual intervention
                        print("⚠️ Cloudflare protection still active. Switching to non-headless mode...")
                        
                        # If we're in headless mode and have a context, save the current state and return
                        # to trigger a restart in non-headless mode
                        if context and platform:
                            self.non_headless_mode = True
                            print("🔄 Please restart the scraper with NON_HEADLESS_MODE=true to manually solve the Cloudflare challenge")
                            return True
                        
                        # If we're already in non-headless mode, wait for manual intervention
                        print("👤 Please solve the Cloudflare challenge manually. You have 3 minutes...")
                        page.wait_for_timeout(180000)  # Wait 3 minutes for manual intervention
                        
                        # Check if we're still on a Cloudflare page
                        if any(page.query_selector(s) for s in cloudflare_selectors):
                            print("⚠️ Cloudflare challenge still present after timeout. Skipping this page.")
                            return True
                        else:
                            # Challenge solved successfully, save the storage state
                            if context and platform:
                                print("✅ Cloudflare challenge solved manually! Saving cookies...")
                                self.save_storage_state(context, platform)
                                self.non_headless_mode = False  # Reset to headless mode for future runs
                            return True
                    except Exception as e:
                        print(f"Error during Cloudflare handling: {e}")
                        return True
            except Exception as e:
                print(f"Error checking Cloudflare selector {selector}: {e}")
                continue
        
        return False

    def wait_for_content(self, page, timeout: int = 20000, retry_count: int = 4):
        """Wait for page content to load with enhanced error handling and retry mechanism."""
        for attempt in range(retry_count):
            try:
                # Set default navigation timeout
                page.set_default_navigation_timeout(timeout)
                
                # Wait for page to be ready with multiple load states
                for state in ['domcontentloaded', 'networkidle']:
                    try:
                        # Use shorter timeout for each state to avoid hanging
                        page.wait_for_load_state(state, timeout=min(timeout//2, 10000))
                        print(f"✅ Load state '{state}' reached successfully")
                    except Exception as e:
                        print(f"⚠️ Load state '{state}' not reached: {e}")
                        # If domcontentloaded fails, try to continue anyway
                        if state == 'networkidle':
                            # Try scrolling to trigger content loading
                            try:
                                page.evaluate("window.scrollTo(0, 100)")
                                time.sleep(1)
                            except Exception:
                                pass
                
                # Wait for body content with shorter timeout
                try:
                    page.wait_for_selector('body', timeout=min(timeout//3, 5000))
                    print("✅ Body element found")
                except Exception as e:
                    print(f"⚠️ Body selector not found: {e}")
                    # Try to continue anyway if we're on retry attempts
                
                # Check if page has actual content
                content_check = page.evaluate("""
                    () => {
                        const bodyText = document.body.innerText;
                        return {
                            textLength: bodyText.length,
                            hasContent: bodyText.length > 100,
                            hasLinks: document.querySelectorAll('a').length > 0
                        };
                    }
                """)
                
                if content_check.get('hasContent', False):
                    print(f"✅ Page loaded successfully with {content_check.get('textLength', 0)} characters")
                    return True
                else:
                    print(f"⚠️ Page loaded but may not have enough content: {content_check}")
                    if attempt < retry_count - 1:
                        print(f"Retrying content wait (attempt {attempt + 1}/{retry_count})")
                        # Scroll and wait before retry
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.3)")
                        time.sleep(3)
                    else:
                        # Last attempt, return anyway
                        return False
                        
            except Exception as e:
                print(f"⚠️ Timeout waiting for content: {e}")
                if attempt < retry_count - 1:
                    print(f"Retrying content wait (attempt {attempt + 1}/{retry_count})")
                    time.sleep(3)
                else:
                    return False
        
        return True
    
    def debug_page_content(self, page, platform: str):
        """Enhanced debug page content for troubleshooting with detailed element analysis."""
        try:
            print(f"🔍 Debugging {platform} page content...")
            
            # Get page title and URL
            title = page.title()
            url = page.url
            print(f"📄 Page title: {title}")
            print(f"🔗 Current URL: {url}")
            
            # Check for common elements
            body = page.query_selector('body')
            if body:
                body_text = body.inner_text()[:500]  # First 500 chars
                print(f"📝 Body content preview: {body_text}...")
                print(f"📊 Body content length: {len(body.inner_text())} characters")
            
            # Check for frames
            frames = page.frames
            print(f"🖼️ Number of frames: {len(frames)}")
            if len(frames) > 1:
                for i, frame in enumerate(frames):
                    try:
                        frame_url = frame.url
                        print(f"  Frame {i}: URL={frame_url}, Name={frame.name}")
                    except Exception:
                        print(f"  Frame {i}: [Error accessing frame]")
            
            # Check for common job-related elements with more detailed selectors
            job_selectors = [
                '[class*="job"]', '[class*="internship"]', '[data-testid*="job"]',
                '.jobsearch-ResultsList', '.job_seen_beacon', '.tapItem', '.result',
                'div[id*="job"]', 'article', '.css-5lfssm', '.job-card', '.jobCard'
            ]
            
            print("💼 Job element detection:")
            for selector in job_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        print(f"  ✅ Found {len(elements)} elements matching '{selector}'")
                        # Show sample of first element if available
                        if len(elements) > 0:
                            try:
                                sample_text = elements[0].inner_text().strip()[:100]
                                print(f"    Sample: {sample_text}...")
                            except Exception:
                                pass
                    else:
                        print(f"  ❌ No elements found for '{selector}'")
                except Exception as sel_err:
                    print(f"  ⚠️ Error checking selector '{selector}': {sel_err}")
            
            # Check for common error indicators
            error_selectors = [
                '[class*="error"]', '[class*="captcha"]', '[class*="blocked"]',
                '[class*="security"]', '#challenge-running', '#cf-error-details'
            ]
            
            print("🚨 Error element detection:")
            for selector in error_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        print(f"  ⚠️ Found {len(elements)} potential error elements matching '{selector}'")
                        # Show sample of first element if available
                        if len(elements) > 0:
                            try:
                                sample_text = elements[0].inner_text().strip()[:100]
                                print(f"    Error text: {sample_text}...")
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception as e:
            print(f"❌ Error during page content debugging: {e}")
            
        
    def filter_jobs(self, jobs, keywords, resume_embedding, ai_agents):
        filtered = []
        for job in jobs:
            job_id = job.get('id') or job.get('link') or job.get('title')
            if self.job_cache.exists(job_id):
                continue
            if any(kw.lower() in job['title'].lower() for kw in keywords):
                filtered.append(job)
            elif job.get('description') and job['description'].strip() and resume_embedding and ai_agents:
                try:
                    # Only attempt embedding if we have a non-empty description
                    job_emb = ai_agents.generate_embeddings_with_cohere([job['description']])
                    if job_emb and len(job_emb) > 0:
                        sim = ai_agents.calculate_similarity_score(resume_embedding, job_emb[0])
                        if sim > 0.8:
                            filtered.append(job)
                except Exception as e:
                    print(f"Error during job filtering: {e}")
                    # If embedding fails, include the job based on keywords only
                    if any(kw.lower() in job['description'].lower() for kw in keywords):
                        filtered.append(job)
        return filtered

    def scrape_linkedin_internships(self, keywords: List[str] = None, location: str = None) -> List[Dict]:
        """Scrape internships from LinkedIn with improved selectors and error handling."""
        if keywords is None:
            keywords = ["internship", "software", "data", "engineering", "development"]
        
        # If location is None, don't filter by location
        location_param = "" if location is None else location
        
        internships = []
        platform = 'linkedin'
        
        try:
            with sync_playwright() as p:
                # Configure browser with anti-detection measures
                browser = p.chromium.launch(
                    headless=not self.non_headless_mode,  # Use non-headless mode if enabled
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-site-isolation-trials',
                        '--disable-web-security',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )
                
                # Set random viewport size to appear more human-like
                viewport_width = random.randint(1366, 1920)
                viewport_height = random.randint(768, 1080)
                
                # Try to load saved storage state (cookies)
                storage_state = self.load_storage_state(platform)
                
                # Create browser context with enhanced anti-detection measures
                context = browser.new_context(
                    viewport={'width': viewport_width, 'height': viewport_height},
                    locale="en-US",
                    timezone_id="America/New_York",
                    java_script_enabled=True,
                    storage_state=storage_state,  # Load cookies if available
                    user_agent=random.choice([
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
                    ])
                )
                
                # Add init script to override navigator properties
                context.add_init_script('''
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                Object.defineProperty(navigator, 'plugins', { get: () => [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format' },
                    { name: 'Native Client', filename: 'internal-nacl-plugin', description: 'Native Client' }
                ]});
                ''')
                
                page = context.new_page()
                page.set_extra_http_headers(self.get_random_headers())
                page.set_default_navigation_timeout(30000)  # Increased timeout
                
                for keyword in keywords:
                    try:
                        # LinkedIn internship search URL with more general terms
                        search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&f_E=1&f_JT=I&position=1&pageNum=0"
                        # Add location parameter only if it's provided
                        if location_param:
                            search_url += f"&location={location_param}"
                        
                        print(f"🔍 Searching LinkedIn for: {keyword}")
                        page.goto(search_url)
                        
                        # Wait for content to load
                        self.wait_for_content(page)
                        
                        # Handle CAPTCHA if present
                        if self.handle_captcha(page, context, platform):
                            print("CAPTCHA handled, continuing...")
                            # If we've switched to non-headless mode, save state and exit to restart
                            if self.non_headless_mode:
                                print("🔄 Exiting to restart in non-headless mode...")
                                return internships
                        
                        # Debug page content if no jobs found
                        if not page.query_selector_all('.job-search-card, .job-card-container, [data-testid="job-card"]'):
                            self.debug_page_content(page, "LinkedIn")
                        
                        # Scroll to load more jobs
                        for _ in range(3):
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            time.sleep(random.uniform(2, 4))
                        
                        # Try multiple selectors for job cards with waiting
                        job_card_selectors = [
                            '.job-search-card',
                            '.job-card-container',
                            '[data-testid="job-card"]',
                            '.job-card',
                            '.job-search-card__container'
                        ]
                        
                        job_cards = []
                        for selector in job_card_selectors:
                            try:
                                # Wait for selector with timeout
                                page.wait_for_selector(selector, timeout=5000)
                                job_cards = page.query_selector_all(selector)
                                if job_cards:
                                    print(f"✅ Found {len(job_cards)} jobs with selector: {selector}")
                                    break
                            except Exception as e:
                                print(f"⚠️ Selector {selector} not found: {e}")
                                continue
                        
                        if not job_cards:
                            # Try alternative approach
                            try:
                                job_cards = page.query_selector_all('li')
                                job_cards = [card for card in job_cards if card.query_selector('a[href*="/jobs/"]')]
                                print(f"✅ Found {len(job_cards)} jobs with alternative approach")
                            except Exception as e:
                                print(f"⚠️ Alternative approach failed: {e}")
                                continue
                        
                        for card in job_cards[:10]:  # Limit to 10 jobs per keyword
                            try:
                                # Extract job information with multiple selector attempts
                                title = ""
                                company = ""
                                location = ""
                                job_link = ""
                                
                                # Try multiple selectors for title
                                title_selectors = [
                                    '.job-search-card__title',
                                    '.job-card-list__title',
                                    '[data-testid="job-title"]',
                                    'h3',
                                    'h4',
                                    '.job-title'
                                ]
                                
                                for selector in title_selectors:
                                    try:
                                        title_elem = card.query_selector(selector)
                                        if title_elem:
                                            title = title_elem.inner_text().strip()
                                            break
                                    except Exception:
                                        continue
                                
                                # Try multiple selectors for company
                                company_selectors = [
                                    '.job-search-card__subtitle',
                                    '.job-card-list__company',
                                    '[data-testid="company-name"]',
                                    '.company-name'
                                ]
                                
                                for selector in company_selectors:
                                    try:
                                        company_elem = card.query_selector(selector)
                                        if company_elem:
                                            company = company_elem.inner_text().strip()
                                            break
                                    except Exception:
                                        continue
                                
                                # Try multiple selectors for location
                                location_selectors = [
                                    '.job-search-card__location',
                                    '.job-card-list__location',
                                    '[data-testid="job-location"]',
                                    '.job-location'
                                ]
                                
                                for selector in location_selectors:
                                    try:
                                        location_elem = card.query_selector(selector)
                                        if location_elem:
                                            location = location_elem.inner_text().strip()
                                            break
                                    except Exception:
                                        continue
                                
                                # Get job link
                                try:
                                    link_elem = card.query_selector('a[href*="/jobs/"]')
                                    if link_elem:
                                        job_link = link_elem.get_attribute('href')
                                        if job_link and not job_link.startswith('http'):
                                            job_link = "https://www.linkedin.com" + job_link
                                except Exception:
                                    pass
                                
                                if title and company:
                                    internship = {
                                        'title': title,
                                        'company': company,
                                        'location': location,
                                        'link': job_link,
                                        'platform': 'LinkedIn',
                                        'keywords': keyword,
                                        'scraped_at': datetime.now().isoformat()
                                    }
                                    
                                    # Get detailed job description if link is available
                                    if job_link:
                                        try:
                                            internship['description'] = self._get_linkedin_job_description(page, job_link, context, platform)
                                        except Exception as e:
                                            print(f"⚠️ Error getting description: {e}")
                                            internship['description'] = ""
                                    
                                    internships.append(internship)
                                    print(f"✅ Found: {title} at {company}")
                                
                            except Exception as e:
                                print(f"⚠️ Error extracting LinkedIn job: {e}")
                                continue
                        
                        # Add delay between keywords
                        time.sleep(random.uniform(3, 6))
                        
                    except Exception as e:
                        print(f"⚠️ Error searching LinkedIn for {keyword}: {e}")
                        continue
                
                # Save storage state before closing browser
                self.save_storage_state(context, platform)
                browser.close()
                
        except Exception as e:
            print(f"❌ Error scraping LinkedIn: {e}")
        
        return internships
    
    def _get_linkedin_job_description(self, page, job_url: str, context=None, platform='linkedin') -> str:
        """Get detailed job description from LinkedIn job page."""
        try:
            page.goto(job_url)
            self.wait_for_content(page)
            
            # Handle CAPTCHA if present
            if self.handle_captcha(page, context, platform):
                print("CAPTCHA handled on job page...")
                # If we've switched to non-headless mode, exit to restart
                if self.non_headless_mode:
                    print("🔄 Exiting to restart in non-headless mode...")
                    return ""
            
            # Try multiple selectors for description
            description_selectors = [
                '.description__text',
                '.job-description',
                '[data-testid="job-description"]',
                '.show-more-less-html__markup',
                '.job-description__content'
            ]
            
            for selector in description_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    description_elem = page.query_selector(selector)
                    if description_elem:
                        return description_elem.inner_text().strip()
                except Exception:
                    continue
            
        except Exception as e:
            print(f"Error getting LinkedIn job description: {e}")
        
        return ""
    
    # Placeholder methods for API compatibility
    
    def _get_internshala_job_description(self, page, job_url: str, context=None, platform=None) -> str:
        """This method has been removed as the scraper now focuses exclusively on LinkedIn.
        
        This is a placeholder method that returns an empty string to maintain API compatibility.
        """
        return ""
    
    def _get_indeed_job_description(self, page, job_url: str, context=None, platform=None) -> str:
        """This method has been removed as the scraper now focuses exclusively on LinkedIn.
        
        This is a placeholder method that returns an empty string to maintain API compatibility.
        """
        return ""
    
    
    def scrape_all_platforms(self, keywords: List[str] = None, location: str = None) -> List[Dict]:
        """Scrape internships from LinkedIn only."""
        # Use more general keywords if none provided
        if keywords is None:
            keywords = [
                "internship", "software", "data", "engineering", "development",
                "python", "javascript", "react", "node", "machine learning",
                "frontend", "backend", "full stack", "web development", "programming",
                "computer science", "information technology", "software engineering",
                "data science", "artificial intelligence", "mobile development",
                "cloud computing", "cybersecurity", "database", "devops"
            ]
        
        print(f"🔍 Starting LinkedIn internship search with keywords: {keywords}")
        
        # Scrape LinkedIn only
        print("\n📊 Scraping LinkedIn internships...")
        linkedin_internships = self.scrape_linkedin_internships(keywords, location)
        print(f"✅ Found {len(linkedin_internships)} LinkedIn internships")
        
        print(f"\n🎯 Total internships found: {len(linkedin_internships)}")
        return linkedin_internships
    
    def save_internships_to_json(self, internships: List[Dict], filename: str = "scraped_internships.json"):
        """Save scraped internships to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(internships, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(internships)} internships to {filename}")
        except Exception as e:
            print(f"❌ Error saving internships: {e}")
    
    def load_internships_from_json(self, filename: str = "scraped_internships.json") -> List[Dict]:
        """Load internships from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ File {filename} not found")
            return []
        except Exception as e:
            print(f"❌ Error loading internships: {e}")
            return []


# Add a main function to test the functionality when the file is run directly
if __name__ == "__main__":
    print("Initializing JobScraper...")
    scraper = JobScraper()
    print("JobScraper initialized successfully!")
    
    # Example of how to use the scraper
    print("\nExample usage:")
    keywords = ["software", "internship"]
    location = "United States"
    print(f"Keywords: {keywords}")
    print(f"Location: {location}")
    print("To scrape internships, uncomment the following lines:")
    # internships = scraper.scrape_all_platforms(keywords, location)
    # scraper.save_internships_to_json(internships, "test_internships.json")
import os
import time
import logging
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinkedInLogin:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.base_url = "https://www.linkedin.com"
        self.timeout = 30000  # 30 seconds timeout
        self.max_retries = 3
        self.browser = None
        self.page = None
        self.playwright = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, slow_mo=100)
        self.page = self.browser.new_page()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def handle_captcha(self):
        """Handle CAPTCHA if it appears during login"""
        try:
            # Check if CAPTCHA is present
            if self.page.is_visible("iframe[title*='captcha']"):
                logger.warning("CAPTCHA detected. Please solve it manually...")
                # Wait for user to solve CAPTCHA
                self.page.wait_for_selector("iframe[title*='captcha']", state="hidden", timeout=120000)
                return True
            return False
        except Exception as e:
            logger.error(f"Error handling CAPTCHA: {e}")
            return False

    def handle_mfa(self):
        """Handle Multi-Factor Authentication if required"""
        try:
            # Check if MFA is required
            if self.page.is_visible("input[autocomplete='one-time-code']"):
                logger.warning("MFA required. Please enter the code sent to your device...")
                # Wait for user to enter MFA code
                self.page.wait_for_selector("button:has-text('Submit')", timeout=120000)
                return True
            return False
        except Exception as e:
            logger.error(f"Error handling MFA: {e}")
            return False

    def login(self):
        """Login to LinkedIn with retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to login to LinkedIn (Attempt {attempt + 1}/{self.max_retries})")
                
                # Navigate to LinkedIn login page
                self.page.goto(f"{self.base_url}/login", timeout=self.timeout)
                
                # Fill in email and password
                self.page.fill('input[name="username"]', self.email)
                self.page.fill('input[name="password"]', self.password)
                
                # Click login button
                self.page.click('button[type="submit"]')
                
                # Wait for navigation or CAPTCHA/MFA
                try:
                    # Wait for either the feed to load or CAPTCHA/MFA to appear
                    self.page.wait_for_selector(
                        "div.feed-identity-module__actor-meta:has-text('Feed')", 
                        timeout=10000
                    )
                    logger.info("Successfully logged in to LinkedIn")
                    return True
                    
                except PlaywrightTimeoutError:
                    # Check for CAPTCHA or MFA
                    if self.handle_captcha() or self.handle_mfa():
                        # Wait for login to complete after CAPTCHA/MFA
                        self.page.wait_for_selector(
                            "div.feed-identity-module__actor-meta:has-text('Feed')", 
                            timeout=60000
                        )
                        logger.info("Successfully logged in after CAPTCHA/MFA")
                        return True
                    
                    # If we get here, login might have failed
                    logger.warning("Login attempt failed. Retrying...")
                    time.sleep(2)  # Small delay before retry
            
            except Exception as e:
                logger.error(f"Error during login attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:  # Last attempt
                    logger.error("Max login attempts reached. Please check your credentials and try again.")
                    return False
                time.sleep(2)  # Small delay before retry
        
        return False

    def is_logged_in(self):
        """Check if the user is logged in"""
        try:
            self.page.goto(f"{self.base_url}/feed", timeout=self.timeout)
            return "feed" in self.page.url
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

def main():
    with LinkedInLogin() as linkedin:
        if linkedin.login():
            logger.info("Successfully logged in to LinkedIn")
            # Keep the browser open for a while to verify login
            time.sleep(5)
        else:
            logger.error("Failed to log in to LinkedIn")

if __name__ == "__main__":
    main()

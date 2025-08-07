import os
import smtplib
import ssl
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional

class EmailNotifier:
    """Email notification system for successful internship applications."""
    
    def __init__(self, config: Dict = None):
        """Initialize the email notifier with configuration."""
        self.config = config or {}
        self.setup_logging()
        
        # Email configuration
        self.sender_email = os.getenv('EMAIL_SENDER', '')
        self.sender_password = os.getenv('EMAIL_PASSWORD', '')
        self.recipient_email = os.getenv('EMAIL_RECIPIENT', self.sender_email)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        
        # Retry configuration
        self.max_retries = int(os.getenv('EMAIL_MAX_RETRIES', 3))
        self.retry_delay = int(os.getenv('EMAIL_RETRY_DELAY', 5))
        
        # Validate configuration
        self.is_configured = self._validate_config()
        
    def setup_logging(self):
        """Setup logging for email notifications."""
        self.logger = logging.getLogger(__name__)
        
    def _validate_config(self) -> bool:
        """Validate that email configuration is complete."""
        required_fields = ['sender_email', 'sender_password', 'smtp_server', 'smtp_port']
        
        for field in required_fields:
            if not getattr(self, field, None):
                self.logger.warning(f"Missing required email configuration: {field}")
                return False
                
        return True
    
    def send_application_notification(self, 
                                     job_title: str, 
                                     company_name: str, 
                                     platform: str,
                                     matching_skills: List[str],
                                     resume_file: str,
                                     timestamp: str = None,
                                     additional_info: Dict = None) -> bool:
        """Send email notification for successful application."""
        if not self.is_configured:
            self.logger.warning("Email notification not configured. Skipping notification.")
            return False
            
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        # Create email content
        subject = f"✅ Successfully Applied: {job_title} at {company_name}"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
                <h2 style="color: #4CAF50; border-bottom: 1px solid #eee; padding-bottom: 10px;">Successful Internship Application</h2>
                
                <div style="margin: 20px 0;">
                    <p><strong>Job Title:</strong> {job_title}</p>
                    <p><strong>Company:</strong> {company_name}</p>
                    <p><strong>Platform:</strong> {platform}</p>
                    <p><strong>Applied At:</strong> {timestamp}</p>
                    <p><strong>Resume Used:</strong> {os.path.basename(resume_file)}</p>
                </div>
                
                <div style="margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #2196F3;">Matching Skills:</h3>
                    <ul style="padding-left: 20px;">
        """
        
        # Add matching skills
        for skill in matching_skills:
            html_content += f"<li>{skill}</li>\n"
            
        html_content += """
                    </ul>
                </div>
        """
        
        # Add additional info if provided
        if additional_info:
            html_content += """        
                <div style="margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2196F3;">Additional Information:</h3>
                    <ul style="padding-left: 20px;">
            """
            
            for key, value in additional_info.items():
                html_content += f"<li><strong>{key}:</strong> {value}</li>\n"
                
            html_content += """
                    </ul>
                </div>
            """
            
        # Close HTML content
        html_content += """
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; color: #777; font-size: 0.9em;">
                    <p>This is an automated notification from your Internship Application Bot.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
        Successful Internship Application
        
        Job Title: {job_title}
        Company: {company_name}
        Platform: {platform}
        Applied At: {timestamp}
        Resume Used: {os.path.basename(resume_file)}
        
        Matching Skills:
        {', '.join(matching_skills)}
        
        This is an automated notification from your Internship Application Bot.
        """
        
        # Send the email with retry logic
        return self._send_email_with_retry(subject, html_content, text_content)
    
    def _send_email_with_retry(self, subject: str, html_content: str, text_content: str) -> bool:
        """Send email with retry logic."""
        retries = 0
        
        while retries < self.max_retries:
            try:
                return self._send_email(subject, html_content, text_content)
            except Exception as e:
                retries += 1
                self.logger.error(f"Email sending failed (attempt {retries}/{self.max_retries}): {e}")
                
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Failed to send email after {self.max_retries} attempts")
                    return False
    
    def _send_email(self, subject: str, html_content: str, text_content: str) -> bool:
        """Send email using SMTP."""
        try:
            # Create message container
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = self.recipient_email
            
            # Attach parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            message.attach(part1)
            message.attach(part2)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            
            self.logger.info(f"Email notification sent successfully: {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"Error sending email: {e}")
            self.logger.error("Authentication failed. If using Gmail, make sure you're using an App Password, not your regular password.")
            self.logger.error("See EMAIL_NOTIFICATION.md for instructions on creating an App Password.")
            raise
        except smtplib.SMTPConnectError as e:
            self.logger.error(f"Error connecting to SMTP server: {e}")
            self.logger.error(f"Check that your SMTP server ({self.smtp_server}) and port ({self.smtp_port}) are correct.")
            raise
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            raise
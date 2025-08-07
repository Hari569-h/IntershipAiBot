# Email Notification System for Internship Bot

The email notification system automatically sends notifications when the bot successfully applies to internship positions. This document explains how to set up and use this feature.

## Setup

### 1. Configure Email Settings

Add the following settings to your `.env` file:

```
# Email Notification Settings
EMAIL_SENDER=your.email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=your.email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_MAX_RETRIES=3
EMAIL_RETRY_DELAY=5
EMAIL_NOTIFICATIONS_ENABLED=True
```

### 2. Gmail App Password

If you're using Gmail, you'll need to create an App Password:

1. Go to your Google Account settings
2. Navigate to Security > 2-Step Verification
3. Scroll down and select "App passwords"
4. Create a new app password for "Mail" and "Other (Custom name)"
5. Use the generated password as your `EMAIL_PASSWORD` in the `.env` file

## Features

The email notification system provides the following features:

- **HTML and Plain Text Emails**: Sends both HTML-formatted and plain text emails for compatibility
- **Detailed Application Information**: Includes job title, company, platform, and matching skills
- **Retry Logic**: Automatically retries sending emails if there are temporary failures
- **Configurable Settings**: Customize SMTP server, port, retry attempts, and more

## Email Content

Each notification email includes:

- Job title and company name
- Platform where the application was submitted
- Timestamp of the application
- Resume file used for the application
- List of matching skills between your resume and the job description
- Additional information like job link, similarity score, and location

## Testing

You can test the email notification system by running the test script:

```bash
python test_email_notification.py
```

This script will send a test email to verify that your configuration is working correctly.

## Troubleshooting

### Common Issues

1. **Authentication Failed (Username and Password not accepted)**: This is the most common error, especially with Gmail. It occurs when:
   - You're using your regular Gmail password instead of an App Password
   - The App Password is incorrect or has expired
   - Your account has additional security settings that block the connection
   
   **Solution**: Create a new App Password specifically for this application following the steps in the setup section above.

2. **Connection Refused**: Verify that the SMTP server and port are correct and that your network allows connections to these services.

3. **Timeout**: If the connection times out, check your internet connection and try again.

4. **Email Not Received**: Check your spam folder. Some email providers may mark automated emails as spam.

### Logs

Check the application logs for detailed error messages if you're having trouble with email notifications. The system logs all email sending attempts and errors.

## Disabling Notifications

To disable email notifications, set `EMAIL_NOTIFICATIONS_ENABLED=False` in your `.env` file.
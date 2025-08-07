# Cloud Deployment Guide for AI Internship Application Bot

This guide provides step-by-step instructions for deploying your AI Internship Application Bot to cloud platforms for fully automated operation every 3 hours.

## Option 1: Deploy to Render (Free & Cloud-Hosted)

Render is perfect for this use case as it provides free cron job services that can run your automation script on a schedule.

### Step 1: Push Your Code to GitHub

1. Create a private GitHub repository
2. Push your full project (including run_automation.py, .env, etc.)
3. Make sure the render.yaml file is included in your repository

### Step 2: Connect to Render

1. Create a Render account at [render.com](https://render.com)
2. Go to the Dashboard and click "New +" > "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the render.yaml file and set up your cron job

### Step 3: Configure Environment Variables

1. In the Render dashboard, navigate to your cron job service
2. Go to the "Environment" tab
3. Add all the environment variables from your .env file
4. Make sure to mark sensitive variables (like API keys and passwords) as secret

### Step 4: Deploy

1. Click "Deploy" to start the deployment process
2. Render will build your application and set up the cron job
3. Your bot will now run automatically every 3 hours

## Option 2: Deploy to AWS Lambda with EventBridge

For more advanced users, AWS Lambda with EventBridge provides a scalable solution.

### Step 1: Prepare Your Code

1. Create a Lambda handler function in your project:

```python
# lambda_handler.py
from run_automation import run_automation

def handler(event, context):
    result = run_automation()
    return {
        'statusCode': 200 if result else 500,
        'body': 'Automation completed successfully' if result else 'Automation failed'
    }
```

2. Create a requirements.txt file with all dependencies

### Step 2: Package Your Application

1. Install the AWS CLI and configure it with your credentials
2. Create a deployment package:

```bash
pip install -r requirements.txt -t ./package
cp -r src/ ./package/
cp *.py ./package/
cp *.pdf ./package/  # Include your resume
cd package
zip -r ../deployment.zip .
```

### Step 3: Create Lambda Function

1. Go to AWS Lambda console
2. Create a new function
3. Upload your deployment.zip file
4. Set the handler to "lambda_handler.handler"
5. Configure environment variables from your .env file
6. Increase timeout to at least 5 minutes

### Step 4: Set Up EventBridge Rule

1. Go to Amazon EventBridge console
2. Create a new rule
3. Use a schedule expression: `rate(3 hours)`
4. Set the target as your Lambda function
5. Save the rule

## Option 3: Deploy to GitHub Actions

GitHub Actions provides a free way to run scheduled workflows.

### Step 1: Create GitHub Workflow File

Create a file at `.github/workflows/automation.yml`:

```yaml
name: Run Internship Bot

on:
  schedule:
    - cron: '0 */3 * * *'  # Every 3 hours
  workflow_dispatch:  # Allow manual trigger

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          playwright install chromium
          
      - name: Run automation script
        run: python run_automation.py
        env:
          # Add all your environment variables here
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          # Add all other environment variables
```

### Step 2: Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add all environment variables from your .env file as secrets

### Step 3: Push Changes and Enable Workflow

1. Push the workflow file to your repository
2. Go to the Actions tab in your repository
3. Enable the workflow

## Troubleshooting

### Email Notifications

If you're having issues with email notifications in your cloud deployment:

1. Make sure your SMTP settings are correct
2. For Gmail, use an App Password instead of your regular password
3. To disable email notifications, set `EMAIL_NOTIFICATIONS_ENABLED=False` in your environment variables

### Browser Automation

Playwright requires special setup in cloud environments:

1. Make sure to include `playwright install chromium` in your build commands
2. Use headless mode for browser automation
3. If you encounter issues, check the logs for specific error messages

## Monitoring

Regularly check your deployment logs to ensure the bot is running correctly. Most cloud platforms provide logging and monitoring tools to help you track the performance of your application.
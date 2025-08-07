# AutoIntern AI Bot

An autonomous bot that automatically searches and applies for internships on LinkedIn based on your profile and preferences. This bot uses multi-agent AI to evaluate job postings and generate personalized cover letters.

The project also includes a Streamlit web application for filtering internship descriptions based on your skills.

## Features

### Automation Bot
- 🔒 Secure credential management using environment variables
- 🤖 Automated LinkedIn login with CAPTCHA handling
- 🎯 Smart job matching using AI embeddings (Cohere Embed v3)
- 🧠 Multi-agent AI for job evaluation and cover letter generation
- ⏰ Configurable scheduling via GitHub Actions
- 📝 Automatic application submission
- 📊 Detailed tracking of all applications

### Streamlit Web App
- 🔍 Filter internship descriptions based on your skills
- 📄 Support for text input or file upload (TXT, PDF, DOCX)
- 🔎 Highlight matching skills in job descriptions
- 📊 Analyze skill matches with visual feedback

## Setup

### Automation Bot
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials
4. Place your resume in the directory and update the path in `.env`
5. Run the bot:
   ```bash
   python run_automation.py
   ```

### Streamlit Web App
1. Install dependencies (if not already done):
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Streamlit app:
   ```bash
   streamlit run src/internship_filter_app.py
   ```
3. Open your browser at `http://localhost:8501`

## Configuration

Edit the `.env` file to configure:
- LinkedIn credentials
- AI API keys (Cohere, OpenAI, OpenRouter)
- Application settings (similarity threshold, delay, max applications)
- User profile details
- Internship titles to search for

## Logs

All activities are logged in `internship_bot.log` with detailed information about:
- LinkedIn login attempts
- Internship scraping results
- Job evaluation scores
- Application attempts and results

Application data is also stored in a structured format for later analysis.

## Deployment

This project can be deployed in several ways:

- **GitHub Actions**: For automated bot runs (see `.github/workflows/automation.yml`)
- **GitHub Pages**: For Streamlit app documentation (see `.github/workflows/deploy_streamlit.yml`)
- **Streamlit Cloud**: For hosting the web application
- **Render.com**: Using the provided `render.yaml` configuration

For detailed deployment instructions, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).

## Project Structure

```
├── .github/workflows/    # GitHub Actions workflows
├── src/                  # Source code
│   ├── internship_filter_app.py  # Streamlit application
│   └── skill_matcher.py  # Skill matching logic
├── run_automation.py     # Main automation script
├── requirements.txt      # Python dependencies
├── Procfile             # For Render/Heroku deployment
└── render.yaml          # Render.com configuration
```

## License

MIT
# Ai-Intership-Application-BOt
# IntershipAiBot

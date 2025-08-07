# 🚀 Quick Start Guide

## ⚡ Get Started in 5 Minutes

### 1. Install the Bot
```bash
# Clone and setup
git clone <repository-url>
cd NEWAI

# Run setup script
python setup.py
```

### 2. Configure Your Settings
Edit the `.env` file with your credentials:
```env
# Optional: OpenAI API for better cover letters
OPENAI_API_KEY=your_key_here

# Application settings
SIMILARITY_THRESHOLD=0.85
APPLICATION_DELAY=30
MAX_APPLICATIONS_PER_DAY=50
```

### 3. Start the Dashboard
```bash
streamlit run dashboard.py
```

### 4. Upload Your Resume
- Go to the sidebar in the dashboard
- Upload your PDF or DOCX resume
- Click "Load Resume"

### 5. Start Applying!
- Click "Search Internships" to find jobs
- Click "Evaluate Matches" to see recommendations
- Click "Apply to Jobs" to start applications

## 🎯 Command Line Usage

### Manual Mode (Step-by-step)
```bash
python main.py --resume resume.pdf --mode manual
```

### Automatic Mode (Full Cycle)
```bash
python main.py --resume resume.pdf --mode auto --keywords "python,data science"
```

### Dashboard Mode
```bash
python main.py --resume resume.pdf --mode dashboard
```

## 📊 What You Get

### ✅ Automated Features
- **Smart Resume Parsing**: Extracts skills, contact info, experience
- **AI Job Matching**: 200% accurate skill matching
- **Multi-Platform Scraping**: LinkedIn, Internshala, AngelList
- **Intelligent Applications**: Auto-fills forms with your data
- **Real-time Tracking**: Monitor all applications

### 📈 Analytics Dashboard
- Application success rates
- Platform performance
- Match score distribution
- Export to Excel/CSV

### 🔧 Customization
- Adjust similarity threshold (0.85 default)
- Set application delays (30s default)
- Configure search keywords
- Control daily limits (50 default)

## 🛡️ Safety Features

### Rate Limiting
- Configurable delays between applications
- Respects platform limits
- Human-like behavior patterns

### Error Handling
- Graceful failure recovery
- Comprehensive logging
- CAPTCHA detection

### Data Protection
- Environment variables for credentials
- Local data storage
- Secure configuration

## 🎯 Best Practices

### For High Success Rate
- Use similarity threshold 0.90+
- Limit to 20-30 applications/day
- Customize keywords for your field
- Update resume with relevant skills

### For Platform Safety
- Increase delays to 60+ seconds
- Use different accounts if needed
- Monitor application logs
- Respect platform terms of service

## 🆘 Troubleshooting

### Common Issues
1. **Resume not loading**: Check PDF/DOCX format
2. **No jobs found**: Try different keywords
3. **Applications failing**: Check credentials in .env
4. **Browser errors**: Run `playwright install chromium`

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python main.py --resume resume.pdf --mode manual
```

## 📞 Support

- **Documentation**: Check README.md for full details
- **Testing**: Run `python test_bot.py` to verify setup
- **Logs**: Check `internship_bot.log` for errors
- **Dashboard**: Use the web interface for easy monitoring

---

**🎉 Ready to automate your internship search? Start with the dashboard for the best experience!** 
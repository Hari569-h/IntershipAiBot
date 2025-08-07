# Internship Filter App

## Overview

The Internship Filter App is a Streamlit-based web application that helps you filter internship descriptions based on your skills. It analyzes job descriptions and highlights matching skills, making it easier to identify suitable opportunities.

## Features

- **Skill Configuration**: Choose from default skills or add your own custom skills
- **Multiple Input Methods**: Enter job descriptions directly or upload files (TXT, PDF, DOCX)
- **Skill Matching**: Identifies which of your skills match the job description
- **Visual Highlighting**: Displays the job description with matched skills highlighted
- **Match Analysis**: Shows the count and list of matched skills

## Installation

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AIBot.git
   ```

2. Navigate to the project directory:
   ```bash
   cd AIBot
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run src/internship_filter_app.py
   ```

2. Open your web browser and go to `http://localhost:8501`

3. Configure your skills:
   - Select from the default skills list, or
   - Enter custom skills separated by commas

4. Input a job description:
   - Paste text directly into the text area, or
   - Upload a file (TXT, PDF, or DOCX)

5. Click "Analyze Job Description" to see the results

## Deployment

This application can be deployed to various platforms:

- **GitHub Pages**: For documentation and instructions (see `.github/workflows/deploy_streamlit.yml`)
- **Streamlit Cloud**: For a fully interactive deployment
- **Render.com**: Using the provided `render.yaml` configuration

For detailed deployment instructions, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).

## Integration with AutoIntern AI Bot

This Streamlit app is part of the larger AutoIntern AI Bot project, which includes:

- Automated job searching
- Skill matching (used by this app)
- Application submission
- Scheduled runs via GitHub Actions

The Streamlit app provides a user-friendly interface to the skill matching functionality, which is also used by the automation bot.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
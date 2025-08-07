# Deployment Guide for Internship Filter App

This guide will help you deploy the Internship Filter application on various platforms including Render.com, GitHub Pages, and Streamlit Cloud.

## Prerequisites

1. Git repository with your AIBot project
2. Accounts on your preferred deployment platforms (Render.com, GitHub, Streamlit Cloud, etc.)

## Deployment Steps

### Option 1: Deploy using render.yaml (Recommended)

1. **Push your code to a Git repository**
   - Make sure your repository includes all the necessary files:
     - `src/internship_filter_app.py`
     - `requirements.txt`
     - `render.yaml`
     - `runtime.txt`
     - `Procfile`

2. **Connect your repository to Render**
   - Log in to your Render dashboard
   - Click on "New" and select "Blueprint"
   - Connect your Git repository
   - Render will automatically detect the `render.yaml` file and set up your service

3. **Review and deploy**
   - Review the configuration
   - Click "Apply" to start the deployment

### Option 2: Manual Deployment

1. **Log in to Render**
   - Go to [dashboard.render.com](https://dashboard.render.com) and sign in

2. **Create a new Web Service**
   - Click on "New" and select "Web Service"
   - Connect your Git repository

3. **Configure the service**
   - Name: `internship-filter` (or your preferred name)
   - Environment: `Python`
   - Region: Choose the region closest to your users
   - Branch: `main` (or your default branch)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run src/internship_filter_app.py --server.port=$PORT --server.address=0.0.0.0`

4. **Set environment variables**
   - Click on "Advanced" and add the following environment variable:
     - Key: `PYTHON_VERSION`
     - Value: `3.9.18`

5. **Create Web Service**
   - Click "Create Web Service" to start the deployment

## Verifying Deployment

1. **Check deployment status**
   - Render will show the build and deployment logs
   - Wait for the deployment to complete

2. **Access your application**
   - Once deployed, Render will provide a URL for your application
   - Click on the URL to open your Internship Filter app

## Troubleshooting

### Common Issues

1. **Build failures**
   - Check the build logs for specific errors
   - Ensure all dependencies are correctly listed in `requirements.txt`

2. **Application errors**
   - Check the application logs in the Render dashboard
   - Verify that the start command is correct

3. **Streamlit not loading**
   - Ensure the `--server.port=$PORT --server.address=0.0.0.0` parameters are included in the start command

### Updating Your Deployment

- Push changes to your Git repository
- Render will automatically rebuild and deploy your application (if auto-deploy is enabled)

## Additional Configuration

### Custom Domains (Render.com)

1. Go to your service in the Render dashboard
2. Click on "Settings" and then "Custom Domain"
3. Follow the instructions to add your domain

### Environment Variables

If your application requires additional environment variables:

1. Go to your service in the Render dashboard
2. Click on "Environment"

## GitHub Pages Deployment

Since Streamlit requires a running Python server, GitHub Pages can't directly host the interactive application. However, you can use GitHub Pages to host documentation and instructions for your app:

1. **Set up GitHub Actions workflow**
   - The repository already includes a workflow file at `.github/workflows/deploy_streamlit.yml`
   - This workflow creates a static site with instructions for running the app locally

2. **Enable GitHub Pages**
   - Go to your repository settings
   - Navigate to "Pages"
   - Set the source to "GitHub Actions"

3. **Access your GitHub Pages site**
   - Once deployed, your site will be available at `https://yourusername.github.io/AIBot/`
   - The site includes instructions for running the app locally and deployment options

## Streamlit Cloud Deployment

The easiest way to deploy a Streamlit app is using Streamlit Cloud:

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository, branch, and the path to the app file (`src/internship_filter_app.py`)
6. Click "Deploy"

Your app will be available at a URL like `https://yourusername-aibot-src-internship-filter-app-xxxx.streamlit.app`

### Environment Variables

If your application requires environment variables on Streamlit Cloud:

1. Go to your app settings in Streamlit Cloud
2. Navigate to the "Secrets" section
3. Add your environment variables in the TOML format

## Resources

- [Render Documentation](https://render.com/docs)
- [Streamlit Deployment Guide](https://docs.streamlit.io/knowledge-base/tutorials/deploy/)
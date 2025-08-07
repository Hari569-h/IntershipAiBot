#!/usr/bin/env python3
"""
Internship Filter Streamlit App

This Streamlit application provides a web interface for filtering internship descriptions
based on user skills. It determines if at least one of the user's skills is mentioned
in the job description.
"""

import streamlit as st
import os
import sys
from typing import List

# Add the parent directory to the path to import skill_matcher
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.skill_matcher import SkillMatcher

# Set page configuration
st.set_page_config(
    page_title="Internship Filter",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define default user skills
DEFAULT_SKILLS = [
    "Java",
    "Web Development",  # HTML, CSS
    "Firebase",  # Also matches Firestore
    "React",  # Basic knowledge
    "AI/ML",  # Fundamentals
    "Git",  # Also matches GitHub
    "Razorpay",  # Integration
    "Google Apps Script",
    "PDF"  # PDF and report generation (jsPDF)
]

def filter_internship(user_skills: List[str], job_description: str):
    """Filter an internship description based on user skills."""
    # Initialize the skill matcher
    matcher = SkillMatcher()
    
    # Filter the internship
    return matcher.filter_internship_by_skills(user_skills, job_description)

# App title and description
st.title("Internship Filter")
st.markdown(
    """
    This tool analyzes job descriptions and determines if at least one of your skills 
    is mentioned in the required or preferred qualifications, responsibilities, tools, or technologies.
    """
)

# Sidebar for skills configuration
st.sidebar.header("Skills Configuration")

# Option to use default skills or custom skills
use_default_skills = st.sidebar.checkbox("Use Default Skills", value=True)

if use_default_skills:
    # Display default skills with option to deselect
    selected_skills = []
    st.sidebar.subheader("Default Skills")
    for skill in DEFAULT_SKILLS:
        if st.sidebar.checkbox(skill, value=True, key=f"default_{skill}"):
            selected_skills.append(skill)
    
    # Show selected skills count
    st.sidebar.caption(f"Selected {len(selected_skills)} out of {len(DEFAULT_SKILLS)} default skills")
else:
    # Custom skills input
    st.sidebar.subheader("Custom Skills")
    custom_skills_input = st.sidebar.text_area(
        "Enter your skills (one per line)",
        height=200,
        help="Enter each skill on a new line"
    )
    selected_skills = [skill.strip() for skill in custom_skills_input.split("\n") if skill.strip()]
    
    # Show entered skills count
    st.sidebar.caption(f"Entered {len(selected_skills)} custom skills")

# Main content area
st.header("Job Description Analysis")

# Input method selection
input_method = st.radio(
    "Select input method",
    options=["Enter Text", "Upload File"],
    horizontal=True
)

job_description = ""

if input_method == "Enter Text":
    # Text area for job description input
    job_description = st.text_area(
        "Enter the job description",
        height=300,
        placeholder="Paste the internship job description here..."
    )
else:
    # File uploader for job description
    uploaded_file = st.file_uploader("Upload job description", type=["txt", "pdf", "docx"])
    
    if uploaded_file is not None:
        # Handle different file types
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        if file_extension == "txt":
            # Read text file
            job_description = uploaded_file.read().decode("utf-8")
        elif file_extension == "pdf":
            st.warning("PDF parsing requires pdfplumber library. Make sure it's installed.")
            try:
                import pdfplumber
                with pdfplumber.open(uploaded_file) as pdf:
                    job_description = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            except ImportError:
                st.error("Could not import pdfplumber. Please install it or use text input.")
        elif file_extension == "docx":
            st.warning("DOCX parsing requires python-docx library. Make sure it's installed.")
            try:
                import docx
                doc = docx.Document(uploaded_file)
                job_description = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            except ImportError:
                st.error("Could not import python-docx. Please install it or use text input.")
        
        # Display the extracted text
        if job_description:
            st.subheader("Extracted Text")
            with st.expander("View extracted text", expanded=False):
                st.text(job_description)

# Analysis button
if st.button("Analyze Job Description", type="primary", disabled=not (job_description and selected_skills)):
    # Show a spinner while analyzing
    with st.spinner("Analyzing job description..."):
        # Perform the analysis
        result = filter_internship(selected_skills, job_description)
        
        # Display results
        st.subheader("Analysis Results")
        
        # Create columns for results display
        col1, col2 = st.columns(2)
        
        with col1:
            # Display match status with appropriate styling
            if result["status"] == "MATCH":
                st.success("✅ MATCH FOUND")
            else:
                st.error("❌ NO MATCH")
        
        with col2:
            # Display matched skills count
            matched_count = len(result["matched_skills"])
            total_count = len(selected_skills)
            st.metric(
                "Skills Matched",
                f"{matched_count}/{total_count}",
                delta=f"{matched_count} skills",
                delta_color="normal"
            )
        
        # Display matched skills
        if result["matched_skills"]:
            st.subheader("Matched Skills")
            for skill in result["matched_skills"]:
                st.markdown(f"- **{skill}**")
        
        # Display job description with highlighted skills
        st.subheader("Job Description with Highlighted Skills")
        highlighted_text = job_description
        
        # Simple highlighting by wrapping matched skills with markdown
        for skill in result["matched_skills"]:
            # Case-insensitive replacement with highlighting
            import re
            pattern = re.compile(re.escape(skill), re.IGNORECASE)
            highlighted_text = pattern.sub(f"**{skill}**", highlighted_text)
        
        st.markdown(highlighted_text)

# Display instructions if no job description is entered
if not job_description:
    st.info("Enter a job description or upload a file to analyze")

# Display warning if no skills are selected
if not selected_skills:
    st.warning("Please select at least one skill to analyze")

# Footer
st.markdown("---")
st.caption("Internship Filter Tool | AIBot Project")
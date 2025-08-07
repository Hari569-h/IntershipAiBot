import os

def get_env_str(name, default=""):
    return os.getenv(name, default)

def get_env_int(name, default=0):
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default

def get_env_float(name, default=0.0):
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default

# Configuration variables
ENV = get_env_str("ENV", "development")
RESUME_PATH = get_env_str("RESUME_PATH", "data/resume.pdf")
COHERE_API_KEY = get_env_str("COHERE_API_KEY")
OPENAI_API_KEY = get_env_str("OPENAI_API_KEY")
GEMINI_API_KEY = get_env_str("GEMINI_API_KEY")
GROQ_API_KEY = get_env_str("GROQ_API_KEY")
OPENROUTER_API_KEY = get_env_str("OPENROUTER_API_KEY")
EMBEDDING_MODEL = get_env_str("EMBEDDING_MODEL", "cohere")
SIMILARITY_THRESHOLD = get_env_float("SIMILARITY_THRESHOLD", 0.8)

# Feature toggles
ENABLE_LINKEDIN = get_env_str("ENABLE_LINKEDIN", "true").lower() == "true"
ENABLE_INTERNSHALA = get_env_str("ENABLE_INTERNSHALA", "true").lower() == "true"
ENABLE_ANGELLIST = get_env_str("ENABLE_ANGELLIST", "false").lower() == "true"
ENABLE_INDEED = get_env_str("ENABLE_INDEED", "false").lower() == "true"

# Misc settings
USER_AGENT = get_env_str("USER_AGENT", "Mozilla/5.0")
RUN_INTERVAL_SECONDS = get_env_int("RUN_INTERVAL_SECONDS", 10800)
APPLICATION_DELAY = get_env_int("APPLICATION_DELAY", 30)  # Default 30 seconds delay between applications
MAX_APPLICATIONS_PER_RUN = get_env_int("MAX_APPLICATIONS_PER_RUN", 10)
RUN_INTERVAL_HOURS = get_env_int("RUN_INTERVAL_HOURS", 6)
INTERNSHIP_TITLES = get_env_str("INTERNSHIP_TITLES", "").split(',')
USER_NAME = get_env_str("USER_NAME", "")
USER_EMAIL = get_env_str("USER_EMAIL", "")
USER_PHONE = get_env_str("USER_PHONE", "")
USER_LOCATION = get_env_str("USER_LOCATION", "")
USER_SKILLS = get_env_str("USER_SKILLS", "").split(',')
LINKEDIN_EMAIL = get_env_str("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = get_env_str("LINKEDIN_PASSWORD", "")

def get_config():
    return {
        "env": ENV,
        "resume_path": RESUME_PATH,
        "cohere_api_key": COHERE_API_KEY,
        "openai_api_key": OPENAI_API_KEY,
        "gemini_api_key": GEMINI_API_KEY,
        "groq_api_key": GROQ_API_KEY,
        "openrouter_api_key": OPENROUTER_API_KEY,
        "embedding_model": EMBEDDING_MODEL,
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "enable_linkedin": ENABLE_LINKEDIN,
        "enable_internshala": ENABLE_INTERNSHALA,
        "enable_angellist": ENABLE_ANGELLIST,
        "enable_indeed": ENABLE_INDEED,
        "user_agent": USER_AGENT,
        "run_interval_seconds": RUN_INTERVAL_SECONDS,
        "application_delay": APPLICATION_DELAY,
        "max_applications_per_run": MAX_APPLICATIONS_PER_RUN,
        "run_interval_hours": RUN_INTERVAL_HOURS,
        "internship_titles": INTERNSHIP_TITLES,
        "user_name": USER_NAME,
        "user_email": USER_EMAIL,
        "user_phone": USER_PHONE,
        "user_location": USER_LOCATION,
        "user_skills": USER_SKILLS,
        "linkedin_email": LINKEDIN_EMAIL,
        "linkedin_password": LINKEDIN_PASSWORD,
    }

def update_config(key, value):
    globals()[key] = value

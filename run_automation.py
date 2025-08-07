#!/usr/bin/env python3
"""
LinkedIn Internship Application Bot Runner
This script is designed to be run by cron at configurable intervals for automatic LinkedIn internship applications.
"""

import os
import sys
import logging
import schedule
import time
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from src.internship_bot import InternshipBot
from config import get_config

def setup_logging():
    """Setup logging for the automation script."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"automation_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def run_automation():
    """Run the automated LinkedIn internship application cycle."""
    logger = setup_logging()
    
    try:
        logger.info("🤖 Starting automated LinkedIn internship application cycle")
        logger.info(f"⏰ Started at: {datetime.now().isoformat()}")
        
        # Initialize the bot
        logger.info("📋 Initializing LinkedIn Internship Bot...")
        bot = InternshipBot()
        
        # Get configuration
        config = get_config()
        
        # Load resume
        resume_file = config['resume_path']
        if not os.path.exists(resume_file):
            logger.error(f"❌ Resume file not found: {resume_file}")
            return False
        
        logger.info(f"📄 Loading resume: {resume_file}")
        bot.load_resume(resume_file)
        
        # Get internship titles from config
        internship_titles = config['internship_titles']
        
        logger.info(f"🔍 Searching for internship titles: {internship_titles}")
        logger.info("📍 Not filtering by location as per user request")
        
        # Run the full cycle without location filter
        logger.info("🚀 Starting full application cycle...")
        results = bot.run_full_cycle(internship_titles)
        
        # Log results
        logger.info("📊 Automation Results:")
        logger.info(f"   - Scraped Internships: {results['total_internships_scraped']}")
        logger.info(f"   - Evaluated Internships: {results['total_internships_evaluated']}")
        logger.info(f"   - Recommended Internships: {results['total_recommended_internships']}")
        logger.info(f"   - Applications Attempted: {results['total_applications_attempted']}")
        logger.info(f"   - Successful Applications: {results['total_applications_successful']}")
        logger.info(f"   - Failed Applications: {results['total_applications_failed']}")
        
        if results['error']:
            logger.warning(f"⚠️ Error encountered during application cycle")
            logger.error(f"   - {results['error']}")
        
        # Get application summary
        summary = bot.application_tracker.get_applications_summary()
        logger.info(f"📈 Total Applications Tracked: {summary['total_applications']}")
        logger.info(f"✅ Successful: {summary['successful_applications']}")
        logger.info(f"❌ Failed: {summary['failed_applications']}")
        
        logger.info("✅ Automation cycle completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Automation failed with error: {e}")
        return False
    
    finally:
        logger.info(f"⏰ Finished at: {datetime.now().isoformat()}")

def schedule_job():
    """Schedule the job to run every 6 hours."""
    config = get_config()
    run_interval = config['run_interval_hours']
    
    logger = setup_logging()
    logger.info(f"⏰ Scheduling job to run every {run_interval} hours")
    
    # Run immediately on startup
    run_automation()
    
    # Schedule to run every X hours
    schedule.every(run_interval).hours.do(run_automation)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        schedule_job()
    else:
        success = run_automation()
        sys.exit(0 if success else 1)
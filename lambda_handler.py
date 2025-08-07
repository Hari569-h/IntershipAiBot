#!/usr/bin/env python3
"""
AWS Lambda handler for the AI Internship Application Bot.
This file is used when deploying the bot to AWS Lambda with EventBridge for scheduled execution.
"""

from run_automation import run_automation
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Lambda handler function that runs the automation script.
    
    Args:
        event: The event dict that contains the parameters passed when the function is invoked
        context: The context object that provides methods and properties about the invocation, function, and runtime environment
        
    Returns:
        dict: A response object with statusCode and body
    """
    logger.info("Starting Lambda execution for AI Internship Application Bot")
    
    try:
        # Run the automation script
        result = run_automation()
        
        # Return success or failure response
        if result:
            logger.info("Automation completed successfully")
            return {
                'statusCode': 200,
                'body': 'Automation completed successfully'
            }
        else:
            logger.error("Automation failed")
            return {
                'statusCode': 500,
                'body': 'Automation failed'
            }
            
    except Exception as e:
        logger.error(f"Lambda execution failed with error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Lambda execution failed with error: {str(e)}'
        }
"""
Example script demonstrating the usage of the LM Studio client.
"""

import yaml
import logging
from pathlib import Path
from src.core.lm_studio_client import LMStudioClient

def setup_logging(config):
    """Set up logging configuration."""
    logging.basicConfig(
        level=config["logging"]["level"],
        format=config["logging"]["format"],
        handlers=[
            logging.FileHandler(config["logging"]["file"]),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    """Load configuration from YAML file."""
    config_path = Path("config/lm_studio.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)

def main():
    """Main function demonstrating LM Studio client usage."""
    # Load configuration
    config = load_config()
    
    # Set up logging
    logger = setup_logging(config)
    logger.info("Starting LM Studio example")
    
    try:
        # Initialize client
        client = LMStudioClient(
            base_url=config["api"]["base_url"],
            max_requests_per_minute=config["api"]["max_requests_per_minute"],
            max_tokens_per_request=config["api"]["max_tokens_per_request"],
            cooldown_period=config["api"]["cooldown_period"]
        )
        
        # Check if LM Studio is running
        if not client.health_check():
            logger.error("LM Studio is not running. Please start it first.")
            return
            
        # Get model information
        model_info = client.get_model_info()
        logger.info(f"Connected to model: {model_info}")
        
        # Example 1: Code Analysis
        code = """
def calculate_factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return n * calculate_factorial(n - 1)
"""
        logger.info("Analyzing code...")
        analysis = client.analyze_code(code, "review")
        logger.info(f"Code analysis results: {analysis}")
        
        # Example 2: Knowledge Extraction
        content = """
Python is a high-level, interpreted programming language known for its simplicity and readability.
It supports multiple programming paradigms, including procedural, object-oriented, and functional programming.
Python's extensive standard library and third-party packages make it suitable for various applications,
from web development to data science and artificial intelligence.
"""
        logger.info("Extracting knowledge...")
        knowledge = client.extract_knowledge(content, "text")
        logger.info(f"Extracted knowledge: {knowledge}")
        
        # Example 3: Workflow Generation
        task = "Implement a REST API for a todo list application"
        logger.info("Generating workflow...")
        workflow = client.generate_workflow(task)
        logger.info(f"Generated workflow: {workflow}")
        
        # Example 4: Code Validation
        requirements = [
            "Function should handle negative numbers",
            "Should use recursion",
            "Should have proper error handling",
            "Should be well-documented"
        ]
        logger.info("Validating code...")
        validation = client.validate_code(code, requirements)
        logger.info(f"Validation results: {validation}")
        
    except Exception as e:
        logger.error(f"Error during example execution: {e}")
        raise
        
    logger.info("LM Studio example completed successfully")

if __name__ == "__main__":
    main() 
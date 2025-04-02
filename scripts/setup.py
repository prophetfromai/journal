#!/usr/bin/env python3
import os
import sys
import subprocess
import yaml
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "config",
        "docs",
        "tests",
        "src/core",
        "src/agents",
        "src/knowledge_graph",
        "src/tools",
        "src/workflows",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def create_config_file():
    """Create default configuration file."""
    config = {
        "model": {
            "name": "deepseek-coder",
            "version": "latest",
            "device": "cuda",  # or "cpu"
            "max_length": 2048,
            "temperature": 0.7,
            "top_p": 0.95
        },
        "rate_limiting": {
            "max_requests_per_minute": 60,
            "max_tokens_per_request": 4000,
            "cooldown_period_seconds": 5
        },
        "knowledge_graph": {
            "neo4j_uri": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "your_password",
            "database": "neo4j"
        },
        "git": {
            "base_repo_path": "./repos",
            "max_concurrent_operations": 3,
            "commit_message_template": "AI: {description}"
        },
        "workflows": {
            "max_concurrent_workflows": 5,
            "timeout_seconds": 3600,
            "retry_attempts": 3
        },
        "content_processing": {
            "max_file_size_mb": 100,
            "supported_formats": [
                "pdf",
                "txt",
                "md",
                "youtube"
            ],
            "output_dir": "./data/processed"
        },
        "self_improvement": {
            "knowledge_extraction_interval_hours": 24,
            "max_knowledge_updates_per_day": 10,
            "validation_threshold": 0.85
        }
    }
    
    config_path = Path("config/deepseek.yaml")
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Created configuration file: {config_path}")

def install_dependencies():
    """Install required Python packages."""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed successfully!")

def setup_neo4j():
    """Check if Neo4j is installed and running."""
    try:
        # Try to connect to Neo4j
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687")
        driver.close()
        print("Neo4j connection successful!")
    except Exception as e:
        print("Warning: Could not connect to Neo4j. Please ensure Neo4j is installed and running.")
        print("You can download Neo4j from: https://neo4j.com/download/")
        print(f"Error: {str(e)}")

def initialize_knowledge_graph():
    """Initialize the knowledge graph."""
    print("Initializing knowledge graph...")
    subprocess.check_call([sys.executable, "src/knowledge_graph/init_graph.py"])
    print("Knowledge graph initialized successfully!")

def main():
    """Main setup function."""
    print("Setting up Autonomous AI System...")
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Create configuration file
    create_config_file()
    
    # Install dependencies
    install_dependencies()
    
    # Setup Neo4j
    setup_neo4j()
    
    # Initialize knowledge graph
    initialize_knowledge_graph()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Edit config/deepseek.yaml with your settings")
    print("2. Start the application: python src/main.py")
    print("3. Access the API at http://localhost:8000")
    print("\nFor more information, see the README.md file.")

if __name__ == "__main__":
    main() 
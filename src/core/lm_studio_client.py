"""
LM Studio Client for local model interactions.

This module provides tools for interacting with LM Studio's local model,
including rate limiting and error handling.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class LMStudioClient:
    """Client for interacting with LM Studio's local model."""
    
    def __init__(self, base_url: str = "http://localhost:1234", 
                 max_requests_per_minute: int = 60,
                 max_tokens_per_request: int = 4000,
                 cooldown_period: float = 5.0):
        """Initialize the LM Studio client.
        
        Args:
            base_url: Base URL for LM Studio API
            max_requests_per_minute: Maximum number of requests per minute
            max_tokens_per_request: Maximum tokens per request
            cooldown_period: Cooldown period between requests in seconds
        """
        self.base_url = base_url
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_request = max_tokens_per_request
        self.cooldown_period = cooldown_period
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = datetime.now()
        
    def _wait_for_rate_limit(self) -> None:
        """Wait if necessary to respect rate limits."""
        current_time = datetime.now()
        
        # Reset counter if we're in a new minute
        if (current_time - self.request_window_start).total_seconds() >= 60:
            self.request_count = 0
            self.request_window_start = current_time
            
        # Wait if we've hit the rate limit
        if self.request_count >= self.max_requests_per_minute:
            time.sleep(60 - (current_time - self.request_window_start).total_seconds())
            self.request_count = 0
            self.request_window_start = datetime.now()
            
        # Wait for cooldown period
        time_since_last_request = time.time() - self.last_request_time
        if time_since_last_request < self.cooldown_period:
            time.sleep(self.cooldown_period - time_since_last_request)
            
    def _make_request(self, endpoint: str, method: str = "POST", 
                     data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the LM Studio API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            
        Returns:
            API response
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to LM Studio: {e}")
            raise
            
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None,
                         temperature: float = 0.7, top_p: float = 0.9) -> str:
        """Generate a response from the model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Generated response
        """
        if max_tokens is None:
            max_tokens = self.max_tokens_per_request
            
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False
        }
        
        response = self._make_request("v1/completions", data=data)
        return response["choices"][0]["text"]
        
    def analyze_code(self, code: str, analysis_type: str = "review") -> Dict[str, Any]:
        """Analyze code using the model.
        
        Args:
            code: Code to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        prompt = f"Analyze the following code for {analysis_type}:\n\n{code}"
        response = self.generate_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse analysis response"}
            
    def extract_knowledge(self, content: str, content_type: str) -> Dict[str, Any]:
        """Extract structured knowledge from content.
        
        Args:
            content: Content to analyze
            content_type: Type of content
            
        Returns:
            Extracted knowledge
        """
        prompt = f"Extract structured knowledge from the following {content_type}:\n\n{content}"
        response = self.generate_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse knowledge extraction response"}
            
    def generate_workflow(self, task_description: str) -> Dict[str, Any]:
        """Generate a workflow from a task description.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Generated workflow
        """
        prompt = f"Generate a workflow for the following task:\n\n{task_description}"
        response = self.generate_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse workflow response"}
            
    def validate_code(self, code: str, requirements: List[str]) -> Dict[str, Any]:
        """Validate code against requirements.
        
        Args:
            code: Code to validate
            requirements: List of requirements
            
        Returns:
            Validation results
        """
        prompt = f"Validate the following code against these requirements:\n\n"
        prompt += "\n".join(f"- {req}" for req in requirements)
        prompt += f"\n\nCode:\n{code}"
        
        response = self.generate_response(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse validation response"}
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.
        
        Returns:
            Model information
        """
        return self._make_request("v1/models", method="GET")
        
    def health_check(self) -> bool:
        """Check if the LM Studio API is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            self._make_request("v1/health", method="GET")
            return True
        except requests.exceptions.RequestException:
            return False 
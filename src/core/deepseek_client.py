from typing import Dict, List, Optional, Union
import yaml
from pathlib import Path
import time
from datetime import datetime
import json
import aiohttp

class DeepSeekClient:
    def __init__(self, config_path: str = "config/deepseek.yaml"):
        self.config = self._load_config(config_path)
        self._last_request_time = 0
        self._request_count = 0
        self._reset_time = datetime.now()
        self._session = None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def close(self):
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None

    def _check_rate_limits(self) -> None:
        """Check and enforce rate limits."""
        current_time = datetime.now()
        
        # Reset counter if a minute has passed
        if (current_time - self._reset_time).total_seconds() >= 60:
            self._request_count = 0
            self._reset_time = current_time

        # Check rate limits
        if self._request_count >= self.config['rate_limiting']['max_requests_per_minute']:
            sleep_time = 60 - (current_time - self._reset_time).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._request_count = 0
            self._reset_time = current_time

        # Enforce cooldown period
        time_since_last_request = (current_time - datetime.fromtimestamp(self._last_request_time)).total_seconds()
        if time_since_last_request < self.config['rate_limiting']['cooldown_period_seconds']:
            time.sleep(self.config['rate_limiting']['cooldown_period_seconds'] - time_since_last_request)

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None
    ) -> str:
        """
        Generate text using DeepSeek model with rate limiting and error handling.
        """
        self._check_rate_limits()

        # Use config defaults if not specified
        max_tokens = max_tokens or self.config['model']['max_length']
        temperature = temperature or self.config['model']['temperature']
        top_p = top_p or self.config['model']['top_p']

        try:
            if self._session is None:
                self._session = aiohttp.ClientSession()
            
            # Prepare request for LM Studio server
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
                "stream": False
            }

            # Make request to LM Studio server
            async with self._session.post(
                f"{self.config['model']['server_url']}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")
                
                result = await response.json()
                generated_text = result["choices"][0]["message"]["content"]
            
            self._last_request_time = time.time()
            self._request_count += 1
            
            return generated_text
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")

    async def analyze_code(
        self,
        code: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze code using DeepSeek model.
        """
        prompt = f"Analyze the following code:\n\n{code}"
        if context:
            prompt += f"\n\nContext: {context}"

        response = await self.generate(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"analysis": response}

    async def generate_workflow(
        self,
        task_description: str,
        constraints: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate an AI agent workflow based on task description.
        """
        prompt = f"Generate a workflow for the following task:\n\n{task_description}"
        if constraints:
            prompt += f"\n\nConstraints:\n" + "\n".join(constraints)

        response = await self.generate(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"workflow": response}

    async def extract_knowledge(
        self,
        content: str,
        content_type: str
    ) -> Dict:
        """
        Extract structured knowledge from content.
        """
        prompt = f"Extract structured knowledge from the following {content_type}:\n\n{content}"
        response = await self.generate(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"knowledge": response} 
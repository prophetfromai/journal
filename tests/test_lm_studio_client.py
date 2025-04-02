"""
Tests for the LM Studio client.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.lm_studio_client import LMStudioClient

@pytest.fixture
def client():
    """Create a test client instance."""
    return LMStudioClient(
        base_url="http://localhost:1234",
        max_requests_per_minute=60,
        max_tokens_per_request=4000,
        cooldown_period=0.1  # Short cooldown for testing
    )

def test_initialization(client):
    """Test client initialization."""
    assert client.base_url == "http://localhost:1234"
    assert client.max_requests_per_minute == 60
    assert client.max_tokens_per_request == 4000
    assert client.cooldown_period == 0.1

@patch('requests.request')
def test_generate_response(mock_request, client):
    """Test response generation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"text": "Test response"}]
    }
    mock_request.return_value = mock_response
    
    response = client.generate_response("Test prompt")
    assert response == "Test response"
    
    mock_request.assert_called_once()
    call_args = mock_request.call_args[1]
    assert call_args["method"] == "POST"
    assert call_args["url"] == "http://localhost:1234/v1/completions"
    assert "prompt" in call_args["json"]

@patch('requests.request')
def test_analyze_code(mock_request, client):
    """Test code analysis."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"text": '{"analysis": "Test analysis"}'}]
    }
    mock_request.return_value = mock_response
    
    result = client.analyze_code("def test(): pass")
    assert result == {"analysis": "Test analysis"}

@patch('requests.request')
def test_extract_knowledge(mock_request, client):
    """Test knowledge extraction."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"text": '{"knowledge": "Test knowledge"}'}]
    }
    mock_request.return_value = mock_response
    
    result = client.extract_knowledge("Test content", "text")
    assert result == {"knowledge": "Test knowledge"}

@patch('requests.request')
def test_generate_workflow(mock_request, client):
    """Test workflow generation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"text": '{"workflow": "Test workflow"}'}]
    }
    mock_request.return_value = mock_response
    
    result = client.generate_workflow("Test task")
    assert result == {"workflow": "Test workflow"}

@patch('requests.request')
def test_validate_code(mock_request, client):
    """Test code validation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"text": '{"validation": "Test validation"}'}]
    }
    mock_request.return_value = mock_response
    
    result = client.validate_code("def test(): pass", ["Requirement 1"])
    assert result == {"validation": "Test validation"}

@patch('requests.request')
def test_get_model_info(mock_request, client):
    """Test model info retrieval."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"model": "Test model"}
    mock_request.return_value = mock_response
    
    result = client.get_model_info()
    assert result == {"model": "Test model"}
    
    mock_request.assert_called_once()
    call_args = mock_request.call_args[1]
    assert call_args["method"] == "GET"
    assert call_args["url"] == "http://localhost:1234/v1/models"

@patch('requests.request')
def test_health_check(mock_request, client):
    """Test health check."""
    mock_request.return_value = MagicMock()
    assert client.health_check() is True
    
    mock_request.side_effect = Exception()
    assert client.health_check() is False

def test_rate_limiting(client):
    """Test rate limiting behavior."""
    with patch('time.sleep') as mock_sleep:
        # Make max_requests_per_minute requests
        for _ in range(client.max_requests_per_minute):
            client._wait_for_rate_limit()
        
        # Next request should trigger rate limiting
        client._wait_for_rate_limit()
        mock_sleep.assert_called_once()

def test_cooldown_period(client):
    """Test cooldown period behavior."""
    with patch('time.sleep') as mock_sleep:
        client._wait_for_rate_limit()
        client._wait_for_rate_limit()
        mock_sleep.assert_called_once_with(0.1) 
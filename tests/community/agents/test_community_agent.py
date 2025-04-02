import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from collections import Counter

from src.community.agents.community_agent import CommunityAgent, CommunityInsight, ContentSuggestion
from src.core.deepseek_client import DeepSeekClient
from src.knowledge_graph.graph_manager import KnowledgeGraphManager

@pytest.fixture
def mock_deepseek():
    return AsyncMock(spec=DeepSeekClient)

@pytest.fixture
def mock_graph_manager():
    return AsyncMock(spec=KnowledgeGraphManager)

@pytest.fixture
def community_agent(mock_deepseek, mock_graph_manager):
    return CommunityAgent(mock_deepseek, mock_graph_manager)

@pytest.mark.asyncio
async def test_analyze_community_activity(community_agent, mock_deepseek, mock_graph_manager):
    # Mock data
    recent_activity = [
        {
            "id": "1",
            "type": "post",
            "content": "Python programming best practices",
            "tags": ["python", "best-practices"],
            "skills": ["python", "coding"]
        },
        {
            "id": "2",
            "type": "question",
            "content": "How to use async/await in Python?",
            "tags": ["python", "async"],
            "skills": ["python", "async"]
        }
    ]
    
    topic_analysis = {
        "trending_topics": [
            {"topic": "python", "count": 3},
            {"topic": "async", "count": 2}
        ]
    }
    
    insight_response = """
    {
        "trending_topics": ["python", "async"],
        "skill_gaps": ["async programming", "testing"],
        "recommended_resources": [
            {"title": "Async Python Guide", "url": "example.com"}
        ],
        "connection_opportunities": [
            {"mentor": ["user1"], "learner": ["user2"]}
        ],
        "growth_suggestions": ["Create more async tutorials"]
    }
    """
    
    # Setup mocks
    mock_graph_manager.get_recent_activity.return_value = recent_activity
    mock_deepseek.generate.return_value = insight_response
    community_agent.topic_extractor.analyze_topic_trends = AsyncMock(return_value=topic_analysis)
    
    # Execute
    result = await community_agent.analyze_community_activity(timedelta(days=7))
    
    # Assert
    assert isinstance(result, CommunityInsight)
    assert "python" in result.trending_topics
    assert "async programming" in result.skill_gaps
    assert len(result.recommended_resources) == 1
    assert len(result.connection_opportunities) == 1
    assert len(result.growth_suggestions) == 1

@pytest.mark.asyncio
async def test_generate_content_suggestions(community_agent, mock_deepseek, mock_graph_manager):
    # Mock data
    insight = CommunityInsight(
        trending_topics=["python", "async"],
        skill_gaps=["testing"],
        recommended_resources=[],
        connection_opportunities=[],
        growth_suggestions=[]
    )
    
    content_response = """
    {
        "title": "Async Python Tutorial",
        "type": "tutorial",
        "description": "Learn async programming in Python",
        "outline": ["Basics", "Advanced concepts"],
        "target_audience": ["intermediate developers"],
        "prerequisites": ["Python basics"],
        "estimated_value": 8
    }
    """
    
    # Setup mocks
    mock_deepseek.generate.return_value = content_response
    mock_graph_manager.get_resources_by_topic.return_value = []
    
    # Execute
    result = await community_agent.generate_content_suggestions(insight)
    
    # Assert
    assert len(result) == 2  # One for each trending topic
    assert isinstance(result[0], ContentSuggestion)
    assert result[0].title == "Async Python Tutorial"
    assert result[0].type == "tutorial"
    assert result[0].estimated_value == 8

@pytest.mark.asyncio
async def test_identify_mentorship_opportunities(community_agent, mock_graph_manager):
    # Mock data
    insight = CommunityInsight(
        trending_topics=["python"],
        skill_gaps=[],
        recommended_resources=[],
        connection_opportunities=[],
        growth_suggestions=[]
    )
    
    expert = {
        "id": "expert1",
        "skills": ["python", "django"],
        "interests": ["web development"],
        "experience_level": 5,
        "availability": [
            {
                "day": "Monday",
                "start": datetime.now().replace(hour=9, minute=0),
                "end": datetime.now().replace(hour=17, minute=0)
            }
        ]
    }
    
    learner = {
        "id": "learner1",
        "skills": ["python"],
        "interests": ["web development"],
        "experience_level": 2,
        "availability": [
            {
                "day": "Monday",
                "start": datetime.now().replace(hour=10, minute=0),
                "end": datetime.now().replace(hour=16, minute=0)
            }
        ]
    }
    
    # Setup mocks
    mock_graph_manager.find_experts = AsyncMock(return_value=[expert])
    mock_graph_manager.find_learners = AsyncMock(return_value=[learner])
    
    # Execute
    result = await community_agent.identify_mentorship_opportunities(insight)
    
    # Assert
    assert len(result) == 1
    assert result[0]["mentor"] == "expert1"
    assert result[0]["learner"] == "learner1"
    assert result[0]["match_score"] >= 0.6
    assert "web development" in result[0]["common_interests"]

@pytest.mark.asyncio
async def test_generate_weekly_digest(community_agent, mock_deepseek, mock_graph_manager):
    # Mock dependencies
    community_agent.analyze_community_activity = AsyncMock(return_value=CommunityInsight(
        trending_topics=["python"],
        skill_gaps=["testing"],
        recommended_resources=[],
        connection_opportunities=[],
        growth_suggestions=[]
    ))
    
    community_agent.generate_content_suggestions = AsyncMock(return_value=[
        ContentSuggestion(
            title="Python Testing Guide",
            type="guide",
            description="Learn testing in Python",
            outline=["Unit testing", "Integration testing"],
            target_audience=["developers"],
            prerequisites=["Python basics"],
            estimated_value=8
        )
    ])
    
    community_agent.identify_mentorship_opportunities = AsyncMock(return_value=[
        {
            "mentor": "expert1",
            "learner": "learner1",
            "match_score": 0.8
        }
    ])
    
    mock_graph_manager.count_active_users.return_value = 100
    mock_graph_manager.count_total_users.return_value = 200
    mock_graph_manager.count_new_members.return_value = 20
    mock_graph_manager.count_new_content.return_value = 30
    
    # Execute
    result = await community_agent.generate_weekly_digest()
    
    # Assert
    assert isinstance(result, dict)
    assert "timestamp" in result
    assert "insights" in result
    assert "content_suggestions" in result
    assert "mentorship_opportunities" in result
    assert "growth_metrics" in result
    assert result["growth_metrics"]["engagement_rate"] == 0.5

@pytest.mark.asyncio
async def test_auto_curate_resources(community_agent):
    # Mock data
    resources = [
        {
            "id": "1",
            "type": "tutorial",
            "content": "Python programming guide"
        },
        {
            "id": "2",
            "type": "article",
            "content": "Async programming patterns"
        }
    ]
    
    # Setup mocks
    community_agent.graph.get_all_resources = AsyncMock(return_value=resources)
    community_agent.topic_extractor.extract_topics_from_text = AsyncMock(return_value=["python", "programming"])
    
    # Execute
    result = await community_agent.auto_curate_resources()
    
    # Assert
    assert isinstance(result, list)
    assert len(result) > 0
    for recommendation in result:
        assert "type" in recommendation
        assert "action" in recommendation
        assert "priority" in recommendation 
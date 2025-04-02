from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, UTC
import json
import asyncio
from collections import Counter
from uuid import UUID, uuid4

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from src.core.deepseek_client import DeepSeekClient
from src.knowledge_graph.graph_manager import KnowledgeGraphManager
from src.community.agents.topic_extractor import TopicExtractor

class CommunityInsight(BaseModel):
    """Insights about community activity and trends."""
    trending_topics: List[str] = Field(description="Currently trending topics in the community")
    skill_gaps: List[str] = Field(description="Skills that the community needs more expertise in")
    recommended_resources: List[Dict[str, str]] = Field(description="Recommended resources to create")
    connection_opportunities: List[Dict[str, List[str]]] = Field(description="Potential connections between members")
    growth_suggestions: List[str] = Field(description="Suggestions for community growth")

class ContentSuggestion(BaseModel):
    """Suggested content to create for the community."""
    title: str = Field(description="Title of the content")
    type: str = Field(description="Type of content (guide, tutorial, template, etc.)")
    description: str = Field(description="Description of the content")
    outline: List[str] = Field(description="Outline of the content")
    target_audience: List[str] = Field(description="Target audience for this content")
    prerequisites: List[str] = Field(description="Required prerequisites")
    estimated_value: int = Field(description="Estimated value to the community (1-10)")

class CommunityAgent:
    def __init__(
        self,
        deepseek_client: DeepSeekClient,
        graph_manager: KnowledgeGraphManager
    ):
        self.deepseek = deepseek_client
        self.graph = graph_manager
        self.topic_extractor = TopicExtractor(deepseek_client)
        self.insight_parser = PydanticOutputParser(pydantic_object=CommunityInsight)
        self.content_parser = PydanticOutputParser(pydantic_object=ContentSuggestion)

    async def analyze_community_activity(
        self,
        timeframe: timedelta = timedelta(days=7)
    ) -> CommunityInsight:
        """Analyze recent community activity to generate insights."""
        # Get recent activity from the knowledge graph
        recent_activity = await self.graph.get_recent_activity(timeframe)
        
        # Extract topics and skills from activity
        topics = Counter()
        skills = Counter()
        texts = []
        
        for item in recent_activity:
            if "tags" in item:
                topics.update(item["tags"])
            if "skills" in item:
                skills.update(item["skills"])
            if "content" in item:
                texts.append(item["content"])
        
        # Extract topics from content
        if texts:
            topic_analysis = await self.topic_extractor.analyze_topic_trends(texts)
            for topic_info in topic_analysis["trending_topics"]:
                topics[topic_info["topic"]] += topic_info["count"]
        
        # Generate insights using DeepSeek
        prompt = self._create_insight_prompt(topics, skills, recent_activity)
        response = await self.deepseek.generate(prompt)
        
        return self.insight_parser.parse(response)

    async def generate_content_suggestions(
        self,
        insight: CommunityInsight
    ) -> List[ContentSuggestion]:
        """Generate content suggestions based on community insights."""
        suggestions = []
        
        for topic in insight.trending_topics:
            prompt = self._create_content_prompt(
                topic=topic,
                skill_gaps=insight.skill_gaps,
                existing_resources=await self.graph.get_resources_by_topic(topic)
            )
            response = await self.deepseek.generate(prompt)
            suggestion = self.content_parser.parse(response)
            suggestions.append(suggestion)
            
        return suggestions

    async def identify_mentorship_opportunities(
        self,
        insight: CommunityInsight
    ) -> List[Dict[str, Any]]:
        """Identify potential mentorship opportunities."""
        opportunities = []
        
        # Find experts in trending topics
        for topic in insight.trending_topics:
            experts = await self.graph.find_experts(topic)
            learners = await self.graph.find_learners(topic)
            
            for expert in experts:
                matches = self._match_mentor_learner(expert, learners)
                opportunities.extend(matches)
                
        return opportunities

    async def generate_weekly_digest(self) -> Dict[str, Any]:
        """Generate a weekly community digest."""
        insight = await self.analyze_community_activity()
        content_suggestions = await self.generate_content_suggestions(insight)
        mentorship_opportunities = await self.identify_mentorship_opportunities(insight)
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "insights": insight.model_dump(),
            "content_suggestions": [s.model_dump() for s in content_suggestions],
            "mentorship_opportunities": mentorship_opportunities,
            "growth_metrics": await self._calculate_growth_metrics(),
            "recommendations": await self._generate_recommendations(insight)
        }

    async def auto_curate_resources(self) -> List[Dict[str, Any]]:
        """Automatically curate and organize community resources."""
        # Get all resources
        resources = await self.graph.get_all_resources()
        
        # Extract topics from resource content
        for resource in resources:
            if "content" in resource:
                topics = await self.topic_extractor.extract_topics_from_text(resource["content"])
                resource["extracted_topics"] = topics
        
        # Analyze and categorize resources
        categorized = await self._categorize_resources(resources)
        
        # Generate recommendations for improvement
        recommendations = await self._generate_resource_recommendations(categorized)
        
        return recommendations

    def _create_insight_prompt(
        self,
        topics: Counter,
        skills: Counter,
        activity: List[Dict[str, Any]]
    ) -> str:
        """Create a prompt for generating community insights."""
        return f"""
        Analyze the following community activity data and generate insights:
        
        Top Topics: {dict(topics.most_common(10))}
        Top Skills: {dict(skills.most_common(10))}
        Recent Activity: {json.dumps(activity, indent=2)}
        
        Generate insights in the following format:
        {self.insight_parser.get_format_instructions()}
        """

    def _create_content_prompt(
        self,
        topic: str,
        skill_gaps: List[str],
        existing_resources: List[Dict[str, Any]]
    ) -> str:
        """Create a prompt for generating content suggestions."""
        return f"""
        Generate a content suggestion for the following topic:
        
        Topic: {topic}
        Skill Gaps: {skill_gaps}
        Existing Resources: {json.dumps(existing_resources, indent=2)}
        
        Generate a content suggestion in the following format:
        {self.content_parser.get_format_instructions()}
        """

    def _match_mentor_learner(
        self,
        expert: Dict[str, Any],
        learners: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Match mentors with potential learners."""
        matches = []
        
        for learner in learners:
            score = self._calculate_mentor_match_score(expert, learner)
            if score >= 0.6:  # Lower the threshold to be more inclusive
                matches.append({
                    "mentor": expert["id"],
                    "learner": learner["id"],
                    "match_score": score,
                    "common_interests": self._find_common_interests(expert, learner)
                })
                
        return matches

    def _calculate_mentor_match_score(
        self,
        expert: Dict[str, Any],
        learner: Dict[str, Any]
    ) -> float:
        """Calculate a match score between a mentor and learner."""
        score = 0.0
        weights = {
            "skills": 0.35,
            "interests": 0.35,
            "experience_level": 0.2,
            "availability": 0.1
        }
        
        # Calculate skill overlap
        expert_skills = set(expert.get("skills", []))
        learner_skills = set(learner.get("skills", []))
        skill_score = 0.0
        if expert_skills and learner_skills:
            # Give more weight to matching skills
            matching_skills = expert_skills & learner_skills
            skill_overlap = len(matching_skills) / max(len(expert_skills), len(learner_skills))
            # Boost score if there's any overlap at all
            if matching_skills:
                skill_overlap = max(skill_overlap, 0.5)
            skill_score = skill_overlap * weights["skills"]
            score += skill_score
            print(f"Skill score: {skill_score} (overlap: {skill_overlap})")
        
        # Calculate interest overlap
        expert_interests = set(expert.get("interests", []))
        learner_interests = set(learner.get("interests", []))
        interest_score = 0.0
        if expert_interests and learner_interests:
            # Perfect match for interests is highly valued
            interest_overlap = len(expert_interests & learner_interests) / len(expert_interests | learner_interests)
            interest_score = interest_overlap * weights["interests"]
            score += interest_score
            print(f"Interest score: {interest_score} (overlap: {interest_overlap})")
        
        # Consider experience level difference
        expert_level = expert.get("experience_level", 5)
        learner_level = learner.get("experience_level", 1)
        exp_diff = abs(expert_level - learner_level)
        # Prefer larger experience gaps (better mentoring potential)
        exp_score = (1 - (exp_diff / 4)) * weights["experience_level"]  # Use 4 instead of 5 to be more lenient
        score += exp_score
        print(f"Experience score: {exp_score} (diff: {exp_diff})")
        
        # Consider availability overlap
        availability_score = self._calculate_availability_overlap(
            expert.get("availability", []),
            learner.get("availability", [])
        ) * weights["availability"]
        score += availability_score
        print(f"Availability score: {availability_score}")
        
        print(f"Total score: {score}")
        return score

    def _find_common_interests(
        self,
        expert: Dict[str, Any],
        learner: Dict[str, Any]
    ) -> List[str]:
        """Find common interests between mentor and learner."""
        expert_interests = set(expert.get("interests", []))
        learner_interests = set(learner.get("interests", []))
        return list(expert_interests & learner_interests)

    def _calculate_availability_overlap(
        self,
        expert_availability: List[Dict[str, Any]],
        learner_availability: List[Dict[str, Any]]
    ) -> float:
        """Calculate overlap in availability schedules."""
        if not expert_availability or not learner_availability:
            return 0.0
            
        overlap_hours = 0
        total_hours = 0
        
        for expert_slot in expert_availability:
            for learner_slot in learner_availability:
                if expert_slot["day"] == learner_slot["day"]:
                    overlap = self._calculate_time_overlap(
                        expert_slot["start"],
                        expert_slot["end"],
                        learner_slot["start"],
                        learner_slot["end"]
                    )
                    overlap_hours += overlap
                    
        # Calculate total hours by converting timedelta to hours
        for slot in expert_availability + learner_availability:
            delta = slot["end"] - slot["start"]
            total_hours += delta.total_seconds() / 3600
        
        return overlap_hours / total_hours if total_hours > 0 else 0.0

    def _calculate_time_overlap(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> float:
        """Calculate overlap between two time periods in hours."""
        latest_start = max(start1, start2)
        earliest_end = min(end1, end2)
        overlap = (earliest_end - latest_start).total_seconds() / 3600
        return max(0, overlap)

    async def _calculate_growth_metrics(self) -> Dict[str, Any]:
        """Calculate community growth metrics."""
        now = datetime.now(UTC)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        return {
            "weekly_active_users": await self.graph.count_active_users(week_ago),
            "monthly_active_users": await self.graph.count_active_users(month_ago),
            "new_members": await self.graph.count_new_members(week_ago),
            "content_creation": await self.graph.count_new_content(week_ago),
            "engagement_rate": await self._calculate_engagement_rate(week_ago)
        }

    async def _generate_recommendations(
        self,
        insight: CommunityInsight
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Add recommendations based on insights
        for topic in insight.trending_topics:
            recommendations.append({
                "type": "content",
                "priority": "high",
                "action": f"Create more content about {topic}",
                "reason": "Trending topic with high demand"
            })
            
        for skill in insight.skill_gaps:
            recommendations.append({
                "type": "workshop",
                "priority": "medium",
                "action": f"Organize workshop for {skill}",
                "reason": "Identified skill gap in community"
            })
            
        return recommendations

    async def _categorize_resources(
        self,
        resources: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize resources by type and topic."""
        categories = {}
        
        for resource in resources:
            resource_type = resource.get("type", "other")
            if resource_type not in categories:
                categories[resource_type] = []
            categories[resource_type].append(resource)
            
        return categories

    async def _generate_resource_recommendations(
        self,
        categorized_resources: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for resource improvement."""
        recommendations = []
        
        for category, resources in categorized_resources.items():
            if len(resources) < 3:
                recommendations.append({
                    "type": "content_gap",
                    "category": category,
                    "action": f"Create more {category} resources",
                    "priority": "high"
                })
                
        return recommendations

    async def _calculate_engagement_rate(
        self,
        since: datetime
    ) -> float:
        """Calculate community engagement rate."""
        active_users = await self.graph.count_active_users(since)
        total_users = await self.graph.count_total_users()
        
        if total_users == 0:
            return 0.0
            
        return active_users / total_users 
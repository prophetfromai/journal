from typing import List, Dict, Any
import json
from collections import Counter

from src.core.deepseek_client import DeepSeekClient

class TopicExtractor:
    def __init__(self, deepseek_client: DeepSeekClient):
        self.deepseek = deepseek_client
        self.topic_cache = {}

    async def extract_topics_from_text(self, text: str) -> List[str]:
        """Extract relevant topics from text content."""
        if text in self.topic_cache:
            return self.topic_cache[text]

        prompt = self._create_topic_extraction_prompt(text)
        response = await self.deepseek.generate(prompt)
        
        try:
            topics = json.loads(response)
            self.topic_cache[text] = topics
            return topics
        except json.JSONDecodeError:
            # Fallback to simple topic extraction if JSON parsing fails
            return self._extract_topics_simple(text)

    def _create_topic_extraction_prompt(self, text: str) -> str:
        """Create a prompt for topic extraction."""
        return f"""
        Extract the main topics from the following text. Return them as a JSON array of strings.
        Focus on technical concepts, skills, and domain-specific terminology.
        
        Text:
        {text}
        
        Expected format:
        ["topic1", "topic2", "topic3"]
        """

    def _extract_topics_simple(self, text: str) -> List[str]:
        """Simple topic extraction fallback using common patterns."""
        # Split into words and clean up
        words = text.lower().split()
        
        # Remove common stop words and punctuation
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with"}
        words = [word.strip(".,!?()[]{}") for word in words if word not in stop_words]
        
        # Find potential multi-word topics (e.g., "machine learning")
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        
        # Count occurrences
        word_counts = Counter(words + bigrams)
        
        # Return most common topics
        return [topic for topic, count in word_counts.most_common(10) if len(topic) > 3]

    async def analyze_topic_trends(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze topic trends across multiple texts."""
        all_topics = []
        for text in texts:
            topics = await self.extract_topics_from_text(text)
            all_topics.extend(topics)
        
        topic_counts = Counter(all_topics)
        
        return {
            "trending_topics": [
                {"topic": topic, "count": count}
                for topic, count in topic_counts.most_common(10)
            ],
            "topic_groups": self._group_related_topics(topic_counts),
            "total_topics": len(topic_counts)
        }

    def _group_related_topics(self, topic_counts: Counter) -> List[Dict[str, Any]]:
        """Group related topics together."""
        groups = []
        processed_topics = set()
        
        for topic, count in topic_counts.most_common():
            if topic in processed_topics:
                continue
                
            related = self._find_related_topics(topic, topic_counts.keys())
            if related:
                groups.append({
                    "main_topic": topic,
                    "count": count,
                    "related_topics": list(related)
                })
                processed_topics.add(topic)
                processed_topics.update(related)
            
        return groups

    def _find_related_topics(self, topic: str, all_topics: List[str]) -> set:
        """Find topics that are related to the given topic."""
        related = set()
        words = set(topic.split())
        
        for other in all_topics:
            if other == topic:
                continue
                
            other_words = set(other.split())
            
            # Check for word overlap
            if words & other_words:
                related.add(other)
            # Check if one is a substring of the other
            elif topic in other or other in topic:
                related.add(other)
                
        return related

    def clear_cache(self):
        """Clear the topic cache."""
        self.topic_cache.clear() 
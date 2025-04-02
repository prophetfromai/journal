from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path
import json
import asyncio
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from pytube import YouTube
import os
from ..core.deepseek_client import DeepSeekClient
from ..knowledge_graph.graph_manager import KnowledgeGraphManager

class ContentProcessor:
    def __init__(
        self,
        config_path: str = "config/deepseek.yaml",
        deepseek_client: Optional[DeepSeekClient] = None,
        graph_manager: Optional[KnowledgeGraphManager] = None
    ):
        self.config = self._load_config(config_path)
        self.deepseek_client = deepseek_client or DeepSeekClient(config_path)
        self.graph_manager = graph_manager or KnowledgeGraphManager(config_path)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    async def process_content(
        self,
        content_path: str,
        content_type: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Process content based on its type and store in knowledge graph.
        """
        if content_type == "book":
            return await self._process_book(content_path, metadata)
        elif content_type == "paper":
            return await self._process_paper(content_path, metadata)
        elif content_type == "video":
            return await self._process_video(content_path, metadata)
        elif content_type == "webpage":
            return await self._process_webpage(content_path, metadata)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

    async def _process_book(
        self,
        book_path: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Process a book file and extract structured knowledge.
        """
        # Read book content
        with open(book_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract knowledge using DeepSeek
        knowledge = await self.deepseek_client.extract_knowledge(
            content,
            "book"
        )

        # Store in knowledge graph
        book_id = self.graph_manager.add_knowledge_node(
            content=json.dumps(knowledge),
            content_type="book",
            metadata={
                "file_path": book_path,
                "file_name": os.path.basename(book_path),
                "processed_at": datetime.now().isoformat(),
                **(metadata or {})
            }
        )

        return {
            "book_id": book_id,
            "knowledge": knowledge
        }

    async def _process_paper(
        self,
        paper_path: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Process a scientific paper and extract structured knowledge.
        """
        # Read paper content
        with open(paper_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract knowledge using DeepSeek
        knowledge = await self.deepseek_client.extract_knowledge(
            content,
            "paper"
        )

        # Store in knowledge graph
        paper_id = self.graph_manager.add_knowledge_node(
            content=json.dumps(knowledge),
            content_type="paper",
            metadata={
                "file_path": paper_path,
                "file_name": os.path.basename(paper_path),
                "processed_at": datetime.now().isoformat(),
                **(metadata or {})
            }
        )

        return {
            "paper_id": paper_id,
            "knowledge": knowledge
        }

    async def _process_video(
        self,
        video_url: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Process a YouTube video and extract structured knowledge.
        """
        try:
            # Download video transcript
            yt = YouTube(video_url)
            transcript = yt.captions.get_by_language_code('en')
            
            if not transcript:
                raise ValueError("No English transcript available")
                
            content = transcript.generate_srt_captions()
            
            # Extract knowledge using DeepSeek
            knowledge = await self.deepseek_client.extract_knowledge(
                content,
                "video"
            )

            # Store in knowledge graph
            video_id = self.graph_manager.add_knowledge_node(
                content=json.dumps(knowledge),
                content_type="video",
                metadata={
                    "video_url": video_url,
                    "video_title": yt.title,
                    "processed_at": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )

            return {
                "video_id": video_id,
                "knowledge": knowledge
            }
            
        except Exception as e:
            raise Exception(f"Error processing video: {str(e)}")

    async def _process_webpage(
        self,
        url: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Process a webpage and extract structured knowledge.
        """
        try:
            # Fetch webpage content
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main content (remove scripts, styles, etc.)
            for script in soup(["script", "style"]):
                script.decompose()
                
            content = soup.get_text()
            
            # Extract knowledge using DeepSeek
            knowledge = await self.deepseek_client.extract_knowledge(
                content,
                "webpage"
            )

            # Store in knowledge graph
            webpage_id = self.graph_manager.add_knowledge_node(
                content=json.dumps(knowledge),
                content_type="webpage",
                metadata={
                    "url": url,
                    "title": soup.title.string if soup.title else None,
                    "processed_at": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )

            return {
                "webpage_id": webpage_id,
                "knowledge": knowledge
            }
            
        except Exception as e:
            raise Exception(f"Error processing webpage: {str(e)}")

    def get_processed_content(
        self,
        content_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve processed content from the knowledge graph.
        """
        query = """
        MATCH (n:Knowledge)
        """
        
        if content_type:
            query += "WHERE n.type = $content_type "
            
        query += """
        RETURN n.content as content, n.metadata as metadata
        ORDER BY n.created_at DESC
        LIMIT $limit
        """
        
        return self.graph_manager.query_knowledge(
            query,
            {
                "content_type": content_type,
                "limit": limit
            }
        ) 
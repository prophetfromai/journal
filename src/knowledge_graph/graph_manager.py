from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path
import json
from datetime import datetime, timedelta
import uuid
import networkx as nx
from neo4j import AsyncGraphDatabase
from uuid import UUID

class KnowledgeGraphManager:
    def __init__(self, config_path: str = "config/deepseek.yaml", uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        self.config = self._load_config(config_path)
        self.knowledge_nodes = {}
        self.relationships = {}
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        self.graph = nx.Graph()  # Local cache for quick operations

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    async def get_recent_activity(self, timeframe: timedelta) -> List[Dict[str, Any]]:
        """Get recent community activity within the specified timeframe."""
        since = datetime.utcnow() - timeframe
        query = """
        MATCH (a:Activity)
        WHERE a.timestamp >= $since
        RETURN a
        ORDER BY a.timestamp DESC
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, since=since.isoformat())
            return [record["a"] for record in await result.fetch_all()]

    async def get_resources_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get resources related to a specific topic."""
        query = """
        MATCH (r:Resource)-[:TAGGED]->(t:Topic {name: $topic})
        RETURN r
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, topic=topic)
            return [record["r"] for record in await result.fetch_all()]

    async def find_experts(self, topic: str) -> List[Dict[str, Any]]:
        """Find users with expertise in a specific topic."""
        query = """
        MATCH (u:User)-[e:HAS_EXPERTISE]->(t:Topic {name: $topic})
        WHERE e.level >= 4
        RETURN u, e.level as expertise_level
        ORDER BY e.level DESC
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, topic=topic)
            return [
                {**record["u"], "expertise_level": record["expertise_level"]}
                for record in await result.fetch_all()
            ]

    async def find_learners(self, topic: str) -> List[Dict[str, Any]]:
        """Find users interested in learning a specific topic."""
        query = """
        MATCH (u:User)-[i:INTERESTED_IN]->(t:Topic {name: $topic})
        WHERE NOT (u)-[:HAS_EXPERTISE]->(t) OR (u)-[:HAS_EXPERTISE {level: <= 3}]->(t)
        RETURN u, i.level as interest_level
        ORDER BY i.level DESC
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, topic=topic)
            return [
                {**record["u"], "interest_level": record["interest_level"]}
                for record in await result.fetch_all()
            ]

    async def get_all_resources(self) -> List[Dict[str, Any]]:
        """Get all community resources."""
        query = """
        MATCH (r:Resource)
        OPTIONAL MATCH (r)-[:TAGGED]->(t:Topic)
        RETURN r, collect(t.name) as topics
        """
        
        async with self.driver.session() as session:
            result = await session.run(query)
            return [
                {**record["r"], "topics": record["topics"]}
                for record in await result.fetch_all()
            ]

    async def count_active_users(self, since: datetime) -> int:
        """Count users active since the specified datetime."""
        query = """
        MATCH (u:User)
        WHERE u.last_active >= $since
        RETURN count(u) as active_count
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, since=since.isoformat())
            record = await result.single()
            return record["active_count"]

    async def count_total_users(self) -> int:
        """Count total number of users."""
        query = "MATCH (u:User) RETURN count(u) as total_count"
        
        async with self.driver.session() as session:
            result = await session.run(query)
            record = await result.single()
            return record["total_count"]

    async def count_new_members(self, since: datetime) -> int:
        """Count new members who joined since the specified datetime."""
        query = """
        MATCH (u:User)
        WHERE u.joined_at >= $since
        RETURN count(u) as new_count
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, since=since.isoformat())
            record = await result.single()
            return record["new_count"]

    async def count_new_content(self, since: datetime) -> int:
        """Count new content created since the specified datetime."""
        query = """
        MATCH (c:Content)
        WHERE c.created_at >= $since
        RETURN count(c) as content_count
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, since=since.isoformat())
            record = await result.single()
            return record["content_count"]

    async def add_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new user to the knowledge graph."""
        query = """
        CREATE (u:User {
            id: $id,
            username: $username,
            email: $email,
            joined_at: $joined_at,
            last_active: $last_active
        })
        RETURN u
        """
        
        async with self.driver.session() as session:
            result = await session.run(
                query,
                id=str(user_data["id"]),
                username=user_data["username"],
                email=user_data["email"],
                joined_at=datetime.utcnow().isoformat(),
                last_active=datetime.utcnow().isoformat()
            )
            record = await result.single()
            return record["u"]

    async def add_resource(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new resource to the knowledge graph."""
        query = """
        CREATE (r:Resource {
            id: $id,
            title: $title,
            description: $description,
            type: $type,
            created_at: $created_at,
            updated_at: $updated_at
        })
        WITH r
        UNWIND $topics as topic
        MERGE (t:Topic {name: topic})
        CREATE (r)-[:TAGGED]->(t)
        RETURN r
        """
        
        async with self.driver.session() as session:
            result = await session.run(
                query,
                id=str(resource_data["id"]),
                title=resource_data["title"],
                description=resource_data["description"],
                type=resource_data["type"],
                topics=resource_data.get("topics", []),
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )
            record = await result.single()
            return record["r"]

    async def update_user_expertise(
        self,
        user_id: UUID,
        topic: str,
        level: int
    ) -> None:
        """Update a user's expertise level in a topic."""
        query = """
        MATCH (u:User {id: $user_id})
        MERGE (t:Topic {name: $topic})
        MERGE (u)-[e:HAS_EXPERTISE]->(t)
        SET e.level = $level,
            e.updated_at = $updated_at
        """
        
        async with self.driver.session() as session:
            await session.run(
                query,
                user_id=str(user_id),
                topic=topic,
                level=level,
                updated_at=datetime.utcnow().isoformat()
            )

    async def update_user_interests(
        self,
        user_id: UUID,
        interests: List[str]
    ) -> None:
        """Update a user's interests."""
        query = """
        MATCH (u:User {id: $user_id})
        // Remove old interests
        OPTIONAL MATCH (u)-[i:INTERESTED_IN]->(:Topic)
        DELETE i
        WITH u
        // Add new interests
        UNWIND $interests as interest
        MERGE (t:Topic {name: interest})
        CREATE (u)-[:INTERESTED_IN {level: 1, updated_at: $updated_at}]->(t)
        """
        
        async with self.driver.session() as session:
            await session.run(
                query,
                user_id=str(user_id),
                interests=interests,
                updated_at=datetime.utcnow().isoformat()
            )

    async def record_activity(
        self,
        user_id: UUID,
        activity_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record a user activity in the knowledge graph."""
        query = """
        MATCH (u:User {id: $user_id})
        CREATE (a:Activity {
            id: $activity_id,
            type: $activity_type,
            timestamp: $timestamp,
            metadata: $metadata
        })
        CREATE (u)-[:PERFORMED]->(a)
        RETURN a
        """
        
        async with self.driver.session() as session:
            result = await session.run(
                query,
                user_id=str(user_id),
                activity_id=str(UUID()),
                activity_type=activity_type,
                timestamp=datetime.utcnow().isoformat(),
                metadata=json.dumps(metadata)
            )
            record = await result.single()
            return record["a"]

    async def close(self):
        """Close the database connection."""
        await self.driver.close()

    def add_knowledge_node(
        self,
        content: str,
        content_type: str,
        metadata: Optional[Dict] = None,
        relationships: Optional[List[Dict]] = None
    ) -> str:
        """
        Add a new knowledge node to the graph.
        Returns the node ID.
        """
        node_id = str(uuid.uuid4())
        node = {
            "id": node_id,
            "content": content,
            "type": content_type,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.knowledge_nodes[node_id] = node

        if relationships:
            for rel in relationships:
                self._create_relationship(node_id, rel)

        return node_id

    def _create_relationship(self, source_id: str, relationship: Dict):
        """Create a relationship between nodes."""
        target_id = relationship.get("target_id")
        if not target_id or target_id not in self.knowledge_nodes:
            return

        rel_id = f"{source_id}-{target_id}"
        self.relationships[rel_id] = {
            "source_id": source_id,
            "target_id": target_id,
            "type": relationship.get("type", "RELATES_TO"),
            "properties": relationship.get("properties", {}),
            "created_at": datetime.utcnow().isoformat()
        }

    def query_knowledge(
        self,
        cypher_query: str,
        params: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher-like query on the knowledge graph.
        This is a simplified implementation that supports basic queries.
        """
        # Simple query parser for basic WHERE clause
        if "WHERE n.id =" in cypher_query and params and "workflow_id" in params:
            workflow_id = params["workflow_id"]
            if workflow_id in self.knowledge_nodes:
                node = self.knowledge_nodes[workflow_id]
                return [{"workflow": node["content"]}]
        return []

    def get_related_knowledge(
        self,
        node_id: str,
        relationship_types: Optional[List[str]] = None,
        depth: int = 1
    ) -> List[Dict[str, Any]]:
        """Get related knowledge nodes or a specific node by ID."""
        # First, try to get the node directly
        if node_id in self.knowledge_nodes:
            return [self.knowledge_nodes[node_id]]

        # If not found directly, look for related nodes
        if node_id not in self.knowledge_nodes:
            return []

        related_nodes = []
        for rel_id, rel in self.relationships.items():
            if rel["source_id"] == node_id:
                if not relationship_types or rel["type"] in relationship_types:
                    target_id = rel["target_id"]
                    if target_id in self.knowledge_nodes:
                        related_nodes.append(self.knowledge_nodes[target_id])

        return related_nodes

    def update_knowledge_node(
        self,
        node_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a knowledge node."""
        if node_id not in self.knowledge_nodes:
            return False

        node = self.knowledge_nodes[node_id]
        node.update(updates)
        node["updated_at"] = datetime.utcnow().isoformat()
        return True

    def delete_knowledge_node(
        self,
        node_id: str,
        cascade: bool = False
    ) -> bool:
        """Delete a knowledge node and optionally its relationships."""
        if node_id not in self.knowledge_nodes:
            return False

        if cascade:
            # Delete all relationships
            self.relationships = {
                rel_id: rel for rel_id, rel in self.relationships.items()
                if rel["source_id"] != node_id and rel["target_id"] != node_id
            }

        del self.knowledge_nodes[node_id]
        return True 
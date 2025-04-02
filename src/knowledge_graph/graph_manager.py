from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path
import json
from datetime import datetime
import uuid

class KnowledgeGraphManager:
    def __init__(self, config_path: str = "config/deepseek.yaml"):
        self.config = self._load_config(config_path)
        self.knowledge_nodes = {}
        self.relationships = {}

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def close(self):
        """Clean up resources."""
        self.knowledge_nodes.clear()
        self.relationships.clear()

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
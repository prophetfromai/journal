from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase, Driver, Session
import yaml
from pathlib import Path
import json
from datetime import datetime

class KnowledgeGraphManager:
    def __init__(self, config_path: str = "config/deepseek.yaml"):
        self.config = self._load_config(config_path)
        self.driver = self._create_driver()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _create_driver(self) -> Driver:
        """Create Neo4j driver instance."""
        return GraphDatabase.driver(
            self.config['knowledge_graph']['neo4j_uri'],
            auth=(
                self.config['knowledge_graph']['username'],
                self.config['knowledge_graph']['password']
            )
        )

    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()

    def _create_session(self) -> Session:
        """Create a new Neo4j session."""
        return self.driver.session(database=self.config['knowledge_graph']['database'])

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
        with self._create_session() as session:
            # Create base node
            query = """
            CREATE (n:Knowledge {
                content: $content,
                type: $type,
                metadata: $metadata,
                created_at: datetime(),
                updated_at: datetime()
            })
            RETURN id(n) as node_id
            """
            
            result = session.run(
                query,
                content=content,
                type=content_type,
                metadata=metadata or {}
            )
            
            node_id = result.single()["node_id"]

            # Create relationships if specified
            if relationships:
                for rel in relationships:
                    rel_query = """
                    MATCH (source:Knowledge)
                    WHERE id(source) = $source_id
                    MATCH (target:Knowledge)
                    WHERE id(target) = $target_id
                    CREATE (source)-[r:RELATES_TO {
                        type: $rel_type,
                        properties: $properties,
                        created_at: datetime()
                    }]->(target)
                    """
                    
                    session.run(
                        rel_query,
                        source_id=node_id,
                        target_id=rel["target_id"],
                        rel_type=rel.get("type", "RELATES_TO"),
                        properties=rel.get("properties", {})
                    )

            return str(node_id)

    def query_knowledge(
        self,
        cypher_query: str,
        params: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query on the knowledge graph.
        """
        with self._create_session() as session:
            result = session.run(cypher_query, params or {})
            return [dict(record) for record in result]

    def get_related_knowledge(
        self,
        node_id: str,
        relationship_types: Optional[List[str]] = None,
        depth: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get related knowledge nodes based on relationships.
        """
        rel_types = relationship_types or ["RELATES_TO"]
        rel_pattern = "|".join(rel_types)
        
        query = f"""
        MATCH (n:Knowledge)
        WHERE id(n) = $node_id
        MATCH path = (n)-[r:{rel_pattern}*1..{depth}]->(related:Knowledge)
        RETURN path
        """
        
        with self._create_session() as session:
            result = session.run(query, node_id=int(node_id))
            return [dict(record) for record in result]

    def update_knowledge_node(
        self,
        node_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update properties of a knowledge node.
        """
        set_clauses = []
        params = {"node_id": int(node_id)}
        
        for key, value in updates.items():
            set_clauses.append(f"n.{key} = ${key}")
            params[key] = value
        
        set_clauses.append("n.updated_at = datetime()")
        
        query = f"""
        MATCH (n:Knowledge)
        WHERE id(n) = $node_id
        SET {', '.join(set_clauses)}
        RETURN count(n) > 0 as updated
        """
        
        with self._create_session() as session:
            result = session.run(query, params)
            return result.single()["updated"]

    def delete_knowledge_node(
        self,
        node_id: str,
        cascade: bool = False
    ) -> bool:
        """
        Delete a knowledge node and optionally its relationships.
        """
        query = """
        MATCH (n:Knowledge)
        WHERE id(n) = $node_id
        """
        
        if cascade:
            query += "DETACH DELETE n"
        else:
            query += "DELETE n"
            
        query += " RETURN count(n) > 0 as deleted"
        
        with self._create_session() as session:
            result = session.run(query, node_id=int(node_id))
            return result.single()["deleted"] 
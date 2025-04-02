from graph_manager import KnowledgeGraphManager
import yaml
from pathlib import Path

def init_graph():
    """
    Initialize the Neo4j knowledge graph with necessary indexes and constraints.
    """
    # Load configuration
    config_path = Path("config/deepseek.yaml")
    if not config_path.exists():
        print("Error: Configuration file not found at config/deepseek.yaml")
        return

    # Initialize graph manager
    graph_manager = KnowledgeGraphManager()

    try:
        # Create indexes
        indexes = [
            """
            CREATE INDEX knowledge_type IF NOT EXISTS
            FOR (n:Knowledge) ON (n.type)
            """,
            """
            CREATE INDEX knowledge_created_at IF NOT EXISTS
            FOR (n:Knowledge) ON (n.created_at)
            """,
            """
            CREATE INDEX knowledge_updated_at IF NOT EXISTS
            FOR (n:Knowledge) ON (n.updated_at)
            """
        ]

        # Create constraints
        constraints = [
            """
            CREATE CONSTRAINT knowledge_id IF NOT EXISTS
            FOR (n:Knowledge) REQUIRE n.id IS UNIQUE
            """
        ]

        # Execute indexes
        for index in indexes:
            graph_manager.query_knowledge(index)
            print(f"Created index: {index.split()[2]}")

        # Execute constraints
        for constraint in constraints:
            graph_manager.query_knowledge(constraint)
            print(f"Created constraint: {constraint.split()[2]}")

        print("Knowledge graph initialization completed successfully!")

    except Exception as e:
        print(f"Error initializing knowledge graph: {str(e)}")
    finally:
        graph_manager.close()

if __name__ == "__main__":
    init_graph() 
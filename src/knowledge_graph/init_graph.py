from graph_manager import KnowledgeGraphManager
import yaml
from pathlib import Path

def init_graph():
    """
    Initialize the knowledge graph with necessary structures.
    """
    # Load configuration
    config_path = Path("config/deepseek.yaml")
    if not config_path.exists():
        print("Error: Configuration file not found at config/deepseek.yaml")
        return

    # Initialize graph manager
    graph_manager = KnowledgeGraphManager()

    try:
        # Add some initial knowledge nodes
        initial_nodes = [
            {
                "content": "System initialized",
                "content_type": "system",
                "metadata": {"version": "1.0.0"}
            },
            {
                "content": "LM Studio server running on port 1234",
                "content_type": "system",
                "metadata": {"component": "llm"}
            }
        ]

        for node in initial_nodes:
            graph_manager.add_knowledge_node(**node)

        print("Knowledge graph initialized successfully")
        print(f"Added {len(initial_nodes)} initial nodes")

    except Exception as e:
        print(f"Error initializing knowledge graph: {str(e)}")
    finally:
        graph_manager.close()

if __name__ == "__main__":
    init_graph() 
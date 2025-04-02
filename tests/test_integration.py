import pytest
import asyncio
from pathlib import Path
import json
from src.core.deepseek_client import DeepSeekClient
from src.knowledge_graph.graph_manager import KnowledgeGraphManager
from src.workflows.workflow_manager import WorkflowManager
from src.tools.content_processor import ContentProcessor

@pytest.fixture
async def deepseek_client():
    client = DeepSeekClient()
    yield client

@pytest.fixture
async def graph_manager():
    manager = KnowledgeGraphManager()
    yield manager
    manager.close()

@pytest.fixture
async def workflow_manager(deepseek_client, graph_manager):
    manager = WorkflowManager(deepseek_client=deepseek_client, graph_manager=graph_manager)
    yield manager

@pytest.fixture
async def content_processor(deepseek_client, graph_manager):
    processor = ContentProcessor(deepseek_client=deepseek_client, graph_manager=graph_manager)
    yield processor

@pytest.mark.asyncio
async def test_workflow_generation_and_execution(workflow_manager):
    """Test workflow generation and execution."""
    # Generate workflow
    workflow = await workflow_manager.generate_workflow(
        "Create a simple Python function that adds two numbers",
        ["Use type hints", "Include docstring"]
    )
    
    assert workflow is not None
    assert "id" in workflow
    assert "steps" in workflow
    
    # Execute workflow
    result = await workflow_manager.execute_workflow(
        workflow["id"],
        {"numbers": [5, 3]}
    )
    
    assert result is not None
    assert len(result) > 0

@pytest.mark.asyncio
async def test_content_processing(content_processor):
    """Test content processing for different types."""
    # Create test content
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Test book processing
    book_path = test_dir / "test_book.txt"
    book_path.write_text("This is a test book content.")
    
    book_result = await content_processor.process_content(
        str(book_path),
        "book",
        {"author": "Test Author"}
    )
    
    assert book_result is not None
    assert "book_id" in book_result
    assert "knowledge" in book_result
    
    # Test paper processing
    paper_path = test_dir / "test_paper.txt"
    paper_path.write_text("This is a test paper content.")
    
    paper_result = await content_processor.process_content(
        str(paper_path),
        "paper",
        {"authors": ["Test Author 1", "Test Author 2"]}
    )
    
    assert paper_result is not None
    assert "paper_id" in paper_result
    assert "knowledge" in paper_result
    
    # Cleanup
    book_path.unlink()
    paper_path.unlink()
    test_dir.rmdir()

@pytest.mark.asyncio
async def test_knowledge_graph_operations(graph_manager):
    """Test knowledge graph operations."""
    # Add test node
    node_id = graph_manager.add_knowledge_node(
        content="Test content",
        content_type="test",
        metadata={"test": True}
    )
    
    assert node_id is not None
    
    # Query node
    result = graph_manager.query_knowledge(
        """
        MATCH (n:Knowledge)
        WHERE n.id = $node_id
        RETURN n.content as content, n.type as type, n.metadata as metadata
        """,
        {"node_id": node_id}
    )
    
    assert len(result) == 1
    assert result[0]["content"] == "Test content"
    assert result[0]["type"] == "test"
    assert result[0]["metadata"]["test"] is True
    
    # Update node
    success = graph_manager.update_knowledge_node(
        node_id,
        {"content": "Updated content"}
    )
    
    assert success is True
    
    # Verify update
    result = graph_manager.query_knowledge(
        """
        MATCH (n:Knowledge)
        WHERE n.id = $node_id
        RETURN n.content as content
        """,
        {"node_id": node_id}
    )
    
    assert result[0]["content"] == "Updated content"
    
    # Delete node
    success = graph_manager.delete_knowledge_node(node_id)
    assert success is True

@pytest.mark.asyncio
async def test_deepseek_client(deepseek_client):
    """Test DeepSeek client operations."""
    # Test basic generation
    response = await deepseek_client.generate(
        "What is 2 + 2?",
        max_tokens=100
    )
    
    assert response is not None
    assert isinstance(response, str)
    
    # Test code analysis
    code = """
    def add(a: int, b: int) -> int:
        return a + b
    """
    
    analysis = await deepseek_client.analyze_code(code)
    assert analysis is not None
    assert isinstance(analysis, dict)
    
    # Test knowledge extraction
    knowledge = await deepseek_client.extract_knowledge(
        "Python is a programming language.",
        "text"
    )
    
    assert knowledge is not None
    assert isinstance(knowledge, dict) 
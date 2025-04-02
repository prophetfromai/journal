import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from pathlib import Path

from core.deepseek_client import DeepSeekClient
from knowledge_graph.graph_manager import KnowledgeGraphManager
from workflows.workflow_manager import WorkflowManager
from tools.content_processor import ContentProcessor

app = FastAPI(title="Autonomous AI System")

# Initialize components
deepseek_client = DeepSeekClient()
graph_manager = KnowledgeGraphManager()
workflow_manager = WorkflowManager(deepseek_client=deepseek_client, graph_manager=graph_manager)
content_processor = ContentProcessor(deepseek_client=deepseek_client, graph_manager=graph_manager)

class ContentRequest(BaseModel):
    content_path: str
    content_type: str
    metadata: Optional[Dict] = None

class WorkflowRequest(BaseModel):
    task_description: str
    constraints: Optional[List[str]] = None
    parameters: Optional[Dict] = None

@app.post("/process-content")
async def process_content(request: ContentRequest):
    """
    Process content (book, paper, video, webpage) and store in knowledge graph.
    """
    try:
        result = await content_processor.process_content(
            request.content_path,
            request.content_type,
            request.metadata
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-workflow")
async def generate_workflow(request: WorkflowRequest):
    """
    Generate a workflow based on task description.
    """
    try:
        workflow = await workflow_manager.generate_workflow(
            request.task_description,
            request.constraints
        )
        return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-workflow/{workflow_id}")
async def execute_workflow(workflow_id: str, request: WorkflowRequest):
    """
    Execute a workflow by ID.
    """
    try:
        result = await workflow_manager.execute_workflow(
            workflow_id,
            request.parameters
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/active-workflows")
async def get_active_workflows():
    """
    Get list of currently active workflows.
    """
    return workflow_manager.get_active_workflows()

@app.get("/knowledge/{content_type}")
async def get_knowledge(content_type: Optional[str] = None, limit: int = 10):
    """
    Retrieve processed content from the knowledge graph.
    """
    return content_processor.get_processed_content(content_type, limit)

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000) 
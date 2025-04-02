import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Path as FastAPIPath, Request
from pydantic import BaseModel, UUID4, constr
from typing import Dict, List, Optional, Any, Annotated
from pathlib import Path
import sys
import os
import re
from uuid import UUID

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.deepseek_client import DeepSeekClient
from src.knowledge_graph.graph_manager import KnowledgeGraphManager
from src.workflows.workflow_manager import WorkflowManager
from src.tools.content_processor import ContentProcessor

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

def validate_uuid(value: str) -> str:
    """Validate that a string is a valid UUID."""
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    if not uuid_pattern.match(value):
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    return value

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
async def execute_workflow(
    workflow_request: WorkflowRequest,
    workflow_id: UUID = FastAPIPath(..., description="The ID of the workflow to execute")
):
    """
    Execute a workflow by ID.
    """
    try:
        # Convert UUID to string
        workflow_id_str = str(workflow_id)
        
        # Check if workflow exists
        if workflow_id_str not in graph_manager.knowledge_nodes:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id_str} not found")

        try:
            result = await workflow_manager.execute_workflow(
                workflow_id_str,
                workflow_request.parameters
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            import traceback
            error_details = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            raise HTTPException(status_code=500, detail=error_details)
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_details)

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
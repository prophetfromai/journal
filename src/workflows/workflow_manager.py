from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path
import json
import asyncio
from datetime import datetime
import git
from src.core.deepseek_client import DeepSeekClient
from src.knowledge_graph.graph_manager import KnowledgeGraphManager

class WorkflowManager:
    def __init__(
        self,
        config_path: str = "config/deepseek.yaml",
        deepseek_client: Optional[DeepSeekClient] = None,
        graph_manager: Optional[KnowledgeGraphManager] = None
    ):
        self.config = self._load_config(config_path)
        self.deepseek_client = deepseek_client or DeepSeekClient(config_path)
        self.graph_manager = graph_manager or KnowledgeGraphManager(config_path)
        self.active_workflows: Dict[str, asyncio.Task] = {}

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    async def generate_workflow(
        self,
        task_description: str,
        constraints: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate a workflow using DeepSeek.
        """
        workflow = await self.deepseek_client.generate_workflow(
            task_description,
            constraints
        )
        
        # Store workflow in knowledge graph
        workflow_id = self.graph_manager.add_knowledge_node(
            content=json.dumps(workflow),
            content_type="workflow",
            metadata={
                "task_description": task_description,
                "constraints": constraints,
                "generated_at": datetime.now().isoformat()
            }
        )
        
        workflow["id"] = workflow_id
        return workflow

    async def execute_workflow(
        self,
        workflow_id: str,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """
        Execute a workflow by ID.
        """
        # Get workflow from knowledge graph
        if workflow_id not in self.graph_manager.knowledge_nodes:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        workflow_node = self.graph_manager.knowledge_nodes[workflow_id]
        workflow_content = workflow_node["content"]
        
        # Create a simple workflow structure
        workflow = {
            "steps": [
                {
                    "type": "code_generation",
                    "id": "step1",
                    "prompt": workflow_content,
                    "parameters": parameters or {}
                }
            ]
        }
        
        # Create execution task
        task = asyncio.create_task(
            self._execute_workflow_steps(workflow, parameters or {})
        )
        
        # Store active workflow
        self.active_workflows[workflow_id] = task
        
        try:
            result = await task
            return result
        finally:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

    async def _execute_workflow_steps(
        self,
        workflow: Dict,
        parameters: Dict
    ) -> Dict:
        """
        Execute workflow steps sequentially.
        """
        results = {}
        
        for step in workflow.get("steps", []):
            step_type = step.get("type")
            step_params = step.get("parameters", {})
            
            # Merge workflow parameters with step parameters
            merged_params = {**parameters, **step_params}
            
            if step_type == "code_generation":
                result = await self._execute_code_generation_step(step, merged_params)
            elif step_type == "knowledge_extraction":
                result = await self._execute_knowledge_extraction_step(step, merged_params)
            elif step_type == "git_operation":
                result = await self._execute_git_operation_step(step, merged_params)
            else:
                raise ValueError(f"Unknown step type: {step_type}")
                
            results[step.get("id", "unknown")] = result
            
        return results

    async def _execute_code_generation_step(
        self,
        step: Dict,
        parameters: Dict
    ) -> Dict:
        """
        Execute a code generation step.
        """
        prompt = step.get("prompt", "")
        context = step.get("context", {})
        
        # Generate code using DeepSeek
        code = await self.deepseek_client.generate(
            prompt,
            max_tokens=step.get("max_tokens", 2000)
        )
        
        # Store generated code in knowledge graph
        code_id = self.graph_manager.add_knowledge_node(
            content=code,
            content_type="generated_code",
            metadata={
                "step_id": step.get("id"),
                "context": context,
                "parameters": parameters,
                "generated_at": datetime.now().isoformat()
            }
        )
        
        return {
            "code_id": code_id,
            "code": code,
            "context": context
        }

    async def _execute_knowledge_extraction_step(
        self,
        step: Dict,
        parameters: Dict
    ) -> Dict:
        """
        Execute a knowledge extraction step.
        """
        content = step.get("content", "")
        content_type = step.get("content_type", "text")
        
        # Extract knowledge using DeepSeek
        knowledge = await self.deepseek_client.extract_knowledge(
            content,
            content_type
        )
        
        # Store extracted knowledge in graph
        knowledge_id = self.graph_manager.add_knowledge_node(
            content=json.dumps(knowledge),
            content_type="extracted_knowledge",
            metadata={
                "step_id": step.get("id"),
                "source_content_type": content_type,
                "extracted_at": datetime.now().isoformat()
            }
        )
        
        return {
            "knowledge_id": knowledge_id,
            "knowledge": knowledge
        }

    async def _execute_git_operation_step(
        self,
        step: Dict,
        parameters: Dict
    ) -> Dict:
        """
        Execute a Git operation step.
        """
        operation = step.get("operation")
        repo_path = step.get("repo_path", self.config["git"]["base_repo_path"])
        
        try:
            repo = git.Repo(repo_path)
            
            if operation == "commit":
                message = step.get("message", "AI: Automated commit")
                repo.index.add(step.get("files", []))
                commit = repo.index.commit(message)
                return {"commit_hash": commit.hexsha}
                
            elif operation == "branch":
                branch_name = step.get("branch_name")
                if not branch_name:
                    raise ValueError("Branch name required for branch operation")
                    
                new_branch = repo.create_head(branch_name)
                new_branch.checkout()
                return {"branch_name": branch_name}
                
            else:
                raise ValueError(f"Unknown Git operation: {operation}")
                
        except git.GitCommandError as e:
            raise Exception(f"Git operation failed: {str(e)}")

    def get_active_workflows(self) -> List[Dict]:
        """
        Get list of currently active workflows.
        """
        return [
            {
                "workflow_id": workflow_id,
                "status": "running" if not task.done() else "completed",
                "result": task.result() if task.done() else None
            }
            for workflow_id, task in self.active_workflows.items()
        ] 
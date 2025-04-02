"""
Global Coordination System for Distributed AI Code Generation.

This module provides tools for coordinating work across multiple repositories
and ensuring consistent branch naming and work area management.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import subprocess
from coordination_manager import CoordinationManager

class GlobalCoordinator:
    """Manages global coordination between distributed AI code generation agents."""
    
    def __init__(self, repo_root: str = "."):
        """Initialize the global coordinator.
        
        Args:
            repo_root: Path to the repository root directory
        """
        self.repo_root = Path(repo_root)
        self.coordinator = CoordinationManager(repo_root)
        
    def _run_git_command(self, command: str) -> Tuple[str, str]:
        """Run a git command and return its output.
        
        Args:
            command: The git command to run
            
        Returns:
            Tuple of (stdout, stderr)
        """
        try:
            result = subprocess.run(
                command.split(),
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            return result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.stdout, e.stderr
            
    def get_remote_branches(self) -> List[str]:
        """Get list of remote branches.
        
        Returns:
            List of remote branch names
        """
        stdout, _ = self._run_git_command("git branch -r")
        return [b.strip() for b in stdout.split('\n') if b.strip()]
        
    def get_local_branches(self) -> List[str]:
        """Get list of local branches.
        
        Returns:
            List of local branch names
        """
        stdout, _ = self._run_git_command("git branch")
        return [b.strip().replace('* ', '') for b in stdout.split('\n') if b.strip()]
        
    def is_branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists locally or remotely.
        
        Args:
            branch_name: Name of the branch to check
            
        Returns:
            True if branch exists, False otherwise
        """
        local_branches = self.get_local_branches()
        remote_branches = self.get_remote_branches()
        return branch_name in local_branches or branch_name in remote_branches
        
    def create_work_branch(self, area_id: str, agent_id: str) -> Optional[str]:
        """Create a new branch for a work area.
        
        Args:
            area_id: The work area ID
            agent_id: The ID of the agent creating the branch
            
        Returns:
            The branch name if successful, None otherwise
        """
        # Check if area is available
        available_areas = self.coordinator.get_available_areas()
        if not any(area['id'] == area_id for area in available_areas):
            return None
            
        # Check dependencies
        deps_met, _ = self.coordinator.check_dependencies(area_id)
        if not deps_met:
            return None
            
        # Create branch name
        branch_name = f"feature/{area_id}-{agent_id}"
        
        # Check if branch already exists
        if self.is_branch_exists(branch_name):
            return None
            
        # Create and switch to new branch
        stdout, stderr = self._run_git_command(f"git checkout -b {branch_name}")
        if stderr:
            return None
            
        # Update coordination file
        if not self.coordinator.claim_area(area_id, agent_id):
            self._run_git_command("git checkout main")
            self._run_git_command(f"git branch -D {branch_name}")
            return None
            
        return branch_name
        
    def complete_work_branch(self, branch_name: str, agent_id: str) -> bool:
        """Complete work on a branch and merge it.
        
        Args:
            branch_name: Name of the branch to complete
            agent_id: ID of the agent completing the work
            
        Returns:
            True if successful, False otherwise
        """
        # Extract area_id from branch name
        match = re.match(r"feature/([A-Z]+-\d+)-", branch_name)
        if not match:
            return False
            
        area_id = match.group(1)
        
        # Switch to main branch
        stdout, stderr = self._run_git_command("git checkout main")
        if stderr:
            return False
            
        # Pull latest changes
        stdout, stderr = self._run_git_command("git pull")
        if stderr:
            return False
            
        # Merge the feature branch
        stdout, stderr = self._run_git_command(f"git merge {branch_name}")
        if stderr:
            return False
            
        # Update coordination file
        if not self.coordinator.complete_area(area_id, agent_id):
            return False
            
        # Delete the feature branch
        self._run_git_command(f"git branch -D {branch_name}")
        return True
        
    def get_available_work(self, agent_capabilities: List[str], 
                          priority: str = "HIGH") -> Optional[Dict[str, str]]:
        """Get next available work area that isn't being worked on in any branch.
        
        Args:
            agent_capabilities: List of capabilities the agent has
            priority: Preferred priority level
            
        Returns:
            Dictionary containing area information if found, None otherwise
        """
        # Get all remote branches
        remote_branches = self.get_remote_branches()
        
        # Get available areas from coordination file
        available_areas = self.coordinator.get_available_areas()
        
        # Filter out areas that are being worked on in branches
        active_area_ids = set()
        for branch in remote_branches:
            match = re.match(r"origin/feature/([A-Z]+-\d+)-", branch)
            if match:
                active_area_ids.add(match.group(1))
                
        # Find first available area that isn't being worked on
        for area in available_areas:
            if (area['id'] not in active_area_ids and 
                area['priority'] == priority and
                any(cap in area['id'] for cap in agent_capabilities)):
                return area
                
        return None
        
    def sync_coordination_file(self) -> bool:
        """Sync the coordination file with current branch state.
        
        Returns:
            True if successful, False otherwise
        """
        # Get all remote branches
        remote_branches = self.get_remote_branches()
        
        # Update active areas based on branches
        active_areas = self.coordinator.get_active_areas()
        for branch in remote_branches:
            match = re.match(r"origin/feature/([A-Z]+-\d+)-([A-Z0-9-]+)", branch)
            if match:
                area_id, agent_id = match.groups()
                # Update area status if needed
                for area in active_areas:
                    if area['id'] == area_id and area['assigned_to'] != agent_id:
                        self.coordinator.claim_area(area_id, agent_id)
                        break
                        
        return True
        
    def get_work_status(self, area_id: str) -> Dict[str, str]:
        """Get current status of a work area across all branches.
        
        Args:
            area_id: The work area ID to check
            
        Returns:
            Dictionary containing status information
        """
        status = {
            'area_id': area_id,
            'branch_exists': False,
            'branch_name': None,
            'assigned_to': None,
            'status': 'AVAILABLE'
        }
        
        # Check remote branches
        remote_branches = self.get_remote_branches()
        for branch in remote_branches:
            match = re.match(r"origin/feature/([A-Z]+-\d+)-([A-Z0-9-]+)", branch)
            if match:
                branch_area_id, agent_id = match.groups()
                if branch_area_id == area_id:
                    status.update({
                        'branch_exists': True,
                        'branch_name': branch,
                        'assigned_to': agent_id,
                        'status': 'IN_PROGRESS'
                    })
                    break
                    
        return status 
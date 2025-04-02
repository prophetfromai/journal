"""
Example script demonstrating how to use the global coordination system
for distributed AI code generation.
"""

import os
from typing import List, Optional, Dict
from global_coordinator import GlobalCoordinator

class DistributedAIAgent:
    """Example distributed AI agent that uses the global coordination system."""
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        """Initialize the distributed AI agent.
        
        Args:
            agent_id: Unique identifier for this agent
            capabilities: List of capabilities this agent has
        """
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.coordinator = GlobalCoordinator()
        
    def start_work(self) -> Optional[str]:
        """Start working on an available work area.
        
        Returns:
            The branch name if successful, None otherwise
        """
        # Sync coordination file with current branch state
        self.coordinator.sync_coordination_file()
        
        # Get next available work area
        work_area = self.coordinator.get_available_work(
            self.capabilities,
            priority="HIGH"
        )
        
        if not work_area:
            print(f"Agent {self.agent_id}: No suitable work areas found")
            return None
            
        # Create branch for the work area
        branch_name = self.coordinator.create_work_branch(
            work_area['id'],
            self.agent_id
        )
        
        if branch_name:
            print(f"Agent {self.agent_id}: Created branch {branch_name}")
            print(f"Description: {work_area['description']}")
            return branch_name
        else:
            print(f"Agent {self.agent_id}: Failed to create branch")
            return None
            
    def complete_work(self, branch_name: str) -> bool:
        """Complete work on a branch.
        
        Args:
            branch_name: Name of the branch to complete
            
        Returns:
            True if successful, False otherwise
        """
        if self.coordinator.complete_work_branch(branch_name, self.agent_id):
            print(f"Agent {self.agent_id}: Successfully completed work on {branch_name}")
            return True
        else:
            print(f"Agent {self.agent_id}: Failed to complete work on {branch_name}")
            return False
            
    def check_work_status(self, area_id: str) -> Dict[str, str]:
        """Check the status of a work area.
        
        Args:
            area_id: The work area ID to check
            
        Returns:
            Dictionary containing status information
        """
        return self.coordinator.get_work_status(area_id)

def main():
    """Example usage of the distributed AI agent coordination system."""
    
    # Create two example agents with different capabilities
    agent1 = DistributedAIAgent("AGENT-001", ["FEAT", "TEST", "DOCS"])
    agent2 = DistributedAIAgent("AGENT-002", ["FIX", "PERF", "SEC"])
    
    # Agent 1 starts work
    print("\nAgent 1 starting work...")
    branch1 = agent1.start_work()
    
    # Agent 2 starts work
    print("\nAgent 2 starting work...")
    branch2 = agent2.start_work()
    
    # Check status of a work area
    print("\nChecking status of FEAT-003...")
    status = agent1.check_work_status("FEAT-003")
    print(f"Status: {status}")
    
    # Agent 1 completes work
    if branch1:
        print("\nAgent 1 completing work...")
        agent1.complete_work(branch1)
        
    # Agent 2 completes work
    if branch2:
        print("\nAgent 2 completing work...")
        agent2.complete_work(branch2)

if __name__ == "__main__":
    main() 
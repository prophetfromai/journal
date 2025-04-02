"""
Example script demonstrating how AI agents can use the coordination system.
"""

import os
from typing import List
from coordination_manager import CoordinationManager

class AIAgent:
    """Example AI agent that uses the coordination system."""
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        """Initialize the AI agent.
        
        Args:
            agent_id: Unique identifier for this agent
            capabilities: List of capabilities this agent has
        """
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.coordinator = CoordinationManager()
        
    def find_and_claim_work(self) -> bool:
        """Find and claim available work.
        
        Returns:
            True if work was found and claimed, False otherwise
        """
        # Get next available work area
        work_area = self.coordinator.get_next_available_area(
            self.capabilities,
            priority="HIGH"
        )
        
        if not work_area:
            print(f"Agent {self.agent_id}: No suitable work areas found")
            return False
            
        # Check dependencies
        deps_met, unmet_deps = self.coordinator.check_dependencies(work_area['id'])
        if not deps_met:
            print(f"Agent {self.agent_id}: Dependencies not met for {work_area['id']}")
            print(f"Unmet dependencies: {', '.join(unmet_deps)}")
            return False
            
        # Try to claim the work area
        if self.coordinator.claim_area(work_area['id'], self.agent_id):
            print(f"Agent {self.agent_id}: Successfully claimed {work_area['id']}")
            print(f"Description: {work_area['description']}")
            return True
        else:
            print(f"Agent {self.agent_id}: Failed to claim {work_area['id']}")
            return False
            
    def complete_work(self, area_id: str) -> bool:
        """Mark work as completed.
        
        Args:
            area_id: ID of the work area to complete
            
        Returns:
            True if successful, False otherwise
        """
        if self.coordinator.complete_area(area_id, self.agent_id):
            print(f"Agent {self.agent_id}: Successfully completed {area_id}")
            return True
        else:
            print(f"Agent {self.agent_id}: Failed to complete {area_id}")
            return False
            
    def add_new_work_area(self, category: str, description: str, 
                         priority: str = "HIGH", dependencies: str = "") -> str:
        """Add a new work area.
        
        Args:
            category: Category of the work area
            description: Description of the work
            priority: Priority level
            dependencies: Comma-separated list of dependencies
            
        Returns:
            The new area ID if successful, empty string otherwise
        """
        area_id = self.coordinator.add_new_area(
            category=category,
            description=description,
            priority=priority,
            dependencies=dependencies
        )
        
        if area_id:
            print(f"Agent {self.agent_id}: Added new work area {area_id}")
        else:
            print(f"Agent {self.agent_id}: Failed to add new work area")
            
        return area_id or ""

def main():
    """Example usage of the AI agent coordination system."""
    
    # Create two example agents with different capabilities
    agent1 = AIAgent("AGENT-001", ["FEAT", "TEST", "DOCS"])
    agent2 = AIAgent("AGENT-002", ["FIX", "PERF", "SEC"])
    
    # Agent 1 finds and claims work
    print("\nAgent 1 looking for work...")
    agent1.find_and_claim_work()
    
    # Agent 2 finds and claims work
    print("\nAgent 2 looking for work...")
    agent2.find_and_claim_work()
    
    # Agent 1 adds a new work area
    print("\nAgent 1 adding new work area...")
    new_area = agent1.add_new_work_area(
        category="FEAT",
        description="Add new feature for workflow optimization",
        priority="HIGH",
        dependencies="FEAT-001"
    )
    
    # Agent 2 tries to claim the new work area
    print("\nAgent 2 trying to claim new work area...")
    agent2.find_and_claim_work()
    
    # Agent 1 completes its work
    print("\nAgent 1 completing work...")
    agent1.complete_work("FEAT-002")

if __name__ == "__main__":
    main() 
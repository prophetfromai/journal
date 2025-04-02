"""
Coordination Manager for AI Code Generation Agents.

This module provides tools for AI agents to interact with the AI_COORDINATION.md file,
helping them select work areas and manage their status.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class CoordinationManager:
    """Manages coordination between AI code generation agents."""
    
    def __init__(self, repo_root: str = "."):
        """Initialize the coordination manager.
        
        Args:
            repo_root: Path to the repository root directory
        """
        self.repo_root = Path(repo_root)
        self.coordination_file = self.repo_root / "AI_COORDINATION.md"
        
    def _read_coordination_file(self) -> str:
        """Read the contents of the coordination file.
        
        Returns:
            The contents of the file as a string
        """
        if not self.coordination_file.exists():
            raise FileNotFoundError("AI_COORDINATION.md not found")
        return self.coordination_file.read_text()
    
    def _write_coordination_file(self, content: str) -> None:
        """Write content to the coordination file.
        
        Args:
            content: The content to write
        """
        self.coordination_file.write_text(content)
    
    def get_available_areas(self) -> List[Dict[str, str]]:
        """Get all available work areas.
        
        Returns:
            List of dictionaries containing area information
        """
        content = self._read_coordination_file()
        available_section = re.search(r"### Available Work Areas\n(.*?)(?=\n##|$)", content, re.DOTALL)
        if not available_section:
            return []
            
        areas = []
        for line in available_section.group(1).split('\n'):
            if '|' in line and not line.startswith('|--'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5:
                    areas.append({
                        'id': parts[1],
                        'description': parts[2],
                        'priority': parts[3],
                        'dependencies': parts[4]
                    })
        return areas
    
    def get_active_areas(self) -> List[Dict[str, str]]:
        """Get all active work areas.
        
        Returns:
            List of dictionaries containing active area information
        """
        content = self._read_coordination_file()
        active_section = re.search(r"### Active Work Areas\n(.*?)(?=\n###|$)", content, re.DOTALL)
        if not active_section:
            return []
            
        areas = []
        for line in active_section.group(1).split('\n'):
            if '|' in line and not line.startswith('|--'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6:
                    areas.append({
                        'id': parts[1],
                        'description': parts[2],
                        'status': parts[3],
                        'assigned_to': parts[4],
                        'last_updated': parts[5]
                    })
        return areas
    
    def claim_area(self, area_id: str, agent_id: str) -> bool:
        """Claim a work area for an AI agent.
        
        Args:
            area_id: The ID of the area to claim
            agent_id: The ID of the AI agent claiming the area
            
        Returns:
            True if successful, False otherwise
        """
        content = self._read_coordination_file()
        
        # Check if area is available
        available_areas = self.get_available_areas()
        if not any(area['id'] == area_id for area in available_areas):
            return False
            
        # Move area from available to active
        new_content = content.replace(
            f"| {area_id} |",
            f"| {area_id} | IN_PROGRESS | {agent_id} | {datetime.now().strftime('%Y-%m-%d')} |"
        )
        
        self._write_coordination_file(new_content)
        return True
    
    def complete_area(self, area_id: str, agent_id: str) -> bool:
        """Mark a work area as completed.
        
        Args:
            area_id: The ID of the area to complete
            agent_id: The ID of the AI agent completing the area
            
        Returns:
            True if successful, False otherwise
        """
        content = self._read_coordination_file()
        
        # Check if area is active and assigned to the agent
        active_areas = self.get_active_areas()
        if not any(area['id'] == area_id and area['assigned_to'] == agent_id 
                  and area['status'] == 'IN_PROGRESS' for area in active_areas):
            return False
            
        # Update area status to completed
        new_content = content.replace(
            f"| {area_id} |",
            f"| {area_id} | COMPLETED | {agent_id} | {datetime.now().strftime('%Y-%m-%d')} |"
        )
        
        self._write_coordination_file(new_content)
        return True
    
    def add_new_area(self, category: str, description: str, priority: str, 
                     dependencies: str = "") -> Optional[str]:
        """Add a new work area.
        
        Args:
            category: The category of the work area (e.g., FEAT, FIX)
            description: Description of the work area
            priority: Priority level (HIGH, MEDIUM, LOW)
            dependencies: Comma-separated list of dependent area IDs
            
        Returns:
            The new area ID if successful, None otherwise
        """
        content = self._read_coordination_file()
        
        # Find the next available number for the category
        existing_areas = self.get_available_areas() + self.get_active_areas()
        category_areas = [area for area in existing_areas if area['id'].startswith(category)]
        if category_areas:
            last_number = max(int(area['id'].split('-')[1]) for area in category_areas)
            new_number = str(last_number + 1).zfill(3)
        else:
            new_number = "001"
            
        area_id = f"{category}-{new_number}"
        
        # Add new area to available areas
        new_area = f"| {area_id} | {description} | {priority} | {dependencies} |\n"
        available_section = re.search(r"(### Available Work Areas\n.*?)(?=\n##|$)", content, re.DOTALL)
        if available_section:
            new_content = content.replace(
                available_section.group(1),
                available_section.group(1) + new_area
            )
            self._write_coordination_file(new_content)
            return area_id
            
        return None
    
    def get_next_available_area(self, agent_capabilities: List[str], 
                              priority: str = "HIGH") -> Optional[Dict[str, str]]:
        """Get the next available work area based on agent capabilities and priority.
        
        Args:
            agent_capabilities: List of capabilities the agent has
            priority: Preferred priority level
            
        Returns:
            Dictionary containing area information if found, None otherwise
        """
        available_areas = self.get_available_areas()
        active_areas = self.get_active_areas()
        
        # Filter areas by priority and capabilities
        suitable_areas = [
            area for area in available_areas
            if area['priority'] == priority
            and not any(area['id'] == active['id'] for active in active_areas)
        ]
        
        if not suitable_areas:
            return None
            
        # Return the first suitable area
        return suitable_areas[0]
    
    def check_dependencies(self, area_id: str) -> Tuple[bool, List[str]]:
        """Check if all dependencies for an area are completed.
        
        Args:
            area_id: The ID of the area to check
            
        Returns:
            Tuple of (bool, List[str]) indicating if dependencies are met and list of unmet dependencies
        """
        available_areas = self.get_available_areas()
        area = next((a for a in available_areas if a['id'] == area_id), None)
        if not area or not area['dependencies']:
            return True, []
            
        dependencies = [d.strip() for d in area['dependencies'].split(',')]
        active_areas = self.get_active_areas()
        
        unmet_dependencies = []
        for dep in dependencies:
            if not any(a['id'] == dep and a['status'] == 'COMPLETED' 
                      for a in active_areas):
                unmet_dependencies.append(dep)
                
        return len(unmet_dependencies) == 0, unmet_dependencies 
from pydantic import BaseModel, EmailStr, UUID4, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    MEMBER = "member"
    CONTRIBUTOR = "contributor"
    MODERATOR = "moderator"
    ADMIN = "admin"

class User(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    role: UserRole = UserRole.MEMBER
    bio: Optional[str] = None
    skills: List[str] = []
    projects: List[UUID4] = []
    created_at: datetime
    last_active: datetime

class Project(BaseModel):
    id: UUID4
    title: str
    description: str
    owner_id: UUID4
    collaborators: List[UUID4] = []
    tags: List[str] = []
    ai_tools_used: List[str] = []
    github_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Resource(BaseModel):
    id: UUID4
    title: str
    description: str
    type: str  # guide, tutorial, template, etc.
    content: str
    author_id: UUID4
    tags: List[str] = []
    ai_prompts_used: List[str] = []
    created_at: datetime
    updated_at: datetime

class Event(BaseModel):
    id: UUID4
    title: str
    description: str
    event_type: str  # workshop, meetup, hackathon
    start_time: datetime
    end_time: datetime
    organizer_id: UUID4
    participants: List[UUID4] = []
    resources: List[UUID4] = []
    created_at: datetime

class Discussion(BaseModel):
    id: UUID4
    title: str
    content: str
    author_id: UUID4
    project_id: Optional[UUID4] = None
    resource_id: Optional[UUID4] = None
    parent_id: Optional[UUID4] = None
    replies: List[UUID4] = []
    created_at: datetime
    updated_at: datetime

class Achievement(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: UUID4
    title: str
    description: str
    criteria: Dict[str, Any]
    badge_url: str
    created_at: datetime

class UserAchievement(BaseModel):
    user_id: UUID4
    achievement_id: UUID4
    earned_at: datetime
    achievement_metadata: Optional[Dict[str, Any]] = None 
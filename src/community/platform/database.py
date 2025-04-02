from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional

from .models import UserRole

# Create SQLAlchemy base
Base = declarative_base()

# Database models
class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.MEMBER)
    bio = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    projects = relationship("ProjectDB", back_populates="owner")
    resources = relationship("ResourceDB", back_populates="author")
    events = relationship("EventDB", back_populates="organizer")
    discussions = relationship("DiscussionDB", back_populates="author")

class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    github_url = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("UserDB", back_populates="projects")
    discussions = relationship("DiscussionDB", back_populates="project")

class ResourceDB(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("UserDB", back_populates="resources")
    discussions = relationship("DiscussionDB", back_populates="resource")

class EventDB(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    organizer_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    organizer = relationship("UserDB", back_populates="events")

class DiscussionDB(Base):
    __tablename__ = "discussions"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=True)
    parent_id = Column(String, ForeignKey("discussions.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("UserDB", back_populates="discussions")
    project = relationship("ProjectDB", back_populates="discussions")
    resource = relationship("ResourceDB", back_populates="discussions")
    replies = relationship("DiscussionDB", backref="parent", remote_side=[id])

class AchievementDB(Base):
    __tablename__ = "achievements"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    criteria = Column(String, nullable=False)  # JSON string
    badge_url = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class UserAchievementDB(Base):
    __tablename__ = "user_achievements"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    achievement_id = Column(String, ForeignKey("achievements.id"), primary_key=True)
    earned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    metadata = Column(String, nullable=True)  # JSON string

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./community.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine) 
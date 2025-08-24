from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Expert(Base):
    __tablename__ = "experts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    cv_url = Column(String)
    bio = Column(Text)
    roles = Column(ARRAY(Text))
    sectors = Column(ARRAY(Text))
    regions = Column(ARRAY(Text))
    languages = Column(ARRAY(Text))
    years_experience = Column(Integer)
    prior_engagements = Column(JSON)
    embedding = Column(JSON)  # Store as list for now, Qdrant handles vector
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ToR(Base):
    __tablename__ = "tor_drafts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    embedding = Column(JSON)

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    expert_id = Column(UUID(as_uuid=True), ForeignKey("experts.id"))
    tor_id = Column(UUID(as_uuid=True), ForeignKey("tor_drafts.id"))
    rating = Column(Integer)
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow) 
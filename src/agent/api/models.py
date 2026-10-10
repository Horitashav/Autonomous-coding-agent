"""Database Models — SQLAlchemy ORM table definitions for PostgreSQL."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from agent.api.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    """User account for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    chats = relationship("Chat", back_populates="owner", cascade="all, delete-orphan")


class Chat(Base):
    """A conversation thread with the agent."""

    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(36), unique=True, default=generate_uuid, index=True)
    name = Column(String(200), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner = relationship("User", back_populates="chats")
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    approval_requests = relationship(
        "ApprovalRequest",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="ApprovalRequest.id",
    )


class Message(Base):
    """A single message record in a chat thread."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    code = Column(Text, nullable=True)
    optimized_code = Column(Text, nullable=True)
    optimization_metrics = Column(JSONB, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    status = Column(String(20), default="")
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)

    # Native PostgreSQL JSONB column for React Flow structures
    flow_graph = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    chat = relationship("Chat", back_populates="messages")


class ApprovalRequest(Base):
    """Human-in-the-Loop pending action authorization record."""

    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    reason = Column(Text, nullable=False)
    proposed_code = Column(Text, nullable=False)
    checkpoint_state = Column(JSONB, nullable=False)  # Serialized LangGraph state

    chat = relationship("Chat", back_populates="approval_requests")

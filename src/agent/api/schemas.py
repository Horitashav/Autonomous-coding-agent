"""Pydantic Schemas — Request and response validation contracts for the REST API."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ===========================================================================
# AUTH SCHEMAS
# ===========================================================================

class UserCreate(BaseModel):
    """Payload contract for user registration."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Payload contract for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public user identity contract returned across API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    created_at: datetime


class TokenResponse(BaseModel):
    """Access token payload returned on successful authentication."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ===========================================================================
# CHAT & MESSAGE SCHEMAS
# ===========================================================================

class ChatCreate(BaseModel):
    """Payload to initiate a new chat thread."""

    name: str = Field(..., min_length=1, max_length=200)


class ChatRename(BaseModel):
    """Payload to update chat title."""

    name: str = Field(..., min_length=1, max_length=200)


class MessageCreate(BaseModel):
    """Payload sent by user to prompt the coding agent."""

    content: str = Field(..., min_length=1, max_length=15000)
    project_path: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    code: str | None = None
    optimized_code: str | None = None
    optimization_metrics: dict[str, Any] | None = None
    stdout: str | None = None
    stderr: str | None = None
    status: str
    tokens_used: int
    cost_usd: float
    flow_graph: dict[str, Any] | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSummary(BaseModel):
    """Summary of a chat session for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ChatDetail(BaseModel):
    """Complete chat session including full message history."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []


# ===========================================================================
# FLOW GRAPH SCHEMA
# ===========================================================================

class FlowGraphRequest(BaseModel):
    """Standalone payload to extract AST flow trees from Python code."""

    code: str = Field(..., min_length=1)
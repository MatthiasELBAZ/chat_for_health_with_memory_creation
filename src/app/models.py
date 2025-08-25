"""Pydantic models for API requests and responses."""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    thread_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    user_id: str


class InitializeUserRequest(BaseModel):
    user_id: str


class InitializeUserResponse(BaseModel):
    user_id: str
    message: str
    status: str
    health_data: Dict[str, Any]  # Include health data in response 
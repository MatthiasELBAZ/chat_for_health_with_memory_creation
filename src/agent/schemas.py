"""Pydantic schemas for structured output."""

from typing import Literal
from pydantic import BaseModel, Field


class MemoryEvaluationSchema(BaseModel):
    """Schema for memory evaluation output."""
    
    evaluation: Literal["STORE", "SKIP", "EXPLICIT"] = Field(
        default="SKIP",
        description="The result of memory evaluation: STORE, SKIP, or EXPLICIT"
    )
    


__all__ = ["MemoryEvaluationSchema"] 
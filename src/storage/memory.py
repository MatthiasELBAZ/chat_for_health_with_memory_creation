"""In-memory storage implementation for LangGraph agent."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from typing import Tuple


def create_memory_storage() -> Tuple[InMemorySaver, InMemoryStore]:
    """Create in-memory checkpointer and store for development/testing.
    
    Returns:
        Tuple of (checkpointer, store)
    """
    # In-memory checkpointer for conversation persistence
    checkpointer = InMemorySaver()
    
    # In-memory store for cross-thread memory (user data, etc.)
    store = InMemoryStore()
    
    return checkpointer, store 
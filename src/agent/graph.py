"""Graphs that extract memories on a schedule."""

import asyncio
import logging
from datetime import datetime
from typing import cast

from langchain_core.messages import SystemMessage, ToolMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import END, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.base import BaseStore
from langgraph.config import get_store
import os

from agent import tools, utils
from agent.context import Context
from agent.state import State

logger = logging.getLogger(__name__)

# Remove the global llm initialization - we'll create it dynamically in call_model

async def call_model(state: State, runtime: Runtime[Context]) -> dict:
    """Extract the user's state from the conversation and update the memory."""
    user_id = runtime.context.user_id
    model = runtime.context.model
    system_prompt = runtime.context.system_prompt

    # Get the store from the runtime context
    store = get_store()
    
    # Search for relevant memories
    namespace = (user_id, "memories")
    memories = await store.asearch(
        namespace,
        query=str(state.messages[-1].content),
        limit=5
    )
    
    # Format memories for the prompt
    memory_text = ""
    if memories:
        memory_text = "\n\nRelevant memories:\n" + "\n".join(
            f"- {mem.value.get('content', '')}" for mem in memories
        )
    
    # Create system prompt with memories
    sys = system_prompt + memory_text
    
    # Initialize the language model
    # Parse the model and provider from the context
    model_info = utils.split_model_and_provider(model)
    
    if model_info["provider"]:
        # Set environment variables for the specific provider
        if model_info["provider"] == "anthropic":
            # Ensure ANTHROPIC_API_KEY is set
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required for Anthropic models")
            os.environ["ANTHROPIC_API_KEY"] = api_key
        
        llm = init_chat_model(
            model=model_info["model"], 
            model_provider=model_info["provider"]
        )
    else:
        # Fallback for models without explicit provider
        llm = init_chat_model(model)
    
    # Invoke the language model with the prepared prompt and tools
    # "bind_tools" gives the LLM the JSON schema for all tools in the list so it knows how
    # to use them.
    msg = await llm.bind_tools([tools.upsert_memory]).ainvoke(
        [SystemMessage(content=sys), *state.messages],
    )
    return {"messages": [msg]}


async def store_memory(state: State, runtime: Runtime[Context]):
    # Extract tool calls from the last message
    msg = state.messages[-1]
    tool_calls = getattr(msg, "tool_calls", []) or []
    
    if not tool_calls:
        # No tool calls to process
        return {"messages": []}

    # Get the store from the runtime context
    store = get_store()
    
    # Concurrently execute all upsert_memory calls
    saved_memories = await asyncio.gather(
        *(
            tools.upsert_memory(
                **tc["args"],
                user_id=runtime.context.user_id,
                store=store,
            )
            for tc in tool_calls
        )
    )

    # Format the results of memory storage operations
    # This provides confirmation to the model that the actions it took were completed
    results = [
        ToolMessage(
            content=mem,
            tool_call_id=tc["id"],
        )
        for tc, mem in zip(tool_calls, saved_memories)
    ]
    return {"messages": results}


def route_message(state: State):
    """Determine the next step based on the presence of tool calls."""
    msg = state.messages[-1]
    if getattr(msg, "tool_calls", None):
        # If there are tool calls, we need to store memories
        return "store_memory"
    # Otherwise, finish; user can send the next message
    return END


# Create the graph + all nodes
builder = StateGraph(State, context_schema=Context)

# Define the flow of the memory extraction process
builder.add_node("call_model", call_model)
builder.add_node("store_memory", store_memory)

# Clear flow definition
builder.add_edge("__start__", "call_model")
builder.add_conditional_edges(
    "call_model", 
    route_message, 
    {
        "store_memory": "store_memory",
        END: END
    }
)
builder.add_edge("store_memory", END)

# Export both the builder and a basic compiled graph
graph = builder.compile()
graph.name = "MemoryAgent"

# Also export the builder for adding checkpointing
graph_builder = builder


__all__ = ["graph", "graph_builder"]
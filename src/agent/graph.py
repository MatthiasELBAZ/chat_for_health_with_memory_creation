"""Graphs that extract memories on a schedule."""

import asyncio
import logging
from datetime import datetime

from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.runtime import Runtime
from langgraph.config import get_store

from . import tools, utils
from .context import Context
from .state import State
from .schemas import MemoryEvaluationSchema

logger = logging.getLogger(__name__)


async def call_model(state: State, runtime: Runtime[Context]) -> dict:
    """Main chatbot node that handles conversation, memory evaluation, and storage."""
    user_id = runtime.context.user_id
    model = runtime.context.model
    system_prompt = runtime.context.system_prompt

    # Get the store from the runtime context
    store = get_store()
    
    # Search for relevant memories - use the same namespace as storage
    namespace = ("memories", user_id)
    
    # Try both targeted search and general retrieval for better context
    targeted_memories = await store.asearch(
        namespace,
        query=str(state.messages[-1].content),
        limit=3
    )
    
    # Also get recent general memories for this user
    general_memories = await store.asearch(
        namespace,
        query="",  # Empty query to get all memories
        limit=5
    )
    
    # Combine and deduplicate memories
    all_memories = {}
    for mem in targeted_memories + general_memories:
        all_memories[mem.key] = mem
    
    memories = list(all_memories.values())
    
    # Format memories for the prompt
    memory_text = ""
    if memories:
        memory_list = []
        for mem in memories:
            content = mem.value.get('content', '')
            context = mem.value.get('context', '')
            if content:
                if context:
                    memory_list.append(f"- {content} ({context})")
                else:
                    memory_list.append(f"- {content}")
        
        if memory_list:
            memory_text = f"\n\n**IMPORTANT - USER MEMORIES & PREVIOUS CONTEXT:**\nYou have stored the following information about this user. Use this context to provide personalized, continuous responses:\n" + "\n".join(memory_list)
            memory_text += f"\n\n**CRITICAL:** Based on these memories, DO NOT greet the user as if meeting for the first time. Continue the conversation naturally based on previous interactions and their established goals."
    
    # Create system prompt with memories and fill placeholders
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Fill system prompt placeholders
    formatted_system_prompt = system_prompt.format(
        user_info=f"User ID: {user_id}",
        time=current_time
    )
    
    sys = formatted_system_prompt + memory_text
    
    # Initialize the language model
    llm = utils.get_llm(model)
    
    # First, evaluate if we need to store memory
    llm_for_evaluation = utils.get_llm(model)
    structured_llm = llm_for_evaluation.with_structured_output(MemoryEvaluationSchema)
    
    # Get recent messages for evaluation (filter out tool messages)
    recent_messages = state.messages[-3:] if len(state.messages) >= 3 else state.messages
    filtered_for_eval = []
    for msg in recent_messages:
        if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls') and not hasattr(msg, 'tool_call_id'):
            filtered_for_eval.append(msg)
    
    # Evaluate if we should store memory
    evaluation_result = await structured_llm.ainvoke([
        SystemMessage(content=runtime.context.memory_evaluation_prompt),
        *filtered_for_eval
    ])
    
    # If we should store memory, do it before generating response
    if evaluation_result.evaluation in ["STORE", "EXPLICIT"]:
        # Use the LLM with tools to generate memory and response
        llm_with_tools = llm.bind_tools([tools.upsert_memory])
        
        # Use all conversation messages for context
        response_msg = await llm_with_tools.ainvoke([
            SystemMessage(content=sys),
            *state.messages
        ])
        
        # If the model made tool calls, execute them
        if hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
            tool_calls = response_msg.tool_calls
            
            # Execute memory storage
            saved_memories = await asyncio.gather(
                *(
                    tools.upsert_memory(
                        **tc["args"],
                        user_id=user_id,
                        store=store,
                    )
                    for tc in tool_calls
                )
            )
            
            # Create tool messages for the conversation
            tool_messages = [
                ToolMessage(
                    content=mem,
                    tool_call_id=tc["id"],
                )
                for tc, mem in zip(tool_calls, saved_memories)
            ]
            
            # Generate final response without tools
            final_response = await llm.ainvoke([
                SystemMessage(content=sys),
                *state.messages,
                response_msg,
                *tool_messages
            ])
            
            return {"messages": [response_msg, *tool_messages, final_response]}
        else:
            # No tool calls made, return the response as is
            return {"messages": [response_msg]}
    else:
        # No memory storage needed, just generate response
        response_msg = await llm.ainvoke([
            SystemMessage(content=sys),
            *state.messages
        ])
        
        return {"messages": [response_msg]}


# Simplified graph structure following LangGraph best practices
builder = StateGraph(State, context_schema=Context)

# Single node that handles everything
builder.add_node("call_model", call_model)

# Simple flow: START → call_model → END
builder.add_edge("__start__", "call_model")
builder.add_edge("call_model", END)

# Export both the builder and a basic compiled graph
graph = builder.compile()
graph.name = "MemoryAgent"

# Also export the builder for adding checkpointing
graph_builder = builder

__all__ = ["graph", "graph_builder"]
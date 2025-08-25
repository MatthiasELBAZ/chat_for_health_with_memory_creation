"""API routes for the Fitbit Conversational AI application."""

import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from langchain_core.messages import HumanMessage
from langgraph.errors import GraphRecursionError

from ..agent.context import Context
from ..agent.state import State
from .models import ChatRequest, ChatResponse, InitializeUserRequest, InitializeUserResponse

# Create router instance
router = APIRouter()

# Global variables - will be set by app.py
graph_with_checkpointer = None
store = None


def set_globals(graph, store_instance):
    """Set global variables from app.py"""
    global graph_with_checkpointer, store
    graph_with_checkpointer = graph
    store = store_instance


def generate_fake_health_data(user_id: str) -> Dict[str, Any]:
    """Generate realistic fake health data for demonstration."""
    import random
    
    # Generate some variation in the data
    base_steps = random.randint(6000, 12000)
    base_heart_rate = random.randint(58, 72)
    base_sleep = random.uniform(6.5, 8.5)
    
    return {
        "user_id": user_id,
        "daily_stats": {
            "steps": base_steps,
            "calories_burned": base_steps * 0.04,
            "active_minutes": random.randint(20, 60),
            "distance_km": base_steps * 0.0008,
        },
        "heart_rate": {
            "resting": base_heart_rate,
            "current": random.randint(base_heart_rate + 10, base_heart_rate + 40),
            "max_today": random.randint(base_heart_rate + 50, base_heart_rate + 80),
            "variability": random.randint(20, 50),
        },
        "sleep": {
            "duration_hours": base_sleep,
            "deep_sleep_hours": base_sleep * 0.25,
            "rem_sleep_hours": base_sleep * 0.20,
            "light_sleep_hours": base_sleep * 0.55,
            "sleep_score": random.randint(70, 95),
        },
        "goals": {
            "daily_steps": 10000,
            "weekly_workouts": 3,
            "sleep_target": 8.0,
            "resting_heart_rate_target": 65,
        },
        "achievements": [
            "7-day streak of meeting step goal",
            "Improved sleep score by 15% this month",
            "Consistent heart rate variability",
        ]
    }


async def initialize_user_health_data(user_id: str):
    """Initialize user's health data in memory store."""
    health_data = generate_fake_health_data(user_id)
    
    # Store health data as memories with proper namespace
    health_memories = [
        {
            "content": f"User's daily step count: {health_data['daily_stats']['steps']} steps",
            "context": "Daily activity tracking data"
        },
        {
            "content": f"User's resting heart rate: {health_data['heart_rate']['resting']} bpm",
            "context": "Heart rate monitoring data"
        },
        {
            "content": f"User's sleep duration: {health_data['sleep']['duration_hours']:.1f} hours with sleep score {health_data['sleep']['sleep_score']}",
            "context": "Sleep quality and duration data"
        },
        {
            "content": f"User's current goals: {health_data['goals']['daily_steps']} daily steps, {health_data['goals']['weekly_workouts']} weekly workouts",
            "context": "Fitness and health goals"
        },
        {
            "content": f"Recent achievements: {', '.join(health_data['achievements'])}",
            "context": "User's fitness accomplishments"
        }
    ]
    
    # Store each memory with proper namespace (consistent with tools.py)
    for memory in health_memories:
        await store.aput(
            ("memories", user_id),  # Use same namespace as tools.py
            key=str(uuid.uuid4()),
            value=memory
        )
    
    return health_data


@router.get("/")
async def root():
    """Root endpoint with welcome message and API information."""
    return {
        "message": "Welcome to Fitbit Conversational AI! 🏃‍♂️💬",
        "description": "AI-powered health assistant for Fitbit users",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "initialize_user": "/initialize-user",
            "chat": "/chat"
        },
        "status": "healthy"
    }


@router.get("/favicon.ico")
async def favicon():
    """Return a simple favicon response to prevent 404 errors."""
    # Return an empty response with appropriate headers
    return Response(status_code=204)  # No Content


@router.post("/initialize-user", response_model=InitializeUserResponse)
async def initialize_user(request: InitializeUserRequest):
    """Initialize a new user with fake health data."""
    try:
        # Initialize health data in memory
        health_data = await initialize_user_health_data(request.user_id)
        
        return InitializeUserResponse(
            user_id=request.user_id,
            message=f"User {request.user_id} initialized with health data.",
            status="success",
            health_data=health_data  # Include health data in response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize user: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the Fitbit AI assistant."""
    try:
        # Generate thread_id if not provided
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Create context with both user_id and thread_id
        context = Context(
            user_id=request.user_id,
            thread_id=thread_id
        )
        
        # Create initial state
        state = State(
            messages=[HumanMessage(content=request.message)]
        )
        
        # Run the simplified graph with proper LangGraph invocation
        result = await graph_with_checkpointer.ainvoke(
            state, 
            context=context,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 10  # Sufficient for simplified graph
            }
        )
        
        # Extract response from the last message
        last_message = result["messages"][-1]
        response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        return ChatResponse(
            response=response_content,
            thread_id=thread_id,
            user_id=request.user_id
        )
        
    except GraphRecursionError:
        raise HTTPException(
            status_code=400, 
            detail="Conversation too complex. Please try a simpler request."
        )
    except Exception as e:
        # More detailed error logging for debugging
        print(f"Chat error for user {request.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Fitbit Conversational AI"}


@router.get("/health/agent")
async def agent_health_check():
    """Check agent graph health."""
    try:
        # Test graph compilation and basic functionality
        test_state = State(messages=[HumanMessage(content="health check test")])
        test_context = Context(user_id="health_check", thread_id="health_check")
        
        # Quick test invocation to verify the simplified graph works
        result = await graph_with_checkpointer.ainvoke(
            test_state, 
            context=test_context,
            config={
                "configurable": {"thread_id": "health_check"},
                "recursion_limit": 5  # Sufficient for simplified graph
            }
        )
        
        # Verify we got a proper response
        if not result or "messages" not in result or not result["messages"]:
            raise Exception("Graph did not return proper message structure")
        
        return {
            "status": "healthy",
            "agent": "Fitbit AI Health Assistant",
            "graph_compiled": True,
            "graph_structure": "simplified",
            "memory_store": "operational",
            "checkpointer": "operational",
            "test_messages_count": len(result["messages"])
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "agent": "Fitbit AI Health Assistant",
            "graph_structure": "simplified"
        }


@router.get("/users/{user_id}/memories")
async def get_user_memories(user_id: str):
    """Get all memories for a specific user."""
    try:
        # Use the same store instance that the LangGraph agent uses
        # Access the store from the compiled graph to ensure consistency
        agent_store = graph_with_checkpointer.store if graph_with_checkpointer else store
        
        # Search for memories in the specific namespace
        memories = await agent_store.asearch(
            ("memories", user_id), # Use same namespace as tools.py
            query="",
            limit=100
        )
        
        return {
            "user_id": user_id,
            "memories": [
                {
                    "key": mem.key,
                    "value": mem.value,
                    "score": mem.score
                } for mem in memories
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memories: {str(e)}") 
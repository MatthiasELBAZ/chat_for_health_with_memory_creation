"""FastAPI application for Fitbit Conversational AI."""

import uuid
import os
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from agent.graph import graph_builder
from agent.context import Context
from agent.state import State
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.errors import GraphRecursionError

# Load environment variables from .env file
load_dotenv()

# Set up environment variables for API keys
def setup_environment():
    """Set up environment variables for API keys."""
    # Check if ANTHROPIC_API_KEY is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY environment variable is not set")
        print("   Please set it before running the application:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print("   Or create a .env file with: ANTHROPIC_API_KEY=your-key-here")

# Call setup on import
setup_environment()

# Global variables for checkpointer and store
checkpointer = None
store = None
graph_with_checkpointer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    global checkpointer, store, graph_with_checkpointer
    
    # Startup logic
    print("🚀 Starting up Fitbit Conversational AI...")
    
    # Create checkpointer and store
    checkpointer = InMemorySaver()
    store = InMemoryStore()
    
    # Compile the graph with both checkpointer and store
    graph_with_checkpointer = graph_builder.compile(
        checkpointer=checkpointer,
        store=store
    )
    
    # Test graph compilation
    try:
        test_state = State(messages=[HumanMessage(content="startup test")])
        test_context = Context(user_id="startup", thread_id="startup")
        
        # Quick test to ensure graph is working with proper configurable keys
        await graph_with_checkpointer.ainvoke(
            test_state, 
            context=test_context,
            config={
                "configurable": {
                    "thread_id": "startup",
                    "checkpoint_id": "startup_test"
                },
                "recursion_limit": 5  # Increased from 1 to allow proper execution
            }
        )
        
        print("✅ LangGraph agent initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize LangGraph agent: {e}")
        raise
    
    yield
    
    # Shutdown logic
    print("🛑 Shutting down Fitbit Conversational AI...")
    # Clean up resources if needed
    if store:
        print("🧹 Cleaning up memory store...")

app = FastAPI(
    title="Fitbit Conversational AI",
    description="AI-powered health assistant for Fitbit users",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
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
            "chat": "/chat",
            "chat_stream": "/chat/stream"
        },
        "status": "healthy"
    }


@app.get("/favicon.ico")
async def favicon():
    """Return a simple favicon response to prevent 404 errors."""
    from fastapi.responses import Response
    # Return an empty response with appropriate headers
    return Response(status_code=204)  # No Content


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


@app.post("/initialize-user", response_model=InitializeUserResponse)
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


@app.post("/chat", response_model=ChatResponse)
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
        
        # Run the graph directly with proper LangGraph invocation
        result = await graph_with_checkpointer.ainvoke(
            state, 
            context=context,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 10  # Prevent infinite loops
            }
        )
        
        # Extract response
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
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint for real-time responses."""
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
        
        # Stream the graph execution
        async for chunk in graph_with_checkpointer.astream(
            state,
            context=context,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 10
            },
            stream_mode="values"
        ):
            yield {
                "data": chunk,
                "thread_id": thread_id,
                "user_id": request.user_id
            }
            
    except GraphRecursionError:
        yield {"error": "Conversation too complex. Please try a simpler request."}
    except Exception as e:
        yield {"error": f"Chat error: {str(e)}"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Fitbit Conversational AI"}


@app.get("/health/agent")
async def agent_health_check():
    """Check agent graph health."""
    try:
        # Test graph compilation
        test_state = State(messages=[HumanMessage(content="test")])
        test_context = Context(user_id="test", thread_id="test")
        
        # Quick test invocation with minimal recursion
        result = await graph_with_checkpointer.ainvoke(
            test_state, 
            context=test_context,
            config={"recursion_limit": 1}
        )
        
        return {
            "status": "healthy",
            "agent": "Fitbit AI Health Assistant",
            "graph_compiled": True,
            "memory_store": "operational",
            "checkpointer": "operational"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "agent": "Fitbit AI Health Assistant"
        }


@app.get("/users/{user_id}/memories")
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


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user and all their memories."""
    try:
        # Use the same store instance that the LangGraph agent uses
        agent_store = graph_with_checkpointer.store if graph_with_checkpointer else store
        
        # Get all memories for the user
        memories = await agent_store.asearch(
            ("memories", user_id), # Use same namespace as tools.py
            query="",
            limit=1000
        )
        
        # Delete each memory
        for memory in memories:
            await agent_store.adelete(("memories", user_id), memory.key)
        
        return {"message": f"User {user_id} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

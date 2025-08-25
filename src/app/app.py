"""FastAPI application setup and configuration."""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from ..agent.graph import graph_builder
from ..agent.context import Context
from ..agent.state import State
from ..storage.memory import create_memory_storage
from .routers import router, set_globals

# Load environment variables from .env file
load_dotenv()

# Global variables for checkpointer and store
checkpointer = None
store = None
graph_with_checkpointer = None


def setup_environment():
    """Set up environment variables for API keys."""
    # Check if ANTHROPIC_API_KEY is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY environment variable is not set")
        print("   Please set it before running the application:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print("   Or create a .env file with: ANTHROPIC_API_KEY=your-key-here")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    global checkpointer, store, graph_with_checkpointer
    
    # Startup logic
    print("🚀 Starting up Fitbit Conversational AI...")
    
    # Create checkpointer and store
    checkpointer, store = create_memory_storage()
    
    # Compile the graph with both checkpointer and store
    graph_with_checkpointer = graph_builder.compile(
        checkpointer=checkpointer,
        store=store
    )
    
    # Set globals in routers
    set_globals(graph_with_checkpointer, store)
    
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
                "recursion_limit": 10  # Sufficient for simplified graph
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


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Call setup on import
    setup_environment()
    
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
    
    # Include routers
    app.include_router(router)
    
    return app


# Create the app instance
app = create_app() 
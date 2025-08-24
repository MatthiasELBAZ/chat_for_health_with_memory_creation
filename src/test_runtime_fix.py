"""Test script to verify the runtime usage fix."""

import asyncio
import logging
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent.graph import graph_builder
from agent.context import Context
from agent.state import State
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_graph_invocation():
    """Test the graph invocation without Runtime usage."""
    print("Testing graph invocation...")
    
    try:
        # Create checkpointer and store
        checkpointer = InMemorySaver()
        store = InMemoryStore()
        print("✅ Checkpointer and store created")
        
        # Compile graph with both checkpointer and store
        print("Compiling graph with checkpointer and store...")
        graph_with_checkpointer = graph_builder.compile(
            checkpointer=checkpointer,
            store=store
        )
        print("✅ Graph compiled successfully")
        
        # Create test context with the real model
        context = Context(
            user_id="test_user",
            thread_id="test_thread",
            model="anthropic/claude-3-5-sonnet-20240620",
            system_prompt="You are a helpful assistant."
        )
        print("✅ Context created")
        
        # Use proper LangChain message objects
        state = State(
            messages=[HumanMessage(content="Hello, how are you?")]
        )
        print("✅ State created")
        
        print("Invoking graph...")
        # Test direct graph invocation
        result = await graph_with_checkpointer.ainvoke(
            state,
            context=context,
            config={
                "configurable": {"thread_id": "test_thread"},
                "recursion_limit": 5
            }
        )
        
        print("✅ Graph invocation successful!")
        print(f"Result: {result}")
        
        # Test streaming
        print("\nTesting streaming...")
        stream_count = 0
        async for chunk in graph_with_checkpointer.astream(
            state,
            context=context,
            config={
                "configurable": {"thread_id": "test_thread"},
                "recursion_limit": 5
            },
            stream_mode="values"
        ):
            stream_count += 1
            print(f"Stream chunk {stream_count}: {chunk}")
        
        print(f"✅ Streaming successful! Received {stream_count} chunks")
        
    except Exception as e:
        print(f"❌ Error during graph invocation: {e}")
        logger.exception("Detailed error information:")
        raise

if __name__ == "__main__":
    asyncio.run(test_graph_invocation()) 
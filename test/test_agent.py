"""Test script to demonstrate the agent functionality."""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_agent():
    """Test the Fitbit agent with a conversation."""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. Initialize a new user
        print("1. Initializing user...")
        try:
            init_response = await client.post(
                f"{base_url}/initialize-user",
                json={"user_id": "user123"}
            )
            init_response.raise_for_status()
            init_data = init_response.json()
            print(f"✅ Initialization successful: {init_data['message']}")
            
            # Check if health data is included
            if 'health_data' in init_data:
                print(f"📊 Health data initialized:")
                print(f"   - Steps: {init_data['health_data']['daily_stats']['steps']}")
                print(f"   - Heart Rate: {init_data['health_data']['heart_rate']['resting']} bpm")
                print(f"   - Sleep: {init_data['health_data']['sleep']['duration_hours']:.1f} hours")
            else:
                print("⚠️  No health data in response")
                
        except httpx.HTTPStatusError as e:
            print(f"❌ Initialization failed with status {e.response.status_code}: {e.response.text}")
            return
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return
        
        # 2. Start a conversation
        print("\n2. Starting conversation...")
        try:
            chat_response = await client.post(
                f"{base_url}/chat",
                json={
                    "user_id": "user123",
                    "thread_id": "thread456",
                    "message": "How am I doing with my health goals today?"
                }
            )
            chat_response.raise_for_status()
            chat_data = chat_response.json()
            print(f"✅ Chat response: {chat_data['response']}")
            
        except httpx.HTTPStatusError as e:
            print(f"❌ Chat failed with status {e.response.status_code}: {e.response.text}")
            return
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return
        
        # 3. Check stored memories
        print("\n3. Checking stored memories...")
        try:
            memories_response = await client.get(
                f"{base_url}/users/user123/memories"
            )
            memories_response.raise_for_status()
            memories_data = memories_response.json()
            print(f"✅ Found {len(memories_data['memories'])} memories")
            for i, memory in enumerate(memories_data['memories'][:3]):  # Show first 3
                print(f"   Memory {i+1}: {memory['value']['content']}")
                
        except httpx.HTTPStatusError as e:
            print(f"❌ Memories retrieval failed with status {e.response.status_code}: {e.response.text}")
        except Exception as e:
            print(f"❌ Memories error: {e}")
        
        # 4. Continue conversation
        print("\n4. Continuing conversation...")
        try:
            follow_up_response = await client.post(
                f"{base_url}/chat",
                json={
                    "user_id": "user123",
                    "thread_id": "thread456",
                    "message": "What can I do to improve my sleep quality?"
                }
            )
            follow_up_response.raise_for_status()
            follow_up_data = follow_up_response.json()
            print(f"✅ Follow-up response: {follow_up_data['response']}")
            
        except httpx.HTTPStatusError as e:
            print(f"❌ Follow-up failed with status {e.response.status_code}: {e.response.text}")
        except Exception as e:
            print(f"❌ Follow-up error: {e}")
        
        # 5. Test health check endpoints
        print("\n5. Testing health endpoints...")
        try:
            health_response = await client.get(f"{base_url}/health")
            health_response.raise_for_status()
            print(f"✅ Health check: {health_response.json()}")
            
            agent_health_response = await client.get(f"{base_url}/health/agent")
            agent_health_response.raise_for_status()
            print(f"✅ Agent health: {agent_health_response.json()}")
            
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # 6. Test root endpoint
        print("\n6. Testing root endpoint...")
        try:
            root_response = await client.get(f"{base_url}/")
            root_response.raise_for_status()
            root_data = root_response.json()
            print(f"✅ Root endpoint: {root_data['message']}")
            print(f"   Available endpoints: {len(root_data['endpoints'])}")
            
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")


if __name__ == "__main__":
    # Check if server is running
    print("🧪 Testing Fitbit Conversational AI Agent")
    print("Make sure the server is running on http://localhost:8000")
    print("Run: cd src && python main.py")
    print("-" * 50)
    
    asyncio.run(test_agent())

"""PostgreSQL storage implementation for LangGraph agent with async support."""

import os
from typing import Tuple, Optional, AsyncContextManager
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.store.base import BaseStore
from langgraph.checkpoint.base import BaseCheckpointSaver


@asynccontextmanager
async def create_postgres_storage(
    setup_db: bool = True
) -> AsyncContextManager[Tuple[BaseCheckpointSaver, BaseStore]]:
    """Create async PostgreSQL checkpointer and store with proper lifecycle management.
    
    This function creates both an AsyncPostgresSaver for conversation persistence
    and an AsyncPostgresStore for long-term memory storage.
    
    Reads connection string from DATABASE_URL environment variable.
    
    Args:
        setup_db: Whether to create tables if they don't exist
        
    Yields:
        Tuple of (async_checkpointer, async_store)
        
    Raises:
        ValueError: If DATABASE_URL is not set
        ImportError: If required PostgreSQL dependencies are not installed
    """
    # Get connection string from environment
    connection_string = os.getenv("DATABASE_URL")
    if not connection_string:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please set it in your .env file: DATABASE_URL=postgresql://user:password@host:port/database"
        )
    
    try:
        print(f"🐘 Connecting to PostgreSQL: {connection_string.split('@')[1] if '@' in connection_string else 'localhost'}")
        
        # Create async checkpointer and store using context managers
        async with AsyncPostgresSaver.from_conn_string(connection_string) as checkpointer, \
                   AsyncPostgresStore.from_conn_string(connection_string) as store:
            
            if setup_db:
                print("🔧 Setting up database tables...")
                try:
                    # Setup tables for both checkpointer and store
                    await checkpointer.setup()
                    await store.setup()
                    print("✅ PostgreSQL tables created successfully")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to setup database tables: {e}")
                    print("   Tables may need to be created manually or database may not be accessible")
            
            print("🚀 AsyncPostgresSaver and AsyncPostgresStore initialized successfully")
            yield checkpointer, store
            
    except ImportError as e:
        print(f"❌ PostgreSQL dependencies not available: {e}")
        print("📦 Install with: pip install langgraph-checkpoint-postgres langgraph-store-postgres psycopg[binary]")
        raise
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        raise


async def test_postgres_connection() -> bool:
    """Test PostgreSQL connection and return True if successful.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        async with create_postgres_storage(setup_db=False) as (checkpointer, store):
            # Try a simple operation to verify the connection
            await store.alist_namespaces(limit=1)
            print("✅ PostgreSQL connection test successful")
            return True
    except Exception as e:
        print(f"❌ PostgreSQL connection test failed: {e}")
        return False


def is_postgres_configured() -> bool:
    """Check if PostgreSQL environment variables are configured.
    
    Returns:
        True if DATABASE_URL is set, False otherwise
    """
    return bool(os.getenv("DATABASE_URL"))

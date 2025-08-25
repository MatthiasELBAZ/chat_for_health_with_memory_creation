# """PostgreSQL storage implementation for LangGraph agent (production ready)."""

# import os
# from typing import Tuple, Optional
# from langgraph.checkpoint.postgres import PostgresSaver
# from langgraph.store.postgres import PostgresStore


# def create_postgres_storage(
#     connection_string: Optional[str] = None,
#     setup_db: bool = True
# ) -> Tuple[PostgresSaver, PostgresStore]:
#     """Create PostgreSQL checkpointer and store for production.
    
#     Args:
#         connection_string: PostgreSQL connection string. If None, reads from env.
#         setup_db: Whether to create tables if they don't exist
        
#     Returns:
#         Tuple of (checkpointer, store)
#     """
#     # Get connection string from environment if not provided
#     if connection_string is None:
#         connection_string = os.getenv("POSTGRES_CONNECTION_STRING")
#         if not connection_string:
#             raise ValueError(
#                 "PostgreSQL connection string not provided. "
#                 "Set POSTGRES_CONNECTION_STRING environment variable or pass connection_string parameter."
#             )
    
#     # PostgreSQL checkpointer for conversation persistence
#     checkpointer = PostgresSaver.from_conn_string(connection_string)
    
#     # PostgreSQL store for cross-thread memory
#     store = PostgresStore.from_conn_string(connection_string)
    
#     # Setup database tables if requested
#     if setup_db:
#         checkpointer.setup()
#         store.setup()
    
#     return checkpointer, store


# # Example connection strings for reference:
# EXAMPLE_CONNECTION_STRINGS = {
#     "local": "postgresql://user:password@localhost:5432/langgraph_db",
#     "docker": "postgresql://postgres:password@localhost:5432/postgres", 
#     "production": "postgresql://user:password@prod-host:5432/langgraph_prod"
# } 
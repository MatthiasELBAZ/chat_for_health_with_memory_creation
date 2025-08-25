# Fitbit Conversational AI POC

A conversational AI framework prototype designed to enhance Fitbit user engagement through personalized, data-driven health insights and natural language interactions.

## 🎯 Project Overview

This project demonstrates how Fitbit can integrate a conversational AI assistant into their app to:
- **Drive daily user engagement** through personalized interactions
- **Offer data-driven health insights** based on user's Fitbit data
- **Build trust and ongoing dialogue** between Fitbit and its users

## ✨ Key Features

- **Natural Language Understanding**: Handle health-related queries like "How did I sleep last night?" or "Am I more active this week?"
- **Personalized Insights**: Generate meaningful health insights from step count, heart rate, sleep data, and goals
- **Proactive Suggestions**: Offer helpful follow-ups and nudges based on user patterns
- **Intelligent Memory System**: Automatically evaluates and stores important health information for personalized experiences
- **Contextual Conversations**: Uses stored memories to maintain conversation continuity and build rapport
- **Modular Architecture**: Built with LangGraph for scalable, production-ready conversational AI
- **PostgreSQL Persistence**: Reliable conversation and user data storage with pgvector support

## 🧠 Intelligent Memory System

The AI assistant features an advanced memory system that enhances user experience through personalization:

### Memory Intelligence
- **Automatic Evaluation**: For each user message, the AI determines if information is worth storing using specialized evaluation prompts
- **Smart Storage Decisions**: Automatically stores health goals, personal preferences, medical conditions, lifestyle information, and communication preferences
- **Context Retrieval**: Before responding to any message, the agent searches and uses stored memories to provide personalized, contextual responses
- **Conversation Continuity**: Maintains rapport across sessions by remembering previous discussions and user preferences

### What Gets Stored
The AI intelligently stores:
- **Health & Fitness**: Personal goals, fitness levels, medical conditions, sleep patterns, workout preferences
- **Personal Context**: Names, age, occupation, lifestyle details, communication style preferences
- **Coaching Context**: What motivates the user, preferred coaching approaches, feedback on recommendations
- **Explicit Requests**: Any information the user specifically asks to be remembered

### Memory Usage
- **Contextual Responses**: Every response is informed by relevant stored memories
- **Personalized Advice**: Recommendations based on known preferences and past interactions
- **Goal Tracking**: Continuous reference to user's stated health objectives
- **Relationship Building**: Avoids repetitive introductions and builds on established rapport

## 🏗️ Architecture

The system is built using modern AI orchestration frameworks with a modular architecture:

- **LangGraph**: Core conversational flow management and state handling
- **LangChain**: LLM integration and tool management  
- **FastAPI**: RESTful API for easy integration and testing
- **PostgreSQL + pgvector**: Persistent storage for conversations and user preferences
- **Anthropic Claude**: Advanced language model for natural conversations
- **Docker Compose**: Containerized database setup for development

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Anthropic API key
- Docker & Docker Compose (for PostgreSQL storage)
- uv (recommended) or pip for dependency management

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd helloheart_HA
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file with your API key
   echo "ANTHROPIC_API_KEY=your-key-here" > .env
   ```

4. **Start PostgreSQL database**
   ```bash
   # Start PostgreSQL with pgvector extension
   docker compose up -d
   
   # Check container status
   docker compose ps
   
   # View logs if needed
   docker compose logs -f
   ```

5. **Start the application**
   ```bash
   # Run the FastAPI application
   python -m src.app.run
   
   # Alternative: Run with uvicorn directly
   uvicorn src.app.app:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🐘 PostgreSQL Storage Configuration

The application uses PostgreSQL with pgvector extension for persistent storage of conversations, user preferences, and checkpoints.

### Docker Compose Setup

The `compose.yaml` file provides a complete PostgreSQL setup:

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required: Anthropic API Key
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# PostgreSQL Configuration (defaults shown)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fitbit_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Alternative: Use connection string
# POSTGRES_CONNECTION_STRING=postgresql://postgres:password@localhost:5432/fitbit_ai
```

### Database Management

```bash
# Start database
docker compose up -d

# Stop database  
docker compose down

# Reset database (removes all data)
docker compose down -v

# View database logs
docker compose logs -f db

# Connect to database
docker compose exec db psql -U postgres -d fitbit_ai
```

## 📱 API Usage

### Core Endpoints

- **`POST /chat`** - Send a message to the AI assistant
- **`POST /initialize-user`** - Initialize a new user with mock health data (optional)
- **`GET /users/{user_id}/memories`** - View all stored memories for a user
- **`GET /health`** - Check system health
- **`GET /health/agent`** - Check AI agent health
- **`GET /docs`** - Interactive API documentation (available at http://localhost:8000/docs)

### Getting Started with a User

You have two options to start using the AI assistant:

#### Option 1: Start Fresh
Simply start chatting with the AI without initialization. The agent will:
- Ask for relevant health information as needed
- Automatically store important details as you share them
- Build your profile organically through conversation

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "john_doe",
       "message": "Hi, I want to improve my fitness"
     }'
```

#### Option 2: Initialize with Mock Data
Use the initialize endpoint to pre-populate the user with realistic health data:

```bash
curl -X POST "http://localhost:8000/initialize-user" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "john_doe"}'
```

This creates mock data including:
- Daily step counts, heart rate, sleep data
- Fitness goals and achievements
- Recent activity patterns

### Viewing Stored Memories

Check what the AI has learned about a user:

```bash
curl -X GET "http://localhost:8000/users/john_doe/memories"
```

## 🔧 Development

### Key Components

#### Agent Layer (`src/agent/`)
- **State Management**: Handles conversation flow and user context
- **LangGraph Integration**: Orchestrates conversational AI workflow  
- **Memory System**: Stores and retrieves relevant user information
- **Tool Integration**: Provides health data analysis capabilities
- **Prompt Engineering**: Optimized prompts for health-focused conversations

#### Application Layer (`src/app/`)
- **FastAPI Setup**: Web framework with async support
- **API Routes**: RESTful endpoints for chat and user management
- **Lifecycle Management**: Database connection and startup/shutdown
- **Request/Response Models**: Type-safe API contracts

#### Storage Layer (`src/storage/`)
- **PostgreSQL Integration**: Production-ready persistence with pgvector
- **LangGraph Checkpoints**: Conversation state persistence
- **Memory Fallback**: In-memory storage for development
- **Connection Management**: Async database connection handling

## 📊 Performance Requirements

- **Response Time**: < 2 seconds for most queries
- **Concurrency**: Support for 100+ concurrent users
- **Uptime**: Target ≥99% availability
- **Error Handling**: Graceful fallbacks for all error scenarios
- **Database**: PostgreSQL with connection pooling and health checks

## 🚀 Production Readiness

### Immediate Action Items (Priority Order)
1. Fix DATABASE_URL configuration bug (CRITICAL)
2. Create production .env template (CRITICAL)
3. Add security middleware (HIGH)
4. Implement comprehensive logging (HIGH)
5. Create production Dockerfile (HIGH)
6. Add rate limiting (MEDIUM)
7. Implement monitoring (MEDIUM)
8. Write integration tests (MEDIUM)

### Estimated Timeline
- **Phase 1-2**: 1-2 weeks (Critical fixes & infrastructure)
- **Phase 3-4**: 2-3 weeks (Monitoring & performance)
- **Phase 5-6**: 2-3 weeks (Testing & deployment)
- **Phase 7**: 1-2 weeks (Production considerations)

**Total**: 6-10 weeks for full production readiness

The codebase is well-architected but needs significant production hardening, especially around configuration management, security, monitoring, and testing before it can handle real users safely and reliably.

## 🤝 Contributing

This is a proof-of-concept project demonstrating conversational AI capabilities for health applications. The modular architecture makes it easy to extend and improve.

## 👨‍💻 Author

**Matthias Elbaz** - Senior AI Engineer  
Email: matthias.elbaz91@gmail.com

---

*Built with ❤️ using LangGraph, LangChain, PostgreSQL, and modern AI orchestration techniques.*

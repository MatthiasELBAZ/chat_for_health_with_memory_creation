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
- **Memory System**: Remember user preferences and conversation history for personalized experiences
- **Modular Architecture**: Built with LangGraph for scalable, production-ready conversational AI

## 🏗️ Architecture

The system is built using modern AI orchestration frameworks:

- **LangGraph**: Core conversational flow management and state handling
- **LangChain**: LLM integration and tool management
- **FastAPI**: RESTful API for easy integration and testing
- **Memory Store**: Persistent conversation and user preference storage
- **Anthropic Claude**: Advanced language model for natural conversations

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd helloheart_HA
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   # or using uv (recommended)
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   # or create a .env file
   echo "ANTHROPIC_API_KEY=your-anthropic-api-key" > .env
   ```

4. **Run the application**
   ```bash
   # Start the FastAPI server
   python src/main.py
   
   # Or run tests
   pytest
   
   # Or use the Jupyter notebook for interactive testing
   jupyter notebook test.ipynb
   ```

## 📱 Usage Examples

### API Endpoints

- `POST /chat` - Send a message to the AI assistant
- `GET /health` - Check system health
- `GET /docs` - Interactive API documentation

### Sample Conversation

```
User: "How did I sleep last night?"
Assistant: "Based on your sleep data, you slept for 7.5 hours with good sleep quality. 
Your deep sleep was 2.1 hours, which is within the recommended range. 
Would you like some tips to improve your sleep quality further?"

User: "Am I meeting my weekly step goal?"
Assistant: "You're currently at 45,000 steps this week, which is 90% of your 50,000 step goal. 
You're very close! A 30-minute walk this evening would help you reach your target. 
Would you like me to set a reminder for you?"
```

## 🧪 Testing

The project includes comprehensive testing:

```bash
# Run all tests
pytest

# Run specific test files
pytest src/test_agent.py
pytest src/test_runtime_fix.py

# Run with coverage
pytest --cov=src
```

## 🔧 Development

### Project Structure

```
src/
├── agent/           # Core AI agent components
│   ├── context.py   # Context management
│   ├── graph.py     # LangGraph flow definition
│   ├── prompts.py   # System prompts and templates
│   ├── state.py     # Conversation state management
│   ├── tools.py     # AI tools and functions
│   └── utils.py     # Utility functions
├── main.py          # FastAPI application entry point
└── test_*.py        # Test files
```

### Key Components

- **State Management**: Handles conversation flow and user context
- **Memory System**: Stores and retrieves relevant user information
- **Tool Integration**: Provides health data analysis capabilities
- **Prompt Engineering**: Optimized prompts for health-focused conversations

## 📊 Performance Requirements

- **Response Time**: < 2 seconds for most queries
- **Concurrency**: Support for 100+ concurrent users
- **Uptime**: Target ≥99% availability
- **Error Handling**: Graceful fallbacks for all error scenarios

## 🔮 Future Enhancements

- **Real-time Data Integration**: Live Fitbit API integration
- **Multi-modal Inputs**: Voice and text support
- **Clinical Validation**: Healthcare professional oversight
- **Advanced Personalization**: Machine learning-based user modeling
- **Proactive Notifications**: Smart health reminders and alerts

## 🤝 Contributing

This is a proof-of-concept project demonstrating conversational AI capabilities for health applications. The modular architecture makes it easy to extend and improve.

## 📄 License

This project is created as part of a technical assessment for Fitbit's conversational AI initiative.

## 👨‍💻 Author

**Matthias Elbaz** - Senior AI Engineer  
Email: matthias.elbaz91@gmail.com

---

*Built with ❤️ using LangGraph, LangChain, and modern AI orchestration techniques.*

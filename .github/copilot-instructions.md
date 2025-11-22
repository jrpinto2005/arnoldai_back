<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Arnold Fitness Coach - AI-Powered FastAPI Application

This is a sophisticated FastAPI-based fitness application featuring an AI-powered conversational chatbot that provides real-time coaching, personalized workout planning, and motivational guidance.

## Project Architecture

### Core Technologies
- **FastAPI**: Modern Python web framework with automatic API documentation
- **SQLAlchemy**: SQL toolkit and ORM for database management
- **OpenAI GPT**: Large language model integration for AI coaching
- **ElevenLabs**: Text-to-speech service for voice responses
- **Pydantic**: Data validation using Python type hints
- **JWT Authentication**: Secure token-based authentication

### Project Structure
```
app/
├── main.py                   # FastAPI application entry point
├── core/config.py           # Application configuration and settings
├── db/
│   ├── session.py           # Database session management
│   └── models.py            # SQLAlchemy database models
├── schemas/                 # Pydantic models for request/response validation
├── services/                # Business logic and AI integration services
└── api/
    ├── deps.py              # FastAPI dependencies (auth, database)
    └── routes/              # API endpoint definitions
```

## Development Guidelines

### Code Style & Patterns
- Follow **FastAPI best practices** with proper dependency injection
- Use **type hints** extensively for better IDE support and validation
- Implement **async/await** patterns for I/O operations
- Follow **RESTful API** conventions for endpoint design
- Use **Pydantic models** for all request/response validation
- Implement proper **error handling** with appropriate HTTP status codes

### AI Integration Guidelines
- **LLM Service** (`services/llm.py`): Handles OpenAI GPT interactions
- **Session Coach** (`services/session_coach.py`): Provides real-time workout guidance
- **Workout Planner** (`services/planner.py`): Generates personalized workout plans
- **ElevenLabs Client** (`services/elevenlabs_client.py`): Text-to-speech functionality

### Database Guidelines
- Use **SQLAlchemy models** with proper relationships
- Follow **database normalization** principles
- Implement **soft deletes** where appropriate
- Use **database migrations** for schema changes (Alembic)
- Include **created_at/updated_at** timestamps on relevant models

### API Design Principles
- **Consistent response formats** across all endpoints
- **Proper HTTP status codes** (200, 201, 400, 401, 404, 500, etc.)
- **Comprehensive error messages** with helpful details
- **Request validation** using Pydantic models
- **Authentication required** for protected endpoints
- **Rate limiting** considerations for AI service calls

### AI Coaching Context
The application provides contextual AI coaching by:
1. **User Profile Analysis**: Age, fitness goals, activity level, preferences
2. **Workout History**: Previous sessions, performance data, progress tracking
3. **Real-time Adaptation**: Exercise modifications based on user feedback
4. **Conversation Memory**: Maintaining context across chat sessions
5. **Progressive Training**: Workouts that evolve with user fitness level

### Key Features to Remember
- **Real-time coaching** during workout sessions with live guidance
- **Voice responses** using ElevenLabs for motivational audio
- **Adaptive difficulty** that adjusts based on user performance
- **Contextual conversations** that remember user history
- **Equipment adaptation** for different workout environments
- **Progress analytics** with comprehensive fitness tracking

### Testing Guidelines
- Write **unit tests** for business logic in services
- Include **integration tests** for API endpoints
- Test **AI service integrations** with proper mocking
- Validate **authentication and authorization** flows
- Test **database operations** and model relationships

### Security Considerations
- **JWT token validation** for protected endpoints
- **Password hashing** using bcrypt
- **Input sanitization** and validation
- **Rate limiting** for AI service calls
- **Environment variable** protection for API keys
- **CORS configuration** for frontend integration

### Performance Optimization
- **Async database operations** for better concurrency
- **Connection pooling** for database efficiency
- **Caching strategies** for frequently accessed data
- **Optimized AI prompts** to reduce token usage
- **Background tasks** for non-blocking operations

When working on this codebase, prioritize user experience, data security, maintainable code architecture, and efficient AI integration patterns.

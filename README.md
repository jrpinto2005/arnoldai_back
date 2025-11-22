# Arnold - AI Fitness Coach 🏋️‍♂️

A sophisticated FastAPI-based fitness application featuring an AI-powered conversational chatbot that provides real-time coaching, personalized workout plans, and motivational guidance.

## 🚀 Features

### 🤖 AI Coaching System
- **Real-time coaching** during workout sessions with form tips and motivation
- **Personalized workout generation** based on user profile and goals
- **Voice responses** using ElevenLabs text-to-speech (optional)
- **Adaptive difficulty** that adjusts based on user feedback
- **Contextual conversations** that remember user history and preferences

### 💪 Workout Management
- **Custom workout sessions** with detailed exercise tracking
- **Progressive training plans** that evolve over time
- **Equipment adaptation** - workouts adapt to available equipment
- **Performance tracking** with sets, reps, weight, and duration
- **Session coaching** with live guidance and encouragement

### 💬 Conversational Chat
- **Multi-session chat** with persistent conversation history
- **Context-aware responses** based on user profile and workout history
- **Different chat types**: general fitness, workout planning, nutrition, motivation
- **Voice interaction** support (with ElevenLabs integration)

### 📊 Smart Analytics
- **Progress tracking** across all workouts and sessions
- **Performance analytics** with completion rates and improvements
- **Personalized insights** based on user activity patterns

## 🏗️ Architecture

### Backend Structure
```
app/
├── main.py                    # FastAPI application entry point
├── core/
│   └── config.py             # Application configuration
├── db/
│   ├── session.py            # Database session management
│   └── models.py             # SQLAlchemy models
├── schemas/
│   ├── user.py               # User-related Pydantic models
│   ├── workout.py            # Workout-related schemas
│   └── chat.py               # Chat and coaching schemas
├── services/
│   ├── llm.py                # OpenAI LLM integration
│   ├── elevenlabs_client.py  # Text-to-speech service
│   ├── planner.py            # Workout planning algorithms
│   └── session_coach.py      # Real-time coaching logic
└── api/
    ├── deps.py               # FastAPI dependencies (auth, db)
    └── routes/
        ├── chat.py           # Chat and conversation endpoints
        └── sessions.py       # Workout session management
```

### Key Technologies
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **OpenAI GPT**: Large language model for AI coaching
- **ElevenLabs**: Text-to-speech for voice responses
- **Pydantic**: Data validation using Python type hints
- **JWT**: Secure authentication tokens
- **SQLite**: Lightweight database (easily upgradable to PostgreSQL)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or poetry

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd arnold
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python -m app.main
   # or
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - **API**: http://localhost:8000
   - **Interactive docs**: http://localhost:8000/docs
   - **Alternative docs**: http://localhost:8000/redoc

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection string | `sqlite:///./arnold.db` | No |
| `SECRET_KEY` | JWT signing secret | - | **Yes** |
| `OPENAI_API_KEY` | OpenAI API key for AI features | - | No* |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for voice | - | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` | No |

*\*Required for full AI functionality*

### AI Services Setup

1. **OpenAI Integration**
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Generate an API key
   - Add to `.env`: `OPENAI_API_KEY=your-key-here`

2. **ElevenLabs Voice (Optional)**
   - Sign up at [ElevenLabs](https://elevenlabs.io/)
   - Generate an API key
   - Add to `.env`: `ELEVENLABS_API_KEY=your-key-here`

## 🔌 API Endpoints

### Chat & Coaching
- `POST /api/chat/message` - Send message to AI coach
- `GET /api/chat/sessions` - Get chat sessions
- `POST /api/chat/sessions` - Create new chat session
- `GET /api/chat/sessions/{id}` - Get specific session
- `DELETE /api/chat/sessions/{id}` - Delete session

### Workout Sessions
- `POST /api/sessions/create` - Create workout session
- `POST /api/sessions/start` - Start coaching session
- `GET /api/sessions/` - Get user's workout sessions
- `GET /api/sessions/{id}` - Get specific session
- `PUT /api/sessions/{id}` - Update session
- `POST /api/sessions/generate` - Generate AI workout plan

### Real-time Coaching
- `POST /api/sessions/{id}/exercises/{exercise_id}/complete` - Complete exercise
- `POST /api/sessions/{id}/exercises/{exercise_id}/guidance` - Get exercise guidance
- `POST /api/sessions/{id}/exercises/{exercise_id}/difficulty` - Report difficulty
- `GET /api/sessions/{id}/coach/status` - Get coaching status

## 🎯 Usage Examples

### 1. Start a Conversation
```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Hi Arnold! I want to start working out",
    "session_type": "general",
    "voice_enabled": false
  }'
```

### 2. Generate a Workout Plan
```bash
curl -X POST "http://localhost:8000/api/sessions/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "duration": 30,
    "equipment": ["bodyweight"],
    "difficulty": "intermediate",
    "goal": "strength"
  }'
```

### 3. Start a Coaching Session
```bash
curl -X POST "http://localhost:8000/api/sessions/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "workout_id=1"
```

## 🧠 AI Coaching Features

### Contextual Awareness
- **User Profile Integration**: Age, fitness goals, activity level
- **Workout History**: Previous sessions and performance
- **Conversation Memory**: Maintains context across chat sessions
- **Progress Tracking**: Adapts advice based on user improvement

### Real-time Guidance
- **Form Corrections**: AI provides technique tips during exercises
- **Motivation**: Personalized encouragement and support
- **Adaptive Difficulty**: Suggests modifications based on user feedback
- **Rest Period Coaching**: Guidance during rest intervals

### Workout Intelligence
- **Progressive Planning**: Workouts that evolve with user fitness level
- **Equipment Adaptation**: Automatic exercise substitutions
- **Goal-specific Programs**: Tailored for weight loss, muscle gain, endurance
- **Recovery Optimization**: Smart rest day recommendations

## 🔐 Authentication

The API uses JWT tokens for authentication:

1. **Register/Login** (implement auth endpoints as needed)
2. **Include token** in Authorization header: `Bearer YOUR_TOKEN`
3. **Token expires** after configured time (default 30 minutes)

## 🗄️ Database Models

### Core Entities
- **User**: Profile, goals, preferences
- **WorkoutSession**: Individual workout instances
- **Exercise**: Specific exercises within workouts
- **ChatSession**: Conversation containers
- **ChatMessage**: Individual messages

### Relationships
- Users have many WorkoutSessions and ChatSessions
- WorkoutSessions contain multiple Exercises
- ChatSessions contain multiple ChatMessages
- Full history preservation for analytics and personalization

## 🚀 Deployment

### Production Checklist
- [ ] Change `SECRET_KEY` to secure random string
- [ ] Set `DEBUG=False`
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure rate limiting
- [ ] Set up logging and monitoring
- [ ] Add API key security for AI services

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-specific Configs
```bash
# Development
DATABASE_URL=sqlite:///./arnold.db
DEBUG=True

# Production
DATABASE_URL=postgresql://user:pass@localhost/arnold_prod
DEBUG=False
```

## 🧪 Development

### Running Tests
```bash
pytest
```

### Code Structure Guidelines
- **Separation of Concerns**: Services handle business logic
- **Dependency Injection**: Use FastAPI's dependency system
- **Type Hints**: Full type annotation for better development experience
- **Error Handling**: Comprehensive exception handling
- **Documentation**: Docstrings for all public functions

### Adding New Features
1. **Models**: Add database models in `db/models.py`
2. **Schemas**: Create Pydantic models in appropriate `schemas/` file
3. **Services**: Implement business logic in `services/`
4. **Routes**: Add API endpoints in `api/routes/`
5. **Tests**: Write tests for new functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check `/docs` endpoint for API documentation
- **Issues**: Report bugs and feature requests on GitHub
- **AI Features**: Ensure proper API keys are configured for full functionality

---

**Arnold** - Your AI-powered fitness companion! 💪

*"I'll be back... to help you reach your fitness goals!"* - Arnold AI

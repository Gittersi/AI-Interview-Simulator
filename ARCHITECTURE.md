# AI Interview Simulator - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│        React + TypeScript + TailwindCSS                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Dashboard   │  │  Interview   │  │   Reports    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│        │                  │                  │          │
└────────┼──────────────────┼──────────────────┼──────────┘
         │                  │                  │
    WebSocket/HTTP API (REST)
         │                  │                  │
┌────────▼──────────────────▼──────────────────▼──────────┐
│              Application Layer                          │
│           FastAPI + Python 3.9+                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Auth Routes  │  │ Interview    │  │ Evaluation   │  │
│  │              │  │ Routes       │  │ Routes       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│        │                  │                  │          │
│  ┌──────────────────────────────────────────────────┐  │
│  │       Business Logic & Services                  │  │
│  │ - LLM Integration                               │  │
│  │ - Answer Evaluation                             │  │
│  │ - Question Generation                           │  │
│  │ - Resume Parsing                                │  │
│  │ - Speech-to-Text Processing                     │  │
│  └──────────────────────────────────────────────────┘  │
└────────┬──────────────────┬──────────────────┬──────────┘
         │                  │                  │
         │                  │                  │
    MongoDB          External APIs        Cache Layer
    Database         (LLM, STT)           (Optional)
```

## Technology Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool (Fast bundling)
- **TailwindCSS** - Utility-first CSS
- **Zustand** - Lightweight state management
- **Axios** - HTTP client
- **React Router** - Navigation
- **Recharts** - Data visualization
- **Lucide Icons** - Icon library

### Backend
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **PyJWT** - JWT authentication
- **bcrypt** - Password hashing

### ML/NLP
- **scikit-learn** - Machine learning
- **spaCy** - NLP tasks
- **NLTK** - Natural language toolkit
- **numpy** - Numerical computing

### Database
- **MongoDB** - NoSQL database
- Async driver (Motor) for non-blocking operations

### External APIs
- **OpenAI/Anthropic** - LLM for question generation
- **AssemblyAI** - Speech-to-text transcription

## Data Models

### User
```typescript
{
  _id: ObjectId,
  email: string,
  name: string,
  password_hash: string,
  skills: string[],
  resume: string,
  created_at: datetime
}
```

### Interview
```typescript
{
  _id: string,
  userId: string,
  startTime: datetime,
  endTime?: datetime,
  status: 'in_progress' | 'completed' | 'abandoned',
  category: string,
  difficulty: 'easy' | 'medium' | 'hard',
  questions: Question[],
  answers: Answer[]
}
```

### Question
```typescript
{
  id: string,
  text: string,
  category: string,
  difficulty: string,
  timeLimit: number,
  keywords?: string[],
  expected_answer?: string
}
```

### Evaluation
```typescript
{
  answerId: string,
  correctness: number (0-100),
  confidence: number (0-100),
  communication: number (0-100),
  feedback: string,
  timestamp: datetime
}
```

## API Flow

### Interview Flow
1. User starts interview → POST `/api/interviews`
2. Backend generates questions via LLM API
3. Frontend displays questions with timer
4. User speaks/types answer → WebSocket/POST `/api/interviews/{id}/submit`
5. Backend evaluates answer in real-time
6. Frontend shows next question or completion
7. User completes all questions → POST `/api/interviews/{id}/complete`
8. Backend generates performance report
9. User views report → GET `/api/evaluation/report/{id}`

## Evaluation Pipeline

```
User Answer
    ↓
Speech-to-Text (AssemblyAI)
    ↓
Text Normalization
    ↓
┌─────────────────────────────────┐
│  Multi-Criteria Evaluation       │
├─────────────────────────────────┤
│ • Semantic Similarity            │
│ • Keyword Matching               │
│ • Sentiment Analysis             │
│ • Communication Quality          │
│ • Technical Depth                │
└─────────────────────────────────┘
    ↓
LLM Feedback Generation
    ↓
Score Aggregation
    ↓
Performance Report
```

## Security Measures

- **Authentication**: JWT tokens with expiration
- **Password**: bcrypt hashing
- **CORS**: Restricted origin policy
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: MongoDB parameterized queries
- **Rate Limiting**: Implement per deployment needs
- **HTTPS**: Required in production

## Performance Considerations

### Caching
- LLM responses cached (same category/difficulty)
- User skills cached in session
- Question metadata in memory

### Database Indexing
```javascript
// Recommended indexes
db.users.createIndex({ email: 1 })
db.interviews.createIndex({ userId: 1, status: 1 })
db.interviews.createIndex({ startTime: -1 })
db.reports.createIndex({ interviewId: 1 })
```

### Async Operations
- All database operations are async (Motor)
- LLM API calls are non-blocking
- File uploads processed asynchronously

## Deployment Considerations

### Docker
- Multi-stage builds for smaller images
- Environment variables for configuration
- Docker Compose for local development

### Scaling
- Stateless backend (allows horizontal scaling)
- Session data in database (not in-memory)
- API Gateway/Load Balancer ready

## Monitoring & Logging

### Backend Logging
- Error tracking
- Request logging
- Performance metrics

### Frontend Error Boundary
- Graceful error handling
- User-friendly error messages
- Error reporting to backend

## Future Enhancements

1. **Real-time Collaboration**: WebSocket for interviewer/interviewee
2. **ML Model Training**: Custom models on user data
3. **Video Recording**: Store interview videos
4. **Advanced Analytics**: More detailed performance insights
5. **Mobile App**: React Native version
6. **Gamification**: Leaderboards and achievements
7. **Integration**: Connect with LinkedIn, GitHub
8. **Advanced NLP**: Transformers-based evaluation

## Development Workflow

```
Feature Request
    ↓
Create Branch (feature/name)
    ↓
Develop & Test
    ↓
Code Review
    ↓
Merge to Main
    ↓
Automated Tests
    ↓
Deploy to Staging
    ↓
Production Deployment
```

## Key Files & Responsibilities

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app setup |
| `backend/app/services/llm_service.py` | LLM integration |
| `backend/app/services/evaluation_service.py` | Answer evaluation |
| `frontend/src/App.tsx` | React routing |
| `frontend/src/pages/Dashboard.tsx` | Main interface |
| `frontend/src/components/InterviewPanel.tsx` | Interview UI |
| `ml/models/answer_evaluator.py` | ML evaluation |
| `docker-compose.yml` | Container orchestration |

---

For more details, see [SETUP.md](./SETUP.md) and [README.md](./README.md)

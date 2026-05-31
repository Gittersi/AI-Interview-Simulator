# AI Interview Simulator 🎤

An intelligent AI-powered technical interview platform that conducts mock interviews with real-time evaluation, voice-based interaction, and comprehensive performance analysis.

## 🌟 Features

### Core Functionality
- **Mock Technical Interviews** - Dynamic questions across multiple domains (DSA, Web Dev, System Design, etc.)
- **Voice-Based Interaction** - Speak your answers naturally; AI transcribes and evaluates
- **Real-time Evaluation** - Instant feedback on correctness, communication, and confidence
- **Performance Reports** - Detailed analysis with visualization of strengths/weaknesses
- **Progress Tracking** - Monitor improvement across multiple interviews
- **Resume-Based Questions** - Tailored questions based on your resume
- **Coding Interview Mode** - Real-time code execution with evaluation

### AI/ML Capabilities
- **NLP Answer Evaluation** - Semantic similarity analysis
- **Sentiment Analysis** - Confidence and communication assessment
- **Confidence Scoring** - Analyze response certainty
- **Resume Parsing** - Extract skills and generate relevant questions
- **Interview Analytics** - ML-based performance scoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│              (Vite + JavaScript + React)                 │
└────────────────────┬────────────────────────────────────┘
                     │ WebSocket/HTTP
┌────────────────────▼────────────────────────────────────┐
│                 FastAPI Backend                          │
│        (Auth, Interview Logic, API Routes)              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    MongoDB      LLM APIs    Speech-to-Text
  (User Data,   (Evaluation)  (Transcription)
   Results)
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- MongoDB 4.4+
- API Keys:
  - OpenAI API (or Anthropic/HuggingFace)
  - AssemblyAI (or Google Speech-to-Text)

### Installation

1. **Clone and Setup**
```bash
git clone <repo>
cd majorproject
```

2. **Frontend Setup**

Note: The frontend has been converted from TypeScript to JavaScript. All source files are `.js`/`.jsx` and the Vite config is `vite.config.js`.

```bash
cd frontend
npm install
npm run dev
```

3. **Backend Setup**
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
```

4. **Environment Configuration**

Create `frontend/.env.local`:
```env
VITE_API_URL=http://localhost:8000/api
VITE_SPEECH_API_KEY=your_assemblyai_key
```

Create `backend/.env`:
```env
DATABASE_URL=mongodb://localhost:27017/ai_interview
OPENAI_API_KEY=your_openai_key
ASSEMBLYAI_API_KEY=your_assemblyai_key
JWT_SECRET=your_jwt_secret
ALLOWED_ORIGINS=http://localhost:5173
```

5. **Start Services**

Backend:
```bash
cd backend
python main.py
```

Frontend:
```bash
cd frontend
npm run dev
```

Access at `http://localhost:5173`

## 📋 Project Structure

```
majorproject/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InterviewPanel.jsx
│   │   │   ├── CodingEditor.jsx
│   │   │   ├── PerformanceReport.jsx
│   │   │   └── VoiceRecorder.jsx
│   │   ├── pages/
│   │   ├── services/
│   │   │   ├── apiClient.js
│   │   │   └── speechService.js
│   │   └── App.jsx
│   ├── vite.config.js
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── interviews.py
│   │   │   ├── questions.py
│   │   │   ├── evaluation.py
│   │   │   └── users.py
│   │   ├── models/
│   │   │   ├── interview.py
│   │   │   ├── question.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── evaluation_service.py
│   │   │   ├── speech_service.py
│   │   │   └── resume_parser.py
│   │   ├── db/
│   │   │   └── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
│
├── ml/
│   ├── models/
│   │   ├── answer_evaluator.py
│   │   ├── sentiment_analyzer.py
│   │   └── confidence_scorer.py
│   ├── utils/
│   │   └── nlp_utils.py
│   └── requirements.txt
│
└── docker-compose.yml
```

## 🔑 Key APIs

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token

### Interviews
- `GET /api/interviews` - Get user's interviews
- `POST /api/interviews` - Start new interview
- `GET /api/interviews/{id}` - Get interview details
- `POST /api/interviews/{id}/submit` - Submit answer

### Questions
- `GET /api/questions/next` - Get next question
- `POST /api/questions/generate` - Generate custom questions
- `POST /api/questions/from-resume` - Generate from resume

### Evaluation
- `POST /api/evaluation/answer` - Evaluate answer
- `POST /api/evaluation/code` - Evaluate code
- `GET /api/evaluation/report/{interview_id}` - Get performance report

### Users
- `GET /api/users/profile` - Get user profile
- `POST /api/users/resume` - Upload resume
- `GET /api/users/progress` - Get progress metrics

## 🛠️ Technologies

### Frontend
- React 18+
- JavaScript
- Vite
- TailwindCSS / Material-UI
- Socket.io (WebSocket)
- Axios

### Backend
- FastAPI
- SQLAlchemy / PyMongo
- Pydantic
- JWT Authentication
- OpenAI API / Anthropic API
- AssemblyAI / Google Speech-to-Text
- scikit-learn, spaCy, NLTK

### Database
- MongoDB (Users, interviews, results, resumes)
- Redis (Session/caching - optional)

### Deployment
- Docker & Docker Compose
- Optional: AWS/GCP/Azure

## 📊 ML/NLP Pipeline

1. **Speech-to-Text** → AssemblyAI API
2. **Answer Evaluation** → Semantic similarity + keyword matching
3. **Sentiment Analysis** → spaCy + transformers
4. **Confidence Scoring** → Linguistic patterns + keyword analysis
5. **Resume Parsing** → spaCy NER + keyword extraction
6. **Performance Metrics** → Aggregation & trend analysis

## 🔐 Security
- JWT authentication
- Password hashing (bcrypt)
- CORS configuration
- Environment variable management
- Rate limiting
- Input validation & sanitization

## 📈 Future Enhancements
- Video recording capability
- Live peer interviews
- Mobile app
- Advanced ML models for evaluation
- Integration with LeetCode/HackerRank
- Team/corporate dashboard
- Interview scheduling

## 🐛 Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

### Linting & Formatting
```bash
# Frontend
npm run lint
npm run format

# Backend
flake8 app/
black app/
```

## 📝 License
MIT License

## 🤝 Contributing
Contributions welcome! Please see CONTRIBUTING.md

## 📧 Support
For issues and questions, please open a GitHub issue.

---

**Made with ❤️ for interview preparation**

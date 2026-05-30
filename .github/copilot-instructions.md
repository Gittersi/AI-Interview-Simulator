# AI Interview Simulator - Project Instructions

## Project Overview
Full-stack AI Interview Simulator application for conducting mock technical interviews with real-time AI evaluation, voice-based questioning, and performance tracking.

## Tech Stack
- **Frontend**: React with TypeScript, Vite
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **LLM Integration**: OpenAI API / Anthropic / HuggingFace
- **Speech-to-Text**: Web Speech API / AssemblyAI
- **ML/NLP**: scikit-learn, spaCy, NLTK

## Project Structure
```
majorproject/
├── frontend/           # React application
├── backend/            # FastAPI server
├── ml/                 # NLP/ML models and utilities
├── docs/               # Documentation
└── docker-compose.yml  # Container orchestration
```

## Key Features
1. **Mock Technical Interviews** - Dynamic question generation
2. **Voice-Based Questioning** - Speech-to-text interview interaction
3. **AI Evaluation** - Confidence, correctness, communication analysis
4. **Performance Reports** - Detailed feedback and metrics
5. **Progress Tracking** - Improvement metrics over time
6. **Resume-Based Questions** - Tailored questions from resume
7. **Real-time Coding Evaluator** - Code execution and feedback

## Setup Instructions

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- MongoDB 4.4+ or MongoDB Atlas
- API Keys: OpenAI/Anthropic, AssemblyAI/Google Speech-to-Text

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Environment Variables
Create `.env` files in both frontend and backend:
- `REACT_APP_API_URL` - Backend API URL
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` - LLM
- `ASSEMBLYAI_API_KEY` - Speech-to-text
- `MONGODB_URI` - Database connection
- `JWT_SECRET` - Authentication secret

## Development Workflow
1. Frontend development on port 5173
2. Backend API on port 8000
3. MongoDB local or cloud instance
4. Real-time WebSocket for live feedback

## Documentation
See [README.md](../../README.md) for detailed setup and usage.

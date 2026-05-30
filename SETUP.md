# Development Setup Guide

## Project Setup

This guide covers the complete setup process for the AI Interview Simulator project.

### Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Python** 3.9+ ([Download](https://www.python.org/))
- **MongoDB** 4.4+ (local or [MongoDB Atlas](https://www.mongodb.com/cloud/atlas))
- **Git** (optional)

### API Keys Required

1. **LLM API** (choose one):
   - OpenAI API Key: https://platform.openai.com/api-keys
   - Anthropic API Key: https://console.anthropic.com/
   - HuggingFace API Key: https://huggingface.co/settings/tokens

2. **Speech-to-Text**:
   - AssemblyAI API Key: https://www.assemblyai.com/

## Installation Steps

### 1. Clone/Download the Project

```bash
cd majorproject
```

### 2. Backend Setup

```bash
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Verify installation
npm list react react-dom
```

### 4. Environment Configuration

#### Backend Configuration

Create `backend/.env`:

```env
# Database
DATABASE_URL=mongodb://localhost:27017/ai_interview

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# LLM Configuration (choose one)
OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here

# Speech-to-Text
ASSEMBLYAI_API_KEY=your_assemblyai_key_here

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True
```

#### Frontend Configuration

Create `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:8000/api
VITE_SPEECH_API_KEY=your_assemblyai_key_here
```

### 5. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Windows
mongod

# macOS (with Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

**Option B: MongoDB Atlas (Cloud)**
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string
4. Update `DATABASE_URL` in `.env`

## Running the Application

### Development Mode

#### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m app.main
```

Backend will run on `http://localhost:8000`

#### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

### Production Build

#### Frontend
```bash
cd frontend
npm run build
npm run preview
```

#### Backend
```bash
cd backend
python -m app.main
```

## Docker Setup

### Prerequisites
- Docker and Docker Compose installed

### Run with Docker

```bash
# From project root
docker-compose up -d
```

This will start:
- MongoDB on port 27017
- Backend API on port 8000
- Frontend on port 5173

### Stop containers
```bash
docker-compose down
```

## Project Structure

```
majorproject/
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API and service clients
│   │   ├── store/             # State management (Zustand)
│   │   ├── types/             # TypeScript type definitions
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── models/            # Data models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── db/                # Database connection
│   │   ├── config.py          # Configuration
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
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
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh token

### Interviews
- `GET /api/interviews` - Get user's interviews
- `POST /api/interviews` - Start new interview
- `GET /api/interviews/{id}` - Get interview details
- `POST /api/interviews/{id}/submit` - Submit answer
- `POST /api/interviews/{id}/complete` - Complete interview

### Evaluation
- `POST /api/evaluation/answer` - Evaluate answer
- `POST /api/evaluation/code` - Evaluate code
- `GET /api/evaluation/report/{id}` - Get performance report

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `POST /api/users/resume` - Upload resume
- `GET /api/users/progress` - Get progress metrics

## Development Commands

### Frontend

```bash
cd frontend

# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Linting
npm run lint

# Code formatting
npm run format

# Run tests
npm run test
```

### Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate

# Run server
python -m app.main

# Run tests
pytest

# Linting
flake8 app/

# Code formatting
black app/
```

## Troubleshooting

### Port Already in Use

**Frontend (5173)**:
```bash
# Kill process on port 5173
# Windows: netstat -ano | findstr :5173
# macOS/Linux: lsof -i :5173
```

**Backend (8000)**:
```bash
# Kill process on port 8000
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000
```

### MongoDB Connection Issues

1. Check MongoDB is running: `mongo --version`
2. Verify connection string in `.env`
3. If using MongoDB Atlas, whitelist your IP in cluster settings

### API Connection Issues

1. Verify backend is running on http://localhost:8000/health
2. Check `VITE_API_URL` in frontend `.env.local`
3. Ensure CORS is properly configured

### Python/Node Issues

1. Ensure virtual environment is activated (backend)
2. Try deleting `node_modules` and reinstalling: `npm install`
3. Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`

## Performance Optimization

### Frontend
- Code splitting: Routes are automatically split with React Router
- Lazy loading: Use `React.lazy()` for components
- Image optimization: Use formats like WebP when possible

### Backend
- Database indexing: Create indexes on frequently queried fields
- Caching: Implement Redis for session caching
- Rate limiting: Add rate limit middleware

## Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **JWT Secret**: Change `JWT_SECRET` in production
3. **CORS**: Restrict `ALLOWED_ORIGINS` to your domain in production
4. **Password**: Ensure strong password hashing (bcrypt)
5. **HTTPS**: Use HTTPS in production
6. **API Keys**: Use environment variables for sensitive keys

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

## Getting Help

For issues or questions:
1. Check the logs (browser console and server logs)
2. Review API response errors
3. Consult framework documentation
4. Create GitHub issue with error details

## Next Steps

1. Set up API keys for LLM and Speech-to-Text
2. Configure MongoDB connection
3. Run development servers
4. Test authentication flow
5. Create sample interview questions
6. Test interview functionality
7. Deploy to production when ready

# Quick Start Guide - 5 Minutes Setup

## TL;DR - Get Running Fast

### Prerequisites
- Node.js 18+
- Python 3.9+
- MongoDB (local or Atlas)

### Step 1: Install Dependencies

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Frontend (in new terminal)
cd frontend
npm install
```

### Step 2: Configure Environment

**backend/.env**:
```env
DATABASE_URL=mongodb://localhost:27017/ai_interview
JWT_SECRET=dev-secret-key-change-in-production
OPENAI_API_KEY=your_key_here
ASSEMBLYAI_API_KEY=your_key_here
DEBUG=True
```

**frontend/.env.local**:
```env
VITE_API_URL=http://localhost:8000/api
```

### Step 3: Start Services

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m app.main
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Step 4: Access Application

Open browser: **http://localhost:5173**

- **Test Account** (after registration):
  - Email: test@example.com
  - Password: test123

## What's Included

### Frontend Features
✅ User authentication (login/register)
✅ Dashboard with interview history
✅ Interview interface with voice recording
✅ Real-time evaluation feedback
✅ Performance reports with visualizations
✅ Responsive design with TailwindCSS

### Backend Features
✅ FastAPI REST API
✅ JWT authentication
✅ MongoDB integration
✅ LLM API integration (OpenAI/Anthropic)
✅ Speech-to-text (AssemblyAI)
✅ Answer evaluation engine
✅ Performance report generation

### ML/NLP Features
✅ Semantic answer evaluation
✅ Sentiment analysis
✅ Confidence scoring
✅ Resume parsing
✅ Question generation

## API Testing

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Health check
curl http://localhost:8000/health
```

### Using Postman

1. Import API collection (coming soon)
2. Set `baseUrl` to `http://localhost:8000/api`
3. Test endpoints with provided examples

## File Structure

```
majorproject/
├── frontend/          # React app
├── backend/           # FastAPI server
├── ml/                # ML models
├── docker-compose.yml # For Docker users
├── README.md          # Main documentation
├── SETUP.md           # Detailed setup
├── ARCHITECTURE.md    # System design
└── CONTRIBUTING.md    # Contributing guide
```

## Common Issues

### MongoDB Connection Error
```bash
# Start MongoDB locally
mongod

# Or use MongoDB Atlas - update DATABASE_URL in .env
```

### Port Already in Use
```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Module Not Found
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### API Connection Error
1. Check backend is running: http://localhost:8000/health
2. Verify `VITE_API_URL` in frontend `.env.local`
3. Restart frontend: Stop and run `npm run dev` again

## Next Steps

1. ✅ Run application locally
2. 📝 Create test account
3. 🎤 Start mock interview
4. 📊 View performance report
5. 🚀 Deploy to production

## Environment Variables Reference

### Backend
| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `mongodb://localhost:27017/ai_interview` | MongoDB connection |
| `JWT_SECRET` | None | Token signing key |
| `OPENAI_API_KEY` | None | OpenAI API key |
| `ASSEMBLYAI_API_KEY` | None | Speech-to-text API |
| `DEBUG` | `True` | Debug mode |
| `SERVER_PORT` | `8000` | Server port |

### Frontend
| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_URL` | `http://localhost:8000/api` | Backend URL |
| `VITE_SPEECH_API_KEY` | None | Speech API key |

## Docker Quick Start

```bash
# Start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

Services will be available at:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- MongoDB: localhost:27017

## Development Tips

### Hot Reload
- Frontend: Automatically reloads on file changes
- Backend: Use `--reload` flag (already configured)

### Database Inspection
```bash
# Connect to MongoDB
mongosh
use ai_interview
db.users.find()
db.interviews.find()
```

### Debug Backend
```python
# In any route
import logging
logging.info("Debug message")
```

## Useful Commands

```bash
# Frontend
npm run lint      # Check code style
npm run format    # Format code
npm run build     # Production build

# Backend
flake8 app/       # Lint
black app/        # Format
pytest            # Run tests
```

## Getting Help

1. Check logs in terminal
2. Review error messages
3. Check [SETUP.md](./SETUP.md) for detailed setup
4. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for design details
5. Review [README.md](./README.md) for features

## Success Indicators

✅ Backend running: http://localhost:8000/health returns `{"status":"healthy"}`
✅ Frontend running: http://localhost:5173 loads login page
✅ Database connected: No connection errors in logs
✅ Can register and login successfully
✅ Can start interview
✅ Can submit answer and see evaluation

## Production Checklist

Before deploying:
- [ ] Change `JWT_SECRET` to strong random string
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_ORIGINS` with production domain
- [ ] Use production LLM API keys
- [ ] Set up production MongoDB
- [ ] Configure HTTPS
- [ ] Set up CI/CD pipeline
- [ ] Configure monitoring/logging
- [ ] Set up backup strategy

---

**Questions?** See full [SETUP.md](./SETUP.md) or [ARCHITECTURE.md](./ARCHITECTURE.md)

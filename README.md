# PDF Summarizer with GPT-4

A full-stack application that allows users to upload PDF documents and receive AI-generated summaries via email.

## Tech Stack

- **Backend**: FastAPI + Celery + Redis
- **Database**: PostgreSQL + SQLAlchemy
- **PDF Processing**: PyMuPDF
- **AI**: LangChain + GPT-4
- **Email**: SendGrid
- **Auth**: JWT (fastapi-users)
- **Frontend**: React + Vite + Tailwind CSS

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- OpenAI API key
- SendGrid API key (optional, for email delivery)

### 1. Clone and Setup

```bash
cd pdf_summarizer

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env and add your API keys
```

### 2. Start Services with Docker

```bash
# Start PostgreSQL, Redis, Backend, and Celery Worker
docker-compose up -d
```

### 3. Start Frontend (Development)

```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## Development Setup (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Start FastAPI server
uvicorn app.main:app --reload
```

### Celery Worker

```bash
# In a separate terminal, with venv activated
celery -A app.tasks.worker:celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL async connection string | Yes |
| `DATABASE_URL_SYNC` | PostgreSQL sync connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SECRET_KEY` | JWT secret key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `SENDGRID_API_KEY` | SendGrid API key | No |
| `FROM_EMAIL` | Sender email address | No |
| `FRONTEND_URL` | Frontend URL for CORS | Yes |

### Frontend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API URL | Yes |

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/jwt/login` - Login and get JWT token
- `GET /users/me` - Get current user

### PDF Operations
- `POST /pdf/upload` - Upload PDF for summarization
- `GET /pdf/documents` - List user's documents
- `GET /pdf/documents/{id}` - Get document details
- `DELETE /pdf/documents/{id}` - Delete document

### Summaries
- `GET /summaries` - List user's summaries
- `GET /summaries/{id}` - Get summary details
- `POST /summaries/{id}/resend-email` - Resend summary email

## Project Structure

```
pdf_summarizer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings/env vars
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # JWT auth setup
│   │   ├── routers/             # API routes
│   │   ├── services/            # Business logic
│   │   └── tasks/               # Celery tasks
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API client & stores
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## Deployment

### Railway (Backend)

1. Create a new project on Railway
2. Add PostgreSQL and Redis services
3. Connect your GitHub repository
4. Set environment variables
5. Deploy backend and Celery worker as separate services

### Vercel (Frontend)

1. Import your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Add `VITE_API_URL` environment variable
4. Deploy

## License

MIT

# Kashar AI - AI-Powered Personal Study Companion

An AI-powered personal study companion that enables users to upload study material, interact with a real-time voice/text tutor, generate quizzes, track progress, and create flashcards.

## Features

- **Document Upload & Parsing**: Upload PDFs and extract text for AI processing
- **Live AI Tutor**: Real-time voice and text interactions with AI tutor
- **Quiz Generation**: Automatically generated quizzes with adaptive difficulty
- **Flashcards**: AI-generated flashcards from study material
- **Progress Tracking**: Analytics and performance tracking dashboard

## Tech Stack

### Frontend
- React
- Agora Web SDK (RTC/RTM)
- Axios
- Modern UI components

### Backend
- FastAPI (main API)
- Flask (document parsing service)
- Python

### AI & Data
- Mistral AI API
- ChromaDB (vector embeddings)
- Supabase (user data, metadata)

### Real-time Communication
- Agora SDK (voice/text)
- Speech-to-Text & Text-to-Speech

## Project Structure

```
kashar-ai/
├── frontend/          # React application
├── backend/           # FastAPI main backend
├── parsing-service/   # Flask PDF parsing service
├── docs/             # Documentation
└── scripts/          # Deployment and utility scripts
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- Supabase account
- Mistral AI API key
- Agora.io account

### Installation

1. Clone the repository
2. Set up environment variables (see .env.example files)
3. Install dependencies:
   ```bash
   # Frontend
   cd frontend && npm install
   
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Parsing Service
   cd parsing-service && pip install -r requirements.txt
   ```

4. Run the services:
   ```bash
   # Backend (FastAPI)
   cd backend && uvicorn main:app --reload
   
   # Parsing Service (Flask)
   cd parsing-service && python app.py
   
   # Frontend
   cd frontend && npm start
   ```

## Environment Variables

Create `.env` files in each service directory with the required variables (see `.env.example` files).

## License

MIT License

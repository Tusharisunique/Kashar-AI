# Kashar AI Setup Guide

This guide will help you set up and run the Kashar AI project locally.

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **Supabase** account
- **Mistral AI** API key
- **Agora.io** account

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd "Kashar AI"
   ```

2. **Run the setup script:**
   ```bash
   ./scripts/start-dev.sh
   ```

## Manual Setup

### 1. Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   MISTRAL_API_KEY=your_mistral_api_key
   AGORA_APP_ID=your_agora_app_id
   AGORA_APP_CERTIFICATE=your_agora_app_certificate
   ```

5. **Start the backend:**
   ```bash
   uvicorn main:app --reload
   ```

### 2. Parsing Service Setup

1. **Navigate to parsing service directory:**
   ```bash
   cd parsing-service
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the parsing service:**
   ```bash
   python app.py
   ```

### 3. Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the frontend:**
   ```bash
   npm start
   ```

### 4. Database Setup

1. **Create a new Supabase project**
2. **Run the SQL schema** from `database/schema.sql` in your Supabase SQL editor
3. **Configure Row Level Security** policies as defined in the schema

## Environment Variables

### Backend (.env)
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key
- `MISTRAL_API_KEY`: Your Mistral AI API key
- `AGORA_APP_ID`: Your Agora App ID
- `AGORA_APP_CERTIFICATE`: Your Agora App Certificate
- `CHROMA_DB_PATH`: Path for ChromaDB storage (default: ./chroma_db)
- `PARSING_SERVICE_URL`: URL of the parsing service (default: http://localhost:5001)

## Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Parsing Service**: http://localhost:5001

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Check if services are already running: `lsof -i :3000,8000,5001`
   - Kill existing processes or change ports

2. **Environment variables not loaded**
   - Ensure `.env` file exists in backend directory
   - Check that all required variables are set

3. **Database connection issues**
   - Verify Supabase credentials
   - Check if RLS policies are properly configured

4. **ChromaDB issues**
   - Ensure write permissions for the chroma_db directory
   - Delete and recreate the chroma_db folder if corrupted

5. **Mistral AI API errors**
   - Verify API key is valid
   - Check API rate limits

### Development Tips

- Use the development startup script for easy setup: `./scripts/start-dev.sh`
- Check logs in each service terminal for debugging
- Use the FastAPI docs at `/docs` for API testing
- Monitor network requests in browser dev tools

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │    │   Flask Parser  │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Service)     │
│   Port 3000     │    │   Port 8000     │    │   Port 5001     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   Supabase      │              │
         │              │   (Database)    │              │
         │              └─────────────────┘              │
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   ChromaDB      │              │
         │              │   (Vectors)     │              │
         │              └─────────────────┘              │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                        ┌─────────────────┐
                        │   Mistral AI    │
                        │   (LLM API)     │
                        └─────────────────┘
```

## Next Steps

1. **Upload Documents**: Start by uploading PDF study materials
2. **Generate Content**: Create quizzes and flashcards from your documents
3. **Use AI Tutor**: Ask questions about your study materials
4. **Track Progress**: Monitor your learning journey in the progress dashboard

For more detailed information, check the individual component documentation in the `docs/` directory.

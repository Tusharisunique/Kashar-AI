-- Kashar AI Database Schema
-- Run this in your Supabase SQL editor

-- Users table (extends auth.users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    topics TEXT[] DEFAULT '{}',
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Topics table
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'medium',
    questions JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quiz results table
CREATE TABLE IF NOT EXISTS quiz_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    answers JSONB NOT NULL,
    time_taken INTEGER, -- in seconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tutor sessions table
CREATE TABLE IF NOT EXISTS tutor_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type TEXT NOT NULL DEFAULT 'text', -- 'text' or 'voice'
    duration INTEGER DEFAULT 0, -- in seconds
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Tutor messages table
CREATE TABLE IF NOT EXISTS tutor_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES tutor_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Flashcard sets table
CREATE TABLE IF NOT EXISTS flashcard_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    cards JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User progress logs table
CREATE TABLE IF NOT EXISTS progress_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL, -- 'quiz', 'tutor', 'flashcard'
    topic TEXT,
    score INTEGER,
    duration INTEGER, -- in seconds
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_topics_user_id ON topics(user_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_user_id ON quizzes(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_results_user_id ON quiz_results(user_id);
CREATE INDEX IF NOT EXISTS idx_tutor_sessions_user_id ON tutor_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_tutor_messages_session_id ON tutor_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_flashcard_sets_user_id ON flashcard_sets(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_logs_user_id ON progress_logs(user_id);

-- Row Level Security Policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tutor_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE flashcard_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_logs ENABLE ROW LEVEL SECURITY;

-- Users policies
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);

-- Documents policies
DROP POLICY IF EXISTS "Users can view own documents" ON documents;
DROP POLICY IF EXISTS "Users can insert own documents" ON documents;
DROP POLICY IF EXISTS "Users can update own documents" ON documents;
DROP POLICY IF EXISTS "Users can delete own documents" ON documents;
CREATE POLICY "Users can view own documents" ON documents FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own documents" ON documents FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own documents" ON documents FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own documents" ON documents FOR DELETE USING (auth.uid() = user_id);

-- Topics policies
DROP POLICY IF EXISTS "Users can view own topics" ON topics;
DROP POLICY IF EXISTS "Users can insert own topics" ON topics;
DROP POLICY IF EXISTS "Users can delete own topics" ON topics;
CREATE POLICY "Users can view own topics" ON topics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own topics" ON topics FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own topics" ON topics FOR DELETE USING (auth.uid() = user_id);

-- Quizzes policies
DROP POLICY IF EXISTS "Users can view own quizzes" ON quizzes;
DROP POLICY IF EXISTS "Users can insert own quizzes" ON quizzes;
CREATE POLICY "Users can view own quizzes" ON quizzes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own quizzes" ON quizzes FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Quiz results policies
DROP POLICY IF EXISTS "Users can view own quiz results" ON quiz_results;
DROP POLICY IF EXISTS "Users can insert own quiz results" ON quiz_results;
CREATE POLICY "Users can view own quiz results" ON quiz_results FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own quiz results" ON quiz_results FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Tutor sessions policies
DROP POLICY IF EXISTS "Users can view own tutor sessions" ON tutor_sessions;
DROP POLICY IF EXISTS "Users can insert own tutor sessions" ON tutor_sessions;
DROP POLICY IF EXISTS "Users can update own tutor sessions" ON tutor_sessions;
CREATE POLICY "Users can view own tutor sessions" ON tutor_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own tutor sessions" ON tutor_sessions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own tutor sessions" ON tutor_sessions FOR UPDATE USING (auth.uid() = user_id);

-- Tutor messages policies
DROP POLICY IF EXISTS "Users can view own tutor messages" ON tutor_messages;
DROP POLICY IF EXISTS "Users can insert own tutor messages" ON tutor_messages;
CREATE POLICY "Users can view own tutor messages" ON tutor_messages FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own tutor messages" ON tutor_messages FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Flashcard sets policies
DROP POLICY IF EXISTS "Users can view own flashcard sets" ON flashcard_sets;
DROP POLICY IF EXISTS "Users can insert own flashcard sets" ON flashcard_sets;
DROP POLICY IF EXISTS "Users can delete own flashcard sets" ON flashcard_sets;
CREATE POLICY "Users can view own flashcard sets" ON flashcard_sets FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own flashcard sets" ON flashcard_sets FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own flashcard sets" ON flashcard_sets FOR DELETE USING (auth.uid() = user_id);

-- Progress logs policies
DROP POLICY IF EXISTS "Users can view own progress logs" ON progress_logs;
DROP POLICY IF EXISTS "Users can insert own progress logs" ON progress_logs;
CREATE POLICY "Users can view own progress logs" ON progress_logs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own progress logs" ON progress_logs FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Functions for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to handle new user creation
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email)
    VALUES (NEW.id, NEW.email);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create user record when auth user is created
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

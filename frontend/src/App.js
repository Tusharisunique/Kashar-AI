import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Auth/Login';
import Signup from './components/Auth/Signup';
import Dashboard from './components/Dashboard/Dashboard';
import DocumentUpload from './components/Documents/DocumentUpload';
import DocumentsPage from './components/Documents/DocumentsPage';
import TutorRoom from './components/Tutor/TutorRoom';
import LiveTutorRoom from './components/Tutor/LiveTutorRoom';
import AgoraVoiceTutor from './components/Tutor/AgoraVoiceTutor';
import QuizPage from './components/Quiz/QuizPage';
import FlashcardsPage from './components/Flashcards/FlashcardsPage';
import ProgressPage from './components/Progress/ProgressPage';
import Layout from './components/Layout/Layout';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-900"></div>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/login" />;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-900"></div>
      </div>
    );
  }
  
  return user ? <Navigate to="/dashboard" /> : children;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1e293b',
                color: '#f8fafc',
              },
            }}
          />
          
          <Routes>
            <Route path="/login" element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            } />
            
            <Route path="/signup" element={
              <PublicRoute>
                <Signup />
              </PublicRoute>
            } />
            
            <Route path="/" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Navigate to="/dashboard" />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="upload" element={<DocumentUpload />} />
              <Route path="documents" element={<DocumentsPage />} />
              <Route path="tutor" element={<TutorRoom />} />
              <Route path="live-tutor" element={<AgoraVoiceTutor />} />
              <Route path="quiz" element={<QuizPage />} />
              <Route path="flashcards" element={<FlashcardsPage />} />
              <Route path="progress" element={<ProgressPage />} />
            </Route>
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

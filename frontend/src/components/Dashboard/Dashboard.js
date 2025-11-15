import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { 
  Upload, 
  MessageCircle, 
  Brain, 
  CreditCard, 
  BarChart3, 
  BookOpen,
  TrendingUp,
  Clock,
  Target,
  Mic
} from 'lucide-react';
import toast from 'react-hot-toast';

function Dashboard() {
  const [stats, setStats] = useState({
    documents: 0,
    topics: 0,
    quizzes: 0,
    studyTime: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [progressOverview, setProgressOverview] = useState({
    currentStreak: 0,
    averageScore: 0,
    topicsMastered: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [documentsRes, topicsRes, progressRes, streaksRes, analyticsRes] = await Promise.all([
        axios.get('/api/documents/'),
        axios.get('/api/documents/topics'),
        axios.get('/api/progress/'),
        axios.get('/api/progress/streaks'),
        axios.get('/api/progress/analytics')
      ]);

      setStats({
        documents: documentsRes.data.documents.length,
        topics: topicsRes.data.topics.length,
        quizzes: progressRes.data.progress.quiz_scores.length,
        studyTime: Math.round(progressRes.data.progress.total_study_time / 60) // Convert to minutes
      });

      // Set progress overview with real data
      setProgressOverview({
        currentStreak: streaksRes.data.streaks.current_streak,
        averageScore: Math.round(analyticsRes.data.analytics.average_score),
        topicsMastered: Object.keys(analyticsRes.data.analytics.topic_performance || {}).length
      });

      // Generate real recent activity from progress data
      const realActivity = [];
      const progress = progressRes.data.progress;
      
      // Add recent quiz activities
      if (progress.quiz_scores && progress.quiz_scores.length > 0) {
        const recentQuizzes = progress.quiz_scores.slice(-3).reverse();
        recentQuizzes.forEach(quiz => {
          const date = new Date(quiz.created_at);
          const timeAgo = getTimeAgo(date);
          realActivity.push({
            type: 'quiz',
            message: `Completed ${quiz.quizzes?.topic || 'quiz'} with ${Math.round(quiz.percentage)}% score`,
            time: timeAgo
          });
        });
      }

      // Add recent tutor sessions
      if (progress.tutor_sessions && progress.tutor_sessions.length > 0) {
        const recentSessions = progress.tutor_sessions.slice(-2).reverse();
        recentSessions.forEach(session => {
          const date = new Date(session.created_at);
          const timeAgo = getTimeAgo(date);
          realActivity.push({
            type: 'tutor',
            message: `Started AI tutor session`,
            time: timeAgo
          });
        });
      }

      // Add document uploads (from documents API)
      if (documentsRes.data.documents && documentsRes.data.documents.length > 0) {
        const recentDocs = documentsRes.data.documents.slice(-2).reverse();
        recentDocs.forEach(doc => {
          const date = new Date(doc.created_at);
          const timeAgo = getTimeAgo(date);
          realActivity.push({
            type: 'document',
            message: `Uploaded "${doc.title}"`,
            time: timeAgo
          });
        });
      }

      // Sort by most recent and limit to 5 items
      realActivity.sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0));
      setRecentActivity(realActivity.slice(0, 5));

      // If no activity, show a helpful message
      if (realActivity.length === 0) {
        setRecentActivity([{
          type: 'info',
          message: 'No recent activity yet. Start by uploading a document!',
          time: 'Get started'
        }]);
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getTimeAgo = (date) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    return date.toLocaleDateString();
  };

  const quickActions = [
    {
      title: 'Upload Documents',
      description: 'Add new study materials',
      icon: Upload,
      href: '/upload',
      color: 'bg-accent-500'
    },
    {
      title: 'My Documents',
      description: 'View and manage files',
      icon: BookOpen,
      href: '/documents',
      color: 'bg-primary-500'
    },
    {
      title: 'AI Tutor',
      description: 'Get instant help',
      icon: MessageCircle,
      href: '/tutor',
      color: 'bg-success-500'
    },
    {
      title: 'Live Tutor',
      description: 'Voice conversation',
      icon: Mic,
      href: '/live-tutor',
      color: 'bg-accent-600'
    },
    {
      title: 'Take Quiz',
      description: 'Test your knowledge',
      icon: Brain,
      href: '/quiz',
      color: 'bg-primary-600'
    },
    {
      title: 'Flashcards',
      description: 'Review key concepts',
      icon: CreditCard,
      href: '/flashcards',
      color: 'bg-accent-600'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center space-x-3">
            <BookOpen className="h-8 w-8 text-accent-600" />
            <div>
              <h1 className="card-title">Dashboard</h1>
              <p className="card-description">
                Your learning progress at a glance
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-600">Documents</p>
                <p className="text-2xl font-bold text-primary-900">{stats.documents}</p>
              </div>
              <BookOpen className="h-8 w-8 text-accent-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-600">Topics</p>
                <p className="text-2xl font-bold text-primary-900">{stats.topics}</p>
              </div>
              <Target className="h-8 w-8 text-success-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-600">Quizzes Taken</p>
                <p className="text-2xl font-bold text-primary-900">{stats.quizzes}</p>
              </div>
              <Brain className="h-8 w-8 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-600">Study Time</p>
                <p className="text-2xl font-bold text-primary-900">{stats.studyTime}m</p>
              </div>
              <Clock className="h-8 w-8 text-accent-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Quick Actions</h2>
          <p className="card-description">Jump into your learning activities</p>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {quickActions.map((action) => (
              <Link
                key={action.title}
                to={action.href}
                className="group p-4 rounded-lg border border-primary-200 hover:border-accent-300 hover:shadow-md transition-all"
              >
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${action.color}`}>
                    <action.icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-medium text-primary-900 group-hover:text-accent-700">
                      {action.title}
                    </h3>
                    <p className="text-sm text-primary-600">{action.description}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity & Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent Activity</h2>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {activity.type === 'quiz' && (
                      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <Brain className="w-4 h-4 text-primary-600" />
                      </div>
                    )}
                    {activity.type === 'tutor' && (
                      <div className="w-8 h-8 bg-success-100 rounded-full flex items-center justify-center">
                        <MessageCircle className="w-4 h-4 text-success-600" />
                      </div>
                    )}
                    {activity.type === 'document' && (
                      <div className="w-8 h-8 bg-accent-100 rounded-full flex items-center justify-center">
                        <Upload className="w-4 h-4 text-accent-600" />
                      </div>
                    )}
                    {activity.type === 'info' && (
                      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <BookOpen className="w-4 h-4 text-primary-600" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-primary-900">{activity.message}</p>
                    <p className="text-xs text-primary-500">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Progress Overview */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Progress Overview</h2>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-primary-600">Learning Streak</span>
                <span className="text-sm font-medium text-primary-900">
                  {progressOverview.currentStreak} {progressOverview.currentStreak === 1 ? 'day' : 'days'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-primary-600">Average Quiz Score</span>
                <span className={`text-sm font-medium ${progressOverview.averageScore >= 70 ? 'text-success-600' : progressOverview.averageScore >= 50 ? 'text-accent-600' : 'text-error-600'}`}>
                  {progressOverview.averageScore}%
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-primary-600">Topics Studied</span>
                <span className="text-sm font-medium text-primary-900">{progressOverview.topicsMastered}</span>
              </div>
              <Link
                to="/progress"
                className="inline-flex items-center text-sm text-accent-600 hover:text-accent-700 font-medium"
              >
                View detailed progress
                <TrendingUp className="ml-1 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

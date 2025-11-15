import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { BarChart3, TrendingUp, Clock, Target, Award, Calendar } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

function ProgressPage() {
  const [progressData, setProgressData] = useState(null);
  const [streaks, setStreaks] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    fetchProgressData();
  }, [timeRange]);

  const fetchProgressData = async () => {
    setLoading(true);
    try {
      const [progressRes, streaksRes, analyticsRes] = await Promise.all([
        axios.get(`/api/progress/?days=${timeRange}`),
        axios.get('/api/progress/streaks'),
        axios.get('/api/progress/analytics')
      ]);

      setProgressData(progressRes.data.progress);
      setStreaks(streaksRes.data.streaks);
      setAnalytics(analyticsRes.data.analytics);
    } catch (error) {
      console.error('Error fetching progress data:', error);
      toast.error('Failed to load progress data');
    } finally {
      setLoading(false);
    }
  };

  const formatChartData = (quizScores) => {
    return quizScores.map((score, index) => ({
      quiz: index + 1,
      percentage: score.percentage,
      date: new Date(score.created_at).toLocaleDateString()
    }));
  };

  const formatTopicData = (topicPerformance) => {
    return Object.entries(topicPerformance).map(([topic, score]) => ({
      topic: topic.length > 15 ? topic.substring(0, 15) + '...' : topic,
      score: Math.round(score)
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-900"></div>
      </div>
    );
  }

  const chartData = progressData?.quiz_scores ? formatChartData(progressData.quiz_scores) : [];
  const topicData = analytics?.topic_performance ? formatTopicData(analytics.topic_performance) : [];

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <BarChart3 className="h-8 w-8 text-accent-600" />
              <div>
                <h1 className="card-title">Progress Dashboard</h1>
                <p className="card-description">
                  Track your learning journey and achievements
                </p>
              </div>
            </div>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(parseInt(e.target.value))}
              className="input w-auto"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-600">Current Streak</p>
                <p className="text-2xl font-bold text-primary-900">
                  {streaks?.current_streak || 0} days
                </p>
              </div>
              <Award className="h-8 w-8 text-accent-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-600">Longest Streak</p>
                <p className="text-2xl font-bold text-primary-900">
                  {streaks?.longest_streak || 0} days
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-success-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-600">Total Quizzes</p>
                <p className="text-2xl font-bold text-primary-900">
                  {analytics?.total_quizzes || 0}
                </p>
              </div>
              <Target className="h-8 w-8 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-600">Average Score</p>
                <p className="text-2xl font-bold text-primary-900">
                  {analytics?.average_score || 0}%
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-accent-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quiz Performance Over Time */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Quiz Performance Trend</h2>
            <p className="card-description">Your quiz scores over time</p>
          </div>
          <div className="card-content">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="quiz" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Score']}
                    labelFormatter={(label) => `Quiz ${label}`}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="percentage" 
                    stroke="#f59e0b" 
                    strokeWidth={2}
                    dot={{ fill: '#f59e0b', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-primary-500">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No quiz data available</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Topic Performance */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Performance by Topic</h2>
            <p className="card-description">Average scores across different topics</p>
          </div>
          <div className="card-content">
            {topicData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topicData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="topic" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Average Score']}
                  />
                  <Bar dataKey="score" fill="#64748b" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-primary-500">
                <div className="text-center">
                  <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No topic data available</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Study Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Topics Studied */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Topics Studied</h2>
            <p className="card-description">Recent study topics</p>
          </div>
          <div className="card-content">
            {progressData?.topics_studied?.length > 0 ? (
              <div className="space-y-2">
                {progressData.topics_studied.slice(0, 8).map((topic, index) => (
                  <div key={index} className="flex items-center space-x-3 p-2 rounded-lg bg-primary-50">
                    <div className="w-2 h-2 bg-accent-500 rounded-full"></div>
                    <span className="text-sm text-primary-900">{topic}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-primary-500">
                <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No study activity yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Study Time */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Study Summary</h2>
            <p className="card-description">Your learning statistics</p>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-primary-600" />
                  <span className="text-sm text-primary-700">Total Study Time</span>
                </div>
                <span className="font-medium text-primary-900">
                  {Math.round((progressData?.total_study_time || 0) / 60)} minutes
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Target className="h-5 w-5 text-primary-600" />
                  <span className="text-sm text-primary-700">Tutor Sessions</span>
                </div>
                <span className="font-medium text-primary-900">
                  {progressData?.tutor_sessions?.length || 0}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Award className="h-5 w-5 text-primary-600" />
                  <span className="text-sm text-primary-700">Topics Covered</span>
                </div>
                <span className="font-medium text-primary-900">
                  {progressData?.topics_studied?.length || 0}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProgressPage;

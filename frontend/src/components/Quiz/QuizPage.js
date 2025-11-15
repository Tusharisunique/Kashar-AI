import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { Brain, CheckCircle, XCircle, RotateCcw } from 'lucide-react';

function QuizPage() {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [numQuestions, setNumQuestions] = useState(5);
  const [quiz, setQuiz] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [quizResult, setQuizResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    try {
      const response = await axios.get('/api/documents/topics');
      setTopics(response.data.topics);
    } catch (error) {
      console.error('Error fetching topics:', error);
      toast.error('Failed to load topics');
    }
  };

  const generateQuiz = async () => {
    if (!selectedTopic) {
      toast.error('Please select a topic');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/quiz/generate', {
        topic: selectedTopic,
        difficulty,
        num_questions: numQuestions
      });

      setQuiz(response.data.quiz);
      setCurrentQuestion(0);
      setAnswers([]);
      setSelectedAnswer(null);
      setShowResult(false);
      setQuizResult(null);
    } catch (error) {
      console.error('Error generating quiz:', error);
      toast.error('Failed to generate quiz');
    } finally {
      setLoading(false);
    }
  };

  const selectAnswer = (answerIndex) => {
    setSelectedAnswer(answerIndex);
  };

  const nextQuestion = () => {
    if (selectedAnswer === null) {
      toast.error('Please select an answer');
      return;
    }

    const newAnswers = [...answers, selectedAnswer];
    setAnswers(newAnswers);
    setSelectedAnswer(null);

    if (currentQuestion + 1 < quiz.questions.length) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      submitQuiz(newAnswers);
    }
  };

  const submitQuiz = async (finalAnswers) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/quiz/submit', {
        quiz_id: quiz.id,
        answers: finalAnswers
      });

      setQuizResult(response.data.result);
      setShowResult(true);
    } catch (error) {
      console.error('Error submitting quiz:', error);
      toast.error('Failed to submit quiz');
    } finally {
      setLoading(false);
    }
  };

  const resetQuiz = () => {
    setQuiz(null);
    setCurrentQuestion(0);
    setAnswers([]);
    setSelectedAnswer(null);
    setShowResult(false);
    setQuizResult(null);
  };

  if (showResult && quizResult) {
    return (
      <div className="space-y-6">
        <div className="card">
          <div className="card-header">
            <h1 className="card-title">Quiz Results</h1>
          </div>
        </div>

        <div className="card">
          <div className="card-content text-center">
            <div className="mb-6">
              {quizResult.percentage >= 70 ? (
                <CheckCircle className="h-16 w-16 text-success-500 mx-auto mb-4" />
              ) : (
                <XCircle className="h-16 w-16 text-danger-500 mx-auto mb-4" />
              )}
              
              <h2 className="text-3xl font-bold text-primary-900 mb-2">
                {quizResult.percentage}%
              </h2>
              <p className="text-lg text-primary-600">
                {quizResult.score} out of {quizResult.total_questions} correct
              </p>
            </div>

            <div className="bg-primary-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-primary-600 mb-2">Next Difficulty Level</p>
              <p className="font-medium text-primary-900 capitalize">
                {quizResult.new_difficulty}
              </p>
            </div>

            <div className="flex justify-center space-x-4">
              <button onClick={resetQuiz} className="btn-secondary">
                <RotateCcw className="h-4 w-4 mr-2" />
                Take Another Quiz
              </button>
              <button onClick={generateQuiz} className="btn-primary">
                Retry Same Topic
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (quiz) {
    const question = quiz.questions[currentQuestion];
    const progress = ((currentQuestion + 1) / quiz.questions.length) * 100;

    return (
      <div className="space-y-6">
        <div className="card">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <h1 className="card-title">Quiz: {selectedTopic}</h1>
              <span className="text-sm text-primary-600">
                Question {currentQuestion + 1} of {quiz.questions.length}
              </span>
            </div>
            <div className="w-full bg-primary-200 rounded-full h-2 mt-4">
              <div
                className="bg-accent-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-content">
            <h2 className="text-xl font-semibold text-primary-900 mb-6">
              {question.question}
            </h2>

            <div className="space-y-3 mb-6">
              {question.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => selectAnswer(index)}
                  className={`w-full p-4 text-left rounded-lg border transition-colors ${
                    selectedAnswer === index
                      ? 'border-accent-500 bg-accent-50 text-accent-700'
                      : 'border-primary-200 hover:border-accent-300 hover:bg-accent-50'
                  }`}
                >
                  <span className="font-medium mr-3">
                    {String.fromCharCode(65 + index)}.
                  </span>
                  {option}
                </button>
              ))}
            </div>

            <div className="flex justify-end">
              <button
                onClick={nextQuestion}
                disabled={selectedAnswer === null || loading}
                className="btn-primary"
              >
                {loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {currentQuestion + 1 === quiz.questions.length ? 'Submitting...' : 'Processing...'}
                  </div>
                ) : (
                  currentQuestion + 1 === quiz.questions.length ? 'Submit Quiz' : 'Next Question'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <div className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-accent-600" />
            <div>
              <h1 className="card-title">Quiz Generator</h1>
              <p className="card-description">
                Test your knowledge with AI-generated quizzes
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-primary-700 mb-2">
                Select Topic
              </label>
              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                className="input"
              >
                <option value="">Choose a topic...</option>
                {topics.map((topic) => (
                  <option key={topic} value={topic}>
                    {topic}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-primary-700 mb-2">
                Difficulty Level
              </label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="input"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-primary-700 mb-2">
                Number of Questions
              </label>
              <select
                value={numQuestions}
                onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                className="input"
              >
                <option value={5}>5 Questions</option>
                <option value={10}>10 Questions</option>
                <option value={15}>15 Questions</option>
                <option value={20}>20 Questions</option>
              </select>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={generateQuiz}
              disabled={loading || !selectedTopic}
              className="btn-primary"
            >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating Quiz...
                </div>
              ) : (
                'Generate Quiz'
              )}
            </button>
          </div>
        </div>
      </div>

      {topics.length === 0 && (
        <div className="card">
          <div className="card-content text-center py-8">
            <Brain className="h-12 w-12 text-primary-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-primary-900 mb-2">
              No Topics Available
            </h3>
            <p className="text-primary-600">
              Upload some study materials first to generate quizzes.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default QuizPage;

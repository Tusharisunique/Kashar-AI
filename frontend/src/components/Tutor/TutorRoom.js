import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { Send, MessageCircle, Bot, User } from 'lucide-react';

function TutorRoom() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    startSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startSession = async () => {
    try {
      const response = await axios.post('/api/tutor/start-session', {
        session_type: 'text'
      });
      setSessionId(response.data.session_id);
      
      // Add welcome message
      setMessages([{
        role: 'assistant',
        content: 'Hello! I\'m your AI tutor. I\'m here to help you with your studies. What would you like to learn about today?',
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Error starting session:', error);
      toast.error('Failed to start tutor session');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post('/api/tutor/message', {
        message: inputMessage,
        session_id: sessionId
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response.response,
        timestamp: new Date(),
        sources: response.data.response.sources
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
      
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const endSession = async () => {
    if (sessionId) {
      try {
        await axios.post(`/api/tutor/end-session/${sessionId}`);
        toast.success('Session ended successfully');
        setSessionId(null);
        setMessages([]);
      } catch (error) {
        console.error('Error ending session:', error);
        toast.error('Failed to end session');
      }
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="card mb-6">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <MessageCircle className="h-8 w-8 text-accent-600" />
              <div>
                <h1 className="card-title">AI Tutor</h1>
                <p className="card-description">
                  Get instant help with your studies
                </p>
              </div>
            </div>
            {sessionId && (
              <button
                onClick={endSession}
                className="btn-secondary"
              >
                End Session
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="card flex-1 flex flex-col">
        <div className="card-content flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4 max-h-96">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-accent-500 text-white'
                      : message.isError
                      ? 'bg-danger-100 text-danger-800 border border-danger-200'
                      : 'bg-primary-100 text-primary-900'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.role === 'assistant' && (
                      <Bot className="h-4 w-4 mt-1 flex-shrink-0" />
                    )}
                    {message.role === 'user' && (
                      <User className="h-4 w-4 mt-1 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      {message.sources && (
                        <div className="mt-2 text-xs opacity-75">
                          <p>Sources: {message.sources.join(', ')}</p>
                        </div>
                      )}
                      <p className="text-xs opacity-75 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-primary-100 text-primary-900 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Bot className="h-4 w-4" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form onSubmit={sendMessage} className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask me anything about your studies..."
              className="input flex-1"
              disabled={loading || !sessionId}
            />
            <button
              type="submit"
              disabled={loading || !sessionId || !inputMessage.trim()}
              className="btn-primary"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default TutorRoom;

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import AgoraRTC from 'agora-rtc-sdk-ng';
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  MessageCircle, 
  Send,
  Phone,
  PhoneOff,
  Loader,
  AlertCircle,
  Settings,
  Bot
} from 'lucide-react';

function LiveTutorRoom() {
  const { user } = useAuth();
  
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  
  // Audio state
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Agora clients
  const rtcClient = useRef(null);
  const localAudioTrack = useRef(null);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  
  // Session data
  const [sessionData, setSessionData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  useEffect(() => {
    return () => {
      // Cleanup on unmount
      handleDisconnect();
    };
  }, []);

  const handleConnect = async () => {
    setIsConnecting(true);
    setConnectionStatus('connecting');
    
    try {
      // Get auth token
      const token = localStorage.getItem('access_token');
      console.log('Auth token check:', token ? 'Token found' : 'No token found');
      
      if (!token) {
        throw new Error('Authentication required - please log in first');
      }
      
      console.log('Starting voice session...');
      
      // Start voice session
      const response = await axios.post('/api/tutor/voice/start-session', {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const session = response.data;
      console.log('Session started successfully:', session);
      
      setSessionId(session.session_id);
      setSessionData(session);
      
      // Initialize Agora RTC for voice (simplified for testing)
      try {
        await initializeAgoraRTC(session);
      } catch (agoraError) {
        console.warn('Agora initialization failed, continuing without real-time audio:', agoraError);
        // Continue without Agora for basic functionality
      }
      
      setIsConnected(true);
      setConnectionStatus('connected');
      toast.success('Connected to Kashar AI! You can now speak or type.');
      
      // Add welcome message from Kashar
      addMessage('ai', 'Hello! I\'m Kashar, your AI tutor. You can speak to me directly or type your questions. How can I help you learn today?');
      
    } catch (error) {
      console.error('Connection error:', error);
      setConnectionStatus('error');
      
      let errorMessage = 'Failed to connect to Kashar AI';
      
      if (error.message === 'Authentication required - please log in first') {
        errorMessage = 'Please log in first to use the voice tutor';
      } else if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.detail || `Server error: ${error.response.status}`;
      } else if (error.request) {
        // Network error
        errorMessage = 'Network error - please check your connection';
      } else {
        // Other error
        errorMessage = error.message || 'Unknown error occurred';
      }
      
      console.error('Detailed error:', errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsConnecting(false);
    }
  };

  const initializeAgoraRTC = async (session) => {
    try {
      const { agora_tokens, channel_name } = session;
      
      // Initialize RTC client for voice communication
      rtcClient.current = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
      
      // Join RTC channel
      await rtcClient.current.join(
        agora_tokens.app_id,
        channel_name,
        agora_tokens.rtc_token,
        parseInt(user.id) || user.id // Ensure user ID is in correct format
      );
      
      // Create local audio track
      localAudioTrack.current = await AgoraRTC.createMicrophoneAudioTrack({
        encoderConfig: {
          sampleRate: 48000,
          stereo: true,
          bitrate: 48
        }
      });
      
      // Publish local audio
      await rtcClient.current.publish([localAudioTrack.current]);
      
      // Listen for remote users (AI responses)
      rtcClient.current.on('user-published', async (remoteUser, mediaType) => {
        if (mediaType === 'audio') {
          await rtcClient.current.subscribe(remoteUser, mediaType);
          if (isSpeakerOn) {
            remoteUser.audioTrack.play();
          }
          console.log('Playing AI audio response');
        }
      });
      
      // Handle user left
      rtcClient.current.on('user-left', (remoteUser) => {
        console.log('Remote user left:', remoteUser.uid);
      });
      
      console.log('Agora RTC initialized successfully');
      
    } catch (error) {
      console.error('Error initializing Agora RTC:', error);
      throw error;
    }
  };

  const addMessage = (type, content) => {
    const message = {
      id: Date.now() + Math.random(),
      type,
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };
  
  const handleDisconnect = async () => {
    try {
      setConnectionStatus('disconnecting');
      
      // Stop recording if active
      if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
        mediaRecorder.current.stop();
      }
      
      // Clean up Agora resources
      if (localAudioTrack.current) {
        localAudioTrack.current.close();
        localAudioTrack.current = null;
      }
      
      if (rtcClient.current) {
        await rtcClient.current.leave();
        rtcClient.current = null;
      }
      
      // End session
      if (sessionId) {
        const token = localStorage.getItem('access_token');
        await axios.post(`/api/tutor/voice/end-session/${sessionId}`, {}, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      }
      
      // Reset state
      setIsConnected(false);
      setConnectionStatus('disconnected');
      setSessionId(null);
      setSessionData(null);
      setMessages([]);
      
      toast.success('Disconnected from Kashar AI');
      
    } catch (error) {
      console.error('Disconnect error:', error);
      toast.error('Error disconnecting');
    }
  };

  const toggleMute = async () => {
    if (localAudioTrack.current) {
      await localAudioTrack.current.setMuted(!isMuted);
      setIsMuted(!isMuted);
    }
  };

  const toggleSpeaker = () => {
    setIsSpeakerOn(!isSpeakerOn);
    // Note: Speaker control would need additional implementation
    // This is a UI toggle for now
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];
      
      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };
      
      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        await processVoiceMessage(audioBlob);
        setIsRecording(false);
      };
      
      mediaRecorder.current.start();
      setIsRecording(true);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('Failed to start recording');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
    }
  };

  const processVoiceMessage = async (audioBlob) => {
    if (!sessionId) return;
    
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('audio_file', audioBlob, 'voice_message.wav');
      
      const token = localStorage.getItem('access_token');
      const response = await axios.post('/api/tutor/voice/process-audio', formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = response.data;
      
      // Add user message (transcribed)
      if (result.user_message) {
        addMessage('user', result.user_message);
      }
      
      // Add AI response
      if (result.response) {
        addMessage('ai', result.response);
        
        // Play audio response if available
        if (result.audio_response && result.has_audio) {
          playAudioResponse(result.audio_response);
        }
      }
      
      if (result.error) {
        toast.error(result.error);
      }
      
    } catch (error) {
      console.error('Error processing voice message:', error);
      toast.error('Failed to process voice message');
    } finally {
      setIsProcessing(false);
    }
  };

  const playAudioResponse = (audioData) => {
    try {
      // Convert base64 to blob and play
      const byteCharacters = atob(audioData);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const audioBlob = new Blob([byteArray], { type: 'audio/mpeg' });
      
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
      
    } catch (error) {
      console.error('Error playing audio response:', error);
    }
  };

  const sendTextMessage = async () => {
    if (!currentMessage.trim() || !sessionId) return;
    
    const message = currentMessage.trim();
    setCurrentMessage('');
    
    // Add user message immediately
    addMessage('user', message);
    
    setIsProcessing(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post('/api/tutor/voice/process-text', {
        session_id: sessionId,
        message: message
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = response.data;
      
      // Add AI response
      if (result.response) {
        addMessage('ai', result.response);
        
        // Play audio response if available
        if (result.audio_response && result.has_audio) {
          playAudioResponse(result.audio_response);
        }
      }
      
    } catch (error) {
      console.error('Error sending text message:', error);
      toast.error('Failed to send message');
    } finally {
      setIsProcessing(false);
    }
  };


  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 flex items-center justify-center p-4">
        <div className="card max-w-md w-full text-center">
          <div className="card-content space-y-6">
            <div className="w-20 h-20 mx-auto bg-accent-100 rounded-full flex items-center justify-center">
              <MessageCircle className="w-10 h-10 text-accent-600" />
            </div>
            
            <div>
              <h1 className="text-2xl font-bold text-primary-900 mb-2">Live AI Tutor</h1>
              <p className="text-primary-600">
                Connect to start a voice conversation with your AI tutor. 
                Ask questions, get explanations, and learn interactively!
              </p>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-center space-x-2 text-sm text-primary-600">
                <Mic className="w-4 h-4" />
                <span>Voice Recognition</span>
              </div>
              <div className="flex items-center justify-center space-x-2 text-sm text-primary-600">
                <Volume2 className="w-4 h-4" />
                <span>AI Voice Responses</span>
              </div>
              <div className="flex items-center justify-center space-x-2 text-sm text-primary-600">
                <MessageCircle className="w-4 h-4" />
                <span>Text Chat Support</span>
              </div>
            </div>
            
            <button
              onClick={handleConnect}
              disabled={isConnecting}
              className="btn btn-primary w-full disabled:opacity-50"
            >
              {isConnecting ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <Phone className="w-4 h-4 mr-2" />
                  Start Live Session
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-primary-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-primary-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-success-500 rounded-full animate-pulse"></div>
            <h1 className="text-lg font-semibold text-primary-900">Live AI Tutor</h1>
            <span className="text-sm text-primary-600">Connected</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={toggleMute}
              className={`p-2 rounded-lg transition-colors ${
                isMuted 
                  ? 'bg-error-100 text-error-600 hover:bg-error-200' 
                  : 'bg-success-100 text-success-600 hover:bg-success-200'
              }`}
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
            
            <button
              onClick={toggleSpeaker}
              className={`p-2 rounded-lg transition-colors ${
                isSpeakerOn 
                  ? 'bg-primary-100 text-primary-600 hover:bg-primary-200' 
                  : 'bg-primary-200 text-primary-500'
              }`}
              title={isSpeakerOn ? 'Mute Speaker' : 'Unmute Speaker'}
            >
              {isSpeakerOn ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </button>
            
            <button
              onClick={handleDisconnect}
              className="p-2 bg-error-100 text-error-600 hover:bg-error-200 rounded-lg transition-colors"
              title="End Session"
            >
              <PhoneOff className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-accent-600 text-white'
                  : 'bg-white text-primary-900 border border-primary-200'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <p className={`text-xs mt-1 ${
                message.type === 'user' ? 'text-accent-200' : 'text-primary-500'
              }`}>
                {formatTime(message.timestamp)}
              </p>
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-white border border-primary-200 rounded-lg px-4 py-2">
              <div className="flex items-center space-x-2">
                <Loader className="w-4 h-4 animate-spin text-primary-600" />
                <span className="text-sm text-primary-600">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Voice Controls */}
      <div className="bg-white border-t border-primary-200 p-4">
        <div className="flex items-center justify-center space-x-4 mb-4">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
              isRecording
                ? 'bg-error-500 hover:bg-error-600 text-white animate-pulse'
                : 'bg-accent-500 hover:bg-accent-600 text-white'
            } disabled:opacity-50`}
          >
            <Mic className="w-6 h-6" />
          </button>
        </div>
        
        <div className="text-center text-sm text-primary-600 mb-4">
          {isRecording ? 'Recording... Tap to stop' : 'Tap to speak'}
        </div>

        {/* Text Input */}
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
            placeholder="Type a message..."
            className="input flex-1"
            disabled={isProcessing}
          />
          <button
            onClick={sendTextMessage}
            disabled={!currentMessage.trim() || isProcessing}
            className="btn btn-primary disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default LiveTutorRoom;

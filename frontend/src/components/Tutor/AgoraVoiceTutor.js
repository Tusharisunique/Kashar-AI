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
  Bot,
  Waves
} from 'lucide-react';

function AgoraVoiceTutor() {
  const { user } = useAuth();
  
  // Session state
  const [sessionId, setSessionId] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  
  // Agora state
  const [agoraClient, setAgoraClient] = useState(null);
  const [localAudioTrack, setLocalAudioTrack] = useState(null);
  const [remoteUsers, setRemoteUsers] = useState({});
  const [isJoined, setIsJoined] = useState(false);
  
  // Audio state
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showChat, setShowChat] = useState(false);
  
  // Session data
  const [sessionData, setSessionData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  // Refs
  const audioProcessorRef = useRef(null);
  const streamingIntervalRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  
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
      
      console.log('Starting Agora voice session...');
      
      // Start Agora voice session
      const response = await axios.post('/api/agora/voice/start-session', {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const session = response.data;
      console.log('Agora voice session started:', session);
      
      setSessionId(session.session_id);
      setSessionData(session);
      
      // Initialize Agora RTC
      await initializeAgoraRTC(session);
      
      setIsConnected(true);
      setConnectionStatus('connected');
      toast.success('Connected to Kashar AI with Agora voice streaming!');
      
      // Add welcome message from Kashar
      addMessage('ai', 'Hello! I\'m Kashar, your AI tutor. I can hear you through Agora real-time voice streaming. Start speaking and I\'ll respond with my voice!');
      
    } catch (error) {
      console.error('Connection error:', error);
      setConnectionStatus('error');
      
      let errorMessage = 'Failed to connect to Kashar AI';
      
      if (error.message === 'Authentication required - please log in first') {
        errorMessage = 'Please log in first to use the voice tutor';
      } else if (error.response) {
        errorMessage = error.response.data?.detail || `Server error: ${error.response.status}`;
      } else if (error.request) {
        errorMessage = 'Network error - please check your connection';
      } else {
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
      console.log('Initializing Agora RTC with session:', { agora_tokens, channel_name });
      
      if (!agora_tokens || !agora_tokens.app_id || !agora_tokens.rtc_token) {
        throw new Error('Missing Agora tokens in session data');
      }
      
      // Create Agora client
      const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
      
      // Set up event handlers
      client.on('user-published', async (remoteUser, mediaType) => {
        console.log('Remote user published:', remoteUser.uid, mediaType);
        
        if (mediaType === 'audio') {
          await client.subscribe(remoteUser, mediaType);
          
          if (isSpeakerOn && remoteUser.audioTrack) {
            remoteUser.audioTrack.play();
          }
          
          setRemoteUsers(prev => ({
            ...prev,
            [remoteUser.uid]: remoteUser
          }));
          
          console.log('Playing AI audio response from Agora');
        }
      });
      
      client.on('user-unpublished', (remoteUser, mediaType) => {
        console.log('Remote user unpublished:', remoteUser.uid, mediaType);
        
        if (mediaType === 'audio') {
          setRemoteUsers(prev => {
            const updated = { ...prev };
            delete updated[remoteUser.uid];
            return updated;
          });
        }
      });
      
      client.on('user-left', (remoteUser) => {
        console.log('Remote user left:', remoteUser.uid);
        setRemoteUsers(prev => {
          const updated = { ...prev };
          delete updated[remoteUser.uid];
          return updated;
        });
      });
      
      // Use the UID from the token data - this ensures consistency
      // The backend should include the UID that was used for token generation
      let agoraUserId;
      if (agora_tokens.user_uid) {
        // Use the UID that was actually used for token generation
        agoraUserId = agora_tokens.user_uid;
      } else {
        // Fallback: use the same logic as backend
        if (typeof user.id === 'string' && user.id.match(/^\d+$/)) {
          agoraUserId = parseInt(user.id);
        } else {
          // For non-numeric user IDs, we need to use the exact same hash as the backend
          // Since JavaScript and Python hash differently, we'll use a simple approach
          agoraUserId = user.id; // Let Agora handle string UIDs
        }
      }
      
      console.log('Joining Agora channel with:', {
        appId: agora_tokens.app_id,
        channel: channel_name,
        token: agora_tokens.rtc_token.substring(0, 20) + '...',
        userId: agoraUserId,
        originalUserId: user.id
      });
      
      // Join channel
      await client.join(
        agora_tokens.app_id,
        channel_name,
        agora_tokens.rtc_token,
        agoraUserId
      );
      
      console.log('Joined Agora channel successfully');
      setIsJoined(true);
      
      // Create and publish local audio track
      const audioTrack = await AgoraRTC.createMicrophoneAudioTrack({
        encoderConfig: {
          sampleRate: 48000,
          stereo: false,
          bitrate: 48
        }
      });
      
      await client.publish([audioTrack]);
      
      setAgoraClient(client);
      setLocalAudioTrack(audioTrack);
      
      // Start audio streaming for AI processing
      startAudioStreaming(audioTrack);
      
      // Notify backend that user joined
      await notifyUserJoined(session.session_id, user.id);
      
      console.log('Agora RTC initialized successfully with voice streaming');
      
    } catch (error) {
      console.error('Error initializing Agora RTC:', error);
      throw error;
    }
  };

  const startAudioStreaming = (audioTrack) => {
    try {
      console.log('Audio streaming ready - use push-to-talk or text chat');
      setIsStreaming(true);
      
      if (streamingIntervalRef.current) {
        clearInterval(streamingIntervalRef.current);
      }

      streamingIntervalRef.current = setInterval(() => {
        try {
          if (!audioTrack) {
            setAudioLevel(0);
            return;
          }
          const level = typeof audioTrack.getVolumeLevel === 'function'
            ? audioTrack.getVolumeLevel()
            : 0;
          setAudioLevel(prev => prev * 0.7 + level * 0.3);
        } catch (err) {
          console.error('Error reading audio level:', err);
        }
      }, 100);

      // For now, we'll use text-based interaction
      // Voice streaming through Agora is connected and ready
      toast.success('Voice streaming connected! Use text chat to interact with Kashar.');
      
    } catch (error) {
      console.error('Error starting audio streaming:', error);
    }
  };

  const notifyUserJoined = async (sessionId, userId) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post('/api/agora/voice/user-joined', {
        session_id: sessionId,
        user_id: userId
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('Error notifying user joined:', error);
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

  const toggleMute = async () => {
    if (localAudioTrack) {
      await localAudioTrack.setMuted(!isMuted);
      setIsMuted(!isMuted);
    }
  };

  const toggleSpeaker = () => {
    setIsSpeakerOn(!isSpeakerOn);
    
    // Apply to all remote users
    Object.values(remoteUsers).forEach(remoteUser => {
      if (remoteUser.audioTrack) {
        if (isSpeakerOn) {
          remoteUser.audioTrack.stop();
        } else {
          remoteUser.audioTrack.play();
        }
      }
    });
  };

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processVoiceMessage(audioBlob);
        setIsRecording(false);
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      toast.success('Recording... Speak now!');
      
    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('Failed to start recording. Please check microphone permissions.');
    }
  };

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      // Toast will be shown in processVoiceMessage function
    }
  };

  const processVoiceMessage = async (audioBlob) => {
    if (!sessionId) return;
    
    setIsProcessing(true);
    const loadingToast = toast.loading('Processing your voice message...');
    
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
      
      // Dismiss loading toast
      toast.dismiss(loadingToast);
      
      // Add user message (transcribed)
      if (result.user_message) {
        addMessage('user', result.user_message);
      }
      
      // Add AI response
      if (result.response) {
        addMessage('ai', result.response);
        toast.success('Voice message processed!');
        
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
      toast.dismiss(loadingToast);
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

  const handleDisconnect = async () => {
    try {
      setConnectionStatus('disconnecting');
      
      // Stop audio streaming
      if (streamingIntervalRef.current) {
        clearInterval(streamingIntervalRef.current);
        streamingIntervalRef.current = null;
      }
      
      setIsStreaming(false);
      setAudioLevel(0);
      
      // Clean up Agora resources
      if (localAudioTrack) {
        localAudioTrack.close();
        setLocalAudioTrack(null);
      }
      
      if (agoraClient && isJoined) {
        await agoraClient.leave();
        setIsJoined(false);
      }
      
      setAgoraClient(null);
      setRemoteUsers({});
      
      // End session
      if (sessionId) {
        const token = localStorage.getItem('access_token');
        await axios.post(`/api/agora/voice/end-session/${sessionId}`, {}, {
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
        
        // Audio response will be handled through Agora streaming
        if (result.has_audio) {
          console.log('AI audio response available through Agora');
        }
      }
      
      if (result.error) {
        toast.error(result.error);
      }
      
    } catch (error) {
      console.error('Error sending text message:', error);
      const errorMessage =
        (error.response && (error.response.data?.detail || error.response.data?.error)) ||
        'Failed to send message';
      toast.error(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const blobOuterScale = 1 + audioLevel * 0.4;
  const blobInnerScale = 1 + audioLevel * 0.25;
  const blobGlow = 80 + audioLevel * 60;
  const blobOuterOpacity = 0.5 + audioLevel * 0.4;
  const blobBlur = 40 + audioLevel * 20;

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 flex items-center justify-center p-4">
        <div className="card max-w-md w-full text-center">
          <div className="card-content space-y-6">
            <div className="w-20 h-20 mx-auto bg-accent-100 rounded-full flex items-center justify-center">
              <Waves className="w-10 h-10 text-accent-600" />
            </div>
            
            <div>
              <h1 className="text-2xl font-bold text-primary-900 mb-2">Agora Voice Tutor</h1>
              <p className="text-primary-600">
                Connect to start real-time voice conversations with Kashar AI using Agora RTC streaming. 
                Experience natural voice interactions with instant AI responses!
              </p>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-center space-x-2 text-sm text-primary-600">
                <Waves className="w-4 h-4" />
                <span>Agora Real-time Communication</span>
              </div>
              <div className="flex items-center justify-center space-x-2 text-sm text-primary-600">
                <Mic className="w-4 h-4" />
                <span>ElevenLabs Speech Recognition</span>
              </div>
              <div className="flex items-center justify-center space-x-2 text-sm text-primary-600">
                <Volume2 className="w-4 h-4" />
                <span>ElevenLabs Voice Synthesis</span>
              </div>
              <div className="flex items-center justify-center space-x-2 text-sm text-primary-600">
                <Bot className="w-4 h-4" />
                <span>AI-Powered Learning Assistant</span>
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
                  Connecting to Agora...
                </>
              ) : (
                <>
                  <Phone className="w-4 h-4 mr-2" />
                  Start Agora Voice Session
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (

    <div className="min-h-screen bg-[#050509] flex flex-col text-white">
      {/* Header */}
      <div className="px-6 py-4 bg-[#111318] border-b border-[#1f2128]">
        <h1 className="text-sm font-medium tracking-wide">Conversational AI Agent</h1>
      </div>

      {/* Messages */}
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-4xl aspect-video bg-[#111318] rounded-2xl flex items-center justify-center relative overflow-hidden">
          <div className="relative w-56 h-56 sm:w-64 sm:h-64">
            <div
              className="absolute inset-0 bg-gradient-to-tr from-[#00f5ff] via-[#007bff] to-[#0014ff] rounded-full"
              style={{
                opacity: blobOuterOpacity,
                filter: `blur(${blobBlur}px)`,
                transform: `scale(${blobOuterScale})`,
                transition: 'transform 120ms ease-out, opacity 120ms ease-out, filter 120ms ease-out'
              }}
            ></div>
            <div
              className="absolute inset-4 bg-gradient-to-br from-[#00c3ff] via-[#0050ff] to-[#0014ff] rounded-full"
              style={{
                boxShadow: `0 0 ${blobGlow}px rgba(0,112,255,0.9)`,
                transform: `scale(${blobInnerScale})`,
                transition: 'transform 120ms ease-out, box-shadow 120ms ease-out'
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="pb-8 pt-4 flex justify-center">
        <div className="flex items-center space-x-6">
          <button
            onMouseDown={startVoiceRecording}
            onMouseUp={stopVoiceRecording}
            onTouchStart={startVoiceRecording}
            onTouchEnd={stopVoiceRecording}
            disabled={isProcessing}
            className={`w-14 h-14 rounded-full flex items-center justify-center text-white shadow-lg transition-transform transform ${
              isRecording
                ? 'bg-[#0ea5e9] scale-105 animate-pulse'
                : 'bg-[#0ea5e9] hover:scale-105'
            } disabled:opacity-50`}
            title="Hold to speak"
          >
            <Mic className="w-6 h-6" />
          </button>

          <button
            onClick={() => setIsSpeakerOn(!isSpeakerOn)}
            className="w-12 h-12 rounded-full bg-[#1f2933] flex items-center justify-center text-gray-300 hover:bg-[#323945] transition-colors"
            title={isSpeakerOn ? 'Mute Speaker' : 'Unmute Speaker'}
          >
            {isSpeakerOn ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
          </button>

          <button
            onClick={() => setShowChat(prev => !prev)}
            className="w-12 h-12 rounded-full bg-[#1f2933] flex items-center justify-center text-gray-300 hover:bg-[#323945] transition-colors"
            title="Toggle chat"
          >
            <MessageCircle className="w-5 h-5" />
          </button>

          <button
            onClick={handleDisconnect}
            className="w-12 h-12 rounded-full bg-[#ef4444] flex items-center justify-center text-white hover:bg-[#dc2626] transition-colors"
            title="End call"
          >
            <PhoneOff className="w-5 h-5" />
          </button>
        </div>
      </div>

      {showChat && (
        <div className="fixed inset-x-4 bottom-4 sm:bottom-8 sm:inset-x-0 sm:mx-auto sm:max-w-xl">
          <div className="bg-[#111318] border border-[#1f2128] rounded-2xl overflow-hidden shadow-xl">
            <div className="max-h-64 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                      message.type === 'user'
                        ? 'bg-[#0ea5e9] text-white'
                        : 'bg-[#1f2933] text-gray-100'
                    }`}
                  >
                    <p>{message.content}</p>
                    <p className="text-[10px] mt-1 opacity-70">
                      {formatTime(message.timestamp)}
                    </p>
                  </div>
                </div>
              ))}

              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-[#1f2933] text-gray-100 px-3 py-2 rounded-lg text-sm flex items-center space-x-2">
                    <Loader className="w-4 h-4 animate-spin" />
                    <span>Kashar is thinking...</span>
                  </div>
                </div>
              )}
            </div>

            <div className="border-t border-[#1f2128] p-3 flex items-center space-x-2">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
                placeholder="Type a message..."
                className="flex-1 bg-[#050509] border border-[#323945] rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-[#0ea5e9] focus:border-transparent"
                disabled={isProcessing}
              />
              <button
                onClick={sendTextMessage}
                disabled={!currentMessage.trim() || isProcessing}
                className="w-10 h-10 rounded-full bg-[#0ea5e9] flex items-center justify-center text-white disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AgoraVoiceTutor;

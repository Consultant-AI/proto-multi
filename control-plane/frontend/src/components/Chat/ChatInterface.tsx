import React, { useState, useEffect, useRef, useCallback, lazy, Suspense } from 'react';
import { checkWebGLSupport } from '../Avatar';

// Lazy load the avatar component - only loads when avatar is enabled
const TalkingAvatar = lazy(() => import('../Avatar/TalkingAvatar'));

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  instanceId: string;
  instanceStatus?: string;
  showHeader?: boolean;
}

// Generate unique IDs
const generateId = () => Math.random().toString(36).substring(2, 15);

// Icons
const SettingsIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const PlusIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
  </svg>
);

const SendIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
  </svg>
);

const MicIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
  </svg>
);

const AttachmentIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
  </svg>
);

const CameraIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const SpeakerIcon: React.FC<{ className?: string; muted?: boolean }> = ({ className, muted }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    {muted ? (
      <>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
      </>
    ) : (
      <>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
      </>
    )}
  </svg>
);

// Status dot component
const StatusDot: React.FC<{ status: 'connected' | 'connecting' | 'error' | 'disconnected' }> = ({ status }) => {
  const colors = {
    connected: 'bg-green-500',
    connecting: 'bg-yellow-500 animate-pulse',
    error: 'bg-red-500',
    disconnected: 'bg-gray-500',
  };
  return <span className={`w-2 h-2 rounded-full ${colors[status]}`} />;
};

const ChatInterface: React.FC<ChatInterfaceProps> = ({ instanceId, instanceStatus, showHeader = true }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<string>('Connecting...');
  const [retryCount, setRetryCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const sessionKeyRef = useRef(`web-${instanceId}-${generateId()}`);
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const mountedRef = useRef(false); // Track if we've already connected for this instance
  const connectionIdRef = useRef(0); // Unique ID for each connection attempt

  // Avatar state
  const [avatarEnabled, setAvatarEnabled] = useState(() => {
    // Check if WebGL is supported and user preference
    const saved = localStorage.getItem('cloudbot-avatar-enabled');
    return saved !== null ? saved === 'true' : checkWebGLSupport();
  });
  const [currentSpeech, setCurrentSpeech] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [avatarLoaded, setAvatarLoaded] = useState(false);
  const [avatarCharacter, setAvatarCharacter] = useState(() => {
    return localStorage.getItem('cloudbot-avatar-character') || 'brunette';
  });

  // Auto-speak state (TTS for AI responses)
  const [autoSpeak, setAutoSpeak] = useState(() => {
    const saved = localStorage.getItem('cloudbot-auto-speak');
    return saved !== null ? saved === 'true' : true; // Default to enabled
  });
  const speechSynthRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Voice input state (speech-to-text)
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [audioLevels, setAudioLevels] = useState<number[]>(new Array(20).fill(0));
  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const silenceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const transcriptRef = useRef<string>(''); // Track latest transcript for auto-send
  const isRecordingRef = useRef<boolean>(false); // Track recording state for callbacks
  const connectedRef = useRef<boolean>(false); // Track connection state for callbacks

  // Keep connectedRef in sync with connected state
  useEffect(() => {
    connectedRef.current = connected;
  }, [connected]);

  // Save avatar preference
  useEffect(() => {
    localStorage.setItem('cloudbot-avatar-enabled', avatarEnabled.toString());
  }, [avatarEnabled]);

  // Save avatar character preference
  useEffect(() => {
    localStorage.setItem('cloudbot-avatar-character', avatarCharacter);
  }, [avatarCharacter]);

  // Save auto-speak preference
  useEffect(() => {
    localStorage.setItem('cloudbot-auto-speak', autoSpeak.toString());
  }, [autoSpeak]);

  // Fallback browser TTS when avatar is not available
  const speakWithBrowserTTS = useCallback((text: string) => {
    if (!autoSpeak || !('speechSynthesis' in window)) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.15; // Slightly faster for snappier response
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Try to find a good English voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v =>
      v.name.includes('Google US English') ||
      v.name.includes('Samantha') ||
      (v.lang.startsWith('en') && v.localService)
    ) || voices.find(v => v.lang.startsWith('en'));

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onend = () => {
      setIsSpeaking(false);
      speechSynthRef.current = null;
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      speechSynthRef.current = null;
    };

    speechSynthRef.current = utterance;
    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  }, [autoSpeak]);

  // Stop browser TTS (kept for potential future use)
  const _stopBrowserTTS = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
    speechSynthRef.current = null;
  }, []);
  void _stopBrowserTTS; // Suppress unused warning

  // Trigger avatar speech when new assistant message arrives
  const handleAvatarSpeak = useCallback((text: string) => {
    if (!autoSpeak || !text) return;

    console.log('handleAvatarSpeak called:', { avatarEnabled, avatarLoaded, textLength: text.length });

    if (avatarEnabled) {
      // Always use avatar when enabled - it handles its own TTS
      console.log('Using avatar for speech');
      setCurrentSpeech(text);
      setIsSpeaking(true);
    } else {
      // Fallback to browser TTS only when avatar is disabled
      console.log('Avatar disabled, using browser TTS');
      speakWithBrowserTTS(text);
    }
  }, [avatarEnabled, autoSpeak, speakWithBrowserTTS]);

  const handleSpeakingEnd = useCallback(() => {
    setIsSpeaking(false);
    setCurrentSpeech(null);
    // Don't call _stopBrowserTTS here - the avatar handles its own TTS cleanup
    // _stopBrowserTTS() would cancel any ongoing speech prematurely
  }, []);

  // Track when avatar loads successfully
  const handleAvatarLoaded = useCallback(() => {
    setAvatarLoaded(true);
  }, []);

  // Track when avatar fails to load
  const handleAvatarError = useCallback(() => {
    setAvatarLoaded(false);
  }, []);

  // Voice recording functions
  // Helper to send voice message (uses same format as handleSend)
  const sendVoiceMessage = useCallback((text: string) => {
    console.log('sendVoiceMessage called:', { text, connected: connectedRef.current });

    if (!text.trim()) return;
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    if (!connectedRef.current) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    // Use same format as handleSend
    const requestId = generateId();
    const request = {
      type: 'req',
      id: requestId,
      method: 'chat.send',
      params: {
        sessionKey: sessionKeyRef.current,
        message: text.trim(),
        idempotencyKey: requestId,
      },
    };

    console.log('sendVoiceMessage: sending request:', request);
    wsRef.current.send(JSON.stringify(request));
  }, []);

  const startRecording = useCallback(async () => {
    try {
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      // Set up audio analyzer for visualizer
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 64;
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);

      // Mark as recording
      isRecordingRef.current = true;
      setIsRecording(true);
      setTranscript('');
      transcriptRef.current = '';

      // Update audio levels for visualizer
      const updateLevels = () => {
        if (!analyserRef.current || !isRecordingRef.current) return;
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);
        const levels = Array.from(dataArray.slice(0, 20)).map(v => v / 255);
        setAudioLevels(levels);
        animationFrameRef.current = requestAnimationFrame(updateLevels);
      };

      // Set up speech recognition
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (!SpeechRecognition) {
        throw new Error('Speech recognition not supported');
      }

      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += result;
          } else {
            interimTranscript += result;
          }
        }

        const currentText = finalTranscript || interimTranscript;
        setTranscript(currentText);
        transcriptRef.current = currentText;

        // Reset silence timeout on speech
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
        }

        // Auto-send after 2 seconds of silence when we have final text
        if (finalTranscript.trim()) {
          silenceTimeoutRef.current = setTimeout(() => {
            console.log('Auto-sending after silence:', finalTranscript.trim());
            // Stop everything
            if (recognitionRef.current) {
              recognitionRef.current.stop();
              recognitionRef.current = null;
            }
            if (mediaStreamRef.current) {
              mediaStreamRef.current.getTracks().forEach(track => track.stop());
              mediaStreamRef.current = null;
            }
            if (audioContextRef.current) {
              audioContextRef.current.close();
              audioContextRef.current = null;
            }
            if (animationFrameRef.current) {
              cancelAnimationFrame(animationFrameRef.current);
              animationFrameRef.current = null;
            }
            isRecordingRef.current = false;
            setIsRecording(false);
            setAudioLevels(new Array(20).fill(0));
            setTranscript('');
            transcriptRef.current = '';
            // Send the message
            sendVoiceMessage(finalTranscript.trim());
          }, 2000);
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        cancelRecording();
      };

      recognition.onend = () => {
        // Restart if still recording
        if (isRecordingRef.current && recognitionRef.current) {
          try {
            recognitionRef.current.start();
          } catch (e) {
            // Already started or stopped
          }
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
      updateLevels();

    } catch (err) {
      console.error('Failed to start recording:', err);
      alert('Could not access microphone. Please allow microphone access.');
    }
  }, [sendVoiceMessage]);

  const stopRecording = useCallback((finalText?: string) => {
    // Use provided text, or ref (most recent), or state as fallback
    const textToSend = finalText || transcriptRef.current || transcript;

    // Clear silence timeout first
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }

    // Stop recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }

    // Stop audio
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    // Stop audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Stop animation
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    isRecordingRef.current = false;
    setIsRecording(false);
    setAudioLevels(new Array(20).fill(0));
    setTranscript('');
    transcriptRef.current = '';

    // Send the message if there's text
    if (textToSend.trim()) {
      sendVoiceMessage(textToSend.trim());
    }
  }, [transcript, sendVoiceMessage]);

  const cancelRecording = useCallback(() => {
    // Clear silence timeout first
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }

    // Stop recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }

    // Stop audio
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    // Stop audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Stop animation
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    isRecordingRef.current = false;
    transcriptRef.current = '';
    setIsRecording(false);
    setTranscript('');
    setAudioLevels(new Array(20).fill(0));
  }, []);

  // Cleanup recording on unmount
  useEffect(() => {
    return () => {
      cancelRecording();
    };
  }, [cancelRecording]);

  // Retry configuration
  const MAX_RETRIES = 15;
  const RETRY_DELAYS = [2000, 3000, 5000, 8000, 10000]; // ms

  // Derive status type from connectionStatus
  const getStatusType = (): 'connected' | 'connecting' | 'error' | 'disconnected' => {
    if (connected) return 'connected';
    if (connectionStatus.startsWith('Error') || connectionStatus.includes('not available')) return 'error';
    if (connectionStatus === 'Disconnected') return 'disconnected';
    return 'connecting';
  };

  // Reset when instanceId changes
  useEffect(() => {
    setRetryCount(0);
    setConnected(false);
    setMessages([]);
    mountedRef.current = false;
    // connectionIdRef is incremented in the main effect
  }, [instanceId]);

  // Main WebSocket connection effect
  useEffect(() => {
    // Don't connect if instance isn't running
    if (instanceStatus && instanceStatus !== 'running') {
      setConnectionStatus('Instance is starting up...');
      setConnected(false);
      return;
    }

    // Clear any pending retry
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }

    // Max retries reached
    if (retryCount >= MAX_RETRIES) {
      setConnectionStatus('Connection failed. Please refresh to try again.');
      return;
    }

    // Increment and track this connection attempt
    connectionIdRef.current += 1;
    const thisConnectionId = connectionIdRef.current;

    // If already connected with an active WebSocket, skip
    // (This handles StrictMode double-invoke and polling re-renders)
    if (mountedRef.current && wsRef.current) {
      const state = wsRef.current.readyState;
      if (state === WebSocket.OPEN || state === WebSocket.CONNECTING) {
        return;
      }
    }

    const token = localStorage.getItem('access_token') || '';
    const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';

    if (retryCount > 0) {
      setConnectionStatus(`Reconnecting... (attempt ${retryCount + 1})`);
    } else {
      setConnectionStatus('Connecting to CloudBot...');
    }

    // Close existing connection if any (shouldn't happen due to check above, but be safe)
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const websocket = new WebSocket(`${WS_BASE_URL}/api/instances/${instanceId}/cloudbot?token=${token}`);
    wsRef.current = websocket;
    mountedRef.current = true;

    websocket.onopen = () => {
      console.log('CloudBot WebSocket opened, waiting for connect.challenge...');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('CloudBot message:', data);

        // Handle status events from the proxy
        if (data.type === 'event' && data.event === 'status') {
          const { status, message } = data.payload;
          console.log('Status update:', status, message);
          setConnectionStatus(message);
          if (status === 'error') {
            setConnected(false);
          }
          return;
        }

        // Handle connect.challenge event - send connect request
        if (data.type === 'event' && data.event === 'connect.challenge') {
          console.log('Received connect.challenge, sending connect request...');
          setConnectionStatus('Authenticating...');

          const connectRequest = {
            type: 'req',
            id: generateId(),
            method: 'connect',
            params: {
              minProtocol: 3,
              maxProtocol: 3,
              client: {
                id: 'openclaw-control-ui',
                displayName: 'CloudBot Web',
                version: '1.0.0',
                platform: 'web',
                mode: 'ui',
              },
              auth: {
                password: 'cloudbot-gateway-secret',
              },
            },
          };
          websocket.send(JSON.stringify(connectRequest));
          return;
        }

        // Handle response frames
        if (data.type === 'res') {
          if (data.ok && data.payload?.type === 'hello-ok') {
            console.log('CloudBot handshake complete', data.payload);
            setConnected(true);
            setConnectionStatus('Ready');
            setRetryCount(0); // Reset retry count on successful connection

            // Add welcome message on first connection
            if (messages.length === 0) {
              setMessages([{
                id: 'welcome',
                role: 'system',
                content: 'CloudBot is ready! You can ask me to control the desktop, browse the web, or help with any task.',
                timestamp: new Date(),
              }]);
            }

            setTimeout(() => inputRef.current?.focus(), 100);
            return;
          }

          if (!data.ok && data.error) {
            console.error('Connection failed:', data.error);
            setConnectionStatus(`Error: ${data.error.message || 'Connection failed'}`);
            return;
          }

          if (data.ok && data.payload?.status === 'started') {
            console.log('Chat request started:', data.payload.runId);
          } else if (!data.ok) {
            console.error('Request failed:', data.error);
            setLoading(false);
          }
          return;
        }

        // Handle chat responses
        if (data.type === 'event' && data.event === 'chat') {
          const payload = data.payload;

          if (payload.state === 'final' && payload.message) {
            let content = '';
            if (Array.isArray(payload.message.content)) {
              content = payload.message.content
                .filter((c: any) => c.type === 'text')
                .map((c: any) => c.text)
                .join('\n');
            } else if (typeof payload.message.content === 'string') {
              content = payload.message.content;
            }

            if (content) {
              setMessages((prev) => [
                ...prev,
                {
                  id: payload.runId || Date.now().toString(),
                  role: 'assistant',
                  content,
                  timestamp: new Date(),
                },
              ]);
              // Trigger avatar to speak the response
              handleAvatarSpeak(content);
            }
            setLoading(false);
          } else if (payload.state === 'error') {
            console.error('Chat error:', payload.errorMessage);
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                role: 'assistant',
                content: `Error: ${payload.errorMessage || 'Unknown error'}`,
                timestamp: new Date(),
              },
            ]);
            setLoading(false);
          }
          return;
        }

        // Handle agent events
        if (data.type === 'event' && data.event === 'agent') {
          console.log('Agent event:', data.payload);
          return;
        }

        // Ignore tick events
        if (data.type === 'event' && data.event === 'tick') {
          return;
        }

      } catch (error) {
        console.error('Failed to parse CloudBot message:', error);
      }
    };

    websocket.onerror = (error) => {
      console.error('CloudBot WebSocket error:', error);
      setLoading(false);
      setConnected(false);
    };

    websocket.onclose = (event) => {
      console.log('CloudBot WebSocket disconnected', event.code, event.reason);
      setLoading(false);
      setConnected(false);

      // Schedule retry if not at max retries and instance is still running
      if (retryCount < MAX_RETRIES && (!instanceStatus || instanceStatus === 'running')) {
        const delay = RETRY_DELAYS[Math.min(retryCount, RETRY_DELAYS.length - 1)];
        setConnectionStatus(`CloudBot not ready, retrying in ${delay / 1000}s...`);
        retryTimeoutRef.current = setTimeout(() => {
          setRetryCount((prev) => prev + 1);
        }, delay);
      } else if (!event.reason?.includes('timeout')) {
        setConnectionStatus(event.reason || 'Disconnected');
      }
    };

    return () => {
      // Only cleanup if this is still the current connection
      // (Prevents StrictMode from closing our active connection)
      if (connectionIdRef.current !== thisConnectionId) {
        return; // A newer connection has been created, don't close
      }

      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
      if (wsRef.current === websocket) {
        wsRef.current = null;
        mountedRef.current = false;
      }
      websocket.close();
    };
  }, [instanceId, retryCount]); // instanceStatus handled separately to avoid unnecessary reconnects

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN || !connected) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageText = input;
    setInput('');
    setLoading(true);

    const requestId = generateId();
    const request = {
      type: 'req',
      id: requestId,
      method: 'chat.send',
      params: {
        sessionKey: sessionKeyRef.current,
        message: messageText,
        idempotencyKey: requestId,
      },
    };

    console.log('Sending chat request:', request);
    wsRef.current.send(JSON.stringify(request));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    sessionKeyRef.current = `web-${instanceId}-${generateId()}`;
  };

  const statusType = getStatusType();

  return (
    <div className="h-full flex flex-col bg-theme-primary text-theme-primary">
      {/* Header - only shown if showHeader is true */}
      {showHeader && (
        <div className="flex items-center justify-between px-4 py-2 border-b border-theme bg-theme-nav">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-theme-primary">New conversation</span>
            <div className="flex items-center gap-1">
              <StatusDot status={statusType} />
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => setAutoSpeak(!autoSpeak)}
              className={`p-1.5 rounded hover:bg-theme-hover transition-colors ${
                autoSpeak ? 'text-blue-500' : 'text-theme-muted hover:text-theme-primary'
              }`}
              aria-label={autoSpeak ? 'Disable auto-speak' : 'Enable auto-speak'}
              title={autoSpeak ? 'Auto-speak enabled' : 'Auto-speak disabled'}
            >
              <SpeakerIcon className="w-4 h-4" muted={!autoSpeak} />
            </button>
            <button
              type="button"
              className="p-1.5 rounded hover:bg-theme-hover text-theme-muted hover:text-theme-primary transition-colors"
              aria-label="Settings"
            >
              <SettingsIcon className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleNewConversation}
              className="p-1.5 rounded hover:bg-theme-hover text-theme-muted hover:text-theme-primary transition-colors"
              aria-label="New conversation"
            >
              <PlusIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Avatar Section - lazy loaded */}
      {avatarEnabled && connected && (
        <div className="border-b border-theme bg-theme-tertiary/30">
          <div className="relative">
            <Suspense fallback={
              <div className="flex items-center justify-center bg-gradient-to-b from-purple-500/20 to-pink-500/20 rounded-lg" style={{ height: 200 }}>
                <div className="text-center">
                  <div className="w-10 h-10 border-4 border-purple-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                  <p className="text-sm text-white/80">Loading avatar...</p>
                </div>
              </div>
            }>
              <TalkingAvatar
                text={currentSpeech}
                isSpeaking={isSpeaking}
                onSpeakingEnd={handleSpeakingEnd}
                onLoaded={handleAvatarLoaded}
                onError={handleAvatarError}
                height={200}
                enabled={avatarEnabled}
                characterId={avatarCharacter}
                onCharacterChange={setAvatarCharacter}
                showCharacterSelector={true}
              />
            </Suspense>
            {/* Avatar toggle button */}
            <button
              type="button"
              onClick={() => setAvatarEnabled(false)}
              className="absolute top-2 right-2 p-1 rounded bg-black/30 hover:bg-black/50 text-white/70 hover:text-white transition-colors"
              aria-label="Hide avatar"
              title="Hide avatar"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Show avatar button when disabled */}
      {!avatarEnabled && connected && (
        <button
          type="button"
          onClick={() => setAvatarEnabled(true)}
          className="w-full py-2 text-xs text-theme-muted hover:text-theme-primary hover:bg-theme-hover border-b border-theme transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          Show Avatar
        </button>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-6">
            {instanceStatus && instanceStatus !== 'running' ? (
              // Instance is still launching
              <div className="mb-6">
                <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-theme-tertiary flex items-center justify-center">
                  <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                </div>
                <h2 className="text-base font-medium text-theme-primary mb-2">
                  Setting up your CloudBot
                </h2>
                <p className="text-sm text-theme-muted">
                  This usually takes 5-10 minutes. The AI will be ready soon.
                </p>
              </div>
            ) : !connected ? (
              // Instance running but not connected yet
              <div className="mb-6">
                <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-theme-tertiary flex items-center justify-center">
                  <div className="w-6 h-6 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" />
                </div>
                <h2 className="text-base font-medium text-theme-primary mb-2">
                  Connecting to CloudBot...
                </h2>
                <p className="text-sm text-theme-muted">
                  {connectionStatus}
                </p>
              </div>
            ) : (
              // Connected - show suggestions
              <>
                <div className="mb-6">
                  <h2 className="text-base font-medium text-theme-primary mb-2">
                    Ask to do anything
                  </h2>
                  <p className="text-sm text-theme-muted">
                    Control the desktop, open apps, or browse the web
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 justify-center">
                  {['Open Chrome', 'Create a file', 'Take screenshot'].map((suggestion) => (
                    <button
                      type="button"
                      key={suggestion}
                      onClick={() => {
                        setInput(suggestion);
                        inputRef.current?.focus();
                      }}
                      className="px-3 py-1.5 text-xs bg-theme-tertiary hover:bg-theme-hover text-theme-secondary rounded-lg transition-colors border border-theme"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-theme-tertiary text-theme-primary'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  <p className={`text-[10px] mt-1.5 text-right ${
                    message.role === 'user' ? 'opacity-70' : 'text-theme-muted'
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-theme-tertiary rounded-2xl px-4 py-3 min-w-[80px]">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      <span className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                      <span className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                      <span className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce" />
                    </div>
                    <span className="text-xs text-theme-muted animate-pulse">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area - WhatsApp style */}
      <div className="px-2 py-2 bg-theme-primary">
        {isRecording ? (
          /* Recording UI */
          <div className="flex items-center gap-2">
            <div className="flex-1 flex items-center gap-3 bg-theme-secondary dark:bg-gray-700 rounded-full px-4 py-2">
              {/* Delete/Cancel button */}
              <button
                type="button"
                onClick={cancelRecording}
                className="p-1 text-red-400 hover:text-red-300 transition-colors"
                aria-label="Cancel recording"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>

              {/* Recording indicator */}
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />

              {/* Audio visualizer */}
              <div className="flex-1 flex items-center justify-center gap-[2px] h-6">
                {audioLevels.map((level, i) => (
                  <div
                    key={i}
                    className="w-1 bg-blue-500 rounded-full transition-all duration-75"
                    style={{
                      height: `${Math.max(3, level * 20)}px`,
                      opacity: 0.5 + level * 0.5,
                    }}
                  />
                ))}
              </div>

              {/* Transcript preview */}
              {transcript && (
                <div className="max-w-[100px] truncate text-xs text-theme-muted">
                  {transcript}
                </div>
              )}
            </div>

            {/* Stop/Send button */}
            <button
              type="button"
              onClick={() => stopRecording()}
              className="w-12 h-12 flex items-center justify-center bg-blue-500 hover:bg-blue-600 text-white rounded-full transition-colors shadow-lg flex-shrink-0"
              aria-label="Stop and send"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 6h12v12H6z" />
              </svg>
            </button>
          </div>
        ) : (
          /* Normal input UI - WhatsApp style */
          <div className="flex items-center gap-2">
            {/* Input field with icons */}
            <div className="flex-1 flex items-center bg-theme-secondary dark:bg-gray-700 rounded-full px-4 py-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={connected ? "Message" : connectionStatus}
                disabled={loading || !connected}
                className="flex-1 bg-transparent text-sm text-theme-primary placeholder-theme-muted focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed min-w-0"
              />
              <div className="flex items-center gap-1 ml-2 flex-shrink-0">
                <button
                  type="button"
                  disabled={!connected}
                  className="p-1.5 text-theme-muted hover:text-theme-primary disabled:opacity-30 transition-colors"
                  aria-label="Attach file"
                >
                  <AttachmentIcon className="w-5 h-5" />
                </button>
                <button
                  type="button"
                  disabled={!connected}
                  className="p-1.5 text-theme-muted hover:text-theme-primary disabled:opacity-30 transition-colors"
                  aria-label="Camera"
                >
                  <CameraIcon className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Mic or Send button */}
            {input.trim() ? (
              <button
                type="button"
                onClick={handleSend}
                disabled={loading || !connected}
                aria-label="Send message"
                className="w-12 h-12 flex items-center justify-center bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-full transition-colors shadow-lg flex-shrink-0"
              >
                <SendIcon className="w-5 h-5" />
              </button>
            ) : (
              <button
                type="button"
                onClick={startRecording}
                disabled={!connected || loading}
                className="w-12 h-12 flex items-center justify-center bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white rounded-full transition-colors shadow-lg flex-shrink-0"
                aria-label="Voice input"
              >
                <MicIcon className="w-6 h-6" />
              </button>
            )}
          </div>
        )}
        {statusType === 'error' && (
          <p className="mt-2 text-xs text-red-500 text-center">
            {connectionStatus}
          </p>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;

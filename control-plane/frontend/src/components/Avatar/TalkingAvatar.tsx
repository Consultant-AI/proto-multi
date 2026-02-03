import React, { useEffect, useRef, useState } from 'react';

declare global {
  interface Window {
    TalkingHead?: any;
    HeadTTS?: any;
  }
}

export interface AvatarCharacter {
  id: string;
  name: string;
  url: string;
  body: 'M' | 'F';
  voice: string;
}

export interface AvatarBackground {
  id: string;
  name: string;
  type: 'color' | 'gradient' | 'image';
  value: string; // CSS color/gradient or image URL
}

export const AVATAR_BACKGROUNDS: AvatarBackground[] = [
  // Solid colors
  { id: 'black', name: 'Black', type: 'color', value: '#000000' },
  { id: 'dark-gray', name: 'Dark Gray', type: 'color', value: '#1a1a2e' },
  { id: 'navy', name: 'Navy', type: 'color', value: '#0f0f23' },
  { id: 'purple', name: 'Purple', type: 'color', value: '#2d1b4e' },
  // Gradients
  { id: 'sunset', name: 'Sunset', type: 'gradient', value: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { id: 'ocean', name: 'Ocean', type: 'gradient', value: 'linear-gradient(135deg, #1a365d 0%, #2a4365 50%, #1a365d 100%)' },
  { id: 'forest', name: 'Forest', type: 'gradient', value: 'linear-gradient(135deg, #134e5e 0%, #71b280 100%)' },
  { id: 'aurora', name: 'Aurora', type: 'gradient', value: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)' },
  // Nature images
  { id: 'mountains', name: 'Mountains', type: 'image', value: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80' },
  { id: 'beach', name: 'Beach', type: 'image', value: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80' },
  { id: 'forest-img', name: 'Forest', type: 'image', value: 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=800&q=80' },
  { id: 'lake', name: 'Lake', type: 'image', value: 'https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=800&q=80' },
  // Home & Indoor
  { id: 'cozy-room', name: 'Cozy Room', type: 'image', value: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&q=80' },
  { id: 'living-room', name: 'Living Room', type: 'image', value: 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80' },
  { id: 'modern-home', name: 'Modern Home', type: 'image', value: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&q=80' },
  { id: 'bedroom', name: 'Bedroom', type: 'image', value: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80' },
  { id: 'kitchen', name: 'Kitchen', type: 'image', value: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80' },
  // Office & Work
  { id: 'office', name: 'Office', type: 'image', value: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80' },
  { id: 'home-office', name: 'Home Office', type: 'image', value: 'https://images.unsplash.com/photo-1593062096033-9a26b09da705?w=800&q=80' },
  { id: 'modern-office', name: 'Modern Office', type: 'image', value: 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=800&q=80' },
  { id: 'library', name: 'Library', type: 'image', value: 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=800&q=80' },
  // Outdoor & Garden
  { id: 'porch-garden', name: 'Porch & Garden', type: 'image', value: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80' },
  { id: 'garden-view', name: 'Garden View', type: 'image', value: 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800&q=80' },
  { id: 'terrace', name: 'Terrace', type: 'image', value: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&q=80' },
  { id: 'balcony-nature', name: 'Balcony Nature', type: 'image', value: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80' },
  { id: 'backyard', name: 'Backyard', type: 'image', value: 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&q=80' },
];

const TALKINGHEAD_CDN = 'https://cdn.jsdelivr.net/gh/met4citizen/TalkingHead@main/avatars';

export const AVATAR_CHARACTERS: AvatarCharacter[] = [
  {
    id: 'brunette',
    name: 'Emma',
    url: `${TALKINGHEAD_CDN}/brunette.glb`,
    body: 'F',
    voice: 'af_bella',
  },
  {
    id: 'avaturn',
    name: 'Mia',
    url: `${TALKINGHEAD_CDN}/avaturn.glb`,
    body: 'F',
    voice: 'af_nicole',
  },
  {
    id: 'james',
    name: 'James',
    url: `${TALKINGHEAD_CDN}/avatarsdk.glb`,
    body: 'M',
    voice: 'am_adam',
  },
];

interface TalkingAvatarProps {
  text?: string | null;
  isSpeaking?: boolean;
  onSpeakingEnd?: () => void;
  onSpeakingStart?: () => void;
  onLoaded?: () => void;
  onError?: (error: string) => void;
  height?: number | string;
  enabled?: boolean;
  characterId?: string;
  onCharacterChange?: (characterId: string) => void;
  backgroundId?: string;
  onBackgroundChange?: (backgroundId: string) => void;
  showCharacterSelector?: boolean;
  /** When false, avatar will animate lips but not play audio */
  audioEnabled?: boolean;
}

const TalkingAvatar: React.FC<TalkingAvatarProps> = ({
  text,
  isSpeaking = false,
  onSpeakingEnd,
  onSpeakingStart,
  onLoaded,
  onError,
  height = 200,
  enabled = true,
  characterId = 'brunette',
  onCharacterChange,
  backgroundId = 'black',
  onBackgroundChange,
  showCharacterSelector = true,
  audioEnabled = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const headRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isActuallySpeaking, setIsActuallySpeaking] = useState(false);
  const [libraryLoaded, setLibraryLoaded] = useState(!!window.TalkingHead);
  const [headTTSLoaded, setHeadTTSLoaded] = useState(!!window.HeadTTS);

  // Debug: log speaking state (prevents unused variable warnings)
  if (isActuallySpeaking && headTTSLoaded) {
    console.debug('Avatar speaking with HeadTTS');
  }
  const headTTSRef = useRef<any>(null);
  const lastTextRef = useRef<string | null>(null);
  const currentCharacterRef = useRef<string>(characterId);
  const [showSettings, setShowSettings] = useState(false);
  const [settingsTab, setSettingsTab] = useState<'avatar' | 'background'>('avatar');

  const currentCharacter = AVATAR_CHARACTERS.find(c => c.id === characterId) || AVATAR_CHARACTERS[0];
  const currentBackground = AVATAR_BACKGROUNDS.find(b => b.id === backgroundId) || AVATAR_BACKGROUNDS[0];

  // Generate background style
  const getBackgroundStyle = (): React.CSSProperties => {
    if (currentBackground.type === 'image') {
      return {
        backgroundImage: `url(${currentBackground.value})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      };
    } else if (currentBackground.type === 'gradient') {
      return {
        background: currentBackground.value,
      };
    } else {
      return {
        backgroundColor: currentBackground.value,
      };
    }
  };

  // Wait for TalkingHead library to load
  useEffect(() => {
    if (window.TalkingHead) {
      setLibraryLoaded(true);
      return;
    }

    const handleLoaded = () => {
      if (window.TalkingHead) {
        setLibraryLoaded(true);
      }
    };
    const handleError = (e: CustomEvent) => {
      setError(`Library failed: ${e.detail}`);
      setIsLoading(false);
    };

    window.addEventListener('talkinghead-loaded', handleLoaded);
    window.addEventListener('talkinghead-error', handleError as EventListener);

    const timeout = setTimeout(() => {
      if (window.TalkingHead) setLibraryLoaded(true);
    }, 5000);

    return () => {
      window.removeEventListener('talkinghead-loaded', handleLoaded);
      window.removeEventListener('talkinghead-error', handleError as EventListener);
      clearTimeout(timeout);
    };
  }, []);

  // Wait for HeadTTS library to load and initialize it
  useEffect(() => {
    if (window.HeadTTS) {
      setHeadTTSLoaded(true);
    }

    const handleLoaded = async () => {
      if (window.HeadTTS) {
        setHeadTTSLoaded(true);
        console.log('=== INITIALIZING HeadTTS ===');

        try {
          const config = (window as any).HeadTTSConfig || {};
          console.log('HeadTTS config:', config);

          // Check WebGPU availability
          const hasWebGPU = !!(navigator as any).gpu;
          console.log('WebGPU available:', hasWebGPU);

          // Check WASM support
          const hasWASM = typeof WebAssembly !== 'undefined';
          console.log('WASM available:', hasWASM);

          if (!hasWebGPU && !hasWASM) {
            console.error('Neither WebGPU nor WASM available - HeadTTS cannot run');
            return;
          }

          console.log('Creating HeadTTS instance...');
          const tts = new window.HeadTTS({
            endpoints: hasWebGPU ? ['webgpu', 'wasm'] : ['wasm'],
            languages: ['en-us'],
            voices: ['af_bella', 'af_nicole', 'am_adam'],
            workerModule: config.workerModule,
            dictionaryURL: config.dictionaryURL,
          });

          console.log('HeadTTS instance created, connecting...');
          await tts.connect();
          console.log('HeadTTS connected!');

          console.log('Setting up voice:', currentCharacter.voice || 'af_bella');
          tts.setup({
            voice: currentCharacter.voice || 'af_bella',
            language: 'en-us',
            speed: 1,
            audioEncoding: 'wav',
          });

          headTTSRef.current = tts;
          console.log('=== HeadTTS READY! Lip sync will work properly ===');
        } catch (err: any) {
          console.error('=== HeadTTS INIT FAILED ===');
          console.error('Error:', err?.message || err);
          console.error('Stack:', err?.stack);
          console.log('Falling back to browser TTS (no lip sync)');
        }
      } else {
        console.log('HeadTTS class not available on window');
      }
    };

    const handleError = (e: CustomEvent) => {
      console.warn('HeadTTS failed to load:', e.detail);
      // Not critical - will fall back to browser TTS
    };

    window.addEventListener('headtts-loaded', handleLoaded);
    window.addEventListener('headtts-error', handleError as EventListener);

    // Check if already loaded
    if (window.HeadTTS && !headTTSRef.current) {
      console.log('HeadTTS already available, initializing...');
      handleLoaded();
    } else if (!window.HeadTTS) {
      console.log('HeadTTS not yet available, waiting for load event...');
      // Also check after a delay in case event was missed
      const checkTimer = setTimeout(() => {
        if (window.HeadTTS && !headTTSRef.current) {
          console.log('HeadTTS became available (delayed check), initializing...');
          handleLoaded();
        }
      }, 3000);
      return () => {
        clearTimeout(checkTimer);
        window.removeEventListener('headtts-loaded', handleLoaded);
        window.removeEventListener('headtts-error', handleError as EventListener);
      };
    }

    return () => {
      window.removeEventListener('headtts-loaded', handleLoaded);
      window.removeEventListener('headtts-error', handleError as EventListener);
    };
  }, [currentCharacter.voice]);


  // Initialize avatar
  useEffect(() => {
    if (!containerRef.current || !enabled || !libraryLoaded || !window.TalkingHead) return;

    const needsReload = currentCharacterRef.current !== characterId || !headRef.current;
    if (!needsReload) return;

    currentCharacterRef.current = characterId;

    const initAvatar = async () => {
      try {
        setIsLoading(true);
        console.log('Initializing avatar:', currentCharacter.name);

        if (headRef.current) {
          try { headRef.current.stop?.(); } catch (e) { /* ignore */ }
        }
        if (containerRef.current) {
          containerRef.current.innerHTML = '';
        }

        const head = new window.TalkingHead(containerRef.current, {
          cameraView: 'head',
          cameraDistance: 0.5,
          cameraY: -0.1,
          cameraRotateX: 0.15,
          cameraRotateY: 0,
          lightAmbientIntensity: 2,
          lightDirectIntensity: 30,
          avatarIdleEyeContact: 1,
        });

        await head.showAvatar({
          url: currentCharacter.url,
          body: currentCharacter.body,
          avatarMood: 'neutral',
          lipsyncLang: 'en',
        });

        // Make the avatar look at the camera
        head.lookAtCamera(1);

        headRef.current = head;
        setIsLoading(false);
        onLoaded?.();
        console.log('Avatar ready:', currentCharacter.name);
        // Log available methods for debugging
        const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(head)).filter(m => typeof head[m] === 'function');
        console.log('TalkingHead methods:', methods);
      } catch (err) {
        console.error('Avatar init error:', err);
        setError(err instanceof Error ? err.message : 'Failed to load');
        setIsLoading(false);
        onError?.(err instanceof Error ? err.message : 'Failed');
      }
    };

    initAvatar();
  }, [enabled, libraryLoaded, characterId, currentCharacter, onLoaded, onError]);

  // Helper to clean and prepare text for TTS
  const cleanTextForSpeech = (text: string): string => {
    return text
      .replace(/\*\*/g, '') // Remove bold markers
      .replace(/\*/g, '')   // Remove italic markers
      .replace(/^[-•]\s*/gm, '') // Remove bullet points
      .replace(/^\d+\.\s*/gm, '') // Remove numbered lists
      .replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F000}-\u{1F02F}]|[\u{1F0A0}-\u{1F0FF}]|[\u{1F100}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]/gu, '') // Remove emojis
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();
  };

  // Shared AudioContext for the component
  const audioContextRef = useRef<AudioContext | null>(null);

  // Unlock audio on first user interaction (browser autoplay policy)
  const audioUnlockedRef = useRef(false);
  useEffect(() => {
    const unlockAudio = async () => {
      if (audioUnlockedRef.current) return;
      audioUnlockedRef.current = true;
      console.log('Unlocking audio...');

      // Create and store AudioContext
      const AudioContextClass = (window as any).AudioContext || (window as any).webkitAudioContext;
      if (AudioContextClass && !audioContextRef.current) {
        const ctx = new AudioContextClass();
        audioContextRef.current = ctx;
        await ctx.resume();
        console.log('AudioContext created and resumed, state:', ctx.state);
      }

      // Play a short silent tone to unlock audio
      if (audioContextRef.current) {
        const oscillator = audioContextRef.current.createOscillator();
        const gain = audioContextRef.current.createGain();
        gain.gain.value = 0.001; // Nearly silent
        oscillator.connect(gain);
        gain.connect(audioContextRef.current.destination);
        oscillator.start();
        oscillator.stop(audioContextRef.current.currentTime + 0.1);
      }

      // Remove listeners after unlocking
      document.removeEventListener('click', unlockAudio);
      document.removeEventListener('touchstart', unlockAudio);
      document.removeEventListener('keydown', unlockAudio);
    };

    document.addEventListener('click', unlockAudio);
    document.addEventListener('touchstart', unlockAudio);
    document.addEventListener('keydown', unlockAudio);

    return () => {
      document.removeEventListener('click', unlockAudio);
      document.removeEventListener('touchstart', unlockAudio);
      document.removeEventListener('keydown', unlockAudio);
    };
  }, []);

  // Preload voices on component mount
  useEffect(() => {
    if (window.speechSynthesis) {
      // Trigger voice loading
      window.speechSynthesis.getVoices();
      window.speechSynthesis.onvoiceschanged = () => {
        console.log('Voices available:', window.speechSynthesis.getVoices().length);
      };
    }
  }, []);

  // Handle speaking - HeadTTS with lip sync, fallback to speakAudio with word timing
  useEffect(() => {
    if (!headRef.current || !text || !isSpeaking || !enabled) return;
    if (text === lastTextRef.current) return;

    lastTextRef.current = text;
    const cleanText = cleanTextForSpeech(text);
    console.log('Speaking:', cleanText.substring(0, 80) + '...');

    const head = headRef.current;

    // Try HeadTTS first (provides proper neural TTS with lip sync)
    const speakWithHeadTTS = async () => {
      if (!headTTSRef.current) {
        console.log('HeadTTS not available, falling back to speakAudio with browser TTS');
        speakWithBrowserTTS();
        return;
      }

      try {
        console.log('Using HeadTTS for speech with lip sync...');
        setIsActuallySpeaking(true);
        onSpeakingStart?.();

        // Set up message handler for HeadTTS response
        headTTSRef.current.onmessage = (message: any) => {
          if (message.type === 'audio') {
            console.log('HeadTTS audio received, playing with speakAudio...');
            // Pass audio + viseme data to TalkingHead's speakAudio
            head.speakAudio(message.data, { lipsyncLang: 'en' })
              .then(() => {
                console.log('HeadTTS speech completed');
                setIsActuallySpeaking(false);
                onSpeakingEnd?.();
              })
              .catch((err: any) => {
                console.error('speakAudio failed:', err);
                setIsActuallySpeaking(false);
                onSpeakingEnd?.();
              });
          } else if (message.type === 'error') {
            console.error('HeadTTS error:', message.data?.error);
            speakWithBrowserTTS();
          }
        };

        // Synthesize text - result comes via onmessage callback
        headTTSRef.current.synthesize({ input: cleanText });
      } catch (err) {
        console.error('HeadTTS failed:', err);
        speakWithBrowserTTS();
      }
    };

    // Fallback: Use browser TTS for audio + speakAudio with word timing for lip sync
    // This is the CORRECT way to use TalkingHead without external TTS service
    // Fallback: Use browser TTS for audio + TalkingHead's speakAudio for lip sync
    // This is the CORRECT way per TalkingHead documentation
    const speakWithBrowserTTS = async () => {
      console.log('Using browser TTS + speakAudio for lip sync...');

      if (!window.speechSynthesis) {
        console.error('SpeechSynthesis not available');
        onSpeakingEnd?.();
        return;
      }

      window.speechSynthesis.cancel();

      const voices = window.speechSynthesis.getVoices();
      if (voices.length === 0) {
        console.log('Waiting for voices...');
        setTimeout(speakWithBrowserTTS, 100);
        return;
      }

      const voice = voices.find(v => v.name === 'Samantha')
        || voices.find(v => v.name.includes('Google') && v.lang.startsWith('en'))
        || voices.find(v => v.lang === 'en-US')
        || voices.find(v => v.lang.startsWith('en'))
        || voices[0];

      // Convert text to visemes (mouth shapes) for lip sync
      // Oculus viseme IDs: sil, PP, FF, TH, DD, kk, CH, SS, nn, RR, aa, E, I, O, U
      const charToViseme = (char: string): string => {
        const c = char.toLowerCase();
        if ('aáàâä'.includes(c)) return 'aa';
        if ('eéèêë'.includes(c)) return 'E';
        if ('iíìîï'.includes(c)) return 'I';
        if ('oóòôö'.includes(c)) return 'O';
        if ('uúùûü'.includes(c)) return 'U';
        if ('pbm'.includes(c)) return 'PP';
        if ('fv'.includes(c)) return 'FF';
        if ('td'.includes(c)) return 'DD';
        if ('kg'.includes(c)) return 'kk';
        if ('sz'.includes(c)) return 'SS';
        if ('nl'.includes(c)) return 'nn';
        if ('r'.includes(c)) return 'RR';
        if ('jy'.includes(c)) return 'CH';
        if ('wq'.includes(c)) return 'U';
        if ('hx'.includes(c)) return 'SS';
        if ('c'.includes(c)) return 'kk';
        return 'sil'; // silence for spaces, punctuation, etc.
      };

      // Generate viseme sequence from text
      const visemes: string[] = [];
      const vtimes: number[] = [];
      const vdurations: number[] = [];

      // ~60ms per character at normal speech rate
      const msPerChar = 60;
      let currentTime = 0;

      for (const char of cleanText) {
        const viseme = charToViseme(char);
        visemes.push(viseme);
        vtimes.push(currentTime);
        vdurations.push(msPerChar);
        currentTime += msPerChar;
      }

      const totalDuration = currentTime / 1000; // seconds

      // Also create word timing for subtitles
      const words = cleanText.split(/\s+/).filter(w => w.length > 0);
      const avgWordDuration = totalDuration * 1000 / words.length;
      const wtimes = words.map((_, i) => i * avgWordDuration);
      const wdurations = words.map(() => avgWordDuration);

      console.log('Browser TTS with voice:', voice?.name);
      console.log('Generated', visemes.length, 'visemes, duration:', totalDuration.toFixed(1) + 's');

      // Create an AudioBuffer using Web Audio API for TalkingHead
      // TalkingHead's playAudio expects an AudioBuffer, not a WAV ArrayBuffer
      const AudioContextClass = (window as any).AudioContext || (window as any).webkitAudioContext;
      const audioCtx = audioContextRef.current || new AudioContextClass();
      if (audioCtx.state === 'suspended') {
        await audioCtx.resume();
      }

      const sampleRate = 22050;
      const numSamples = Math.floor(totalDuration * sampleRate);
      // Create a valid AudioBuffer with near-silent audio (tiny noise to pass validation)
      const audioBuffer = audioCtx.createBuffer(1, Math.max(numSamples, sampleRate), sampleRate);
      const channelData = audioBuffer.getChannelData(0);
      // Fill with very quiet noise (nearly inaudible but valid audio)
      for (let i = 0; i < channelData.length; i++) {
        channelData[i] = (Math.random() - 0.5) * 0.001; // Very quiet random noise
      }

      console.log('Created AudioBuffer:', audioBuffer.duration.toFixed(1) + 's');

      setIsActuallySpeaking(true);
      onSpeakingStart?.();

      // Only play browser TTS audio if audioEnabled is true
      // Lip sync animation will still run regardless
      let keepAlive: ReturnType<typeof setInterval> | null = null;
      if (audioEnabled) {
        // Start browser TTS for actual audio
        const utterance = new SpeechSynthesisUtterance(cleanText);
        if (voice) utterance.voice = voice;
        utterance.rate = 1;
        utterance.pitch = 1;
        utterance.volume = 1;

        utterance.onend = () => {
          console.log('>>> Browser TTS ENDED');
          setIsActuallySpeaking(false);
          onSpeakingEnd?.();
        };

        utterance.onerror = (e) => {
          console.error('>>> Browser TTS ERROR:', e.error);
          setIsActuallySpeaking(false);
          onSpeakingEnd?.();
        };

        // Start browser TTS
        window.speechSynthesis.speak(utterance);

        // Chrome workaround: keep speech alive for long texts
        keepAlive = setInterval(() => {
          if (window.speechSynthesis.speaking) {
            window.speechSynthesis.pause();
            window.speechSynthesis.resume();
          } else {
            if (keepAlive) clearInterval(keepAlive);
          }
        }, 10000);
      } else {
        // Audio disabled - just run lip sync animation, end after duration
        console.log('Audio disabled, running lip sync only');
        setTimeout(() => {
          setIsActuallySpeaking(false);
          onSpeakingEnd?.();
        }, totalDuration * 1000);
      }

      // Use TalkingHead's speakAudio with viseme data for lip sync
      try {
        // Ensure animation loop is running (fixes second message issue)
        try { head.start?.(); } catch { /* ignore */ }

        console.log('Starting speakAudio for lip sync with', visemes.length, 'visemes...');
        head.speakAudio({
          audio: audioBuffer,
          words: words,
          wtimes: wtimes,
          wdurations: wdurations,
          visemes: visemes,
          vtimes: vtimes,
          vdurations: vdurations,
          markers: [],
          mtimes: []
        }, {
          lipsyncLang: 'en'
        });
        console.log('speakAudio started');
      } catch (err) {
        console.error('speakAudio failed:', err);
      }

      // Cleanup
      void keepAlive;
    };

    // Start speaking
    speakWithHeadTTS();

  }, [text, isSpeaking, enabled, audioEnabled, onSpeakingStart, onSpeakingEnd]);

  // Stop speaking only when explicitly requested (isSpeaking goes from true to false)
  const prevIsSpeakingRef = useRef(isSpeaking);
  useEffect(() => {
    // Only cancel if isSpeaking changed from true to false (user requested stop)
    if (prevIsSpeakingRef.current && !isSpeaking) {
      console.log('User requested stop speaking');
      window.speechSynthesis?.cancel();
      headRef.current?.stop?.();
      setIsActuallySpeaking(false);
    }
    prevIsSpeakingRef.current = isSpeaking;
  }, [isSpeaking]);

  // Stop audio (but not lip sync) when audioEnabled is toggled off mid-speech
  const prevAudioEnabledRef = useRef(audioEnabled);
  useEffect(() => {
    // If audio was just disabled while speaking, cancel the TTS audio
    // but let the lip sync animation continue
    if (prevAudioEnabledRef.current && !audioEnabled) {
      console.log('Audio disabled mid-speech, stopping TTS but keeping lip sync');
      window.speechSynthesis?.cancel();
    }
    prevAudioEnabledRef.current = audioEnabled;
  }, [audioEnabled]);

  // Reset lastTextRef when text changes to null (ready for new speech)
  useEffect(() => {
    if (!text) {
      lastTextRef.current = null;
    }
  }, [text]);

  // Cleanup
  useEffect(() => {
    return () => {
      window.speechSynthesis?.cancel();
    };
  }, []);

  if (!enabled) return null;

  return (
    <div className="relative" style={{ height, ...getBackgroundStyle() }}>
      {/* Loading states */}
      {!libraryLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg">
          <div className="text-center">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-white/80">Loading libraries...</p>
          </div>
        </div>
      )}

      {libraryLoaded && isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg">
          <div className="text-center">
            <div className="w-10 h-10 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-white/80">Loading avatar...</p>
          </div>
        </div>
      )}

      {error && !isLoading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/50 rounded-lg p-4">
          <p className="text-sm text-red-400 mb-3">{error}</p>
          <button
            type="button"
            onClick={() => {
              setError(null);
              setIsLoading(true);
              currentCharacterRef.current = '';
            }}
            className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
          >
            Retry
          </button>
        </div>
      )}

      <div
        ref={containerRef}
        className="w-full h-full rounded-lg overflow-hidden"
        style={{ opacity: isLoading || error ? 0 : 1 }}
      />

      {/* Settings button - portrait icon (person with background frame) */}
      {showCharacterSelector && !isLoading && !error && (
        <button
          type="button"
          onClick={() => setShowSettings(!showSettings)}
          className="absolute top-10 right-2 p-1 rounded bg-black/30 hover:bg-black/50 text-white/70 hover:text-white transition-colors"
          title="Avatar settings"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            {/* Background frame */}
            <rect x="3" y="3" width="18" height="18" rx="2" strokeLinecap="round" strokeLinejoin="round" />
            {/* Person silhouette */}
            <circle cx="12" cy="9" r="3" strokeLinecap="round" strokeLinejoin="round" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M7 21v-1a5 5 0 0110 0v1" />
          </svg>
        </button>
      )}

      {/* Unified settings dropdown */}
      {showSettings && (
        <div className="absolute top-16 right-2 bg-gray-900/95 rounded-lg shadow-xl border border-gray-700 min-w-[160px] max-h-[280px] overflow-hidden flex flex-col">
          {/* Tabs */}
          <div className="flex border-b border-gray-700">
            <button
              type="button"
              onClick={() => setSettingsTab('avatar')}
              className={`flex-1 px-3 py-2 text-xs font-medium transition-colors ${
                settingsTab === 'avatar'
                  ? 'text-white bg-gray-800'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Avatar
            </button>
            <button
              type="button"
              onClick={() => setSettingsTab('background')}
              className={`flex-1 px-3 py-2 text-xs font-medium transition-colors ${
                settingsTab === 'background'
                  ? 'text-white bg-gray-800'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Background
            </button>
          </div>

          {/* Content */}
          <div className="p-2 overflow-y-auto">
            {settingsTab === 'avatar' ? (
              /* Avatar selector */
              <div className="space-y-1">
                {AVATAR_CHARACTERS.map((char) => (
                  <button
                    key={char.id}
                    type="button"
                    onClick={() => {
                      onCharacterChange?.(char.id);
                      setShowSettings(false);
                    }}
                    className={`w-full text-left px-2 py-1.5 rounded text-sm transition-colors ${
                      char.id === characterId
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {char.name}
                  </button>
                ))}
              </div>
            ) : (
              /* Background selector */
              <div>
                {/* Colors section */}
                <p className="text-[10px] text-gray-500 px-1 mb-1">Colors</p>
                <div className="flex flex-wrap gap-1 px-1 pb-2">
                  {AVATAR_BACKGROUNDS.filter(b => b.type === 'color').map((bg) => (
                    <button
                      key={bg.id}
                      type="button"
                      onClick={() => {
                        onBackgroundChange?.(bg.id);
                        setShowSettings(false);
                      }}
                      className={`w-6 h-6 rounded border-2 transition-all ${
                        bg.id === backgroundId
                          ? 'border-blue-500 scale-110'
                          : 'border-transparent hover:border-gray-500'
                      }`}
                      style={{ backgroundColor: bg.value }}
                      title={bg.name}
                    />
                  ))}
                </div>

                {/* Gradients section */}
                <p className="text-[10px] text-gray-500 px-1 mb-1">Gradients</p>
                <div className="flex flex-wrap gap-1 px-1 pb-2">
                  {AVATAR_BACKGROUNDS.filter(b => b.type === 'gradient').map((bg) => (
                    <button
                      key={bg.id}
                      type="button"
                      onClick={() => {
                        onBackgroundChange?.(bg.id);
                        setShowSettings(false);
                      }}
                      className={`w-6 h-6 rounded border-2 transition-all ${
                        bg.id === backgroundId
                          ? 'border-blue-500 scale-110'
                          : 'border-transparent hover:border-gray-500'
                      }`}
                      style={{ background: bg.value }}
                      title={bg.name}
                    />
                  ))}
                </div>

                {/* Images section */}
                <p className="text-[10px] text-gray-500 px-1 mb-1">Environments</p>
                <div className="space-y-1">
                  {AVATAR_BACKGROUNDS.filter(b => b.type === 'image').map((bg) => (
                    <button
                      key={bg.id}
                      type="button"
                      onClick={() => {
                        onBackgroundChange?.(bg.id);
                        setShowSettings(false);
                      }}
                      className={`w-full text-left px-2 py-1 rounded text-xs transition-colors flex items-center gap-2 ${
                        bg.id === backgroundId
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-300 hover:bg-gray-700'
                      }`}
                    >
                      <div
                        className="w-8 h-5 rounded bg-cover bg-center flex-shrink-0"
                        style={{ backgroundImage: `url(${bg.value})` }}
                      />
                      {bg.name}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TalkingAvatar;

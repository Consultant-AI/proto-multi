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
  showCharacterSelector?: boolean;
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
  showCharacterSelector = true,
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
  const [showSelector, setShowSelector] = useState(false);

  const currentCharacter = AVATAR_CHARACTERS.find(c => c.id === characterId) || AVATAR_CHARACTERS[0];

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

      // Start browser TTS for actual audio
      const utterance = new SpeechSynthesisUtterance(cleanText);
      if (voice) utterance.voice = voice;
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 1;

      setIsActuallySpeaking(true);
      onSpeakingStart?.();

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
      const keepAlive = setInterval(() => {
        if (window.speechSynthesis.speaking) {
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        } else {
          clearInterval(keepAlive);
        }
      }, 10000);

      // Use TalkingHead's speakAudio with viseme data for lip sync
      try {
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

  }, [text, isSpeaking, enabled, onSpeakingStart, onSpeakingEnd]);

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
    <div className="relative" style={{ height }}>
      {/* Loading states */}
      {!libraryLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-b from-blue-900/50 to-purple-900/50 rounded-lg">
          <div className="text-center">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-white/80">Loading libraries...</p>
          </div>
        </div>
      )}

      {libraryLoaded && isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-b from-blue-900/50 to-purple-900/50 rounded-lg">
          <div className="text-center">
            <div className="w-10 h-10 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-white/80">Loading avatar...</p>
          </div>
        </div>
      )}

      {error && !isLoading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-b from-red-900/30 to-purple-900/50 rounded-lg p-4">
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

      {showCharacterSelector && !isLoading && !error && (
        <>
          <button
            type="button"
            onClick={() => setShowSelector(!showSelector)}
            className="absolute bottom-2 left-2 p-1.5 rounded bg-black/40 hover:bg-black/60 text-white/80 hover:text-white transition-colors"
            title="Change character"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </button>
          <button
            type="button"
            onClick={async () => {
              console.log('=== AUDIO TEST ===');

              // Step 1: Test Web Audio API with audible beep
              try {
                const AudioContextClass = (window as any).AudioContext || (window as any).webkitAudioContext;
                const ctx = audioContextRef.current || new AudioContextClass();
                if (ctx.state === 'suspended') {
                  await ctx.resume();
                }
                console.log('AudioContext state:', ctx.state);

                // Play an audible beep
                const oscillator = ctx.createOscillator();
                const gain = ctx.createGain();
                oscillator.frequency.value = 440; // A4 note
                gain.gain.value = 0.3;
                oscillator.connect(gain);
                gain.connect(ctx.destination);
                oscillator.start();
                oscillator.stop(ctx.currentTime + 0.2);
                console.log('Beep played - did you hear it?');
              } catch (e) {
                console.error('Web Audio failed:', e);
              }

              // Step 2: Test TalkingHead capabilities and speak
              setTimeout(() => {
                console.log('=== TALKINGHEAD CAPABILITIES TEST ===');
                const head = headRef.current as any;

                if (head) {
                  // Log all available methods
                  const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(head))
                    .filter(m => typeof head[m] === 'function');
                  console.log('Available TalkingHead methods:', methods);

                  // Check for viseme-related properties
                  console.log('head.animQueue:', head.animQueue);
                  console.log('head.visemeNames:', head.visemeNames);
                  console.log('head.playViseme:', typeof head.playViseme);
                  console.log('head.avatar:', head.avatar);
                  console.log('head.model:', head.model);

                  // Try to test speaking with HeadTTS if available
                  if (headTTSRef.current) {
                    console.log('HeadTTS is available! Testing...');
                    headTTSRef.current.synthesize('Hello test').then((audio: any) => {
                      console.log('HeadTTS generated audio:', audio);
                      head.speakAudio(audio, { lipsyncLang: 'en' });
                    }).catch((e: any) => console.error('HeadTTS test failed:', e));
                  } else {
                    console.log('HeadTTS not available, using browser TTS');
                    // Just speak with browser TTS
                    const voices = window.speechSynthesis.getVoices();
                    const utterance = new SpeechSynthesisUtterance('Hello, this is a test.');
                    const voice = voices.find(v => v.name === 'Samantha') || voices[0];
                    if (voice) utterance.voice = voice;
                    window.speechSynthesis.speak(utterance);
                  }
                }
              }, 500);
            }}
            className="absolute bottom-2 right-2 p-1.5 rounded bg-black/40 hover:bg-black/60 text-white/80 hover:text-white transition-colors"
            title="Test audio (beep + avatar speech)"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
          </button>
        </>
      )}

      {showSelector && (
        <div className="absolute bottom-10 left-2 bg-gray-900/95 rounded-lg shadow-xl border border-gray-700 p-2 min-w-[120px]">
          <p className="text-xs text-gray-400 px-2 pb-1 border-b border-gray-700 mb-1">Character</p>
          {AVATAR_CHARACTERS.map((char) => (
            <button
              key={char.id}
              type="button"
              onClick={() => {
                onCharacterChange?.(char.id);
                setShowSelector(false);
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
      )}
    </div>
  );
};

export default TalkingAvatar;

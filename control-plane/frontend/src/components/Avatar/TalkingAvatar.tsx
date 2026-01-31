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
    id: 'sophia',
    name: 'Sophia',
    url: 'https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb?morphTargets=ARKit,Oculus+Visemes',
    body: 'F',
    voice: 'af_bella',
  },
  {
    id: 'brunette',
    name: 'Brunette',
    url: `${TALKINGHEAD_CDN}/brunette.glb`,
    body: 'F',
    voice: 'af_sarah',
  },
  {
    id: 'avaturn',
    name: 'Avaturn',
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
  characterId = 'sophia',
  onCharacterChange,
  showCharacterSelector = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const headRef = useRef<any>(null);
  const ttsRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [ttsLoading, setTtsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isActuallySpeaking, setIsActuallySpeaking] = useState(false);
  const [libraryLoaded, setLibraryLoaded] = useState(!!window.TalkingHead);
  const lastTextRef = useRef<string | null>(null);
  const currentCharacterRef = useRef<string>(characterId);
  const [showSelector, setShowSelector] = useState(false);

  const currentCharacter = AVATAR_CHARACTERS.find(c => c.id === characterId) || AVATAR_CHARACTERS[0];

  // Wait for libraries to load
  useEffect(() => {
    if (window.TalkingHead && window.HeadTTS) {
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

  // Initialize HeadTTS for neural text-to-speech with visemes
  useEffect(() => {
    if (!libraryLoaded || !window.HeadTTS || ttsRef.current) return;

    const initTTS = async () => {
      try {
        setTtsLoading(true);
        console.log('Initializing HeadTTS...');

        const tts = new window.HeadTTS({
          workerModule: 'https://cdn.jsdelivr.net/npm/@met4citizen/headtts@1.2/modules/worker-tts.mjs',
          dictionaryURL: 'https://cdn.jsdelivr.net/npm/@met4citizen/headtts@1.2/dictionaries/',
          endpoints: ['webgpu', 'wasm'],
          languages: ['en-us'],
          voices: ['af_bella', 'af_sarah', 'af_nicole', 'am_adam', 'am_michael'],
        });

        await tts.connect();
        ttsRef.current = tts;
        setTtsLoading(false);
        console.log('HeadTTS ready!');
      } catch (err) {
        console.warn('HeadTTS init failed, will use browser TTS:', err);
        setTtsLoading(false);
      }
    };

    initTTS();
  }, [libraryLoaded]);

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
          cameraY: 0.1,
          cameraRotateX: -0.1,
          cameraRotateY: 0,
          lightAmbientIntensity: 2,
          lightDirectIntensity: 30,
        });

        await head.showAvatar({
          url: currentCharacter.url,
          body: currentCharacter.body,
          avatarMood: 'neutral',
          lipsyncLang: 'en',
        });

        headRef.current = head;
        setIsLoading(false);
        onLoaded?.();
        console.log('Avatar ready:', currentCharacter.name);
      } catch (err) {
        console.error('Avatar init error:', err);
        setError(err instanceof Error ? err.message : 'Failed to load');
        setIsLoading(false);
        onError?.(err instanceof Error ? err.message : 'Failed');
      }
    };

    initAvatar();
  }, [enabled, libraryLoaded, characterId, currentCharacter, onLoaded, onError]);

  // Handle speaking with lip sync
  useEffect(() => {
    if (!headRef.current || !text || !isSpeaking || !enabled) return;
    if (text === lastTextRef.current) return;

    lastTextRef.current = text;

    const speak = async () => {
      try {
        setIsActuallySpeaking(true);
        onSpeakingStart?.();
        console.log('Starting speech:', text.substring(0, 50));

        const head = headRef.current;

        // Try HeadTTS first (neural TTS with proper lip-sync)
        if (ttsRef.current) {
          console.log('Using HeadTTS for lip-synced speech...');

          return new Promise<void>((resolve, reject) => {
            const tts = ttsRef.current;

            tts.onmessage = (message: any) => {
              if (message.type === 'audio') {
                console.log('Received audio from HeadTTS, playing with lip-sync...');

                head.speakAudio(message.data, { lipsyncLang: 'en' })
                  .then(() => {
                    console.log('HeadTTS speech completed');
                    setIsActuallySpeaking(false);
                    // Don't reset lastTextRef here - let it persist to prevent double-speak
                    onSpeakingEnd?.();
                    resolve();
                  })
                  .catch((err: any) => {
                    console.error('speakAudio error:', err);
                    reject(err);
                  });
              } else if (message.type === 'error') {
                console.error('HeadTTS error:', message.data);
                reject(new Error(message.data));
              }
            };

            tts.setup({
              voice: currentCharacter.voice,
              language: 'en-us',
              speed: 1.1,
              audioEncoding: 'wav',
            });

            tts.synthesize({ input: text });
          });
        }

        // Fallback to browser TTS (no lip sync, just mood change)
        console.log('HeadTTS not available, using browser TTS fallback...');

        if (!window.speechSynthesis) {
          throw new Error('Speech synthesis not available');
        }

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v =>
          v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('Daniel'))
        ) || voices.find(v => v.lang.startsWith('en')) || voices[0];

        if (preferredVoice) utterance.voice = preferredVoice;
        utterance.rate = 1.1;
        utterance.pitch = 1.0;

        utterance.onstart = () => head.setMood?.('talking');
        utterance.onend = () => {
          head.setMood?.('neutral');
          setIsActuallySpeaking(false);
          onSpeakingEnd?.();
        };
        utterance.onerror = () => {
          head.setMood?.('neutral');
          setIsActuallySpeaking(false);
          onSpeakingEnd?.();
        };

        window.speechSynthesis.speak(utterance);

      } catch (err) {
        console.error('Speech error:', err);
        setIsActuallySpeaking(false);
        onSpeakingEnd?.();
      }
    };

    speak();
  }, [text, isSpeaking, enabled, currentCharacter.voice, onSpeakingStart, onSpeakingEnd]);

  // Stop speaking
  useEffect(() => {
    if (!isSpeaking && isActuallySpeaking) {
      headRef.current?.stop?.();
      window.speechSynthesis?.cancel();
      setIsActuallySpeaking(false);
    }
  }, [isSpeaking, isActuallySpeaking]);

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
      ttsRef.current?.disconnect?.();
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

      {libraryLoaded && (isLoading || ttsLoading) && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-b from-blue-900/50 to-purple-900/50 rounded-lg">
          <div className="text-center">
            <div className="w-10 h-10 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-white/80">
              {isLoading ? 'Loading avatar...' : 'Loading TTS...'}
            </p>
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
        style={{ opacity: isLoading || ttsLoading || error ? 0 : 1 }}
      />

      {showCharacterSelector && !isLoading && !error && (
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

import React, { useEffect, useRef, useState } from 'react';
import Lottie from 'lottie-react';

// Cute animated characters from LottieFiles (free to use)
export interface LottieCharacter {
  id: string;
  name: string;
  // Using inline animation data URLs from LottieFiles CDN
  animationUrl: string;
  talkingSpeed?: number; // Speed multiplier when talking
}

export const LOTTIE_CHARACTERS: LottieCharacter[] = [
  {
    id: 'robot',
    name: 'CloudBot',
    animationUrl: '',
    talkingSpeed: 2,
  },
];

// Cute robot face animation
const fallbackAnimation = {"v":"5.7.4","fr":30,"ip":0,"op":90,"w":300,"h":300,"nm":"CuteRobot","layers":[{"ty":4,"nm":"Face","sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":0,"k":0},"p":{"a":1,"k":[{"t":0,"s":[150,150],"e":[150,145],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":22,"s":[150,145],"e":[150,155],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":45,"s":[150,155],"e":[150,145],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":67,"s":[150,145],"e":[150,150],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":90,"s":[150,150]}]},"a":{"a":0,"k":[0,0]},"s":{"a":0,"k":[100,100]}},"shapes":[{"ty":"rc","p":{"a":0,"k":[0,0]},"s":{"a":0,"k":[120,100]},"r":{"a":0,"k":30}},{"ty":"fl","c":{"a":0,"k":[0.4,0.6,0.9,1]},"o":{"a":0,"k":100}}]},{"ty":4,"nm":"LeftEye","sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":0,"k":0},"p":{"a":1,"k":[{"t":0,"s":[125,140],"e":[125,135],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":22,"s":[125,135],"e":[125,145],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":45,"s":[125,145],"e":[125,135],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":67,"s":[125,135],"e":[125,140],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":90,"s":[125,140]}]},"a":{"a":0,"k":[0,0]},"s":{"a":0,"k":[100,100]}},"shapes":[{"ty":"el","p":{"a":0,"k":[0,0]},"s":{"a":0,"k":[20,20]}},{"ty":"fl","c":{"a":0,"k":[1,1,1,1]},"o":{"a":0,"k":100}}]},{"ty":4,"nm":"RightEye","sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":0,"k":0},"p":{"a":1,"k":[{"t":0,"s":[175,140],"e":[175,135],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":22,"s":[175,135],"e":[175,145],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":45,"s":[175,145],"e":[175,135],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":67,"s":[175,135],"e":[175,140],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":90,"s":[175,140]}]},"a":{"a":0,"k":[0,0]},"s":{"a":0,"k":[100,100]}},"shapes":[{"ty":"el","p":{"a":0,"k":[0,0]},"s":{"a":0,"k":[20,20]}},{"ty":"fl","c":{"a":0,"k":[1,1,1,1]},"o":{"a":0,"k":100}}]},{"ty":4,"nm":"LeftPupil","sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":0,"k":0},"p":{"a":1,"k":[{"t":0,"s":[125,142],"e":[125,137],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":22,"s":[125,137],"e":[125,147],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":45,"s":[125,147],"e":[125,137],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":67,"s":[125,137],"e":[125,142],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":90,"s":[125,142]}]},"a":{"a":0,"k":[0,0]},"s":{"a":0,"k":[100,100]}},"shapes":[{"ty":"el","p":{"a":0,"k":[0,0]},"s":{"a":0,"k":[8,8]}},{"ty":"fl","c":{"a":0,"k":[0.2,0.2,0.3,1]},"o":{"a":0,"k":100}}]},{"ty":4,"nm":"RightPupil","sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":0,"k":0},"p":{"a":1,"k":[{"t":0,"s":[175,142],"e":[175,137],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":22,"s":[175,137],"e":[175,147],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":45,"s":[175,147],"e":[175,137],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":67,"s":[175,137],"e":[175,142],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":90,"s":[175,142]}]},"a":{"a":0,"k":[0,0]},"s":{"a":0,"k":[100,100]}},"shapes":[{"ty":"el","p":{"a":0,"k":[0,0]},"s":{"a":0,"k":[8,8]}},{"ty":"fl","c":{"a":0,"k":[0.2,0.2,0.3,1]},"o":{"a":0,"k":100}}]},{"ty":4,"nm":"Mouth","sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":0,"k":0},"p":{"a":1,"k":[{"t":0,"s":[150,170],"e":[150,165],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":22,"s":[150,165],"e":[150,175],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":45,"s":[150,175],"e":[150,165],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":67,"s":[150,165],"e":[150,170],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":90,"s":[150,170]}]},"a":{"a":0,"k":[0,0]},"s":{"a":1,"k":[{"t":0,"s":[100,100],"e":[100,120],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":15,"s":[100,120],"e":[100,80],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":30,"s":[100,80],"e":[100,130],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":45,"s":[100,130],"e":[100,90],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":60,"s":[100,90],"e":[100,110],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":75,"s":[100,110],"e":[100,100],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":90,"s":[100,100]}]}},"shapes":[{"ty":"rc","p":{"a":0,"k":[0,0]},"s":{"a":0,"k":[30,10]},"r":{"a":0,"k":5}},{"ty":"fl","c":{"a":0,"k":[0.95,0.4,0.5,1]},"o":{"a":0,"k":100}}]},{"ty":4,"nm":"Antenna","sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":1,"k":[{"t":0,"s":[0],"e":[10],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":22,"s":[10],"e":[-10],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":45,"s":[-10],"e":[10],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":67,"s":[10],"e":[0],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":90,"s":[0]}]},"p":{"a":0,"k":[150,90]},"a":{"a":0,"k":[0,15]},"s":{"a":0,"k":[100,100]}},"shapes":[{"ty":"rc","p":{"a":0,"k":[0,0]},"s":{"a":0,"k":[4,30]},"r":{"a":0,"k":2}},{"ty":"fl","c":{"a":0,"k":[0.3,0.5,0.8,1]},"o":{"a":0,"k":100}}]},{"ty":4,"nm":"AntennaBall","sr":1,"ks":{"o":{"a":0,"k":100},"r":{"a":0,"k":0},"p":{"a":1,"k":[{"t":0,"s":[150,75],"e":[152,73],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":22,"s":[152,73],"e":[148,77],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":45,"s":[148,77],"e":[152,73],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":67,"s":[152,73],"e":[150,75],"i":{"x":0.5,"y":1},"o":{"x":0.5,"y":0}},{"t":90,"s":[150,75]}]},"a":{"a":0,"k":[0,0]},"s":{"a":0,"k":[100,100]}},"shapes":[{"ty":"el","p":{"a":0,"k":[0,0]},"s":{"a":0,"k":[12,12]}},{"ty":"fl","c":{"a":0,"k":[1,0.8,0.2,1]},"o":{"a":0,"k":100}}]}]};

interface LottieAvatarProps {
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

const LottieAvatar: React.FC<LottieAvatarProps> = ({
  text,
  isSpeaking = false,
  onSpeakingEnd,
  onSpeakingStart,
  onLoaded,
  onError: _onError,
  height = 200,
  enabled = true,
  characterId = 'robot',
  onCharacterChange: _onCharacterChange,
  showCharacterSelector: _showCharacterSelector = true,
}) => {
  // Suppress unused variable warnings
  void _onError; void _onCharacterChange; void _showCharacterSelector;

  const lottieRef = useRef<any>(null);
  const [animationData, setAnimationData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [_showSelector, _setShowSelector] = useState(false);
  void _showSelector; void _setShowSelector;
  const lastTextRef = useRef<string | null>(null);
  const currentCharacterRef = useRef<string>(characterId);

  const currentCharacter = LOTTIE_CHARACTERS.find(c => c.id === characterId) || LOTTIE_CHARACTERS[0];

  // Load animation data - use fallback for reliability
  useEffect(() => {
    if (!enabled) return;

    // Use fallback animation directly for reliability
    setAnimationData(fallbackAnimation);
    setIsLoading(false);
    onLoaded?.();
  }, [enabled, onLoaded]);

  // Adjust animation speed based on speaking state
  useEffect(() => {
    if (!lottieRef.current) return;

    if (isSpeaking) {
      lottieRef.current.setSpeed(currentCharacter.talkingSpeed || 2);
    } else {
      lottieRef.current.setSpeed(1);
    }
  }, [isSpeaking, currentCharacter.talkingSpeed]);

  // Handle text-to-speech
  useEffect(() => {
    if (!text || !isSpeaking || !enabled) return;
    if (text === lastTextRef.current) return;

    lastTextRef.current = text;

    // Clean text for speech
    const cleanText = text
      .replace(/\*\*/g, '')
      .replace(/\*/g, '')
      .replace(/^[-•]\s*/gm, '')
      .replace(/^\d+\.\s*/gm, '')
      .replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '')
      .replace(/\s+/g, ' ')
      .trim();

    if (!window.speechSynthesis || !cleanText) {
      onSpeakingEnd?.();
      return;
    }

    window.speechSynthesis.cancel();
    onSpeakingStart?.();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    const voices = window.speechSynthesis.getVoices();

    const preferredVoice = voices.find(v =>
      v.lang.startsWith('en') && (
        v.name.includes('Google') ||
        v.name.includes('Samantha') ||
        v.name.includes('Daniel')
      )
    ) || voices.find(v => v.lang.startsWith('en')) || voices[0];

    if (preferredVoice) utterance.voice = preferredVoice;
    utterance.rate = 1.2;
    utterance.pitch = 1.1;

    utterance.onend = () => {
      onSpeakingEnd?.();
    };

    utterance.onerror = () => {
      onSpeakingEnd?.();
    };

    window.speechSynthesis.speak(utterance);
  }, [text, isSpeaking, enabled, onSpeakingStart, onSpeakingEnd]);

  // Reset lastTextRef when text is null
  useEffect(() => {
    if (!text) {
      lastTextRef.current = null;
    }
  }, [text]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      window.speechSynthesis?.cancel();
    };
  }, []);

  if (!enabled) return null;

  const numericHeight = typeof height === 'number' ? height : parseInt(height.toString(), 10) || 200;

  return (
    <div
      className="relative flex items-center justify-center bg-gradient-to-b from-indigo-500/20 via-purple-500/20 to-pink-500/20 dark:from-indigo-900/40 dark:via-purple-900/40 dark:to-pink-900/40"
      style={{ height: numericHeight }}
    >
      {/* Loading state */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="w-10 h-10 border-4 border-purple-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-theme-muted">Loading avatar...</p>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && !isLoading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center p-4">
          <p className="text-sm text-red-400 mb-3">{error}</p>
          <button
            type="button"
            onClick={() => {
              setError(null);
              setIsLoading(true);
              currentCharacterRef.current = '';
            }}
            className="px-4 py-2 text-sm bg-purple-500 hover:bg-purple-600 text-white rounded-lg"
          >
            Retry
          </button>
        </div>
      )}

      {/* Lottie Animation */}
      {animationData && !isLoading && !error && (
        <div
          className={`transition-transform duration-300 ${isSpeaking ? 'scale-105' : 'scale-100'}`}
          style={{
            height: numericHeight * 0.85,
            width: numericHeight * 0.85,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Lottie
            lottieRef={lottieRef}
            animationData={animationData}
            loop={true}
            autoplay={true}
            style={{
              height: '100%',
              width: '100%',
              maxWidth: numericHeight * 0.85,
              maxHeight: numericHeight * 0.85,
            }}
          />
        </div>
      )}

      {/* Speaking indicator */}
      {isSpeaking && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-1 bg-black/40 px-3 py-1.5 rounded-full">
          <div className="flex gap-0.5">
            {[0, 1, 2].map(i => (
              <div
                key={i}
                className="w-1 bg-white rounded-full animate-pulse"
                style={{
                  height: '12px',
                  animationDelay: `${i * 0.15}s`,
                  animationDuration: '0.6s'
                }}
              />
            ))}
          </div>
          <span className="text-xs text-white ml-1">Speaking...</span>
        </div>
      )}

      {/* Character selector - hidden for now since we only have one */}
    </div>
  );
};

export default LottieAvatar;

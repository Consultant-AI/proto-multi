import React, { useEffect, useRef, useState } from 'react';
import { TalkingHead } from '@met4citizen/talkinghead';

// Default avatar URL - Ready Player Me with ARKit blend shapes
const DEFAULT_AVATAR_URL = 'https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb?morphTargets=ARKit,Oculus+Visemes';

interface TalkingAvatarProps {
  /** Text for the avatar to speak */
  text?: string | null;
  /** Whether the avatar should be speaking */
  isSpeaking?: boolean;
  /** Callback when speaking ends */
  onSpeakingEnd?: () => void;
  /** Callback when speaking starts */
  onSpeakingStart?: () => void;
  /** Avatar GLB URL (with morph targets) */
  avatarUrl?: string;
  /** Height of the avatar container */
  height?: number | string;
  /** Whether avatar is enabled/visible */
  enabled?: boolean;
  /** ElevenLabs voice ID */
  voiceId?: string;
  /** ElevenLabs API key */
  apiKey?: string;
}

const TalkingAvatar: React.FC<TalkingAvatarProps> = ({
  text,
  isSpeaking = false,
  onSpeakingEnd,
  onSpeakingStart,
  avatarUrl = DEFAULT_AVATAR_URL,
  height = 200,
  enabled = true,
  // voiceId and apiKey reserved for future ElevenLabs TTS integration
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const headRef = useRef<TalkingHead | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAvatarSpeaking, setIsAvatarSpeaking] = useState(false);

  // Initialize TalkingHead
  useEffect(() => {
    if (!containerRef.current || !enabled) return;

    let mounted = true;

    const initAvatar = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Create TalkingHead instance
        const head = new TalkingHead(containerRef.current, {
          cameraView: 'head',
          cameraDistance: 0.5,
          cameraY: 0,
          backgroundColor: 'transparent',
          lightAmbientIntensity: 0.8,
          lightDirectIntensity: 1.0,
        });

        // Load the avatar
        await head.loadAvatar(avatarUrl, {
          body: 'F',
          lipsyncLang: 'en',
          avatarMood: 'neutral',
        });

        if (mounted) {
          headRef.current = head;
          head.showAvatar();
          setIsLoading(false);
        }
      } catch (err) {
        console.error('Failed to initialize avatar:', err);
        if (mounted) {
          setError('Failed to load avatar');
          setIsLoading(false);
        }
      }
    };

    initAvatar();

    return () => {
      mounted = false;
      if (headRef.current) {
        headRef.current.dispose();
        headRef.current = null;
      }
    };
  }, [avatarUrl, enabled]);

  // Handle speaking
  useEffect(() => {
    if (!headRef.current || !text || !isSpeaking) return;

    const speak = async () => {
      try {
        setIsAvatarSpeaking(true);
        onSpeakingStart?.();

        // Use browser TTS for now (can be replaced with ElevenLabs)
        await headRef.current!.speakText(text, {
          ttsLang: 'en-US',
          ttsVoice: 'Google US English',
          lipsyncLang: 'en',
        });

        setIsAvatarSpeaking(false);
        onSpeakingEnd?.();
      } catch (err) {
        console.error('Speech error:', err);
        setIsAvatarSpeaking(false);
        onSpeakingEnd?.();
      }
    };

    speak();
  }, [text, isSpeaking, onSpeakingStart, onSpeakingEnd]);

  // Stop speaking when disabled
  useEffect(() => {
    if (!isSpeaking && headRef.current && isAvatarSpeaking) {
      headRef.current.stop();
      setIsAvatarSpeaking(false);
    }
  }, [isSpeaking, isAvatarSpeaking]);

  if (!enabled) {
    return null;
  }

  return (
    <div className="relative" style={{ height }}>
      {/* Loading state */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-theme-tertiary rounded-lg">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            <p className="text-xs text-theme-muted">Loading avatar...</p>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-theme-tertiary rounded-lg">
          <p className="text-xs text-red-500">{error}</p>
        </div>
      )}

      {/* Avatar container */}
      <div
        ref={containerRef}
        className="w-full h-full rounded-lg overflow-hidden"
        style={{
          opacity: isLoading ? 0 : 1,
          transition: 'opacity 0.3s ease',
        }}
      />

      {/* Speaking indicator */}
      {isAvatarSpeaking && (
        <div className="absolute bottom-2 left-2 flex items-center gap-1 px-2 py-1 bg-black/50 rounded-full">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs text-white">Speaking...</span>
        </div>
      )}
    </div>
  );
};

export default TalkingAvatar;

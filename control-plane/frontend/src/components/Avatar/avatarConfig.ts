// Avatar configuration and constants

// Pre-defined avatar URLs from Ready Player Me
// These URLs include morph targets for lip sync
export const AVATAR_PRESETS = {
  female1: 'https://models.readyplayer.me/64bfa15f0e72c63d7c3934a6.glb?morphTargets=ARKit,Oculus+Visemes',
  male1: 'https://models.readyplayer.me/638df693fc6cc48cdf2cd4ea.glb?morphTargets=ARKit,Oculus+Visemes',
  // Add more preset avatars here
} as const;

// Default avatar for CloudBot
export const DEFAULT_AVATAR = AVATAR_PRESETS.female1;

// Camera view presets
export const CAMERA_VIEWS = {
  head: { view: 'head', distance: 0.5, y: 0 },
  upper: { view: 'upper', distance: 0.8, y: -0.1 },
  mid: { view: 'mid', distance: 1.2, y: -0.3 },
  full: { view: 'full', distance: 2.0, y: -0.5 },
} as const;

// Mood presets
export const MOODS = {
  neutral: 'neutral',
  happy: 'happy',
  sad: 'sad',
  angry: 'angry',
  surprised: 'surprised',
  thinking: 'thinking',
} as const;

// ElevenLabs voice presets
export const ELEVENLABS_VOICES = {
  rachel: 'EXAVITQu4vr4xnSDxMaL', // Rachel - calm female
  bella: '21m00Tcm4TlvDq8ikWAM', // Bella - soft female
  adam: 'pNInz6obpgDQGcFmaJgB', // Adam - deep male
  sam: 'yoZ06aMxZJJ28mfd3POQ', // Sam - dynamic male
} as const;

// TTS configuration
export const TTS_CONFIG = {
  defaultVoice: ELEVENLABS_VOICES.rachel,
  stability: 0.5,
  similarityBoost: 0.75,
  style: 0.0,
  useSpeakerBoost: true,
};

// Animation names supported by Ready Player Me avatars
export const ANIMATIONS = {
  idle: 'Idle',
  talking: 'Talking',
  thinking: 'Thinking',
  greeting: 'Greeting',
  nodding: 'Nodding',
} as const;

// Utility function to build Ready Player Me avatar URL with morph targets
export function buildAvatarUrl(
  avatarId: string,
  options: {
    morphTargets?: ('ARKit' | 'Oculus Visemes')[];
    quality?: 'low' | 'medium' | 'high';
    textureAtlas?: number;
  } = {}
): string {
  const params = new URLSearchParams();

  // Default morph targets for lip sync
  const morphTargets = options.morphTargets || ['ARKit', 'Oculus Visemes'];
  params.set('morphTargets', morphTargets.join(','));

  // Quality settings
  if (options.quality) {
    params.set('quality', options.quality);
  }

  if (options.textureAtlas) {
    params.set('textureAtlas', options.textureAtlas.toString());
  }

  return `https://models.readyplayer.me/${avatarId}.glb?${params.toString()}`;
}

// Check if browser supports WebGL (required for Three.js)
export function checkWebGLSupport(): boolean {
  try {
    const canvas = document.createElement('canvas');
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
    );
  } catch {
    return false;
  }
}

// Check if browser supports Web Audio API (required for TTS)
export function checkAudioSupport(): boolean {
  return !!(window.AudioContext || (window as any).webkitAudioContext);
}

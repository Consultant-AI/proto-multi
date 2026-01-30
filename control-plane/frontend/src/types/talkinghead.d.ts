// Type declarations for @met4citizen/talkinghead

declare module '@met4citizen/talkinghead' {
  export interface TalkingHeadOptions {
    /** Show stats in the corner */
    showStats?: boolean;
    /** Camera view: 'full', 'mid', 'upper', 'head' */
    cameraView?: 'full' | 'mid' | 'upper' | 'head';
    /** Camera distance from avatar */
    cameraDistance?: number;
    /** Camera vertical offset */
    cameraY?: number;
    /** Camera horizontal offset */
    cameraX?: number;
    /** Camera rotation offset */
    cameraRotateX?: number;
    /** Camera rotation offset */
    cameraRotateY?: number;
    /** Enable orbit controls */
    cameraControls?: boolean;
    /** Light intensity */
    lightAmbientIntensity?: number;
    lightDirectIntensity?: number;
    lightSpotIntensity?: number;
    /** Background color */
    backgroundColor?: string;
  }

  export interface AvatarOptions {
    /** Body type 'M' or 'F' */
    body?: 'M' | 'F';
    /** Lip-sync language */
    lipsyncLang?: string;
    /** TTS language */
    ttsLang?: string;
    /** TTS voice name */
    ttsVoice?: string;
    /** TTS rate */
    ttsRate?: number;
    /** TTS pitch */
    ttsPitch?: number;
    /** TTS volume */
    ttsVolume?: number;
    /** Initial mood */
    avatarMood?: string;
    /** Mute avatar */
    avatarMute?: boolean;
  }

  export interface SpeakOptions {
    /** Text to speak */
    text?: string;
    /** TTS language */
    ttsLang?: string;
    /** TTS voice */
    ttsVoice?: string;
    /** TTS endpoint URL */
    ttsEndpoint?: string;
    /** TTS API key */
    ttsApikey?: string;
    /** Lip-sync language */
    lipsyncLang?: string;
    /** Exclude from subtitles */
    excludeSubtitles?: boolean;
  }

  export interface StreamOptions {
    /** TTS language */
    ttsLang?: string;
    /** TTS voice */
    ttsVoice?: string;
    /** Lip-sync language */
    lipsyncLang?: string;
  }

  export type AudioCallback = () => void;
  export type SubtitlesCallback = (node: HTMLElement) => void;
  export type MetricsCallback = (metrics: { latency: number; duration: number }) => void;

  export class TalkingHead {
    constructor(container: HTMLElement | null, options?: TalkingHeadOptions);

    /** Load avatar from URL */
    loadAvatar(url: string, options?: AvatarOptions, onProgress?: (url: string, event: ProgressEvent) => void): Promise<void>;

    /** Show avatar */
    showAvatar(): void;

    /** Start speaking text */
    speakText(text: string, options?: SpeakOptions): Promise<void>;

    /** Start speaking with pre-generated audio */
    speakAudio(audio: ArrayBuffer | ArrayBuffer[], options?: SpeakOptions): Promise<void>;

    /** Start streaming mode */
    streamStart(
      options?: StreamOptions,
      onAudioStart?: AudioCallback,
      onAudioEnd?: AudioCallback,
      onSubtitles?: SubtitlesCallback,
      onMetrics?: MetricsCallback
    ): Promise<void>;

    /** Stream audio chunks */
    streamAudio(audioChunks: ArrayBuffer | ArrayBuffer[]): void;

    /** Notify that streaming has ended */
    streamNotifyEnd(): void;

    /** Interrupt streaming without ending session */
    streamInterrupt(): void;

    /** Stop streaming mode */
    streamStop(): void;

    /** Stop speaking */
    stop(): void;

    /** Set mood */
    setMood(mood: string): void;

    /** Look at position */
    lookAt(x: number, y: number, z: number): void;

    /** Start animation */
    playAnimation(name: string, duration?: number, repeat?: number): void;

    /** Stop current animation */
    stopAnimation(): void;

    /** Mute/unmute */
    setMute(mute: boolean): void;

    /** Check if speaking */
    isSpeaking(): boolean;

    /** Get current mood */
    getMood(): string;

    /** Dispose resources */
    dispose(): void;
  }
}

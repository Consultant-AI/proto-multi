declare module '@novnc/novnc/lib/rfb' {
  interface RFBCredentials {
    username?: string;
    password?: string;
    target?: string;
  }

  interface RFBCapabilities {
    power: boolean;
  }

  interface RFBOptions {
    shared?: boolean;
    credentials?: RFBCredentials;
    repeaterID?: string;
    wsProtocols?: string[];
  }

  export default class RFB {
    constructor(target: HTMLElement, url: string, options?: RFBOptions);

    viewOnly: boolean;
    focusOnClick: boolean;
    clipViewport: boolean;
    dragViewport: boolean;
    scaleViewport: boolean;
    resizeSession: boolean;
    showDotCursor: boolean;
    background: string;
    qualityLevel: number;
    compressionLevel: number;
    capabilities: RFBCapabilities;

    disconnect(): void;
    sendCredentials(credentials: RFBCredentials): void;
    sendKey(keysym: number, code: string | null, down?: boolean): void;
    sendCtrlAltDel(): void;
    focus(): void;
    blur(): void;
    machineShutdown(): void;
    machineReboot(): void;
    machineReset(): void;
    clipboardPasteFrom(text: string): void;

    addEventListener(type: string, listener: (e: CustomEvent) => void): void;
    removeEventListener(type: string, listener: (e: CustomEvent) => void): void;
  }
}

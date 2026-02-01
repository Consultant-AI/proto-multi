const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';

declare global {
  interface Window {
    RFB?: any;
  }
}

// Wait for noVNC to load from CDN
const waitForNoVNC = (): Promise<any> => {
  return new Promise((resolve, reject) => {
    if (window.RFB) {
      resolve(window.RFB);
      return;
    }

    const handleLoaded = () => {
      window.removeEventListener('novnc-loaded', handleLoaded);
      window.removeEventListener('novnc-error', handleError);
      if (window.RFB) {
        resolve(window.RFB);
      } else {
        reject(new Error('RFB not found after loading'));
      }
    };

    const handleError = (e: Event) => {
      window.removeEventListener('novnc-loaded', handleLoaded);
      window.removeEventListener('novnc-error', handleError);
      reject(new Error((e as CustomEvent).detail || 'Failed to load noVNC'));
    };

    window.addEventListener('novnc-loaded', handleLoaded);
    window.addEventListener('novnc-error', handleError);

    // Timeout after 30 seconds
    setTimeout(() => {
      window.removeEventListener('novnc-loaded', handleLoaded);
      window.removeEventListener('novnc-error', handleError);
      if (window.RFB) {
        resolve(window.RFB);
      } else {
        reject(new Error('Timeout waiting for noVNC to load'));
      }
    }, 30000);
  });
};

export const connectToVNC = async (
  instanceId: string,
  token: string,
  container: HTMLElement,
  onConnect?: () => void,
  onDisconnect?: () => void,
  onError?: (error: any) => void,
  backgroundColor?: string
): Promise<any> => {
  const url = `${WS_BASE_URL}/api/instances/${instanceId}/vnc?token=${token}`;

  try {
    // Wait for noVNC to load from CDN
    const RFB = await waitForNoVNC();

    const rfb = new RFB(container, url, {
      wsProtocols: ['binary'],
    });

    // Let noVNC handle scaling - this ensures mouse coordinates work correctly
    rfb.scaleViewport = true;  // Scale to fit container
    rfb.clipViewport = false;  // Don't clip - show full desktop
    rfb.resizeSession = false; // Don't resize the remote session
    rfb.qualityLevel = 3;
    rfb.compressionLevel = 7;

    // Set background color for areas outside the remote desktop
    if (backgroundColor) {
      rfb.background = backgroundColor;
    }

    rfb.addEventListener('connect', () => {
      console.log('VNC connected');
      onConnect?.();
    });

    rfb.addEventListener('disconnect', (e: any) => {
      console.log('VNC disconnected', e.detail);
      onDisconnect?.();
    });

    rfb.addEventListener('securityfailure', (e: any) => {
      console.error('VNC security failure:', e.detail);
      onError?.(e.detail);
    });

    return rfb;
  } catch (err) {
    console.error('Failed to initialize VNC:', err);
    onError?.(err);
    return null;
  }
};

export const disconnectVNC = (rfb: any) => {
  if (rfb && rfb.disconnect) {
    try {
      rfb.disconnect();
    } catch (e) {
      // ignore
    }
  }
};

// Update VNC background color (for theme changes)
export const setVNCBackground = (rfb: any, color: string) => {
  if (rfb) {
    rfb.background = color;
  }
};

/**
 * Patch noVNC's coordinate conversion to account for CSS transform scaling.
 * noVNC's absX/absY divide by _display._scale, but with CSS transform
 * the _scale is 1.0 while the visual scale is different.
 */
export const patchMouseCoordinates = (rfb: any, cssScale: number) => {
  if (!rfb) {
    console.warn('patchMouseCoordinates: rfb is null');
    return false;
  }
  if (!rfb._display) {
    console.warn('patchMouseCoordinates: rfb._display is null');
    return false;
  }
  const display = rfb._display;
  display._cssTransformScale = cssScale;

  display.absX = function (x: number) {
    const s = this._cssTransformScale || 1;
    const viewportX = this._viewportLoc?.x || 0;
    const result = Math.round(x / s + viewportX);
    return result;
  };
  display.absY = function (y: number) {
    const s = this._cssTransformScale || 1;
    const viewportY = this._viewportLoc?.y || 0;
    const result = Math.round(y / s + viewportY);
    return result;
  };

  console.log('Mouse coordinates patched successfully:', {
    cssScale,
    viewportLoc: display._viewportLoc,
    displayScale: display._scale
  });
  return true;
};

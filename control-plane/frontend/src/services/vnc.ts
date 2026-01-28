// Temporarily disabled noVNC import due to build issues
// Will be fixed once main UI is working
// import RFB from '@novnc/novnc/lib/rfb';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';

export const connectToVNC = (
  instanceId: string,
  token: string,
  canvas: HTMLCanvasElement,
  onConnect?: () => void,
  onDisconnect?: () => void,
  onError?: (error: any) => void
): any => {
  console.warn('VNC is temporarily disabled - showing placeholder');

  // Show placeholder in canvas
  const ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.fillStyle = '#1f2937';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#9ca3af';
    ctx.font = '16px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('VNC Viewer (Temporarily Disabled)', canvas.width / 2, canvas.height / 2 - 10);
    ctx.fillText('Working on fixing noVNC compatibility...', canvas.width / 2, canvas.height / 2 + 20);
  }

  // Return a mock object
  return {
    disconnect: () => console.log('Mock disconnect'),
    scaleViewport: true,
    resizeSession: false,
  };
};

export const disconnectVNC = (rfb: any) => {
  if (rfb && rfb.disconnect) {
    rfb.disconnect();
  }
};

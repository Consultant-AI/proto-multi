import React, { useEffect, useRef, useState, useCallback } from 'react';
import { connectToVNC, disconnectVNC, setVNCBackground } from '../../services/vnc';
import { useTheme } from '../../contexts/ThemeContext';

// Fixed framebuffer size matching Xvfb config on EC2
const FB_HEIGHT = 1080;

interface RemoteDesktopProps {
  instanceId: string;
}

const RemoteDesktop: React.FC<RemoteDesktopProps> = ({ instanceId }) => {
  const outerRef = useRef<HTMLDivElement>(null);
  const vncTargetRef = useRef<HTMLDivElement>(null);
  const rfbRef = useRef<any>(null);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('connecting');
  const [error, setError] = useState<string>('');
  const { theme } = useTheme();

  // Get background color based on theme
  const bgColor = theme === 'dark' ? '#000000' : '#ffffff';

  // Notify noVNC of container size changes so it can rescale
  const triggerResize = useCallback(() => {
    if (rfbRef.current) {
      // noVNC's scaleViewport automatically adjusts when container resizes
      // We just need to trigger a resize event
      window.dispatchEvent(new Event('resize'));
    }
  }, []);

  // Watch the outer container for size changes
  useEffect(() => {
    if (!outerRef.current) return;
    const observer = new ResizeObserver(() => triggerResize());
    observer.observe(outerRef.current);
    return () => observer.disconnect();
  }, [triggerResize]);

  // Update VNC background when theme changes
  useEffect(() => {
    if (rfbRef.current) {
      setVNCBackground(rfbRef.current, bgColor);
    }
  }, [theme, bgColor]);

  // Connect to VNC
  useEffect(() => {
    if (!vncTargetRef.current) return;

    const token = localStorage.getItem('access_token') || '';
    const target = vncTargetRef.current;
    let cancelled = false;
    const currentBgColor = theme === 'dark' ? '#000000' : '#ffffff';

    const connect = async () => {
      try {
        const rfb = await connectToVNC(
          instanceId,
          token,
          target,
          () => {
            if (!cancelled) {
              setStatus('connected');
              triggerResize();
            }
          },
          () => { if (!cancelled) setStatus('disconnected'); },
          (err) => {
            if (!cancelled) {
              setStatus('error');
              setError(typeof err === 'string' ? err : err?.message || 'Failed to connect');
            }
          },
          currentBgColor
        );
        if (!cancelled && rfb) {
          rfbRef.current = rfb;

          // Debug: log canvas size when available
          setTimeout(() => {
            const canvas = vncTargetRef.current?.querySelector('canvas');
            if (canvas) {
              console.log('VNC canvas dimensions:', {
                width: canvas.width,
                height: canvas.height,
                clientWidth: canvas.clientWidth,
                clientHeight: canvas.clientHeight,
                boundingRect: canvas.getBoundingClientRect()
              });
            }
          }, 2000);
        }
      } catch (err: any) {
        if (!cancelled) {
          setStatus('error');
          setError(err?.message || 'Failed to initialize VNC');
        }
      }
    };

    connect();

    return () => {
      cancelled = true;
      if (rfbRef.current) {
        disconnectVNC(rfbRef.current);
        rfbRef.current = null;
      }
    };
  }, [instanceId, triggerResize]);

  return (
    <div className="flex flex-col flex-1 min-h-0" style={{ backgroundColor: bgColor }}>
      {/* Outer container: fills flex space, provides measurement for scale */}
      <div
        ref={outerRef}
        className="flex-1 overflow-hidden relative min-h-0"
        style={{ backgroundColor: bgColor }}
      >
        {status === 'connecting' && (
          <div className="absolute inset-0 flex items-center justify-center z-10" style={{ backgroundColor: bgColor }}>
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-transparent border-b-blue-500 rounded-full mx-auto mb-4 animate-spin" />
              <p className="text-theme-primary">Connecting to desktop...</p>
            </div>
          </div>
        )}
        {status === 'error' && (
          <div className="absolute inset-0 flex items-center justify-center z-10" style={{ backgroundColor: bgColor }}>
            <div className="text-center text-red-400">
              <p className="text-lg">Failed to connect</p>
              <p className="text-sm mt-2">{error}</p>
              <p className="text-xs mt-4 text-theme-muted">The instance may still be starting up. Try refreshing.</p>
            </div>
          </div>
        )}
        {/* VNC target - noVNC's scaleViewport handles sizing and coordinate conversion */}
        <div
          ref={vncTargetRef}
          className="vnc-target-container"
          style={{
            width: '100%',
            height: '100%',
            position: 'absolute',
            top: 0,
            left: 0,
            overflow: 'hidden',
            backgroundColor: bgColor,
          }}
        />
        <style>{`
          .vnc-target-container canvas {
            max-height: ${FB_HEIGHT}px !important;
          }
          .vnc-target-container > div {
            max-height: ${FB_HEIGHT}px !important;
            overflow: hidden !important;
            background-color: ${bgColor} !important;
          }
          .vnc-target-container > div > div {
            background-color: ${bgColor} !important;
          }
        `}</style>
      </div>
    </div>
  );
};

export default RemoteDesktop;

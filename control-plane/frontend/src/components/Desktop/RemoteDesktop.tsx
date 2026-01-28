import React, { useEffect, useRef, useState } from 'react';
import { connectToVNC, disconnectVNC } from '../../services/vnc';

interface RemoteDesktopProps {
  instanceId: string;
}

const RemoteDesktop: React.FC<RemoteDesktopProps> = ({ instanceId }) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [rfb, setRfb] = useState<any>(null);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('connecting');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!canvasRef.current) return;

    const token = localStorage.getItem('access_token') || '';
    const canvas = document.createElement('canvas');
    canvasRef.current.appendChild(canvas);

    const rfbConnection = connectToVNC(
      instanceId,
      token,
      canvas,
      () => {
        setStatus('connected');
        setError('');
      },
      () => {
        setStatus('disconnected');
      },
      (err) => {
        setStatus('error');
        setError(err.detail || 'Failed to connect to desktop');
      }
    );

    setRfb(rfbConnection);

    return () => {
      if (rfbConnection) {
        disconnectVNC(rfbConnection);
      }
      if (canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }
    };
  }, [instanceId]);

  return (
    <div className="h-full w-full flex flex-col bg-gray-900">
      <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center">
          <div
            className={`w-2 h-2 rounded-full mr-2 ${
              status === 'connected'
                ? 'bg-green-500'
                : status === 'connecting'
                ? 'bg-yellow-500 animate-pulse'
                : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-300">
            {status === 'connected'
              ? 'Connected'
              : status === 'connecting'
              ? 'Connecting...'
              : status === 'error'
              ? 'Connection Error'
              : 'Disconnected'}
          </span>
        </div>
      </div>
      <div className="flex-1 relative">
        {status === 'connecting' && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p className="text-white">Connecting to desktop...</p>
            </div>
          </div>
        )}
        {status === 'error' && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
            <div className="text-center text-red-400">
              <p>Failed to connect</p>
              <p className="text-sm mt-2">{error}</p>
            </div>
          </div>
        )}
        <div ref={canvasRef} className="w-full h-full" />
      </div>
    </div>
  );
};

export default RemoteDesktop;

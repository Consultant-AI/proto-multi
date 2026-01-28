import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useInstances } from '../../contexts/InstanceContext';
import RemoteDesktop from './RemoteDesktop';
import ChatInterface from '../Chat/ChatInterface';

const SplitView: React.FC = () => {
  const { instanceId } = useParams<{ instanceId: string }>();
  const { selectedInstance, refreshInstance } = useInstances();
  const navigate = useNavigate();

  useEffect(() => {
    if (instanceId) {
      refreshInstance(instanceId);
      const interval = setInterval(() => refreshInstance(instanceId), 5000);
      return () => clearInterval(interval);
    }
  }, [instanceId]);

  if (!instanceId) {
    return <div>Instance ID not provided</div>;
  }

  const isReady = selectedInstance?.status === 'running' && selectedInstance?.public_ip;

  return (
    <div className="h-screen flex flex-col">
      <div className="bg-gray-800 px-4 py-3 text-white flex items-center justify-between">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/dashboard')}
            className="mr-4 text-gray-300 hover:text-white"
          >
            ← Back to Dashboard
          </button>
          <h2 className="font-semibold">
            {selectedInstance?.name || 'Instance'} - {selectedInstance?.status}
          </h2>
        </div>
      </div>

      {!isReady ? (
        <div className="flex-1 flex items-center justify-center bg-gray-100">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-700 font-medium">
              {selectedInstance?.status === 'launching'
                ? 'Instance is launching... This may take 2-3 minutes'
                : 'Waiting for instance to be ready...'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Status: {selectedInstance?.status}
            </p>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 border-r">
            <RemoteDesktop instanceId={instanceId} />
          </div>
          <div className="w-96">
            <ChatInterface instanceId={instanceId} />
          </div>
        </div>
      )}
    </div>
  );
};

export default SplitView;

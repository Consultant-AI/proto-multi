import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInstances } from '../../contexts/InstanceContext';

const InstanceList: React.FC = () => {
  const { instances, loading, fetchInstances, deleteInstance, selectInstance } = useInstances();
  const navigate = useNavigate();

  useEffect(() => {
    fetchInstances();
    const interval = setInterval(fetchInstances, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleViewInstance = (instance: any) => {
    selectInstance(instance);
    navigate(`/instances/${instance.id}`);
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this instance?')) {
      await deleteInstance(id);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-500/20 text-green-400 dark:bg-green-500/20 dark:text-green-400';
      case 'launching':
        return 'bg-yellow-500/20 text-yellow-400 dark:bg-yellow-500/20 dark:text-yellow-400';
      case 'stopping':
      case 'stopped':
        return 'bg-gray-500/20 text-gray-400 dark:bg-gray-500/20 dark:text-gray-400';
      default:
        return 'bg-red-500/20 text-red-400 dark:bg-red-500/20 dark:text-red-400';
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-theme-primary">Your Instances</h2>
        <button
          type="button"
          onClick={() => navigate('/create-instance')}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors"
        >
          + Create Instance
        </button>
      </div>

      {loading && instances.length === 0 ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-theme-muted">Loading instances...</p>
        </div>
      ) : instances.length === 0 ? (
        <div className="text-center py-12 bg-theme-card rounded-xl border border-theme">
          <div className="w-16 h-16 rounded-full bg-theme-tertiary flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-theme-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <p className="text-theme-secondary mb-4">No instances yet</p>
          <button
            type="button"
            onClick={() => navigate('/create-instance')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            Create your first instance
          </button>
        </div>
      ) : (
        <div className="bg-theme-card rounded-xl border border-theme overflow-hidden">
          <ul className="divide-y divide-[var(--border-color)]">
            {instances.map((instance) => (
              <li
                key={instance.id}
                className="hover:bg-theme-hover cursor-pointer transition-colors"
                onClick={() => handleViewInstance(instance)}
              >
                <div className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-blue-500 hover:text-blue-400 truncate">
                        {instance.name || 'Unnamed Instance'}
                      </p>
                      <div className="mt-2 flex items-center text-sm text-theme-muted">
                        <span
                          className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(
                            instance.status
                          )}`}
                        >
                          {instance.status}
                        </span>
                        {instance.public_ip && (
                          <span className="ml-4 font-mono text-xs">{instance.public_ip}</span>
                        )}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => handleDelete(instance.id, e)}
                      className="ml-4 px-3 py-1.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default InstanceList;

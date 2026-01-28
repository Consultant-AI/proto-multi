import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInstances } from '../../contexts/InstanceContext';
import { useAuth } from '../../contexts/AuthContext';

const InstanceList: React.FC = () => {
  const { instances, loading, fetchInstances, deleteInstance, selectInstance } = useInstances();
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchInstances();
    const interval = setInterval(fetchInstances, 10000); // Poll every 10 seconds
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
        return 'bg-green-100 text-green-800';
      case 'launching':
        return 'bg-yellow-100 text-yellow-800';
      case 'stopping':
      case 'stopped':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">CloudBot Platform</h1>
            </div>
            <div className="flex items-center">
              <button
                onClick={logout}
                className="ml-4 px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Your Instances</h2>
            <button
              onClick={() => navigate('/create-instance')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Create Instance
            </button>
          </div>

          {loading && instances.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">Loading...</p>
            </div>
          ) : instances.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-500 mb-4">No instances yet</p>
              <button
                onClick={() => navigate('/create-instance')}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Create your first instance
              </button>
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {instances.map((instance) => (
                  <li
                    key={instance.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleViewInstance(instance)}
                  >
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-blue-600 truncate">
                            {instance.name || 'Unnamed Instance'}
                          </p>
                          <div className="mt-2 flex items-center text-sm text-gray-500">
                            <span
                              className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${getStatusColor(
                                instance.status
                              )}`}
                            >
                              {instance.status}
                            </span>
                            {instance.public_ip && (
                              <span className="ml-4">{instance.public_ip}</span>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={(e) => handleDelete(instance.id, e)}
                          className="ml-4 px-3 py-1 text-sm text-red-600 hover:text-red-800"
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
      </div>
    </div>
  );
};

export default InstanceList;

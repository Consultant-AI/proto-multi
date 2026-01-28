import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInstances } from '../../contexts/InstanceContext';

const CreateInstance: React.FC = () => {
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { createInstance, selectInstance } = useInstances();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const instance = await createInstance(name || undefined);
      selectInstance(instance);

      // Poll for instance to be ready
      navigate(`/instances/${instance.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create instance');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create New Instance
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            This will provision an Ubuntu desktop with CloudBot
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Instance Name (optional)
            </label>
            <input
              id="name"
              name="name"
              type="text"
              className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="My Instance"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="flex-1 py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Instance'}
            </button>
          </div>
        </form>

        {loading && (
          <div className="text-center text-sm text-gray-500">
            <p>Provisioning your instance...</p>
            <p className="mt-1">This may take 2-3 minutes</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CreateInstance;

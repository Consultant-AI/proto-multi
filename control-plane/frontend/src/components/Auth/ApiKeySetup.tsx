import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

const ApiKeySetup: React.FC = () => {
  const [anthropicKey, setAnthropicKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [googleKey, setGoogleKey] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Store only non-empty API keys
      const promises = [];
      if (anthropicKey) {
        promises.push(
          api.post('/api/user/api-keys', {
            provider: 'anthropic',
            api_key: anthropicKey,
          })
        );
      }
      if (openaiKey) {
        promises.push(
          api.post('/api/user/api-keys', {
            provider: 'openai',
            api_key: openaiKey,
          })
        );
      }
      if (googleKey) {
        promises.push(
          api.post('/api/user/api-keys', {
            provider: 'google',
            api_key: googleKey,
          })
        );
      }

      await Promise.all(promises);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save API keys');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Configure API Keys
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Add your AI provider API keys to enable CloudBot. You can skip this and add them later.
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="anthropic" className="block text-sm font-medium text-gray-700">
                Anthropic API Key (Claude)
              </label>
              <input
                id="anthropic"
                name="anthropic"
                type="password"
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="sk-ant-..."
                value={anthropicKey}
                onChange={(e) => setAnthropicKey(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="openai" className="block text-sm font-medium text-gray-700">
                OpenAI API Key (GPT)
              </label>
              <input
                id="openai"
                name="openai"
                type="password"
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="sk-..."
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="google" className="block text-sm font-medium text-gray-700">
                Google API Key (Gemini)
              </label>
              <input
                id="google"
                name="google"
                type="password"
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="AI..."
                value={googleKey}
                onChange={(e) => setGoogleKey(e.target.value)}
              />
            </div>
          </div>

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={handleSkip}
              className="flex-1 py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Skip for now
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save and continue'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ApiKeySetup;

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInstances } from '../../contexts/InstanceContext';

const INSTANCE_TYPES = [
  {
    value: 't3.micro',
    label: 'Micro',
    specs: '2 vCPU, 1GB RAM',
    price: 'Free Tier',
    freeTier: true,
    fallbackOnly: true,
    note: 'Fallback gateway only'
  },
  {
    value: 't3.small',
    label: 'Small',
    specs: '2 vCPU, 2GB RAM',
    price: '~$0.02/hr',
    fallbackOnly: true,
    note: 'Fallback gateway only'
  },
  {
    value: 't3.medium',
    label: 'Medium',
    specs: '2 vCPU, 4GB RAM',
    price: '~$0.04/hr',
    supportsOpenclaw: true,
    recommended: true,
    note: 'Full openclaw support'
  },
  {
    value: 't3.large',
    label: 'Large',
    specs: '2 vCPU, 8GB RAM',
    price: '~$0.08/hr',
    supportsOpenclaw: true,
    note: 'Best performance'
  },
];

// LLM providers supported by CloudBot
const LLM_PROVIDERS = [
  { id: 'anthropic', name: 'Anthropic', icon: '🧠', placeholder: 'sk-ant-api03-...' },
  { id: 'openai', name: 'OpenAI', icon: '💚', placeholder: 'sk-proj-...' },
  { id: 'google', name: 'Gemini', icon: '✨', placeholder: 'AIza...' },
  { id: 'groq', name: 'Groq', icon: '⚡', placeholder: 'gsk_...' },
  { id: 'together', name: 'Together', icon: '🤝', placeholder: '' },
  { id: 'openrouter', name: 'OpenRouter', icon: '🔀', placeholder: 'sk-or-...' },
  { id: 'mistral', name: 'Mistral', icon: '🌬️', placeholder: '' },
  { id: 'deepseek', name: 'DeepSeek', icon: '🔍', placeholder: 'sk-...' },
  { id: 'xai', name: 'xAI', icon: '𝕏', placeholder: 'xai-...' },
];

const CreateInstance: React.FC = () => {
  const [name, setName] = useState('');
  const [instanceType, setInstanceType] = useState('t3.medium');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('anthropic');
  const [apiKey, setApiKey] = useState('');
  const { createInstance, selectInstance } = useInstances();
  const navigate = useNavigate();

  const currentProvider = LLM_PROVIDERS.find(p => p.id === selectedProvider);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate API key is provided
    if (!apiKey.trim()) {
      setError('API key is required for CloudBot to work');
      return;
    }

    setLoading(true);

    try {
      const apiKeys = { [selectedProvider]: apiKey };
      const instance = await createInstance(name || undefined, instanceType, apiKeys);
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
    <div className="max-w-xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-theme-primary">
          Create New Instance
        </h2>
        <p className="mt-2 text-sm text-theme-muted">
          Ubuntu desktop with Chrome, VS Code, LibreOffice
        </p>
      </div>
      <form className="space-y-6" onSubmit={handleSubmit}>
        {error && (
          <div className="rounded-md bg-red-500/10 border border-red-500 p-4">
            <p className="text-sm text-red-500">{error}</p>
          </div>
        )}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-theme-secondary">
            Instance Name (optional)
          </label>
          <input
            id="name"
            name="name"
            type="text"
            className="mt-1 appearance-none relative block w-full px-3 py-2 border border-theme bg-theme-tertiary placeholder-theme-muted text-theme-primary rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="My Instance"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-theme-secondary mb-2">
            Instance Size
          </label>
          <p className="text-xs text-theme-muted mb-2">
            t3.medium or larger required for full openclaw bot. Smaller instances use a basic fallback gateway.
          </p>
          <div className="grid grid-cols-2 gap-3">
            {INSTANCE_TYPES.map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => setInstanceType(type.value)}
                className={`relative p-4 border rounded-lg text-left transition-all ${
                  instanceType === type.value
                    ? 'border-blue-500 bg-blue-500/10 ring-2 ring-blue-500'
                    : type.fallbackOnly
                    ? 'border-theme bg-theme-card hover:border-theme-hover opacity-75'
                    : 'border-theme bg-theme-card hover:border-theme-hover'
                }`}
              >
                {type.recommended && (
                  <span className="absolute -top-2 right-2 px-2 py-0.5 text-xs bg-green-500 text-white rounded-full">
                    Recommended
                  </span>
                )}
                {type.freeTier && !type.recommended && (
                  <span className="absolute -top-2 right-2 px-2 py-0.5 text-xs bg-blue-500 text-white rounded-full">
                    Free Tier
                  </span>
                )}
                <div className="font-medium text-theme-primary">{type.label}</div>
                <div className="text-xs text-theme-muted mt-1">{type.specs}</div>
                <div className="text-xs text-theme-muted mt-0.5">{type.price}</div>
                {type.note && (
                  <div className={`text-xs mt-1 ${type.supportsOpenclaw ? 'text-green-500' : 'text-yellow-500'}`}>
                    {type.note}
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* LLM Provider Selection */}
        <div>
          <label className="block text-sm font-medium text-theme-secondary mb-2">
            LLM Provider
          </label>
          <p className="text-xs text-theme-muted mb-3">
            Select your AI provider and enter the API key.
          </p>

          {/* Provider radio buttons */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            {LLM_PROVIDERS.map((provider) => (
              <label
                key={provider.id}
                className={`flex items-center gap-2 p-3 border rounded-lg cursor-pointer transition-all ${
                  selectedProvider === provider.id
                    ? 'border-blue-500 bg-blue-500/10 ring-1 ring-blue-500'
                    : 'border-theme bg-theme-card hover:border-theme-hover'
                }`}
              >
                <input
                  type="radio"
                  name="llm-provider"
                  value={provider.id}
                  checked={selectedProvider === provider.id}
                  onChange={(e) => {
                    setSelectedProvider(e.target.value);
                    setApiKey(''); // Clear key when switching providers
                  }}
                  className="sr-only"
                />
                <span className="text-base">{provider.icon}</span>
                <span className="text-sm text-theme-primary">{provider.name}</span>
              </label>
            ))}
          </div>

          {/* API Key input */}
          <div>
            <label htmlFor="api-key" className="block text-xs font-medium text-theme-secondary mb-1">
              {currentProvider?.icon} {currentProvider?.name} API Key
            </label>
            <input
              id="api-key"
              type="password"
              className="appearance-none relative block w-full px-3 py-2 border border-theme bg-theme-tertiary placeholder-theme-muted text-theme-primary rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder={currentProvider?.placeholder || 'Enter API key'}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
          </div>
        </div>

        <div className="flex space-x-3">
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="flex-1 py-2 px-4 border border-theme text-sm font-medium rounded-md text-theme-secondary bg-theme-tertiary hover:bg-theme-hover"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading || !apiKey.trim()}
            className="flex-1 py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create Instance'}
          </button>
        </div>
      </form>

      {loading && (
        <div className="text-center text-sm text-theme-muted mt-6">
          <p>Provisioning your instance...</p>
          <p className="mt-1">This may take 2-3 minutes</p>
        </div>
      )}
    </div>
  );
};

export default CreateInstance;

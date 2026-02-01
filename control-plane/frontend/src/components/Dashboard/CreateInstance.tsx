import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInstances } from '../../contexts/InstanceContext';

const INSTANCE_TYPES = [
  {
    value: 't3.medium',
    label: 'Light',
    specs: '2 vCPU, 4GB RAM',
    price: '~$0.04/hr',
    supportsOpenclaw: true,
    note: 'Great for simple tasks'
  },
  {
    value: 't3.large',
    label: 'Regular',
    specs: '2 vCPU, 8GB RAM',
    price: '~$0.08/hr',
    supportsOpenclaw: true,
    recommended: true,
    note: 'Best for everyday use'
  },
  {
    value: 't3.xlarge',
    label: 'Pro',
    specs: '4 vCPU, 16GB RAM',
    price: '~$0.17/hr',
    supportsOpenclaw: true,
    pro: true,
    note: 'Maximum performance'
  },
];

// LLM providers supported by CloudBot
const LLM_PROVIDERS = [
  { id: 'anthropic', name: 'Anthropic', placeholder: 'sk-ant-api03-...', enabled: true },
  { id: 'openai', name: 'OpenAI', placeholder: 'sk-proj-...', enabled: false },
  { id: 'google', name: 'Google Gemini', placeholder: 'AIza...', enabled: false },
  { id: 'groq', name: 'Groq', placeholder: 'gsk_...', enabled: false },
  { id: 'openrouter', name: 'OpenRouter', placeholder: 'sk-or-...', enabled: false },
];

const CreateInstance: React.FC = () => {
  const [name, setName] = useState('');
  const [instanceType, setInstanceType] = useState('t3.large');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('anthropic');
  const [apiKey, setApiKey] = useState('');
  const { createInstance, selectInstance } = useInstances();
  const navigate = useNavigate();

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
            Choose the right size for your workload.
          </p>
          <div className="grid grid-cols-3 gap-3">
            {INSTANCE_TYPES.map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => setInstanceType(type.value)}
                className={`relative p-4 border rounded-lg text-left transition-all ${
                  instanceType === type.value
                    ? 'border-blue-500 bg-blue-500/10 ring-2 ring-blue-500'
                    : 'border-theme bg-theme-card hover:border-theme-hover'
                }`}
              >
                {type.recommended && (
                  <span className="absolute -top-2 right-2 px-2 py-0.5 text-xs bg-green-500 text-white rounded-full">
                    Popular
                  </span>
                )}
                {type.pro && (
                  <span className="absolute -top-2 right-2 px-2 py-0.5 text-xs bg-purple-500 text-white rounded-full">
                    Pro
                  </span>
                )}
                <div className="font-medium text-theme-primary">{type.label}</div>
                <div className="text-xs text-theme-muted mt-1">{type.specs}</div>
                <div className="text-xs text-theme-muted mt-0.5">{type.price}</div>
                {type.note && (
                  <div className="text-xs mt-1 text-green-500">
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
            AI Provider
          </label>
          <p className="text-xs text-theme-muted mb-3">
            Connect your API key to power the AI assistant.
          </p>

          {/* Provider radio list with inline input */}
          <div className="space-y-2">
            {LLM_PROVIDERS.map((provider) => (
              <div
                key={provider.id}
                className={`group relative flex items-center gap-3 p-3 border rounded-lg transition-all ${
                  !provider.enabled
                    ? 'border-theme bg-theme-card opacity-50 cursor-not-allowed'
                    : selectedProvider === provider.id
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-theme bg-theme-card'
                }`}
              >
                <input
                  type="radio"
                  name="llm-provider"
                  id={`provider-${provider.id}`}
                  value={provider.id}
                  checked={selectedProvider === provider.id}
                  disabled={!provider.enabled}
                  onChange={(e) => {
                    setSelectedProvider(e.target.value);
                    setApiKey('');
                  }}
                  className="w-4 h-4 text-blue-500 border-theme bg-theme-tertiary focus:ring-blue-500 disabled:opacity-50"
                />
                <label
                  htmlFor={`provider-${provider.id}`}
                  className={`text-sm min-w-[100px] ${
                    provider.enabled ? 'text-theme-primary cursor-pointer' : 'text-theme-muted cursor-not-allowed'
                  }`}
                >
                  {provider.name}
                </label>
                {provider.enabled && selectedProvider === provider.id && (
                  <input
                    type="password"
                    className="flex-1 px-3 py-1.5 border border-theme bg-theme-tertiary placeholder-theme-muted text-theme-primary rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                    placeholder={provider.placeholder || 'Enter API key'}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                  />
                )}
                {!provider.enabled && (
                  <span className="absolute right-3 px-2 py-0.5 text-xs bg-theme-tertiary text-theme-muted rounded border border-theme opacity-0 group-hover:opacity-100 transition-opacity">
                    Coming soon
                  </span>
                )}
              </div>
            ))}
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

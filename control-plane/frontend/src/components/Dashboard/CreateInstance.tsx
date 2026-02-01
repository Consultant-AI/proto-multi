import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInstances } from '../../contexts/InstanceContext';
import { useSubscription } from '../../contexts/SubscriptionContext';

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
  const { createInstance, selectInstance, instances } = useInstances();
  const { subscription, hasActiveSubscription, loading: subLoading } = useSubscription();
  const navigate = useNavigate();

  // Set instance type based on subscription plan
  useEffect(() => {
    if (subscription?.instance_type) {
      setInstanceType(subscription.instance_type);
    }
  }, [subscription]);

  // If no active subscription, redirect to select plan
  useEffect(() => {
    if (!subLoading && !hasActiveSubscription) {
      navigate('/select-plan');
    }
  }, [subLoading, hasActiveSubscription, navigate]);

  // Check if user has reached their worker limit
  const activeInstances = instances.filter(i => i.status !== 'terminated').length;
  const maxWorkers = subscription?.max_workers || 1;
  const canCreateMore = activeInstances < maxWorkers;

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

  if (subLoading) {
    return (
      <div className="max-w-xl mx-auto text-center py-12">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-theme-muted">Loading...</p>
      </div>
    );
  }

  if (!canCreateMore) {
    return (
      <div className="max-w-xl mx-auto">
        <div className="text-center py-12 px-6 border border-theme rounded-xl bg-theme-card">
          <div className="w-16 h-16 bg-yellow-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-theme-primary mb-2">Worker Limit Reached</h2>
          <p className="text-theme-secondary mb-6">
            You have {activeInstances} of {maxWorkers} workers active on your {subscription?.plan_type} plan.
            Upgrade your plan to add more workers.
          </p>
          <div className="flex gap-3 justify-center">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 border border-theme text-theme-secondary rounded-lg hover:bg-theme-secondary"
            >
              Back to Dashboard
            </button>
            <button
              type="button"
              onClick={() => navigate('/select-plan')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Upgrade Plan
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-theme-primary">
          Create New Instance
        </h2>
        <p className="mt-2 text-sm text-theme-muted">
          Ubuntu desktop with Chrome, VS Code, LibreOffice
        </p>
        {subscription && (
          <p className="mt-1 text-xs text-theme-muted">
            {activeInstances} of {maxWorkers} workers used ({subscription.plan_type} plan)
          </p>
        )}
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

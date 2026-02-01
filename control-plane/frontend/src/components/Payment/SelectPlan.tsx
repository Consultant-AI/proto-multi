import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSubscription } from '../../contexts/SubscriptionContext';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: 29,
    instanceType: 't3.medium',
    specs: '2 vCPU, 4GB RAM',
    maxWorkers: 2,
    features: [
      'Up to 2 cloud workers',
      'Ubuntu desktop with Chrome, VS Code',
      'Vision + mouse + keyboard control',
      'All app integrations',
      'Email support',
    ],
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 79,
    instanceType: 't3.large',
    specs: '2 vCPU, 8GB RAM',
    maxWorkers: 5,
    recommended: true,
    features: [
      'Up to 5 cloud workers',
      'Faster performance (8GB RAM)',
      'Priority task scheduling',
      'All Starter features',
      'Priority support',
    ],
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 199,
    instanceType: 't3.xlarge',
    specs: '4 vCPU, 16GB RAM',
    maxWorkers: 10,
    features: [
      'Up to 10 cloud workers',
      'Maximum performance (16GB RAM)',
      'Dedicated resources',
      'All Pro features',
      '24/7 premium support',
    ],
  },
];

const SelectPlan: React.FC = () => {
  const [selectedPlan, setSelectedPlan] = useState('pro');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { createCheckoutSession, hasActiveSubscription } = useSubscription();
  const navigate = useNavigate();

  // If user already has a subscription, redirect to dashboard
  React.useEffect(() => {
    if (hasActiveSubscription) {
      navigate('/dashboard');
    }
  }, [hasActiveSubscription, navigate]);

  const handleSubscribe = async () => {
    setLoading(true);
    setError('');

    try {
      const checkoutUrl = await createCheckoutSession(selectedPlan);
      // Redirect to Stripe Checkout
      window.location.href = checkoutUrl;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create checkout session');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-theme-primary py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-theme-primary mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-theme-secondary">
            Select the plan that fits your needs. Upgrade or downgrade anytime.
          </p>
        </div>

        {error && (
          <div className="max-w-md mx-auto mb-8 rounded-lg bg-red-500/10 border border-red-500 p-4">
            <p className="text-sm text-red-500 text-center">{error}</p>
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              onClick={() => setSelectedPlan(plan.id)}
              className={`relative p-6 rounded-2xl border-2 cursor-pointer transition-all ${
                selectedPlan === plan.id
                  ? 'border-blue-500 bg-blue-500/5 shadow-xl shadow-blue-500/10'
                  : 'border-theme bg-theme-card hover:border-theme-hover'
              }`}
            >
              {plan.recommended && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-blue-500 text-white text-xs font-semibold px-3 py-1 rounded-full">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-xl font-bold text-theme-primary mb-2">{plan.name}</h3>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-4xl font-bold text-theme-primary">${plan.price}</span>
                  <span className="text-theme-muted">/month</span>
                </div>
                <p className="text-sm text-theme-muted mt-2">
                  {plan.specs}
                </p>
              </div>

              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-theme-secondary">
                    <svg className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <div
                className={`w-full py-3 rounded-lg font-semibold text-center transition-colors ${
                  selectedPlan === plan.id
                    ? 'bg-blue-500 text-white'
                    : 'bg-theme-tertiary text-theme-secondary'
                }`}
              >
                {selectedPlan === plan.id ? 'Selected' : 'Select Plan'}
              </div>
            </div>
          ))}
        </div>

        <div className="max-w-md mx-auto text-center">
          <button
            onClick={handleSubscribe}
            disabled={loading}
            className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg text-lg transition-colors"
          >
            {loading ? 'Redirecting to checkout...' : 'Continue to Payment'}
          </button>

          <p className="mt-4 text-sm text-theme-muted">
            Secure payment powered by Stripe. Cancel anytime.
          </p>

          <div className="mt-8 flex justify-center gap-6 text-sm text-theme-muted">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              SSL Encrypted
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Money-back guarantee
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SelectPlan;

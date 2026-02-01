import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import api from '../services/api';
import { useAuth } from './AuthContext';

interface Subscription {
  id: string;
  plan_type: string;
  status: string;
  instance_type: string;
  max_workers: number;
  current_period_end: string | null;
}

interface StripeConfig {
  publishable_key: string;
  plans: {
    [key: string]: {
      name: string;
      instance_type: string;
      max_workers: number;
    };
  };
}

interface SubscriptionContextType {
  subscription: Subscription | null;
  loading: boolean;
  stripeConfig: StripeConfig | null;
  hasActiveSubscription: boolean;
  createCheckoutSession: (planType: string) => Promise<string>;
  refreshSubscription: () => Promise<void>;
  cancelSubscription: () => Promise<void>;
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(undefined);

export const SubscriptionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [stripeConfig, setStripeConfig] = useState<StripeConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchSubscription();
      fetchStripeConfig();
    } else {
      setSubscription(null);
      setLoading(false);
    }
  }, [user]);

  const fetchStripeConfig = async () => {
    try {
      const response = await api.get('/api/payments/config');
      setStripeConfig(response.data);
    } catch (error) {
      console.error('Failed to fetch Stripe config:', error);
    }
  };

  const fetchSubscription = async () => {
    try {
      const response = await api.get('/api/payments/subscription');
      setSubscription(response.data);
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
      setSubscription(null);
    } finally {
      setLoading(false);
    }
  };

  const createCheckoutSession = async (planType: string): Promise<string> => {
    const response = await api.post('/api/payments/create-checkout', {
      plan_type: planType,
      success_url: `${window.location.origin}/payment-success`,
      cancel_url: `${window.location.origin}/select-plan`,
    });
    return response.data.checkout_url;
  };

  const refreshSubscription = async () => {
    setLoading(true);
    await fetchSubscription();
  };

  const cancelSubscription = async () => {
    await api.post('/api/payments/cancel');
    await fetchSubscription();
  };

  const hasActiveSubscription = subscription?.status === 'active';

  return (
    <SubscriptionContext.Provider
      value={{
        subscription,
        loading,
        stripeConfig,
        hasActiveSubscription,
        createCheckoutSession,
        refreshSubscription,
        cancelSubscription,
      }}
    >
      {children}
    </SubscriptionContext.Provider>
  );
};

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (context === undefined) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
};

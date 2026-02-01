import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useSubscription } from '../../contexts/SubscriptionContext';

const PaymentSuccess: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshSubscription } = useSubscription();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    const sessionId = searchParams.get('session_id');

    if (!sessionId) {
      setStatus('error');
      return;
    }

    // Refresh subscription to get the new status
    const checkSubscription = async () => {
      try {
        await refreshSubscription();
        setStatus('success');

        // Redirect to dashboard after 3 seconds
        setTimeout(() => {
          navigate('/dashboard');
        }, 3000);
      } catch (error) {
        console.error('Failed to refresh subscription:', error);
        setStatus('error');
      }
    };

    checkSubscription();
  }, [searchParams, refreshSubscription, navigate]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-theme-primary flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-theme-secondary">Processing your payment...</p>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen bg-theme-primary flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-theme-primary mb-2">Something went wrong</h1>
          <p className="text-theme-secondary mb-6">
            We couldn't verify your payment. Please contact support if you were charged.
          </p>
          <button
            onClick={() => navigate('/select-plan')}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-theme-primary flex items-center justify-center">
      <div className="text-center max-w-md mx-auto px-4">
        <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="text-3xl font-bold text-theme-primary mb-3">Payment Successful!</h1>
        <p className="text-lg text-theme-secondary mb-6">
          Your subscription is now active. Let's create your first AI cloud worker!
        </p>
        <div className="space-y-3">
          <button
            onClick={() => navigate('/create-instance')}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            Create Your First Worker
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full px-6 py-3 border border-theme text-theme-secondary hover:bg-theme-secondary font-semibold rounded-lg transition-colors"
          >
            Go to Dashboard
          </button>
        </div>
        <p className="mt-6 text-sm text-theme-muted">
          Redirecting to dashboard in a few seconds...
        </p>
      </div>
    </div>
  );
};

export default PaymentSuccess;

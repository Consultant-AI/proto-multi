import React, { useState } from 'react';

interface WaitlistFormProps {
  variant?: 'default' | 'hero' | 'footer';
  className?: string;
}

const WaitlistForm: React.FC<WaitlistFormProps> = ({ variant = 'default', className = '' }) => {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      setStatus('error');
      setMessage('Please enter a valid email address');
      return;
    }

    setStatus('loading');

    // TODO: Integrate with actual waitlist API
    // For now, simulate API call
    setTimeout(() => {
      setStatus('success');
      setMessage('You\'re on the list! We\'ll be in touch soon.');
      setEmail('');
    }, 1000);
  };

  const isHero = variant === 'hero';
  const isFooter = variant === 'footer';

  if (status === 'success') {
    return (
      <div className={`${className} flex items-center justify-center`}>
        <div className={`flex items-center gap-2 ${isFooter ? 'text-white' : 'text-green-500'}`}>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span className="font-medium">{message}</span>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className={`${className}`}>
      <div className={`flex ${isHero ? 'flex-col sm:flex-row' : 'flex-col sm:flex-row'} gap-3`}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          className={`
            flex-1 px-4 py-3 rounded-lg border transition-all
            ${isFooter
              ? 'bg-white/10 border-white/20 text-white placeholder-white/60 focus:border-white focus:ring-2 focus:ring-white/30'
              : 'bg-theme-primary border-theme text-theme-primary placeholder-theme-muted focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
            }
            outline-none
          `}
          disabled={status === 'loading'}
        />
        <button
          type="submit"
          disabled={status === 'loading'}
          className={`
            px-6 py-3 font-medium rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap
            ${isFooter
              ? 'bg-white text-blue-600 hover:bg-gray-100 shadow-lg'
              : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg'
            }
          `}
        >
          {status === 'loading' ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Joining...
            </span>
          ) : (
            'Join Waitlist'
          )}
        </button>
      </div>
      {status === 'error' && (
        <p className="mt-2 text-red-500 text-sm">{message}</p>
      )}
    </form>
  );
};

export default WaitlistForm;

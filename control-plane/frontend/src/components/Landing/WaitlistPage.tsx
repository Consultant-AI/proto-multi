import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';

const WaitlistPage: React.FC = () => {
  const { theme } = useTheme();
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState<'form' | 'success'>('form');
  const [loading, setLoading] = useState(false);
  const [hasPrefilledEmail, setHasPrefilledEmail] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    company: '',
    role: '',
    teamSize: '',
    useCase: '',
    useCaseDetails: '',
    howHeard: '',
  });

  // Check for pre-filled email from URL params
  useEffect(() => {
    const emailParam = searchParams.get('email');
    if (emailParam) {
      setFormData(prev => ({ ...prev, email: emailParam }));
      setHasPrefilledEmail(true);
    }
  }, [searchParams]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // TODO: Integrate with actual waitlist API
    console.log('Waitlist signup:', formData);

    setTimeout(() => {
      setLoading(false);
      setStep('success');
    }, 1500);
  };

  if (step === 'success') {
    return (
      <div className={`min-h-screen ${theme === 'dark' ? 'dark' : 'light'} bg-theme-primary text-theme-primary`}>
        <div className="max-w-2xl mx-auto px-6 py-20">
          {/* Success State */}
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/20 mb-8">
              <svg className="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <h1 className="text-4xl font-bold mb-4">You're on the list! 🎉</h1>
            <p className="text-xl text-theme-secondary mb-8">
              Thanks for joining the CloudBot waitlist, {formData.name || 'friend'}!
            </p>

            <div className="bg-theme-card border border-theme rounded-2xl p-8 mb-8 text-left">
              <h2 className="text-lg font-semibold mb-4">What happens next?</h2>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 text-white text-sm flex items-center justify-center">1</span>
                  <div>
                    <p className="font-medium">Check your inbox</p>
                    <p className="text-sm text-theme-muted">We've sent a confirmation to {formData.email}</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 text-white text-sm flex items-center justify-center">2</span>
                  <div>
                    <p className="font-medium">Early access invitation</p>
                    <p className="text-sm text-theme-muted">We're rolling out access in batches. You'll hear from us soon.</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 text-white text-sm flex items-center justify-center">3</span>
                  <div>
                    <p className="font-medium">Get started</p>
                    <p className="text-sm text-theme-muted">Once invited, launch your first AI worker in under 5 minutes.</p>
                  </div>
                </li>
              </ul>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Back to Home
              </Link>
              <a
                href="https://twitter.com/cloudbot"
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 border border-theme rounded-lg font-medium hover:bg-theme-secondary transition-colors"
              >
                Follow us on X
              </a>
            </div>

            <p className="text-sm text-theme-muted mt-12">
              Questions? Email us at <a href="mailto:hello@cloudbot.ai" className="text-blue-500 hover:underline">hello@cloudbot.ai</a>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : 'light'} bg-theme-primary text-theme-primary`}>
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-12">
          <Link to="/" className="flex items-center gap-2 text-xl font-bold hover:text-blue-500 transition-colors">
            <span>🤖</span>
            <span>CloudBot</span>
          </Link>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Left - Info */}
          <div>
            <div className="inline-block px-3 py-1 rounded-full bg-blue-500/10 text-blue-500 text-sm font-medium mb-6">
              Early Access
            </div>
            <h1 className="text-4xl lg:text-5xl font-bold mb-6 leading-tight">
              Get your AI cloud worker
            </h1>
            <p className="text-xl text-theme-secondary mb-8">
              Join 2,500+ companies on the waitlist. Be among the first to automate tedious computer tasks with AI.
            </p>

            {/* Features */}
            <div className="space-y-4 mb-8">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-theme-tertiary flex items-center justify-center text-xl">🖥️</div>
                <div>
                  <p className="font-medium">Real cloud computer</p>
                  <p className="text-sm text-theme-muted">Ubuntu desktop with browser, apps, terminal</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-theme-tertiary flex items-center justify-center text-xl">👁️</div>
                <div>
                  <p className="font-medium">Vision + mouse + keyboard</p>
                  <p className="text-sm text-theme-muted">AI sees and controls the screen like a human</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-theme-tertiary flex items-center justify-center text-xl">🧠</div>
                <div>
                  <p className="font-medium">Memory system</p>
                  <p className="text-sm text-theme-muted">Learns your preferences and workflows</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-theme-tertiary flex items-center justify-center text-xl">💬</div>
                <div>
                  <p className="font-medium">Works anywhere</p>
                  <p className="text-sm text-theme-muted">Slack, Teams, WhatsApp, Email, SMS</p>
                </div>
              </div>
            </div>

            {/* Testimonial/Social proof */}
            <div className="bg-theme-card border border-theme rounded-xl p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white font-bold">
                  S
                </div>
                <div>
                  <p className="text-sm">
                    "CloudBot saved our ops team 20+ hours/week on CRM updates alone."
                  </p>
                  <p className="text-xs text-theme-muted mt-1">Sarah K., Head of Operations at TechCorp</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right - Form */}
          <div className="bg-theme-card border border-theme rounded-2xl p-8">
            {hasPrefilledEmail ? (
              <>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🎉</span>
                  <h2 className="text-2xl font-semibold">You're almost there!</h2>
                </div>
                <p className="text-theme-secondary mb-6">
                  Great, we have your email! Just a few more details to complete your signup.
                </p>
              </>
            ) : (
              <>
                <h2 className="text-2xl font-semibold mb-2">Join the waitlist</h2>
                <p className="text-theme-secondary mb-6">Fill out the form below and we'll be in touch.</p>
              </>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-2">
                  Work email *
                  {hasPrefilledEmail && <span className="text-green-500 ml-2">✓ Saved</span>}
                </label>
                <div className="relative">
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="you@company.com"
                    className={`w-full px-4 py-3 rounded-lg border text-theme-primary placeholder-theme-muted focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all ${
                      hasPrefilledEmail
                        ? 'border-green-500/50 bg-green-500/5'
                        : 'border-theme bg-theme-input'
                    }`}
                  />
                  {hasPrefilledEmail && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>

              {/* Name */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium mb-2">Your name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="John Smith"
                  className="w-full px-4 py-3 rounded-lg border border-theme bg-theme-input text-theme-primary placeholder-theme-muted focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                />
              </div>

              {/* Company & Role */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="company" className="block text-sm font-medium mb-2">Company *</label>
                  <input
                    type="text"
                    id="company"
                    name="company"
                    value={formData.company}
                    onChange={handleChange}
                    required
                    placeholder="Acme Inc"
                    className="w-full px-4 py-3 rounded-lg border border-theme bg-theme-input text-theme-primary placeholder-theme-muted focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  />
                </div>
                <div>
                  <label htmlFor="role" className="block text-sm font-medium mb-2">Your role</label>
                  <input
                    type="text"
                    id="role"
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    placeholder="VP of Ops"
                    className="w-full px-4 py-3 rounded-lg border border-theme bg-theme-input text-theme-primary placeholder-theme-muted focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  />
                </div>
              </div>

              {/* Team Size */}
              <div>
                <label htmlFor="teamSize" className="block text-sm font-medium mb-2">Team size</label>
                <select
                  id="teamSize"
                  name="teamSize"
                  value={formData.teamSize}
                  onChange={handleChange}
                  aria-label="Team size"
                  className="w-full px-4 py-3 rounded-lg border border-theme bg-theme-input text-theme-primary focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                >
                  <option value="">Select team size</option>
                  <option value="1-10">1-10 employees</option>
                  <option value="11-50">11-50 employees</option>
                  <option value="51-200">51-200 employees</option>
                  <option value="201-500">201-500 employees</option>
                  <option value="500+">500+ employees</option>
                </select>
              </div>

              {/* Use Case */}
              <div>
                <label htmlFor="useCase" className="block text-sm font-medium mb-2">Primary use case *</label>
                <select
                  id="useCase"
                  name="useCase"
                  value={formData.useCase}
                  onChange={handleChange}
                  required
                  aria-label="Primary use case"
                  className="w-full px-4 py-3 rounded-lg border border-theme bg-theme-input text-theme-primary focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                >
                  <option value="">What will you use CloudBot for?</option>
                  <option value="sales">Sales & CRM automation</option>
                  <option value="recruiting">HR & Recruiting</option>
                  <option value="finance">Finance & Admin</option>
                  <option value="research">Research & Data</option>
                  <option value="marketing">Marketing & Social</option>
                  <option value="development">Development & DevOps</option>
                  <option value="customer-support">Customer Support</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Use Case Details */}
              <div>
                <label htmlFor="useCaseDetails" className="block text-sm font-medium mb-2">
                  Tell us more <span className="text-theme-muted font-normal">(optional)</span>
                </label>
                <textarea
                  id="useCaseDetails"
                  name="useCaseDetails"
                  value={formData.useCaseDetails}
                  onChange={handleChange}
                  rows={3}
                  placeholder="Describe the tasks you'd like CloudBot to handle..."
                  className="w-full px-4 py-3 rounded-lg border border-theme bg-theme-input text-theme-primary placeholder-theme-muted focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none"
                />
              </div>

              {/* How did you hear */}
              <div>
                <label htmlFor="howHeard" className="block text-sm font-medium mb-2">How did you hear about us?</label>
                <select
                  id="howHeard"
                  name="howHeard"
                  value={formData.howHeard}
                  onChange={handleChange}
                  aria-label="How did you hear about us"
                  className="w-full px-4 py-3 rounded-lg border border-theme bg-theme-input text-theme-primary focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                >
                  <option value="">Select an option</option>
                  <option value="twitter">Twitter/X</option>
                  <option value="linkedin">LinkedIn</option>
                  <option value="google">Google Search</option>
                  <option value="friend">Friend/Colleague</option>
                  <option value="podcast">Podcast</option>
                  <option value="blog">Blog/Article</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Joining...
                  </span>
                ) : (
                  'Join the Waitlist'
                )}
              </button>

              <p className="text-center text-xs text-theme-muted">
                No credit card required. We'll email you when it's your turn.
              </p>
            </form>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-theme text-center text-sm text-theme-muted">
          <p>© 2026 CloudBot Inc. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default WaitlistPage;

import React from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';

const PrivacyPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-theme-primary text-theme-primary">
      {/* Nav */}
      <nav className="fixed top-0 w-full bg-theme-primary/80 backdrop-blur-md border-b border-theme z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-xl">🤖</span>
            <span className="text-sm font-medium">CloudBot</span>
            <span className="text-[10px] px-1.5 py-0.5 bg-blue-500/20 text-blue-400 rounded-full">BETA</span>
          </Link>
          <button
            type="button"
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-theme-secondary transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </nav>

      {/* Content */}
      <main className="pt-24 pb-16 px-6">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Privacy Policy</h1>
          <p className="text-theme-muted mb-8">Last updated: January 30, 2026</p>

          <div className="prose prose-invert max-w-none space-y-6 text-theme-secondary">
            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">1. Introduction</h2>
              <p>CloudBot Inc. ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our cloud AI worker platform.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">2. Information We Collect</h2>
              <h3 className="text-lg font-medium text-theme-primary mb-2">Account Information</h3>
              <p>When you create an account, we collect your email address, name, company name, and billing information.</p>

              <h3 className="text-lg font-medium text-theme-primary mb-2 mt-4">Usage Data</h3>
              <p>We collect information about how you interact with our platform, including task logs, session data, and performance metrics to improve our service.</p>

              <h3 className="text-lg font-medium text-theme-primary mb-2 mt-4">Third-Party Credentials</h3>
              <p>When you connect third-party services, credentials are encrypted and stored securely. We never have access to your plaintext passwords.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">3. How We Use Your Information</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>To provide and maintain our service</li>
                <li>To process transactions and send billing information</li>
                <li>To respond to your requests and support needs</li>
                <li>To improve our platform and develop new features</li>
                <li>To send service-related communications</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">4. Data Security</h2>
              <p>We implement industry-standard security measures including:</p>
              <ul className="list-disc pl-6 space-y-2 mt-2">
                <li>Encryption at rest and in transit (AES-256, TLS 1.3)</li>
                <li>Isolated cloud containers for each worker instance</li>
                <li>Regular security audits and penetration testing</li>
                <li>SOC 2 Type II compliance</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">5. Data Retention</h2>
              <p>Your data is retained only as long as necessary to provide our services. When you terminate a worker, all associated data is deleted within 30 days. You can request data export at any time.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">6. Your Rights</h2>
              <p>You have the right to:</p>
              <ul className="list-disc pl-6 space-y-2 mt-2">
                <li>Access your personal data</li>
                <li>Correct inaccurate data</li>
                <li>Request deletion of your data</li>
                <li>Export your data in a portable format</li>
                <li>Opt out of marketing communications</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">7. Cookies</h2>
              <p>We use essential cookies to maintain your session and remember your preferences. We do not use tracking cookies for advertising purposes.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">8. Contact Us</h2>
              <p>For privacy-related inquiries, contact us at:</p>
              <p className="mt-2">
                <a href="mailto:privacy@cloudbot.ai" className="text-blue-400 hover:underline">privacy@cloudbot.ai</a>
              </p>
            </section>
          </div>

          <div className="mt-12 pt-8 border-t border-theme">
            <Link to="/" className="text-blue-400 hover:underline">← Back to Home</Link>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PrivacyPage;

import React from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';

const TermsPage: React.FC = () => {
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
          <h1 className="text-3xl font-bold mb-2">Terms of Service</h1>
          <p className="text-theme-muted mb-8">Last updated: January 30, 2026</p>

          <div className="prose prose-invert max-w-none space-y-6 text-theme-secondary">
            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">1. Acceptance of Terms</h2>
              <p>By accessing or using CloudBot's services, you agree to be bound by these Terms of Service. If you do not agree to these terms, do not use our services.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">2. Description of Service</h2>
              <p>CloudBot provides AI-powered cloud workers that operate real virtual desktops to perform computer-based tasks on your behalf. Each worker runs in an isolated cloud environment with its own browser, applications, and file system.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">3. Account Responsibilities</h2>
              <p>You are responsible for:</p>
              <ul className="list-disc pl-6 space-y-2 mt-2">
                <li>Maintaining the security of your account credentials</li>
                <li>All activities that occur under your account</li>
                <li>Ensuring that your use complies with applicable laws</li>
                <li>Providing accurate and complete registration information</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">4. Acceptable Use</h2>
              <p>You agree NOT to use CloudBot for:</p>
              <ul className="list-disc pl-6 space-y-2 mt-2">
                <li>Any illegal activities or to violate any laws</li>
                <li>Unauthorized access to third-party systems</li>
                <li>Spamming, phishing, or sending unsolicited communications</li>
                <li>Scraping data in violation of website terms of service</li>
                <li>Activities that could harm, overload, or impair our systems</li>
                <li>Circumventing security measures or access controls</li>
                <li>Automated account creation or credential stuffing</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">5. Third-Party Services</h2>
              <p>When you connect CloudBot to third-party services (CRM, email, etc.), you are responsible for:</p>
              <ul className="list-disc pl-6 space-y-2 mt-2">
                <li>Ensuring you have permission to use those services</li>
                <li>Complying with the third-party's terms of service</li>
                <li>Any fees or charges from the third-party service</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">6. Billing and Payment</h2>
              <p>Subscription fees are billed monthly or annually in advance. You authorize us to charge your payment method for all applicable fees. Refunds are provided on a case-by-case basis.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">7. Service Availability</h2>
              <p>We strive for 99.9% uptime but do not guarantee uninterrupted service. Scheduled maintenance will be communicated in advance. We are not liable for downtime or data loss.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">8. Intellectual Property</h2>
              <p>You retain ownership of your data and content. CloudBot retains ownership of the platform, technology, and any improvements made based on aggregate usage data (not your specific data).</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">9. Limitation of Liability</h2>
              <p>CloudBot is provided "as is" without warranties. We are not liable for indirect, incidental, or consequential damages. Our total liability is limited to the fees paid in the 12 months preceding the claim.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">10. Termination</h2>
              <p>Either party may terminate the service at any time. Upon termination, your access will be revoked and data will be deleted within 30 days. You can export your data before termination.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">11. Changes to Terms</h2>
              <p>We may update these terms from time to time. Material changes will be communicated via email or in-app notification. Continued use after changes constitutes acceptance.</p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-theme-primary mb-3">12. Contact</h2>
              <p>For questions about these terms, contact us at:</p>
              <p className="mt-2">
                <a href="mailto:legal@cloudbot.ai" className="text-blue-400 hover:underline">legal@cloudbot.ai</a>
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

export default TermsPage;

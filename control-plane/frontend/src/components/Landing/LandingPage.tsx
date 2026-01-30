import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import AuthModal from './AuthModal';
import WaitlistForm from './WaitlistForm';

// Icons
const SunIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
);

const MoonIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
  </svg>
);

const ChevronIcon: React.FC<{ className?: string; isOpen?: boolean }> = ({ className, isOpen }) => (
  <svg className={`${className} transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
  </svg>
);

// Capabilities
const capabilities = [
  { emoji: '✋', title: 'AI with Hands', desc: 'Real agency, not just text' },
  { emoji: '👁️', title: 'Vision Control', desc: 'Sees, clicks, types' },
  { emoji: '💻', title: 'Code Execution', desc: 'Runs commands & scripts' },
  { emoji: '🧠', title: 'Second Brain', desc: 'Evolving memory' },
  { emoji: '⏰', title: 'Long Tasks', desc: 'Hours or days of work' },
  { emoji: '📊', title: 'Visual Output', desc: 'Charts & dashboards' },
  { emoji: '🔧', title: 'Self-Improving', desc: 'Writes new skills' },
  { emoji: '💡', title: 'Proactive', desc: 'Initiates actions' },
];

// Use cases
const useCases = [
  { emoji: '🔬', title: 'Research', items: ['Deep web analysis', 'Competitive intel', 'Report generation'] },
  { emoji: '👨‍💻', title: 'Development', items: ['PR reviews', 'Bug monitoring', 'CI/CD management'] },
  { emoji: '📈', title: 'Operations', items: ['Email triage', 'Data processing', 'Task automation'] },
  { emoji: '💹', title: 'Finance', items: ['Market monitoring', 'Portfolio tracking', 'Analytics'] },
];

// Tiers
const tiers = [
  { emoji: '👤', name: 'Starter', spec: '2 CPU · 4GB · 20GB', desc: 'Single tasks, chat' },
  { emoji: '👥', name: 'Team', spec: '4 CPU · 8GB · 40GB', desc: 'Multi-channel, alerts', featured: true },
  { emoji: '🏢', name: 'Scale', spec: '16 CPU · 32GB · 100GB+', desc: 'Agent swarms' },
];

// Security
const security = [
  { emoji: '🔒', title: 'Isolated', desc: 'Secure containers' },
  { emoji: '🔐', title: 'Encrypted', desc: 'At rest & in transit' },
  { emoji: '🚫', title: 'No retention', desc: 'Your data stays yours' },
  { emoji: '📝', title: 'Audit logs', desc: 'Complete history' },
  { emoji: '👥', title: 'Access control', desc: 'RBAC & SSO' },
  { emoji: '✅', title: 'Compliant', desc: 'SOC 2 ready' },
];

// FAQ
const faqs = [
  { q: 'What can CloudBot do?', a: 'Control any desktop application, browse the web, write and run code, manage files, create documents — anything you can do on a computer.' },
  { q: 'How is this different from ChatGPT?', a: 'Traditional AI waits for prompts. CloudBot has a real computer with hands — it sees the screen, moves the mouse, types, and proactively initiates tasks.' },
  { q: 'What is "Second Brain"?', a: 'Persistent memory that evolves. It learns your preferences, remembers past projects, and builds context across sessions — never forgets.' },
  { q: 'Can it work overnight?', a: 'Yes. CloudBot runs 24/7 on cloud infrastructure. Start long-running tasks that span hours or days, get alerts when done.' },
  { q: 'Is my data secure?', a: 'Each instance runs isolated. Data is encrypted. Nothing is used for training. Complete audit logs for compliance.' },
  { q: 'Can multiple workers collaborate?', a: 'Yes. Multi-instance orchestration lets you spin up agent swarms that coordinate on complex projects in parallel.' },
];

// Integrations
const integrations = [
  { emoji: '💬', name: 'Slack' },
  { emoji: '📧', name: 'Email' },
  { emoji: '📱', name: 'WhatsApp' },
  { emoji: '✈️', name: 'Telegram' },
  { emoji: '📅', name: 'Calendar' },
  { emoji: '🔗', name: 'API' },
];

const LandingPage: React.FC = () => {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('signup');
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
  const { theme, toggleTheme } = useTheme();

  const handleSignIn = () => {
    setAuthMode('login');
    setShowAuthModal(true);
  };

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-theme-primary text-theme-primary">
      {/* Nav */}
      <nav className="fixed top-0 w-full bg-theme-primary/80 backdrop-blur-md border-b border-theme z-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex justify-between items-center h-14">
            <div className="flex items-center gap-3">
              <span className="text-xl">🤖</span>
              <span className="text-lg font-semibold tracking-tight">CloudBot</span>
              <span className="text-[10px] font-medium text-blue-500 border border-blue-500/30 px-1.5 py-0.5 rounded">BETA</span>
            </div>
            <div className="hidden md:flex items-center gap-8 text-sm text-theme-muted">
              <button type="button" onClick={() => scrollToSection('features')} className="hover:text-theme-primary transition-colors">Features</button>
              <button type="button" onClick={() => scrollToSection('pricing')} className="hover:text-theme-primary transition-colors">Pricing</button>
              <button type="button" onClick={() => scrollToSection('faq')} className="hover:text-theme-primary transition-colors">FAQ</button>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={toggleTheme}
                className="p-2 text-theme-muted hover:text-theme-primary transition-colors"
                aria-label="Toggle theme"
              >
                {theme === 'dark' ? <SunIcon className="w-4 h-4" /> : <MoonIcon className="w-4 h-4" />}
              </button>
              <button type="button" onClick={handleSignIn} className="text-sm text-theme-muted hover:text-theme-primary transition-colors px-3 py-1.5">
                Sign in
              </button>
              <button
                type="button"
                onClick={() => scrollToSection('waitlist')}
                className="text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white px-4 py-1.5 rounded transition-colors"
              >
                Join waitlist ✨
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 relative overflow-hidden">
        {/* Subtle gradient bg */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/3 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-3xl" />
          <div className="absolute top-20 right-1/3 w-[400px] h-[400px] bg-purple-500/5 rounded-full blur-3xl" />
        </div>

        <div className="max-w-3xl mx-auto relative">
          <div className="flex items-center gap-2 text-sm text-theme-muted mb-6">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
            Early access · Limited spots
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight leading-[1.1] mb-6">
            AI Cloud Workers
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500">with Real Computers 🖥️</span>
          </h1>

          <p className="text-xl text-theme-secondary max-w-xl mb-4 leading-relaxed">
            Not chatbots — AI employees with their own cloud desktops
          </p>

          <p className="text-base text-theme-muted max-w-lg mb-10 leading-relaxed">
            Each worker gets a real computer they control: see the screen 👁️, move the mouse 🖱️, type ⌨️, run code 💻, browse 🌐. Like a remote employee that never sleeps 🌙
          </p>

          <div className="flex flex-col sm:flex-row gap-3 mb-8">
            <div className="flex-1 max-w-sm">
              <WaitlistForm variant="hero" />
            </div>
          </div>

          <p className="text-xs text-theme-muted">
            ⭐ 2,500+ companies on the waitlist
          </p>
        </div>

        {/* Hero Screenshot - Main product view */}
        <div className="max-w-5xl mx-auto mt-16 relative">
          <div className="border border-theme rounded-xl overflow-hidden shadow-2xl shadow-black/20">
            {/* Window chrome */}
            <div className="flex items-center gap-2 px-4 py-2.5 border-b border-theme bg-theme-secondary">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
              </div>
              <span className="text-xs text-theme-muted ml-2 font-mono">cloudbot-worker-01</span>
              <div className="ml-auto flex items-center gap-3 text-xs text-theme-muted">
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" /> Connected</span>
              </div>
            </div>
            {/* Split view */}
            <div className="aspect-[16/9] bg-[#1a1a2e] flex">
              {/* Left - Ubuntu Desktop */}
              <div className="flex-[2] flex flex-col bg-gradient-to-br from-[#300a24] to-[#2c001e]">
                {/* Ubuntu top bar */}
                <div className="h-7 bg-[#2c001e] flex items-center px-4 text-[10px] text-white/70">
                  <span className="font-medium">Activities</span>
                  <div className="flex-1 text-center font-medium">Thu Jan 30  14:32</div>
                  <div className="flex items-center gap-3">
                    <span>🔊</span>
                    <span>📶</span>
                    <span>🔋</span>
                  </div>
                </div>

                {/* Desktop area */}
                <div className="flex-1 p-3 relative">
                  {/* Chrome browser - main window */}
                  <div className="absolute top-3 left-3 right-20 bottom-3 bg-[#202124] rounded-lg border border-white/10 shadow-2xl overflow-hidden flex flex-col">
                    {/* Chrome header */}
                    <div className="flex items-center gap-2 px-3 py-2 bg-[#35363a] border-b border-white/10">
                      <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500" />
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                      </div>
                      {/* Tabs */}
                      <div className="flex gap-1 ml-2">
                        <div className="bg-[#202124] px-4 py-1.5 rounded-t text-[10px] text-white/90 flex items-center gap-2">
                          <span className="text-blue-400">🔵</span> Crunchbase - AI Startups
                        </div>
                        <div className="bg-white/5 px-3 py-1.5 rounded-t text-[10px] text-white/50">
                          Google Docs
                        </div>
                        <div className="bg-white/5 px-3 py-1.5 rounded-t text-[10px] text-white/50">
                          +
                        </div>
                      </div>
                    </div>
                    {/* URL bar */}
                    <div className="px-3 py-2 bg-[#202124] border-b border-white/10 flex items-center gap-2">
                      <div className="flex gap-2 text-white/40">
                        <span>←</span><span>→</span><span>↻</span>
                      </div>
                      <div className="flex-1 bg-[#35363a] rounded-full px-4 py-1 text-[10px] text-white/70 flex items-center gap-2">
                        <span>🔒</span> crunchbase.com/lists/ai-startups-2024
                      </div>
                    </div>
                    {/* Page content */}
                    <div className="flex-1 p-4 bg-[#202124] overflow-hidden">
                      <div className="text-white/90 font-medium text-sm mb-4">Top AI Startups 2024</div>
                      <div className="grid grid-cols-2 gap-3">
                        {['OpenAI • $11.3B', 'Anthropic • $7.3B', 'Mistral • $2B', 'Cohere • $2.1B', 'Perplexity • $520M', 'Runway • $500M'].map((company, i) => (
                          <div key={i} className="bg-white/5 rounded-lg p-3 text-[10px] hover:bg-white/10 transition-colors">
                            <div className="text-white/90 font-medium">{company.split(' • ')[0]}</div>
                            <div className="text-green-400 mt-1">{company.split(' • ')[1]} raised</div>
                          </div>
                        ))}
                      </div>
                      {/* Mouse cursor */}
                      <div className="absolute bottom-20 left-40 flex items-center gap-2">
                        <svg className="w-5 h-5 text-white drop-shadow-lg" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M4 4l16 8-7 2-2 7z"/>
                        </svg>
                        <span className="text-[9px] text-blue-400 bg-blue-500/20 px-2 py-0.5 rounded animate-pulse">selecting data</span>
                      </div>
                    </div>
                  </div>

                  {/* VS Code - behind */}
                  <div className="absolute top-8 right-3 w-40 h-32 bg-[#1e1e1e] rounded-lg border border-white/10 shadow-xl overflow-hidden opacity-90">
                    <div className="flex items-center gap-1 px-2 py-1.5 bg-[#323233]">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 rounded-full bg-red-500/70" />
                        <div className="w-2 h-2 rounded-full bg-yellow-500/70" />
                        <div className="w-2 h-2 rounded-full bg-green-500/70" />
                      </div>
                      <span className="text-[8px] text-white/50 ml-1">VS Code</span>
                    </div>
                    <div className="p-2 font-mono text-[8px] text-white/60">
                      <div><span className="text-purple-400">import</span> pandas</div>
                      <div><span className="text-purple-400">def</span> <span className="text-yellow-300">analyze</span>():</div>
                      <div className="pl-2">df = pd.read...</div>
                    </div>
                  </div>
                </div>

                {/* Ubuntu dock */}
                <div className="h-14 bg-[#2c001e]/90 backdrop-blur border-t border-white/10 flex items-center justify-center gap-2 px-4">
                  <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center text-xl hover:bg-white/20 transition-colors border-b-2 border-orange-500">🦊</div>
                  <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center text-xl hover:bg-white/20 transition-colors">📁</div>
                  <div className="w-10 h-10 bg-blue-500/30 rounded-xl flex items-center justify-center text-xl hover:bg-white/20 transition-colors border-b-2 border-blue-500">💻</div>
                  <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center text-xl hover:bg-white/20 transition-colors">⬛</div>
                  <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center text-xl hover:bg-white/20 transition-colors">⚙️</div>
                </div>
              </div>

              {/* Right - Chat panel */}
              <div className="w-48 border-l border-white/10 bg-[#0f0f1a] flex flex-col">
                <div className="p-2 border-b border-white/10 flex items-center gap-2">
                  <span className="text-sm">🤖</span>
                  <span className="text-[10px] text-white/90 font-medium">CloudBot</span>
                  <span className="ml-auto text-[8px] text-green-400 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" /> Online
                  </span>
                </div>
                <div className="flex-1 p-2 space-y-1.5 overflow-hidden">
                  <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-1.5 text-[8px] text-white/90">
                    Research AI startups
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-lg p-1.5 text-[8px] text-white/70">
                    Opening Chrome...
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-lg p-1.5 text-[8px] text-white/70">
                    Found 6 companies
                  </div>
                  <div className="flex items-center gap-1 text-[8px] text-green-400 px-1">
                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                    Extracting...
                  </div>
                </div>
                <div className="p-2 border-t border-white/10">
                  <div className="bg-white/5 border border-white/10 rounded-lg px-2 py-1.5 text-[8px] text-white/40">
                    Type...
                  </div>
                </div>
              </div>
            </div>
          </div>
          <p className="text-center text-xs text-theme-muted mt-4">Ubuntu desktop on the left • Chat on the right • Watch AI work in real-time</p>
        </div>
      </section>

      {/* AI Employees on the Cloud - Dashboard view */}
      <section className="py-24 px-6 border-t border-theme">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-xs font-medium text-blue-500 uppercase tracking-wider mb-4">☁️ Key difference</p>
            <h2 className="text-3xl font-semibold tracking-tight mb-4">
              AI employees on the cloud
            </h2>
            <p className="text-theme-secondary max-w-xl mx-auto">
              Each AI gets its own cloud computer. Real desktop, real browser, real tools.
            </p>
          </div>

          {/* Dashboard mockup showing multiple workers */}
          <div className="border border-theme rounded-xl overflow-hidden shadow-xl shadow-black/10">
            {/* Dashboard header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-theme bg-theme-secondary">
              <div className="flex items-center gap-3">
                <span className="text-xl">🤖</span>
                <span className="font-medium">CloudBot Dashboard</span>
              </div>
              <div className="flex items-center gap-4 text-sm">
                <span className="text-theme-muted">3 workers active</span>
                <button type="button" className="bg-blue-500 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors">
                  + New Worker
                </button>
              </div>
            </div>

            {/* Workers grid */}
            <div className="bg-theme-tertiary p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Worker 1 - Research - Split view */}
                <div className="bg-theme-card border border-theme rounded-lg overflow-hidden hover:border-blue-500/50 transition-colors">
                  <div className="aspect-video bg-[#1a1a2e] flex relative">
                    {/* Status badge */}
                    <div className="absolute top-1 right-1 bg-green-500/80 text-white text-[8px] px-1.5 py-0.5 rounded font-medium z-10">
                      ● Working
                    </div>
                    {/* Left - Ubuntu with Chrome */}
                    <div className="flex-1 bg-gradient-to-br from-[#300a24] to-[#2c001e] p-1.5">
                      <div className="h-full bg-[#202124] rounded border border-white/10 overflow-hidden">
                        <div className="h-4 bg-[#35363a] flex items-center px-1.5 gap-1">
                          <div className="flex gap-0.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-yellow-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                          </div>
                          <span className="text-[8px] text-white/70 ml-1">Crunchbase</span>
                        </div>
                        <div className="p-1.5 text-[8px] text-white/70">
                          <div className="bg-white/5 rounded p-1 mb-1 font-medium">AI Startups 2024</div>
                          <div className="grid grid-cols-2 gap-1">
                            <div className="bg-white/5 rounded p-1">
                              <div className="text-white/80">OpenAI</div>
                              <div className="text-green-400 text-[7px]">$11B</div>
                            </div>
                            <div className="bg-white/5 rounded p-1">
                              <div className="text-white/80">Anthropic</div>
                              <div className="text-green-400 text-[7px]">$7B</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {/* Right - Chat */}
                    <div className="w-[20%] bg-[#0f0f1a] border-l border-white/10 flex flex-col">
                      <div className="flex-1 p-1 space-y-0.5 overflow-hidden flex flex-col justify-center">
                        <div className="bg-blue-500/20 rounded p-0.5 text-[5px] text-white/80">Research</div>
                        <div className="text-[5px] text-green-400 flex items-center gap-0.5">
                          <span className="w-1 h-1 bg-green-400 rounded-full animate-pulse" />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">🔬 research-worker</span>
                      <span className="text-xs text-green-500">● Running</span>
                    </div>
                    <p className="text-xs text-theme-muted">Researching AI startups...</p>
                  </div>
                </div>

                {/* Worker 2 - Coding - Split view */}
                <div className="bg-theme-card border border-theme rounded-lg overflow-hidden hover:border-blue-500/50 transition-colors">
                  <div className="aspect-video bg-[#1a1a2e] flex relative">
                    {/* Status badge */}
                    <div className="absolute top-1 right-1 bg-green-500/80 text-white text-[8px] px-1.5 py-0.5 rounded font-medium z-10">
                      ● Working
                    </div>
                    {/* Left - Ubuntu with VS Code */}
                    <div className="flex-1 bg-gradient-to-br from-[#300a24] to-[#2c001e] p-1.5">
                      <div className="h-full bg-[#1e1e1e] rounded border border-white/10 overflow-hidden flex flex-col">
                        <div className="h-4 bg-[#323233] flex items-center px-1.5 gap-1">
                          <div className="flex gap-0.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500/70" />
                            <div className="w-1.5 h-1.5 rounded-full bg-yellow-500/70" />
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500/70" />
                          </div>
                          <span className="text-[8px] text-white/70 ml-1">VS Code</span>
                        </div>
                        <div className="flex-1 p-1.5 font-mono text-[8px]">
                          <div><span className="text-purple-400">import</span> <span className="text-blue-400">React</span></div>
                          <div><span className="text-purple-400">const</span> App = () =&gt;</div>
                          <div className="pl-2 text-white/60">return &lt;div&gt;</div>
                          <div className="pl-4 text-yellow-300">"Dashboard"</div>
                        </div>
                        <div className="h-5 bg-[#0d0d0d] px-1.5 flex items-center">
                          <span className="text-green-400 text-[7px]">✓ Build OK</span>
                        </div>
                      </div>
                    </div>
                    {/* Right - Chat */}
                    <div className="w-[20%] bg-[#0f0f1a] border-l border-white/10 flex flex-col">
                      <div className="flex-1 p-1 space-y-0.5 overflow-hidden flex flex-col justify-center">
                        <div className="bg-blue-500/20 rounded p-0.5 text-[5px] text-white/80">Build</div>
                        <div className="text-[5px] text-green-400 flex items-center gap-0.5">
                          <span className="w-1 h-1 bg-green-400 rounded-full animate-pulse" />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">💻 dev-worker</span>
                      <span className="text-xs text-green-500">● Running</span>
                    </div>
                    <p className="text-xs text-theme-muted">Building React dashboard...</p>
                  </div>
                </div>

                {/* Worker 3 - Email - Split view */}
                <div className="bg-theme-card border border-theme rounded-lg overflow-hidden hover:border-blue-500/50 transition-colors">
                  <div className="aspect-video bg-[#1a1a2e] flex relative">
                    {/* Status badge */}
                    <div className="absolute top-1 right-1 bg-yellow-500/80 text-white text-[8px] px-1.5 py-0.5 rounded font-medium z-10">
                      ● Waiting
                    </div>
                    {/* Left - Ubuntu with Gmail */}
                    <div className="flex-1 bg-gradient-to-br from-[#300a24] to-[#2c001e] p-1.5">
                      <div className="h-full bg-[#202124] rounded border border-white/10 overflow-hidden">
                        <div className="h-4 bg-[#35363a] flex items-center px-1.5 gap-1">
                          <div className="flex gap-0.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-yellow-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                          </div>
                          <span className="text-red-400 text-[10px] ml-1">✉️</span>
                          <span className="text-[8px] text-white/70">Gmail</span>
                        </div>
                        <div className="p-1.5 space-y-1 text-[8px]">
                          <div className="bg-blue-500/20 rounded p-1 text-white/80 flex items-center gap-1">
                            <span className="text-blue-400 text-[10px]">●</span>
                            <span className="font-medium">Investor reply</span>
                          </div>
                          <div className="bg-white/5 rounded p-1 text-white/60">Newsletter...</div>
                          <div className="bg-white/5 rounded p-1 text-white/50">Update...</div>
                        </div>
                      </div>
                    </div>
                    {/* Right - Chat */}
                    <div className="w-[20%] bg-[#0f0f1a] border-l border-white/10 flex flex-col">
                      <div className="flex-1 p-1 space-y-0.5 overflow-hidden flex flex-col justify-center">
                        <div className="bg-blue-500/20 rounded p-0.5 text-[5px] text-white/80">Monitor</div>
                        <div className="text-[5px] text-yellow-400">⏳</div>
                      </div>
                    </div>
                  </div>
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">📧 email-worker</span>
                      <span className="text-xs text-yellow-500">● Waiting</span>
                    </div>
                    <p className="text-xs text-theme-muted">Monitoring inbox for VCs...</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Comparison below */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 max-w-2xl mx-auto">
            <div className="flex items-center gap-4 p-4 border border-theme rounded-lg bg-theme-secondary/50">
              <span className="text-lg">💬</span>
              <div>
                <p className="text-xs font-medium text-theme-muted uppercase">Chatbots</p>
                <p className="text-sm text-theme-secondary">Text in, text out — no real action</p>
              </div>
            </div>
            <div className="flex items-center gap-4 p-4 border border-blue-500/30 rounded-lg bg-blue-500/5">
              <span className="text-lg">🖥️</span>
              <div>
                <p className="text-xs font-medium text-blue-500 uppercase">CloudBot</p>
                <p className="text-sm">AI with a computer — real work, real output</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-24 px-6 border-t border-theme">
        <div className="max-w-6xl mx-auto">
          <p className="text-xs font-medium text-theme-muted uppercase tracking-wider mb-4">⚡ Process</p>
          <h2 className="text-3xl font-semibold tracking-tight mb-16">How it works</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Step 1 - Launch */}
            <div className="group">
              <div className="border border-theme rounded-lg overflow-hidden mb-4 bg-theme-secondary/30">
                <div className="aspect-[4/3] bg-[#0f0f1a] p-3 flex flex-col">
                  {/* Dashboard mockup */}
                  <div className="text-[9px] text-white/50 mb-2">Dashboard</div>
                  <div className="flex-1 space-y-2">
                    <div className="bg-blue-500/20 border border-blue-500/30 rounded p-2 flex items-center gap-2">
                      <div className="w-6 h-6 bg-blue-500 rounded flex items-center justify-center text-white text-[10px]">+</div>
                      <div>
                        <div className="text-[9px] text-white/80">New Instance</div>
                        <div className="text-[8px] text-blue-400">Click to create</div>
                      </div>
                    </div>
                    <div className="bg-white/5 rounded p-2 flex items-center gap-2">
                      <div className="w-6 h-6 bg-green-500/30 rounded flex items-center justify-center text-[10px]">🖥️</div>
                      <div>
                        <div className="text-[9px] text-white/60">worker-01</div>
                        <div className="text-[8px] text-green-400">● Running</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl group-hover:scale-110 transition-transform">🚀</span>
                <span className="text-xs font-mono text-theme-muted">01</span>
              </div>
              <h3 className="text-lg font-medium mb-1">Launch</h3>
              <p className="text-sm text-theme-secondary">Spin up cloud computer in seconds</p>
            </div>

            {/* Step 2 - Instruct */}
            <div className="group">
              <div className="border border-theme rounded-lg overflow-hidden mb-4 bg-theme-secondary/30">
                <div className="aspect-[4/3] bg-[#1a1a2e] flex">
                  {/* Left - Mini Ubuntu desktop */}
                  <div className="flex-1 bg-gradient-to-br from-[#300a24] to-[#2c001e] p-1.5 flex flex-col">
                    <div className="h-4 bg-[#2c001e] flex items-center px-2 text-[7px] text-white/60">
                      <span>Activities</span>
                      <div className="flex-1 text-center">14:32</div>
                    </div>
                    <div className="flex-1 p-1 relative">
                      <div className="absolute inset-0 bg-[#202124] rounded border border-white/10">
                        <div className="h-4 bg-[#35363a] flex items-center px-1.5 gap-1">
                          <div className="flex gap-0.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-yellow-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                          </div>
                          <span className="text-[7px] text-white/60 ml-1">Chrome</span>
                        </div>
                        <div className="p-2 text-[8px] text-white/70">
                          <div className="bg-white/5 rounded p-1.5 font-medium">crunchbase.com</div>
                          <div className="mt-1 text-[7px] text-white/50">AI Startups List</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  {/* Right - Chat */}
                  <div className="w-[25%] bg-[#0f0f1a] border-l border-white/10 p-1 flex flex-col justify-center">
                    <div className="bg-blue-500/20 rounded p-1 text-[6px] text-white/90 mb-1">
                      Research competitors
                    </div>
                    <div className="text-[6px] text-green-400 flex items-center gap-0.5">
                      <span className="w-1 h-1 bg-green-400 rounded-full animate-pulse" />
                      Starting...
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl group-hover:scale-110 transition-transform">💬</span>
                <span className="text-xs font-mono text-theme-muted">02</span>
              </div>
              <h3 className="text-lg font-medium mb-1">Instruct</h3>
              <p className="text-sm text-theme-secondary">Chat naturally, like a colleague</p>
            </div>

            {/* Step 3 - Execute */}
            <div className="group">
              <div className="border border-theme rounded-lg overflow-hidden mb-4 bg-theme-secondary/30">
                <div className="aspect-[4/3] bg-[#1a1a2e] flex">
                  {/* Left - Mini Ubuntu desktop */}
                  <div className="flex-1 bg-gradient-to-br from-[#300a24] to-[#2c001e] p-1.5 flex flex-col">
                    <div className="h-4 bg-[#2c001e] flex items-center px-2 text-[7px] text-white/60">
                      <span>Activities</span>
                      <div className="flex-1 text-center">14:35</div>
                    </div>
                    <div className="flex-1 p-1 relative">
                      <div className="absolute inset-0 bg-[#202124] rounded border border-white/10">
                        <div className="h-4 bg-[#35363a] flex items-center px-1.5 gap-1">
                          <div className="flex gap-0.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-yellow-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                          </div>
                          <span className="text-[7px] text-white/60 ml-1">Chrome</span>
                        </div>
                        <div className="p-2 text-[8px] text-white/70 space-y-1">
                          <div className="bg-white/5 rounded p-1">competitor1.com</div>
                          <div className="bg-white/5 rounded p-1">competitor2.com</div>
                        </div>
                      </div>
                      {/* Cursor */}
                      <div className="absolute bottom-2 right-2">
                        <svg className="w-3 h-3 text-white drop-shadow" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M4 4l16 8-7 2-2 7z"/>
                        </svg>
                      </div>
                    </div>
                  </div>
                  {/* Right - Chat showing progress */}
                  <div className="w-[25%] bg-[#0f0f1a] border-l border-white/10 p-1 flex flex-col justify-center">
                    <div className="bg-white/5 rounded p-1 text-[6px] text-white/60 mb-1">
                      Found 5 sites
                    </div>
                    <div className="text-[6px] text-green-400 flex items-center gap-0.5">
                      <span className="w-1 h-1 bg-green-400 rounded-full animate-pulse" />
                      Extracting...
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl group-hover:scale-110 transition-transform">🤖</span>
                <span className="text-xs font-mono text-theme-muted">03</span>
              </div>
              <h3 className="text-lg font-medium mb-1">Execute</h3>
              <p className="text-sm text-theme-secondary">AI controls desktop with vision</p>
            </div>

            {/* Step 4 - Iterate */}
            <div className="group">
              <div className="border border-theme rounded-lg overflow-hidden mb-4 bg-theme-secondary/30">
                <div className="aspect-[4/3] bg-[#1a1a2e] flex">
                  {/* Left - Mini Ubuntu desktop with Google Docs */}
                  <div className="flex-1 bg-gradient-to-br from-[#300a24] to-[#2c001e] p-1.5 flex flex-col">
                    <div className="h-4 bg-[#2c001e] flex items-center px-2 text-[7px] text-white/60">
                      <span>Activities</span>
                      <div className="flex-1 text-center">14:45</div>
                    </div>
                    <div className="flex-1 p-1 relative">
                      <div className="absolute inset-0 bg-white rounded border border-white/10 overflow-hidden">
                        <div className="h-4 bg-[#35363a] flex items-center px-1.5 gap-1">
                          <div className="flex gap-0.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-yellow-500" />
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                          </div>
                          <span className="text-[7px] text-white/60 ml-1">Docs</span>
                        </div>
                        <div className="p-2 text-[9px] text-gray-700">
                          <div className="font-medium text-[10px]">📄 Report.pdf</div>
                          <div className="text-[8px] text-gray-500 mt-1">12 pages complete</div>
                          <div className="text-[7px] text-green-600 mt-1">✓ Ready to review</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  {/* Right - Chat showing results */}
                  <div className="w-[25%] bg-[#0f0f1a] border-l border-white/10 p-1 flex flex-col justify-center">
                    <div className="bg-green-500/20 rounded p-1 text-[6px] text-green-400 mb-1">
                      ✅ Done!
                    </div>
                    <div className="bg-blue-500/20 rounded p-1 text-[5px] text-white/80">
                      Add more?
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl group-hover:scale-110 transition-transform">✅</span>
                <span className="text-xs font-mono text-theme-muted">04</span>
              </div>
              <h3 className="text-lg font-medium mb-1">Iterate</h3>
              <p className="text-sm text-theme-secondary">Review results, AI learns</p>
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section id="features" className="py-24 px-6 border-t border-theme">
        <div className="max-w-6xl mx-auto">
          <p className="text-xs font-medium text-theme-muted uppercase tracking-wider mb-4">🦾 Capabilities</p>
          <h2 className="text-3xl font-semibold tracking-tight mb-16">What it can do</h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
            {capabilities.map((cap, i) => (
              <div key={i} className="p-5 border border-theme rounded-lg hover:border-blue-500/50 hover:bg-theme-secondary/50 transition-all group">
                <span className="text-2xl mb-3 block group-hover:scale-110 transition-transform">{cap.emoji}</span>
                <h3 className="text-sm font-medium mb-1">{cap.title}</h3>
                <p className="text-xs text-theme-muted">{cap.desc}</p>
              </div>
            ))}
          </div>

          {/* Capability screenshots - Split view */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Vision Control - Split view */}
            <div className="border border-theme rounded-lg overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-theme bg-theme-secondary">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-red-500/70" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500/70" />
                  <div className="w-2 h-2 rounded-full bg-green-500/70" />
                </div>
                <span className="text-[10px] text-theme-muted font-mono">👁️ vision-worker</span>
              </div>
              <div className="aspect-[16/10] bg-[#1a1a2e] flex">
                {/* Left - Ubuntu with Amazon */}
                <div className="flex-[2] bg-gradient-to-br from-[#300a24] to-[#2c001e] flex flex-col">
                  <div className="h-5 bg-[#2c001e] flex items-center px-2 text-[7px] text-white/50">
                    <span>Activities</span>
                    <div className="flex-1 text-center">10:15</div>
                  </div>
                  <div className="flex-1 p-1.5 relative">
                    <div className="absolute inset-1 bg-[#202124] rounded border border-white/10 overflow-hidden">
                      <div className="h-5 bg-[#35363a] flex items-center px-1.5 gap-1">
                        <div className="flex gap-0.5">
                          <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                          <div className="w-1.5 h-1.5 rounded-full bg-yellow-500" />
                          <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                        </div>
                        <span className="text-[6px] text-white/50 ml-1">amazon.com</span>
                      </div>
                      <div className="p-2 relative">
                        <div className="flex gap-2">
                          <div className="w-10 h-10 bg-white/10 rounded flex items-center justify-center text-lg">📦</div>
                          <div className="flex-1">
                            <div className="text-[8px] text-white/80">Headphones</div>
                            <div className="text-[7px] text-green-400">$79.99</div>
                            <div className="relative inline-block mt-1">
                              <div className="bg-yellow-500 text-black text-[6px] px-2 py-0.5 rounded font-medium">
                                Add to Cart
                              </div>
                              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 border border-blue-400 rounded-full animate-pulse" />
                            </div>
                          </div>
                        </div>
                        <svg className="absolute bottom-1 right-4 w-3 h-3 text-white" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M4 4l16 8-7 2-2 7z"/>
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Right - Chat */}
                <div className="w-[20%] bg-[#0f0f1a] border-l border-white/10 flex flex-col justify-center p-2">
                  <div className="bg-blue-500/20 rounded p-1 text-[6px] text-white/90 mb-1">
                    Buy headphones
                  </div>
                  <div className="text-[6px] text-blue-400 flex items-center gap-0.5">
                    <span className="w-1 h-1 bg-blue-400 rounded-full animate-pulse" />
                    Clicking...
                  </div>
                </div>
              </div>
            </div>

            {/* Code Execution - Split view */}
            <div className="border border-theme rounded-lg overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-theme bg-theme-secondary">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-red-500/70" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500/70" />
                  <div className="w-2 h-2 rounded-full bg-green-500/70" />
                </div>
                <span className="text-[10px] text-theme-muted font-mono">💻 code-worker</span>
              </div>
              <div className="aspect-[16/10] bg-[#1a1a2e] flex">
                {/* Left - Ubuntu with VS Code */}
                <div className="flex-[2] bg-gradient-to-br from-[#300a24] to-[#2c001e] flex flex-col">
                  <div className="h-5 bg-[#2c001e] flex items-center px-2 text-[7px] text-white/50">
                    <span>Activities</span>
                    <div className="flex-1 text-center">11:30</div>
                  </div>
                  <div className="flex-1 p-1.5 relative">
                    <div className="absolute inset-1 bg-[#1e1e1e] rounded border border-white/10 overflow-hidden flex flex-col">
                      <div className="h-4 bg-[#323233] flex items-center px-1.5">
                        <div className="flex gap-0.5">
                          <div className="w-1.5 h-1.5 rounded-full bg-red-500/70" />
                          <div className="w-1.5 h-1.5 rounded-full bg-yellow-500/70" />
                          <div className="w-1.5 h-1.5 rounded-full bg-green-500/70" />
                        </div>
                        <span className="text-[6px] text-white/40 ml-1">analyze.py</span>
                      </div>
                      <div className="flex-1 p-1.5 font-mono text-[6px]">
                        <div><span className="text-purple-400">import</span> pandas</div>
                        <div><span className="text-purple-400">def</span> <span className="text-blue-400">process</span>():</div>
                        <div className="pl-2 text-white/60">df = pd.read_csv()</div>
                        <div className="pl-2 text-green-400"># AI added ↑</div>
                      </div>
                      <div className="h-8 bg-[#0d0d0d] p-1 font-mono text-[5px]">
                        <div className="text-green-400">$ python analyze.py</div>
                        <div className="text-blue-400">✓ Output saved</div>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Right - Chat */}
                <div className="w-[20%] bg-[#0f0f1a] border-l border-white/10 flex flex-col justify-center p-2">
                  <div className="bg-blue-500/20 rounded p-1 text-[6px] text-white/90 mb-1">
                    Analyze data
                  </div>
                  <div className="bg-green-500/20 rounded p-1 text-[6px] text-green-400">
                    ✅ 50k rows
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Second Brain */}
      <section className="py-24 px-6 border-t border-theme">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <p className="text-xs font-medium text-theme-muted uppercase tracking-wider mb-4">🧠 Memory</p>
              <h2 className="text-3xl font-semibold tracking-tight mb-6">
                Second brain
              </h2>
              <p className="text-theme-secondary mb-8 leading-relaxed">
                Not a stateless chatbot. Persistent memory that evolves — learns preferences,
                remembers projects, builds context across sessions.
              </p>

              <div className="space-y-3 text-sm text-theme-secondary">
                {[
                  { emoji: '♾️', text: 'Never loses context' },
                  { emoji: '📚', text: 'Learns your patterns' },
                  { emoji: '🔍', text: 'References past work' },
                  { emoji: '☁️', text: 'Cloud-stored, never lost' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span>{item.emoji}</span>
                    {item.text}
                  </div>
                ))}
              </div>
            </div>

            {/* Memory screenshot */}
            <div className="border border-theme rounded-lg overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-theme bg-theme-secondary">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-red-500/70" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500/70" />
                  <div className="w-2 h-2 rounded-full bg-green-500/70" />
                </div>
                <span className="text-[10px] text-theme-muted font-mono">🧠 Memory System</span>
              </div>
              <div className="bg-theme-tertiary p-4">
                <div className="grid grid-cols-2 gap-3">
                  {/* File structure */}
                  <div className="bg-theme-secondary/30 rounded-lg border border-theme p-3 font-mono text-[10px]">
                    <p className="text-theme-muted mb-2 flex items-center gap-2">
                      📁 ~/cloudbot/memory/
                    </p>
                    <div className="space-y-1.5">
                      {[
                        { file: 'USER.md', desc: 'preferences' },
                        { file: 'MEMORY.md', desc: 'long-term' },
                        { file: '2026-01-30.md', desc: 'today' },
                        { file: '2026-01-29.md', desc: 'yesterday' },
                      ].map((item, i) => (
                        <div key={i} className="flex items-center justify-between py-1 border-b border-theme/50 last:border-0">
                          <span className="text-theme-primary">{item.file}</span>
                          <span className="text-theme-muted">{item.desc}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  {/* Memory content preview */}
                  <div className="bg-theme-secondary/30 rounded-lg border border-theme p-3 text-[10px]">
                    <p className="text-theme-muted mb-2">📄 USER.md</p>
                    <div className="space-y-1 text-theme-secondary">
                      <p>• Prefers dark mode</p>
                      <p>• Timezone: PST</p>
                      <p>• Code style: TypeScript</p>
                      <p>• Reports: PDF format</p>
                    </div>
                    <div className="mt-3 pt-2 border-t border-theme/50 text-theme-muted">
                      Last updated: 2 hours ago
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use cases */}
      <section className="py-24 px-6 border-t border-theme">
        <div className="max-w-6xl mx-auto">
          <p className="text-xs font-medium text-theme-muted uppercase tracking-wider mb-4">👔 Applications</p>
          <h2 className="text-3xl font-semibold tracking-tight mb-16">Use cases</h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            {useCases.map((uc, i) => (
              <div key={i} className="p-5 border border-theme rounded-lg hover:border-blue-500/50 transition-all">
                <span className="text-2xl mb-3 block">{uc.emoji}</span>
                <h3 className="text-sm font-medium mb-4">{uc.title}</h3>
                <div className="space-y-2">
                  {uc.items.map((item, j) => (
                    <p key={j} className="text-xs text-theme-muted flex items-center gap-2">
                      <span className="w-1 h-1 bg-theme-muted rounded-full" />
                      {item}
                    </p>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Use case screenshots - Split view */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Research - Split view */}
            <div className="border border-theme rounded-lg overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-theme bg-theme-secondary">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-red-500/70" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500/70" />
                  <div className="w-2 h-2 rounded-full bg-green-500/70" />
                </div>
                <span className="text-[10px] text-theme-muted font-mono">🔬 research-worker</span>
              </div>
              <div className="aspect-[16/10] bg-[#1a1a2e] flex">
                {/* Left - Ubuntu with Chrome */}
                <div className="flex-[2] bg-gradient-to-br from-[#300a24] to-[#2c001e] flex flex-col">
                  <div className="h-5 bg-[#2c001e] flex items-center px-2 text-[7px] text-white/50">
                    <span>Activities</span>
                    <div className="flex-1 text-center">14:32</div>
                  </div>
                  <div className="flex-1 p-1.5 relative">
                    <div className="absolute inset-1 bg-[#202124] rounded border border-white/10 overflow-hidden">
                      <div className="flex items-center gap-1 px-1.5 py-1 bg-[#35363a] border-b border-white/10">
                        <div className="flex gap-0.5">
                          <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                          <div className="w-1.5 h-1.5 rounded-full bg-yellow-500" />
                          <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                        </div>
                        <div className="flex gap-0.5 ml-1">
                          <div className="bg-[#202124] px-1.5 py-0.5 rounded-t text-[6px] text-white/80">Crunchbase</div>
                          <div className="bg-white/5 px-1.5 py-0.5 rounded-t text-[6px] text-white/50">LinkedIn</div>
                        </div>
                      </div>
                      <div className="p-1.5 text-[7px]">
                        <div className="bg-white/5 rounded p-1.5 mb-1">
                          <div className="text-white/80 font-medium">Anthropic</div>
                          <div className="text-green-400 text-[6px]">$7.3B raised</div>
                        </div>
                        <div className="flex items-center gap-1 text-[6px] text-blue-400">
                          <span className="animate-pulse">●</span> Extracting data...
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Right - Chat */}
                <div className="w-[20%] bg-[#0f0f1a] border-l border-white/10 flex flex-col justify-center p-2">
                  <div className="bg-blue-500/20 rounded p-1 text-[6px] text-white/90 mb-1">
                    Research
                  </div>
                  <div className="text-[6px] text-green-400 flex items-center gap-0.5">
                    <span className="w-1 h-1 bg-green-400 rounded-full animate-pulse" />
                    Compiling...
                  </div>
                </div>
              </div>
            </div>

            {/* Development - Split view */}
            <div className="border border-theme rounded-lg overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-theme bg-theme-secondary">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-red-500/70" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500/70" />
                  <div className="w-2 h-2 rounded-full bg-green-500/70" />
                </div>
                <span className="text-[10px] text-theme-muted font-mono">👨‍💻 dev-worker</span>
              </div>
              <div className="aspect-[16/10] bg-[#1a1a2e] flex">
                {/* Left - Ubuntu with GitHub */}
                <div className="flex-[2] bg-gradient-to-br from-[#300a24] to-[#2c001e] flex flex-col">
                  <div className="h-5 bg-[#2c001e] flex items-center px-2 text-[7px] text-white/50">
                    <span>Activities</span>
                    <div className="flex-1 text-center">15:10</div>
                  </div>
                  <div className="flex-1 p-1.5 relative">
                    <div className="absolute inset-1 bg-[#0d1117] rounded border border-[#30363d] overflow-hidden">
                      <div className="flex items-center gap-2 px-2 py-1 bg-[#161b22] border-b border-[#30363d]">
                        <span className="text-[7px] text-green-400">● Open</span>
                        <span className="text-[7px] text-white/70">PR #142</span>
                      </div>
                      <div className="p-1.5 font-mono text-[6px]">
                        <div className="bg-red-500/10 px-1 text-red-400 border-l border-red-500">- if (user.token)</div>
                        <div className="bg-green-500/10 px-1 text-green-400 border-l border-green-500">+ if (token && valid)</div>
                        <div className="mt-1.5 bg-blue-500/10 border border-blue-500/30 rounded p-1">
                          <div className="text-[5px] text-blue-400">🤖 CloudBot:</div>
                          <div className="text-[5px] text-white/60">Add rate limiting</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Right - Chat */}
                <div className="w-[20%] bg-[#0f0f1a] border-l border-white/10 flex flex-col justify-center p-2">
                  <div className="bg-blue-500/20 rounded p-1 text-[6px] text-white/90 mb-1">
                    Review PR
                  </div>
                  <div className="bg-green-500/20 rounded p-1 text-[6px] text-green-400">
                    ✅ Done
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Integrations */}
      <section className="py-24 px-6 border-t border-theme">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-xs font-medium text-theme-muted uppercase tracking-wider mb-4">🔌 Integrations</p>
            <h2 className="text-3xl font-semibold tracking-tight mb-12">Connects to your tools</h2>

            <div className="flex flex-wrap justify-center gap-3 mb-8">
              {integrations.map((item, i) => (
                <div key={i} className="flex items-center gap-2 px-4 py-2.5 border border-theme rounded-lg hover:border-blue-500/50 transition-all">
                  <span className="text-lg">{item.emoji}</span>
                  <span className="text-sm">{item.name}</span>
                </div>
              ))}
            </div>

            <p className="text-xs text-theme-muted">And more coming soon 🔜</p>
          </div>

          {/* Integration screenshots - Split view */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Slack - Split view */}
            <div className="border border-theme rounded-lg overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-theme bg-theme-secondary">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-red-500/70" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500/70" />
                  <div className="w-2 h-2 rounded-full bg-green-500/70" />
                </div>
                <span className="text-[10px] text-theme-muted font-mono">💬 slack-worker</span>
              </div>
              <div className="aspect-[4/3] bg-[#1a1a2e] flex">
                {/* Left - Ubuntu with Slack */}
                <div className="flex-1 bg-gradient-to-br from-[#300a24] to-[#2c001e] flex flex-col">
                  <div className="h-5 bg-[#2c001e] flex items-center px-2 text-[8px] text-white/60">
                    <span>Activities</span>
                    <div className="flex-1 text-center">10:42</div>
                  </div>
                  <div className="flex-1 p-1.5 relative">
                    <div className="absolute inset-0 bg-[#1a1d21] rounded border border-white/10 overflow-hidden flex">
                      <div className="w-8 bg-[#19171d] py-2 flex flex-col items-center gap-1.5">
                        <div className="w-5 h-5 bg-purple-500/30 rounded text-[8px] flex items-center justify-center font-medium">A</div>
                      </div>
                      <div className="flex-1 p-2 space-y-1.5">
                        <div className="text-[8px] text-white/50 font-medium">#general</div>
                        <div className="flex gap-1.5 items-start">
                          <div className="w-4 h-4 bg-blue-500/30 rounded text-[7px] flex items-center justify-center flex-shrink-0">J</div>
                          <div className="text-[8px] text-white/80">@cloudbot sales?</div>
                        </div>
                        <div className="flex gap-1.5 items-start">
                          <div className="w-4 h-4 bg-green-500/30 rounded text-[7px] flex items-center justify-center flex-shrink-0">🤖</div>
                          <div className="bg-green-500/10 rounded p-1.5 text-[8px] text-white/80">📊 $2.4M this month</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Right - Chat */}
                <div className="w-[18%] bg-[#0f0f1a] border-l border-white/10 flex flex-col justify-center p-1">
                  <div className="bg-green-500/20 rounded p-0.5 text-[5px] text-green-400 text-center">
                    ✅ Replied
                  </div>
                </div>
              </div>
            </div>

            {/* Gmail - Split view */}
            <div className="border border-theme rounded-lg overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-theme bg-theme-secondary">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-red-500/70" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500/70" />
                  <div className="w-2 h-2 rounded-full bg-green-500/70" />
                </div>
                <span className="text-[10px] text-theme-muted font-mono">📧 email-worker</span>
              </div>
              <div className="aspect-[4/3] bg-[#1a1a2e] flex">
                {/* Left - Ubuntu with Gmail */}
                <div className="flex-1 bg-gradient-to-br from-[#300a24] to-[#2c001e] flex flex-col">
                  <div className="h-5 bg-[#2c001e] flex items-center px-2 text-[8px] text-white/60">
                    <span>Activities</span>
                    <div className="flex-1 text-center">09:15</div>
                  </div>
                  <div className="flex-1 p-1.5 relative">
                    <div className="absolute inset-0 bg-[#202124] rounded border border-white/10 overflow-hidden">
                      <div className="h-5 bg-[#35363a] flex items-center px-2 gap-1">
                        <span className="text-red-400 text-[10px]">✉️</span>
                        <span className="text-[8px] text-white/60">Gmail</span>
                      </div>
                      <div className="p-2 space-y-1.5">
                        <div className="flex items-center gap-2 bg-blue-500/10 rounded p-1.5 border-l-2 border-blue-400">
                          <div className="text-[8px] text-white/80 flex-1 font-medium">Acme - Contract</div>
                          <div className="text-[7px] text-blue-400 font-medium">URGENT</div>
                        </div>
                        <div className="flex items-center gap-2 bg-white/5 rounded p-1.5">
                          <div className="text-[8px] text-white/60">Newsletter update</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Right - Chat */}
                <div className="w-[18%] bg-[#0f0f1a] border-l border-white/10 flex flex-col justify-center p-1">
                  <div className="bg-blue-500/20 rounded p-0.5 text-[5px] text-blue-400 text-center">
                    📱 Alerted
                  </div>
                </div>
              </div>
            </div>

            {/* WhatsApp - Split view */}
            <div className="border border-theme rounded-lg overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-theme bg-theme-secondary">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-red-500/70" />
                  <div className="w-2 h-2 rounded-full bg-yellow-500/70" />
                  <div className="w-2 h-2 rounded-full bg-green-500/70" />
                </div>
                <span className="text-[10px] text-theme-muted font-mono">📱 notify-worker</span>
              </div>
              <div className="aspect-[4/3] bg-[#1a1a2e] flex">
                {/* Left - Ubuntu with WhatsApp Web */}
                <div className="flex-1 bg-gradient-to-br from-[#300a24] to-[#2c001e] flex flex-col">
                  <div className="h-5 bg-[#2c001e] flex items-center px-2 text-[8px] text-white/60">
                    <span>Activities</span>
                    <div className="flex-1 text-center">16:30</div>
                  </div>
                  <div className="flex-1 p-1.5 relative">
                    <div className="absolute inset-0 bg-[#111b21] rounded border border-white/10 overflow-hidden">
                      <div className="h-5 bg-[#202c33] flex items-center px-2 gap-1">
                        <span className="text-green-400 text-[10px]">📱</span>
                        <span className="text-[8px] text-white/60">WhatsApp</span>
                      </div>
                      <div className="p-2 flex flex-col items-end space-y-1.5">
                        <div className="bg-[#005c4b] rounded-lg p-2 text-[9px] text-white/90 max-w-[85%]">
                          Report done! ✅
                        </div>
                        <div className="bg-[#005c4b] rounded-lg p-2 text-[9px] text-white/90 max-w-[85%]">
                          Task completed 🎉
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Right - Chat */}
                <div className="w-[18%] bg-[#0f0f1a] border-l border-white/10 flex flex-col justify-center p-1">
                  <div className="bg-green-500/20 rounded p-0.5 text-[5px] text-green-400 text-center">
                    ✅ Notified
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Scale */}
      <section id="pricing" className="py-24 px-6 border-t border-theme">
        <div className="max-w-6xl mx-auto">
          <p className="text-xs font-medium text-theme-muted uppercase tracking-wider mb-4">🚀 Scale</p>
          <h2 className="text-3xl font-semibold tracking-tight mb-16">From 1 to 100 workers</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
            {tiers.map((tier, i) => (
              <div key={i} className={`p-6 rounded-lg border ${tier.featured ? 'border-blue-500/50 bg-blue-500/5' : 'border-theme'}`}>
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-2xl">{tier.emoji}</span>
                  <div>
                    <h3 className="text-lg font-medium">{tier.name}</h3>
                    {tier.featured && <span className="text-[10px] text-blue-500 font-medium">POPULAR</span>}
                  </div>
                </div>
                <p className="text-sm font-mono text-theme-muted mb-3">{tier.spec}</p>
                <p className="text-sm text-theme-secondary">{tier.desc}</p>
              </div>
            ))}
          </div>

          <div className="flex flex-wrap gap-6 text-sm text-theme-secondary">
            {[
              { emoji: '🔗', text: 'Multi-instance orchestration' },
              { emoji: '🤝', text: 'Agent swarms' },
              { emoji: '📊', text: 'Scale on demand' },
              { emoji: '📋', text: 'Manager dashboard' },
            ].map((item, i) => (
              <span key={i} className="flex items-center gap-2">
                <span>{item.emoji}</span>
                {item.text}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Security */}
      <section className="py-24 px-6 border-t border-theme">
        <div className="max-w-6xl mx-auto">
          <p className="text-xs font-medium text-theme-muted uppercase tracking-wider mb-4">🛡️ Security</p>
          <h2 className="text-3xl font-semibold tracking-tight mb-16">Enterprise ready</h2>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            {security.map((item, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className="text-xl">{item.emoji}</span>
                <div>
                  <h3 className="text-sm font-medium mb-1">{item.title}</h3>
                  <p className="text-xs text-theme-muted">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-24 px-6 border-t border-theme">
        <div className="max-w-3xl mx-auto">
          <p className="text-xs font-medium text-theme-muted uppercase tracking-wider mb-4">❓ FAQ</p>
          <h2 className="text-3xl font-semibold tracking-tight mb-16">Questions</h2>

          <div className="divide-y divide-theme">
            {faqs.map((faq, i) => (
              <div key={i}>
                <button
                  type="button"
                  onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                  className="w-full py-5 text-left flex items-center justify-between hover:text-blue-500 transition-colors"
                >
                  <span className="text-sm font-medium pr-4">{faq.q}</span>
                  <ChevronIcon className="w-4 h-4 text-theme-muted flex-shrink-0" isOpen={expandedFaq === i} />
                </button>
                {expandedFaq === i && (
                  <p className="text-sm text-theme-secondary pb-5 leading-relaxed">{faq.a}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="waitlist" className="py-24 px-6 border-t border-theme relative overflow-hidden">
        {/* Gradient bg */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/10 to-transparent pointer-events-none" />

        <div className="max-w-xl mx-auto text-center relative">
          <h2 className="text-3xl font-semibold tracking-tight mb-4">
            Ready for your cloud worker? 🤖
          </h2>
          <p className="text-theme-secondary mb-10">
            Get an AI with its own computer working for you 24/7
          </p>
          <div className="max-w-sm mx-auto">
            <WaitlistForm variant="hero" />
          </div>
          <p className="text-xs text-theme-muted mt-6">
            💳 No credit card required
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-theme">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start gap-8 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">🤖</span>
                <span className="text-sm font-medium">CloudBot</span>
              </div>
              <p className="text-xs text-theme-muted">AI + Computer on the cloud ☁️</p>
            </div>

            <div className="flex gap-12 text-xs text-theme-muted">
              <div className="space-y-2">
                <p className="text-theme-primary font-medium mb-3">Product</p>
                <button type="button" onClick={() => scrollToSection('features')} className="block hover:text-theme-primary transition-colors">✨ Features</button>
                <button type="button" onClick={() => scrollToSection('pricing')} className="block hover:text-theme-primary transition-colors">💎 Pricing</button>
                <button type="button" onClick={() => scrollToSection('faq')} className="block hover:text-theme-primary transition-colors">❓ FAQ</button>
              </div>
              <div className="space-y-2">
                <p className="text-theme-primary font-medium mb-3">Company</p>
                <a href="#" className="block hover:text-theme-primary transition-colors">🏢 About</a>
                <a href="#" className="block hover:text-theme-primary transition-colors">📝 Blog</a>
                <a href="#" className="block hover:text-theme-primary transition-colors">📧 Contact</a>
              </div>
              <div className="space-y-2">
                <p className="text-theme-primary font-medium mb-3">Legal</p>
                <a href="#" className="block hover:text-theme-primary transition-colors">🔒 Privacy</a>
                <a href="#" className="block hover:text-theme-primary transition-colors">📜 Terms</a>
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center pt-8 border-t border-theme">
            <p className="text-xs text-theme-muted">© 2026 CloudBot ✌️</p>
            <div className="flex gap-4">
              <a href="#" aria-label="Twitter" className="text-theme-muted hover:text-theme-primary transition-colors">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>
              </a>
              <a href="#" aria-label="GitHub" className="text-theme-muted hover:text-theme-primary transition-colors">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" /></svg>
              </a>
              <a href="#" aria-label="LinkedIn" className="text-theme-muted hover:text-theme-primary transition-colors">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" /></svg>
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          mode={authMode}
          onClose={() => setShowAuthModal(false)}
          onSwitchMode={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}
        />
      )}
    </div>
  );
};

export default LandingPage;

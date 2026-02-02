import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useInstances } from '../../contexts/InstanceContext';
import { useTheme } from '../../contexts/ThemeContext';
import RemoteDesktop from './RemoteDesktop';
import ChatInterface, { type ChatInterfaceRef } from '../Chat/ChatInterface';
import type { SessionInfo } from '../Chat/types';
import {
  generateSessionKey,
  getDefaultSessionKey,
  getSessionDisplayName,
  formatRelativeTime,
  getActiveSessionKey,
  getSessionsCacheKey,
} from '../Chat/types';

const CHAT_WIDTH_KEY = 'cloudbot-chat-panel-width';
const DEFAULT_CHAT_WIDTH = 400;
const MIN_CHAT_WIDTH = 280;
const MAX_CHAT_WIDTH = 800;

// Icons
const ComputerIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
);

const CloseIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const PlusIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
  </svg>
);

const RefreshIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

const SunIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
);

const MoonIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
  </svg>
);

const StopIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
  </svg>
);

const ChevronDownIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
  </svg>
);

const TrashIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

// Instance selector component (shown in new tab)
const InstanceSelector: React.FC<{
  instances: any[];
  onSelect: (id: string) => void;
  onCreateNew: () => void;
}> = ({ instances, onSelect, onCreateNew }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-500/20 text-green-400';
      case 'launching':
        return 'bg-yellow-500/20 text-yellow-400';
      case 'stopping':
      case 'stopped':
        return 'bg-gray-500/20 text-gray-400';
      default:
        return 'bg-red-500/20 text-red-400';
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-theme-primary overflow-auto">
      <div className="max-w-4xl mx-auto w-full p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-theme-primary">Your Instances</h2>
          <button
            type="button"
            onClick={onCreateNew}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            + Create Instance
          </button>
        </div>

        {instances.length === 0 ? (
          <div className="text-center py-12 bg-theme-card rounded-xl border border-theme">
            <div className="w-16 h-16 rounded-full bg-theme-tertiary flex items-center justify-center mx-auto mb-4">
              <ComputerIcon className="w-8 h-8 text-theme-muted" />
            </div>
            <p className="text-theme-secondary mb-4">No instances yet</p>
            <button
              type="button"
              onClick={onCreateNew}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              Create your first instance
            </button>
          </div>
        ) : (
          <div className="bg-theme-card rounded-xl border border-theme overflow-hidden">
            <ul className="divide-y divide-[var(--border-color)]">
              {instances.map((instance) => (
                <li
                  key={instance.id}
                  className="hover:bg-theme-hover cursor-pointer transition-colors"
                  onClick={() => instance.status === 'running' && onSelect(instance.id)}
                >
                  <div className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-blue-500 hover:text-blue-400 truncate">
                          {instance.name || 'Unnamed Instance'}
                        </p>
                        <div className="mt-2 flex items-center text-sm text-theme-muted">
                          <span
                            className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusColor(
                              instance.status
                            )}`}
                          >
                            {instance.status}
                          </span>
                          {instance.public_ip && (
                            <span className="ml-4 font-mono text-xs">{instance.public_ip}</span>
                          )}
                        </div>
                      </div>
                      {instance.status === 'running' && (
                        <span className="text-sm text-blue-500">Connect →</span>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

const SplitView: React.FC = () => {
  const { instanceId } = useParams<{ instanceId: string }>();
  const { instances, selectedInstance, refreshInstance, fetchInstances } = useInstances();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [showNewTab, setShowNewTab] = useState(false);

  // Panel visibility state
  const [showViewer, setShowViewer] = useState(true);
  const [showChat, setShowChat] = useState(true);

  // Resizable panel state
  const [chatWidth, setChatWidth] = useState(() => {
    const saved = localStorage.getItem(CHAT_WIDTH_KEY);
    return saved ? parseInt(saved, 10) : DEFAULT_CHAT_WIDTH;
  });
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const chatRef = useRef<ChatInterfaceRef>(null);

  // Session state
  const [sessions, setSessions] = useState<SessionInfo[]>(() => {
    // Load cached sessions from localStorage
    if (instanceId) {
      const cached = localStorage.getItem(getSessionsCacheKey(instanceId));
      if (cached) {
        try {
          return JSON.parse(cached);
        } catch {
          return [];
        }
      }
    }
    return [];
  });
  const [activeSessionKey, setActiveSessionKey] = useState<string>(() => {
    // Load active session from localStorage or use default
    if (instanceId) {
      const saved = localStorage.getItem(getActiveSessionKey(instanceId));
      if (saved) return saved;
    }
    return instanceId ? getDefaultSessionKey(instanceId) : '';
  });
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  const [isChatConnected, setIsChatConnected] = useState(false);
  const [showSessionDropdown, setShowSessionDropdown] = useState(false);

  // Save sessions to localStorage when they change
  useEffect(() => {
    if (instanceId && sessions.length > 0) {
      localStorage.setItem(getSessionsCacheKey(instanceId), JSON.stringify(sessions));
    }
  }, [instanceId, sessions]);

  // Save active session to localStorage when it changes
  useEffect(() => {
    if (instanceId && activeSessionKey) {
      localStorage.setItem(getActiveSessionKey(instanceId), activeSessionKey);
    }
  }, [instanceId, activeSessionKey]);

  // Reset session state when instanceId changes
  useEffect(() => {
    if (instanceId) {
      // Load cached sessions
      const cached = localStorage.getItem(getSessionsCacheKey(instanceId));
      if (cached) {
        try {
          setSessions(JSON.parse(cached));
        } catch {
          setSessions([]);
        }
      } else {
        setSessions([]);
      }
      // Load active session
      const savedSession = localStorage.getItem(getActiveSessionKey(instanceId));
      setActiveSessionKey(savedSession || getDefaultSessionKey(instanceId));
    }
  }, [instanceId]);

  // Handle sessions loaded from ChatInterface
  const handleSessionsLoaded = useCallback((loadedSessions: SessionInfo[]) => {
    setSessions(loadedSessions);
    // If current session not in list, switch to first one or create new
    if (loadedSessions.length > 0) {
      const exists = loadedSessions.some(s => s.key === activeSessionKey);
      if (!exists && instanceId) {
        setActiveSessionKey(loadedSessions[0].key);
      }
    }
  }, [activeSessionKey, instanceId]);

  // Handle session selection
  const handleSelectSession = useCallback((sessionKey: string) => {
    setActiveSessionKey(sessionKey);
    setShowSessionDropdown(false);
    chatRef.current?.loadSessionHistory(sessionKey);
  }, []);

  // Handle new session creation
  const handleNewSession = useCallback(() => {
    if (instanceId) {
      const newKey = generateSessionKey(instanceId);
      setActiveSessionKey(newKey);
      setShowSessionDropdown(false);
    }
  }, [instanceId]);

  // Handle session deletion
  const handleDeleteSession = useCallback(async (sessionKey: string) => {
    if (isAgentRunning) {
      alert('Please stop the agent first before deleting the session.');
      return;
    }
    const result = await chatRef.current?.deleteSession(sessionKey);
    if (result && sessionKey === activeSessionKey && instanceId) {
      // Switch to another session
      const remaining = sessions.filter(s => s.key !== sessionKey);
      if (remaining.length > 0) {
        setActiveSessionKey(remaining[0].key);
      } else {
        setActiveSessionKey(getDefaultSessionKey(instanceId));
      }
    }
  }, [activeSessionKey, instanceId, isAgentRunning, sessions]);

  // Handle stop agent
  const handleStopAgent = useCallback(() => {
    chatRef.current?.abortAgent();
    setIsAgentRunning(false);
  }, []);

  // Handle refresh sessions
  const handleRefreshSessions = useCallback(() => {
    chatRef.current?.refreshSessions();
  }, []);

  // Get current session display name
  const currentSessionName = sessions.find(s => s.key === activeSessionKey);
  const displayName = currentSessionName ? getSessionDisplayName(currentSessionName) : 'New conversation';

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (showSessionDropdown) {
        const target = e.target as HTMLElement;
        if (!target.closest('.session-dropdown-container')) {
          setShowSessionDropdown(false);
        }
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showSessionDropdown]);

  // Save chat width to localStorage when it changes
  useEffect(() => {
    localStorage.setItem(CHAT_WIDTH_KEY, chatWidth.toString());
  }, [chatWidth]);

  // Handle mouse move during drag
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const newWidth = containerRect.right - e.clientX;
    const clampedWidth = Math.min(MAX_CHAT_WIDTH, Math.max(MIN_CHAT_WIDTH, newWidth));
    setChatWidth(clampedWidth);
  }, [isDragging]);

  // Handle mouse up to stop dragging
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, []);

  // Add/remove event listeners for drag
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  // Start dragging
  const handleDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  useEffect(() => {
    fetchInstances();
  }, []);

  useEffect(() => {
    if (instanceId) {
      setShowNewTab(false);
      refreshInstance(instanceId);
      const interval = setInterval(() => refreshInstance(instanceId), 5000);
      return () => clearInterval(interval);
    }
  }, [instanceId]);

  const isReady = selectedInstance?.status === 'running' && selectedInstance?.public_ip;

  const handleTabClick = (id: string) => {
    setShowNewTab(false);
    navigate(`/instances/${id}`);
  };

  const handleCloseTab = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (id === instanceId) {
      const otherInstance = instances.find(i => i.id !== id && i.status === 'running');
      if (otherInstance) {
        navigate(`/instances/${otherInstance.id}`);
      } else {
        setShowNewTab(true);
      }
    }
  };

  const handleNewTab = () => {
    setShowNewTab(true);
  };

  const handleSelectInstance = (id: string) => {
    setShowNewTab(false);
    navigate(`/instances/${id}`);
  };

  const handleCreateNew = () => {
    navigate('/create-instance');
  };

  const tabInstances = instances.filter(i => i.status === 'running' || i.status === 'launching');
  const showInstanceSelector = showNewTab || !instanceId;

  return (
    <div className="h-screen flex flex-col bg-theme-primary">
      {/* Unified Tab Bar */}
      <div className="bg-theme-nav border-b border-theme flex items-center h-10">
        {/* Viewer Header Section */}
        {showViewer && (
          <div className="flex items-center overflow-x-auto flex-1">
            {tabInstances.map((instance) => (
              <div
                key={instance.id}
                onClick={() => handleTabClick(instance.id)}
                className={`flex items-center gap-2 px-3 h-10 cursor-pointer border-r border-theme transition-colors group min-w-0 ${
                  instance.id === instanceId && !showNewTab
                    ? 'bg-theme-tertiary text-theme-primary'
                    : 'text-theme-muted hover:bg-theme-hover hover:text-theme-secondary'
                }`}
              >
                {/* Status indicator dot */}
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  instance.status === 'running' ? 'bg-green-500' :
                  instance.status === 'launching' ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
                }`} />
                <ComputerIcon className={`w-4 h-4 flex-shrink-0 ${instance.id === instanceId && !showNewTab ? 'text-blue-500' : ''}`} />
                <span className="text-xs whitespace-nowrap truncate max-w-[100px]">
                  {instance.name || 'This Comp...'}
                </span>
                <button
                  type="button"
                  onClick={(e) => handleCloseTab(e, instance.id)}
                  className="p-0.5 rounded opacity-0 group-hover:opacity-100 hover:bg-theme-hover transition-all flex-shrink-0"
                  aria-label="Close tab"
                >
                  <CloseIcon className="w-3 h-3" />
                </button>
              </div>
            ))}

            {/* New Tab Button (+ icon only) */}
            <button
              type="button"
              onClick={handleNewTab}
              className={`flex items-center justify-center px-2 h-10 transition-colors ${
                showInstanceSelector
                  ? 'bg-theme-tertiary text-theme-primary'
                  : 'text-theme-muted hover:bg-theme-hover hover:text-theme-secondary'
              }`}
              aria-label="New tab"
            >
              <PlusIcon className="w-4 h-4" />
            </button>

            {/* Spacer to push controls to the right */}
            <div className="flex-1" />
            <button
              type="button"
              onClick={toggleTheme}
              className="px-2 h-10 text-theme-muted hover:text-theme-primary hover:bg-theme-hover transition-colors"
              aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {theme === 'dark' ? <SunIcon className="w-4 h-4" /> : <MoonIcon className="w-4 h-4" />}
            </button>
            {/* Show close viewer only when chat is visible, otherwise show open chat */}
            {showChat ? (
              <button
                type="button"
                onClick={() => setShowViewer(false)}
                className="px-2 h-10 text-theme-muted hover:text-theme-primary hover:bg-theme-hover transition-colors"
                aria-label="Close viewer"
              >
                <CloseIcon className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={() => setShowChat(true)}
                className="px-2 h-10 text-theme-muted hover:text-theme-primary hover:bg-theme-hover transition-colors"
                aria-label="Show chat"
              >
                <PlusIcon className="w-4 h-4" />
              </button>
            )}
          </div>
        )}

        {/* Show viewer button on top left when viewer is hidden */}
        {!showViewer && (
          <button
            type="button"
            onClick={() => setShowViewer(true)}
            className="px-3 h-10 text-theme-muted hover:text-theme-primary hover:bg-theme-hover transition-colors border-r border-theme"
            aria-label="Show viewer"
          >
            <ComputerIcon className="w-4 h-4" />
          </button>
        )}

        {/* Chat Header Section */}
        {showChat && (
          <div
            className={`flex items-center h-10 border-l border-theme bg-theme-nav ${!showViewer ? 'flex-1 border-l-0' : ''}`}
            style={showViewer ? { width: chatWidth } : undefined}
          >
            {/* Session Dropdown */}
            <div className="relative flex-1 session-dropdown-container">
              <button
                type="button"
                onClick={() => isChatConnected && setShowSessionDropdown(!showSessionDropdown)}
                disabled={!isChatConnected}
                className={`flex items-center gap-1 px-3 h-10 text-sm text-theme-primary hover:bg-theme-hover transition-colors w-full ${!isChatConnected ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <span className="truncate flex-1 text-left">{displayName}</span>
                <ChevronDownIcon className={`w-4 h-4 flex-shrink-0 transition-transform ${showSessionDropdown ? 'rotate-180' : ''}`} />
              </button>

              {/* Dropdown menu */}
              {showSessionDropdown && (
                <div className="absolute top-full left-0 right-0 bg-theme-nav border border-theme rounded-b-lg shadow-lg z-50 max-h-64 overflow-y-auto">
                  {sessions.length === 0 ? (
                    <div className="px-3 py-2 text-sm text-theme-muted">No sessions yet</div>
                  ) : (
                    sessions.map((session) => (
                      <div
                        key={session.key}
                        className={`flex items-center gap-2 px-3 py-2 hover:bg-theme-hover cursor-pointer group ${
                          session.key === activeSessionKey ? 'bg-theme-tertiary' : ''
                        }`}
                        onClick={() => handleSelectSession(session.key)}
                      >
                        <div className="flex-1 min-w-0">
                          <div className="text-sm text-theme-primary truncate">
                            {getSessionDisplayName(session)}
                          </div>
                          {session.updatedAt && (
                            <div className="text-xs text-theme-muted">
                              {formatRelativeTime(session.updatedAt)}
                            </div>
                          )}
                        </div>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteSession(session.key);
                          }}
                          className="p-1 opacity-0 group-hover:opacity-100 text-theme-muted hover:text-red-500 transition-all"
                          aria-label="Delete session"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* Stop button - visible when agent is running */}
            {isAgentRunning && (
              <button
                type="button"
                onClick={handleStopAgent}
                className="px-2 h-10 text-red-500 hover:text-red-400 hover:bg-theme-hover transition-colors"
                aria-label="Stop agent"
                title="Stop agent"
              >
                <StopIcon className="w-4 h-4" />
              </button>
            )}

            <button
              type="button"
              onClick={handleRefreshSessions}
              className="px-2 h-10 text-theme-muted hover:text-theme-primary hover:bg-theme-hover transition-colors"
              aria-label="Refresh sessions"
              title="Refresh sessions"
            >
              <RefreshIcon className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleNewSession}
              className="px-2 h-10 text-theme-muted hover:text-theme-primary hover:bg-theme-hover transition-colors"
              aria-label="New conversation"
              title="New conversation"
            >
              <PlusIcon className="w-4 h-4" />
            </button>
            {/* Only show close when viewer is visible (can't close last panel) */}
            {showViewer && (
              <button
                type="button"
                onClick={() => setShowChat(false)}
                className="px-2 h-10 text-theme-muted hover:text-theme-primary hover:bg-theme-hover transition-colors"
                aria-label="Close chat"
              >
                <CloseIcon className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Content */}
      {showInstanceSelector ? (
        <InstanceSelector
          instances={instances}
          onSelect={handleSelectInstance}
          onCreateNew={handleCreateNew}
        />
      ) : !isReady ? (
        // Show loading view with chat panel during bootstrap
        <div ref={containerRef} className="flex-1 flex overflow-hidden">
          {/* Left Panel - Loading Status */}
          {showViewer && (
            <div className="flex-1 flex items-center justify-center bg-theme-primary">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-theme-primary font-medium">
                  {selectedInstance?.status === 'launching'
                    ? 'Instance is launching...'
                    : 'Waiting for instance to be ready...'}
                </p>
                <p className="text-sm text-theme-muted mt-2">
                  Status: {selectedInstance?.status}
                </p>
                <p className="text-xs text-theme-muted mt-1">
                  This usually takes 5-10 minutes
                </p>
              </div>
            </div>
          )}

          {/* Resizable Divider - only show when both panels visible */}
          {showViewer && showChat && (
            <div
              onMouseDown={handleDragStart}
              className={`w-1 flex-shrink-0 cursor-col-resize transition-colors hover:bg-blue-500 ${
                isDragging ? 'bg-blue-500' : 'bg-theme-tertiary'
              }`}
              title="Drag to resize"
            />
          )}

          {/* Right Panel - Chat (shows status while waiting) */}
          {showChat && (
            <div
              className={`border-l border-theme ${!showViewer ? 'flex-1' : 'flex-shrink-0'}`}
              style={showViewer ? { width: chatWidth } : undefined}
            >
              <ChatInterface
                ref={chatRef}
                instanceId={instanceId!}
                instanceStatus={selectedInstance?.status}
                showHeader={false}
                sessionKey={activeSessionKey}
                onSessionsLoaded={handleSessionsLoaded}
                onAgentStateChange={setIsAgentRunning}
                onConnectedChange={setIsChatConnected}
              />
            </div>
          )}
        </div>
      ) : (
        <div ref={containerRef} className="flex-1 flex overflow-hidden">
          {/* Left Panel - VNC Desktop */}
          {showViewer && (
            <div className={`flex flex-col min-w-0 overflow-hidden ${showChat ? 'flex-1' : 'flex-1'}`}>
              <RemoteDesktop instanceId={instanceId!} />
            </div>
          )}

          {/* Resizable Divider - only show when both panels visible */}
          {showViewer && showChat && (
            <div
              onMouseDown={handleDragStart}
              className={`w-1 flex-shrink-0 cursor-col-resize transition-colors hover:bg-blue-500 ${
                isDragging ? 'bg-blue-500' : 'bg-theme-tertiary'
              }`}
              title="Drag to resize"
            />
          )}

          {/* Right Panel - Chat (no header, header is above) */}
          {showChat && (
            <div
              className={`border-l border-theme ${!showViewer ? 'flex-1' : 'flex-shrink-0'}`}
              style={showViewer ? { width: chatWidth } : undefined}
            >
              <ChatInterface
                ref={chatRef}
                instanceId={instanceId!}
                instanceStatus={selectedInstance?.status}
                showHeader={false}
                sessionKey={activeSessionKey}
                onSessionsLoaded={handleSessionsLoaded}
                onAgentStateChange={setIsAgentRunning}
                onConnectedChange={setIsChatConnected}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SplitView;

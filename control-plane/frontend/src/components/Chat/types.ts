/**
 * Session types for CloudBot chat persistence
 * These types correspond to OpenClaw's session management API
 */

export interface SessionInfo {
  /** Full session key (e.g., "web:inst-123:my-session") */
  key: string;
  /** OpenClaw session UUID */
  sessionId?: string;
  /** User-assigned label */
  label?: string;
  /** Auto-derived title from first message */
  derivedTitle?: string;
  /** Last message preview */
  lastMessagePreview?: string;
  /** Last update timestamp (ms) */
  updatedAt: number | null;
  /** Session type */
  kind?: 'direct' | 'group';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface SessionsListResponse {
  ts: number;
  path?: string;
  count: number;
  sessions: SessionInfo[];
}

export interface ChatHistoryResponse {
  sessionKey: string;
  sessionId?: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string | Array<{ type: string; text?: string }>;
    timestamp?: number;
  }>;
  thinkingLevel?: string;
}

export interface SessionsPatchParams {
  key: string;
  label?: string;
  thinkingLevel?: string;
}

export interface SessionsDeleteParams {
  key: string;
  deleteTranscript?: boolean;
}

export interface ChatAbortParams {
  sessionKey: string;
  runId?: string;
}

/** Generate a unique session key for a new session */
export function generateSessionKey(instanceId: string): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 6);
  return `web:${instanceId}:${timestamp}-${random}`;
}

/** Get the default session key for an instance */
export function getDefaultSessionKey(instanceId: string): string {
  return `web:${instanceId}:main`;
}

/** Get the display name for a session */
export function getSessionDisplayName(session: SessionInfo): string {
  const name = session.label || session.derivedTitle || 'Untitled';
  // Strip timestamp prefix like "[Mon 2026-02-02 19:52 UTC] " and message_id suffix like " [message_id: xyz]"
  return name
    .replace(/^\[[^\]]*\]\s*/, '')  // Remove timestamp prefix
    .replace(/\s*\[message_id:[^\]]*\]$/, '')  // Remove message_id suffix
    .trim() || 'Untitled';
}

/** Format relative time (e.g., "2h ago") */
export function formatRelativeTime(timestamp: number | null): string {
  if (!timestamp) return '';

  const now = Date.now();
  const diff = now - timestamp;

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;

  return new Date(timestamp).toLocaleDateString();
}

/** localStorage keys for session persistence */
export const getActiveSessionKey = (instanceId: string) =>
  `cloudbot-active-session:${instanceId}`;

export const getSessionsCacheKey = (instanceId: string) =>
  `cloudbot-sessions-cache:${instanceId}`;

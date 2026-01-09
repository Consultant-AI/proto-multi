import { useState, useEffect, useRef } from 'react'
import { History } from 'lucide-react'
import '../styles/SessionHistory.css'

interface Session {
  id: string
  createdAt?: string
  lastActive?: string
  timestamp?: string
  preview?: string
  messageCount?: number
  isCurrent?: boolean
}

interface SessionHistoryProps {
  onLoadSession: (sessionId: string) => void
  refreshTrigger?: number
}

export default function SessionHistory({ onLoadSession, refreshTrigger }: SessionHistoryProps) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadSessions()

    // Close dropdown when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [refreshTrigger])

  const loadSessions = async () => {
    try {
      // Try to load from the main sessions endpoint first (more complete data)
      const response = await fetch('/api/sessions')
      if (!response.ok) {
        // Fallback to history endpoint
        const historyResponse = await fetch('/api/sessions/history')
        if (!historyResponse.ok) {
          console.error('Failed to load sessions')
          return
        }
        const data = await historyResponse.json()
        setSessions(data)
        return
      }
      const data = await response.json()
      setSessions(data)
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

  const handleSelectSession = (sessionId: string) => {
    onLoadSession(sessionId)
    setIsOpen(false)
  }

  return (
    <div className="session-history" ref={dropdownRef}>
      <button
        className="session-history-toggle"
        onClick={() => setIsOpen(!isOpen)}
        data-tooltip="Session History"
        aria-label="Session History"
      >
        <History size={18} />
      </button>

      {isOpen && (
        <div className="session-history-dropdown">
          <div className="dropdown-header">
            <h3>Session History</h3>
          </div>
          <div className="sessions-list">
            {sessions.length === 0 ? (
              <div className="empty-sessions">No previous sessions</div>
            ) : (
              sessions.map(session => (
                <div
                  key={session.id}
                  className={`session-item ${session.isCurrent ? 'current' : ''}`}
                  onClick={() => handleSelectSession(session.id)}
                >
                  <div className="session-preview">
                    {session.preview || `Session ${session.id.slice(-4)}`}
                    {session.messageCount !== undefined && ` (${session.messageCount} messages)`}
                  </div>
                  <div className="session-time">
                    {new Date(session.timestamp || session.lastActive || session.createdAt || '').toLocaleString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

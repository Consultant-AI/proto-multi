import { useState, useEffect, useRef } from 'react'
import '../styles/SessionHistory.css'

interface Session {
  id: string
  timestamp: string
  preview: string
}

interface SessionHistoryProps {
  onLoadSession: (sessionId: string) => void
}

export default function SessionHistory({ onLoadSession }: SessionHistoryProps) {
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
  }, [])

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/sessions/history')
      if (!response.ok) {
        console.error('Failed to load sessions')
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
        title="Session History"
      >
        ↻
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
                  className="session-item"
                  onClick={() => handleSelectSession(session.id)}
                >
                  <div className="session-preview">{session.preview}</div>
                  <div className="session-time">
                    {new Date(session.timestamp).toLocaleString()}
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

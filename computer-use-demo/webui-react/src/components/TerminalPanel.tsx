import { useState, useEffect, useRef, useCallback } from 'react'
import '../styles/TerminalPanel.css'

interface TerminalPanelProps {
  sessionId: string
  isActive?: boolean
}

interface TerminalLine {
  type: 'input' | 'output' | 'error'
  content: string
  timestamp: number
}

export default function TerminalPanel({ sessionId, isActive = true }: TerminalPanelProps) {
  const [lines, setLines] = useState<TerminalLine[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const outputRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Create or connect to terminal session
  const connectSession = useCallback(async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/terminal/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      })
      const data = await response.json()
      if (data.session_id) {
        setIsConnected(true)
        setLines(prev => [...prev, {
          type: 'output',
          content: `Terminal session started (${sessionId})`,
          timestamp: Date.now()
        }])
        // Get initial output (like bash prompt)
        await pollOutput()
      }
    } catch (error) {
      console.error('Failed to create terminal session:', error)
      setLines(prev => [...prev, {
        type: 'error',
        content: `Failed to connect: ${error}`,
        timestamp: Date.now()
      }])
    } finally {
      setIsLoading(false)
    }
  }, [sessionId])

  // Poll for new output
  const pollOutput = useCallback(async () => {
    if (!isConnected) return

    try {
      const response = await fetch(`/api/terminal/sessions/${sessionId}/output`)
      if (response.ok) {
        const data = await response.json()
        if (data.output) {
          setLines(prev => [...prev, {
            type: 'output',
            content: data.output,
            timestamp: Date.now()
          }])
        }
      }
    } catch (error) {
      // Ignore polling errors
    }
  }, [sessionId, isConnected])

  // Initialize session on mount
  useEffect(() => {
    connectSession()

    return () => {
      // Cleanup polling interval
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
      }
    }
  }, [connectSession])

  // Start polling when connected
  useEffect(() => {
    if (isConnected && isActive) {
      pollIntervalRef.current = setInterval(pollOutput, 500)
    } else if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
      pollIntervalRef.current = null
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
      }
    }
  }, [isConnected, isActive, pollOutput])

  // Auto-scroll to bottom
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [lines])

  // Focus input when active
  useEffect(() => {
    if (isActive && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isActive])

  const executeCommand = async (command: string) => {
    if (!command.trim() || !isConnected) return

    // Add to history
    setCommandHistory(prev => [...prev.filter(c => c !== command), command])
    setHistoryIndex(-1)

    // Show input line
    setLines(prev => [...prev, {
      type: 'input',
      content: `$ ${command}`,
      timestamp: Date.now()
    }])

    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`/api/terminal/sessions/${sessionId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      })
      const data = await response.json()

      if (data.output) {
        setLines(prev => [...prev, {
          type: 'output',
          content: data.output,
          timestamp: Date.now()
        }])
      }
    } catch (error) {
      setLines(prev => [...prev, {
        type: 'error',
        content: `Error: ${error}`,
        timestamp: Date.now()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      executeCommand(input)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      if (commandHistory.length > 0) {
        const newIndex = historyIndex < commandHistory.length - 1 ? historyIndex + 1 : historyIndex
        setHistoryIndex(newIndex)
        setInput(commandHistory[commandHistory.length - 1 - newIndex] || '')
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setInput(commandHistory[commandHistory.length - 1 - newIndex] || '')
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setInput('')
      }
    } else if (e.key === 'c' && e.ctrlKey) {
      // Ctrl+C - cancel current input
      setInput('')
      setLines(prev => [...prev, {
        type: 'input',
        content: '^C',
        timestamp: Date.now()
      }])
    } else if (e.key === 'l' && e.ctrlKey) {
      // Ctrl+L - clear screen
      e.preventDefault()
      setLines([])
    }
  }

  const handleContainerClick = () => {
    inputRef.current?.focus()
  }

  // Parse ANSI escape codes and convert to styled spans
  const parseAnsi = (text: string): JSX.Element[] => {
    // Simple ANSI parsing - strip escape codes for now
    const cleaned = text.replace(/\x1b\[[0-9;]*m/g, '')
    return cleaned.split('\n').map((line, i) => (
      <div key={i} className="terminal-line">{line || ' '}</div>
    ))
  }

  return (
    <div className="terminal-panel" onClick={handleContainerClick}>
      <div className="terminal-output" ref={outputRef}>
        {lines.map((line, i) => (
          <div key={i} className={`terminal-entry terminal-${line.type}`}>
            {parseAnsi(line.content)}
          </div>
        ))}
        {isLoading && (
          <div className="terminal-loading">...</div>
        )}
      </div>
      <div className="terminal-input-line">
        <span className="terminal-prompt">$</span>
        <input
          ref={inputRef}
          type="text"
          className="terminal-input-field"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isConnected ? "Type a command..." : "Connecting..."}
          disabled={!isConnected || isLoading}
          autoFocus
          spellCheck={false}
          autoComplete="off"
        />
      </div>
    </div>
  )
}

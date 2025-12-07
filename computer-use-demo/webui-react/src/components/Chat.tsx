import { useState, useEffect, useRef } from 'react'
import { Message } from '../types'
import SessionHistory from './SessionHistory'
import AgentTree from './AgentTree'
import '../styles/Chat.css'

interface ChatProps {
  dashboardVisible: boolean
  agentTreeVisible: boolean
  onToggleDashboard: () => void
  onToggleAgentTree: () => void
  selectedAgentId: string | null
  selectedAgentName: string
  onSelectAgent: (agentId: string, agentName: string) => void
}

export default function Chat({
  dashboardVisible,
  agentTreeVisible,
  onToggleDashboard,
  onToggleAgentTree,
  selectedAgentId,
  selectedAgentName,
  onSelectAgent
}: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const handleLoadSession = async (sessionId: string) => {
    try {
      const response = await fetch(`/api/sessions/${sessionId}/messages`)
      if (!response.ok) {
        console.error('Failed to load session messages')
        return
      }
      const data = await response.json()
      setMessages(data)
    } catch (error) {
      console.error('Failed to load session:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    const messageText = input
    setInput('')
    setIsStreaming(true)

    try {
      // Send message - API returns immediately and processes in background
      // Use agent-specific endpoint if an agent is selected
      const endpoint = selectedAgentId
        ? `/api/agents/${selectedAgentId}/chat`
        : '/api/messages'

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText })
      })

      if (!response.ok) throw new Error('Failed to send message')

      // Connect to SSE stream for updates
      const eventSource = new EventSource('/api/stream')

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          // Handle different message types
          if (data.messages && Array.isArray(data.messages)) {
            // Full messages array - update all messages including tool calls
            const formattedMessages = data.messages.map((msg: any) => {
              let content = ''

              if (msg.role === 'user') {
                content = msg.text || msg.content || ''
              } else if (msg.role === 'assistant') {
                content = msg.text || msg.content || ''
              } else if (msg.role === 'tool') {
                // Show tool usage (without ID)
                const label = msg.label || 'Tool'
                const text = msg.text || ''
                // Remove tool ID from label (e.g., "Tool abc123" -> "Tool")
                const cleanLabel = label.replace(/\s+[a-zA-Z0-9_-]+$/, '')
                content = `🔧 ${cleanLabel}\n${text}`
              }

              return {
                role: msg.role === 'tool' ? 'assistant' : msg.role,
                content: content,
                timestamp: new Date().toISOString()
              }
            })

            setMessages(formattedMessages)
            setIsStreaming(data.running || false)

            if (!data.running) {
              eventSource.close()
            }
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error)
        }
      }

      eventSource.onerror = () => {
        eventSource.close()
        setIsStreaming(false)
      }

    } catch (error) {
      console.error('Error sending message:', error)
      setIsStreaming(false)
    }
  }

  const handleStop = async () => {
    try {
      await fetch('/api/stop', { method: 'POST' })
      setIsStreaming(false)
    } catch (error) {
      console.error('Error stopping agent:', error)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <button
            type="button"
            className="toggle-agents-btn"
            onClick={onToggleAgentTree}
            title={agentTreeVisible ? 'Hide Agents' : 'Show Agents'}
          >
            {agentTreeVisible ? '◀' : '▶'}
          </button>
          <button
            type="button"
            className="toggle-dashboard-btn"
            onClick={onToggleDashboard}
            title={dashboardVisible ? 'Hide Files' : 'Show Files'}
          >
            {dashboardVisible ? '▶' : '◀'}
          </button>
          <div className="chat-agent-info">
            <span className="chat-agent-icon">🤖</span>
            <div className="chat-agent-name">{selectedAgentName}</div>
          </div>
        </div>
        <div className="chat-header-right">
          <SessionHistory onLoadSession={handleLoadSession} />
          <button type="button" className="new-chat-btn" title="New Chat">
            +
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <h3>Select a specialist agent to start</h3>
            <div className="embedded-agent-tree">
              <AgentTree
                onSelectAgent={onSelectAgent}
                selectedAgentId={selectedAgentId}
              />
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`message message-${message.role}`}
            >
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-timestamp">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <textarea
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            disabled={isStreaming}
            rows={1}
          />
          {isStreaming ? (
            <button
              type="button"
              className="stop-btn"
              onClick={handleStop}
              title="Stop"
            >
              ⏹
            </button>
          ) : (
            <button
              type="button"
              className="send-btn"
              onClick={handleSend}
              disabled={!input.trim()}
            >
              ➤
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

import { useState, useEffect, useRef } from 'react'
import { PanelLeftClose, PanelLeftOpen, User, Square, Send, Plus } from 'lucide-react'
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
  selectedAgentIcon: string
  onSelectAgent: (agentId: string, agentName: string, agentIcon: string) => void
}

export default function Chat({
  dashboardVisible,
  agentTreeVisible: _agentTreeVisible,
  onToggleDashboard,
  onToggleAgentTree: _onToggleAgentTree,
  selectedAgentId,
  selectedAgentName,
  selectedAgentIcon,
  onSelectAgent
}: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [sessionRefreshTrigger, setSessionRefreshTrigger] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Load current session on mount
  useEffect(() => {
    const loadCurrentSession = async () => {
      try {
        const response = await fetch('/api/messages')
        if (!response.ok) return
        const data = await response.json()
        setCurrentSessionId(data.sessionId)
        // Load messages from the current session
        if (data.messages && Array.isArray(data.messages)) {
          const formattedMessages = data.messages.map((msg: any) => ({
            role: msg.role === 'tool' ? 'assistant' : msg.role,
            content: msg.content || msg.text || '',
            timestamp: new Date().toISOString()
          }))
          setMessages(formattedMessages)
        }
      } catch (error) {
        console.error('Failed to load current session:', error)
      }
    }
    loadCurrentSession()
  }, [])

  const handleLoadSession = async (sessionId: string) => {
    try {
      // First switch to the session
      const switchResponse = await fetch(`/api/sessions/${sessionId}/switch`, {
        method: 'POST'
      })
      if (!switchResponse.ok) {
        console.error('Failed to switch session')
        return
      }
      const sessionData = await switchResponse.json()
      setCurrentSessionId(sessionData.sessionId)

      // Load the session's messages from the serialize() data
      if (sessionData.messages && Array.isArray(sessionData.messages)) {
        const formattedMessages = sessionData.messages.map((msg: any) => ({
          role: msg.role === 'tool' ? 'assistant' : msg.role,
          content: msg.content || msg.text || '',
          timestamp: new Date().toISOString()
        }))
        setMessages(formattedMessages)
      } else {
        // Fallback to empty if no messages
        setMessages([])
      }

      // Trigger refresh
      setSessionRefreshTrigger(prev => prev + 1)
    } catch (error) {
      console.error('Failed to load session:', error)
    }
  }

  const handleNewConversation = async () => {
    try {
      const response = await fetch('/api/sessions/new', {
        method: 'POST'
      })
      if (!response.ok) {
        console.error('Failed to create new session')
        return
      }
      const data = await response.json()
      setCurrentSessionId(data.sessionId)
      setMessages([])
      setInput('')
      // Trigger session list refresh
      setSessionRefreshTrigger(prev => prev + 1)
    } catch (error) {
      console.error('Failed to create new conversation:', error)
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
                // Just use the text directly - the label/icon will show the tool name
                content = msg.text || ''
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
            className="toggle-dashboard-btn"
            onClick={onToggleDashboard}
            title={dashboardVisible ? 'Hide Explorer' : 'Show Explorer'}
          >
            {dashboardVisible ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
          </button>
          <div className="chat-agent-info">
            <span className="chat-agent-icon">{selectedAgentIcon}</span>
            <div className="chat-agent-name">{selectedAgentName}</div>
          </div>
        </div>
        <div className="chat-header-right">
          <SessionHistory
            onLoadSession={handleLoadSession}
            refreshTrigger={sessionRefreshTrigger}
          />
          <button
            type="button"
            className="new-chat-btn"
            title="New Chat"
            onClick={handleNewConversation}
          >
            <Plus size={18} />
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
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message message-${message.role}`}
              >
                <div className="message-avatar">
                  {message.role === 'user' ? <User size={18} /> : selectedAgentIcon}
                </div>
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  <div className="message-timestamp">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            {isStreaming && (
              <div className="message message-assistant">
                <div className="message-avatar">{selectedAgentIcon}</div>
                <div className="message-content">
                  <div className="message-text loading-indicator">
                    <span className="loading-dot"></span>
                    <span className="loading-dot"></span>
                    <span className="loading-dot"></span>
                  </div>
                </div>
              </div>
            )}
          </>
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
              <Square size={18} />
            </button>
          ) : (
            <button
              type="button"
              className="send-btn"
              onClick={handleSend}
              disabled={!input.trim()}
            >
              <Send size={18} />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

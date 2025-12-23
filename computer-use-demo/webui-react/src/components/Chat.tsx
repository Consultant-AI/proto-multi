import { useState, useEffect, useRef } from 'react'
import { PanelLeftOpen, User, Square, Send, Plus, X, Mic } from 'lucide-react'
import { Message } from '../types'
import SessionHistory from './SessionHistory'
import AgentTree from './AgentTree'
import '../styles/Chat.css'

interface ChatProps {
  viewerVisible: boolean
  onToggleViewer: () => void
  onHideChat?: () => void
  selectedAgentId: string | null
  selectedAgentName: string
  selectedAgentIcon: string
  onSelectAgent: (agentId: string, agentName: string, agentIcon: string) => void
}

export default function Chat({
  viewerVisible,
  onToggleViewer,
  onHideChat,
  selectedAgentId,
  selectedAgentName,
  selectedAgentIcon,
  onSelectAgent
}: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [_currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [sessionRefreshTrigger, setSessionRefreshTrigger] = useState(0)
  const [selectedComputer, setSelectedComputer] = useState('local')
  const [selectedMode, setSelectedMode] = useState('edit-auto')
  const [selectedTools, setSelectedTools] = useState<string[]>(['files', 'bash', 'computer', 'mouse', 'keyboard'])
  const [toolsDropdownOpen, setToolsDropdownOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const websocketRef = useRef<WebSocket | null>(null)
  const toolsDropdownRef = useRef<HTMLDivElement>(null)

  // Establish persistent WebSocket connection on mount
  useEffect(() => {
    const connectWebSocket = () => {
      // Close existing connection if any
      if (websocketRef.current) {
        websocketRef.current.close()
      }

      // Create WebSocket connection
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws`)
      websocketRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
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
                timestamp: new Date().toISOString(),
                images: msg.images || []
              }
            })

            setMessages(formattedMessages)
            setIsStreaming(data.running || false)
          }
        } catch (error) {
          console.error('Error parsing WebSocket data:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket closed, reconnecting in 3s...')
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000)
      }
    }

    // Connect WebSocket
    connectWebSocket()

    // Load current session
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
            timestamp: new Date().toISOString(),
            images: msg.images || []
          }))
          setMessages(formattedMessages)
        }
      } catch (error) {
        console.error('Failed to load current session:', error)
      }
    }
    loadCurrentSession()

    // Cleanup on unmount
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close()
      }
    }
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
          timestamp: new Date().toISOString(),
          images: msg.images || []
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

  // Close tools dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (toolsDropdownRef.current && !toolsDropdownRef.current.contains(event.target as Node)) {
        setToolsDropdownOpen(false)
      }
    }

    if (toolsDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [toolsDropdownOpen])

  const toggleTool = (tool: string) => {
    setSelectedTools(prev =>
      prev.includes(tool)
        ? prev.filter(t => t !== tool)
        : [...prev, tool]
    )
  }

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
                timestamp: new Date().toISOString(),
                images: msg.images || []
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
          {!viewerVisible && (
            <button
              type="button"
              className="toggle-viewer-btn"
              onClick={onToggleViewer}
              title="Show Viewer"
            >
              <PanelLeftOpen size={18} />
            </button>
          )}
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
          {onHideChat && (
            <button
              type="button"
              className="hide-chat-btn"
              title="Hide Chat"
              onClick={onHideChat}
            >
              <X size={18} />
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <h3>Select a specialist agent and type your request 🙃</h3>
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
                  {message.images && message.images.length > 0 && (
                    <div className="message-images">
                      {message.images.map((img, i) => (
                        <img key={i} src={img} alt="Tool output" className="message-image" />
                      ))}
                    </div>
                  )}
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
            placeholder="Ask Codex to do anything"
            disabled={isStreaming}
            rows={1}
          />
          <div className="chat-input-buttons">
            <button
              type="button"
              className="input-action-btn"
              title="Add attachment"
            >
              <Plus size={20} />
            </button>
            <div className="input-dropdown-group">
              <select
                className="input-dropdown"
                value={selectedComputer}
                onChange={(e) => setSelectedComputer(e.target.value)}
              >
                <option value="local">Local Computer</option>
                <option value="remote1">Remote Computer 1</option>
                <option value="remote2">Remote Computer 2</option>
              </select>
              <select
                className="input-dropdown"
                value={selectedMode}
                onChange={(e) => setSelectedMode(e.target.value)}
              >
                <option value="planning">Planning</option>
                <option value="edit-auto">Edit automatically</option>
                <option value="ask-before-edit">Ask before edit</option>
              </select>
              <div className="tools-dropdown-wrapper" ref={toolsDropdownRef}>
                <button
                  type="button"
                  className="input-dropdown tools-dropdown-button"
                  onClick={() => setToolsDropdownOpen(!toolsDropdownOpen)}
                >
                  Tools ({selectedTools.length})
                </button>
                {toolsDropdownOpen && (
                  <div className="tools-dropdown-menu">
                    <div className="tools-section">
                      <div className="tools-section-label">Core Tools</div>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('files')}
                          onChange={() => toggleTool('files')}
                        />
                        <span>Modifying Files</span>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('bash')}
                          onChange={() => toggleTool('bash')}
                        />
                        <span>Bash Commands</span>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('computer')}
                          onChange={() => toggleTool('computer')}
                        />
                        <span>Computer Vision</span>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('mouse')}
                          onChange={() => toggleTool('mouse')}
                        />
                        <span>Mouse Control</span>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('keyboard')}
                          onChange={() => toggleTool('keyboard')}
                        />
                        <span>Keyboard Control</span>
                      </label>
                    </div>
                    <div className="tools-section">
                      <div className="tools-section-label">Apps</div>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('drive')}
                          onChange={() => toggleTool('drive')}
                        />
                        <span>Google Drive</span>
                        <button className="tool-configure-btn">Configure</button>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('notion')}
                          onChange={() => toggleTool('notion')}
                        />
                        <span>Notion</span>
                        <button className="tool-configure-btn">Configure</button>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('calendar')}
                          onChange={() => toggleTool('calendar')}
                        />
                        <span>Calendar</span>
                        <button className="tool-configure-btn">Configure</button>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('gmail')}
                          onChange={() => toggleTool('gmail')}
                        />
                        <span>Gmail</span>
                        <button className="tool-configure-btn">Configure</button>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('mcp')}
                          onChange={() => toggleTool('mcp')}
                        />
                        <span>Custom MCP</span>
                        <button className="tool-configure-btn">Configure</button>
                      </label>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <button
              type="button"
              className="mic-btn"
              title="Voice input"
            >
              <Mic size={18} />
            </button>
            {isStreaming ? (
              <button
                type="button"
                className="send-btn"
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
    </div>
  )
}

import { useState, useEffect, useRef } from 'react'
import { PanelLeftOpen, Square, Send, Plus, X, Mic } from 'lucide-react'
import { Message } from '../types'
import SessionHistory from './SessionHistory'
import AgentTree from './AgentTree'
import '../styles/Chat.css'

interface ChatProps {
  viewerVisible: boolean
  onToggleViewer: () => void
  onHideChat?: () => void
  selectedAgentId: string | null
  onSelectAgent: (agentId: string, agentName: string, agentIcon: string) => void
  selectedComputer: string
  onSelectComputer: (computerId: string) => void
  computers: any[]
}

export default function Chat({
  viewerVisible,
  onToggleViewer,
  onHideChat,
  selectedAgentId,
  onSelectAgent,
  selectedComputer,
  onSelectComputer,
  computers
}: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [_currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [sessionRefreshTrigger, setSessionRefreshTrigger] = useState(0)
  const [selectedMode, setSelectedMode] = useState('edit-auto')
  const [selectedTools, setSelectedTools] = useState<string[]>(['files', 'bash', 'computer', 'mouse', 'keyboard'])
  const [toolsDropdownOpen, setToolsDropdownOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const websocketRef = useRef<WebSocket | null>(null)
  const toolsDropdownRef = useRef<HTMLDivElement>(null)
  const streamingTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isConnectingRef = useRef(false)

  // Establish persistent WebSocket connection on mount
  useEffect(() => {
    const connectWebSocket = () => {
      // Prevent multiple simultaneous connection attempts
      if (isConnectingRef.current) {
        console.log('[WebSocket] Already connecting, skipping...')
        return
      }

      // Close existing connection if any
      if (websocketRef.current?.readyState === WebSocket.OPEN) {
        console.log('[WebSocket] Already connected, skipping...')
        return
      }

      isConnectingRef.current = true

      // Create WebSocket connection
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws`)
      websocketRef.current = ws

      ws.onopen = () => {
        console.log('[WebSocket] Connected successfully')
        isConnectingRef.current = false
        // Clear any pending reconnect attempts
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current)
          reconnectTimeoutRef.current = null
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('[WebSocket] Received update:', {
            running: data.running,
            messageCount: data.messages?.length
          })

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
                images: msg.images || [],
                agent_name: msg.agent_name,    // ✅ Include agent identity
                agent_role: msg.agent_role,     // ✅ Include agent role
                label: msg.label                // ✅ Include message label (e.g., "Delegation Status")
              }
            })

            setMessages(formattedMessages)
            setIsStreaming(data.running || false)

            // Clear timeout when we receive updates
            if (!data.running && streamingTimeoutRef.current) {
              clearTimeout(streamingTimeoutRef.current)
              streamingTimeoutRef.current = null
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket data:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        isConnectingRef.current = false
      }

      ws.onclose = (event) => {
        console.log('[WebSocket] Closed:', event.code, event.reason)
        isConnectingRef.current = false

        // Only reconnect if it wasn't a normal closure and no reconnect is pending
        if (event.code !== 1000 && !reconnectTimeoutRef.current) {
          console.log('[WebSocket] Scheduling reconnect in 3s...')
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectTimeoutRef.current = null
            connectWebSocket()
          }, 3000)
        }
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
            images: msg.images || [],
            agent_name: msg.agent_name,    // ✅ Include agent identity
            agent_role: msg.agent_role,     // ✅ Include agent role
            label: msg.label                // ✅ Include message label (e.g., "Delegation Status")
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
      // Clear reconnect timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      // Close WebSocket
      if (websocketRef.current) {
        websocketRef.current.close(1000, 'Component unmounting')
      }
      isConnectingRef.current = false
    }
  }, [])

  const handleLoadSession = async (sessionId: string) => {
    try {
      // Clear timeout when switching sessions
      if (streamingTimeoutRef.current) {
        clearTimeout(streamingTimeoutRef.current)
        streamingTimeoutRef.current = null
      }
      setIsStreaming(false)

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
          images: msg.images || [],
          agent_name: msg.agent_name,    // ✅ Include agent identity
          agent_role: msg.agent_role,     // ✅ Include agent role
          label: msg.label                // ✅ Include message label (e.g., "Delegation Status")
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
      // Clear timeout when creating new conversation
      if (streamingTimeoutRef.current) {
        clearTimeout(streamingTimeoutRef.current)
        streamingTimeoutRef.current = null
      }
      setIsStreaming(false)

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

    // Set a 2-minute timeout to prevent infinite loading
    if (streamingTimeoutRef.current) {
      clearTimeout(streamingTimeoutRef.current)
    }
    streamingTimeoutRef.current = setTimeout(() => {
      console.error('Streaming timeout - no completion signal received within 2 minutes')
      setIsStreaming(false)
      streamingTimeoutRef.current = null
    }, 120000) // 2 minutes

    try {
      // Send message - API returns immediately and processes in background
      // WebSocket will receive all updates automatically
      const endpoint = selectedAgentId
        ? `/api/agents/${selectedAgentId}/chat`
        : '/api/messages'

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          computer_id: selectedComputer
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      // WebSocket will handle all updates - no need for SSE
    } catch (error) {
      console.error('Error sending message:', error)
      if (streamingTimeoutRef.current) {
        clearTimeout(streamingTimeoutRef.current)
        streamingTimeoutRef.current = null
      }
      setIsStreaming(false)
    }
  }

  const handleStop = async () => {
    try {
      await fetch('/api/stop', { method: 'POST' })

      // Clear timeout when stopping
      if (streamingTimeoutRef.current) {
        clearTimeout(streamingTimeoutRef.current)
        streamingTimeoutRef.current = null
      }

      // WebSocket will receive the stopped state automatically
    } catch (error) {
      console.error('Error stopping agent:', error)
      // Fallback: set to false locally if API call fails
      if (streamingTimeoutRef.current) {
        clearTimeout(streamingTimeoutRef.current)
        streamingTimeoutRef.current = null
      }
      setIsStreaming(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Double-click on header toggles window maximize (macOS-style behavior)
  const handleHeaderDoubleClick = (e: React.MouseEvent) => {
    // Only trigger if clicking on empty space (not on buttons, dropdowns, etc.)
    const target = e.target as HTMLElement
    const clickedOnInteractive = target.closest('button, .toggle-viewer-btn, .new-chat-btn, .hide-chat-btn, .session-history')
    if (clickedOnInteractive) {
      console.log('[double-click] clicked on interactive element, ignoring')
      return
    }

    console.log('[double-click] attempting to toggle maximize')

    // Use Electron IPC to toggle maximize
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const electron = window.require('electron')
      console.log('[double-click] electron module:', electron)
      electron.ipcRenderer.invoke('toggle-maximize')
    } catch (err) {
      console.error('[double-click] error:', err)
    }
  }

  return (
    <div className="chat">
      {/* Header */}
      <div className={`chat-header ${!viewerVisible ? 'viewer-hidden' : ''}`} onDoubleClick={handleHeaderDoubleClick}>
        <div className="chat-header-left">
          {!viewerVisible && (
            <button
              type="button"
              className="toggle-viewer-btn"
              onClick={onToggleViewer}
              data-tooltip="Show Viewer"
              aria-label="Show Viewer"
            >
              <PanelLeftOpen size={18} />
            </button>
          )}
          <div className={`chat-agent-info ${!viewerVisible ? 'viewer-hidden' : ''}`}>
            <div className="chat-agent-name">
              {messages.length > 0 ? messages[0].content : 'New conversation'}
            </div>
          </div>
        </div>
        <div className={`chat-header-right ${!viewerVisible ? 'viewer-hidden' : ''}`}>
          <SessionHistory
            onLoadSession={handleLoadSession}
            refreshTrigger={sessionRefreshTrigger}
          />
          <button
            type="button"
            className="new-chat-btn"
            data-tooltip="New Chat"
            aria-label="New Chat"
            onClick={handleNewConversation}
          >
            <Plus size={18} />
          </button>
          {onHideChat && (
            <button
              type="button"
              className="hide-chat-btn"
              data-tooltip="Hide Chat"
              aria-label="Hide Chat"
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
                <div className="message-content">
                  {message.role === 'assistant' && message.agent_name && (
                    <div className="message-agent-name-above">
                      {message.agent_name}
                    </div>
                  )}
                  <div className="message-text">
                    {message.role === 'assistant' && message.label && message.label !== message.agent_name && (
                      <div className="message-tool-name">
                        {message.label}
                      </div>
                    )}
                    {message.content}
                  </div>
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
            placeholder="Ask to do anything"
            disabled={isStreaming}
            rows={1}
          />
          <div className="chat-input-buttons">
            <button
              type="button"
              className="input-action-btn"
              data-tooltip="Add attachment"
              aria-label="Add attachment"
            >
              <Plus size={16} />
            </button>
            <div className="input-dropdown-group">
              <select
                className="input-dropdown"
                value={selectedComputer}
                onChange={(e) => onSelectComputer(e.target.value)}
              >
                {computers.map(computer => (
                  <option key={computer.id} value={computer.id}>
                    {computer.name} {computer.status !== 'online' ? `(${computer.status})` : ''}
                  </option>
                ))}
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
                  aria-label="Select tools"
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
                        <button className="tool-configure-btn" aria-label="Configure integration">Configure</button>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('notion')}
                          onChange={() => toggleTool('notion')}
                        />
                        <span>Notion</span>
                        <button className="tool-configure-btn" aria-label="Configure integration">Configure</button>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('calendar')}
                          onChange={() => toggleTool('calendar')}
                        />
                        <span>Calendar</span>
                        <button className="tool-configure-btn" aria-label="Configure integration">Configure</button>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('gmail')}
                          onChange={() => toggleTool('gmail')}
                        />
                        <span>Gmail</span>
                        <button className="tool-configure-btn" aria-label="Configure integration">Configure</button>
                      </label>
                      <label className="tool-option">
                        <input
                          type="checkbox"
                          checked={selectedTools.includes('mcp')}
                          onChange={() => toggleTool('mcp')}
                        />
                        <span>Custom MCP</span>
                        <button className="tool-configure-btn" aria-label="Configure integration">Configure</button>
                      </label>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <button
              type="button"
              className="mic-btn"
              data-tooltip="Voice input"
              aria-label="Voice input"
            >
              <Mic size={16} />
            </button>
            {isStreaming ? (
              <button
                type="button"
                className="send-btn stop"
                onClick={handleStop}
                data-tooltip="Stop"
                aria-label="Stop"
              >
                <Square size={14} />
              </button>
            ) : (
              <button
                type="button"
                className="send-btn"
                onClick={handleSend}
                disabled={!input.trim()}
                data-tooltip="Send message"
                aria-label="Send message"
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

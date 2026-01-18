import { useState, useEffect } from 'react'
import ViewerTabs from './components/ViewerTabs'
import Chat from './components/Chat'
import Resizer from './components/Resizer'
import './styles/App.css'

function App() {
  const [viewerVisible, setViewerVisible] = useState(true)
  const [chatVisible, setChatVisible] = useState(true)
  const [chatWidth, setChatWidth] = useState(() => {
    const saved = localStorage.getItem('chatWidth')
    return saved ? parseInt(saved, 10) : 420
  })
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>('ceo-agent')
  const [selectedComputer, setSelectedComputer] = useState('local')
  const [computers, setComputers] = useState<any[]>([])

  const handleSelectAgent = (agentId: string, _agentName: string, _agentIcon: string) => {
    setSelectedAgentId(agentId)
  }

  // Save chat width to localStorage
  useEffect(() => {
    localStorage.setItem('chatWidth', chatWidth.toString())
  }, [chatWidth])

  // Fetch computers on mount
  useEffect(() => {
    const fetchComputers = async () => {
      try {
        const response = await fetch('/api/computers')
        if (response.ok) {
          const data = await response.json()
          setComputers(data)
        }
      } catch (error) {
        console.error('Failed to fetch computers:', error)
      }
    }
    fetchComputers()
  }, [])

  const handleChatResize = (deltaX: number) => {
    setChatWidth(prev => {
      // Dragging right = chat gets smaller (negative delta for chat)
      const newWidth = prev - deltaX
      // Ensure chat is at least 280px and leaves at least 300px for viewer
      const maxWidth = window.innerWidth - 300 - 5 // 5px for resizer
      return Math.max(280, Math.min(maxWidth, newWidth))
    })
  }

  return (
    <div className="app">
      {/* Viewer Tabs Panel */}
      {viewerVisible && (
        <div className={`viewer-panel ${!chatVisible ? 'viewer-expanded' : ''}`}>
          <ViewerTabs
            onClose={chatVisible ? () => setViewerVisible(false) : undefined}
            chatVisible={chatVisible}
            onToggleChat={() => setChatVisible(!chatVisible)}
            selectedComputer={selectedComputer}
          />
        </div>
      )}

      {/* Resizer between Viewer and Chat */}
      {viewerVisible && chatVisible && (
        <Resizer
          orientation="vertical"
          onResize={handleChatResize}
        />
      )}

      {/* Chat Panel */}
      {chatVisible && (
        <div className="chat-panel" style={viewerVisible ? { width: `${chatWidth}px` } : {}}>
          <Chat
            viewerVisible={viewerVisible}
            onToggleViewer={() => setViewerVisible(!viewerVisible)}
            onHideChat={viewerVisible ? () => setChatVisible(false) : undefined}
            selectedAgentId={selectedAgentId}
            onSelectAgent={handleSelectAgent}
            selectedComputer={selectedComputer}
            onSelectComputer={setSelectedComputer}
            computers={computers}
          />
        </div>
      )}
    </div>
  )
}

export default App

import { useState, useEffect } from 'react'
import ViewerTabs from './components/ViewerTabs'
import Chat from './components/Chat'
import Resizer from './components/Resizer'
import './styles/App.css'

function App() {
  const [viewerVisible, setViewerVisible] = useState(true)
  const [chatVisible, setChatVisible] = useState(true)
  const [viewerWidth, setViewerWidth] = useState(() => {
    const saved = localStorage.getItem('viewerWidth')
    return saved ? parseInt(saved, 10) : window.innerWidth - 420
  })
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>('ceo')
  const [selectedComputer, setSelectedComputer] = useState('local')
  const [computers, setComputers] = useState<any[]>([])

  const handleSelectAgent = (agentId: string, _agentName: string, _agentIcon: string) => {
    setSelectedAgentId(agentId)
  }

  // Save viewer width to localStorage
  useEffect(() => {
    localStorage.setItem('viewerWidth', viewerWidth.toString())
  }, [viewerWidth])

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

  const handleViewerResize = (deltaX: number) => {
    setViewerWidth(prev => {
      const newWidth = prev + deltaX
      // Ensure viewer is at least 300px and leaves at least 200px for chat
      const maxWidth = window.innerWidth - 200 - 5 // 5px for resizer
      return Math.max(300, Math.min(maxWidth, newWidth))
    })
  }

  return (
    <div className="app">
      {/* Viewer Tabs Panel */}
      {viewerVisible && (
        <div className={`viewer-panel ${!chatVisible ? 'viewer-expanded' : ''}`} style={chatVisible ? { width: `${viewerWidth}px` } : {}}>
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
          onResize={handleViewerResize}
        />
      )}

      {/* Chat Panel */}
      {chatVisible && (
        <div className="chat-panel">
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

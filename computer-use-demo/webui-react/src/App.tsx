import { useState } from 'react'
import ViewerTabs from './components/ViewerTabs'
import Chat from './components/Chat'
import Resizer from './components/Resizer'
import './styles/App.css'

function App() {
  const [viewerVisible, setViewerVisible] = useState(true)
  const [chatVisible, setChatVisible] = useState(true)
  const [viewerWidth, setViewerWidth] = useState(600)
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>('ceo')
  const [selectedAgentName, setSelectedAgentName] = useState<string>('CEO Agent')
  const [selectedAgentIcon, setSelectedAgentIcon] = useState<string>('👔')

  const handleSelectAgent = (agentId: string, agentName: string, agentIcon: string) => {
    setSelectedAgentId(agentId)
    setSelectedAgentName(agentName)
    setSelectedAgentIcon(agentIcon)
  }

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
            selectedAgentName={selectedAgentName}
            selectedAgentIcon={selectedAgentIcon}
            onSelectAgent={handleSelectAgent}
          />
        </div>
      )}
    </div>
  )
}

export default App

import { useState } from 'react'
import FileExplorer from './components/FileExplorer'
import FileViewer from './components/FileViewer'
import Chat from './components/Chat'
import Resizer from './components/Resizer'
import './styles/App.css'

function App() {
  const [dashboardVisible, setDashboardVisible] = useState(true)
  const [agentTreeVisible, setAgentTreeVisible] = useState(true)
  const [explorerWidth, setExplorerWidth] = useState(300)
  const [viewerWidth, setViewerWidth] = useState(400)
  const [selectedPath, setSelectedPath] = useState<string | null>(null)
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>('ceo')
  const [selectedAgentName, setSelectedAgentName] = useState<string>('CEO Agent')
  const [selectedAgentIcon, setSelectedAgentIcon] = useState<string>('👔')

  const handleSelectAgent = (agentId: string, agentName: string, agentIcon: string) => {
    setSelectedAgentId(agentId)
    setSelectedAgentName(agentName)
    setSelectedAgentIcon(agentIcon)
  }

  const handleExplorerResize = (deltaX: number) => {
    setExplorerWidth(prev => Math.max(200, Math.min(600, prev + deltaX)))
  }

  const handleViewerResize = (deltaX: number) => {
    setViewerWidth(prev => Math.max(300, Math.min(800, prev + deltaX)))
  }

  return (
    <div className="app">
      {/* Dashboard Panel (File Explorer + File Viewer) */}
      {dashboardVisible && (
        <div
          className="dashboard-panel"
          style={{ width: `${explorerWidth + viewerWidth}px` }}
        >
          {/* File Explorer */}
          <div
            className="file-explorer-container"
            style={{ width: `${explorerWidth}px` }}
          >
            <FileExplorer
              onSelectPath={setSelectedPath}
              selectedPath={selectedPath}
            />
          </div>

          {/* Resizer between Explorer and Viewer */}
          <Resizer
            orientation="vertical"
            onResize={handleExplorerResize}
          />

          {/* File Viewer */}
          <div
            className="file-viewer-container"
            style={{ width: `${viewerWidth}px` }}
          >
            <FileViewer
              selectedPath={selectedPath}
            />
          </div>
        </div>
      )}

      {/* Resizer between Dashboard and Chat */}
      {dashboardVisible && (
        <Resizer
          orientation="vertical"
          onResize={handleViewerResize}
        />
      )}

      {/* Chat Panel */}
      <div className="chat-panel">
        <Chat
          dashboardVisible={dashboardVisible}
          agentTreeVisible={agentTreeVisible}
          onToggleDashboard={() => setDashboardVisible(!dashboardVisible)}
          onToggleAgentTree={() => setAgentTreeVisible(!agentTreeVisible)}
          selectedAgentId={selectedAgentId}
          selectedAgentName={selectedAgentName}
          selectedAgentIcon={selectedAgentIcon}
          onSelectAgent={handleSelectAgent}
        />
      </div>
    </div>
  )
}

export default App

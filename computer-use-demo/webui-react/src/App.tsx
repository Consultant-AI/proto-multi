import { useState, useEffect } from 'react'
import ViewerTabs from './components/ViewerTabs'
import Chat from './components/Chat'
import Resizer from './components/Resizer'
import './styles/App.css'

function App() {
  const [viewerVisible, setViewerVisible] = useState(() => {
    const saved = localStorage.getItem('viewerVisible')
    return saved !== null ? saved === 'true' : true
  })
  const [chatVisible, setChatVisible] = useState(() => {
    const saved = localStorage.getItem('chatVisible')
    return saved !== null ? saved === 'true' : true
  })
  const [chatWidth, setChatWidth] = useState(() => {
    const saved = localStorage.getItem('chatWidth')
    return saved ? parseInt(saved, 10) : 420
  })
  const [isDarkTheme, setIsDarkTheme] = useState(() => {
    const saved = localStorage.getItem('isDarkTheme')
    return saved !== null ? saved === 'true' : true
  })
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>('ceo-agent')
  const [selectedComputer, setSelectedComputer] = useState('local')
  const [computers, setComputers] = useState<any[]>([])

  const handleSelectAgent = (agentId: string, _agentName: string, _agentIcon: string) => {
    setSelectedAgentId(agentId)
  }

  // Apply theme to document
  useEffect(() => {
    if (isDarkTheme) {
      document.documentElement.classList.remove('light-theme')
      document.documentElement.classList.add('dark-theme')
    } else {
      document.documentElement.classList.remove('dark-theme')
      document.documentElement.classList.add('light-theme')
    }
  }, [isDarkTheme])

  // Save UI state to localStorage
  useEffect(() => {
    localStorage.setItem('chatWidth', chatWidth.toString())
  }, [chatWidth])

  useEffect(() => {
    localStorage.setItem('viewerVisible', viewerVisible.toString())
  }, [viewerVisible])

  useEffect(() => {
    localStorage.setItem('chatVisible', chatVisible.toString())
  }, [chatVisible])

  useEffect(() => {
    localStorage.setItem('isDarkTheme', isDarkTheme.toString())
  }, [isDarkTheme])

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

  // Constrain chat width when window is resized
  useEffect(() => {
    const handleResize = () => {
      setChatWidth(prev => {
        const maxWidth = window.innerWidth - 200 - 5
        return Math.min(prev, maxWidth)
      })
    }
    // Constrain on initial load
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const handleChatResize = (deltaX: number) => {
    setChatWidth(prev => {
      // Dragging right = chat gets smaller (negative delta for chat)
      const newWidth = prev - deltaX
      // Ensure chat is at least 200px and leaves at least 200px for viewer
      const maxWidth = window.innerWidth - 200 - 5 // 5px for resizer
      return Math.max(200, Math.min(maxWidth, newWidth))
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
            isDarkTheme={isDarkTheme}
            onToggleTheme={() => setIsDarkTheme(!isDarkTheme)}
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
        <div className={`chat-panel ${!viewerVisible ? 'chat-expanded' : ''}`} style={viewerVisible ? { width: `${chatWidth}px` } : {}}>
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

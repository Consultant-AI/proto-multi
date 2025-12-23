import { useState, useEffect } from 'react'
import { Files, Globe, Terminal, Monitor, X, Plus, MessageSquare, FileText, FileCode, File, ChevronLeft, ChevronRight, RefreshCw, Sun, Moon } from 'lucide-react'
import { Tab, TabType } from '../types/tabs'
import Dashboard from './Dashboard'
import FileExplorer from './FileExplorer'
import FileViewer from './FileViewer'
import BrowserPanel from './BrowserPanel'
import ComputerPanel from './ComputerPanel'
import Resizer from './Resizer'
import '../styles/ViewerTabs.css'

interface ViewerTabsProps {
  onClose?: () => void
  chatVisible: boolean
  onToggleChat: () => void
}

const DEFAULT_TAB_ICONS: Record<TabType, JSX.Element> = {
  newtab: <Plus size={14} />,
  files: <Files size={14} />,
  web: <Globe size={14} />,
  terminal: <Terminal size={14} />,
  computer: <Monitor size={14} />
}

const TAB_LABELS: Record<TabType, string> = {
  newtab: 'New Tab',
  files: 'Files',
  web: 'Web',
  terminal: 'Terminal',
  computer: 'Computer'
}

const getFileIcon = (filename: string): JSX.Element => {
  if (filename.endsWith('.md') || filename.endsWith('.txt')) return <FileText size={14} />
  if (filename.endsWith('.py') || filename.endsWith('.js') || filename.endsWith('.ts') ||
      filename.endsWith('.tsx') || filename.endsWith('.jsx')) return <FileCode size={14} />
  return <File size={14} />
}

interface TabHistory {
  tabId: string
  history: Tab[]
  currentIndex: number
}

export default function ViewerTabs({ onClose, chatVisible, onToggleChat }: ViewerTabsProps) {
  const [tabs, setTabs] = useState<Tab[]>([
    { id: '1', type: 'newtab', title: 'New Tab', icon: <Plus size={14} /> }
  ])
  const [activeTabId, setActiveTabId] = useState('1')
  const [selectedPath, setSelectedPath] = useState<string | null>(null)
  const [explorerWidth, setExplorerWidth] = useState(250)
  const [explorerVisible, setExplorerVisible] = useState(true)
  const [tabHistories, setTabHistories] = useState<TabHistory[]>([
    { tabId: '1', history: [{ id: '1', type: 'newtab', title: 'New Tab', icon: <Plus size={14} /> }], currentIndex: 0 }
  ])
  const [addressBarInput, setAddressBarInput] = useState('')
  const [isDarkTheme, setIsDarkTheme] = useState(true)

  // Apply theme on mount and when it changes
  useEffect(() => {
    if (isDarkTheme) {
      document.documentElement.classList.remove('light-theme')
      document.documentElement.classList.add('dark-theme')
    } else {
      document.documentElement.classList.remove('dark-theme')
      document.documentElement.classList.add('light-theme')
    }
  }, [isDarkTheme])

  const toggleTheme = () => {
    setIsDarkTheme(prev => !prev)
  }

  const activeTab = tabs.find(tab => tab.id === activeTabId)
  const activeTabHistory = tabHistories.find(h => h.tabId === activeTabId)

  const handleOpenResource = (type: 'files' | 'web' | 'computer' | 'terminal', id: string) => {
    // Determine title and icon for the resource
    let title = TAB_LABELS[type]
    let icon: string | JSX.Element | undefined

    if (type === 'files') {
      // Extract filename from path
      const filename = id.split('/').pop() || id
      title = filename
      icon = getFileIcon(filename)
      // Set the selected path for file viewer
      setSelectedPath(id)
    } else if (type === 'web') {
      // For web, use the URL and try to get favicon
      try {
        const url = new URL(id)
        title = url.hostname
        // Use Google's favicon service
        icon = `https://www.google.com/s2/favicons?domain=${url.hostname}&sz=64`
      } catch {
        title = id
        icon = DEFAULT_TAB_ICONS.web
      }
    } else if (type === 'computer') {
      title = 'Computer'
      icon = <Monitor size={14} />
    } else if (type === 'terminal') {
      title = 'Terminal'
      icon = <Terminal size={14} />
    }

    // If current active tab is a newtab, convert it instead of creating new tab
    if (activeTab && activeTab.type === 'newtab') {
      const updatedTab = { ...activeTab, type, title, icon, resourceId: id }
      setTabs(prev => prev.map(tab =>
        tab.id === activeTabId ? updatedTab : tab
      ))

      // Add to history
      setTabHistories(prev => prev.map(th => {
        if (th.tabId === activeTabId) {
          // Remove any forward history and add new state
          const newHistory = [...th.history.slice(0, th.currentIndex + 1), updatedTab]
          return { ...th, history: newHistory, currentIndex: newHistory.length - 1 }
        }
        return th
      }))
    } else {
      // Otherwise create a new tab
      const newTab: Tab = {
        id: Date.now().toString(),
        type,
        title,
        icon,
        resourceId: id
      }
      setTabs(prev => [...prev, newTab])
      setActiveTabId(newTab.id)

      // Create history for new tab
      setTabHistories(prev => [...prev, {
        tabId: newTab.id,
        history: [newTab],
        currentIndex: 0
      }])
    }
  }

  const handleExplorerResize = (deltaX: number) => {
    setExplorerWidth(prev => Math.max(150, Math.min(400, prev + deltaX)))
  }

  const handleAddTab = (type: TabType = 'newtab') => {
    const newTab: Tab = {
      id: Date.now().toString(),
      type,
      title: TAB_LABELS[type],
      icon: DEFAULT_TAB_ICONS[type]
    }
    setTabs([...tabs, newTab])
    setActiveTabId(newTab.id)

    // Initialize history for new tab
    setTabHistories(prev => [...prev, {
      tabId: newTab.id,
      history: [newTab],
      currentIndex: 0
    }])
  }

  const handleBack = () => {
    if (!activeTabHistory || activeTabHistory.currentIndex <= 0) return

    const newIndex = activeTabHistory.currentIndex - 1
    const previousState = activeTabHistory.history[newIndex]

    // Update tab to previous state
    setTabs(prev => prev.map(tab =>
      tab.id === activeTabId ? previousState : tab
    ))

    // Update selected path based on tab type
    if (previousState.type === 'files' && previousState.resourceId) {
      setSelectedPath(previousState.resourceId)
    } else {
      setSelectedPath(null)
    }

    // Update history index
    setTabHistories(prev => prev.map(th =>
      th.tabId === activeTabId ? { ...th, currentIndex: newIndex } : th
    ))
  }

  const handleForward = () => {
    if (!activeTabHistory || activeTabHistory.currentIndex >= activeTabHistory.history.length - 1) return

    const newIndex = activeTabHistory.currentIndex + 1
    const nextState = activeTabHistory.history[newIndex]

    // Update tab to next state
    setTabs(prev => prev.map(tab =>
      tab.id === activeTabId ? nextState : tab
    ))

    // Update selected path based on tab type
    if (nextState.type === 'files' && nextState.resourceId) {
      setSelectedPath(nextState.resourceId)
    } else {
      setSelectedPath(null)
    }

    // Update history index
    setTabHistories(prev => prev.map(th =>
      th.tabId === activeTabId ? { ...th, currentIndex: newIndex } : th
    ))
  }

  const handleRefresh = () => {
    // Reload current content based on tab type
    if (activeTab?.type === 'files' && selectedPath) {
      // Trigger file reload by updating the path
      const currentPath = selectedPath
      setSelectedPath(null)
      setTimeout(() => setSelectedPath(currentPath), 0)
    }
    // Add other refresh logic for web, computer, terminal tabs as needed
  }

  const handleAddressBarSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key !== 'Enter') return

    const input = addressBarInput.trim()
    if (!input) return

    // Determine what type of resource the user wants to open
    if (input.startsWith('http://') || input.startsWith('https://')) {
      // It's a web URL
      handleOpenResource('web', input)
    } else if (input.startsWith('/') || input.includes('/')) {
      // It's a file path
      handleOpenResource('files', input)
    } else if (input === 'computer' || input.startsWith('computer://')) {
      // Computer view
      handleOpenResource('computer', 'main')
    } else if (input === 'terminal' || input.startsWith('terminal://')) {
      // Terminal
      handleOpenResource('terminal', 'main')
    } else {
      // Default: treat as file path
      handleOpenResource('files', input)
    }

    // Clear the input
    setAddressBarInput('')
  }

  const getTabIcon = (tab: Tab): JSX.Element | JSX.Element => {
    if (tab.icon) {
      // If icon is a string (URL), render as img
      if (typeof tab.icon === 'string') {
        return <img src={tab.icon} alt="" style={{ width: 14, height: 14, borderRadius: '2px' }} />
      }
      // Otherwise it's a JSX element
      return tab.icon
    }
    // Fallback to default icon
    return DEFAULT_TAB_ICONS[tab.type]
  }

  const handleCloseTab = (tabId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const newTabs = tabs.filter(tab => tab.id !== tabId)

    if (newTabs.length === 0) {
      // If no tabs left, close the viewer
      onClose?.()
      return
    }

    setTabs(newTabs)

    // Remove history for closed tab
    setTabHistories(prev => prev.filter(th => th.tabId !== tabId))

    // If closing active tab, switch to the last tab
    if (activeTabId === tabId) {
      setActiveTabId(newTabs[newTabs.length - 1].id)
    }
  }

  const renderPathBar = () => {
    if (!activeTab) return null

    const isNewTab = activeTab.type === 'newtab'
    let pathText = ''
    let placeholder = 'Path or URL'

    if (isNewTab) {
      pathText = addressBarInput
      placeholder = '/path/to/file • https://url • computer:// • terminal://'
    } else {
      switch (activeTab.type) {
        case 'files':
          pathText = selectedPath || activeTab.resourceId || ''
          break
        case 'web':
          pathText = activeTab.resourceId || ''
          break
        case 'computer':
          pathText = 'computer://live-view'
          break
        case 'terminal':
          pathText = `terminal://${activeTab.resourceId || 'session'}`
          break
      }
    }

    const canGoBack = activeTabHistory ? activeTabHistory.currentIndex > 0 : false
    const canGoForward = activeTabHistory ? activeTabHistory.currentIndex < activeTabHistory.history.length - 1 : false

    return (
      <div className="tab-path-bar">
        <div className="browser-controls">
          <button
            className="nav-btn"
            onClick={handleBack}
            disabled={!canGoBack}
            title="Back"
          >
            <ChevronLeft size={16} />
          </button>
          <button
            className="nav-btn"
            onClick={handleForward}
            disabled={!canGoForward}
            title="Forward"
          >
            <ChevronRight size={16} />
          </button>
          <button
            className="nav-btn refresh-nav-btn"
            onClick={handleRefresh}
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>
        <div className="path-input-wrapper">
          <input
            type="text"
            className="path-input"
            value={pathText}
            onChange={isNewTab ? (e) => setAddressBarInput(e.target.value) : undefined}
            onKeyDown={isNewTab ? handleAddressBarSubmit : undefined}
            readOnly={!isNewTab}
            placeholder={placeholder}
          />
        </div>
      </div>
    )
  }

  const renderTabContent = () => {
    if (!activeTab) return null

    switch (activeTab.type) {
      case 'newtab':
        return <Dashboard onOpenResource={handleOpenResource} />

      case 'files':
        return (
          <div className="files-layout">
            {explorerVisible && (
              <>
                <div
                  className="file-explorer-section"
                  style={{ width: `${explorerWidth}px` }}
                >
                  <FileExplorer
                    onSelectPath={setSelectedPath}
                    selectedPath={selectedPath}
                    onToggleVisible={() => setExplorerVisible(false)}
                  />
                </div>
                <Resizer
                  orientation="vertical"
                  onResize={handleExplorerResize}
                />
              </>
            )}
            <div className="file-viewer-section">
              <FileViewer
                selectedPath={selectedPath}
                explorerVisible={explorerVisible}
                onToggleExplorer={() => setExplorerVisible(!explorerVisible)}
              />
            </div>
          </div>
        )

      case 'web':
        return (
          <div className="web-layout">
            <BrowserPanel url={activeTab.resourceId} />
          </div>
        )

      case 'terminal':
        return (
          <div className="terminal-layout">
            <div className="terminal-placeholder">
              <Terminal size={48} />
              <h3>Terminal Sessions</h3>
              <p>Terminal view coming soon</p>
            </div>
          </div>
        )

      case 'computer':
        return (
          <div className="computer-layout">
            <ComputerPanel />
          </div>
        )
    }
  }

  return (
    <div className="viewer-tabs">
      {/* Tab bar */}
      <div className="viewer-tabs-header">
        <div className="viewer-tabs-list">
          {tabs.map(tab => (
            <div
              key={tab.id}
              className={`viewer-tab ${activeTabId === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTabId(tab.id)}
            >
              <span className="viewer-tab-icon">{getTabIcon(tab)}</span>
              <span className="viewer-tab-title">{tab.title}</span>
              <button
                className="viewer-tab-close"
                onClick={(e) => handleCloseTab(tab.id, e)}
                title="Close tab"
              >
                <X size={14} />
              </button>
            </div>
          ))}

          {/* New tab button */}
          <button
            className="new-tab-btn"
            onClick={() => handleAddTab('newtab')}
            title="New tab"
          >
            <Plus size={16} />
          </button>
        </div>

        <div className="viewer-header-controls">
          {!chatVisible && (
            <button
              className="toggle-chat-btn"
              onClick={onToggleChat}
              title="Show Chat"
            >
              <MessageSquare size={16} />
            </button>
          )}
          <button
            className="toggle-theme-btn"
            onClick={toggleTheme}
            title={isDarkTheme ? "Switch to Light Theme" : "Switch to Dark Theme"}
          >
            {isDarkTheme ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          {onClose && (
            <button className="viewer-close-btn" onClick={onClose} title="Close Viewer">
              <X size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Content area */}
      <div className="viewer-tabs-content">
        {renderPathBar()}
        {renderTabContent()}
      </div>
    </div>
  )
}

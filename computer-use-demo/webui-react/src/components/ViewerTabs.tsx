import { useState, useEffect, useRef, useCallback } from 'react'
import { Files, Globe, Terminal, Monitor, X, Plus, MessageSquare, FileText, FileCode, File, ChevronLeft, ChevronRight, RefreshCw, Sun, Moon, Layers } from 'lucide-react'
import { Tab, TabType } from '../types/tabs'
import Dashboard from './Dashboard'
import FileExplorer from './FileExplorer'
import FileViewer from './FileViewer'
import BrowserPanel, { BrowserPanelRef } from './BrowserPanel'
import ComputerPanel from './ComputerPanel'
import ComputersOverview from './ComputersOverview'
import Resizer from './Resizer'
import '../styles/ViewerTabs.css'

interface ViewerTabsProps {
  onClose?: () => void
  chatVisible: boolean
  onToggleChat: () => void
  selectedComputer?: string
}

const DEFAULT_TAB_ICONS: Record<TabType, JSX.Element> = {
  newtab: <Plus size={14} />,
  files: <Files size={14} />,
  web: <Globe size={14} />,
  terminal: <Terminal size={14} />,
  computer: <Monitor size={14} />,
  computers: <Layers size={14} />
}

const TAB_LABELS: Record<TabType, string> = {
  newtab: 'New Tab',
  files: 'Files',
  web: 'Web',
  terminal: 'Terminal',
  computer: 'Computer',
  computers: 'All Computers'
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

// Serializable formats for localStorage (no JSX)
interface SerializableTab {
  id: string
  type: TabType
  title: string
  iconUrl?: string  // Only for string icons (favicons)
  resourceId?: string
}

interface SerializableTabHistory {
  tabId: string
  history: SerializableTab[]
  currentIndex: number
}

interface StoredState {
  tabs: SerializableTab[]
  activeTabId: string
  tabHistories: SerializableTabHistory[]
  selectedPath: string | null
  isDarkTheme: boolean
}

const STORAGE_KEY = 'viewerTabsState'

// Convert tab to serializable format
const serializeTab = (tab: Tab): SerializableTab => ({
  id: tab.id,
  type: tab.type,
  title: tab.title,
  iconUrl: typeof tab.icon === 'string' ? tab.icon : undefined,
  resourceId: tab.resourceId
})

// Convert serializable tab back to Tab with JSX icon
const deserializeTab = (serialized: SerializableTab): Tab => ({
  id: serialized.id,
  type: serialized.type,
  title: serialized.title,
  icon: serialized.iconUrl
    ? serialized.iconUrl
    : serialized.type === 'files' && serialized.resourceId
      ? getFileIcon(serialized.resourceId.split('/').pop() || '')
      : DEFAULT_TAB_ICONS[serialized.type],
  resourceId: serialized.resourceId
})

// Load state from localStorage
const loadStoredState = (): StoredState | null => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return null
    return JSON.parse(stored)
  } catch {
    return null
  }
}

// Initialize state from localStorage or defaults
const getInitialState = () => {
  const stored = loadStoredState()
  if (stored && stored.tabs.length > 0) {
    const tabs = stored.tabs.map(deserializeTab)
    const tabHistories = stored.tabHistories.map(th => ({
      tabId: th.tabId,
      history: th.history.map(deserializeTab),
      currentIndex: th.currentIndex
    }))
    return {
      tabs,
      activeTabId: stored.activeTabId,
      tabHistories,
      selectedPath: stored.selectedPath,
      isDarkTheme: stored.isDarkTheme
    }
  }

  // Default state
  const defaultTab: Tab = { id: '1', type: 'newtab', title: 'New Tab', icon: <Plus size={14} /> }
  return {
    tabs: [defaultTab],
    activeTabId: '1',
    tabHistories: [{ tabId: '1', history: [defaultTab], currentIndex: 0 }],
    selectedPath: null,
    isDarkTheme: true
  }
}

export default function ViewerTabs({ onClose, chatVisible, onToggleChat, selectedComputer }: ViewerTabsProps) {
  const initialState = getInitialState()
  const [tabs, setTabs] = useState<Tab[]>(initialState.tabs)
  const [activeTabId, setActiveTabId] = useState(initialState.activeTabId)
  const [selectedPath, setSelectedPath] = useState<string | null>(initialState.selectedPath)
  const [explorerWidth, setExplorerWidth] = useState(250)
  const [explorerVisible, setExplorerVisible] = useState(true)
  const [tabHistories, setTabHistories] = useState<TabHistory[]>(initialState.tabHistories)
  const [addressBarInput, setAddressBarInput] = useState('')
  const [isDarkTheme, setIsDarkTheme] = useState(initialState.isDarkTheme)
  const [explorerRefreshKey, setExplorerRefreshKey] = useState(0)

  // Web tab state
  const [webTabUrls, setWebTabUrls] = useState<Record<string, string>>({})
  const [webTabNavState, setWebTabNavState] = useState<Record<string, { canGoBack: boolean; canGoForward: boolean }>>({})
  const [webTabLoading, setWebTabLoading] = useState<Record<string, boolean>>({})
  const browserRefs = useRef<Record<string, BrowserPanelRef | null>>({})

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

  // Save state to localStorage whenever tabs or related state changes
  useEffect(() => {
    const state: StoredState = {
      tabs: tabs.map(serializeTab),
      activeTabId,
      tabHistories: tabHistories.map(th => ({
        tabId: th.tabId,
        history: th.history.map(serializeTab),
        currentIndex: th.currentIndex
      })),
      selectedPath,
      isDarkTheme
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch (e) {
      console.error('Failed to save tabs state:', e)
    }
  }, [tabs, activeTabId, tabHistories, selectedPath, isDarkTheme])

  const toggleTheme = () => {
    setIsDarkTheme(prev => !prev)
  }

  const activeTab = tabs.find(tab => tab.id === activeTabId)
  const activeTabHistory = tabHistories.find(h => h.tabId === activeTabId)

  const handleOpenResource = (type: 'files' | 'web' | 'computer' | 'computers' | 'terminal', id: string) => {
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
      // For computer tabs, use the computer ID as title
      // Convert 'hetzner-116309743' to just 'agent-sdk-demo-1' if available
      title = id === 'main' || id === 'local' ? 'This Computer' : id
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

      // Replace history - don't keep newtab in history (user shouldn't go back to newtab)
      setTabHistories(prev => prev.map(th => {
        if (th.tabId === activeTabId) {
          return { ...th, history: [updatedTab], currentIndex: 0 }
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
    setTabs(prev => [...prev, newTab])
    setActiveTabId(newTab.id)

    // Initialize history for new tab
    setTabHistories(prev => [...prev, {
      tabId: newTab.id,
      history: [newTab],
      currentIndex: 0
    }])
  }

  const handleBack = () => {
    // For web tabs, use browser's native back
    if (activeTab?.type === 'web') {
      const browserRef = browserRefs.current[activeTab.id]
      browserRef?.goBack()
      return
    }

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
    // For web tabs, use browser's native forward
    if (activeTab?.type === 'web') {
      const browserRef = browserRefs.current[activeTab.id]
      browserRef?.goForward()
      return
    }

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
    // For web tabs, use browser's reload
    if (activeTab?.type === 'web') {
      const browserRef = browserRefs.current[activeTab.id]
      browserRef?.reload()
      return
    }

    // Reload current content based on tab type
    if (activeTab?.type === 'files') {
      // Trigger explorer refresh
      setExplorerRefreshKey(prev => prev + 1)

      // Also trigger file content reload if a file is selected
      if (selectedPath) {
        const currentPath = selectedPath
        setSelectedPath(null)
        setTimeout(() => setSelectedPath(currentPath), 0)
      }
    }
  }

  // Handle file path selection with history tracking
  const handleSelectPath = (path: string) => {
    // If we're not on a files tab, use handleOpenResource to create/switch tabs
    if (!activeTab || activeTab.type !== 'files') {
      handleOpenResource('files', path)
      return
    }

    // If selecting the same path, do nothing
    if (selectedPath === path) return

    // Update selectedPath
    setSelectedPath(path)

    // Update the tab title and icon
    const filename = path.split('/').pop() || path
    const updatedTab = {
      ...activeTab,
      title: filename,
      icon: getFileIcon(filename),
      resourceId: path
    }

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
  }

  const handleAddressBarSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key !== 'Enter') return

    const input = addressBarInput.trim()
    if (!input) return

    // Regex to detect domain-like patterns (e.g., google.com, example.org, sub.domain.co.uk)
    const domainPattern = /^[\w-]+(\.[\w-]+)+(\/.*)?(:\d+)?$/

    // Determine what type of resource the user wants to open
    if (input.startsWith('http://') || input.startsWith('https://')) {
      // It's a web URL
      handleOpenResource('web', input)
    } else if (domainPattern.test(input)) {
      // Looks like a domain (e.g., google.com, facebook.com/path)
      handleOpenResource('web', `https://${input}`)
    } else if (input.startsWith('/') || input.includes('/')) {
      // It's a file path
      handleOpenResource('files', input)
    } else if (input === 'computer' || input.startsWith('computer://')) {
      // Computer view - extract computer ID from URL
      const computerId = input.startsWith('computer://') ? input.substring(12) : 'local'
      handleOpenResource('computer', computerId || 'local')
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

  // Handle web address bar changes
  const handleWebAddressChange = (tabId: string, value: string) => {
    setWebTabUrls(prev => ({ ...prev, [tabId]: value }))
  }

  // Handle web address bar submit
  const handleWebAddressSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key !== 'Enter' || !activeTab || activeTab.type !== 'web') return

    const url = webTabUrls[activeTab.id] || ''
    if (!url) return

    // Add protocol if missing
    let fullUrl = url
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      fullUrl = 'https://' + url
    }

    const browserRef = browserRefs.current[activeTab.id]
    browserRef?.navigateTo(fullUrl)
  }

  const renderPathBar = () => {
    if (!activeTab) return null

    const isNewTab = activeTab.type === 'newtab'
    const isWebTab = activeTab.type === 'web'
    let pathText = ''
    let placeholder = 'Path or URL'

    if (isNewTab) {
      pathText = addressBarInput
      placeholder = '/path/to/file • https://url • computer:// • terminal://'
    } else if (isWebTab) {
      // For web tabs, use the tracked URL or resourceId
      pathText = webTabUrls[activeTab.id] ?? activeTab.resourceId ?? ''
    } else {
      switch (activeTab.type) {
        case 'files':
          pathText = selectedPath || activeTab.resourceId || ''
          break
        case 'computer':
          // Show computer:// URL with resourceId or localhost
          const computerId = activeTab.resourceId
          if (!computerId || computerId === 'main' || computerId === 'local' || computerId === '') {
            pathText = 'computer://localhost'
          } else if (computerId.startsWith('hetzner-')) {
            // For Hetzner instances, try to extract IP if available in title
            pathText = `computer://${computerId}`
          } else {
            pathText = `computer://${computerId}`
          }
          break
        case 'terminal':
          pathText = `terminal://${activeTab.resourceId || 'session'}`
          break
      }
    }

    // For web tabs, use browser's navigation state; for others, use tab history
    let canGoBack = false
    let canGoForward = false

    if (isWebTab) {
      const navState = webTabNavState[activeTab.id]
      canGoBack = navState?.canGoBack ?? false
      canGoForward = navState?.canGoForward ?? false
    } else {
      canGoBack = activeTabHistory ? activeTabHistory.currentIndex > 0 : false
      canGoForward = activeTabHistory ? activeTabHistory.currentIndex < activeTabHistory.history.length - 1 : false
    }

    const isEditable = isNewTab || isWebTab
    const isLoading = isWebTab && webTabLoading[activeTab.id]

    return (
      <div className="tab-path-bar">
        <div className="browser-controls">
          <button
            className="nav-btn"
            onClick={handleBack}
            disabled={!canGoBack}
            data-tooltip="Back"
            aria-label="Back"
          >
            <ChevronLeft size={16} />
          </button>
          <button
            className="nav-btn"
            onClick={handleForward}
            disabled={!canGoForward}
            data-tooltip="Forward"
            aria-label="Forward"
          >
            <ChevronRight size={16} />
          </button>
          <button
            className={`nav-btn refresh-nav-btn ${isLoading ? 'loading' : ''}`}
            onClick={handleRefresh}
            data-tooltip="Refresh"
            aria-label="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>
        <div className="path-input-wrapper">
          <input
            type="text"
            className="path-input"
            value={pathText}
            onChange={
              isNewTab
                ? (e) => setAddressBarInput(e.target.value)
                : isWebTab
                  ? (e) => handleWebAddressChange(activeTab.id, e.target.value)
                  : undefined
            }
            onKeyDown={
              isNewTab
                ? handleAddressBarSubmit
                : isWebTab
                  ? handleWebAddressSubmit
                  : undefined
            }
            readOnly={!isEditable}
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
                    onSelectPath={handleSelectPath}
                    selectedPath={selectedPath}
                    onToggleVisible={() => setExplorerVisible(false)}
                    refreshKey={explorerRefreshKey}
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
                isDarkTheme={isDarkTheme}
              />
            </div>
          </div>
        )

      case 'web':
        return (
          <div className="web-layout">
            <BrowserPanel
              key={activeTab.id}
              ref={(ref) => { browserRefs.current[activeTab.id] = ref }}
              tabId={activeTab.id}
              url={activeTab.resourceId}
              isActive={true}
              onUrlChange={(url) => {
                setWebTabUrls(prev => ({ ...prev, [activeTab.id]: url }))
                // Also update tab title, icon, and resourceId so URL persists when switching tabs
                try {
                  const urlObj = new URL(url)
                  const hostname = urlObj.hostname
                  setTabs(prev => prev.map(tab =>
                    tab.id === activeTab.id
                      ? { ...tab, title: hostname, icon: `https://www.google.com/s2/favicons?domain=${hostname}&sz=64`, resourceId: url }
                      : tab
                  ))
                } catch {}
              }}
              onLoadingChange={(loading) => {
                setWebTabLoading(prev => ({ ...prev, [activeTab.id]: loading }))
              }}
              onNavigationChange={(canBack, canForward) => {
                setWebTabNavState(prev => ({ ...prev, [activeTab.id]: { canGoBack: canBack, canGoForward: canForward } }))
              }}
            />
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
            <ComputerPanel
              key={activeTab.resourceId || 'local'}
              isActive={true}
              selectedComputer={selectedComputer}
              resourceId={activeTab.resourceId}
            />
          </div>
        )

      case 'computers':
        return (
          <div className="computers-layout">
            <ComputersOverview
              onSelectComputer={(computerId) => {
                handleOpenResource('computer', computerId)
              }}
            />
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
                data-tooltip="Close tab"
                aria-label="Close tab"
              >
                <X size={14} />
              </button>
            </div>
          ))}

          {/* New tab button */}
          <button
            className="new-tab-btn"
            onClick={() => handleAddTab('newtab')}
            data-tooltip="New tab"
            aria-label="New tab"
          >
            <Plus size={16} />
          </button>
        </div>

        <div className="viewer-header-controls">
          {!chatVisible && (
            <button
              className="toggle-chat-btn"
              onClick={onToggleChat}
              data-tooltip="Show Chat"
              aria-label="Show Chat"
            >
              <MessageSquare size={16} />
            </button>
          )}
          <button
            className="toggle-theme-btn"
            onClick={toggleTheme}
            data-tooltip={isDarkTheme ? "Switch to Light Theme" : "Switch to Dark Theme"}
            aria-label={isDarkTheme ? "Switch to Light Theme" : "Switch to Dark Theme"}
          >
            {isDarkTheme ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          {onClose && (
            <button className="viewer-close-btn" onClick={onClose} data-tooltip="Close Viewer" aria-label="Close Viewer">
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

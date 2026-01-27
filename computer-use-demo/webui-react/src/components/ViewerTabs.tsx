import { useState, useEffect, useRef, useCallback } from 'react'
import { Files, Globe, Terminal, Monitor, X, Plus, MessageSquare, FileText, FileCode, File, ChevronLeft, ChevronRight, RefreshCw, Sun, Moon, Layers } from 'lucide-react'
import { Tab, TabType } from '../types/tabs'
import Dashboard from './Dashboard'
import FileExplorer from './FileExplorer'
import FileViewer from './FileViewer'
import BrowserPanel, { BrowserPanelRef } from './BrowserPanel'
import ComputerPanel from './ComputerPanel'
import ComputersOverview from './ComputersOverview'
import TerminalPanel from './TerminalPanel'
import Resizer from './Resizer'
import '../styles/ViewerTabs.css'

interface ViewerTabsProps {
  onClose?: () => void
  chatVisible: boolean
  onToggleChat: () => void
  selectedComputer?: string
  isDarkTheme: boolean
  onToggleTheme: () => void
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
      selectedPath: stored.selectedPath
    }
  }

  // Default state
  const defaultTab: Tab = { id: '1', type: 'newtab', title: 'New Tab', icon: <Plus size={14} /> }
  return {
    tabs: [defaultTab],
    activeTabId: '1',
    tabHistories: [{ tabId: '1', history: [defaultTab], currentIndex: 0 }],
    selectedPath: null
  }
}

export default function ViewerTabs({ onClose, chatVisible, onToggleChat, selectedComputer, isDarkTheme, onToggleTheme }: ViewerTabsProps) {
  const initialState = getInitialState()
  const [tabs, setTabs] = useState<Tab[]>(initialState.tabs)
  const [activeTabId, setActiveTabId] = useState(initialState.activeTabId)
  const [selectedPath, setSelectedPath] = useState<string | null>(initialState.selectedPath)
  const [explorerWidth, setExplorerWidth] = useState(250)
  const [explorerVisible, setExplorerVisible] = useState(true)
  const [tabHistories, setTabHistories] = useState<TabHistory[]>(initialState.tabHistories)
  const [addressBarInput, setAddressBarInput] = useState('')
  const [explorerRefreshKey, setExplorerRefreshKey] = useState(0)

  // Web tab state
  const [webTabUrls, setWebTabUrls] = useState<Record<string, string>>({})
  const [webTabNavState, setWebTabNavState] = useState<Record<string, { canGoBack: boolean; canGoForward: boolean }>>({})
  const [webTabLoading, setWebTabLoading] = useState<Record<string, boolean>>({})
  const browserRefs = useRef<Record<string, BrowserPanelRef | null>>({})

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
      selectedPath
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    } catch (e) {
      console.error('Failed to save tabs state:', e)
    }
  }, [tabs, activeTabId, tabHistories, selectedPath])

  // Double-click on header toggles window maximize (macOS-style behavior)
  const handleHeaderDoubleClick = (e: React.MouseEvent) => {
    const target = e.target as HTMLElement
    console.log('[double-click] event fired on:', target.className)

    // Only trigger if clicking on empty space (not on tabs, buttons, icons)
    const clickedOnInteractive = target.closest('button, .viewer-tab, .new-tab-btn, .toggle-chat-btn, .toggle-theme-btn, .viewer-close-btn')
    if (clickedOnInteractive) {
      console.log('[double-click] clicked on interactive element, ignoring')
      return
    }

    console.log('[double-click] attempting to toggle maximize')
    console.log('[double-click] window.require exists:', typeof window.require)

    // Use Electron IPC to toggle maximize
    try {
      const { ipcRenderer } = window.require('electron')
      console.log('[double-click] ipcRenderer:', ipcRenderer)
      ipcRenderer.invoke('toggle-maximize')
    } catch (err) {
      console.error('[double-click] error:', err)
    }
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
      // Generate unique session ID if not provided
      const sessionId = id || `terminal-${Date.now()}`
      id = sessionId
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
    // For web tabs, check if browser can go back first
    if (activeTab?.type === 'web') {
      const browserRef = browserRefs.current[activeTab.id]
      const navState = webTabNavState[activeTab.id]
      if (navState?.canGoBack) {
        browserRef?.goBack()
        return
      }
      // If browser can't go back, fall through to go back to newtab
    }

    // If there's history to go back to, use it
    if (activeTabHistory && activeTabHistory.currentIndex > 0) {
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
      return
    }

    // No history - go back to newtab screen if not already on newtab
    if (activeTab && activeTab.type !== 'newtab') {
      const newTabState: Tab = {
        id: activeTab.id,
        type: 'newtab',
        title: 'New Tab',
        icon: <Plus size={14} />
      }

      setTabs(prev => prev.map(tab =>
        tab.id === activeTabId ? newTabState : tab
      ))

      setSelectedPath(null)

      // Reset history to just the newtab
      setTabHistories(prev => prev.map(th =>
        th.tabId === activeTabId ? { ...th, history: [newTabState], currentIndex: 0 } : th
      ))
    }
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

  // Memoized callback for toggling explorer visibility - prevents FileExplorer rerenders
  const handleToggleExplorerVisible = useCallback(() => {
    setExplorerVisible(false)
  }, [])

  // Handle file path selection with history tracking - memoized to prevent FileExplorer rerenders
  const handleSelectPath = useCallback((path: string) => {
    console.log('[handleSelectPath] called with path:', path)

    setSelectedPath(currentSelectedPath => {
      // If selecting the same path, do nothing
      if (currentSelectedPath === path) {
        console.log('[handleSelectPath] same path, skipping')
        return currentSelectedPath
      }
      return path
    })

    // Update tab and history using functional updates to avoid stale closures
    setTabs(prev => {
      const currentActiveTab = prev.find(t => t.id === activeTabId)
      if (!currentActiveTab || currentActiveTab.type !== 'files') {
        // Not on files tab - this shouldn't happen if called from FileExplorer
        return prev
      }

      const filename = path.split('/').pop() || path
      const updatedTab = {
        ...currentActiveTab,
        title: filename,
        icon: getFileIcon(filename),
        resourceId: path
      }

      return prev.map(tab => tab.id === activeTabId ? updatedTab : tab)
    })

    // Add to history
    setTabHistories(prev => prev.map(th => {
      if (th.tabId !== activeTabId) return th

      const filename = path.split('/').pop() || path
      const currentTab = th.history[th.currentIndex]
      if (!currentTab || currentTab.type !== 'files') return th

      const updatedTab = {
        ...currentTab,
        title: filename,
        icon: getFileIcon(filename),
        resourceId: path
      }

      const newHistory = [...th.history.slice(0, th.currentIndex + 1), updatedTab]
      return { ...th, history: newHistory, currentIndex: newHistory.length - 1 }
    }))
  }, [activeTabId])

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
          console.log('[renderPathBar] files tab - selectedPath:', selectedPath, 'resourceId:', activeTab.resourceId, 'pathText:', pathText)
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
      // Web tabs can go back if browser has history OR if we can go back to newtab
      canGoBack = (navState?.canGoBack ?? false) || true // Always can go back to newtab from web
      canGoForward = navState?.canGoForward ?? false
    } else if (isNewTab) {
      // New tab has no back
      canGoBack = false
      canGoForward = activeTabHistory ? activeTabHistory.currentIndex < activeTabHistory.history.length - 1 : false
    } else {
      // Content tabs (files, terminal, computer) can always go back (to newtab if no history)
      canGoBack = true
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
                    onToggleVisible={handleToggleExplorerVisible}
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
                onPathChange={handleSelectPath}
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
            <TerminalPanel
              key={activeTab.id}
              sessionId={activeTab.resourceId || activeTab.id}
              isActive={true}
            />
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
      <div className="viewer-tabs-header" onDoubleClick={handleHeaderDoubleClick}>
        <div className="viewer-tabs-area">
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
          </div>

          {/* New tab button - next to tabs */}
          <button
            type="button"
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
            onClick={onToggleTheme}
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

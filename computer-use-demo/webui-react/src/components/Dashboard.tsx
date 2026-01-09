import { useState, useEffect, useRef, useCallback } from 'react'
import { Folder, FolderOpen, Globe, Monitor, Terminal, Plus, ChevronRight, ChevronDown, MoreVertical, Pause, Power, Trash2, RefreshCw, Cloud } from 'lucide-react'
import '../styles/Dashboard.css'

interface DashboardProps {
  onOpenResource?: (type: 'files' | 'web' | 'computer' | 'computers' | 'terminal', id: string) => void
}

interface FileNode {
  name: string
  path: string
  type: 'folder' | 'file'
  children?: FileNode[]
}

interface HetznerInstance {
  id: number
  name: string
  status: string
  public_net?: { ipv4?: { ip: string } }
  server_type?: { name: string; description: string }
  created: string
}

export default function Dashboard({ onOpenResource }: DashboardProps) {
  const [folders, setFolders] = useState<FileNode[]>([])
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
  const [webPages, setWebPages] = useState<any[]>([])
  const [terminals, setTerminals] = useState<any[]>([])
  const [history, setHistory] = useState<any[]>([])

  // Computer states
  const [hetznerInstances, setHetznerInstances] = useState<HetznerInstance[]>([])
  const [localScreenshot, setLocalScreenshot] = useState<string | null>(null)
  const [activeMenu, setActiveMenu] = useState<string | null>(null)
  const [isCreatingInstance, setIsCreatingInstance] = useState(false)
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const menuRef = useRef<HTMLDivElement>(null)

  // Fetch local screenshot
  const fetchLocalScreenshot = useCallback(async () => {
    try {
      const response = await fetch('/api/computer/screenshot')
      if (response.ok) {
        const data = await response.json()
        setLocalScreenshot(data.image)
      }
    } catch (err) {
      console.error('Failed to fetch screenshot:', err)
    }
  }, [])

  // Fetch Hetzner instances
  const fetchHetznerInstances = useCallback(async () => {
    try {
      const response = await fetch('/api/hetzner/instances')
      if (response.ok) {
        const data = await response.json()
        setHetznerInstances(data.instances || [])
      }
    } catch (err) {
      console.error('Failed to fetch Hetzner instances:', err)
    }
  }, [])

  // Helper to filter out paths that are already contained within another path in the list
  const filterRedundantPaths = (nodes: FileNode[]): FileNode[] => {
    return nodes.filter(node => {
      return !nodes.some(otherNode => {
        if (otherNode.path === node.path) return false
        return node.path.startsWith(otherNode.path + '/')
      })
    })
  }

  // Load folder contents during initial setup
  const loadFolderContentsInitial = async (path: string, currentFolders: FileNode[]) => {
    try {
      const isAbsolutePath = path.startsWith('/')
      const apiPath = isAbsolutePath
        ? `/api/browse/folder?path=${encodeURIComponent(path)}`
        : `/api/dashboard/folder?path=${encodeURIComponent(path)}`

      const response = await fetch(apiPath)
      if (!response.ok) return

      const data = await response.json()

      // Update the folder tree with loaded children
      const updateTreeNode = (nodes: FileNode[]): FileNode[] => {
        return nodes.map(node => {
          if (node.path === path) {
            const children: FileNode[] = [
              ...data.folders.map((folder: { name: string; path: string }) => ({
                name: folder.name,
                path: folder.path,
                type: 'folder' as const,
                children: []
              })),
              ...data.files.map((file: { name: string }) => ({
                name: file.name,
                path: `${path}/${file.name}`,
                type: 'file' as const
              }))
            ]
            return { ...node, children }
          } else if (node.children && node.children.length > 0) {
            return { ...node, children: updateTreeNode(node.children) }
          }
          return node
        })
      }

      setFolders(prevFolders => updateTreeNode(prevFolders.length > 0 ? prevFolders : currentFolders))
    } catch (error) {
      console.error('Failed to load folder contents:', error)
    }
  }

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setActiveMenu(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    // Fetch real data from backend
    const fetchData = async () => {
      try {
        // Fetch folders from projects endpoint (same as FileExplorer)
        const projectsRes = await fetch('/api/dashboard/projects')
        if (projectsRes.ok) {
          const projects = await projectsRes.json()
          const projectFolders: FileNode[] = projects.map((project: any) => ({
            name: project.name,
            path: project.path,
            type: 'folder',
            children: []
          }))

          // Load custom paths from localStorage (same as FileExplorer)
          const saved = localStorage.getItem('explorer_custom_paths')
          let customPaths: FileNode[] = []
          if (saved) {
            try {
              customPaths = JSON.parse(saved)
            } catch {
              // Invalid JSON, ignore
            }
          }

          // Migration: Remove old ~/Proto entries (they were moved to projects/)
          const oldProtoPattern = /\/Proto$/
          const hadOldEntries = customPaths.some(p => oldProtoPattern.test(p.path))
          if (hadOldEntries) {
            customPaths = customPaths.filter(p => !oldProtoPattern.test(p.path))
            localStorage.setItem('explorer_custom_paths', JSON.stringify(customPaths))
          }

          // If no custom paths, try to add the default projects path
          if (customPaths.length === 0) {
            try {
              const configRes = await fetch('/api/dashboard/config')
              if (configRes.ok) {
                const config = await configRes.json()
                const defaultPath = config.defaultProjectPath
                if (defaultPath) {
                  // Pre-load folder contents
                  let children: FileNode[] = []
                  try {
                    const folderRes = await fetch(`/api/browse/folder?path=${encodeURIComponent(defaultPath)}`)
                    if (folderRes.ok) {
                      const folderData = await folderRes.json()
                      children = [
                        ...folderData.folders.map((folder: { name: string; path: string }) => ({
                          name: folder.name,
                          path: folder.path,
                          type: 'folder' as const,
                          children: []
                        })),
                        ...folderData.files.map((file: { name: string }) => ({
                          name: file.name,
                          path: `${defaultPath}/${file.name}`,
                          type: 'file' as const
                        }))
                      ]
                    }
                  } catch {
                    // Ignore folder content load failure
                  }

                  const defaultNode: FileNode = {
                    name: 'Projects',
                    path: defaultPath,
                    type: 'folder',
                    children
                  }
                  customPaths = [defaultNode]
                  // Save to localStorage so FileExplorer also sees it
                  localStorage.setItem('explorer_custom_paths', JSON.stringify(customPaths))
                }
              }
            } catch {
              // Ignore config fetch failure
            }
          }

          // Combine and filter redundant paths
          const combined = [...customPaths, ...projectFolders]
          const filtered = filterRedundantPaths(combined)
          setFolders(filtered)

          // Auto-expand first level folders
          const firstLevelPaths = new Set(filtered.map(folder => folder.path))
          setExpandedFolders(firstLevelPaths)

          // Load contents for all first-level folders
          for (const folder of filtered) {
            if (folder.type === 'folder' && (!folder.children || folder.children.length === 0)) {
              loadFolderContentsInitial(folder.path, filtered)
            }
          }
        }

        // Fetch web pages
        const webRes = await fetch('/api/web-pages')
        if (webRes.ok) setWebPages(await webRes.json())

        // Fetch terminals
        const terminalsRes = await fetch('/api/terminals')
        if (terminalsRes.ok) setTerminals(await terminalsRes.json())

        // Fetch history
        const historyRes = await fetch('/api/tab-history')
        if (historyRes.ok) setHistory(await historyRes.json())
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      }
    }

    fetchData()

    // Fetch local screenshot and start polling
    fetchLocalScreenshot()
    const screenshotInterval = setInterval(fetchLocalScreenshot, 2000)

    // Fetch Hetzner instances
    fetchHetznerInstances()
    const hetznerInterval = setInterval(fetchHetznerInstances, 10000)

    return () => {
      clearInterval(screenshotInterval)
      clearInterval(hetznerInterval)
    }
  }, [fetchLocalScreenshot, fetchHetznerInstances])

  const runningTerminals = terminals.filter(t => t.status === 'running').length
  const runningInstances = hetznerInstances.filter(i => i.status === 'running').length

  const toggleFolder = async (path: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
      // Load folder contents if not already loaded
      await loadFolderContents(path)
    }
    setExpandedFolders(newExpanded)
  }

  const loadFolderContents = async (path: string) => {
    try {
      const isAbsolutePath = path.startsWith('/')
      const apiPath = isAbsolutePath
        ? `/api/browse/folder?path=${encodeURIComponent(path)}`
        : `/api/dashboard/folder?path=${encodeURIComponent(path)}`

      const response = await fetch(apiPath)
      if (!response.ok) return

      const data = await response.json()

      // Update the folder tree with loaded children
      const updateTreeNode = (nodes: FileNode[]): FileNode[] => {
        return nodes.map(node => {
          if (node.path === path) {
            const children: FileNode[] = [
              ...data.folders.map((folder: { name: string; path: string }) => ({
                name: folder.name,
                path: folder.path,
                type: 'folder' as const,
                children: []
              })),
              ...data.files.map((file: { name: string }) => ({
                name: file.name,
                path: `${path}/${file.name}`,
                type: 'file' as const
              }))
            ]
            return { ...node, children }
          } else if (node.children && node.children.length > 0) {
            return { ...node, children: updateTreeNode(node.children) }
          }
          return node
        })
      }

      setFolders(updateTreeNode(folders))
    } catch (error) {
      console.error('Failed to load folder contents:', error)
    }
  }

  // Hetzner actions
  const handleCreateInstance = async () => {
    setIsCreatingInstance(true)
    try {
      const response = await fetch('/api/hetzner/instances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `agent-sdk-${Date.now()}`,
          server_type: 'cx22',
          from_snapshot: true
        })
      })
      if (response.ok) {
        fetchHetznerInstances()
      } else {
        const err = await response.json()
        alert(err.detail || 'Failed to create instance')
      }
    } catch (err) {
      console.error('Failed to create instance:', err)
      alert('Failed to create instance')
    } finally {
      setIsCreatingInstance(false)
    }
  }

  const handleStopInstance = async (id: number) => {
    setActionLoading(id)
    try {
      await fetch(`/api/hetzner/instances/${id}/stop`, { method: 'POST' })
      fetchHetznerInstances()
    } finally {
      setActionLoading(null)
      setActiveMenu(null)
    }
  }

  const handleStartInstance = async (id: number) => {
    setActionLoading(id)
    try {
      await fetch(`/api/hetzner/instances/${id}/start`, { method: 'POST' })
      fetchHetznerInstances()
    } finally {
      setActionLoading(null)
      setActiveMenu(null)
    }
  }

  const handleDeleteInstance = async (id: number, name: string) => {
    if (!confirm(`Delete instance "${name}"? This cannot be undone.`)) return
    setActionLoading(id)
    try {
      await fetch(`/api/hetzner/instances/${id}`, { method: 'DELETE' })
      fetchHetznerInstances()
    } finally {
      setActionLoading(null)
      setActiveMenu(null)
    }
  }

  const renderFolder = (folder: FileNode, level: number = 0) => {
    const isExpanded = expandedFolders.has(folder.path)
    const hasChildren = folder.children && folder.children.length > 0

    return (
      <div key={folder.path} className="folder-tree-item">
        <div
          className="folder-item"
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => onOpenResource?.('files', folder.path)}
        >
          {folder.type === 'folder' && (
            <span className="folder-chevron" onClick={(e) => toggleFolder(folder.path, e)}>
              {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </span>
          )}
          {folder.type === 'folder' ? (
            isExpanded ? <FolderOpen size={16} /> : <Folder size={16} />
          ) : null}
          <span className="folder-name">{folder.name}</span>
        </div>
        {isExpanded && hasChildren && (
          <div className="folder-children">
            {folder.children!.map(child => renderFolder(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="dashboard-content">
        {/* FOLDERS Section */}
        <section className="dashboard-section">
          <div className="section-header">
            <Folder size={16} />
            <h2>FOLDERS</h2>
          </div>
          <div className="resource-grid folder-tree">
            {folders.length > 0 ? (
              <>
                {folders.map((folder) => renderFolder(folder))}
                <div className="resource-card new-resource">
                  <Plus size={20} />
                  <span>New File/Folder</span>
                </div>
              </>
            ) : (
              <div className="resource-card new-resource">
                <Plus size={20} />
                <span>New File/Folder</span>
              </div>
            )}
          </div>
        </section>

        {/* WEB PAGES Section */}
        <section className="dashboard-section">
          <div className="section-header">
            <Globe size={16} />
            <h2>WEB PAGES</h2>
            {webPages.length > 0 && <span className="badge">{webPages.length} Active</span>}
          </div>
          <div className="resource-grid">
            {webPages.map((page) => (
              <div key={page.id} className="resource-card" onClick={() => onOpenResource?.('web', page.id)}>
                <div className="card-icon">
                  <span>{page.icon || '🌐'}</span>
                </div>
                <div className="card-info">
                  <div className="card-title">{page.title}</div>
                  <div className="card-subtitle">{page.url}</div>
                </div>
                <button className="card-close" data-tooltip="Remove from recent" aria-label="Remove from recent">×</button>
              </div>
            ))}
            <div className="resource-card new-resource dashed">
              <Plus size={20} />
              <span>New Website</span>
            </div>
          </div>
        </section>

        {/* COMPUTERS Section - All inline */}
        <section className="dashboard-section computers-section">
          <div className="section-header">
            <Monitor size={16} />
            <h2>COMPUTERS</h2>
            {runningInstances > 0 && <span className="badge running">{runningInstances + 1} Active</span>}
          </div>

          <div className="computers-grid">
            {/* This Computer - with live preview */}
            <div
              className="computer-card local-computer"
              onClick={() => onOpenResource?.('computer', 'local')}
            >
              <div className="computer-card-header">
                <div className="computer-card-info">
                  <Monitor size={16} />
                  <span className="computer-card-name">This Computer</span>
                </div>
                <span className="status-badge running">Active</span>
              </div>
              <div
                className="computer-card-preview"
                style={localScreenshot ? {
                  backgroundImage: `url(data:image/png;base64,${localScreenshot})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center'
                } : undefined}
              >
                {!localScreenshot && (
                  <div className="preview-placeholder">
                    <RefreshCw size={20} className="spinning" />
                  </div>
                )}
              </div>
            </div>

            {/* Hetzner Cloud Instances */}
            {hetznerInstances.map(instance => {
              const isRunning = instance.status === 'running'
              const isStopped = instance.status === 'off' || instance.status === 'stopped'

              return (
                <div
                  key={instance.id}
                  className={`computer-card cloud-computer ${instance.status}`}
                  onClick={() => isRunning && onOpenResource?.('computer', `hetzner-${instance.id}`)}
                >
                  <div className="computer-card-header">
                    <div className="computer-card-info">
                      <Cloud size={16} />
                      <span className="computer-card-name">{instance.name}</span>
                    </div>
                    <div className="computer-card-actions">
                      <span className={`status-badge ${instance.status}`}>
                        {isRunning ? 'Running' : isStopped ? 'Stopped' : instance.status}
                      </span>
                      {isRunning && (
                        <div className="menu-container" ref={activeMenu === `instance-${instance.id}` ? menuRef : null}>
                          <button
                            type="button"
                            className="menu-btn"
                            data-tooltip="Instance actions"
                            aria-label="Instance actions"
                            onClick={(e) => {
                              e.stopPropagation()
                              setActiveMenu(activeMenu === `instance-${instance.id}` ? null : `instance-${instance.id}`)
                            }}
                          >
                            <MoreVertical size={16} />
                          </button>
                          {activeMenu === `instance-${instance.id}` && (
                            <div className="dropdown-menu" onClick={(e) => e.stopPropagation()}>
                              <button
                                type="button"
                                onClick={() => handleStopInstance(instance.id)}
                                disabled={actionLoading === instance.id}
                                aria-label="Pause instance"
                              >
                                <Pause size={14} /> Pause
                              </button>
                              <button
                                type="button"
                                className="delete-action"
                                onClick={() => handleDeleteInstance(instance.id, instance.name)}
                                disabled={actionLoading === instance.id}
                                aria-label="Delete instance"
                              >
                                <Trash2 size={14} /> Delete
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="computer-card-preview">
                    {isRunning ? (
                      <div className="preview-placeholder clickable">
                        <Monitor size={32} opacity={0.4} />
                        <span>Click to connect</span>
                      </div>
                    ) : (
                      <div className="preview-placeholder offline">
                        <Monitor size={32} opacity={0.2} />
                        <span>Offline</span>
                      </div>
                    )}
                  </div>
                  <div className="computer-card-footer">
                    <span className="instance-ip">{instance.public_net?.ipv4?.ip || 'No IP'}</span>
                    <span className="instance-type">{instance.server_type?.name || 'Unknown'}</span>
                  </div>
                  {/* Action buttons for stopped instances */}
                  {isStopped && (
                    <div className="computer-card-stopped-actions" onClick={(e) => e.stopPropagation()}>
                      <button
                        type="button"
                        className="action-btn resume"
                        onClick={() => handleStartInstance(instance.id)}
                        disabled={actionLoading === instance.id}
                        aria-label="Start instance"
                      >
                        <Power size={14} /> {actionLoading === instance.id ? 'Starting...' : 'Resume'}
                      </button>
                      <button
                        type="button"
                        className="action-btn delete"
                        onClick={() => handleDeleteInstance(instance.id, instance.name)}
                        disabled={actionLoading === instance.id}
                        aria-label="Delete instance"
                      >
                        <Trash2 size={14} /> Delete
                      </button>
                    </div>
                  )}
                </div>
              )
            })}

            {/* New Instance Button */}
            <div
              className={`computer-card new-computer ${isCreatingInstance ? 'creating' : ''}`}
              onClick={!isCreatingInstance ? handleCreateInstance : undefined}
            >
              <div className="new-computer-content">
                {isCreatingInstance ? (
                  <>
                    <RefreshCw size={20} className="spinning" />
                    <span>Creating...</span>
                  </>
                ) : (
                  <>
                    <Plus size={20} />
                    <span>New Cloud Instance</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* TERMINALS Section */}
        <section className="dashboard-section">
          <div className="section-header">
            <Terminal size={16} />
            <h2>TERMINALS</h2>
            {runningTerminals > 0 && <span className="badge running">{runningTerminals} Running</span>}
          </div>
          <div className="resource-grid">
            {terminals.map((terminal) => (
              <div key={terminal.id} className="resource-card terminal-card" onClick={() => onOpenResource?.('terminal', terminal.id)}>
                <div className={`card-indicator ${terminal.status}`}></div>
                <div className="card-info">
                  <div className="card-title">{terminal.title}</div>
                  <div className="terminal-preview">
                    {terminal.preview}
                  </div>
                </div>
                <button className="card-external" data-tooltip="Open in new window" aria-label="Open in new window">⧉</button>
              </div>
            ))}
            <div className="resource-card new-resource">
              <Plus size={20} />
              <span>New Terminal</span>
            </div>
          </div>
        </section>

        {/* TAB HISTORY */}
        <section className="dashboard-section full-width">
          <div className="section-header">
            <span>🕐</span>
            <h2>TAB HISTORY</h2>
            <a href="#" className="view-all">View Full History</a>
          </div>
          <div className="history-list">
            {history.length > 0 ? (
              history.map((item) => (
                <div key={item.id} className="history-item">
                  <div className="history-icon">{item.icon || '📄'}</div>
                  <div className="history-info">
                    <div className="history-title">{item.title}</div>
                    <div className="history-subtitle">{item.subtitle}</div>
                  </div>
                  <div className="history-time">{item.time}</div>
                </div>
              ))
            ) : (
              <div className="no-history-message">
                No history yet
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}

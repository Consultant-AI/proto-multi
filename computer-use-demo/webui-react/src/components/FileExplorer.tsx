import { useState, useEffect, useRef } from 'react'
import { Folder, FolderOpen, File, FileText, FileCode, Plus, X } from 'lucide-react'
import { FileNode, Project } from '../types'
import '../styles/FileExplorer.css'

interface FileExplorerProps {
  onSelectPath: (path: string) => void
  selectedPath: string | null
  onToggleVisible?: () => void
  refreshKey?: number
}

export default function FileExplorer({ onSelectPath, selectedPath, onToggleVisible, refreshKey }: FileExplorerProps) {
  const [, setProjects] = useState<Project[]>([])
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
  const [fileTree, setFileTree] = useState<FileNode[]>([])
  const [loading, setLoading] = useState(true)
  const [customPaths, setCustomPaths] = useState<FileNode[]>([])
  const [isPicking, setIsPicking] = useState(false)
  const [openMenu, setOpenMenu] = useState<string | null>(null)

  // Refs to access current state without triggering re-renders
  const customPathsRef = useRef<FileNode[]>([])
  const fileTreeRef = useRef<FileNode[]>([])
  const expandedFoldersRef = useRef<Set<string>>(new Set())
  const lastExpandedPathRef = useRef<string | null>(null)

  // Keep refs in sync with state
  useEffect(() => { customPathsRef.current = customPaths }, [customPaths])
  useEffect(() => { fileTreeRef.current = fileTree }, [fileTree])
  useEffect(() => { expandedFoldersRef.current = expandedFolders }, [expandedFolders])

  // Helper to filter out paths that are already contained within another path in the list
  const filterRedundantPaths = (nodes: FileNode[]): FileNode[] => {
    return nodes.filter(node => {
      // Check if any OTHER node is a parent of this node
      return !nodes.some(otherNode => {
        if (otherNode.path === node.path) return false
        // A path is a parent if the test path starts with the other path + /
        // or if they are the same (already handled above)
        return node.path.startsWith(otherNode.path + '/')
      })
    })
  }

  useEffect(() => {
    loadProjects()
    loadFileTree()
    // Load custom paths from localStorage
    const saved = localStorage.getItem('explorer_custom_paths')
    if (saved) {
      try {
        setCustomPaths(JSON.parse(saved))
      } catch {
        // Invalid JSON, ignore
      }
    }
  }, [])

  // Function to expand folders to reveal a path
  const expandToPath = async (targetPath: string) => {
    // Use refs to get current state without triggering re-renders
    const currentCustomPaths = customPathsRef.current
    const currentFileTree = fileTreeRef.current

    // Wait for data to be loaded
    if (currentCustomPaths.length === 0 && currentFileTree.length === 0) return false

    // Find all root folders that could contain this path
    const allRoots = [...currentCustomPaths, ...currentFileTree]

    // Find the root that contains this path
    const matchingRoot = allRoots.find(root =>
      targetPath === root.path || targetPath.startsWith(root.path + '/')
    )

    if (!matchingRoot) return false

    // Build list of all paths that need to be expanded
    const pathsToExpand: string[] = []

    // If it's the root itself, just expand it
    if (targetPath === matchingRoot.path) {
      if (matchingRoot.type === 'folder') {
        pathsToExpand.push(matchingRoot.path)
      }
    } else {
      // Get the relative path from root
      const relativePath = targetPath.slice(matchingRoot.path.length + 1)
      const parts = relativePath.split('/')

      // Start from root and add each parent folder
      let currentPath = matchingRoot.path
      pathsToExpand.push(currentPath)

      // Add all parent folders (not the file itself if it's a file)
      for (let i = 0; i < parts.length - 1; i++) {
        currentPath = currentPath + '/' + parts[i]
        pathsToExpand.push(currentPath)
      }

      // If the selected path is a folder, also expand it
      const lastPart = parts[parts.length - 1]
      if (lastPart && !lastPart.includes('.')) {
        // Likely a folder (no extension)
        pathsToExpand.push(targetPath)
      }
    }

    // Load folder contents for each path that needs expanding
    for (const path of pathsToExpand) {
      await loadFolderContentsForPath(path)
    }

    // Update expanded folders state
    setExpandedFolders(prev => {
      const newExpanded = new Set(prev)
      for (const path of pathsToExpand) {
        newExpanded.add(path)
      }
      return newExpanded
    })

    return true
  }

  // Auto-expand folders to reveal the selected path
  useEffect(() => {
    if (!selectedPath) return
    // Skip if we already expanded for this path
    if (lastExpandedPathRef.current === selectedPath) return

    const tryExpand = async () => {
      const success = await expandToPath(selectedPath)
      if (success) {
        lastExpandedPathRef.current = selectedPath
      }
    }

    tryExpand()
  }, [selectedPath])

  // Retry expansion when data loads (in case selectedPath was set before data was ready)
  useEffect(() => {
    if (!selectedPath) return
    if (lastExpandedPathRef.current === selectedPath) return
    if (customPaths.length === 0 && fileTree.length === 0) return

    const tryExpand = async () => {
      const success = await expandToPath(selectedPath)
      if (success) {
        lastExpandedPathRef.current = selectedPath
      }
    }

    tryExpand()
  }, [customPaths.length, fileTree.length, selectedPath])

  // Handle external refresh trigger
  useEffect(() => {
    if (refreshKey === undefined || refreshKey === 0) return

    const doRefresh = async () => {
      // Capture the current expanded folders before refresh
      const currentExpanded = Array.from(expandedFoldersRef.current)

      setLoading(true)
      await loadProjects()
      await loadFileTree()

      // Only reload contents of folders that were already expanded (using ref to get current value)
      for (const expandedPath of currentExpanded) {
        await loadFolderContentsForPath(expandedPath)
      }
      setLoading(false)
    }

    doRefresh()
  }, [refreshKey])

  const loadProjects = async () => {
    try {
      const response = await fetch('/api/dashboard/projects')
      const data = await response.json()
      setProjects(data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }

  const loadFileTree = async () => {
    setLoading(true)
    try {
      // Build file tree from projects - show directly without .proto/planning wrapper
      const response = await fetch('/api/dashboard/projects')
      const projects = await response.json()

      const tree: FileNode[] = projects.map((project: Project) => ({
        name: project.name,
        path: project.path,
        type: 'folder',
        children: [] // Will be loaded on expansion
      }))

      setFileTree(tree)
    } catch (error) {
      console.error('Failed to load file tree:', error)
    } finally {
      setLoading(false)
    }
  }

  // Load default path on startup
  useEffect(() => {
    // Check if we should add the default path (only if customPaths is empty or explicitly requested)
    const initDefaultPath = async () => {
      let defaultPath: string | null = null

      try {
        // Try config endpoint first
        const response = await fetch('/api/dashboard/config')
        if (response.ok) {
          const config = await response.json()
          defaultPath = config.defaultProjectPath
        }
      } catch (e) {
        // Ignore config failure
      }

      // Config endpoint should always return the default path
      if (!defaultPath) return

      // Check if already in customPaths (re-read from storage to be safe)
      const saved = localStorage.getItem('explorer_custom_paths')
      let currentPaths: FileNode[] = []
      if (saved) {
        try {
          currentPaths = JSON.parse(saved)
        } catch { }
      }

      // Migration: Remove old ~/Proto entries (they were moved to projects/)
      const oldProtoPattern = /\/Proto$/
      const hadOldEntries = currentPaths.some(p => oldProtoPattern.test(p.path))
      if (hadOldEntries) {
        currentPaths = currentPaths.filter(p => !oldProtoPattern.test(p.path))
        localStorage.setItem('explorer_custom_paths', JSON.stringify(currentPaths))
      }

      // If default path is not in the list, add it
      const exists = currentPaths.some(p => p.path === defaultPath)

      // Also check if we already have it in state (to avoid double render issues)
      if (!exists) {
        const newNode: FileNode = {
          name: 'Projects', // Friendly name
          path: defaultPath,
          type: 'folder',
          children: []
        }

        const updatedPaths = [newNode, ...currentPaths]
        setCustomPaths(updatedPaths)
        localStorage.setItem('explorer_custom_paths', JSON.stringify(updatedPaths))
      }
    }

    initDefaultPath()
  }, []) // Empty dependency array - run once on mount

  const handlePickFolder = async () => {
    if (isPicking) return
    setIsPicking(true)

    try {
      const response = await fetch('/api/browse/pick-folder', { method: 'POST' })
      const data = await response.json()

      if (data.cancelled || !data.path) {
        setIsPicking(false)
        return
      }

      const path = data.path
      const pathType = data.type || 'folder'

      // Check if path already exists
      const exists = customPaths.some(p => p.path === path) || fileTree.some(p => p.path === path)
      if (exists) {
        setIsPicking(false)
        onSelectPath(path)
        return
      }

      const name = path.split('/').pop() || path

      const newNode: FileNode = {
        name,
        path,
        type: pathType,
        children: pathType === 'folder' ? [] : undefined
      }

      const updatedCustomPaths = [...customPaths, newNode]
      setCustomPaths(updatedCustomPaths)
      localStorage.setItem('explorer_custom_paths', JSON.stringify(updatedCustomPaths))

      onSelectPath(path)
    } catch (error) {
      console.error('Failed to pick folder:', error)
    } finally {
      setIsPicking(false)
    }
  }

  const handleRemoveCustomPath = (pathToRemove: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const updatedCustomPaths = customPaths.filter(p => p.path !== pathToRemove)
    setCustomPaths(updatedCustomPaths)
    localStorage.setItem('explorer_custom_paths', JSON.stringify(updatedCustomPaths))
    setOpenMenu(null)
  }

  const handleOpenInOS = async (path: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setOpenMenu(null)
    try {
      await fetch('/api/open-in-finder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
      })
    } catch (error) {
      console.error('Failed to open in OS:', error)
    }
  }

  const handleMenuClick = (path: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setOpenMenu(openMenu === path ? null : path)
  }

  const toggleFolder = async (path: string) => {
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

  // Load folder contents - uses functional updates to avoid stale closures
  const loadFolderContentsForPath = async (path: string) => {
    try {
      // Use browse API for absolute paths
      const isAbsolutePath = path.startsWith('/')
      const apiPath = isAbsolutePath
        ? `/api/browse/folder?path=${encodeURIComponent(path)}`
        : `/api/dashboard/folder?path=${encodeURIComponent(path)}`

      const response = await fetch(apiPath)
      if (!response.ok) return

      const data = await response.json()

      // Update the file tree with the loaded children
      const updateTreeNode = (nodes: FileNode[]): FileNode[] => {
        return nodes.map(node => {
          if (node.path === path) {
            // Found the node - update its children
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
            // Recursively search in children
            return { ...node, children: updateTreeNode(node.children) }
          }
          return node
        })
      }

      // Use functional updates to avoid stale closures
      setFileTree(prev => updateTreeNode(prev))
      setCustomPaths(prev => updateTreeNode(prev))
    } catch (error) {
      console.error('Failed to load folder contents:', error)
    }
  }

  const loadFolderContents = async (path: string) => {
    await loadFolderContentsForPath(path)
  }

  const renderFileNode = (node: FileNode, level: number = 0, isCustom: boolean = false) => {
    const isExpanded = expandedFolders.has(node.path)
    const isSelected = selectedPath === node.path
    const isMenuOpen = openMenu === node.path

    return (
      <div key={node.path} className="file-node">
        <div
          className={`file-node-label ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => {
            console.log('[FileExplorer] clicked:', node.type, node.path)
            if (node.type === 'folder') {
              toggleFolder(node.path)
            }
            onSelectPath(node.path)
          }}
        >
          <span className="file-node-icon">
            {node.type === 'folder' ? (
              isExpanded ? <FolderOpen size={16} /> : <Folder size={16} />
            ) : (
              getFileIcon(node.name)
            )}
          </span>
          <span className="file-node-name">{node.name}</span>
          {node.type === 'folder' && node.children && node.children.length > 0 && (
            <span className="file-node-count">({node.children.length})</span>
          )}
          {level === 0 && (
            <div className="file-node-menu">
              <button
                className="menu-dots-btn"
                onClick={(e) => handleMenuClick(node.path, e)}
                data-tooltip="More options"
                aria-label="More options"
              >
                ...
              </button>
              {isMenuOpen && (
                <div className="file-node-dropdown">
                  <button onClick={(e) => handleOpenInOS(node.path, e)}>
                    Open
                  </button>
                  {isCustom && (
                    <button onClick={(e) => handleRemoveCustomPath(node.path, e)}>
                      Remove from Proto
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        {node.type === 'folder' && isExpanded && node.children && (
          <div className="file-node-children">
            {node.children.map(child => renderFileNode(child, level + 1, isCustom))}
          </div>
        )}
      </div>
    )
  }

  const getFileIcon = (filename: string) => {
    if (filename.endsWith('.json')) return <File size={16} />
    if (filename.endsWith('.md')) return <FileText size={16} />
    if (filename.endsWith('.py')) return <FileCode size={16} />
    if (filename.endsWith('.ts') || filename.endsWith('.tsx')) return <FileCode size={16} />
    if (filename.endsWith('.js') || filename.endsWith('.jsx')) return <FileCode size={16} />
    return <File size={16} />
  }

  return (
    <div className="file-explorer">
      <div className="file-explorer-header">
        <h2>Explorer</h2>
        {onToggleVisible && (
          <button
            className="close-explorer-btn"
            onClick={onToggleVisible}
            data-tooltip="Close Explorer"
            aria-label="Close Explorer"
          >
            <X size={16} />
          </button>
        )}
      </div>

      <div className="file-explorer-content">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <div className="file-tree">
            {/* Combined list - all items together, filtered for redundancy */}
            {(() => {
              const combined = [...customPaths, ...fileTree]
              const filtered = filterRedundantPaths(combined)

              if (filtered.length > 0) {
                return filtered.map(node => renderFileNode(node, 0, customPaths.some(c => c.path === node.path)))
              }

              return (
                <div className="empty-explorer">
                  <p>No folders to display</p>
                  <button onClick={handlePickFolder} disabled={isPicking} aria-label="Add a folder or file">
                    {isPicking ? 'Opening...' : 'Add a folder'}
                  </button>
                </div>
              )
            })()}

            {/* Add button at the bottom */}
            {([...customPaths, ...fileTree].length > 0) && (
              <div className="add-buttons-section">
                <button
                  className="add-bottom-btn"
                  onClick={handlePickFolder}
                  disabled={isPicking}
                  aria-label="Add a folder or file"
                >
                  <Plus size={16} style={{ marginRight: '6px', display: 'inline-block', verticalAlign: 'middle' }} /> Add Folder / File
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

import { useState, useEffect, useRef, memo } from 'react'
import { Folder, FolderOpen, File, FileText, FileCode, Plus, X, ChevronRight, ChevronDown } from 'lucide-react'
import { FileNode, Project } from '../types'
import '../styles/FileExplorer.css'

interface FileExplorerProps {
  onSelectPath: (path: string) => void
  selectedPath: string | null
  onToggleVisible?: () => void
  refreshKey?: number
}

const EXPANDED_FOLDERS_KEY = 'explorer_expanded_folders'

// Module-level persistent storage for expanded folders
// This survives component remounts and re-renders
let persistentExpandedFolders: Set<string> | null = null

// Load expanded folders from localStorage (only once)
const loadExpandedFolders = (): Set<string> => {
  if (persistentExpandedFolders !== null) {
    return persistentExpandedFolders
  }
  try {
    const saved = localStorage.getItem(EXPANDED_FOLDERS_KEY)
    if (saved) {
      persistentExpandedFolders = new Set(JSON.parse(saved))
      return persistentExpandedFolders
    }
  } catch { }
  persistentExpandedFolders = new Set()
  return persistentExpandedFolders
}

// Save expanded folders to localStorage and update persistent storage
const saveExpandedFolders = (folders: Set<string>) => {
  persistentExpandedFolders = folders
  try {
    localStorage.setItem(EXPANDED_FOLDERS_KEY, JSON.stringify(Array.from(folders)))
  } catch { }
}

function FileExplorer({ onSelectPath, selectedPath, onToggleVisible, refreshKey }: FileExplorerProps) {
  const [, setProjects] = useState<Project[]>([])
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(() => loadExpandedFolders())
  const [fileTree, setFileTree] = useState<FileNode[]>([])
  const [loading, setLoading] = useState(true)
  const [customPaths, setCustomPaths] = useState<FileNode[]>([])
  const [isPicking, setIsPicking] = useState(false)
  const [openMenu, setOpenMenu] = useState<string | null>(null)

  // Refs to access current state without triggering re-renders
  const customPathsRef = useRef<FileNode[]>([])
  const fileTreeRef = useRef<FileNode[]>([])
  const expandedFoldersRef = useRef<Set<string>>(new Set())

  // Keep refs in sync with state (but DON'T save to persistent storage here - that's done in toggleFolder/expandToPath)
  useEffect(() => { customPathsRef.current = customPaths }, [customPaths])
  useEffect(() => { fileTreeRef.current = fileTree }, [fileTree])
  useEffect(() => {
    expandedFoldersRef.current = expandedFolders
    // Don't call saveExpandedFolders here - it would overwrite persistent storage with potentially stale state
  }, [expandedFolders])

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

    // Clear expanded folders on page load - folders should start collapsed
    // User can expand them again as needed
    persistentExpandedFolders = new Set()
    saveExpandedFolders(persistentExpandedFolders)
    setExpandedFolders(new Set())

    // Load custom paths from localStorage (but clear children to prevent auto-expansion)
    const saved = localStorage.getItem('explorer_custom_paths')
    if (saved) {
      try {
        const parsed = JSON.parse(saved) as FileNode[]
        // Clear children to ensure folders start collapsed on page refresh
        const withoutChildren = parsed.map((node: FileNode) => ({
          ...node,
          children: node.type === 'folder' ? [] : undefined
        }))
        setCustomPaths(withoutChildren)
      } catch {
        // Invalid JSON, ignore
      }
    }
  }, [])

  // Expand parent folders to reveal a path (for address bar navigation)
  // Only ADDS to expanded set, never removes - so it won't interfere with toggleFolder
  const expandToPath = async (targetPath: string) => {
    const currentCustomPaths = customPathsRef.current
    const currentFileTree = fileTreeRef.current
    if (currentCustomPaths.length === 0 && currentFileTree.length === 0) return false

    const allRoots = [...currentCustomPaths, ...currentFileTree]
    const matchingRoot = allRoots.find(root =>
      targetPath === root.path || targetPath.startsWith(root.path + '/')
    )
    if (!matchingRoot) return false

    const pathsToExpand: string[] = []

    if (targetPath === matchingRoot.path) {
      // Target is the root itself - expand it if it's a folder
      if (matchingRoot.type === 'folder') pathsToExpand.push(matchingRoot.path)
    } else {
      // Target is inside the root - expand all parent folders
      const relativePath = targetPath.slice(matchingRoot.path.length + 1)
      const parts = relativePath.split('/')
      let currentPath = matchingRoot.path
      pathsToExpand.push(currentPath)

      // Add all parent folders
      for (let i = 0; i < parts.length - 1; i++) {
        currentPath = currentPath + '/' + parts[i]
        pathsToExpand.push(currentPath)
      }

      // If target is a folder, expand it too
      const lastPart = parts[parts.length - 1]
      if (lastPart && !lastPart.includes('.')) {
        pathsToExpand.push(targetPath)
      }
    }

    // Load folder contents for each path
    for (const path of pathsToExpand) {
      await loadFolderContentsForPath(path)
    }

    // Only ADD to expanded set (never remove) - this prevents interfering with toggleFolder
    const currentPersistent = persistentExpandedFolders || new Set<string>()
    const newExpanded = new Set(currentPersistent)
    for (const path of pathsToExpand) {
      newExpanded.add(path)
    }
    saveExpandedFolders(newExpanded)
    setExpandedFolders(newExpanded)

    return true
  }

  // Track if path change came from clicking in explorer (internal) vs address bar (external)
  const internalClickRef = useRef(false)
  const lastExpandedPathRef = useRef<string | null>(null)

  // Auto-expand parent folders ONLY for external path changes (address bar, not explorer clicks)
  useEffect(() => {
    if (!selectedPath) return
    if (lastExpandedPathRef.current === selectedPath) return

    // Skip if this was an internal click - toggleFolder already handled it
    if (internalClickRef.current) {
      internalClickRef.current = false
      lastExpandedPathRef.current = selectedPath
      return
    }

    // If data not loaded yet, poll until it is (max 2 seconds)
    let attempts = 0
    const maxAttempts = 20

    const tryExpand = async () => {
      if (customPathsRef.current.length === 0 && fileTreeRef.current.length === 0) {
        // Data not ready, try again in 100ms
        attempts++
        if (attempts < maxAttempts) {
          setTimeout(tryExpand, 100)
        }
        return
      }

      const success = await expandToPath(selectedPath)
      if (success) {
        lastExpandedPathRef.current = selectedPath
      }
    }

    tryExpand()
  }, [selectedPath])

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

  // Toggle folder expand/collapse - only affects the clicked folder, never others
  // isVisuallyExpanded: true if children are currently visible on screen
  const toggleFolder = (path: string, isVisuallyExpanded: boolean) => {
    // Use persistent storage as the source of truth
    const currentExpanded = persistentExpandedFolders || new Set<string>()

    // Create new set
    const newExpanded = new Set(currentExpanded)

    if (isVisuallyExpanded) {
      // Folder is visually expanded (children visible) - collapse it
      newExpanded.delete(path)
    } else {
      // Folder is not visually expanded - expand it and load children
      newExpanded.add(path)
      loadFolderContents(path)
    }

    // Update persistent storage FIRST
    saveExpandedFolders(newExpanded)

    // Then update React state
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
    // Use React state for rendering (triggers re-renders when it changes)
    // Only consider expanded if children are actually loaded and visible
    const hasVisibleChildren = !!(node.children && node.children.length > 0)
    const isExpanded = expandedFolders.has(node.path) && hasVisibleChildren
    const isSelected = selectedPath === node.path
    const isMenuOpen = openMenu === node.path

    return (
      <div key={node.path} className="file-node">
        <div
          className={`file-node-label ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => {
            // Mark this as an internal click so expandToPath doesn't run
            internalClickRef.current = true
            if (node.type === 'folder') {
              toggleFolder(node.path, isExpanded)
            }
            onSelectPath(node.path)
          }}
        >
          {node.type === 'folder' ? (
            <span
              className="file-node-chevron"
              onClick={(e) => {
                e.stopPropagation()
                internalClickRef.current = true
                toggleFolder(node.path, isExpanded)
              }}
            >
              {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </span>
          ) : (
            <span className="file-node-chevron-spacer" />
          )}
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

export default memo(FileExplorer)

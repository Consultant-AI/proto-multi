import { useState, useEffect } from 'react'
import { FileNode, Project } from '../types'
import '../styles/FileExplorer.css'

interface FileExplorerProps {
  onSelectPath: (path: string) => void
  selectedPath: string | null
}

export default function FileExplorer({ onSelectPath, selectedPath }: FileExplorerProps) {
  const [, setProjects] = useState<Project[]>([])
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
  const [fileTree, setFileTree] = useState<FileNode[]>([])
  const [loading, setLoading] = useState(true)
  const [customPaths, setCustomPaths] = useState<FileNode[]>([])
  const [isPicking, setIsPicking] = useState(false)
  const [openMenu, setOpenMenu] = useState<string | null>(null)

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
      const pathType = data.type || 'folder' // Default to folder for backward compatibility

      // Check if path already exists
      const exists = customPaths.some(p => p.path === path) || fileTree.some(p => p.path === path)
      if (exists) {
        setIsPicking(false)
        onSelectPath(path)
        return
      }

      // Get the name from the path
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

      // Auto-select the new path
      onSelectPath(path)
    } catch (error) {
      console.error('Failed to pick folder:', error)
    } finally {
      setIsPicking(false)
    }
  }

  const handlePickFile = async () => {
    if (isPicking) return
    setIsPicking(true)

    try {
      const response = await fetch('/api/browse/pick-file', { method: 'POST' })
      const data = await response.json()

      if (data.cancelled || !data.path) {
        setIsPicking(false)
        return
      }

      const path = data.path

      // Check if path already exists
      const exists = customPaths.some(p => p.path === path)
      if (exists) {
        setIsPicking(false)
        onSelectPath(path)
        return
      }

      // Get the file name from the path
      const name = path.split('/').pop() || path

      const newNode: FileNode = {
        name,
        path,
        type: 'file',
        children: undefined
      }

      const updatedCustomPaths = [...customPaths, newNode]
      setCustomPaths(updatedCustomPaths)
      localStorage.setItem('explorer_custom_paths', JSON.stringify(updatedCustomPaths))

      // Auto-select the new path
      onSelectPath(path)
    } catch (error) {
      console.error('Failed to pick file:', error)
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

  const loadFolderContents = async (path: string) => {
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

      setFileTree(updateTreeNode(fileTree))
      setCustomPaths(updateTreeNode(customPaths))
    } catch (error) {
      console.error('Failed to load folder contents:', error)
    }
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
            if (node.type === 'folder') {
              toggleFolder(node.path)
            }
            onSelectPath(node.path)
          }}
        >
          <span className="file-node-icon">
            {node.type === 'folder' ? (
              isExpanded ? '📂' : '📁'
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
                title="More options"
              >
                ...
              </button>
              {isMenuOpen && (
                <div className="file-node-dropdown">
                  <button onClick={(e) => handleOpenInOS(node.path, e)}>
                    {node.type === 'folder' ? 'Open in Finder' : 'Open with Default App'}
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
    if (filename.endsWith('.json')) return '📄'
    if (filename.endsWith('.md')) return '📝'
    if (filename.endsWith('.py')) return '🐍'
    if (filename.endsWith('.ts') || filename.endsWith('.tsx')) return '📘'
    if (filename.endsWith('.js') || filename.endsWith('.jsx')) return '📙'
    return '📄'
  }

  return (
    <div className="file-explorer">
      <div className="file-explorer-header">
        <h2>Explorer</h2>
        <div className="header-buttons">
          <button
            className="add-path-btn"
            onClick={handlePickFolder}
            title="Add folder"
            disabled={isPicking}
          >
            {isPicking ? '...' : '+'}
          </button>
          <button
            className="add-file-btn"
            onClick={handlePickFile}
            title="Add file"
            disabled={isPicking}
          >
            📄
          </button>
          <button
            className="refresh-btn"
            onClick={() => {
              loadProjects()
              loadFileTree()
            }}
            title="Refresh"
          >
            🔄
          </button>
        </div>
      </div>

      <div className="file-explorer-content">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <div className="file-tree">
            {/* Combined list - all items together */}
            {[...customPaths, ...fileTree].length > 0 ? (
              [...customPaths, ...fileTree].map(node => renderFileNode(node, 0, customPaths.some(c => c.path === node.path)))
            ) : (
              <div className="empty-explorer">
                <p>No folders to display</p>
                <button onClick={handlePickFolder} disabled={isPicking}>
                  {isPicking ? 'Opening...' : 'Add a folder'}
                </button>
              </div>
            )}

            {/* Add button at the bottom */}
            {([...customPaths, ...fileTree].length > 0) && (
              <div className="add-buttons-section">
                <button
                  className="add-bottom-btn"
                  onClick={handlePickFolder}
                  disabled={isPicking}
                >
                  + Add Folder / File
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

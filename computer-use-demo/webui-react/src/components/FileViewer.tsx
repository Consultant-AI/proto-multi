import { useState, useEffect } from 'react'
import { Folder, File, FileText } from 'lucide-react'
import { Task } from '../types'
import TaskViewer from './TaskViewer'
import '../styles/FileViewer.css'

interface FileViewerProps {
  selectedPath: string | null
  onPathChange?: (path: string) => void
}

interface FolderContents {
  files: Array<{ name: string; type: string; size?: number; modified?: string }>
  folders: Array<{ name: string; path: string }>
}

export default function FileViewer({ selectedPath, onPathChange }: FileViewerProps) {
  const [contents, setContents] = useState<FolderContents | null>(null)
  const [fileContent, setFileContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [taskData,] = useState<Task | null>(null)
  const [currentPath, setCurrentPath] = useState<string | null>(selectedPath)
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState<string>('')

  // Sync currentPath with selectedPath from parent
  useEffect(() => {
    setCurrentPath(selectedPath)
    setIsEditing(false) // Reset editing when path changes
  }, [selectedPath])

  useEffect(() => {
    if (!currentPath) {
      setContents(null)
      setFileContent(null)
      return
    }

    loadPathContents()
  }, [currentPath])

  const loadPathContents = async () => {
    if (!currentPath) return

    setLoading(true)
    try {
      // Check if it's a specific file by looking at the last part of the path
      const lastPart = currentPath.split('/').pop() || ''
      const isFile = lastPart.includes('.') && (
        lastPart.endsWith('.json') ||
        lastPart.endsWith('.md') ||
        lastPart.endsWith('.txt') ||
        lastPart.endsWith('.py') ||
        lastPart.endsWith('.ts') ||
        lastPart.endsWith('.tsx') ||
        lastPart.endsWith('.js') ||
        lastPart.endsWith('.jsx') ||
        lastPart.endsWith('.html') ||
        lastPart.endsWith('.css')
      )

      if (isFile) {
        await loadFileContents()
      } else {
        // It's a folder - load its contents
        await loadFolderContents()
      }
    } catch (error) {
      console.error('Failed to load path contents:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadFileContents = async () => {
    if (!currentPath) return
    // Clear folder contents when loading a file
    setContents(null)

    try {
      // Use browse API for absolute paths, dashboard API for .proto paths
      const isAbsolutePath = currentPath.startsWith('/')
      const apiPath = isAbsolutePath
        ? `/api/browse/file?path=${encodeURIComponent(currentPath)}`
        : `/api/dashboard/file?path=${encodeURIComponent(currentPath)}`

      const response = await fetch(apiPath)
      if (!response.ok) {
        const error = await response.json()
        setFileContent(`// Error loading file: ${error.detail || 'Unknown error'}`)
        return
      }

      const data = await response.json()
      setFileContent(data.content)
    } catch (error) {
      console.error('Failed to load file contents:', error)
      setFileContent('// Failed to load file contents')
    }
  }

  const loadFolderContents = async () => {
    if (!currentPath) return

    // Clear file content when loading a folder
    setFileContent(null)

    try {
      // Use browse API for absolute paths, dashboard API for .proto paths
      const isAbsolutePath = currentPath.startsWith('/')
      const apiPath = isAbsolutePath
        ? `/api/browse/folder?path=${encodeURIComponent(currentPath)}`
        : `/api/dashboard/folder?path=${encodeURIComponent(currentPath)}`

      const response = await fetch(apiPath)
      if (!response.ok) {
        const error = await response.json()
        console.error('Failed to load folder contents:', error.detail || 'Unknown error')
        return
      }

      const data = await response.json()
      setContents({
        files: data.files || [],
        folders: data.folders || []
      })
    } catch (error) {
      console.error('Failed to load folder contents:', error)
    }
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '-'
    const kb = bytes / 1024
    if (kb < 1024) return `${kb.toFixed(1)} KB`
    return `${((kb / 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString()
  }

  const navigateToPath = (newPath: string) => {
    setCurrentPath(newPath)
    if (onPathChange) {
      onPathChange(newPath)
    }
  }

  const handleFolderClick = (folderPath: string) => {
    // The browse API returns full paths, dashboard API returns relative paths
    if (folderPath.startsWith('/')) {
      navigateToPath(folderPath)
    } else {
      const fullPath = currentPath + '/' + folderPath.split('/').pop()
      navigateToPath(fullPath)
    }
  }

  const handleFileClick = (fileName: string) => {
    const fullPath = currentPath + '/' + fileName
    navigateToPath(fullPath)
  }

  const handleOpen = async () => {
    try {
      await fetch('/api/open-in-finder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: currentPath })
      })
    } catch (error) {
      console.error('Failed to open in Finder:', error)
    }
  }

  const handleEdit = () => {
    setEditedContent(fileContent || '')
    setIsEditing(true)
  }

  const handleSave = async () => {
    if (!currentPath) return
    setLoading(true)
    try {
      const response = await fetch('/api/browse/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: currentPath, content: editedContent })
      })
      if (response.ok) {
        setFileContent(editedContent)
        setIsEditing(false)
      } else {
        const error = await response.json()
        alert('Failed to save: ' + (error.detail || 'Unknown error'))
      }
    } catch (error) {
      console.error('Failed to save file:', error)
      alert('Error saving file')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
  }

  if (!currentPath) {
    return (
      <div className="file-viewer">
        <div className="file-viewer-header">
          <h2>File Viewer</h2>
        </div>
        <div className="file-viewer-content empty">
          <div className="empty-state">
            <span className="empty-icon"><Folder size={48} /></span>
            <p>Select a file or folder to view its contents</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="file-viewer">
      <div className="file-viewer-header">
        <div className="file-viewer-title">
          <h2>{currentPath.split('/').pop()}</h2>
          <div className="file-viewer-path">{currentPath}</div>
        </div>
        <div className="file-viewer-actions">
          {!isEditing && fileContent && (
            <button className="edit-btn" onClick={handleEdit}>
              Edit
            </button>
          )}
          <button className="open-btn" onClick={handleOpen} title="Open in Finder">
            Open
          </button>
        </div>
      </div>

      <div className="file-viewer-content">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : taskData ? (
          <TaskViewer task={taskData} />
        ) : fileContent ? (
          <div className="file-content">
            {isEditing ? (
              <div className="editor-container">
                <textarea
                  className="file-editor"
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  spellCheck={false}
                />
                <div className="editor-actions">
                  <button className="save-btn" onClick={handleSave} disabled={loading}>
                    {loading ? 'Saving...' : 'Save'}
                  </button>
                  <button className="cancel-btn" onClick={handleCancel} disabled={loading}>
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <pre>{fileContent}</pre>
            )}
          </div>
        ) : contents ? (
          <div className="folder-contents">
            {/* Folders */}
            {contents.folders.length > 0 && (
              <div className="folder-section">
                <h3>Folders</h3>
                <div className="items-grid">
                  {contents.folders.map(folder => (
                    <div
                      key={folder.path}
                      className="folder-item clickable"
                      onClick={() => handleFolderClick(folder.path)}
                    >
                      <div className="item-icon"><Folder size={32} /></div>
                      <div className="item-name">{folder.name}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Files */}
            {contents.files.length > 0 && (
              <div className="files-section">
                <h3>Files</h3>
                <div className="files-list">
                  {contents.files.map(file => (
                    <div
                      key={file.name}
                      className="file-item clickable"
                      onClick={() => handleFileClick(file.name)}
                    >
                      <div className="file-icon">
                        {file.type === 'json' ? <File size={24} /> : file.type === 'markdown' ? <FileText size={24} /> : <File size={24} />}
                      </div>
                      <div className="file-info">
                        <div className="file-name">{file.name}</div>
                        <div className="file-meta">
                          {formatFileSize(file.size)} • {formatDate(file.modified)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : null}
      </div>
    </div>
  )
}

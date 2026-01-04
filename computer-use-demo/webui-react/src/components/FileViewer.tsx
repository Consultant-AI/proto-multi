import { useState, useEffect, useRef } from 'react'
import { Folder, File, FileText, PanelLeft, Eye, Code } from 'lucide-react'
import { Task } from '../types'
import TaskViewer from './TaskViewer'
import '../styles/FileViewer.css'

interface FileViewerProps {
  selectedPath: string | null
  onPathChange?: (path: string) => void
  explorerVisible?: boolean
  onToggleExplorer?: () => void
  isDarkTheme?: boolean
}

interface FolderContents {
  files: Array<{ name: string; type: string; size?: number; modified?: string }>
  folders: Array<{ name: string; path: string }>
}

// File types that can be rendered in browser (v2)
const RENDERABLE_EXTENSIONS = ['.html', '.htm', '.md', '.markdown']

// Check if file can be rendered
const isRenderableFile = (path: string): boolean => {
  const lower = path.toLowerCase()
  return RENDERABLE_EXTENSIONS.some(ext => lower.endsWith(ext))
}

// Check if it's a markdown file
const isMarkdownFile = (path: string): boolean => {
  const lower = path.toLowerCase()
  return lower.endsWith('.md') || lower.endsWith('.markdown')
}

// Check if it's an HTML file
const isHtmlFile = (path: string): boolean => {
  const lower = path.toLowerCase()
  return lower.endsWith('.html') || lower.endsWith('.htm')
}

// Get theme colors
const getThemeColors = (isDark: boolean) => isDark ? {
  bg: '#0d1117',
  text: '#c9d1d9',
  heading: '#f0f6fc',
  code: '#21262d',
  link: '#58a6ff'
} : {
  bg: '#ffffff',
  text: '#1f2328',
  heading: '#1f2328',
  code: '#f6f8fa',
  link: '#0969da'
}

// Wrap HTML content with theme-aware styles
const wrapHtmlWithTheme = (html: string, isDark: boolean): string => {
  const colors = getThemeColors(isDark)

  // Check if HTML already has a complete structure
  const hasHtmlTag = /<html/i.test(html)
  const hasBodyTag = /<body/i.test(html)

  // More comprehensive theme overrides for all elements
  const cardBg = isDark ? '#161b22' : '#f6f8fa'
  const cardBorder = isDark ? '#30363d' : '#d0d7de'
  const inputBg = isDark ? '#0d1117' : '#ffffff'

  const themeStyles = `
    <style data-theme-inject="true">
      /* Base overrides */
      html, body {
        background: ${colors.bg} !important;
        color: ${colors.text} !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
      }
      body {
        padding: 20px;
      }

      /* Text elements */
      a { color: ${colors.link} !important; }
      h1, h2, h3, h4, h5, h6 { color: ${colors.heading} !important; }
      p, span, div, li, td, th, label { color: ${colors.text} !important; }

      /* Code blocks */
      pre, code {
        background: ${colors.code} !important;
        color: ${colors.text} !important;
      }

      /* Override ALL divs, sections, articles - force theme background */
      div, section, article, aside, main, header, footer, nav {
        background-color: transparent !important;
      }

      /* Cards, panels, columns - common component patterns */
      [class*="card"], [class*="Card"],
      [class*="panel"], [class*="Panel"],
      [class*="column"], [class*="Column"],
      [class*="item"], [class*="Item"],
      [class*="box"], [class*="Box"],
      [class*="tile"], [class*="Tile"],
      [class*="block"], [class*="Block"],
      [class*="container"], [class*="Container"],
      [class*="wrapper"], [class*="Wrapper"],
      [class*="section"], [class*="Section"],
      [class*="header"], [class*="Header"],
      [class*="footer"], [class*="Footer"],
      [class*="list"], [class*="List"],
      [class*="board"], [class*="Board"],
      [class*="lane"], [class*="Lane"],
      [class*="task"], [class*="Task"],
      [class*="todo"], [class*="Todo"],
      [class*="kanban"], [class*="Kanban"] {
        background-color: ${cardBg} !important;
        border-color: ${cardBorder} !important;
        color: ${colors.text} !important;
      }

      /* Specific board.html classes - use background shorthand to override */
      .kanban-board {
        background: ${colors.bg} !important;
      }
      .kanban-column,
      .column-header,
      .column-tasks,
      .header,
      .header-stats,
      .view-toggle {
        background: ${cardBg} !important;
        border-color: ${cardBorder} !important;
        color: ${colors.text} !important;
      }
      .column-count,
      .view-btn,
      .stat,
      .tag,
      .agent-badge {
        background: ${isDark ? '#30363d' : '#e1e4e8'} !important;
        color: ${colors.text} !important;
      }
      .task-card {
        background: ${colors.bg} !important;
        border-color: ${cardBorder} !important;
        color: ${colors.text} !important;
      }
      .task-title {
        color: ${colors.heading} !important;
        background: transparent !important;
      }
      .task-description,
      .task-meta {
        color: ${isDark ? '#8b949e' : '#57606a'} !important;
        background: transparent !important;
      }

      /* Keep priority badges colorful */
      .priority-low { background: #238636 !important; color: #fff !important; }
      .priority-medium { background: #1f6feb !important; color: #fff !important; }
      .priority-high { background: #d29922 !important; color: ${isDark ? '#000' : '#000'} !important; }
      .priority-critical { background: #f85149 !important; color: #fff !important; }

      /* Status colors */
      .view-btn.active {
        background: #238636 !important;
        color: #fff !important;
      }

      /* Nested content should be transparent */
      [class*="card"] > div,
      [class*="Card"] > div,
      [class*="column"] > div,
      [class*="Column"] > div {
        background-color: transparent !important;
      }

      /* Form elements */
      input, textarea, select, button {
        background-color: ${inputBg} !important;
        color: ${colors.text} !important;
        border-color: ${cardBorder} !important;
      }

      button {
        background-color: ${cardBg} !important;
      }

      button:hover {
        background-color: ${isDark ? '#21262d' : '#eaeef2'} !important;
      }

      /* Tables */
      table, tr, td, th {
        background-color: transparent !important;
        border-color: ${cardBorder} !important;
        color: ${colors.text} !important;
      }

      th {
        background-color: ${cardBg} !important;
      }

      /* Override inline background styles - use [style] attribute selector */
      [style*="background"] {
        background-color: ${cardBg} !important;
      }

      /* But keep body background */
      body[style*="background"], html[style*="background"] {
        background-color: ${colors.bg} !important;
      }
    </style>
  `

  // Inject at BOTH end of head AND end of body for maximum override
  let result = html

  if (hasHtmlTag) {
    // Inject styles at END of head (before </head>) to override page styles
    if (/<\/head>/i.test(result)) {
      result = result.replace(/<\/head>/i, `${themeStyles}</head>`)
    } else if (/<head/i.test(result)) {
      // Has <head> but no </head>, inject after <head>
      result = result.replace(/<head([^>]*)>/i, `<head$1>${themeStyles}`)
    } else {
      result = result.replace(/<html([^>]*)>/i, `<html$1><head>${themeStyles}</head>`)
    }

    // Also inject at end of body for double coverage
    if (/<\/body>/i.test(result)) {
      result = result.replace(/<\/body>/i, `${themeStyles}</body>`)
    }

    return result
  } else if (hasBodyTag) {
    // Wrap with html/head and inject styles
    return `<html><head>${themeStyles}</head>${html.replace(/<\/body>/i, `${themeStyles}</body>`)}</html>`
  } else {
    // No structure, wrap completely
    return `<html><head>${themeStyles}</head><body>${html}${themeStyles}</body></html>`
  }
}

// Simple markdown to HTML converter (theme-aware)
const markdownToHtml = (md: string, isDark: boolean = true): string => {
  let html = md
    // Headers
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    // Code blocks
    .replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
    // Inline code
    .replace(/`(.*?)`/gim, '<code>$1</code>')
    // Links
    .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2">$1</a>')
    // Lists
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    // Line breaks
    .replace(/\n/gim, '<br>')

  // Theme-aware colors
  const colors = isDark ? {
    bg: '#0d1117',
    text: '#c9d1d9',
    heading: '#f0f6fc',
    code: '#21262d',
    link: '#58a6ff'
  } : {
    bg: '#ffffff',
    text: '#1f2328',
    heading: '#1f2328',
    code: '#f6f8fa',
    link: '#0969da'
  }

  return `
    <html>
    <head>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding: 20px;
          max-width: 800px;
          margin: 0 auto;
          background: ${colors.bg};
          color: ${colors.text};
          line-height: 1.6;
        }
        h1, h2, h3 { color: ${colors.heading}; margin-top: 24px; }
        code { background: ${colors.code}; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
        pre { background: ${colors.code}; padding: 16px; border-radius: 8px; overflow-x: auto; }
        pre code { background: none; padding: 0; }
        a { color: ${colors.link}; }
        li { margin: 4px 0; }
      </style>
    </head>
    <body>${html}</body>
    </html>
  `
}

export default function FileViewer({ selectedPath, onPathChange, explorerVisible, onToggleExplorer, isDarkTheme = true }: FileViewerProps) {
  const [contents, setContents] = useState<FolderContents | null>(null)
  const [fileContent, setFileContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [taskData,] = useState<Task | null>(null)
  const [currentPath, setCurrentPath] = useState<string | null>(selectedPath)
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState<string>('')
  const [viewMode, setViewMode] = useState<'view' | 'edit'>('view')
  const iframeRef = useRef<HTMLIFrameElement>(null)

  // Sync currentPath with selectedPath from parent
  useEffect(() => {
    setCurrentPath(selectedPath)
    setIsEditing(false) // Reset editing when path changes
    setViewMode('view') // Reset to view mode for new files
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
          {!explorerVisible && onToggleExplorer && (
            <button
              className="show-explorer-title-btn"
              onClick={onToggleExplorer}
              title="Show Explorer"
            >
              <PanelLeft size={16} />
            </button>
          )}
          <div className="file-viewer-title-text">
            <h2>{currentPath.split('/').pop()}</h2>
            <div className="file-viewer-path">{currentPath}</div>
          </div>
        </div>
        <div className="file-viewer-actions">
          {/* View/Edit toggle for renderable files */}
          {fileContent && currentPath && isRenderableFile(currentPath) && !isEditing && (
            <div className="view-mode-toggle">
              <button
                className={`toggle-btn ${viewMode === 'view' ? 'active' : ''}`}
                onClick={() => setViewMode('view')}
                title="View rendered"
              >
                <Eye size={14} />
                View
              </button>
              <button
                className={`toggle-btn ${viewMode === 'edit' ? 'active' : ''}`}
                onClick={() => setViewMode('edit')}
                title="View source"
              >
                <Code size={14} />
                Code
              </button>
            </div>
          )}
          {!isEditing && fileContent && viewMode === 'edit' && (
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
            ) : currentPath && isRenderableFile(currentPath) && viewMode === 'view' ? (
              <div className="rendered-content">
                <iframe
                  key={`${currentPath}-${isDarkTheme ? 'dark' : 'light'}`}
                  ref={iframeRef}
                  srcDoc={
                    isMarkdownFile(currentPath)
                      ? markdownToHtml(fileContent, isDarkTheme)
                      : isHtmlFile(currentPath)
                        ? wrapHtmlWithTheme(fileContent, isDarkTheme)
                        : fileContent
                  }
                  title="Rendered content"
                  sandbox="allow-scripts allow-same-origin"
                  className="content-iframe"
                />
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

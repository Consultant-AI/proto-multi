import { useState, useEffect, useRef, useCallback, useImperativeHandle, forwardRef } from 'react'
import '../styles/BrowserPanel.css'

// Check if we're running in Electron
const isElectron = typeof window !== 'undefined' &&
  (window as any).process?.versions?.electron !== undefined

// Type for Electron webview element
interface WebviewElement extends HTMLElement {
  src: string
  loadURL: (url: string) => void
  reload: () => void
  goBack: () => void
  goForward: () => void
  canGoBack: () => boolean
  canGoForward: () => boolean
  getURL: () => string
  getTitle: () => string
  isLoading: () => boolean
  addEventListener: (event: string, callback: (event: any) => void) => void
  removeEventListener: (event: string, callback: (event: any) => void) => void
}

interface BrowserPanelProps {
  url?: string
  tabId?: string
  isActive?: boolean
  onUrlChange?: (url: string) => void
  onTitleChange?: (title: string) => void
  onLoadingChange?: (isLoading: boolean) => void
  onNavigationChange?: (canGoBack: boolean, canGoForward: boolean) => void
}

export interface BrowserPanelRef {
  navigateTo: (url: string) => void
  goBack: () => void
  goForward: () => void
  reload: () => void
  canGoBack: () => boolean
  canGoForward: () => boolean
}

const BrowserPanel = forwardRef<BrowserPanelRef, BrowserPanelProps>(({
  url: initialUrl,
  tabId: _tabId = 'default',
  isActive: _isActive = true,
  onUrlChange,
  onTitleChange,
  onLoadingChange,
  onNavigationChange
}, ref) => {
  // Note: _tabId and _isActive are kept for API compatibility but not used internally
  const webviewRef = useRef<WebviewElement>(null)
  const [currentUrl, setCurrentUrl] = useState(initialUrl || '')
  const [canGoBackState, setCanGoBackState] = useState(false)
  const [canGoForwardState, setCanGoForwardState] = useState(false)
  const initializedRef = useRef(false)

  // Store callbacks in refs to avoid useEffect re-runs
  const callbacksRef = useRef({ onUrlChange, onTitleChange, onLoadingChange, onNavigationChange })
  callbacksRef.current = { onUrlChange, onTitleChange, onLoadingChange, onNavigationChange }

  // Navigate to URL
  const navigateTo = useCallback((url: string) => {
    if (!url) return

    // Add protocol if missing
    let fullUrl = url
    if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('file://')) {
      fullUrl = 'https://' + url
    }

    setCurrentUrl(fullUrl)

    if (webviewRef.current) {
      webviewRef.current.src = fullUrl
    }
  }, [])

  // Expose methods via ref
  useImperativeHandle(ref, () => ({
    navigateTo,
    goBack: () => webviewRef.current?.goBack(),
    goForward: () => webviewRef.current?.goForward(),
    reload: () => webviewRef.current?.reload(),
    canGoBack: () => canGoBackState,
    canGoForward: () => canGoForwardState
  }), [navigateTo, canGoBackState, canGoForwardState])

  // Handle URL changes from parent (not initial load)
  useEffect(() => {
    // Skip initial mount - handled in the main useEffect
    if (!initializedRef.current) return

    // Only navigate if URL actually changed from parent
    if (initialUrl && initialUrl !== currentUrl) {
      navigateTo(initialUrl)
    }
  }, [initialUrl])

  // Set up webview event listeners (only once on mount)
  useEffect(() => {
    const webview = webviewRef.current
    if (!webview || !isElectron) return

    const updateNavigationState = () => {
      const canBack = webview.canGoBack()
      const canForward = webview.canGoForward()
      setCanGoBackState(canBack)
      setCanGoForwardState(canForward)
      callbacksRef.current.onNavigationChange?.(canBack, canForward)
    }

    const handleDidNavigate = (event: any) => {
      const url = event.url || webview.getURL()
      setCurrentUrl(url)
      callbacksRef.current.onUrlChange?.(url)
      callbacksRef.current.onLoadingChange?.(false)
      updateNavigationState()
    }

    const handleDidNavigateInPage = (event: any) => {
      const url = event.url || webview.getURL()
      setCurrentUrl(url)
      callbacksRef.current.onUrlChange?.(url)
      updateNavigationState()
    }

    const handleDidStartLoading = () => {
      callbacksRef.current.onLoadingChange?.(true)
    }

    const handleDidStopLoading = () => {
      callbacksRef.current.onLoadingChange?.(false)
      updateNavigationState()
    }

    const handlePageTitleUpdated = (event: any) => {
      const title = event.title || webview.getTitle()
      callbacksRef.current.onTitleChange?.(title)
    }

    const handleDidFailLoad = (event: any) => {
      console.error('Page load failed:', event.errorDescription)
      callbacksRef.current.onLoadingChange?.(false)
    }

    // Add event listeners
    webview.addEventListener('did-navigate', handleDidNavigate)
    webview.addEventListener('did-navigate-in-page', handleDidNavigateInPage)
    webview.addEventListener('did-start-loading', handleDidStartLoading)
    webview.addEventListener('did-stop-loading', handleDidStopLoading)
    webview.addEventListener('page-title-updated', handlePageTitleUpdated)
    webview.addEventListener('did-fail-load', handleDidFailLoad)

    // Navigate to initial URL only once
    if (initialUrl && !initializedRef.current) {
      initializedRef.current = true
      navigateTo(initialUrl)
    }

    return () => {
      webview.removeEventListener('did-navigate', handleDidNavigate)
      webview.removeEventListener('did-navigate-in-page', handleDidNavigateInPage)
      webview.removeEventListener('did-start-loading', handleDidStartLoading)
      webview.removeEventListener('did-stop-loading', handleDidStopLoading)
      webview.removeEventListener('page-title-updated', handlePageTitleUpdated)
      webview.removeEventListener('did-fail-load', handleDidFailLoad)
    }
  }, []) // Empty deps - only run once on mount

  // Fallback for non-Electron (regular browser)
  if (!isElectron) {
    return (
      <div className="browser-panel">
        <div className="browser-viewport">
          {initialUrl ? (
            <iframe
              src={initialUrl}
              className="browser-iframe-fallback"
              title="Web Page"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-top-navigation"
            />
          ) : (
            <div className="browser-loading">
              <p>Enter a URL to browse</p>
              <p className="browser-note">Note: Run as Electron app for full browser features</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Electron webview version - just the webview, no toolbar
  return (
    <div className="browser-panel">
      <div className="browser-viewport">
        {/* @ts-ignore - webview is Electron-specific */}
        <webview
          ref={webviewRef as any}
          src={currentUrl || 'about:blank'}
          className="browser-webview"
          // @ts-ignore - Electron webview attributes
          allowpopups="true"
          partition="persist:main"
        />
      </div>
    </div>
  )
})

BrowserPanel.displayName = 'BrowserPanel'

export default BrowserPanel

import { useState, useEffect, useRef } from 'react'
import { RotateCw } from 'lucide-react'
import '../styles/BrowserPanel.css'

// Track navigation per tab (persists across component remounts)
const tabNavigationMap = new Map<string, string>()

interface ScreenBounds {
    x: number;
    y: number;
    width: number;
    height: number;
}

interface BrowserPanelProps {
    url?: string;
    tabId?: string;  // Unique tab ID for multi-tab support
    isActive?: boolean;  // Explicit control from parent
    useQtBrowser?: boolean;  // If true, use Qt WebEngine streaming instead of iframe
}

export default function BrowserPanel({ url: initialUrl, tabId = 'default', isActive = false, useQtBrowser = true }: BrowserPanelProps) {
    const [screenshot, setScreenshot] = useState<string | null>(null)
    const [bounds, setBounds] = useState<ScreenBounds | null>(null)
    const containerRef = useRef<HTMLDivElement>(null)
    const imageRef = useRef<HTMLImageElement>(null)
    const wsRef = useRef<WebSocket | null>(null)
    const [connected, setConnected] = useState(false)
    const reconnectTimeoutRef = useRef<number | null>(null)
    // Use Qt browser by default (works with all sites), iframe mode blocks many sites due to X-Frame-Options
    const [useIframeFallback, setUseIframeFallback] = useState(!useQtBrowser)
    const fallbackTimeoutRef = useRef<number | null>(null)

    // Clear screenshot when tab changes to avoid showing stale content from previous tab
    useEffect(() => {
        setScreenshot(null)
    }, [tabId])

    // WebSocket connection for real-time frame streaming with iframe fallback
    useEffect(() => {
        // Only connect if active (from parent) and not using iframe fallback
        if (!isActive || useIframeFallback) {
            if (wsRef.current) {
                console.log('Browser panel not visible or using fallback, closing WebSocket')
                wsRef.current.close()
                wsRef.current = null
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current)
                reconnectTimeoutRef.current = null
            }
            if (fallbackTimeoutRef.current) {
                clearTimeout(fallbackTimeoutRef.current)
                fallbackTimeoutRef.current = null
            }
            return
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${protocol}//${window.location.host}/ws/browser/stream`

        // Set a fallback timeout - if no frames received after 3 seconds, use iframe
        fallbackTimeoutRef.current = window.setTimeout(() => {
            if (!screenshot && initialUrl) {
                console.log('No frames received, switching to iframe fallback')
                setUseIframeFallback(true)
            }
        }, 3000)

        const connectWebSocket = () => {
            // Don't reconnect if not active or using fallback
            if (!isActive || useIframeFallback) return

            const ws = new WebSocket(wsUrl)

            ws.onopen = () => {
                console.log('Browser WebSocket connected')
                setConnected(true)
            }

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data)
                    if (data.type === 'frame') {
                        setScreenshot(data.image)
                        setBounds(data.bounds)
                        // Clear fallback timeout since we got a frame
                        if (fallbackTimeoutRef.current) {
                            clearTimeout(fallbackTimeoutRef.current)
                            fallbackTimeoutRef.current = null
                        }
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error)
                }
            }

            ws.onerror = (error) => {
                console.error('Browser WebSocket error:', error)
            }

            ws.onclose = () => {
                console.log('Browser WebSocket closed')
                setConnected(false)
                // Don't auto-reconnect - parent controls lifecycle via isActive
            }

            wsRef.current = ws
        }

        connectWebSocket()

        return () => {
            if (wsRef.current) {
                wsRef.current.close()
                wsRef.current = null
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current)
                reconnectTimeoutRef.current = null
            }
            if (fallbackTimeoutRef.current) {
                clearTimeout(fallbackTimeoutRef.current)
                fallbackTimeoutRef.current = null
            }
        }
    }, [isActive, useIframeFallback, screenshot, initialUrl])

    // Auto-navigate only when URL actually changes (not on tab switch)
    useEffect(() => {
        if (initialUrl && isActive && !useIframeFallback) {
            // Check if this tab has already navigated to this URL
            const lastNavigatedUrl = tabNavigationMap.get(tabId)
            if (lastNavigatedUrl !== initialUrl) {
                // New URL - navigate to it
                handleNavigate(initialUrl)
                tabNavigationMap.set(tabId, initialUrl)
            } else {
                // Same URL - just switch to this tab without re-navigating
                handleSwitchTab()
            }
        }
    }, [initialUrl, isActive, useIframeFallback, tabId])

    const handleSwitchTab = async () => {
        try {
            await fetch('/api/computer/browser/switch-tab', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tab_id: tabId })
            })
        } catch (error) {
            console.error('Tab switch failed:', error)
        }
    }

    const handleNavigate = async (url: string) => {
        if (!url) return
        try {
            await fetch('/api/computer/browser/navigate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, tab_id: tabId })
            })
        } catch (error) {
            console.error('Navigation failed:', error)
        }
    }

    const handleInteraction = async (e: React.MouseEvent<HTMLImageElement>) => {
        if (!imageRef.current || !bounds) return

        const rect = imageRef.current.getBoundingClientRect()
        const scaleX = bounds.width / rect.width
        const scaleY = bounds.height / rect.height

        const x = Math.round((e.clientX - rect.left) * scaleX)
        const y = Math.round((e.clientY - rect.top) * scaleY)

        try {
            await fetch('/api/computer/browser/click', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ x, y, button: 'left', tab_id: tabId })
            })
        } catch (error) {
            console.error('Click interaction failed:', error)
        }
    }

    const handleKeyDown = async (e: React.KeyboardEvent) => {
        // Only handle if not in the address bar
        if (e.target instanceof HTMLInputElement && e.target.className === 'address-input') return

        // Simple key press (ignoring modifiers for now for simplicity)
        if (e.key.length === 1 || e.key === 'Enter' || e.key === 'Backspace') {
            try {
                await fetch('/api/computer/browser/type', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: e.key === 'Enter' ? '' : e.key,
                        enter: e.key === 'Enter'
                    })
                })
            } catch (error) {
                console.error('Type interaction failed:', error)
            }
        }
    }

    const handleScroll = async (e: React.WheelEvent<HTMLImageElement>) => {
        if (!imageRef.current || !bounds) return
        e.preventDefault()

        const rect = imageRef.current.getBoundingClientRect()
        const scaleX = bounds.width / rect.width
        const scaleY = bounds.height / rect.height

        // Get scroll position relative to the image
        const x = Math.round((e.clientX - rect.left) * scaleX)
        const y = Math.round((e.clientY - rect.top) * scaleY)

        // deltaY: positive = scroll down, negative = scroll up
        const deltaX = Math.round(e.deltaX)
        const deltaY = Math.round(e.deltaY)

        try {
            await fetch('/api/computer/browser/scroll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ x, y, deltaX, deltaY, tab_id: tabId })
            })
        } catch (error) {
            console.error('Scroll interaction failed:', error)
        }
    }

    return (
        <div className="browser-panel" onKeyDown={useQtBrowser ? handleKeyDown : undefined} tabIndex={useQtBrowser ? 0 : undefined}>
            <div className="browser-viewport" ref={containerRef}>
                {useIframeFallback ? (
                    initialUrl ? (
                        <iframe
                            src={initialUrl}
                            className="browser-iframe-fallback"
                            title="Web Page"
                            sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-top-navigation"
                        />
                    ) : (
                        <div className="browser-loading">
                            <p>Enter a URL to browse</p>
                        </div>
                    )
                ) : screenshot ? (
                    <div className="browser-canvas">
                        <img
                            ref={imageRef}
                            src={`data:image/jpeg;base64,${screenshot}`}
                            alt="Chromium Browser"
                            onClick={handleInteraction}
                            onWheel={handleScroll}
                            draggable={false}
                        />
                        {!connected && (
                            <div className="connection-status">
                                <span>Reconnecting...</span>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="browser-loading">
                        <RotateCw size={48} className="spin" />
                        <p>Connecting to Qt Browser...</p>
                    </div>
                )}
            </div>
        </div>
    )
}

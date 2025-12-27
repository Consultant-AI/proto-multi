import { useState, useEffect, useRef } from 'react'
import { RotateCw } from 'lucide-react'
import '../styles/BrowserPanel.css'

interface ScreenBounds {
    x: number;
    y: number;
    width: number;
    height: number;
}

interface BrowserPanelProps {
    url?: string;
    isActive?: boolean;  // Explicit control from parent
}

export default function BrowserPanel({ url: initialUrl, isActive = false }: BrowserPanelProps) {
    const [screenshot, setScreenshot] = useState<string | null>(null)
    const [bounds, setBounds] = useState<ScreenBounds | null>(null)
    const containerRef = useRef<HTMLDivElement>(null)
    const imageRef = useRef<HTMLImageElement>(null)
    const wsRef = useRef<WebSocket | null>(null)
    const [hasNavigated, setHasNavigated] = useState(false)
    const [connected, setConnected] = useState(false)
    const reconnectTimeoutRef = useRef<number | null>(null)
    // Start with Qt browser streaming - only fall back to iframe if streaming fails
    const [useIframeFallback, setUseIframeFallback] = useState(false)
    const fallbackTimeoutRef = useRef<number | null>(null)

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

    // Auto-navigate when URL prop changes
    useEffect(() => {
        if (initialUrl && !hasNavigated) {
            handleNavigate(initialUrl)
            setHasNavigated(true)
        }
    }, [initialUrl, hasNavigated])

    const handleNavigate = async (url: string) => {
        if (!url) return
        try {
            await fetch('/api/computer/browser/navigate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: url })
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
                body: JSON.stringify({ x, y, button: 'left' })
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

    return (
        <div className="browser-panel" onKeyDown={handleKeyDown} tabIndex={0}>
            <div className="browser-viewport" ref={containerRef}>
                {useIframeFallback && initialUrl ? (
                    <iframe
                        src={initialUrl}
                        className="browser-iframe-fallback"
                        title="Web Page"
                        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                    />
                ) : screenshot ? (
                    <div className="browser-canvas">
                        <img
                            ref={imageRef}
                            src={`data:image/jpeg;base64,${screenshot}`}
                            alt="Chromium Browser"
                            onClick={handleInteraction}
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
                        <p>Connecting to Real Chromium Browser...</p>
                    </div>
                )}
            </div>
        </div>
    )
}

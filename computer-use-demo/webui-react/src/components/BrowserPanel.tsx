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
}

export default function BrowserPanel({ url: initialUrl }: BrowserPanelProps) {
    const [screenshot, setScreenshot] = useState<string | null>(null)
    const [bounds, setBounds] = useState<ScreenBounds | null>(null)
    const containerRef = useRef<HTMLDivElement>(null)
    const imageRef = useRef<HTMLImageElement>(null)
    const [hasNavigated, setHasNavigated] = useState(false)

    const fetchScreenshot = async () => {
        try {
            const response = await fetch('/api/computer/browser/screenshot')
            if (response.ok) {
                const data = await response.json()
                setScreenshot(data.image)
                setBounds(data.bounds)
            }
        } catch (error) {
            console.error('Failed to fetch browser screenshot:', error)
        }
    }

    useEffect(() => {
        fetchScreenshot()
        const interval = setInterval(fetchScreenshot, 1000) // Fast refresh for interaction
        return () => clearInterval(interval)
    }, [])

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
                {screenshot ? (
                    <div className="browser-canvas">
                        <img
                            ref={imageRef}
                            src={`data:image/png;base64,${screenshot}`}
                            alt="Chromium Viewport"
                            onClick={handleInteraction}
                            draggable={false}
                        />
                    </div>
                ) : (
                    <div className="browser-loading">
                        <RotateCw size={48} className="spin" />
                        <p>Connecting to Chromium...</p>
                    </div>
                )}
            </div>
        </div>
    )
}

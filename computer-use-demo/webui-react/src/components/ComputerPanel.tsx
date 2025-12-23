import { useState, useEffect, useRef } from 'react'
import { Monitor } from 'lucide-react'
import '../styles/ComputerPanel.css'

export default function ComputerPanel() {
    const [screenshot, setScreenshot] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [isVisible, setIsVisible] = useState(true)
    const containerRef = useRef<HTMLDivElement>(null)

    const fetchScreenshot = async () => {
        setError(null)
        try {
            const response = await fetch('/api/computer/screenshot')
            if (response.ok) {
                const data = await response.json()
                setScreenshot(data.image)
            } else {
                setError('Failed to fetch screenshot')
            }
        } catch (error) {
            console.error('Failed to fetch screenshot:', error)
            setError('Connection error')
        }
    }

    // Track visibility of the component
    useEffect(() => {
        if (!containerRef.current) return

        const observer = new IntersectionObserver(
            ([entry]) => {
                setIsVisible(entry.isIntersecting)
            },
            { threshold: 0.1 }
        )

        observer.observe(containerRef.current)

        return () => {
            observer.disconnect()
        }
    }, [])

    // Initial fetch
    useEffect(() => {
        if (isVisible) {
            fetchScreenshot()
        }
    }, [isVisible])

    // Polling interval - only when visible
    useEffect(() => {
        if (!isVisible) return

        const interval = setInterval(fetchScreenshot, 2000) // Every 2s for live feel
        return () => clearInterval(interval)
    }, [isVisible])

    return (
        <div className="computer-panel" ref={containerRef}>
            <div className="computer-panel-header" onClick={(e) => e.stopPropagation()}>
                <div className="computer-panel-title">
                    <Monitor size={18} />
                    <h2>This Computer</h2>
                </div>
            </div>
            <div className="computer-panel-content">
                {screenshot ? (
                    <div className="screen-container">
                        <img src={`data:image/png;base64,${screenshot}`} alt="Computer Screen" className="screen-image" />
                        {error && <div className="error-overlay">{error}</div>}
                    </div>
                ) : (
                    <div className="no-screen">
                        <Monitor size={64} opacity={0.2} />
                        <p>{error || 'Waiting for first screenshot...'}</p>
                        <button className="init-btn" onClick={fetchScreenshot}>
                            Initialize View
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}

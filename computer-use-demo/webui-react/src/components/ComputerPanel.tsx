import { useState, useEffect } from 'react'
import { Monitor, RefreshCw } from 'lucide-react'
import '../styles/ComputerPanel.css'

export default function ComputerPanel() {
    const [screenshot, setScreenshot] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const [autoRefresh, setAutoRefresh] = useState(false)

    const fetchScreenshot = async () => {
        setLoading(true)
        try {
            const response = await fetch('/api/computer/screenshot')
            if (response.ok) {
                const data = await response.json()
                setScreenshot(data.image)
            }
        } catch (error) {
            console.error('Failed to fetch screenshot:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchScreenshot()
    }, [])

    useEffect(() => {
        if (!autoRefresh) return
        const interval = setInterval(fetchScreenshot, 10000) // Every 10s
        return () => clearInterval(interval)
    }, [autoRefresh])

    return (
        <div className="computer-panel">
            <div className="computer-panel-header">
                <div className="computer-panel-title">
                    <Monitor size={18} />
                    <h2>Live View</h2>
                </div>
                <div className="computer-panel-actions">
                    <button
                        className={`refresh-btn ${loading ? 'loading' : ''}`}
                        onClick={fetchScreenshot}
                        disabled={loading}
                        title="Manual Refresh"
                    >
                        <RefreshCw size={16} />
                    </button>
                    <label className="auto-refresh-toggle">
                        <input
                            type="checkbox"
                            checked={autoRefresh}
                            onChange={(e) => setAutoRefresh(e.target.checked)}
                        />
                        <span>Auto-update</span>
                    </label>
                </div>
            </div>
            <div className="computer-panel-content">
                {screenshot ? (
                    <div className="screen-container">
                        <img src={`data:image/png;base64,${screenshot}`} alt="Computer Screen" className="screen-image" />
                    </div>
                ) : (
                    <div className="no-screen">
                        <Monitor size={64} opacity={0.2} />
                        <p>Waiting for first screenshot...</p>
                        <button className="init-btn" onClick={fetchScreenshot}>Initialize View</button>
                    </div>
                )}
            </div>
        </div>
    )
}

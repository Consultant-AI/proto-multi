import { useState, useEffect } from 'react'
import { Monitor, RefreshCw } from 'lucide-react'
import '../styles/ComputerPanel.css'

export default function ComputerPanel() {
    const [screenshot, setScreenshot] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const [autoRefresh, setAutoRefresh] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const fetchScreenshot = async () => {
        setLoading(true)
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
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchScreenshot()
    }, [])

    useEffect(() => {
        if (!autoRefresh) return
        const interval = setInterval(fetchScreenshot, 2000) // Every 2s for live feel
        return () => clearInterval(interval)
    }, [autoRefresh])

    return (
        <div className="computer-panel">
            <div className="computer-panel-header" onClick={(e) => e.stopPropagation()}>
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
                        {error && <div className="error-overlay">{error}</div>}
                    </div>
                ) : (
                    <div className="no-screen">
                        <Monitor size={64} opacity={0.2} />
                        <p>{error || 'Waiting for first screenshot...'}</p>
                        <button className="init-btn" onClick={fetchScreenshot} disabled={loading}>
                            {loading ? 'Loading...' : 'Initialize View'}
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}

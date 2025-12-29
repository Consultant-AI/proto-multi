import { useState, useEffect, useRef, useCallback } from 'react'
import { Monitor, RefreshCw, Pause, Play, Camera, Trash2, MousePointer, MousePointer2Off } from 'lucide-react'
import '../styles/ComputerPanel.css'

interface ComputerPanelProps {
    isActive?: boolean;  // Explicit control from parent
    selectedComputer?: string;  // Computer ID ('local' or remote computer ID)
    resourceId?: string;  // Resource ID from tab (overrides selectedComputer)
    onInstanceDeleted?: () => void;  // Callback when instance is deleted
}

export default function ComputerPanel({ isActive = true, selectedComputer = 'local', resourceId, onInstanceDeleted }: ComputerPanelProps) {
    // Determine actual computer ID - treat 'main', '', undefined as 'local'
    const computerId = (resourceId && resourceId !== 'main' && resourceId !== '') ? resourceId : (selectedComputer || 'local')
    const isLocalComputer = computerId === 'local' || !computerId
    const isHetznerInstance = computerId.startsWith('hetzner-')
    const hetznerInstanceId = isHetznerInstance ? computerId.replace('hetzner-', '') : null

    const [screenshot, setScreenshot] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [vncUrl, setVncUrl] = useState<string | null>(null)
    const [computerName, setComputerName] = useState(isLocalComputer ? 'This Computer' : computerId)
    const [isConnecting, setIsConnecting] = useState(false)
    const [instanceStatus, setInstanceStatus] = useState<string>('running')
    const [isActionPending, setIsActionPending] = useState(false)
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
    const [snapshotName, setSnapshotName] = useState('')
    const [showSnapshotDialog, setShowSnapshotDialog] = useState(false)
    const [controlEnabled, setControlEnabled] = useState(true)
    const containerRef = useRef<HTMLDivElement>(null)
    const iframeRef = useRef<HTMLIFrameElement>(null)

    // Hetzner instance actions
    const handlePauseResume = async () => {
        if (!hetznerInstanceId) return
        setIsActionPending(true)
        try {
            const action = instanceStatus === 'running' ? 'stop' : 'start'
            const response = await fetch(`/api/hetzner/instances/${hetznerInstanceId}/${action}`, {
                method: 'POST'
            })
            if (response.ok) {
                setInstanceStatus(action === 'stop' ? 'stopped' : 'running')
                if (action === 'stop') {
                    setVncUrl(null) // Clear VNC when stopped
                }
            }
        } catch (err) {
            console.error('Failed to pause/resume instance:', err)
        } finally {
            setIsActionPending(false)
        }
    }

    const handleSnapshot = async () => {
        if (!hetznerInstanceId || !snapshotName.trim()) return
        setIsActionPending(true)
        try {
            const response = await fetch(`/api/hetzner/instances/${hetznerInstanceId}/snapshot`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: snapshotName.trim() })
            })
            if (response.ok) {
                setShowSnapshotDialog(false)
                setSnapshotName('')
                alert('Snapshot created successfully!')
            }
        } catch (err) {
            console.error('Failed to create snapshot:', err)
        } finally {
            setIsActionPending(false)
        }
    }

    const handleDelete = async () => {
        if (!hetznerInstanceId) return
        setIsActionPending(true)
        try {
            const response = await fetch(`/api/hetzner/instances/${hetznerInstanceId}`, {
                method: 'DELETE'
            })
            if (response.ok) {
                setShowDeleteConfirm(false)
                onInstanceDeleted?.()
            }
        } catch (err) {
            console.error('Failed to delete instance:', err)
        } finally {
            setIsActionPending(false)
        }
    }

    const fetchScreenshot = useCallback(async () => {
        try {
            const response = await fetch('/api/computer/screenshot')
            if (response.ok) {
                const data = await response.json()
                setScreenshot(data.image)
                setError(null)
            }
        } catch (err) {
            console.error('Failed to fetch screenshot:', err)
        }
    }, [])


    const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    const setupRemoteVNC = useCallback(async () => {
        if (!computerId || computerId === 'local') return

        // Clear any pending retry
        if (retryTimeoutRef.current) {
            clearTimeout(retryTimeoutRef.current)
            retryTimeoutRef.current = null
        }

        setIsConnecting(true)
        setError(null)
        setComputerName(computerId)

        try {
            const response = await fetch(`/api/computers/${computerId}/vnc-tunnel`, {
                method: 'POST'
            })

            if (response.ok) {
                const data = await response.json()
                if (data.computer_name) {
                    setComputerName(data.computer_name)
                }
                setVncUrl(data.vnc_url)
                setIsConnecting(false)
            } else if (response.status === 503) {
                // Services still starting - show loading and retry
                setError('Waiting for instance to start...')
                retryTimeoutRef.current = setTimeout(() => {
                    setupRemoteVNC()
                }, 3000)
            } else {
                const errData = await response.json().catch(() => ({}))
                setError(errData.detail || 'Failed to connect')
                setIsConnecting(false)
            }
        } catch (err) {
            console.error('VNC setup error:', err)
            setError('Could not connect to remote computer')
            setIsConnecting(false)
        }
    }, [computerId])

    // Auto-initialize on mount and when computerId changes
    useEffect(() => {
        if (!isActive) return

        // Reset state when switching computers
        setScreenshot(null)
        setVncUrl(null)
        setError(null)

        // Clear any pending retries
        if (retryTimeoutRef.current) {
            clearTimeout(retryTimeoutRef.current)
            retryTimeoutRef.current = null
        }

        if (isLocalComputer) {
            // Local mode: auto-start screenshot polling
            setComputerName('This Computer')
            fetchScreenshot() // Initial fetch
            const interval = setInterval(fetchScreenshot, 2000)
            return () => clearInterval(interval)
        } else {
            // Remote mode: auto-setup VNC tunnel
            setComputerName(computerId)
            setupRemoteVNC()
        }

        // Cleanup on unmount
        return () => {
            if (retryTimeoutRef.current) {
                clearTimeout(retryTimeoutRef.current)
                retryTimeoutRef.current = null
            }
        }
    }, [isActive, computerId, isLocalComputer, fetchScreenshot, setupRemoteVNC])

    return (
        <div className="computer-panel" ref={containerRef}>
            {/* Header with controls */}
            <div className="computer-panel-header" onClick={(e) => e.stopPropagation()}>
                <div className="computer-panel-title">
                    <Monitor size={18} />
                    <h2>{computerName}</h2>
                </div>
                <div className="computer-panel-actions">
                    {/* Instance status badge */}
                    {isHetznerInstance && (
                        <span className={`instance-status ${instanceStatus}`}>
                            {instanceStatus}
                        </span>
                    )}
                    {/* Control toggle */}
                    {!isLocalComputer && (
                        <button
                            type="button"
                            className={`text-btn control-toggle ${controlEnabled ? 'active' : ''}`}
                            onClick={() => setControlEnabled(!controlEnabled)}
                        >
                            {controlEnabled ? <><MousePointer size={14} /> Control: ON</> : <><MousePointer2Off size={14} /> Control: OFF</>}
                        </button>
                    )}
                    {isHetznerInstance && (
                        <>
                            <button
                                type="button"
                                className={`text-btn ${instanceStatus === 'running' ? 'pause' : 'play'}`}
                                onClick={handlePauseResume}
                                disabled={isActionPending}
                            >
                                {instanceStatus === 'running' ? <><Pause size={14} /> Pause</> : <><Play size={14} /> Resume</>}
                            </button>
                            <button
                                type="button"
                                className="text-btn snapshot"
                                onClick={() => setShowSnapshotDialog(true)}
                                disabled={isActionPending}
                            >
                                <Camera size={14} /> Snapshot
                            </button>
                            <button
                                type="button"
                                className="text-btn delete"
                                onClick={() => setShowDeleteConfirm(true)}
                                disabled={isActionPending}
                            >
                                <Trash2 size={14} /> Delete
                            </button>
                        </>
                    )}
                    {!isLocalComputer && (
                        <button
                            type="button"
                            className="text-btn reconnect"
                            onClick={() => setupRemoteVNC()}
                            disabled={isConnecting}
                        >
                            {isConnecting ? <><RefreshCw size={14} className="spinning" /> Connecting...</> : <><RefreshCw size={14} /> Reconnect</>}
                        </button>
                    )}
                </div>
            </div>
            <div className="computer-panel-content">
                {vncUrl ? (
                    // Remote VNC mode - load remote noVNC interface directly
                    <div className={`vnc-container ${!controlEnabled ? 'control-disabled' : ''}`}>
                        {!controlEnabled && (
                            <div className="control-disabled-overlay">
                                <span>Control Disabled - Click to view only</span>
                            </div>
                        )}
                        <iframe
                            ref={iframeRef}
                            src={(() => {
                                try {
                                    const url = new URL(vncUrl);
                                    // Connect directly to noVNC on the returned URL (host:6080)
                                    const viewOnly = !controlEnabled ? '&view_only=true' : '';
                                    return `${url.origin}/vnc.html?autoconnect=true&resize=scale${viewOnly}`;
                                } catch {
                                    return `/vnc/?host=localhost&port=6080&path=websockify`;
                                }
                            })()}
                            className="vnc-iframe"
                            title="Remote Desktop"
                            allow="clipboard-read; clipboard-write"
                        />
                        {error && <div className="error-overlay">{error}</div>}
                    </div>
                ) : screenshot ? (
                    // Local screenshot mode
                    <div className="screen-container">
                        <img src={`data:image/png;base64,${screenshot}`} alt="Computer Screen" className="screen-image" />
                    </div>
                ) : (
                    // Loading/connecting state
                    <div className="no-screen">
                        <Monitor size={64} opacity={0.2} />
                        {isConnecting ? (
                            <>
                                <RefreshCw size={24} className="spinning" />
                                <p>{error || `Connecting to ${computerName}...`}</p>
                            </>
                        ) : error ? (
                            <>
                                <p className="error-text">{error}</p>
                                <button className="init-btn" onClick={() => isLocalComputer ? fetchScreenshot() : setupRemoteVNC()}>
                                    Retry Connection
                                </button>
                            </>
                        ) : (
                            <>
                                <RefreshCw size={24} className="spinning" />
                                <p>Loading {isLocalComputer ? 'screenshot' : 'remote desktop'}...</p>
                            </>
                        )}
                    </div>
                )}
            </div>

            {/* Snapshot Dialog */}
            {showSnapshotDialog && (
                <div className="dialog-overlay" onClick={() => setShowSnapshotDialog(false)}>
                    <div className="dialog" onClick={(e) => e.stopPropagation()}>
                        <h3>Create Snapshot</h3>
                        <p>Save the current state of this instance</p>
                        <input
                            type="text"
                            placeholder="Snapshot name..."
                            value={snapshotName}
                            onChange={(e) => setSnapshotName(e.target.value)}
                            autoFocus
                        />
                        <div className="dialog-actions">
                            <button type="button" className="cancel-btn" onClick={() => setShowSnapshotDialog(false)}>
                                Cancel
                            </button>
                            <button
                                type="button"
                                className="confirm-btn"
                                onClick={handleSnapshot}
                                disabled={!snapshotName.trim() || isActionPending}
                            >
                                {isActionPending ? 'Creating...' : 'Create Snapshot'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Dialog */}
            {showDeleteConfirm && (
                <div className="dialog-overlay" onClick={() => setShowDeleteConfirm(false)}>
                    <div className="dialog delete-dialog" onClick={(e) => e.stopPropagation()}>
                        <h3>Delete Instance?</h3>
                        <p>This will permanently delete <strong>{computerName}</strong> and all its data. This action cannot be undone.</p>
                        <div className="dialog-actions">
                            <button type="button" className="cancel-btn" onClick={() => setShowDeleteConfirm(false)}>
                                Cancel
                            </button>
                            <button
                                type="button"
                                className="delete-btn"
                                onClick={handleDelete}
                                disabled={isActionPending}
                            >
                                {isActionPending ? 'Deleting...' : 'Delete Instance'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

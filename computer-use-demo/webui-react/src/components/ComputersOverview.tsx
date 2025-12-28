import { useState, useEffect, useCallback } from 'react'
import { Monitor, Power, Trash2, Plus, RefreshCw, Cloud, MoreVertical, Pause, Unplug } from 'lucide-react'
import '../styles/ComputersOverview.css'

interface Computer {
  id: string
  name: string
  type: 'local' | 'remote' | 'hetzner'
  host?: string
  status: string
  platform_type: string
  vnc_port?: number
}

interface ComputerWithPreview extends Computer {
  screenshot?: string
  isLoading?: boolean
  error?: string
}

interface Props {
  onSelectComputer: (computerId: string) => void
}

export default function ComputersOverview({ onSelectComputer }: Props) {
  const [computers, setComputers] = useState<ComputerWithPreview[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hetznerInstances, setHetznerInstances] = useState<any[]>([])
  const [activeMenu, setActiveMenu] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  const fetchComputers = useCallback(async () => {
    try {
      const response = await fetch('/api/computers')
      if (response.ok) {
        const data = await response.json()
        setComputers(data)
        setError(null)
      }
    } catch (err) {
      console.error('Failed to fetch computers:', err)
      setError('Failed to load computers')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchLocalScreenshot = useCallback(async () => {
    try {
      const response = await fetch('/api/computer/screenshot')
      if (response.ok) {
        const data = await response.json()
        setComputers(prev => prev.map(c =>
          c.id === 'local' ? { ...c, screenshot: data.image } : c
        ))
      }
    } catch (err) {
      // Silent fail for screenshots
    }
  }, [])

  const fetchHetznerInstances = useCallback(async () => {
    try {
      const response = await fetch('/api/hetzner/instances')
      if (response.ok) {
        const data = await response.json()
        setHetznerInstances(data.instances || [])
      }
    } catch (err) {
      // Hetzner not available
    }
  }, [])

  const refreshAll = useCallback(async () => {
    await Promise.all([fetchComputers(), fetchHetznerInstances()])
  }, [fetchComputers, fetchHetznerInstances])

  useEffect(() => {
    fetchComputers()
    fetchHetznerInstances()

    // Refresh screenshots every 3 seconds
    const screenshotInterval = setInterval(fetchLocalScreenshot, 3000)
    // Refresh instances every 10 seconds
    const instanceInterval = setInterval(fetchHetznerInstances, 10000)

    return () => {
      clearInterval(screenshotInterval)
      clearInterval(instanceInterval)
    }
  }, [fetchComputers, fetchHetznerInstances, fetchLocalScreenshot])

  // Close menu when clicking outside
  useEffect(() => {
    const handleClick = () => setActiveMenu(null)
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

  const handleCreateInstance = async () => {
    setCreating(true)
    try {
      const response = await fetch('/api/hetzner/instances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `agent-${Date.now().toString(36)}`,
          server_type: 'cpx22',
          region: 'fsn1',
          cloud_init: true
        })
      })
      if (response.ok) {
        await refreshAll()
      } else {
        const err = await response.json()
        alert(err.detail || 'Failed to create instance')
      }
    } catch (err) {
      console.error('Failed to create instance:', err)
      alert('Failed to create instance')
    } finally {
      setCreating(false)
    }
  }

  const handleStartInstance = async (instanceId: number) => {
    try {
      await fetch(`/api/hetzner/instances/${instanceId}/start`, { method: 'POST' })
      await fetchHetznerInstances()
    } catch (err) {
      console.error('Failed to start instance:', err)
    }
  }

  const handleStopInstance = async (instanceId: number) => {
    try {
      await fetch(`/api/hetzner/instances/${instanceId}/stop`, { method: 'POST' })
      await fetchHetznerInstances()
    } catch (err) {
      console.error('Failed to stop instance:', err)
    }
  }

  const handleDeleteInstance = async (instanceId: number, name: string) => {
    if (!confirm(`Delete ${name}? This cannot be undone.`)) return
    try {
      await fetch(`/api/hetzner/instances/${instanceId}`, { method: 'DELETE' })
      await refreshAll()
    } catch (err) {
      console.error('Failed to delete instance:', err)
    }
  }

  if (loading) {
    return (
      <div className="computers-overview">
        <div className="overview-header">
          <h2>All Computers</h2>
        </div>
        <div className="loading-state">
          <RefreshCw size={32} className="spinning" />
          <p>Loading computers...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="computers-overview">
      <div className="overview-header">
        <h2>All Computers & Cloud Instances</h2>
        <div className="header-actions">
          <button
            className="create-btn"
            onClick={handleCreateInstance}
            disabled={creating}
            title="Create new cloud instance"
          >
            {creating ? <RefreshCw size={16} className="spinning" /> : <Plus size={16} />}
            New Instance
          </button>
          <button className="refresh-btn" onClick={refreshAll} title="Refresh">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="computers-grid">
        {/* Local Computer */}
        {computers.filter(c => c.id === 'local').map(computer => (
          <div
            key={computer.id}
            className="computer-card local"
            onClick={() => onSelectComputer('local')}
          >
            <div className="card-preview">
              {computer.screenshot ? (
                <img
                  src={`data:image/png;base64,${computer.screenshot}`}
                  alt={computer.name}
                  className="preview-image"
                />
              ) : (
                <div className="preview-placeholder">
                  <Monitor size={40} />
                </div>
              )}
              <div className={`status-dot ${computer.status}`} />
            </div>
            <div className="card-body">
              <h4>This Computer</h4>
              <span className="card-type">Local • {computer.platform_type}</span>
            </div>
          </div>
        ))}

        {/* Remote Computers (non-Hetzner) */}
        {computers.filter(c => c.type === 'remote' && !c.id.startsWith('hetzner-')).map(computer => (
          <div
            key={computer.id}
            className="computer-card remote"
            onClick={() => onSelectComputer(computer.id)}
          >
            <div className="card-preview">
              <div className="preview-placeholder">
                <Monitor size={40} />
              </div>
              <div className={`status-dot ${computer.status}`} />
            </div>
            <div className="card-body">
              <h4>{computer.name}</h4>
              <span className="card-type">{computer.host}</span>
            </div>
          </div>
        ))}

        {/* Hetzner Cloud Instances */}
        {hetznerInstances.map(instance => (
          <div
            key={instance.id}
            className={`computer-card cloud ${instance.status}`}
            onClick={() => onSelectComputer(`hetzner-${instance.id}`)}
          >
            <div className="card-preview cloud-preview">
              <Cloud size={40} />
              <div className={`status-dot ${instance.status}`} />
            </div>
            <div className="card-body">
              <h4>{instance.name}</h4>
              <span className="card-type">
                {instance.public_net?.ipv4?.ip || 'No IP'} • {instance.server_type?.name}
              </span>
              <span className={`status-badge ${instance.status}`}>
                {instance.status.toUpperCase()}
              </span>
            </div>

            {/* Action Menu Button */}
            <button
              className="menu-btn"
              onClick={(e) => {
                e.stopPropagation()
                setActiveMenu(activeMenu === `instance-${instance.id}` ? null : `instance-${instance.id}`)
              }}
            >
              <MoreVertical size={18} />
            </button>

            {/* Dropdown Menu */}
            {activeMenu === `instance-${instance.id}` && (
              <div className="dropdown-menu" onClick={(e) => e.stopPropagation()}>
                {instance.status === 'running' && (
                  <>
                    <button onClick={() => handleStopInstance(instance.id)}>
                      <Pause size={14} /> Pause
                    </button>
                    <button onClick={() => onSelectComputer(`hetzner-${instance.id}`)}>
                      <Monitor size={14} /> Connect
                    </button>
                  </>
                )}
                {instance.status === 'off' && (
                  <button onClick={() => handleStartInstance(instance.id)}>
                    <Power size={14} /> Start
                  </button>
                )}
                <button className="disconnect-btn" onClick={() => setActiveMenu(null)}>
                  <Unplug size={14} /> Disconnect
                </button>
                <button className="delete-btn" onClick={() => handleDeleteInstance(instance.id, instance.name)}>
                  <Trash2 size={14} /> Delete
                </button>
              </div>
            )}
          </div>
        ))}

        {/* Empty state */}
        {computers.length === 0 && hetznerInstances.length === 0 && (
          <div className="empty-state">
            <Monitor size={48} />
            <p>No computers found</p>
            <button className="create-btn" onClick={handleCreateInstance}>
              <Plus size={16} /> Create Cloud Instance
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

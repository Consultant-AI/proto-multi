import { useState, useEffect } from 'react'
import { Trash2, Plus, Check, AlertCircle, Eye, EyeOff } from 'lucide-react'
import '../styles/ComputerManagement.css'
import HetznerCostSummary from './HetznerCostSummary'
import HetznerInstanceList from './HetznerInstanceList'
import HetznerSnapshotList from './HetznerSnapshotList'
import HetznerQuickDeploy from './HetznerQuickDeploy'

interface Computer {
  id: string
  name: string
  type: 'local' | 'remote'
  host?: string
  port?: number
  username?: string
  ssh_key_path?: string
  vnc_port?: number
  api_port?: number
  status: 'online' | 'offline' | 'error' | 'unknown'
  error_msg?: string | null
}

interface HetznerInstance {
  id: number
  name: string
  status: string
  public_net?: {
    ipv4?: {
      ip: string
    }
  }
  server_type?: {
    name: string
  }
  cost_per_hour?: number
}

interface HetznerSnapshot {
  id: number
  description: string
  created: string
  image_size: number
  cost_per_month?: number
}

interface HetznerCosts {
  hourly: number
  daily: number
  monthly: number
  running_count: number
  stopped_count: number
  snapshot_count: number
  snapshot_cost: number
}

interface ComputerManagementProps {
  onComputersUpdate?: (computers: Computer[]) => void
}

export default function ComputerManagement({ onComputersUpdate }: ComputerManagementProps) {
  const [computers, setComputers] = useState<Computer[]>([])
  const [showAddForm, setShowAddForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    type: 'remote' as 'local' | 'remote',
    host: '',
    port: 22,
    username: '',
    ssh_key_path: '',
    vnc_port: 6080,
    api_port: 8000
  })

  // Hetzner Cloud state
  const [hetznerEnabled, setHetznerEnabled] = useState(false)
  const [showHetznerSection, setShowHetznerSection] = useState(false)
  const [hetznerInstances, setHetznerInstances] = useState<HetznerInstance[]>([])
  const [hetznerSnapshots, setHetznerSnapshots] = useState<HetznerSnapshot[]>([])
  const [hetznerCosts, setHetznerCosts] = useState<HetznerCosts | null>(null)
  const [hetznerLoading, setHetznerLoading] = useState(false)

  // Fetch computers on mount and check for Hetzner
  useEffect(() => {
    fetchComputers()
    checkHetznerAvailability()
  }, [])

  const fetchComputers = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/computers')
      if (response.ok) {
        const data = await response.json()
        setComputers(data)
        onComputersUpdate?.(data)
      }
    } catch (err) {
      setError('Failed to fetch computers')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddComputer = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/computers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setFormData({
          name: '',
          type: 'remote',
          host: '',
          port: 22,
          username: '',
          ssh_key_path: '',
          vnc_port: 6080,
          api_port: 8000
        })
        setShowAddForm(false)
        await fetchComputers()
      } else {
        setError('Failed to add computer')
      }
    } catch (err) {
      setError('Error adding computer')
      console.error(err)
    }
  }

  const handleDeleteComputer = async (computerId: string) => {
    if (computerId === 'local') {
      setError('Cannot delete local computer')
      return
    }

    if (!confirm('Are you sure you want to delete this computer?')) {
      return
    }

    try {
      const response = await fetch(`/api/computers/${computerId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        await fetchComputers()
      } else {
        setError('Failed to delete computer')
      }
    } catch (err) {
      setError('Error deleting computer')
      console.error(err)
    }
  }

  const handleTestConnection = async (computerId: string) => {
    try {
      const response = await fetch(`/api/computers/${computerId}/status`)
      if (response.ok) {
        await fetchComputers()
      }
    } catch (err) {
      console.error('Test connection failed:', err)
    }
  }

  // Hetzner Cloud functions
  const checkHetznerAvailability = async () => {
    try {
      const response = await fetch('/api/hetzner/costs')
      if (response.ok) {
        setHetznerEnabled(true)
        await fetchHetznerData()
      } else {
        setHetznerEnabled(false)
      }
    } catch (err) {
      setHetznerEnabled(false)
    }
  }

  const fetchHetznerData = async () => {
    try {
      setHetznerLoading(true)
      const [instancesRes, snapshotsRes, costsRes] = await Promise.all([
        fetch('/api/hetzner/instances'),
        fetch('/api/hetzner/snapshots'),
        fetch('/api/hetzner/costs')
      ])

      if (instancesRes.ok) {
        const data = await instancesRes.json()
        setHetznerInstances(data.instances || [])
      }

      if (snapshotsRes.ok) {
        const data = await snapshotsRes.json()
        setHetznerSnapshots(data.snapshots || [])
      }

      if (costsRes.ok) {
        const data = await costsRes.json()
        setHetznerCosts(data)
      }
    } catch (err) {
      console.error('Failed to fetch Hetzner data:', err)
    } finally {
      setHetznerLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    if (status === 'online') {
      return <Check size={16} color="#22c55e" />
    } else if (status === 'offline' || status === 'error') {
      return <AlertCircle size={16} color="#ef4444" />
    }
    return null
  }

  if (loading) {
    return <div className="computer-management">Loading computers...</div>
  }

  return (
    <div className="computer-management">
      <div className="computer-header">
        <h3>Registered Computers</h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="add-computer-btn"
        >
          <Plus size={18} /> Add Computer
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showAddForm && (
        <form onSubmit={handleAddComputer} className="add-computer-form">
          <div className="form-row">
            <input
              type="text"
              placeholder="Computer Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="form-row">
            <select
              value={formData.type}
              onChange={(e) =>
                setFormData({ ...formData, type: e.target.value as 'local' | 'remote' })
              }
            >
              <option value="local">Local</option>
              <option value="remote">Remote</option>
            </select>
          </div>

          {formData.type === 'remote' && (
            <>
              <div className="form-row">
                <input
                  type="text"
                  placeholder="Host/IP"
                  value={formData.host}
                  onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                  required
                />
                <input
                  type="number"
                  placeholder="Port"
                  value={formData.port}
                  onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                />
              </div>

              <div className="form-row">
                <input
                  type="text"
                  placeholder="Username"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                />
              </div>

              <div className="form-row">
                <input
                  type="text"
                  placeholder="SSH Key Path (e.g., ~/.ssh/id_rsa)"
                  value={formData.ssh_key_path}
                  onChange={(e) => setFormData({ ...formData, ssh_key_path: e.target.value })}
                />
              </div>

              <div className="form-row">
                <input
                  type="number"
                  placeholder="VNC Port"
                  value={formData.vnc_port}
                  onChange={(e) => setFormData({ ...formData, vnc_port: parseInt(e.target.value) })}
                />
                <input
                  type="number"
                  placeholder="API Port"
                  value={formData.api_port}
                  onChange={(e) => setFormData({ ...formData, api_port: parseInt(e.target.value) })}
                />
              </div>
            </>
          )}

          <div className="form-actions">
            <button type="submit" className="submit-btn">
              Add Computer
            </button>
            <button
              type="button"
              className="cancel-btn"
              onClick={() => setShowAddForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="computers-list">
        {computers.length === 0 ? (
          <div className="no-computers">No computers registered</div>
        ) : (
          computers.map((computer) => (
            <div key={computer.id} className="computer-item">
              <div className="computer-info">
                <div className="computer-name">
                  {getStatusIcon(computer.status)}
                  {computer.name}
                </div>
                <div className="computer-details">
                  {computer.type === 'remote' && (
                    <>
                      {computer.host && <span>{computer.host}:{computer.port || 22}</span>}
                      {computer.username && <span>@{computer.username}</span>}
                    </>
                  )}
                </div>
                <div className="computer-status">
                  {computer.status === 'online' && <span className="status-badge online">Online</span>}
                  {computer.status === 'offline' && <span className="status-badge offline">Offline</span>}
                  {computer.error_msg && <span className="error-text">{computer.error_msg}</span>}
                </div>
              </div>

              <div className="computer-actions">
                {computer.type === 'remote' && (
                  <button
                    className="test-btn"
                    onClick={() => handleTestConnection(computer.id)}
                    aria-label="Test SSH connection"
                  >
                    Test
                  </button>
                )}
                {computer.id !== 'local' && (
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteComputer(computer.id)}
                    data-tooltip="Delete computer"
                    aria-label="Delete computer"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Hetzner Cloud Section */}
      {hetznerEnabled && (
        <div className="hetzner-section">
          <div className="computer-header hetzner-header">
            <h3>Hetzner Cloud Servers</h3>
            <button
              type="button"
              onClick={() => setShowHetznerSection(!showHetznerSection)}
              className="toggle-hetzner-btn"
              aria-label={showHetznerSection ? 'Hide Hetzner section' : 'Show Hetzner section'}
            >
              {showHetznerSection ? <EyeOff size={18} /> : <Eye size={18} />}
              {showHetznerSection ? 'Hide' : 'Show'}
            </button>
          </div>

          {showHetznerSection && (
            <div className="hetzner-content">
              {hetznerLoading && <div className="loading">Loading Hetzner data...</div>}

              {!hetznerLoading && (
                <>
                  {hetznerCosts && <HetznerCostSummary costs={hetznerCosts} />}
                  <HetznerInstanceList
                    instances={hetznerInstances}
                    onRefresh={fetchHetznerData}
                  />
                  <HetznerSnapshotList
                    snapshots={hetznerSnapshots}
                    onRefresh={fetchHetznerData}
                  />
                  <HetznerQuickDeploy onDeploy={fetchHetznerData} />
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

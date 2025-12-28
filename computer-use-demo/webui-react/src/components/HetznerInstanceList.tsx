import { useState } from 'react'
import { Power, Trash2, Camera } from 'lucide-react'

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

interface Props {
  instances: HetznerInstance[]
  onRefresh: () => void
}

export default function HetznerInstanceList({ instances, onRefresh }: Props) {
  const [loading, setLoading] = useState<number | null>(null)

  const handleStart = async (instanceId: number) => {
    setLoading(instanceId)
    try {
      const response = await fetch(`/api/hetzner/instances/${instanceId}/start`, {
        method: 'POST'
      })
      if (response.ok) {
        onRefresh()
      }
    } catch (err) {
      console.error('Failed to start instance:', err)
    } finally {
      setLoading(null)
    }
  }

  const handleStop = async (instanceId: number) => {
    setLoading(instanceId)
    try {
      const response = await fetch(`/api/hetzner/instances/${instanceId}/stop`, {
        method: 'POST'
      })
      if (response.ok) {
        onRefresh()
      }
    } catch (err) {
      console.error('Failed to stop instance:', err)
    } finally {
      setLoading(null)
    }
  }

  const handleDelete = async (instanceId: number, name: string) => {
    if (!confirm(`Delete ${name}? This cannot be undone.`)) {
      return
    }

    setLoading(instanceId)
    try {
      const response = await fetch(`/api/hetzner/instances/${instanceId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        onRefresh()
      }
    } catch (err) {
      console.error('Failed to delete instance:', err)
    } finally {
      setLoading(null)
    }
  }

  const handleSnapshot = async (instanceId: number) => {
    const description = prompt('Snapshot description:', `snapshot-${new Date().toISOString()}`)
    if (!description) return

    setLoading(instanceId)
    try {
      const response = await fetch(`/api/hetzner/instances/${instanceId}/snapshot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description })
      })
      if (response.ok) {
        alert('Snapshot created successfully!')
        onRefresh()
      }
    } catch (err) {
      console.error('Failed to create snapshot:', err)
    } finally {
      setLoading(null)
    }
  }

  if (instances.length === 0) {
    return <div className="hetzner-empty">No Hetzner instances yet</div>
  }

  return (
    <div className="hetzner-instances">
      <h4>Instances ({instances.length})</h4>
      <div className="instances-table">
        {instances.map((instance) => (
          <div key={instance.id} className="instance-row">
            <div className="instance-info">
              <div className="instance-name">{instance.name}</div>
              <div className="instance-details">
                <span className={`status-badge ${instance.status}`}>
                  {instance.status.toUpperCase()}
                </span>
                {instance.public_net?.ipv4?.ip && (
                  <span className="instance-ip">{instance.public_net.ipv4.ip}</span>
                )}
                {instance.server_type && (
                  <span className="instance-type">{instance.server_type.name}</span>
                )}
                {instance.cost_per_hour && (
                  <span className="instance-cost">
                    €{instance.cost_per_hour.toFixed(4)}/hr
                  </span>
                )}
              </div>
            </div>

            <div className="instance-actions">
              {instance.status === 'running' && (
                <>
                  <button
                    onClick={() => handleSnapshot(instance.id)}
                    disabled={loading === instance.id}
                    className="action-btn snapshot-btn"
                    title="Create snapshot"
                  >
                    <Camera size={16} />
                  </button>
                  <button
                    onClick={() => handleStop(instance.id)}
                    disabled={loading === instance.id}
                    className="action-btn stop-btn"
                    title="Stop instance"
                  >
                    <Power size={16} />
                  </button>
                </>
              )}

              {instance.status === 'off' && (
                <button
                  onClick={() => handleStart(instance.id)}
                  disabled={loading === instance.id}
                  className="action-btn start-btn"
                  title="Start instance"
                >
                  <Power size={16} />
                </button>
              )}

              <button
                onClick={() => handleDelete(instance.id, instance.name)}
                disabled={loading === instance.id}
                className="action-btn delete-btn"
                title="Delete instance"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

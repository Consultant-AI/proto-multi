import { useState } from 'react'
import { Copy, Trash2 } from 'lucide-react'

interface HetznerSnapshot {
  id: number
  description: string
  created: string
  image_size: number
  cost_per_month?: number
}

interface Props {
  snapshots: HetznerSnapshot[]
  onRefresh: () => void
}

export default function HetznerSnapshotList({ snapshots, onRefresh }: Props) {
  const [loading, setLoading] = useState<number | null>(null)

  const handleClone = async (snapshotId: number) => {
    const name = prompt('New instance name:', `clone-${snapshotId}`)
    if (!name) return

    setLoading(snapshotId)
    try {
      const response = await fetch('/api/hetzner/instances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          snapshot_id: snapshotId,
          server_type: 'cpx22'
        })
      })
      if (response.ok) {
        alert('Cloning from snapshot... The instance will appear in the list when ready.')
        onRefresh()
      }
    } catch (err) {
      console.error('Failed to clone snapshot:', err)
    } finally {
      setLoading(null)
    }
  }

  const handleDelete = async (snapshotId: number, description: string) => {
    if (!confirm(`Delete snapshot "${description}"? This cannot be undone.`)) {
      return
    }

    setLoading(snapshotId)
    try {
      const response = await fetch(`/api/hetzner/snapshots/${snapshotId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        onRefresh()
      }
    } catch (err) {
      console.error('Failed to delete snapshot:', err)
    } finally {
      setLoading(null)
    }
  }

  const formatSize = (bytes: number) => {
    const gb = bytes / (1024 ** 3)
    return gb.toFixed(1)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  if (snapshots.length === 0) {
    return <div className="hetzner-empty">No snapshots yet</div>
  }

  return (
    <div className="hetzner-snapshots">
      <h4>Snapshots ({snapshots.length})</h4>
      <div className="snapshots-table">
        {snapshots.map((snapshot) => (
          <div key={snapshot.id} className="snapshot-row">
            <div className="snapshot-info">
              <div className="snapshot-description">{snapshot.description}</div>
              <div className="snapshot-details">
                <span className="snapshot-date">{formatDate(snapshot.created)}</span>
                <span className="snapshot-size">{formatSize(snapshot.image_size)} GB</span>
                {snapshot.cost_per_month && (
                  <span className="snapshot-cost">
                    €{snapshot.cost_per_month.toFixed(2)}/mo
                  </span>
                )}
              </div>
            </div>

            <div className="snapshot-actions">
              <button
                onClick={() => handleClone(snapshot.id)}
                disabled={loading === snapshot.id}
                className="action-btn clone-btn"
                data-tooltip="Clone from snapshot"
                aria-label="Clone from snapshot"
              >
                <Copy size={16} />
              </button>
              <button
                onClick={() => handleDelete(snapshot.id, snapshot.description)}
                disabled={loading === snapshot.id}
                className="action-btn delete-btn"
                data-tooltip="Delete snapshot"
                aria-label="Delete snapshot"
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

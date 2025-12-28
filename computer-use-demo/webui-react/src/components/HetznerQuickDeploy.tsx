import { useState } from 'react'
import { Zap } from 'lucide-react'

interface Props {
  onDeploy: () => void
}

const SERVER_TYPES = [
  { value: 'cpx22', label: 'CPX22 - 2 vCPU, 4GB RAM', cost: '€0.007/hr' },
  { value: 'cpx31', label: 'CPX31 - 4 vCPU, 8GB RAM', cost: '€0.0175/hr' },
  { value: 'cpx41', label: 'CPX41 - 8 vCPU, 16GB RAM', cost: '€0.0345/hr' }
]

export default function HetznerQuickDeploy({ onDeploy }: Props) {
  const [serverType, setServerType] = useState('cpx22')
  const [name, setName] = useState(`instance-${Math.floor(Math.random() * 10000)}`)
  const [loading, setLoading] = useState(false)

  const handleDeploy = async () => {
    if (!name.trim()) {
      alert('Please enter a name for the instance')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/hetzner/instances', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          server_type: serverType,
          location: 'nbg1'
        })
      })

      if (response.ok) {
        alert(
          `Instance "${name}" is being deployed!\n\nSetup time: 5-10 minutes\nThe instance will appear in the list once it's ready.`
        )
        setName(`instance-${Math.floor(Math.random() * 10000)}`)
        onDeploy()
      } else {
        const error = await response.json()
        alert(`Failed to deploy: ${error.detail || 'Unknown error'}`)
      }
    } catch (err) {
      console.error('Failed to deploy:', err)
      alert('Failed to deploy instance')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="hetzner-quick-deploy">
      <div className="deploy-header">
        <h4>
          <Zap size={18} /> One-Click Deploy
        </h4>
        <p>Launch a new Hetzner Cloud server with pre-configured Agent SDK</p>
      </div>

      <div className="deploy-form">
        <div className="form-group">
          <label htmlFor="instance-name">Instance Name</label>
          <input
            id="instance-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., my-agent-server"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="server-type">Server Type</label>
          <div className="server-types">
            {SERVER_TYPES.map((type) => (
              <label key={type.value} className="server-type-option">
                <input
                  type="radio"
                  value={type.value}
                  checked={serverType === type.value}
                  onChange={(e) => setServerType(e.target.value)}
                  disabled={loading}
                />
                <span className="option-label">
                  <span className="option-name">{type.label}</span>
                  <span className="option-cost">{type.cost}</span>
                </span>
              </label>
            ))}
          </div>
        </div>

        <button
          onClick={handleDeploy}
          disabled={loading}
          className="deploy-btn"
        >
          {loading ? 'Deploying...' : 'Deploy Now'}
        </button>

        <div className="deploy-info">
          <p>
            ℹ️ New instances are configured with:
          </p>
          <ul>
            <li>Agent SDK on port 8000</li>
            <li>VNC server on port 5900</li>
            <li>SSH access with your public key</li>
            <li>Auto-registered in computer list</li>
          </ul>
          <p className="deploy-time">
            ⏱️ Setup time: 5-10 minutes. You can monitor progress in the instances list.
          </p>
        </div>
      </div>
    </div>
  )
}

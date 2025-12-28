import { Euro } from 'lucide-react'

interface HetznerCost {
  hourly: number
  daily: number
  monthly: number
  running_count: number
  stopped_count: number
  snapshot_count: number
  snapshot_cost: number
}

interface Props {
  costs: HetznerCost
}

export default function HetznerCostSummary({ costs }: Props) {
  return (
    <div className="hetzner-cost-summary">
      <div className="cost-card">
        <div className="cost-icon">
          <Euro size={20} />
        </div>
        <span className="cost-label">Hourly</span>
        <span className="cost-value">€{costs.hourly.toFixed(4)}</span>
        <span className="cost-detail">{costs.running_count} running</span>
      </div>

      <div className="cost-card">
        <div className="cost-icon">
          <Euro size={20} />
        </div>
        <span className="cost-label">Daily</span>
        <span className="cost-value">€{costs.daily.toFixed(2)}</span>
        <span className="cost-detail">24-hour projection</span>
      </div>

      <div className="cost-card">
        <div className="cost-icon">
          <Euro size={20} />
        </div>
        <span className="cost-label">Monthly</span>
        <span className="cost-value">€{costs.monthly.toFixed(2)}</span>
        <span className="cost-detail">
          {costs.snapshot_count} snapshots (€{costs.snapshot_cost.toFixed(2)})
        </span>
      </div>

      <div className="cost-card">
        <div className="cost-icon">
          <Euro size={20} />
        </div>
        <span className="cost-label">Servers</span>
        <span className="cost-value">
          {costs.running_count + costs.stopped_count}
        </span>
        <span className="cost-detail">
          {costs.running_count} running, {costs.stopped_count} stopped
        </span>
      </div>
    </div>
  )
}

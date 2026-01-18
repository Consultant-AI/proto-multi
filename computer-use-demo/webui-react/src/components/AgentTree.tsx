import { useState, useEffect } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import '../styles/AgentTree.css'

interface Agent {
  id: string
  name: string
  description: string
  icon: string
  sub_agents?: Agent[]
}

interface AgentTreeProps {
  onSelectAgent: (agentId: string, agentName: string, agentIcon: string) => void
  selectedAgentId: string | null
}

function AgentTree({ onSelectAgent, selectedAgentId }: AgentTreeProps) {
  const [rootAgent, setRootAgent] = useState<Agent | null>(null)
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAgentTree()
  }, [])

  const fetchAgentTree = async () => {
    try {
      const response = await fetch('/api/agents/tree')
      const data = await response.json()

      // Get the root agent (CEO) from the first department
      const root = data.departments?.[0]?.agents?.[0]
      setRootAgent(root || null)

      // Auto-expand all agents by default
      const initialExpanded = new Set<string>()
      const collectAllIds = (agent: Agent) => {
        if (agent.sub_agents && agent.sub_agents.length > 0) {
          initialExpanded.add(agent.id)
          agent.sub_agents.forEach(collectAllIds)
        }
      }
      if (root) {
        collectAllIds(root)
        // Select CEO by default if nothing is selected
        if (!selectedAgentId) {
          onSelectAgent(root.id, root.name, root.icon)
        }
      }
      setExpandedAgents(initialExpanded)
    } catch (error) {
      console.error('Failed to fetch agent tree:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleAgent = (agentId: string) => {
    const newExpanded = new Set(expandedAgents)
    if (newExpanded.has(agentId)) {
      newExpanded.delete(agentId)
    } else {
      newExpanded.add(agentId)
    }
    setExpandedAgents(newExpanded)
  }

  const renderAgent = (agent: Agent, level: number = 0) => {
    const isExpanded = expandedAgents.has(agent.id)
    const hasSubAgents = agent.sub_agents && agent.sub_agents.length > 0

    return (
      <div key={agent.id}>
        <div
          className={`agent-item ${selectedAgentId === agent.id ? 'selected' : ''}`}
          style={{ paddingLeft: `${8 + level * 16}px` }}
        >
          {hasSubAgents ? (
            <span
              className="agent-expand-icon"
              onClick={(e) => {
                e.stopPropagation()
                toggleAgent(agent.id)
              }}
            >
              {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </span>
          ) : (
            <span className="agent-expand-spacer" />
          )}
          <div
            className="agent-content"
            onClick={() => onSelectAgent(agent.id, agent.name, agent.icon)}
            title={agent.description}
          >
            <span className="agent-icon">{agent.icon}</span>
            <span className="agent-name">{agent.name}</span>
          </div>
        </div>

        {hasSubAgents && isExpanded && (
          <div className="sub-agents-list">
            {agent.sub_agents!.map(subAgent => renderAgent(subAgent, level + 1))}
          </div>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="agent-tree-container">
        <div className="agent-tree-loading">Loading agents...</div>
      </div>
    )
  }

  if (!rootAgent) {
    return (
      <div className="agent-tree-container">
        <div className="agent-tree-loading">No agents available</div>
      </div>
    )
  }

  return (
    <div className="agent-tree-container">
      {renderAgent(rootAgent)}
    </div>
  )
}

export default AgentTree

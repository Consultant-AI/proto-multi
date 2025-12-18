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

interface Department {
  name: string
  icon: string
  agents: Agent[]
}

interface AgentTreeProps {
  onSelectAgent: (agentId: string, agentName: string, agentIcon: string) => void
  selectedAgentId: string | null
}

function AgentTree({ onSelectAgent, selectedAgentId }: AgentTreeProps) {
  const [departments, setDepartments] = useState<Department[]>([])
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAgentTree()
  }, [])

  const fetchAgentTree = async () => {
    try {
      const response = await fetch('/api/agents/tree')
      const data = await response.json()
      setDepartments(data.departments || [])
      // Auto-expand all agents by default
      const allAgentIds = new Set<string>()
      const collectAgentIds = (agents: Agent[]) => {
        agents.forEach(agent => {
          if (agent.sub_agents && agent.sub_agents.length > 0) {
            allAgentIds.add(agent.id)
            collectAgentIds(agent.sub_agents)
          }
        })
      }
      data.departments?.forEach((dept: Department) => {
        collectAgentIds(dept.agents)
      })
      setExpandedAgents(allAgentIds)
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
          style={{ marginLeft: `${level * 20}px` }}
          title={agent.description}
        >
          {hasSubAgents && (
            <span
              className="agent-expand-icon"
              onClick={(e) => {
                e.stopPropagation()
                toggleAgent(agent.id)
              }}
            >
              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </span>
          )}
          <div
            className="agent-content"
            onClick={() => onSelectAgent(agent.id, agent.name, agent.icon)}
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

  return (
    <div className="agent-tree-container">
      {departments.map(dept => (
        <div key={dept.name}>
          {dept.agents.map(agent => renderAgent(agent))}
        </div>
      ))}
    </div>
  )
}

export default AgentTree

import { Task } from '../types'
import '../styles/TaskViewer.css'

interface TaskViewerProps {
  task: Task
}

export default function TaskViewer({ task }: TaskViewerProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#00a884'
      case 'in_progress': return '#0088cc'
      case 'blocked': return '#ea4335'
      case 'pending': return '#8696a0'
      case 'cancelled': return '#666'
      default: return '#8696a0'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#ea4335'
      case 'high': return '#ff9800'
      case 'medium': return '#0088cc'
      case 'low': return '#8696a0'
      default: return '#8696a0'
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString()
  }

  return (
    <div className="task-viewer">
      <div className="task-header">
        <h1 className="task-title">{task.title}</h1>
        <div className="task-badges">
          <span
            className="task-badge status"
            style={{ background: getStatusColor(task.status) }}
          >
            {task.status.replace('_', ' ')}
          </span>
          <span
            className="task-badge priority"
            style={{ background: getPriorityColor(task.priority) }}
          >
            {task.priority}
          </span>
        </div>
      </div>

      <div className="task-section">
        <h3>Description</h3>
        <p className="task-description">{task.description || 'No description provided'}</p>
      </div>

      <div className="task-meta">
        <div className="meta-item">
          <span className="meta-label">ID:</span>
          <span className="meta-value">{task.id}</span>
        </div>
        {task.assignedAgent && (
          <div className="meta-item">
            <span className="meta-label">Assigned to:</span>
            <span className="meta-value">{task.assignedAgent}</span>
          </div>
        )}
        <div className="meta-item">
          <span className="meta-label">Created:</span>
          <span className="meta-value">{formatDate(task.createdAt)}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Updated:</span>
          <span className="meta-value">{formatDate(task.updatedAt)}</span>
        </div>
      </div>

      {task.children && task.children.length > 0 && (
        <div className="task-section">
          <h3>Subtasks ({task.children.length})</h3>
          <div className="subtasks-list">
            {task.children.map(subtask => (
              <div key={subtask.id} className="subtask-item">
                <div className="subtask-header">
                  <span
                    className="subtask-status"
                    style={{ background: getStatusColor(subtask.status) }}
                  />
                  <span className="subtask-title">{subtask.title}</span>
                </div>
                <span
                  className="subtask-priority"
                  style={{ color: getPriorityColor(subtask.priority) }}
                >
                  {subtask.priority}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

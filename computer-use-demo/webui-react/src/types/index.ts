export interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  size?: number;
  modified?: string;
}

export interface Project {
  name: string;
  path: string;
  totalTasks: number;
  statusCounts: {
    pending: number;
    in_progress: number;
    completed: number;
    blocked: number;
    cancelled: number;
  };
  createdAt: string;
  updatedAt: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignedAgent?: string;
  createdAt: string;
  updatedAt: string;
  parent_id?: string;
  children?: Task[];
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  images?: string[];
  agent_role?: string;  // Which specialist is responding (ceo, senior-developer, etc.)
  agent_name?: string;  // Display name of the agent
  label?: string;       // Message label (e.g., "Delegation Status", "Tool Result")
}

export interface Session {
  id: string;
  name: string;
  createdAt: string;
  lastActive: string;
  messages: Message[];
}

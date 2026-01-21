# Proto Technical Architecture

*For technical due diligence*

---

## Executive Summary

Proto is a multi-agent orchestration platform built on a modern stack: Python/FastAPI backend, React/Electron frontend, with deep integration into Anthropic's Claude API. The system coordinates specialist AI agents to execute complex business operations. Cross-platform (Mac + cloud Linux), with multi-computer orchestration on the roadmap.

**Key technical differentiators:**
- Cross-platform: runs on Mac + cloud Linux (Ubuntu instances with software installed)
- Hierarchical agent system with CEO-led delegation
- Multi-computer orchestration on roadmap (SSH tunneling and VNC infrastructure ready)
- GUI control via screenshot → analyze → mouse/keyboard actions—giving agents access to any tool a human can use on a computer (real computer use, not browser automation)
- Enterprise controls (optional)—Proto can run fully autonomously; optional approval gates, audit logs, kill switch

**On roadmap:**
- Self-improvement: evaluation per task, automatic code/playbook updates, continuous improvement
- Hybrid human delegation: AI hiring and managing humans for tasks that require it
- Multi-computer orchestration: multiple machines working together simultaneously

**Core Capabilities (Built Today):**
- **Project planning system**: For each project, creates planning files and task lists that agents follow and update—enables complex, multi-step projects to be broken down and executed systematically
- Programming (code generation, debugging, deployment)
- GUI control via screenshot → analyze → mouse/keyboard actions—giving agents access to any tool a human can use on a computer
- Integrations with third-party tools and APIs
- Playbooks for domain specialization and repeatable processes

**Self-Improvement Systems (On Roadmap):**
- Task evaluation—what worked, what failed, what to improve
- Automatic code/playbook updates based on evaluations
- Continuous improvement that makes each sub-agent more reliable over time
- Building reusable playbooks from successful patterns

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Electron + React)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │   Chat   │ │  Files   │ │ Terminal │ │ Computer │           │
│  │  Panel   │ │ Explorer │ │  Panel   │ │  Panel   │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │            │                  │
│       └────────────┴────────────┴────────────┘                  │
│                         │                                       │
│                    WebSocket                                    │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                         │                                       │
│  ┌──────────────────────┴──────────────────────┐               │
│  │              WebSocket Handler               │               │
│  │         (Real-time agent streaming)          │               │
│  └──────────────────────┬──────────────────────┘               │
│                         │                                       │
│  ┌──────────────────────┴──────────────────────┐               │
│  │              Agent Orchestrator              │               │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────────┐   │               │
│  │  │   CEO   │→│Directors│→│ Specialists │   │               │
│  │  │  Agent  │ │  (10)   │ │   (149+)    │   │               │
│  │  └─────────┘ └─────────┘ └─────────────┘   │               │
│  └──────────────────────┬──────────────────────┘               │
│                         │                                       │
│  ┌──────────────────────┴──────────────────────┐               │
│  │                Tool Layer                    │               │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────┐ │               │
│  │  │Computer│ │  Bash  │ │  Edit  │ │ Glob │ │               │
│  │  │  Tool  │ │  Tool  │ │  Tool  │ │ Tool │ │               │
│  │  └───┬────┘ └───┬────┘ └────────┘ └──────┘ │               │
│  └──────┼──────────┼───────────────────────────┘               │
│         │          │                                            │
└─────────┼──────────┼────────────────────────────────────────────┘
          │          │
┌─────────┼──────────┼────────────────────────────────────────────┐
│         │    COMPUTER CONTROL LAYER                             │
│         │          │                                            │
│  ┌──────┴──────┐ ┌─┴────────────┐ ┌───────────────┐            │
│  │    Local    │ │     SSH      │ │    Hetzner    │            │
│  │  Computer   │ │   Manager    │ │   Cloud API   │            │
│  │ (PyAutoGUI) │ │  (Tunnels)   │ │ (VM Provision)│            │
│  └──────┬──────┘ └──────┬───────┘ └───────┬───────┘            │
│         │               │                  │                    │
│  ┌──────┴───────────────┴──────────────────┴───────┐           │
│  │              Computer Registry                   │           │
│  │        (Tracks all connected machines)           │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Deep-Dive

### 1. Agent System

**Hierarchy:**
```
CEO
├── CTO (Technology)
│   ├── Tech Lead → Frontend, Backend, Mobile, Database Devs
│   ├── QA Manager → Bug Triage, Code Review
│   ├── DevOps → SRE, Monitoring, CI/CD
│   └── Security Lead → Access Control, Vulnerability Mgmt
├── CMO (Marketing)
│   ├── Marketing Director → Market Research, Brand
│   ├── Content Lead → SEO, Social Media, Creative
│   └── Growth Lead → Paid Acquisition, CRM
├── CPO (Product)
│   ├── Product Manager → Strategy, Discovery, Roadmap
│   ├── Design Lead → UX Research, UI Design
│   └── Experimentation → A/B Testing, Rollout
├── CFO (Finance)
│   └── Finance Manager → Budgeting, Bookkeeping
├── CRO (Revenue)
│   └── Sales Manager → Pipeline, Accounts
└── COO (Operations)
    ├── PMO Director → Scheduling, Admin
    └── Quality & Audit → Policy, Governance
```

**Agent Implementation:**
- Each agent has: system prompt, tool permissions, knowledge context
- Agents are defined in Python with specialized prompts
- CEO analyzes tasks, creates plans, delegates to appropriate specialists
- Specialists execute and return results up the chain

**Agents are continuously added** to cover all standard business functions

### 2. Cross-Platform & Cloud Infrastructure

**Built Today:**
- Proto runs on Mac locally (PyAutoGUI for mouse/keyboard, screenshot capture)
- Proto runs on cloud Linux (Ubuntu instances with software already installed)
- Cross-platform capability proven
- Qt WebEngine browser with Chrome DevTools Protocol (CDP)

**Cloud VM Management:**
- Hetzner Cloud API integration
- Automated instance provisioning
- Snapshot creation/restoration
- Cost tracking

**Infrastructure Ready (for multi-computer orchestration):**
- SSH tunneling via `SSHManager`
- VNC integration via `VNCTunnel`
- NoVNC in frontend for visual display
- Command execution over SSH
- Computer Registry for tracking connected machines

**On Roadmap:**
- Multi-computer orchestration—multiple machines working together simultaneously
- Message bus coordination between machines
- Parallel task execution across local and cloud

### 3. Tool Ecosystem

| Tool | Purpose | Implementation |
|------|---------|----------------|
| `ComputerTool` | Screenshot → analyze → mouse/keyboard actions | PyAutoGUI + Qt |
| `BashTool` | Shell command execution | Subprocess |
| `EditTool` | File editing (str_replace) | File I/O |
| `GlobTool` | File pattern matching | Glob library |
| `GrepTool` | Regex search in files | Ripgrep |
| `GitTool` | Git operations | Git CLI |
| `PythonExecutionTool` | Python script execution | Exec |
| `DelegateTaskTool` | Delegate to specialist | Agent routing |
| `PlanningTool` | Create/update plans | File + state |

### 4. Planning System

**Project Structure:**
```
projects/{name}/
├── .proto/planning/
│   ├── project_overview.md
│   ├── requirements.md
│   ├── technical_spec.md
│   ├── roadmap.md
│   ├── tasks.json
│   ├── agents/
│   └── knowledge/
└── [project files]
```

**Task Management:**
- Hierarchical task decomposition
- Status tracking (pending, in_progress, completed)
- Assignment to specific agents
- Complexity analysis

### 5. Frontend Architecture

**Stack:**
- React 18 + TypeScript
- Electron for desktop
- XTerm.js for terminal
- NoVNC for VNC viewing
- Vite for bundling

**Panels:**
- Chat: Agent conversation with streaming
- Files: Project file browser
- Terminal: Interactive shell
- Computer: VNC/screenshot viewer
- Browser: Embedded web browsing

**State Management:**
- WebSocket for real-time updates
- LocalStorage for persistence
- React context for global state

---

## Security & Controls

### Approval Gates

```python
GATED_ACTIONS = [
    "publish_*",      # External publication
    "payment_*",      # Financial transactions
    "account_*",      # Account changes
    "production_*",   # Production modifications
]

def execute_action(action):
    if requires_approval(action):
        return await_human_approval(action)
    return execute(action)
```

**Gated by default:**
- Publishing to social media, websites
- Spending money (API calls above threshold)
- Creating/modifying accounts
- Deploying to production

### Audit Log

Every action logged with:
```json
{
  "timestamp": "ISO8601",
  "agent_id": "marketing_specialist",
  "action_type": "file_edit",
  "action_details": {...},
  "diff": "...",
  "outcome": "success",
  "human_approval": null
}
```

### Kill Switch

- Single endpoint: `POST /api/emergency-stop`
- Terminates all agent tasks
- Closes all SSH connections
- Pauses VM operations
- Requires explicit restart

### Rate Limits

- Max actions per minute
- Max spend per session
- Configurable per action type

---

## API Integration

### Claude API

- Model: Claude Sonnet 4 / Claude Opus 4
- Extended thinking for complex reasoning
- Function calling for tool use
- Streaming for real-time output

**Prompt Caching:**
- System prompts cached
- Context reuse for efficiency
- Reduces latency and cost

### MCP (Model Context Protocol)

- Third-party tool integration
- Server discovery and registration
- Extensible tool ecosystem

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Agent response latency | 2-5s (depends on task) |
| Tool execution | <1s typical |
| SSH connection setup | 1-2s |
| VNC frame rate | 5-10 FPS |
| Concurrent agents | 10+ |
| Concurrent computers | 5+ tested |

---

## Deployment

**Current:**
- Local development (macOS)
- Manual start via CLI

**Production-ready:**
- Docker containerization supported
- Environment variable configuration
- Multi-instance capable

---

## Technology Stack Summary

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+, TypeScript |
| Backend | FastAPI, WebSocket |
| Frontend | React 18, Electron, Vite |
| AI | Anthropic Claude API |
| Terminal | XTerm.js |
| VNC | NoVNC |
| Browser | Qt WebEngine (CDP) |
| Cloud | Hetzner Cloud API |
| Remote | SSH (Paramiko), VNC |

---

## Codebase Statistics

- **Python files:** 328+
- **Main backend:** ~5,000 lines
- **Agent definitions:** 159 files
- **Frontend components:** 50+
- **Active development:** Yes (last commit: Jan 2026)

---

## Roadmap: Technical Milestones

**Near-term (1-3 months):**
- [ ] Multi-computer orchestration (multiple machines working together simultaneously)
- [ ] Improve reliability of multi-step task completion
- [ ] Add verification loops for task outcomes
- [ ] Expand audit logging granularity
- [ ] Performance optimization for parallel agents

**Medium-term (3-6 months):**
- [ ] Automated error recovery
- [ ] Self-healing agent restarts
- [ ] Reduce intervention rate by 50%
- [ ] Multi-region cloud support

**Long-term (6-12 months):**
- [ ] Fully autonomous operation mode
- [ ] Enhanced self-improvement: expand source code modification scope, deeper evaluation metrics
- [ ] Multi-business orchestration
- [ ] Horizontal scaling architecture

---

*Document version: 1.0*
*Last updated: [Date]*

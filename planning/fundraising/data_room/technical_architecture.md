# Proto Technical Architecture

*For technical due diligence*

---

## Executive Summary

Proto is a multi-agent orchestration platform built on a modern stack: Python/FastAPI backend, React/Electron frontend, with deep integration into Anthropic's Claude API. The system coordinates specialist AI agents to execute complex business operations. Cross-platform (Mac + cloud Linux), with multi-computer orchestration on the roadmap.

**Key technical differentiators:**
- Cross-platform: runs on Mac + cloud Linux (Ubuntu instances with software installed)
- Hierarchical agent system with CEO-led delegation
- Multi-computer orchestration on roadmap (SSH tunneling and VNC infrastructure ready)
- GUI control via screenshot → analyze → mouse/keyboard actions-giving agents access to any tool a human can use on a computer (real computer use, not browser automation)
- Enterprise controls (optional)-Proto can run fully autonomously; optional approval gates, audit logs, kill switch

**On roadmap:**
- Self-improvement: evaluation per task, automatic code/playbook updates, continuous improvement
- Hybrid human delegation: AI hiring and managing humans for tasks that require it
- Multi-computer orchestration: multiple machines working together simultaneously

**Core Capabilities (Built Today):**
- **Project planning system**: For each project, creates planning files and task lists that agents follow and update-enables complex, multi-step projects to be broken down and executed systematically
- Programming (code generation, debugging, deployment)
- GUI control via screenshot → analyze → mouse/keyboard actions-giving agents access to any tool a human can use on a computer
- Integrations with third-party tools and APIs
- Playbooks for domain specialization and repeatable processes

**Self-Improvement Systems (On Roadmap):**

Two-loop mechanism for continuous improvement:

**Loop 1: Real-Time (During Work)**
```
User Task → CEO Agent
    ↓
[SMART RETRIEVAL] Search all projects for relevant knowledge
    ↓
Task Execution by Specialist
    ↓
[SELF-HEALING RETRY LOOP]
├── Success? → Continue ✓
├── Fail? → Search knowledge for similar past failures
│   ├── Inject learnings into retry context
│   ├── Retry with improved approach (max 3 attempts)
│   └── Success after retry? → Capture recovery pattern
    ↓
[AUTO-CAPTURE] Extract patterns, tools used, duration, outcome
    ↓
Knowledge Stored → System improves immediately
```

**Loop 2: Background (Idle Time)**
```
CompanyOrchestrator Event Loop (every ~100 seconds)
    ↓
[LOG MINING] Analyze session logs for patterns
    ↓
[ERROR ANALYSIS] Identify recurring failures
    ↓
[KNOWLEDGE-BASED OPTIMIZATION]
├── 5+ failures? → Queue root cause analysis
├── 5+ patterns? → Queue component creation
└── Multiple projects? → Queue cross-project consolidation
    ↓
Improvement Tasks Queued → System improves continuously
```

**Key Capabilities:**
- Task evaluation-what worked, what failed, what to improve
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

**Peer-to-Peer Collaborative Network:**

This is NOT a strict hierarchy where only CEO delegates. It's a **peer-to-peer collaborative network**:
- ✅ Any agent can delegate to any other specialist
- ✅ Delegation chains can be unlimited depth (specialist → specialist → specialist...)
- ✅ No restrictions on who calls whom

**Example Delegation Chains:**
```
Backend Dev → "Need secure auth" → Security Engineer
Frontend Dev → "Need deployment" → DevOps Engineer
QA Engineer → "Found arch issue" → Senior Developer
Product Manager → "Need user research" → UX Designer
```

**Agent Implementation:**
- Each agent has: system prompt, tool permissions, knowledge context
- Agents are defined in Python with specialized prompts
- CEO analyzes tasks, creates plans, coordinates-but specialists work together fluidly
- Any specialist can call any other specialist when expertise is needed

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
- Multi-computer orchestration-multiple machines working together simultaneously
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

### Human Escalation (Last Resort Only)

Humans are called ONLY when legally, physically, or regulatorily impossible for AI:

**✅ WHEN TO CALL HUMAN (Exhaustive list):**

| Category | Examples |
|----------|----------|
| **Legal/Regulatory** | Sign legal contracts, company formation docs, tax filings, patents |
| **Financial** | Open bank accounts (KYC), sign loan docs, authorize large wires (>$10K) |
| **Physical World** | Mail notarized documents, hardware requiring presence, mandated in-person meetings |

**❌ NEVER CALL HUMAN FOR:**
- Writing code (system does this)
- Debugging (system does this)
- Customer support (system does this)
- Marketing content (system does this)
- Sales outreach (system does this)
- ANY computer-based task (system MUST do this)

This reinforces the autonomy goal-humans only when legally/physically required.

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

### Smart Model Selection (Cost Efficiency)

The system uses an intelligent **SmartSelector** that routes tasks to the optimal model with appropriate thinking budget:

**Philosophy: "Act Like Opus Is Always On"**
- The system BEHAVES like the smartest model is always running
- Only uses weaker models when the RESULT WOULD BE IDENTICAL
- Purely content-based selection (no hardcoded rules based on agent type)

**Model Hierarchy:**
| Model | Role | Usage |
|-------|------|-------|
| Opus 4.5 | CEO-level decisions | 20-30% of calls-strategy, architecture, planning |
| Sonnet 4.5 | Senior implementation | 50-60% of calls-complex features, debugging, judgment |
| Haiku 4.5 | Mechanical tasks | 20-30% of calls-file reads, searches, formatting |

**Selection Flow:**
```
Task → Haiku Classifier (~$0.001) → "Would Opus produce a DIFFERENT result?"
  │
  ├── If MECHANICAL (identical result) → Haiku
  └── If JUDGMENT NEEDED → Sonnet or Opus
```

**Cost Savings:** 70-90% reduction while maintaining quality
- Example project cost: ~$0.35 vs $2-5+ with naive approach

**Adaptive Escalation:**
- Start with recommended model, escalate only when needed
- Escalation path: Haiku → Sonnet → Opus
- Thinking budget: 0 → 4K → 10K → 31,999 tokens

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

## Complete Autonomous Business Loop

How Proto runs a business end-to-end:

```
1. PRODUCT DEVELOPMENT
   Global CEO → Assigns product to Computer → Local CEO builds with Agents
   → Code pushed to GitHub → Deployed via Vercel/AWS

2. CUSTOMER ACQUISITION
   Marketing Agent → Creates content → Posts via Social MCPs
   → SEO Agent optimizes → Leads captured in HubSpot

3. SALES
   Sales Agent → Sends outreach via SendGrid → Follows up
   → Demo scheduled → Contract sent → Human signs if needed

4. REVENUE
   Customer signs up → Stripe processes payment → Invoice generated
   → Revenue tracked → Metrics updated

5. SUPPORT
   Customer issue → Support Agent via Intercom → Resolves or escalates
   → Knowledge captured for future

6. SELF-IMPROVEMENT
   Metrics analyzed → Inefficiencies detected → Code modified
   → Tests pass → Deployed → Performance improves

7. HUMAN ESCALATION (RARE)
   Legal/regulatory block → Human notified → Human acts
   → System continues autonomously
```

This is the end state: Proto runs complete business operations with minimal human involvement.

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

*Document version: 1.1*
*Last updated: Jan 2026*

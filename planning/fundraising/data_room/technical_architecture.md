# Proto Technical Architecture

*For technical due diligence*

---

## Executive Summary

Proto is an autonomous multi-agent system designed to run complete software businesses without constant human supervision. The architecture coordinates 159 specialized AI agents across multiple computers, with a Global CEO (Opus 4.5) making company-wide strategic decisions while Local CEOs manage individual product teams.

**Key Technical Differentiators:**
- **Multi-Computer Orchestration**: Distribute work across Mac, cloud VMs, and remote servers
- **Peer-to-Peer Agent Network**: 159 specialists can delegate to each other without hierarchy constraints
- **Smart Model Selection**: Haiku classifier routes tasks to optimal model, reducing costs 70-90%
- **Self-Improvement Loop**: System automatically captures knowledge and improves over time
- **Production-Grade Reliability**: Circuit breakers, retry with backoff, checkpointing
- **GUI Control**: Screenshot → analyze → mouse/keyboard actions (real computer use, not browser automation)
- **Enterprise Controls**: Optional approval gates, audit logs, kill switch

---

## Core System Concepts

Each concept has a distinct role. Understanding these is key to how Proto works:

| Concept | Role | Responsibility | Analogy |
|---------|------|----------------|---------|
| **Subagents** | Workers | Execute specialized tasks delegated by lead agent | Employees on a team |
| **Tools** | Hands | Perform atomic actions (read file, run command, edit) | Hammers, screwdrivers |
| **MCP** | Universal Adapter | Connect to ANY external system (DB, browser, API) | USB ports |
| **Context** | Short-term Memory | Current conversation, what agent is working on NOW | Working memory |
| **Memory (CLAUDE.md)** | Long-term Memory | Persistent rules, conventions, patterns across sessions | Institutional knowledge |
| **Skills** | Expertise | Auto-activated specialized knowledge for specific tasks | Training/certifications |
| **Rules** | Guardrails | Enforce constraints and policies that ALL agents must follow | Safety protocols |
| **Hooks** | Automation Triggers | Execute shell commands on events (pre/post tool calls) | Circuit breakers |
| **Plugins** | Extensions | Packaged bundles of skills+tools+hooks for distribution | App store packages |
| **Thinking** | Deep Reasoning | Extended thinking for complex decisions (auto-detected) | "Sleep on it" |

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

## 7-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: PRESENTATION                                                                       │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  │ Web UI (FastAPI)     │ CLI Interface      │ REST API Endpoints                           │
│  │ • Dark theme         │ • Direct agent     │ • JSON responses                             │
│  │ • Real-time stream   │   invocation       │ • Webhook support                            │
│  │ • File management    │ • Script-friendly  │ • Status endpoints                           │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: ORCHESTRATION                                                                      │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────────────────────┐ │
│  │    GLOBAL CEO       │  │  COMPUTER POOL      │  │     WORK QUEUE SYSTEM               │ │
│  │    (Opus 4.5)       │  │  ORCHESTRATOR       │  │                                     │ │
│  │  + UltraThink       │  │                     │  │  Priority: CRITICAL > HIGH >        │ │
│  │                     │  │  • Task routing     │  │            MEDIUM > LOW             │ │
│  │  • Company-wide     │  │  • Load balancing   │  │  • Retry mechanism                  │ │
│  │    decisions        │  │  • Health checks    │  │  • State persistence                │ │
│  │  • Product          │  │  • Failover         │  │  • Scheduled execution              │ │
│  │    portfolio        │  │                     │  │                                     │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: AGENT LAYER (159 Agents: C-Suite → Directors → Specialists)                        │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                           PEER-TO-PEER MIXTURE OF EXPERTS                             │  │
│  │       ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐               │  │
│  │       │ Backend  │◄───►│ Frontend │◄───►│   QA     │◄───►│ Security │               │  │
│  │       │   Dev    │     │   Dev    │     │ Engineer │     │ Engineer │               │  │
│  │       └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘               │  │
│  │  KEY: Any agent can call ANY other agent! Not limited by hierarchy.                  │  │
│  └──────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: CONTEXT & MEMORY                                                                   │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  MEMORY HIERARCHY:                                                                          │
│  1. Enterprise: ~/.claude/CLAUDE.md          (Global conventions, team standards)          │
│  2. Project: .claude/CLAUDE.md               (Project-specific patterns, tech stack)       │
│  3. Directory: subdirs/.claude/CLAUDE.md     (Module-specific context)                     │
│  4. Session: in-memory + transcript.jsonl    (Current conversation)                        │
│  5. Knowledge Store: .proto/planning/        (Persistent learnings, patterns)              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: SKILLS, RULES & HOOKS                                                              │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────────────────┐ │
│  │   SKILLS (Expertise) │  │   RULES (Guardrails) │  │      HOOKS (Automation)          │ │
│  │  Auto-activated      │  │  Enforced policies   │  │  Deterministic triggers          │ │
│  │  • code-review       │  │  • No secrets        │  │  • PreToolCall: validate/block   │ │
│  │  • security-audit    │  │  • Always test       │  │  • PostToolCall: verify/notify   │ │
│  │  • test-writing      │  │  • OWASP compliance  │  │  • OnError: recover/alert        │ │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 6: TOOLS & MCP                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  BUILT-IN TOOLS (16+): Bash, Edit, Read, Write, Glob, Grep, Git, Computer, Screenshot      │
│  MCP SERVERS: Database (sqlite), Browser (playwright), Git (github), Email (sendgrid)      │
│  LSP INTEGRATION: Go-to-definition, Find references, Hover docs, Real-time type errors     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 7: INFRASTRUCTURE                                                                     │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   RELIABILITY     │  │    LOGGING       │  │   PERSISTENCE    │  │    MESSAGE BUS   │   │
│  │  • Circuit        │  │  4 Streams:      │  │  • .proto/       │  │  • Redis Pub/Sub │   │
│  │    breakers       │  │  - sessions      │  │    planning/     │  │  • Task assign   │   │
│  │  • Retry w/       │  │  - errors        │  │  • Knowledge     │  │  • Heartbeat     │   │
│  │    backoff        │  │  - tools         │  │    Store         │  │  • Knowledge     │   │
│  │  • Checkpoints    │  │  - system        │  │  • Git commits   │  │    sync          │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Multi-Computer Architecture

The "company factory" vision - Global CEO coordinates multiple computers:

```
                              ┌──────────────────┐
                              │   GLOBAL CEO     │ ◄─── Opus 4.5 + UltraThink
                              │   (Coordinator)  │      Sees ALL products
                              └────────┬─────────┘      Makes company-wide decisions
                                       │
     ┌─────────────────────────────────┼─────────────────────────────────┐
     ▼                                 ▼                                 ▼
 ┌──────────┐                    ┌──────────┐                    ┌──────────┐
 │ COMPUTER │                    │ COMPUTER │                    │ COMPUTER │
 │    1     │                    │    2     │                    │    N     │
 │  (Mac)   │                    │(Hetzner) │                    │ (Cloud)  │
 │          │                    │          │                    │          │
 │Product A │                    │Product B │                    │ Shared   │
 │  Team    │                    │  Team    │                    │  Infra   │
 └────┬─────┘                    └────┬─────┘                    └────┬─────┘
      │                               │                               │
      └───────────────────────────────┼───────────────────────────────┘
                                      │
                                      ▼
                        ┌────────────────────────┐
                        │     MESSAGE BUS        │
                        │     (Redis/NATS)       │
                        │                        │
                        │ • task_assign          │
                        │ • task_complete        │
                        │ • knowledge_sync       │
                        │ • heartbeat            │
                        └───────────┬────────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
               ┌───────────┐                ┌───────────┐
               │  SHARED   │                │  REVENUE  │
               │ KNOWLEDGE │                │  ENGINE   │
               │   HUB     │                │           │
               │           │                │ - Stripe  │
               │- Patterns │                │ - Metrics │
               │- Rules    │                │           │
               └───────────┘                └───────────┘
```

---

## Complete Request Flow

How a request moves through the entire system (9 steps):

```
USER REQUEST: "Build authentication system with tests"
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│ 1. SMART SELECTION (Haiku classifier ~$0.001)                          │
│    "Build auth system" → Strategic task → Opus 4.5 + 10K thinking     │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│ 2. CONTEXT - Load CLAUDE.md → "We use FastAPI + React + pytest"       │
│            - Knowledge Store → "JWT worked well in last project"      │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│ 3. SKILLS - "authentication" detected → loads auth-patterns SKILL.md  │
│           - "tests" detected → loads test-generation SKILL.md         │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│ 4. RULES - ✓ "no-secrets" rule loaded                                  │
│          - ✓ "always-test" rule loaded                                 │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│ 5. SUBAGENTS (Peer-to-peer delegation)                                 │
│    Backend Dev ──► Security Engineer ──► Frontend Dev ──► QA Engineer │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│ 6. TOOLS - PRE-HOOK (lint) → TOOL (Edit) → POST-HOOK (typecheck)      │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│ 7. MCP - playwright → Browser testing | github → Create PR            │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│ 8. KNOWLEDGE CAPTURE - Success patterns, decisions, failure lessons   │
└───────────────────────────────────┼───────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────┐
│ 9. RESULT - ✅ Auth built ✅ Tests passing ✅ Knowledge captured       │
└───────────────────────────────────┴───────────────────────────────────┘
```

---

## System Architecture (Detailed)

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
- Creating/modify=ing accounts
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

## Key Design Principles

1. **Intelligent Delegation**
   - CEO orchestrates, specialists execute
   - Any agent can call any specialist when needed (peer-to-peer)
   - Always delegate to the domain expert

2. **Dual-Structure Organization**
   - Planning/meta in `.proto/planning/`
   - Actual code in project root
   - Clear separation of concerns

3. **Hybrid Context Model**
   - Shared knowledge layer (CLAUDE.md, Knowledge Store, Rules)
   - Isolated execution contexts for subagents
   - Lead agent synthesizes summaries

4. **Deterministic + Intelligent**
   - Hooks for guaranteed automation
   - Skills for intelligent adaptation
   - Rules for policy enforcement

5. **Self-Improvement**
   - Automatic knowledge capture
   - Background pattern mining
   - Improvement task generation

6. **Fault Tolerance**
   - Circuit breakers on API calls
   - Retry with exponential backoff
   - Checkpointing for recovery

7. **Human as Last Resort**
   - System does everything it can autonomously
   - Humans only for legal/physical/regulatory blocks

---

## Reliability Patterns

Production-grade reliability built into the system:

**Circuit Breaker:**
```
CLOSED ────────► OPEN ────────► HALF_OPEN
  │                │                │
(normal)      (blocking)       (testing)
  │                │                │
5 failures      60s wait       1 success
in 1 min       cooldown        → CLOSED
```

**Retry with Exponential Backoff:**
```
Attempt 1 → Fail → Wait 1s
Attempt 2 → Fail → Wait 2s
Attempt 3 → Fail → Wait 4s (+ jitter)
Attempt 4 → Success!
```

| Pattern | Purpose |
|---------|---------|
| **Circuit Breaker** | Prevent cascade failures |
| **Retry with Backoff** | Handle transient errors |
| **Checkpointing** | State recovery after crashes |
| **Health Monitoring** | Service status tracking |
| **Dead Letter Queue** | Failed task handling |

---

## Directory Structure

```
projects/{project-name}/
├── .proto/planning/                 # Planning & Meta
│   ├── tasks.json                  # Task state & dependencies
│   ├── project_overview.md         # High-level description
│   ├── requirements.md             # Detailed requirements
│   ├── technical_spec.md           # Technical specifications
│   ├── agents/                     # Specialist-specific plans
│   └── knowledge/                  # KnowledgeStore
│       ├── technical_decision/
│       ├── learning/
│       ├── pattern/
│       └── best_practice/
└── [Actual Project Files]          # src/, docs/, tests/

~/.proto/                            # Global system state
├── daemon/work_queue.json          # Pending/active work
├── company/portfolio.json          # Products and assignments
└── computers/registry.json         # Known computers

.claude/                             # Project configuration
├── CLAUDE.md                       # Project conventions
├── hooks.json                      # Automation hooks
├── rules/                          # Policy guardrails
└── skills/                         # Auto-activated expertise
```

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

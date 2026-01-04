# Proto Multi-Agent System - Architecture Document

## Vision

**Goal**: Build an autonomous multi-agent system that can run a complete software business while continuously improving itself.

---

## System Overview

```
                    ┌─────────────────────────────────────────────────────────────────────────────────┐
                    │                        PROTO MULTI-AGENT SYSTEM                                  │
                    │              Enterprise-Grade Autonomous Business Platform                        │
                    │                                                                                   │
                    │   "Multiple computers, multiple agents, one unified business brain"              │
                    └─────────────────────────────────────────────────────────────────────────────────┘

                                                      │
                                                      ▼
    ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                    GLOBAL CEO ORCHESTRATOR                                        │
    │                                      (Opus 4.5 + UltraThink)                                      │
    │                                                                                                   │
    │    • Sees ALL computers and ALL products                                                         │
    │    • Makes company-wide strategic decisions                                                      │
    │    • Coordinates work across distributed computers                                               │
    │    • Manages product portfolio and resource allocation                                           │
    └─────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                      │
              ┌───────────────────────────────────────┼───────────────────────────────────────┐
              │                                       │                                       │
              ▼                                       ▼                                       ▼
    ┌──────────────────────┐              ┌──────────────────────┐              ┌──────────────────────┐
    │     COMPUTER 1       │              │     COMPUTER 2       │              │     COMPUTER N       │
    │     (Local Mac)      │              │   (Hetzner VM 1)     │              │      (Cloud)         │
    │                      │              │                      │              │                      │
    │  ┌────────────────┐  │              │  ┌────────────────┐  │              │  ┌────────────────┐  │
    │  │   LOCAL CEO    │  │              │  │   LOCAL CEO    │  │              │  │   LOCAL CEO    │  │
    │  │   (Sonnet)     │  │              │  │   (Sonnet)     │  │              │  │   (Sonnet)     │  │
    │  └───────┬────────┘  │              │  └───────┬────────┘  │              │  └───────┬────────┘  │
    │          │           │              │          │           │              │          │           │
    │  ┌───────┴────────┐  │              │  ┌───────┴────────┐  │              │  ┌───────┴────────┐  │
    │  │   20+ AGENTS   │  │              │  │   20+ AGENTS   │  │              │  │   20+ AGENTS   │  │
    │  │  Dev, QA, PM   │  │              │  │  Dev, QA, PM   │  │              │  │  DevOps, SRE   │  │
    │  │  Sales, Mktg   │  │              │  │  Sales, Mktg   │  │              │  │  Data, Admin   │  │
    │  └────────────────┘  │              │  └────────────────┘  │              │  └────────────────┘  │
    │                      │              │                      │              │                      │
    │  Assigned: Product A │              │  Assigned: Product B │              │  Assigned: Shared    │
    └──────────┬───────────┘              └──────────┬───────────┘              └──────────┬───────────┘
               │                                     │                                     │
               └─────────────────────────────────────┼─────────────────────────────────────┘
                                                     │
                                                     ▼
                              ┌─────────────────────────────────────────────────┐
                              │              SHARED INFRASTRUCTURE               │
                              │                                                  │
                              │   Message Bus │ Knowledge Hub │ Business Ops    │
                              │     (Redis)   │  (PostgreSQL) │   (Metrics)     │
                              └─────────────────────────────────────────────────┘
```

---

## Core Concept Roles

Each concept has a distinct role. Understanding these is key to using the system effectively:

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

---

## Agent Delegation Model

### Peer-to-Peer Collaborative Network

**This is NOT a hierarchical system where only CEO delegates.**

This is a **PEER-TO-PEER COLLABORATIVE NETWORK** where:
- ✅ **Any agent can delegate to any other specialist**
- ✅ Delegation chains can be unlimited depth (specialist → specialist → specialist...)
- ✅ No restrictions on who calls whom

### When ANY Agent Should Delegate

**✅ ALWAYS Delegate When:**
1. Task requires expertise outside your domain
2. Another specialist would do it better/faster
3. You're stuck or hitting errors repeatedly
4. Task spans multiple domains - delegate each part

**Example Peer Delegation Chains:**
```
Backend Dev → "Need secure auth" → Security Engineer
Frontend Dev → "Need deployment" → DevOps Engineer
QA Engineer → "Found arch issue" → Senior Developer
Product Manager → "Need user research" → UX Designer
```

### Sub-Agent Specialization Advantages

1. **Deep Domain Expertise** - Specialists have domain-specific prompts and context
2. **Better Tool Usage** - Each knows optimal tool combinations for their domain
3. **Quality & Efficiency** - Work faster in their domain, fewer iterations needed
4. **Knowledge Accumulation** - Build domain-specific patterns over time
5. **Parallel Execution** - Multiple specialists can work simultaneously

---

## When to Use What: Decision Guide

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              CONCEPT SELECTION FLOWCHART                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

"I need to do X"
       │
       ▼
┌──────────────────┐     YES    ┌─────────────────────────────────────────────────────────────┐
│ Is it a simple   │───────────►│   TOOL                                                       │
│ built-in action? │            │   Read, Write, Edit, Bash, Glob, Grep, Computer             │
└────────┬─────────┘            │   Use for: File operations, commands, GUI automation        │
         │ NO                   └─────────────────────────────────────────────────────────────┘
         ▼
┌──────────────────┐     YES    ┌─────────────────────────────────────────────────────────────┐
│ Need external    │───────────►│   MCP (Model Context Protocol)                               │
│ system/process?  │            │   Database, Browser, GitHub, Email, APIs                    │
└────────┬─────────┘            │   Use for: Connecting to external services                  │
         │ NO                   └─────────────────────────────────────────────────────────────┘
         ▼
┌──────────────────┐     YES    ┌─────────────────────────────────────────────────────────────┐
│ Need specialized │───────────►│   SUBAGENT                                                   │
│ expert (human)?  │            │   Security Engineer, QA, DevOps, UX Designer                │
└────────┬─────────┘            │   Use for: Domain expertise, different perspective          │
         │ NO                   └─────────────────────────────────────────────────────────────┘
         ▼
┌──────────────────┐     YES    ┌─────────────────────────────────────────────────────────────┐
│ Need knowledge   │───────────►│   SKILL                                                      │
│ auto-activated?  │            │   Code-review, Security-patterns, Test-writing              │
└────────┬─────────┘            │   Use for: HOW to think, not WHAT to do                     │
         │ NO                   └─────────────────────────────────────────────────────────────┘
         ▼
┌──────────────────┐     YES    ┌─────────────────────────────────────────────────────────────┐
│ Enforce a        │───────────►│   RULE                                                       │
│ constraint?      │            │   "Never commit secrets", "Always run tests"                │
└────────┬─────────┘            │   Use for: Policies ALL agents must follow                  │
         │ NO                   └─────────────────────────────────────────────────────────────┘
         ▼
┌──────────────────┐     YES    ┌─────────────────────────────────────────────────────────────┐
│ Auto-run on      │───────────►│   HOOK                                                       │
│ event/trigger?   │            │   Pre-edit lint, Post-commit tests, On-error notify         │
└────────┬─────────┘            │   Use for: Deterministic automation (WILL happen)           │
         │ NO                   └─────────────────────────────────────────────────────────────┘
         ▼
┌──────────────────┐     YES    ┌─────────────────────────────────────────────────────────────┐
│ Bundle for       │───────────►│   PLUGIN                                                     │
│ distribution?    │            │   Package of skills + MCPs + hooks + commands               │
└──────────────────┘            │   Use for: Sharing capabilities across projects/teams       │
                                └─────────────────────────────────────────────────────────────┘
```

---

## 7-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: PRESENTATION                                                                       │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│  │ Web UI (FastAPI)     │ CLI Interface      │ REST API Endpoints                           │
│  │ http://localhost:8000│ Terminal commands  │ Programmatic access                          │
│  │ • Dark theme         │ • Direct agent     │ • JSON responses                             │
│  │ • Real-time stream   │   invocation       │ • Webhook support                            │
│  │ • File management    │ • Script-friendly  │ • Status endpoints                           │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: ORCHESTRATION                                                                      │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                              │
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
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: AGENT LAYER (20+ Specialist Agents)                                                │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                           PEER-TO-PEER MIXTURE OF EXPERTS                             │  │
│  │                                                                                       │  │
│  │       ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐               │  │
│  │       │ Backend  │◄───►│ Frontend │◄───►│   QA     │◄───►│ Security │               │  │
│  │       │   Dev    │     │   Dev    │     │ Engineer │     │ Engineer │               │  │
│  │       └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘               │  │
│  │            │                │                │                │                      │  │
│  │       ┌────┼────────────────┼────────────────┼────────────────┼────┐                │  │
│  │       │    │                │                │                │    │                │  │
│  │       ▼    ▼                ▼                ▼                ▼    ▼                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │  DevOps  │  │    UX    │  │    PM    │  │   Data   │  │Marketing │             │  │
│  │  │ Engineer │  │ Designer │  │          │  │ Analyst  │  │ Director │             │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │  │
│  │                                                                                       │  │
│  │  KEY: Any agent can call ANY other agent! Not limited by hierarchy.                  │  │
│  └──────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                              │
│  ENGINEERING          PRODUCT           BUSINESS            OPERATIONS                      │
│  ────────────         ───────           ────────            ──────────                      │
│  • Sr Developer       • Product Mgr     • Marketing Dir     • HR Manager                    │
│  • Frontend Dev       • UX Designer     • Sales Director    • Finance Mgr                   │
│  • Backend Dev        • Strategist      • CS Manager        • Legal/Compliance              │
│  • Mobile Dev         • User Research   • Account Exec      • Biz Ops                       │
│  • DevOps Engineer                      • Sales Rep         • Admin                         │
│  • QA Engineer                          • Support Agent     • Data Analyst                  │
│  • Security Engineer                                        • Tech Writer                   │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: CONTEXT & MEMORY                                                                   │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                          HYBRID CONTEXT ARCHITECTURE                                 │   │
│  │                                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐  │   │
│  │  │                     SHARED KNOWLEDGE LAYER                                    │  │   │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐             │  │   │
│  │  │  │ CLAUDE.md  │  │ Knowledge  │  │  TASKS.md  │  │   RULES    │             │  │   │
│  │  │  │(conventions│  │   Store    │  │(work queue)│  │ (policies) │             │  │   │
│  │  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘             │  │   │
│  │  └──────────────────────────────────────────────────────────────────────────────┘  │   │
│  │         ▲  All agents read this persistent layer                                   │   │
│  │         │                                                                          │   │
│  │  ┌──────┴──────────────────────────────────────────────────────────────────────┐  │   │
│  │  │                 LEAD AGENT (Coordinator - sees all summaries)                │  │   │
│  │  └──────┬──────────────────────────────────────────────────────────────────────┘  │   │
│  │         │ delegates with: objective + context snippet                             │   │
│  │         ▼                                                                          │   │
│  │  ┌────────────┐   ┌────────────┐   ┌────────────┐                                │   │
│  │  │ Dev Agent  │   │ QA Agent   │   │DevOps Agent│  ISOLATED (full token budget)  │   │
│  │  │ (context)  │   │ (context)  │   │ (context)  │                                │   │
│  │  └────────────┘   └────────────┘   └────────────┘                                │   │
│  │         │              │              │                                           │   │
│  │         └──────────────┴──────────────┘  returns SUMMARY (not full context)      │   │
│  │                        ▼                                                          │   │
│  │               Lead Agent Synthesizes                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                              │
│  MEMORY HIERARCHY:                                                                          │
│  1. Enterprise: ~/.claude/CLAUDE.md          (Global conventions, team standards)          │
│  2. Project: .claude/CLAUDE.md               (Project-specific patterns, tech stack)       │
│  3. Directory: subdirs/.claude/CLAUDE.md     (Module-specific context)                     │
│  4. Session: in-memory + transcript.jsonl    (Current conversation)                        │
│  5. Knowledge Store: .proto/planning/        (Persistent learnings, patterns)              │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: SKILLS, RULES & HOOKS                                                              │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────────────────┐ │
│  │   SKILLS (Expertise) │  │   RULES (Guardrails) │  │      HOOKS (Automation)          │ │
│  │                      │  │                      │  │                                  │ │
│  │  Auto-activated      │  │  Enforced policies   │  │  Deterministic triggers          │ │
│  │  specialized         │  │  ALL agents follow   │  │  that WILL execute               │ │
│  │  knowledge           │  │                      │  │                                  │ │
│  │                      │  │  • No secrets        │  │  • PreToolCall: validate/block   │ │
│  │  • code-review       │  │  • Always test       │  │  • PostToolCall: verify/notify   │ │
│  │  • security-audit    │  │  • OWASP compliance  │  │  • OnError: recover/alert        │ │
│  │  • test-writing      │  │  • Code standards    │  │  • OnSessionStart/End            │ │
│  │  • deployment        │  │                      │  │                                  │ │
│  │                      │  │  Rule vs Memory:     │  │  Hook vs Rule:                   │ │
│  │  Skill = HOW to      │  │  CLAUDE.md = prefs   │  │  Rule = "Please do X"           │ │
│  │  think better        │  │  Rule = constraints  │  │  Hook = "X WILL happen"         │ │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 6: TOOLS & MCP                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                              BUILT-IN TOOLS (16+)                                    │   │
│  │                                                                                      │   │
│  │  CORE                  CODING              PLANNING           COMPUTER              │   │
│  │  ────                  ──────              ────────           ────────              │   │
│  │  • Bash                • Glob              • Planning         • Computer            │   │
│  │  • Edit                • Grep              • ReadPlanning     • LocalComputer       │   │
│  │  • Read                • Git               • Delegate         • Screenshot          │   │
│  │  • Write               • PythonExec        • Task                                   │   │
│  │                        • Todo              • Knowledge                              │   │
│  │                                            • Project                                │   │
│  │                                            • WorkQueue                              │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │  LocalComputerTool Actions (GUI Automation):                                         │   │
│  │  • Mouse: mouse_move, left/right/middle_click, double/triple_click, drag            │   │
│  │  • Keyboard: type (text), key (combos like "cmd+c"), hold_key                       │   │
│  │  • Scroll: scroll (up/down/left/right with amount)                                  │   │
│  │  • Screenshot: Capture screen state with automatic scaling                          │   │
│  │  • Wait: Pause execution for timing                                                 │   │
│  │                                                                                      │   │
│  │  Tool Usage Patterns:                                                               │   │
│  │  • File Search: Glob → Grep                                                         │   │
│  │  • Code Changes: Glob → Edit → Git                                                  │   │
│  │  • Project Start: Project → Planning → Task                                         │   │
│  │  • GUI Automation: LocalComputer (screenshot → analyze → click/type)                │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         MCP SERVER REGISTRY (External Systems)                       │   │
│  │                                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │ Database │  │ Browser  │  │ Git/VCS  │  │  Email   │  │  Custom  │             │   │
│  │  │ (sqlite) │  │(playwrt) │  │ (github) │  │(sendgrid)│  │   ...    │             │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                              LSP INTEGRATION (Code Intelligence)                     │   │
│  │                                                                                      │   │
│  │  Go-to-definition │ Find references │ Hover docs │ Real-time type errors           │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 7: INFRASTRUCTURE                                                                     │
│  ─────────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   RELIABILITY     │  │    LOGGING       │  │   PERSISTENCE    │  │    MESSAGE BUS   │   │
│  │                   │  │                  │  │                  │  │                  │   │
│  │  • Circuit        │  │  4 Streams:      │  │  • .proto/       │  │  • Redis Pub/Sub │   │
│  │    breakers       │  │  - sessions      │  │    planning/     │  │  • Task assign   │   │
│  │  • Retry w/       │  │  - errors        │  │  • Knowledge     │  │  • Heartbeat     │   │
│  │    backoff        │  │  - tools         │  │    Store         │  │  • Knowledge     │   │
│  │  • Checkpoints    │  │  - system        │  │  • Git commits   │  │    sync          │   │
│  │  • Health         │  │                  │  │                  │  │                  │   │
│  │    monitoring     │  │  JSONL format    │  │  Full recovery   │  │  Inter-computer  │   │
│  │                   │  │  Machine-readable│  │  capability      │  │  communication   │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Smart Model & Thinking Selection System

The system uses an intelligent **SmartSelector** that routes tasks to the optimal model with appropriate thinking budget. This replaces keyword-based detection with an LLM classifier.

### Philosophy: "Act Like Opus Is Always On"

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  CAPABILITY-FIRST SELECTION                                                                  │
│                                                                                              │
│  The system BEHAVES like the smartest model is always running.                              │
│  Only use weaker models when the RESULT WOULD BE IDENTICAL.                                 │
│                                                                                              │
│  NOT: "Use cheap model, hope it works"                                                      │
│  BUT: "Use strongest model needed for THIS specific task"                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Company Hierarchy Model

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              MODEL SELECTION HIERARCHY                                       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  OPUS 4.5 = CEO (20-30% of calls)                                                           │
│  ├── Makes all strategic decisions                                                          │
│  ├── Handles ambiguity and judgment calls                                                   │
│  ├── Reviews important work                                                                 │
│  └── Planning, architecture, strategy phases                                                │
│                                                                                              │
│  SONNET 4.5 = Senior Engineers (50-60% of calls)                                            │
│  ├── Implements complex features                                                            │
│  ├── Debugs difficult issues                                                                │
│  ├── Makes technical decisions within scope                                                 │
│  └── Quality-critical code, security considerations                                         │
│                                                                                              │
│  HAIKU 4.5 = Junior Staff / Automation (20-30% of calls)                                    │
│  ├── ONLY for truly mechanical tasks                                                        │
│  ├── File operations, searches, formatting                                                  │
│  ├── Never makes decisions                                                                  │
│  └── Result would be IDENTICAL to stronger models                                           │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### SmartSelector Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              SMART SELECTOR FLOW                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

  User Request
       │
       ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                   SMART SELECTOR (Haiku 4.5)                     │
  │                        Cost: ~$0.001                             │
  ├─────────────────────────────────────────────────────────────────┤
  │  Input: Actual task content (purely content-based)               │
  │  Output: {model, thinking_budget, task_type, reasoning}         │
  │                                                                  │
  │  Classifier asks: "Would Opus produce a DIFFERENT result?"       │
  │  - If task is MECHANICAL → Haiku (result identical)             │
  │  - If task needs JUDGMENT → Sonnet or Opus                       │
  └─────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                    EXECUTION ENGINE                              │
  │  Routes to selected model with optimal thinking budget           │
  └─────────────────────────────────────────────────────────────────┘
```

### Content-Based Selection (No Hardcoded Rules)

**IMPORTANT**: Selection is purely based on analyzing the actual task content. There are NO
hardcoded rules based on phase labels, agent types, or other metadata. The Haiku classifier
dynamically determines complexity by reading what the task actually asks for.

```
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │  Task Content Analysis                                                                  │
  ├────────────────────────────────────────────────────────────────────────────────────────┤
  │                                                                                         │
  │  MECHANICAL TASKS (Haiku) - Result would be IDENTICAL:                                 │
  │  • "Read file X and return contents"                                                   │
  │  • "List all .py files in directory"                                                   │
  │  • "Format this JSON"                                                                  │
  │  • "Run command: npm install"                                                          │
  │                                                                                         │
  │  JUDGMENT TASKS (Sonnet/Opus) - Result WOULD differ:                                   │
  │  • "Design a system architecture for..."                                               │
  │  • "Debug this complex race condition"                                                 │
  │  • "Plan how to implement this feature"                                                │
  │  • "Review this code for security issues"                                              │
  │                                                                                         │
  └────────────────────────────────────────────────────────────────────────────────────────┘

  The classifier reads the ACTUAL WORDS in the task to make decisions.
  A "specialist" doing strategic work gets Opus. A "CEO" doing file reads gets Haiku.
```

### Model Pricing (Dec 2024)

```
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │  Model          │  Model ID                    │  Input    │  Output  │  Thinking     │
  ├────────────────────────────────────────────────────────────────────────────────────────┤
  │  Haiku 4.5      │  claude-haiku-4-5-20251001   │  $1/MTok  │  $5/MTok │  Yes          │
  │  Sonnet 4.5     │  claude-sonnet-4-5-20250929  │  $3/MTok  │  $15/MTok│  Yes          │
  │  Opus 4.5       │  claude-opus-4-5-20251101    │  $5/MTok  │  $25/MTok│  Yes          │
  └────────────────────────────────────────────────────────────────────────────────────────┘

  Key insight: Haiku 4.5 now supports extended thinking!
```

### Adaptive Escalation

Start with recommended model, escalate only when needed:

```
  Initial Selection → Execute Task
       │
       ├── Success? → Done ✓
       │
       └── Low confidence or needs more reasoning?
            │
            ▼
       Escalate: Haiku → Sonnet → Opus
                 Thinking: 0 → 4K → 10K → 31,999
            │
            ▼
       Retry with stronger model
```

### Cost Comparison

```
  OLD (keyword-based with Sonnet for everything):
  ─────────────────────────────────────────────────
  "Build a chess game" → ULTRATHINK (31,999) on Sonnet
  CEO call: ~$0.55 (31K thinking tokens)
  Specialist call: ~$0.55 (also gets ULTRATHINK)
  Total per project: $2-5+

  NEW (SmartSelector with content-based selection):
  ─────────────────────────────────────────────────
  "Build a chess game"
    → Haiku classifier: ~$0.005
    → CEO planning: Opus + 10K thinking (~$0.25)
    → Specialist execution: Sonnet + 4K thinking (~$0.08)
    → Total: ~$0.35 per project

  SAVINGS: 70-90% while maintaining quality
```

---

## Module Reference

### Hooks System (`computer_use_demo/hooks/`)

Deterministic automation that executes shell commands on events:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HOOKS SYSTEM                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Hook Types:                                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  PreToolCall     │  Run BEFORE tool executes │ Can block/modify args       │
│  PostToolCall    │  Run AFTER tool completes │ Validate, notify            │
│  OnError         │  Run when tool fails      │ Recovery, alert             │
│  OnSessionStart  │  Run when session begins  │ Load context                │
│  OnSessionEnd    │  Run when session ends    │ Persist learnings           │
│                                                                              │
│  Configuration (.claude/hooks.json):                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  {                                                                          │
│    "hooks": [                                                               │
│      {                                                                      │
│        "event": "post_edit",                                               │
│        "command": "npm run lint -- {{file_path}}",                         │
│        "blocking": true                                                     │
│      }                                                                      │
│    ]                                                                        │
│  }                                                                          │
│                                                                              │
│  Template Variables:                                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  {{file_path}}   - File being operated on                                  │
│  {{tool_name}}   - Name of tool being called                               │
│  {{tool_args}}   - JSON of tool arguments                                  │
│  {{result}}      - Tool result (PostToolCall only)                         │
│  {{error}}       - Error message (OnError only)                            │
│                                                                              │
│  Files:                                                                     │
│  ├── types.py      - HookConfig, HookContext, HookResult, HookEvent        │
│  ├── registry.py   - HookRegistry for managing hooks                       │
│  ├── executor.py   - HookExecutor for running hooks                        │
│  └── template.py   - Variable substitution                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Reliability Module (`computer_use_demo/reliability/`)

Production-grade reliability patterns:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RELIABILITY PATTERNS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Circuit Breaker (circuit_breaker.py):                                      │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│       CLOSED ──────────► OPEN ──────────► HALF_OPEN                         │
│         │                  │                  │                              │
│    (normal)          (blocking)        (testing)                            │
│         │                  │                  │                              │
│    5 failures         60s wait          1 success                           │
│    in 1 min          cooldown         → CLOSED                              │
│                                                                              │
│  Retry with Backoff (retry.py):                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Attempt 1 → Fail → Wait 1s                                                 │
│  Attempt 2 → Fail → Wait 2s                                                 │
│  Attempt 3 → Fail → Wait 4s (+ jitter)                                      │
│  Attempt 4 → Success!                                                       │
│                                                                              │
│  Other Features:                                                            │
│  • Checkpointing (checkpoint.py) - State recovery                          │
│  • Health monitoring (health.py) - Service status                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Memory Module (`computer_use_demo/memory/`)

CLAUDE.md hierarchy for persistent conventions:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEMORY HIERARCHY                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Level 1: Enterprise   ~/.claude/CLAUDE.md                                  │
│           └── Global conventions, API keys, team standards                  │
│                         │                                                   │
│                         ▼ (merged)                                          │
│  Level 2: Project      .claude/CLAUDE.md                                    │
│           └── Project-specific patterns, tech stack                         │
│                         │                                                   │
│                         ▼ (merged)                                          │
│  Level 3: Directory    subdirs/.claude/CLAUDE.md                            │
│           └── Module-specific context                                       │
│                         │                                                   │
│                         ▼ (merged)                                          │
│  Final: Injected into agent system prompt                                   │
│                                                                              │
│  Files:                                                                     │
│  ├── claude_md.py   - CLAUDE.md parser                                     │
│  ├── hierarchy.py   - Enterprise → Project → Directory merge               │
│  ├── loader.py      - Auto-load on session start                           │
│  └── types.py       - MemoryFile, MemorySection, MergedMemory              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Skills Module (`computer_use_demo/skills/`)

Auto-activated specialized knowledge:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SKILLS SYSTEM                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Skill Structure (.claude/skills/):                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│  .claude/skills/                                                            │
│  ├── code-review/                                                           │
│  │   ├── SKILL.md          # Frontmatter + prompt                          │
│  │   ├── scripts/          # Automation scripts                            │
│  │   └── references/       # Checklists, patterns                          │
│  ├── security-audit/                                                        │
│  │   └── SKILL.md                                                          │
│  └── test-writing/                                                          │
│      └── SKILL.md                                                          │
│                                                                              │
│  SKILL.md Frontmatter:                                                      │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ---                                                                        │
│  name: code-review                                                          │
│  description: Expert code reviewer for security & quality                   │
│  triggers:                                                                  │
│    keywords: [review, audit, check]                                        │
│    file_patterns: ["*.py", "*.ts"]                                         │
│  allowed-tools: Read, Grep, Glob                                           │
│  model: claude-sonnet-4                                                    │
│  ---                                                                        │
│                                                                              │
│  Files:                                                                     │
│  ├── types.py     - Skill, SkillContext, SkillTrigger                      │
│  ├── loader.py    - Discover and load skills                               │
│  ├── matcher.py   - Match user message to relevant skills                  │
│  └── executor.py  - Format and inject skills                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Rules Module (`computer_use_demo/rules/`)

Enforced guardrails for all agents:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RULES SYSTEM                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Rule Structure (.claude/rules/):                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  .claude/rules/                                                             │
│  ├── security.md         # "Never commit secrets"                          │
│  └── quality.md          # "Always run tests before deploy"                │
│                                                                              │
│  Rule Example:                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  # Security Rules                                                           │
│                                                                              │
│  ## Config                                                                  │
│  - severity: error                                                          │
│  - scope: file                                                              │
│  - patterns: *.env, secrets.json                                           │
│                                                                              │
│  ## Conditions                                                              │
│  - Block commits of .env files                                             │
│  - Block files containing API keys                                         │
│                                                                              │
│  Files:                                                                     │
│  ├── types.py     - Rule, RuleCheckResult, RuleSeverity                    │
│  ├── loader.py    - Load rules from .claude/rules/                         │
│  └── enforcer.py  - Check actions against rules                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### MCP Module (`computer_use_demo/mcp/`)

Model Context Protocol for external systems:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MCP INTEGRATION                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Supported MCP Servers:                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • @modelcontextprotocol/server-filesystem  - Sandboxed file access        │
│  • @modelcontextprotocol/server-github      - GitHub API                   │
│  • playwright                               - Browser automation           │
│  • sqlite                                   - Database queries             │
│                                                                              │
│  Configuration (.claude/settings.json):                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  {                                                                          │
│    "mcpServers": {                                                          │
│      "playwright": {"command": "npx", "args": [...]},                      │
│      "database": {"command": "python", "args": [...]}                      │
│    }                                                                        │
│  }                                                                          │
│                                                                              │
│  Files:                                                                     │
│  ├── client.py          - MCP client implementation                        │
│  ├── server_registry.py - Manage MCP server processes                      │
│  ├── tool_wrapper.py    - Wrap MCP tools as native tools                   │
│  └── config.py          - Configuration loader                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Smart Selector Module (`computer_use_demo/smart_selector/`)

Intelligent model and thinking budget selection:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SMART SELECTOR MODULE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Files:                                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  models.py           │  Data structures: SelectionResult, ModelConfig,     │
│                      │  TaskType, Phase, model configurations              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  classifier_prompt.py│  Capability-first prompts for Haiku classifier      │
│                      │  "Would Opus produce a DIFFERENT result?"           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  selector.py         │  SmartSelector class - main entry point             │
│                      │  select_sync() and select() methods                 │
│                      │  PURELY CONTENT-BASED (no phase shortcuts)          │
│  ─────────────────────────────────────────────────────────────────────────  │
│  escalation.py       │  AdaptiveExecutor for retry with escalation         │
│                      │  Escalation: Haiku → Sonnet → Opus                  │
│                      │  Thinking: 0 → 4K → 10K → 31,999                    │
│                                                                              │
│  Integration Points:                                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • loop.py           │  SmartSelector called before API calls              │
│  • base_agent.py     │  Agents use SmartSelector (content-based)           │
│                                                                              │
│  Task Types (determined by analyzing task content):                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│  MECHANICAL (Haiku)  │  file_read, file_search, list_files, format_code   │
│  IMPLEMENTATION      │  simple_code, feature_impl, bug_fix, refactor      │
│  STRATEGIC (Opus)    │  planning, architecture, design, strategy, review  │
│                                                                              │
│  Selection Logic:                                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Haiku classifier reads actual task text and asks:                          │
│  "Would Opus produce a DIFFERENT result?"                                   │
│  If task is mechanical → Haiku (identical result)                           │
│  If task needs judgment → Sonnet/Opus (result would differ)                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Additional Modules

| Module | Location | Purpose |
|--------|----------|---------|
| **Smart Selector** | `smart_selector/` | Intelligent model + thinking selection (Haiku classifier) |
| **Thinking** | `thinking/` | ThinkingBudget enum, complexity detection (fallback) |
| **LSP** | `lsp/` | Language Server Protocol for code intelligence |
| **Messaging** | `messaging/` | Inter-computer communication (Redis Pub/Sub) |
| **Registry** | `registry/` | Computer registration and discovery |
| **Orchestrator** | `orchestrator/` | Global CEO, task scheduling |
| **Knowledge** | `knowledge/` | Distributed knowledge synchronization |
| **Plugins** | `plugins/` | Distributable capability bundles |
| **Marketplace** | `marketplace/` | 3rd party component discovery |
| **Business** | `business/` | Revenue, CRM, compliance engines |
| **Self-Improve** | `self_improve/` | Safe self-modification with rollback |
| **Human Pool** | `human_pool/` | Last-resort human escalation |

---

## Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                     HOW A REQUEST FLOWS THROUGH THE SYSTEM                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

USER REQUEST: "Build authentication system with tests"
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. SMART SELECTION (Haiku classifier ~$0.001)                                                │
│    SmartSelector analyzes task content: "Build auth system" → Strategic task                │
│    → Model: Opus 4.5 (needs strategic thinking)                                             │
│    → Thinking: 10,000 tokens (complex multi-step task)                                      │
│    → Reason: "Architecture + planning requires deep reasoning"                              │
└──────────────────────────────────────────────────────────────────────────────────────┬──────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. CONTEXT (Load shared memory)                                                              │
│    ├── CLAUDE.md → "We use FastAPI + React + pytest"                                        │
│    ├── Knowledge Store → "JWT worked well in last project"                                  │
│    └── TASKS.md → Current work queue                                                        │
└──────────────────────────────────────────────────────────────────────────────────────┬──────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. SKILLS (Auto-activate relevant expertise)                                                 │
│    "authentication" detected → loads auth-patterns SKILL.md                                 │
│    "tests" detected → loads test-generation SKILL.md                                        │
└──────────────────────────────────────────────────────────────────────────────────────┬──────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. RULES (Check constraints before execution)                                                │
│    ✓ "no-secrets" rule loaded                                                               │
│    ✓ "always-test" rule loaded                                                              │
└──────────────────────────────────────────────────────────────────────────────────────┬──────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. SUBAGENTS (Delegate to specialists - peer-to-peer)                                        │
│                                                                                              │
│    Each specialist's task analyzed by SmartSelector (content-based)                         │
│                                                                                              │
│       Backend Dev ──────────────► Security Engineer                                         │
│       "Implement JWT"             "Validate token logic"                                    │
│       (Sonnet, 4K thinking)       (Sonnet, 4K thinking)                                    │
│            │                           │                                                    │
│            └───────────┬───────────────┘                                                    │
│                        │                                                                     │
│                        ▼                                                                     │
│       Frontend Dev ◄───┼───► QA Engineer                                                    │
│       "Create login UI"│    "Write E2E tests"                                               │
│       (Sonnet, 4K)     │    (Sonnet, 4K)                                                    │
│                        ▼                                                                     │
│                   DevOps Engineer                                                           │
│                   "Set up deployment" (Sonnet, 4K)                                          │
└──────────────────────────────────────────────────────────────────────────────────────┬──────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 6. TOOLS (Execute with hooks)                                                                │
│                                                                                              │
│    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                  │
│    │ PRE-HOOK    │ → │   TOOL      │ → │ POST-HOOK   │ → │   LSP       │                  │
│    │ (lint check)│   │   (Edit)    │   │ (typecheck) │   │ (errors?)   │                  │
│    └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘                  │
│                                                               │                            │
│                                                 ┌─────────────┴─────────────┐              │
│                                                 │ Fix errors immediately     │              │
│                                                 └────────────────────────────┘              │
└──────────────────────────────────────────────────────────────────────────────────────┬──────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 7. MCP (Connect to external systems as needed)                                               │
│    • playwright MCP → Browser testing                                                       │
│    • github MCP → Create PR                                                                 │
│    • sqlite MCP → Database setup                                                            │
└──────────────────────────────────────────────────────────────────────────────────────┬──────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 8. KNOWLEDGE CAPTURE (Auto-capture learnings)                                                │
│    • Success patterns stored                                                                │
│    • Technical decisions recorded                                                           │
│    • Failure lessons captured                                                               │
└──────────────────────────────────────────────────────────────────────────────────────┬──────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 9. RESULT                                                                                    │
│    ✅ Authentication system built                                                           │
│    ✅ Tests passing                                                                         │
│    ✅ Knowledge captured for next time                                                      │
│    ✅ All agents saw what happened (shared context)                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Self-Improvement Loop

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              SELF-IMPROVEMENT MECHANISM                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                   DURING WORK (Real-time)                             │
└──────────────────────────────────────────────────────────────────────┘

User Task → CEO Agent
    │
    ▼
[SMART RETRIEVAL] Search all projects for relevant knowledge
    │
    ▼
Planning with Past Learnings Applied
    │
    ▼
Task Execution by Specialist
    │
    ▼
[SELF-HEALING RETRY LOOP]
    ├─ Task succeeds? → Continue ✓
    ├─ Task fails? → Analyze failure
    │   ├─ Search knowledge base for similar past failures
    │   ├─ Inject learnings into retry context
    │   ├─ Retry with improved approach (max 3 attempts)
    │   ├─ Success after retry? → Capture recovery pattern as best practice
    │   └─ Still failing? → Queue as "hard failure" for later (HIGH priority)
    │
    ▼
[AUTO-CAPTURE] Extract patterns, tools used, duration, outcome
    │
    ▼
Knowledge Stored in .proto/planning/{project}/knowledge/
    │
    ▼
[AUTO-IMPROVEMENT TASK GENERATION]
    ├─ Task failed? → Queue "Debug and fix" task (MEDIUM priority)
    ├─ Task took 10+ iterations? → Queue "Optimize process" task (MEDIUM priority)
    └─ Error seen 3+ times? → Queue "Systematic fix" task (HIGH priority)
    │
    ▼
System Executes Improvement Tasks → Gets Better Over Time


┌──────────────────────────────────────────────────────────────────────┐
│              BACKGROUND (Idle Time - every ~100 seconds)              │
└──────────────────────────────────────────────────────────────────────┘

CompanyOrchestrator Event Loop
    │
    ▼
[LOG MINING] Analyze session logs for tool patterns
    │
    ▼
[ERROR ANALYSIS] Identify recurring failures
    │
    ▼
[KNOWLEDGE-BASED OPTIMIZATION]
    ├─ Analyze each project's knowledge store
    ├─ 5+ failures? → Queue root cause analysis (MEDIUM priority)
    ├─ 5+ patterns? → Queue component creation (LOW priority)
    └─ Multiple projects? → Queue cross-project consolidation (LOW priority)
    │
    ▼
Project-Aware Improvement Tasks Queued → System Improves
    │
    └──────────────────────────► LOOP (continuous)
```

**Implementation Locations:**
- Auto-capture: [agents/base_agent.py:417-581](computer-use-demo/computer_use_demo/agents/base_agent.py#L417-L581)
- Knowledge retrieval: [agents/ceo_agent.py:398-532](computer-use-demo/computer_use_demo/agents/ceo_agent.py#L398-L532)
- Background improvement: [daemon/orchestrator.py:477-695](computer-use-demo/computer_use_demo/daemon/orchestrator.py#L477-L695)

---

## Multi-Computer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                       MULTI-COMPUTER SOFTWARE COMPANY                                        │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   GLOBAL CEO     │ ◄─── Opus 4.5 + UltraThink
                              │   (Coordinator)  │      Sees ALL products
                              └────────┬─────────┘      Makes company-wide decisions
                                       │
     ┌─────────────────────────────────┼─────────────────────────────────┐
     ▼                                 ▼                                 ▼
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │ PRODUCT  │   │ COMPUTER │   │ BUSINESS │   │  SELF-   │   │  HUMAN   │
 │ PORTFOLIO│   │   POOL   │   │   OPS    │   │ IMPROVE  │   │   POOL   │
 │ MANAGER  │   │ORCHESTR. │   │ MANAGER  │   │  ENGINE  │   │ MANAGER  │
 └──────────┘   └────┬─────┘   └──────────┘   └──────────┘   └──────────┘
                     │
      ┌──────────────┼──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
 ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
 │COMPUTER │   │COMPUTER │   │COMPUTER │   │COMPUTER │
 │   1     │   │   2     │   │   3     │   │   N     │
 │ (Mac)   │   │(Hetzner)│   │(Hetzner)│   │ (Cloud) │
 │         │   │         │   │         │   │         │
 │Product A│   │Product B│   │Product C│   │ Shared  │
 │  Team   │   │  Team   │   │  Team   │   │ Infra   │
 └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
      │             │             │             │
      └─────────────┴─────────────┴─────────────┘
                          │
                          ▼
            ┌────────────────────┐
            │   MESSAGE BUS      │
            │   (Redis/NATS)     │
            │                    │
            │ • task_assign      │
            │ • task_complete    │
            │ • knowledge_sync   │
            │ • heartbeat        │
            └─────────┬──────────┘
                      │
       ┌──────────────┴──────────────┐
       ▼                             ▼
┌─────────────┐            ┌─────────────┐
│  SHARED     │            │  REVENUE    │
│  KNOWLEDGE  │            │  ENGINE     │
│  HUB        │            │             │
│             │            │  - Stripe   │
│ - Patterns  │            │  - Invoices │
│ - Rules     │            │  - Metrics  │
│ - Skills    │            │             │
└─────────────┘            └─────────────┘
```

---

## Human-in-the-Loop Escalation

Humans are called ONLY when legally, physically, or regulatorily impossible for AI:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                         HUMAN POOL - LAST RESORT ONLY                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  ✅ WHEN TO CALL HUMAN (Exhaustive list - ONLY these cases):                                │
│  ──────────────────────────────────────────────────────────────────────────────────────────│
│                                                                                              │
│  LEGAL/REGULATORY (Cannot be done by AI)                                                    │
│  ├── Sign legal contracts (requires human legal signature)                                  │
│  ├── Company formation documents (LLC, Corp filings)                                        │
│  ├── Tax filings requiring human attestation                                                │
│  └── Patent/trademark applications (human inventor required)                                │
│                                                                                              │
│  FINANCIAL (Bank/regulatory requirements)                                                   │
│  ├── Open business bank accounts (KYC requires human)                                       │
│  ├── Sign loan documents                                                                    │
│  ├── Authorize large wire transfers (>$10K, bank policy)                                    │
│  └── Investor agreements (securities law)                                                   │
│                                                                                              │
│  PHYSICAL WORLD (Cannot be done remotely)                                                   │
│  ├── Mail physical documents (notarized, certified mail)                                    │
│  ├── Hardware purchases requiring physical presence                                         │
│  └── In-person meetings mandated by contract                                                │
│                                                                                              │
│  ❌ NEVER CALL HUMAN FOR:                                                                   │
│  ├── Writing code (system does this)                                                        │
│  ├── Debugging (system does this)                                                           │
│  ├── Customer support chat/email (system does this)                                         │
│  ├── Marketing content (system does this)                                                   │
│  ├── Sales outreach (system does this)                                                      │
│  └── ANY computer-based task (system MUST do this)                                          │
│                                                                                              │
│  Escalation Tool: HumanEscalationTool                                                       │
│  ──────────────────────────────────────────────────────────────────────────────────────────│
│  human_tool.request_human_action(                                                           │
│      task="Sign LLC formation documents for Proto AI Inc",                                  │
│      reason="LEGAL: Company formation requires human signature",                            │
│      deadline="2024-01-15",                                                                 │
│      priority="HIGH",                                                                       │
│      assigned_to="founder-1"                                                                │
│  )                                                                                          │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
projects/
└── {project-name}/                    # Example: "saas-company"
    │
    ├── .proto/                        # Planning & Meta (System Management)
    │   └── planning/
    │       ├── .project_metadata.json # Project info (name, description, tags)
    │       ├── tasks.json             # TaskManager state & dependencies
    │       │
    │       ├── project_overview.md    # High-level project description
    │       ├── requirements.md        # Detailed requirements
    │       ├── technical_spec.md      # Technical specifications
    │       ├── roadmap.md             # Project roadmap & milestones
    │       ├── knowledge_base.md      # Aggregated knowledge
    │       ├── decisions.md           # Technical decisions log
    │       │
    │       ├── agents/                # Specialist-specific plans
    │       │   ├── senior-developer_plan.md
    │       │   ├── frontend-developer_plan.md
    │       │   └── ...
    │       │
    │       └── knowledge/             # KnowledgeStore
    │           ├── index.json
    │           ├── technical_decision/
    │           ├── learning/
    │           ├── pattern/
    │           └── best_practice/
    │
    └── [Actual Project Files]         # Standard project structure
        ├── src/
        ├── docs/
        ├── tests/
        └── ...

~/.proto/                              # Global system state
├── daemon/
│   ├── work_queue.json               # Pending/active work items
│   └── orchestrator_state.json       # Runtime state
├── company/
│   ├── portfolio.json                # Products and assignments
│   ├── humans/                       # Human pool configuration
│   └── business/                     # Financial, CRM data
└── computers/
    ├── registry.json                 # Known computers
    └── health/                       # Health status per computer

.claude/                              # Project configuration
├── CLAUDE.md                         # Project conventions (memory)
├── hooks.json                        # Automation hooks
├── settings.json                     # MCP, LSP configuration
├── rules/                            # Policy guardrails
│   ├── security.md
│   └── quality.md
├── skills/                           # Auto-activated expertise
│   ├── code-review/
│   └── security-audit/
└── plugins/                          # Installed plugins

logs/                                 # System logging
├── proto_sessions.jsonl              # Session events
├── proto_errors.jsonl                # Error tracking
├── proto_tools.jsonl                 # Tool invocations
└── proto_system.jsonl                # System events
```

---

## Business Operations

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE AUTONOMOUS BUSINESS LOOP                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

  1. PRODUCT DEVELOPMENT
     ─────────────────────────────────────────────────────────────────────────────────────────
     Global CEO → Assigns product to Computer → Local CEO builds with Agents
     → Code pushed to GitHub → Deployed via Vercel/AWS

  2. CUSTOMER ACQUISITION
     ─────────────────────────────────────────────────────────────────────────────────────────
     Marketing Agent → Creates content → Posts via Social MCPs
     → SEO Agent optimizes → Leads captured in HubSpot

  3. SALES
     ─────────────────────────────────────────────────────────────────────────────────────────
     Sales Agent → Sends outreach via SendGrid → Follows up
     → Demo scheduled → Contract sent → Human signs if needed

  4. REVENUE
     ─────────────────────────────────────────────────────────────────────────────────────────
     Customer signs up → Stripe processes payment → Invoice generated
     → Revenue tracked → Metrics updated

  5. SUPPORT
     ─────────────────────────────────────────────────────────────────────────────────────────
     Customer issue → Support Agent via Intercom → Resolves or escalates
     → Knowledge captured for future

  6. SELF-IMPROVEMENT
     ─────────────────────────────────────────────────────────────────────────────────────────
     Metrics analyzed → Inefficiencies detected → Code modified
     → Tests pass → Deployed → Performance improves

  7. HUMAN ESCALATION (RARE)
     ─────────────────────────────────────────────────────────────────────────────────────────
     Legal/regulatory block → Human notified → Human acts
     → System continues autonomously
```

---

## Project Lifecycle Example

**Building a SaaS App (Condensed Flow):**

1. **User Request** → "Build SaaS with auth and real-time updates"
2. **CEO Analysis** → Complexity: very_complex → Creates planning docs
3. **CEO Delegates**:
   - Product Manager → Define requirements
   - Backend Developer → Implement JWT auth
   - Frontend Developer → Create React UI
   - DevOps Engineer → Set up deployment
4. **Specialists Execute** → Each reads planning context, uses appropriate tools
5. **Knowledge Captured** → Decisions stored in `.proto/planning/knowledge/`
6. **Result** → Working app + knowledge for future projects

**Key Takeaways:**
- ✅ CEO orchestrated, never coded directly
- ✅ Each specialist worked in their domain
- ✅ Planning (.proto/) separate from code
- ✅ All decisions documented in knowledge base

---

## Training & Verification Systems

**Training System** (`computer_use_demo/training/`):
- Test suites for agent validation (QA, DevOps, Senior Dev, Sales, etc.)
- Training data storage in `.proto/training/`
- Agent performance evaluation

**Verification System** (`computer_use_demo/verification/`):
- ScreenshotAnalyzer: Analyze GUI state from screenshots
- StructuralChecker: Verify code structure & correctness
- FeedbackLoop: Iterative improvement cycles

---

## Key Design Principles

1. **Intelligent Delegation**
   - CEO orchestrates, specialists execute
   - Any agent can call any specialist when needed
   - Not constrained by organizational hierarchy
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
   - Multi-computer redundancy

7. **Human as Last Resort**
   - System does everything it can autonomously
   - Humans only for legal/physical/regulatory blocks
   - Clear escalation protocols

---

## Deployment

### Hetzner Cloud (Remote Computers)

```bash
export HETZNER_API_TOKEN=your-token
export ANTHROPIC_API_KEY=your-key
cd computer-use-demo/hetzner-deploy
pip3 install -r requirements.txt
./deploy.sh
```

**Specifications**:
- Server: Hetzner CX22 (2 vCPU, 4GB RAM)
- Cost: ~€5/month if 24/7, €0/hr when paused
- Snapshot-based cloning for fast deployment

### Control Dashboard

```bash
python3 control_panel.py
# Access: http://localhost:5500
```

---

*Last updated: 2025-12-31 - Added Smart Model & Thinking Selection System*

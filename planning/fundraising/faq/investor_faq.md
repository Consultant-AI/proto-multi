# Proto Investor FAQ

## The Vision

### What is Proto?
Proto is a multi-agent orchestration platform that coordinates specialist AI agents across multiple computers to execute **any complex computer-based work** autonomously. Our goal: build the infrastructure for autonomous companies.

### What makes this different from ChatGPT/Claude/other AI tools?
Most AI tools are designed for human augmentation—one human, one AI assistant, task by task. Proto is designed for *autonomous operation*:

- **Multi-agent**: Specialist agents working together (CEO → specialists)
- **Multi-computer**: Controls local machines + cloud VMs simultaneously
- **GUI control**: Takes screenshots, moves mouse, types keyboard—operates any desktop application
- **Multi-step**: Executes complex processes end-to-end, not single tasks
- **Self-improving**: Learns from failures, builds playbooks, optimizes approaches
- **Any domain**: Not limited to one type of work—can do development, content, trading, operations, anything computer-based

ChatGPT can help you write code. Proto can build, launch, and run an entire software business.

### Why "autonomous company factory"?
Once AI agents can reliably execute complex business processes without constant supervision, the playbook changes completely:

1. Identify profitable, automatable business opportunities
2. Deploy Proto to run those businesses
3. Compound profits into more businesses
4. System improves with each business it runs

The end state isn't one product—it's the ability to manufacture unlimited businesses. A factory, not a single company.

### What businesses will Proto run?
**Whatever works fastest.** Proto will experiment across multiple paths:

| Business Type | Examples |
|--------------|----------|
| AI/SaaS Products | Build and launch software |
| Content & Media | Generate content at scale |
| Agency Services | Marketing, development, automation |
| Domain-Specific Agents | Sell specialized AI agents for specific industries |
| Freelance Operations | Execute work on Upwork, Fiverr |
| E-commerce | Dropshipping, digital products |
| Trading & Arbitrage | Algorithmic trading, market inefficiencies |
| Human-in-Loop Platforms | Coordinate humans for tasks AI can't do |

**The key insight:** Any business that would hire people—Proto hires AI (and humans when needed). Not just service businesses—any computer-based business that relies on human labor can be run by Proto.

The scope expands as AI capabilities improve. Today's impossible becomes tomorrow's automated.

The first business is proof of concept. The goal is a portfolio.

### Why do you think we're close to that threshold?
Four things have converged:

1. **Model capability**: Frontier models can reason through complex, multi-step problems
2. **Computer use**: Screenshot → analyze → action loops work reliably
3. **Tooling maturity**: MCP, function calling, and agent frameworks are production-ready
4. **Massive attention and resources**: AI agents are where the industry is focused—billions in investment, top talent, research breakthroughs happening monthly

What's missing is reliability at scale. That's an engineering problem, not a research breakthrough. And with this much attention and resources flowing into the space, the reliability problem will be solved soon.

### Aren't there already many AI agents? What's the gap?

Current AI agents are **domain-specific silos**:
- Coding agents (Devin, Cursor, Replit, Claude Code, OpenAI Codex) — only write code
- Agent-first IDEs (Google Antigravity) — focused on developer workflows
- Sales agents (Lindy, 11x, Salesforce Agentforce) — only handle sales workflows
- Support agents (Zendesk AI, Intercom, Ada) — only answer tickets
- Marketing agents — only create content
- Open source (AutoGPT, SuperAGI, AgentGPT, CrewAI, LangGraph, Agent-S) — frameworks, not businesses

**What's missing:**
- **Cross-domain coordination**: No one combines coding + marketing + sales + operations into one system
- **Self-improvement**: Almost no agents learn from their failures and get better over time
- **Full autonomy goal**: Everyone else builds copilots (human augmentation), not autonomous operations

Proto is designed from the ground up to do all domains, self-improve, and work toward full autonomy.

### What about OpenAI/Anthropic—won't they just build this?

They **could** build this—but they haven't. Their business model is selling API access to millions of developers, not running businesses themselves.

**The first-mover advantage is real:**
- Once Proto starts self-improving, it compounds—each business makes the system better
- By the time labs pivot (if they do), Proto will have playbooks, data, and running businesses
- They'd be starting from zero while we're generating revenue

Different game, different incentives. They want to be the platform. We want to own the gold mines.

---

## The Product

### How does the agent system work?
Proto has **specialist agents** organized like a company:

- **C-Suite**: CEO, CTO, CMO, CFO—strategic coordination
- **Directors**: Product, Engineering, Marketing, Sales—functional leadership
- **Specialists**: Developers, writers, analysts, traders, designers—execution

Each agent has optimized system prompts, tools, and knowledge for its domain. The system is a **peer-to-peer collaborative network**—any agent can delegate to any other specialist when expertise is needed.

The CEO analyzes incoming tasks, creates plans, and coordinates—but specialists work together fluidly, calling each other as needed.

### How does multi-computer control work?
Proto controls computers through a unified interface:

- **Local control**: Mouse, keyboard, screenshots via direct automation
- **Remote servers**: SSH for terminal, VNC for visual desktop control
- **Cloud VMs**: Hetzner instances provisioned on demand
- **Message bus**: Coordinates all computers, routes tasks, syncs knowledge

All computers appear in one interface. Proto can run analysis on a cloud VM while building code locally while managing tasks on another remote machine—all coordinated.

### What can Proto actually do today?

**Real Computer Use** (not simulated):
- **File operations**: Read, write, edit, search any file type
- **Terminal**: Execute commands, run scripts, manage systems
- **GUI automation**: Screenshots → analyze → mouse/keyboard actions
- **Browser control**: Web-based tasks through real browser automation
- **Multi-computer**: Parallel execution across local and cloud machines

**Self-Improvement** (built in):
- Auto-captures learnings from every task execution
- Retrieves relevant past knowledge for new work
- Builds reusable playbooks from successful patterns
- Generates improvement tasks from repeated failures

**Hybrid Models:**
When full automation isn't possible, Proto adapts:
- **AI hires people**: Recruit, onboard, and manage human workers for tasks AI can't do
- **AI delegates to humans**: Break down work, assign to people, synthesize results
- **Humans as reviewers**: AI executes, humans approve or course-correct
- **Humans for key decisions**: AI prepares options and context, humans make strategic calls
- **Approval gates**: Human sign-off for sensitive actions (spending, publishing, trading)

**The end goal is to automate any human labor.** When that's not possible, Proto uses whatever hybrid model fits—not a fixed progression, but the right configuration for each task.

### What can't Proto do yet?
- Fully autonomous operation without human oversight
- 100% reliable execution of novel, complex tasks
- Physical tasks requiring real-world hardware
- Tasks requiring human relationships (sales calls, negotiations)

---

## Risk & Control

### How do you prevent runaway AI / catastrophic mistakes?

**Approval Gates**: Proto pauses before any action that:
- Spends money (API calls, purchases, trades)
- Publishes externally (social media, websites, emails)
- Modifies production systems
- Creates accounts or changes permissions

Human must approve before these actions execute.

**Audit Log**: Every action is logged with:
- What was done
- Which agent did it
- Full diff of any changes
- Timestamp and context

**Kill Switch**: Immediate halt of all agent activity with one command.

**Rate Limits**: Maximum actions per minute, maximum spend per session.

### What if the AI hallucinates or makes errors?

Proto uses verification loops:
1. Execute action (e.g., write code, make trade)
2. Verify result (e.g., run tests, check position)
3. If failure, iterate or escalate to human

For content, it's approval gates. For code, it's automated testing. For trading, it's position limits and stop losses.

### Who has access to the systems Proto controls?
Only the human operator. Proto operates within the permissions granted—same as giving a contractor access. You define the boundaries.

---

## The Business

### Why is this a good opportunity?

**The market gap is clear:**
- Current agents are domain-specific silos (coding only, sales only, support only)
- Almost no agents self-improve and learn from their work
- Everyone builds copilots—no one is building to automate human labor entirely
- Agents aren't maximized yet—there's so much untapped potential

**The reward is enormous:**
- First system that can automate human labor at scale captures the market
- Compounding returns: each business funds more businesses
- The prize isn't one company—it's unlimited companies
- Self-improvement is the key: each task makes Proto better at all tasks

**Why the downside is limited:**
Even if some tasks can't be fully automated, Proto can use hybrid models:
- **AI managing humans**: Proto coordinating human workers—10x productivity gains
- **Automate subsets**: Even automating 50% of a business process is valuable
- **Domain-specific agents**: Spin off specialized agents as standalone products
- **Enterprise automation**: Sell the orchestration platform to companies

**The downside isn't zero—it's a different kind of success.** Full automation is the goal. Hybrid models are the bridge.

### Why not just pick one business to focus on?

We don't know which business will work fastest. That's the point—Proto experiments across multiple paths simultaneously:
- Try agency work while testing e-commerce
- Build a SaaS product while running freelance operations
- Explore trading while generating content

The first successful business proves the capability. Then we scale to many businesses.

### What's the revenue model?

**Phase 1 (Now)**: Prove reliability on complex processes. Generate pilot revenue from whichever path works.

**Phase 2 (Post-raise)**: Run autonomous business operations. Proto becomes the business, not a tool for businesses.

**Phase 3 (At threshold)**: Launch portfolio of autonomous companies. Each one adds revenue and makes the system better.

This is not SaaS. We don't charge per seat. We run businesses.

### What's the market size?
The TAM for "businesses that could be automated" is effectively infinite. But we're not targeting a market—we're building infrastructure to create value across any automatable business.

If Proto can reliably run one business, it can run ten. Or a hundred.

---

## The Raise

### How much are you raising?
**Close A**: $300-500K (momentum round)
**Close B**: $1-2M total (after proof milestones)

### What's the use of funds?
12-month runway covering:
- Founder salary: ₪35,000/month
- 2 senior engineers: ~₪70,000/month
- Aggressive compute (API tokens, cloud VMs): ~$4,000/month
- Overhead: ~₪12,000/month

**Total monthly burn**: ~₪132,000 (~$37K)
**12-month need**: ~$500K + buffer

### What are the milestones for Close B?
1. Self-improvement systems demonstrably working
2. Mastery of at least one domain (end-to-end execution with minimal intervention)
3. Complete product or service delivered autonomously

### What's the valuation / terms?
Raising on SAFE with standard terms. Looking for investors who see the opportunity and want to be part of building it.

**Pre-Seed Valuation Reality:**
At pre-seed, formal business valuation is somewhat arbitrary—it's an agreement on risk vs. reward. Current market range: $3M-$5M caps for pre-seed.

**Post-Money vs. Pre-Money:**
- **Pre-money**: Company value before the investment
- **Post-money**: Company value after the investment (pre-money + investment amount)
- SAFEs are typically post-money (simpler math)

### What about dilution?
When you raise, investors get newly issued shares. Your number of shares stays the same, but your percentage decreases.

Typical founder ownership trajectory:
- After Pre-Seed: ~85-90%
- After Seed: ~70-80%
- After Series A: ~55-65%
- After Series B: ~40-50%

This is normal. A smaller percentage of a larger company is worth more than 100% of nothing.

### Why no 5-year projections?
5-year financial projections at seed stage are guesswork—it's impossible to predict that far ahead for an early-stage company.

We focus on the next **12-18 months**:
- Clear monthly burn calculation
- Specific milestones we'll hit
- What the money will be used for

If asked for projections, we provide short-term focus with honest assumptions, not made-up hockey sticks.

---

## The Founder

### Why are you the right person to build this?
- Built Proto's entire stack solo—backend, frontend, agent orchestration, self-improvement systems
- Full-stack developer who founded, developed, and released multiple apps independently
- Vision + execution: I see where this goes AND I can build it

**First-principles approach:** I started with the end goal—an AI agent that self-improves and runs companies autonomously. Then I broke it down into components: What does it need to control computers? What specialist skills does it need? How does it learn from failures? How does it coordinate multiple agents? I designed and built each component to work together as a coherent system. Not a wrapper on existing tools—purpose-built from the ground up for autonomous operation.

**Resilience:** Building Proto has meant months of solo development, countless failed experiments, and moments where the whole approach seemed impossible. I kept going because I believe this is inevitable—and I want to be the one who builds it. That stubbornness is what this problem requires.

**Authenticity:** I'm not pretending this is easy or that I have all the answers. What I have is a working system, a clear vision, and the willingness to grind through the hard parts. I'm aware of my limitations—I need great engineers, I need compute resources, I need time. That's why I'm raising.

### Are you looking for co-founders?
Open to it for the right person, but not actively seeking. Need someone who believes in autonomous companies and can contribute at a senior technical or operational level.

### What's your timeline?
- **Now**: Fundraising + proving complex process execution
- **Months 1-6**: Team + reliability improvements + business experiments
- **Months 6-12**: Scale operations, decrease intervention rate, portfolio growth

---

## Fundability Controls (Technical Detail)

### Approval Gate System
```
Action → Classification → Gate Check → Human Approval → Execute
                              ↓
                     (if no gate) → Execute immediately
```

**Gated actions**:
- `publish_*` - Any external publication
- `payment_*` - Any financial transaction
- `trade_*` - Any trading operation
- `account_*` - Any account creation/modification
- `production_*` - Any production system change

### Audit Log Schema
```json
{
  "timestamp": "ISO8601",
  "agent_id": "string",
  "action_type": "string",
  "action_details": "object",
  "diff": "string (if applicable)",
  "outcome": "success | failure | pending_approval",
  "human_approval": "null | {approver, timestamp, notes}"
}
```

### Kill Switch
`POST /api/emergency-stop` immediately:
- Terminates all running agent tasks
- Closes all SSH connections
- Pauses all VM operations
- Exits all trading positions (if applicable)
- Logs emergency stop event

Human must explicitly restart system after kill switch activation.

---

*Last updated: Jan 2026*
*Contact: me@nirfeinste.in*

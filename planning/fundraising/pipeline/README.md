# Investor Pipeline Management

## Fundraising is a Numbers Game

**Real example from Fresh Paint (YC company):**
- Met with **160 investors**
- Got **39 checks**
- That's a 24% conversion rate—and that's considered GOOD

**What this means for you:**
- Prepare for volume—your tracker needs to handle 100-200+ leads
- Most will say no. This is normal.
- It's "coffee chats and Zoom calls" not one high-stakes pitch
- Don't get discouraged by rejections—it's just math

---

## Do Your Homework First

**Fundraising is 75% listening/researching, 25% talking.**

Before any outreach, research each investor deeply:

### Basic Research
1. **Portfolio Check**: What have they invested in? Look for AI, agents, infrastructure, automation
2. **Thesis/Focus**: What do they say they care about? Check their website, tweets, blog posts
3. **Stage & Check Size**: Are they actually pre-seed/seed? What's their typical check?
4. **Recent Activity**: Are they actively investing right now?

### Deeper Research (Capacity & Values)
5. **Capacity Indicators**: What suggests their check size?
   - Fund size (for VCs)
   - Other investments they've made
   - Company exits, board positions
6. **Values & Interests**: What do they genuinely care about?
   - What do they write about?
   - What causes do they support?
   - What gets them excited in interviews/podcasts?

### The 30-Second Rule
For each investor, you should be able to answer in 30 seconds:
**"Why should THIS specific person invest in Proto?"**

Not "they invest in AI" but "They led Devin's seed round, write about autonomous systems, and just tweeted about AI agents replacing entire departments."

If you can't answer this in 30 seconds, you aren't ready to meet them.

**Use this research to:**
- Tailor your pitch to their interests
- Reference specific portfolio companies in cold emails ("Saw you invested in X...")
- Skip investors who clearly won't be a fit
- Fill in the "Fit Reason" column in your tracker

**This goes in the "Fit Reason" field** - not just "AI investor" but "Invested in Devin, writes about autonomous agents, $25-50k checks"

---

## Files

| File | Purpose |
|------|---------|
| `outreach_tracker.csv` | Daily tracking of all investor touches |
| `investor_list.csv` | Master list of 150 target investors |

## Outreach Tracker Fields

| Field | Values | Notes |
|-------|--------|-------|
| **Name** | Full name | |
| **Type** | Angel, Micro-VC, Pre-Seed Fund, Accelerator | |
| **Fund/Company** | Their firm/company | |
| **Email** | | |
| **LinkedIn** | Profile URL | |
| **Intro Path** | Direct, Warm Intro, Cold, Application | How you'll reach them |
| **Fit Reason** | Why they'd invest | AI focus, Israel, early-stage, etc. |
| **Status** | See below | |
| **Last Contact** | Date | YYYY-MM-DD |
| **Next Action** | What to do next | |
| **Next Action Date** | When | YYYY-MM-DD |
| **Notes** | Call notes, context | |
| **Amount Interest** | $X if mentioned | |
| **Objections** | What concerns they raised | Feed back to FAQ |

## Status Values

| Status | Meaning |
|--------|---------|
| `Not Started` | Haven't reached out yet |
| `Intro Requested` | Asked someone for intro |
| `Intro Made` | Intro sent, waiting for response |
| `Outreach Sent` | Cold email/LinkedIn sent |
| `Responded` | They replied |
| `Call Scheduled` | Meeting booked |
| `Call Done` | Had the call |
| `Follow-up Sent` | Post-call materials sent |
| `Interested` | Expressed interest |
| `Soft Commit` | Verbal yes, no paper |
| `Due Diligence` | Reviewing materials |
| `Term Sheet` | Negotiating terms |
| `Signed` | SAFE signed |
| `Wired` | Money received |
| `Passed` | Said no |
| `No Response` | Ghosted after 2+ attempts |

## Daily Workflow

**Morning (30 min):**
1. Review "Next Action Date = Today"
2. Do those actions first

**Outreach Block (1-2 hours):**
1. Send 10 warm intro requests (use `templates/intro_request.md`)
2. Send 10-20 cold emails (use `templates/cold_outreach.md`)
3. Send 10 follow-ups (use `templates/follow_up.md`)
4. Update tracker after each touch

**End of Day (15 min):**
1. Update all statuses
2. Set next actions for everyone you touched
3. Log any objections heard

## Weekly Review (Monday)

1. Count by status:
   - Total pipeline
   - Calls scheduled this week
   - Soft commits
   - Closed $

2. Identify blockers:
   - Who's stuck in "No Response"?
   - Who needs follow-up?

3. Update scoreboard

---

## Investor Stewardship (After They Invest)

**The relationship doesn't end when the wire hits.**

Even investors who've committed want to feel "seen"—recognized for their belief in you. This builds trust for future rounds and referrals.

### The Rule of Seven
Plan to thank each investor through multiple channels:

1. **Immediate thank-you email** - Personal, not templated
2. **Formal acknowledgment letter** - For their records
3. **Personal phone call** - Just to say thanks, not to ask for anything
4. **Monthly update emails** - Progress, wins, challenges (brief)
5. **Milestone celebrations** - Share wins: "We hit X, you helped make this happen"
6. **Quarterly check-ins** - Quick call or coffee to maintain relationship
7. **Annual summary** - Where we started, where we are, where we're going

### Why This Matters
- Investors talk to other investors. Happy investors refer you.
- Future rounds are easier with existing investors who feel valued.
- If things get hard, investors who feel connected will help more.

**Add to your tracker:** After status = "Wired", track stewardship touches in the Notes field.

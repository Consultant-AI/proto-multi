# Demo Preparation - Live Demo & Video Capture

**Priority:** Critical (Fundraising)
**Status:** Not Started
**Estimated Time:** 3-4 days

## Objective
Make Proto demo-ready for investor meetings: ensure reliable live demo capability, capture high-quality demo videos, and finalize demo scripts.

---

## Part 1: Software Ready for Live Demo

### Pre-Demo Checklist
- [ ] All UI elements render correctly
- [ ] Agent delegation tree displays properly
- [ ] Terminal tab works (local + cloud)
- [ ] Files tab shows output correctly
- [ ] Browser tab functions
- [ ] Computer tab (screenshots, mouse, keyboard) works
- [ ] Cloud VM connection stable

### Stability Requirements
- [ ] No crashes during multi-agent execution
- [ ] Graceful error handling (no ugly stack traces)
- [ ] Loading states for all async operations
- [ ] Smooth animations and transitions
- [ ] Quick startup time (< 5 seconds to usable state)

### Demo-Specific Features
- [ ] Clean "fresh session" state (one-click reset)
- [ ] Sample project pre-loaded and ready
- [ ] Approval gates work visibly (show human-in-loop)
- [ ] Agent activity visible in real-time
- [ ] Progress indicators during task execution

### Fallback Systems
- [ ] Quick switch to pre-recorded video if live fails
- [ ] Backup demo tasks that always work
- [ ] Offline mode for demos without internet
- [ ] Pre-saved output files in `demo/demo_fallback/`

---

## Part 2: Demo Video Capture

### Videos to Create
1. **90-second highlight** (primary - for cold outreach)
   - Hook in first 5 seconds
   - Show: task input → agent coordination → execution → output
   - End with "autonomous company factory" message

2. **5-minute walkthrough** (secondary - for interested investors)
   - Full demo with narration
   - Explain each component
   - Show approval gates and controls
   - Demonstrate cross-platform capability

3. **Technical deep-dive** (optional - for technical due diligence)
   - Architecture explanation
   - Self-improvement system demo
   - Code walkthrough

### Recording Requirements
- [ ] Screen recording software setup (OBS or similar)
- [ ] High resolution (1080p minimum, 4K preferred)
- [ ] Clean desktop (no personal files visible)
- [ ] Consistent window size across recordings
- [ ] Good audio quality if narrating

### Post-Production
- [ ] Edit out dead time / loading delays
- [ ] Add subtle zoom on key moments
- [ ] Include captions/subtitles
- [ ] Add Proto logo watermark
- [ ] Export in multiple formats (MP4, WebM)

### Hosting
- [ ] Upload to reliable host (YouTube unlisted, Vimeo, or direct)
- [ ] Create short link for easy sharing
- [ ] Test link works in all contexts (email, LinkedIn, Zoom chat)

---

## Part 3: Demo Script Updates

### Review and Update
- [ ] Review `planning/fundraising/demo/demo_script.md`
- [ ] Ensure timing matches actual execution speed
- [ ] Update talking points based on latest messaging
- [ ] Add recovery scripts for common failures
- [ ] Test full script end-to-end 3+ times

### Demo Task Options
Choose tasks that demonstrate:
- Multi-agent coordination (CEO delegates to specialists)
- Cross-platform capability (mention Mac + cloud Linux)
- Real computer use (files, terminal, or GUI)
- Business value (output that makes sense to investors)

**Recommended demo tasks:**
1. Marketing campaign creation (landing page + ad copy)
2. Research report generation (competitive analysis)
3. Simple SaaS feature build (code + deploy)
4. Content generation at scale

### Key Messages to Hit (per demo_script.md)
1. Specialist agents coordinating like a company
2. Cross-platform (Mac + cloud Linux) — multi-computer orchestration on roadmap
3. Self-improvement — gets better with each task
4. Approval gates — human oversight that reduces over time
5. Any business — not limited to one domain
6. Path to autonomy — architecture is ready, reliability is the work

---

## Deliverables

### Must Have (for fundraising)
- [ ] Live demo works reliably (3/3 successful runs)
- [ ] 90-second video uploaded and shareable
- [ ] Demo script tested and timed
- [ ] Fallback video ready in `demo/demo_fallback/`
- [ ] One-click demo reset working

### Nice to Have
- [ ] 5-minute walkthrough video
- [ ] Multiple demo task options tested
- [ ] Demo mode with simulated fast execution

---

## Testing Protocol

Before any investor demo:
1. Fresh restart of Proto
2. Verify cloud VM is connected
3. Run demo task once privately
4. Check all tabs work
5. Confirm fallback video is accessible
6. Test screen share works

---

## Files to Update

| File | Update Needed |
|------|---------------|
| `planning/fundraising/demo/demo_script.md` | Verify timing, update talking points |
| `planning/fundraising/demo/demo_fallback/README.md` | Add video links |
| `planning/fundraising/narrative/one_pager.md` | Add demo link |
| `planning/fundraising/narrative/executive_summary.md` | Add demo link |
| `planning/fundraising/templates/*.md` | Update [link] placeholders |

---

*Created: 2026-01-20*

# Computer Target Selector

**Priority:** High
**Status:** Not Started
**Estimated Time:** 1-2 days

## Objective
Add dropdown next to chat input to choose which computer/server to control.

## Requirements
- [ ] Dropdown UI component next to chat input
- [ ] Options: "Local", "Ubuntu Server 1", "Ubuntu Server 2", etc.
- [ ] Connection status indicator (connected/disconnected/loading)
- [ ] Save selected computer preference per session
- [ ] Clean design that fits new theme

## Technical Details
- Create ComputerSelector component
- Store selection in session state
- Add backend API for computer list
- Implement connection status checking
- Add icons for different computer types

## UI/UX Considerations
- Clear visual feedback for active computer
- Quick switching without confirmation
- Show computer specs/info on hover
- Keyboard shortcuts for quick switching

## Deliverables
- [ ] ComputerSelector component created
- [ ] Backend API endpoint for computers list
- [ ] Session persistence for selection
- [ ] Connection status indicators
- [ ] Integration with chat input area

---
*Created: 2025-12-17*

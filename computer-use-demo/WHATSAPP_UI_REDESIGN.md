# WhatsApp Web Dark Theme UI Redesign

## Overview

The webui has been redesigned to match WhatsApp Web's dark theme aesthetic with:
- **Sidebar** for session/conversation management (left panel)
- **Chat area** for messages and interaction (right panel)
- **WhatsApp-style colors** (dark greens, grays, authentic message bubbles)
- **Modern chat interface** with proper message alignment and styling

## New UI Structure

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  Sidebar (400px)       │  Chat Area (flex-1)            │
│  ┌──────────────────┐  │  ┌───────────────────────────┐ │
│  │ Header           │  │  │ Chat Header               │ │
│  │ + New  ⏹ Stop   │  │  │ Claude [status] SDK       │ │
│  ├──────────────────┤  │  ├───────────────────────────┤ │
│  │ Search...        │  │  │                           │ │
│  ├──────────────────┤  │  │      Messages             │ │
│  │ ● Session 1      │  │  │      (WhatsApp style)     │ │
│  │ ● Session 2      │  │  │                           │ │
│  │ ● Session 3      │  │  │                           │ │
│  │                  │  │  ├───────────────────────────┤ │
│  │                  │  │  │ Composer (Type message)  │ │
│  └──────────────────┘  │  └───────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Color Palette (WhatsApp Dark)

```css
--bg-main: #111b21          /* Main background */
--bg-sidebar: #111b21       /* Sidebar background */
--bg-chat: #0b141a          /* Chat area background */
--bg-panel-header: #202c33  /* Header backgrounds */
--bg-message-in: #202c33    /* Incoming messages (Claude) */
--bg-message-out: #005c4b   /* Outgoing messages (User) */
--bg-input: #2a3942         /* Input field background */
--text-primary: #e9edef     /* Primary text */
--text-secondary: #8696a0   /* Secondary/muted text */
--border: #2a3942           /* Borders */
--accent: #00a884           /* WhatsApp green accent */
--hover: #2a3942            /* Hover states */
```

## Key Features

### 1. Sidebar (Session Management)
- **Header**: "Conversations" title with New Chat (+) and Stop (⏹) buttons
- **Search bar**: Search through conversations (with search icon)
- **Session list**:
  - Each session shows avatar (green circle with "C")
  - Session name/time on right
  - Preview of last message
  - Active session highlighted
  - Hover effects

### 2. Chat Area
- **Header**:
  - Claude avatar (green circle)
  - "Claude" name with status ("Idle" or "Working...")
  - "Agent SDK" badge

- **Messages**:
  - WhatsApp-style bubbles
  - User messages: right-aligned, dark green (#005c4b)
  - Assistant/Tool messages: left-aligned, dark gray (#202c33)
  - Proper padding and shadows
  - Subtle background pattern

- **Composer**:
  - Dark input field with rounded corners
  - Auto-expanding textarea
  - Send button (paper plane icon)
  - Green send button when enabled

### 3. Typing Indicator
- Appears as left-aligned bubble
- Three bouncing dots
- Same style as incoming messages

## File Structure

### HTML Structure

```html
<div id="app">
  <!-- Sidebar -->
  <div id="sidebar">
    <div id="sidebar-header">
      <h1>Conversations</h1>
      <div class="header-icons">
        <button id="newSessionBtn" class="icon-btn new-chat">+</button>
        <button id="stopBtn" class="icon-btn stop-btn">⏹</button>
      </div>
    </div>
    <div id="search-container">
      <input id="search-input" placeholder="Search conversations..." />
    </div>
    <div id="sessions-list">
      <!-- Session items populated by JS -->
    </div>
  </div>

  <!-- Chat Area -->
  <div id="chat-area">
    <div id="chat-header">
      <div class="chat-title">
        <div class="chat-avatar">C</div>
        <div class="chat-info">
          <h2>Claude</h2>
          <div class="chat-status" id="status">Idle</div>
        </div>
      </div>
      <div class="badge">Agent SDK</div>
    </div>
    <div id="messages">
      <!-- Messages populated by JS -->
    </div>
    <div id="composer">
      <form id="chat-form">
        <div class="composer-wrapper">
          <textarea id="prompt" placeholder="Type a message"></textarea>
          <button id="sendBtn" type="submit">📤</button>
        </div>
      </form>
    </div>
  </div>
</div>
```

## JavaScript Updates Needed

### Session Rendering

Update `loadSessions()` to populate sidebar:

```javascript
async function loadSessions() {
    const res = await fetch('/api/sessions');
    const sessions = await res.json();

    const list = document.getElementById('sessions-list');
    list.innerHTML = '';

    sessions.forEach(session => {
        const div = document.createElement('div');
        div.className = 'session-item' + (session.isCurrent ? ' active' : '');
        div.dataset.sessionId = session.id;
        div.innerHTML = `
            <div class="session-avatar">C</div>
            <div class="session-info">
                <div class="session-header">
                    <div class="session-name">Session ${session.id.slice(-4)}</div>
                    <div class="session-time">${formatDate(session.lastActive)}</div>
                </div>
                <div class="session-preview">${session.messageCount} messages</div>
            </div>
        `;
        div.addEventListener('click', () => switchSession(session.id));
        list.appendChild(div);
    });
}
```

### Message Rendering

Update `renderMessages()` for WhatsApp-style bubbles:

```javascript
function renderMessages(messages, scrollToBottom=true) {
    messagesEl.innerHTML = '';

    messages.forEach(msg => {
        const bubble = document.createElement('div');
        bubble.className = `bubble ${msg.role}`;

        let html = '';
        if (msg.label) {
            html += `<div class="label">${msg.label}</div>`;
        }
        html += `<div class="text">${msg.text}</div>`;

        (msg.images || []).forEach(src => {
            html += `<img src="${src}" class="tool-screenshot" />`;
        });

        bubble.innerHTML = html;
        messagesEl.appendChild(bubble);
    });

    if (scrollToBottom) {
        scrollMessagesToBottom();
    }
}
```

## Implementation Steps

1. **Backup current webui.py**
   ```bash
   cp computer_use_demo/webui.py computer_use_demo/webui_backup.py
   ```

2. **Update CSS** in `_html_shell()` function
   - Replace all CSS with WhatsApp-style CSS (see template)

3. **Update HTML** structure
   - Replace single-column layout with sidebar + chat layout
   - Update element IDs and structure

4. **Update JavaScript**
   - Modify `loadSessions()` to populate sidebar
   - Update `renderMessages()` for bubble alignment
   - Keep all existing functionality (SSE, stop, etc.)

5. **Test**
   - Restart webui
   - Verify session switching works
   - Verify messages display correctly
   - Verify stop button works

## Benefits

✅ **Modern WhatsApp-like interface** - Familiar UX
✅ **Better session visibility** - See all conversations at a glance
✅ **Improved message readability** - Proper bubble alignment
✅ **Cleaner layout** - Sidebar separates navigation from chat
✅ **Authentic dark theme** - WhatsApp's actual color palette
✅ **Better use of space** - Wider messages area

## Preview

A complete HTML template is available at:
`whatsapp_ui_template.html`

Open this file in a browser to see the static design before implementing.

## Status

📝 **Design Complete** - Template created
⏳ **Implementation Pending** - Awaiting integration into webui.py

The full redesign requires updating:
- ✅ CSS (complete in template)
- ✅ HTML structure (complete in template)
- ⏳ JavaScript updates (needs adaptation of existing JS)
- ⏳ Integration testing

## Notes

- All existing functionality preserved (SSE, sessions, stop/resume)
- Only visual redesign - no API changes needed
- Backward compatible with existing session storage
- Responsive design considerations for smaller screens

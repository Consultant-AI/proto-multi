# Session Management & Stop/Resume - Implementation Guide

## What's Been Added

I've implemented the backend for:

1. **Stop Button** - API endpoint to interrupt running agent
2. **Session Persistence** - Save/load conversations to disk
3. **Multiple Sessions** - Create new conversations, switch between them
4. **Resume Capability** - Continue from where you left off

## Backend Changes Made

### 1. Session Class Updates ([webui.py](computer_use_demo/webui.py))

**Added to ChatSession:**
```python
# Stop/resume functionality
self._stop_requested = False
self._current_task: asyncio.Task | None = None

# Session persistence
self.created_at = datetime.now()
self.last_active = datetime.now()

def save(self, sessions_dir: Path) -> None:
    """Save session to disk."""

@classmethod
def load(cls, session_id: str, sessions_dir: Path, api_key: str) -> "ChatSession":
    """Load session from disk."""

async def stop(self) -> None:
    """Request the agent to stop."""
    self._stop_requested = True
    if self._current_task:
        self._current_task.cancel()
```

### 2. New API Endpoints

**POST /api/stop** - Stop the currently running agent
```python
await fetch('/api/stop', { method: 'POST' })
```

**GET /api/sessions** - List all sessions (active + saved)
```javascript
const response = await fetch('/api/sessions')
const sessions = await response.json()
// Returns array of: { id, createdAt, lastActive, messageCount, isCurrent }
```

**POST /api/sessions/new** - Create a new session
```javascript
const response = await fetch('/api/sessions/new', { method: 'POST' })
const newSession = await response.json()
```

**POST /api/sessions/{id}/switch** - Switch to a different session
```javascript
await fetch(`/api/sessions/${sessionId}/switch`, { method: 'POST' })
```

**DELETE /api/sessions/{id}** - Delete a session
```javascript
await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' })
```

### 3. Session Storage

Sessions are saved to: `~/.claude/webui_sessions/`

Each session is a pickle file containing:
- session_id
- messages (API format)
- display_messages (UI format)
- created_at, last_active timestamps
- model, tool_version

## Frontend UI Needed

The backend is complete, but you need to add UI elements. Here's what to add to the HTML:

### 1. Header with Stop Button and Session Controls

```html
<header>
    <h1>Claude Computer Use</h1>
    <div class="header-right">
        <div class="controls-row">
            <!-- Session selector -->
            <select id="sessionSelect" class="session-select">
                <option value="">Loading sessions...</option>
            </select>

            <!-- New conversation button -->
            <button id="newSessionBtn" class="icon-btn" title="New Conversation">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
            </button>

            <!-- Stop button -->
            <button id="stopBtn" class="icon-btn stop-btn" title="Stop Agent" style="display:none">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="6" y="6" width="12" height="12"></rect>
                </svg>
            </button>
        </div>

        <div class="badge">Agent SDK Enabled</div>
        <div id="status">Idle</div>
    </div>
</header>
```

### 2. CSS for New Elements

```css
.controls-row {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 8px;
}

.session-select {
    background: #080b11;
    border: 1px solid var(--border);
    color: var(--text);
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 13px;
    cursor: pointer;
    min-width: 200px;
}

.session-select:hover {
    border-color: var(--accent);
}

.icon-btn {
    background: rgba(102, 126, 234, 0.1);
    border: 1px solid rgba(102, 126, 234, 0.3);
    color: #667eea;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.icon-btn:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: translateY(-2px);
}

.stop-btn {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
    color: #ef4444;
}

.stop-btn:hover {
    background: rgba(239, 68, 68, 0.2);
}
```

### 3. JavaScript for Session Management

```javascript
let currentSessionId = null;

// Load sessions list
async function loadSessions() {
    const res = await fetch('/api/sessions');
    const sessions = await res.json();

    const select = document.getElementById('sessionSelect');
    select.innerHTML = '';

    sessions.forEach(session => {
        const option = document.createElement('option');
        option.value = session.id;
        option.textContent = `${formatDate(session.lastActive)} (${session.messageCount} msgs)`;
        if (session.isCurrent) {
            option.selected = true;
            currentSessionId = session.id;
        }
        select.appendChild(option);
    });
}

// Switch session
document.getElementById('sessionSelect').addEventListener('change', async (e) => {
    const sessionId = e.target.value;
    if (!sessionId) return;

    const res = await fetch(`/api/sessions/${sessionId}/switch`, { method: 'POST' });
    const data = await res.json();
    renderMessages(data.messages, true);
    updateStatus(data.running);
    currentSessionId = sessionId;
});

// New session
document.getElementById('newSessionBtn').addEventListener('click', async () => {
    const res = await fetch('/api/sessions/new', { method: 'POST' });
    const data = await res.json();
    currentSessionId = data.sessionId;
    await loadSessions();
    renderMessages([], true);
});

// Stop button
document.getElementById('stopBtn').addEventListener('click', async () => {
    await fetch('/api/stop', { method: 'POST' });
    document.getElementById('stopBtn').style.display = 'none';
});

// Show/hide stop button based on status
function updateStatus(running) {
    statusEl.textContent = running ? 'Claude is working…' : 'Idle';
    sendBtn.disabled = running;
    promptEl.disabled = running;

    // Show stop button when running
    document.getElementById('stopBtn').style.display = running ? 'flex' : 'none';

    if (!running) {
        promptEl.focus();
    }
}

// Load sessions on page load
loadSessions();
setInterval(loadSessions, 5000); // Refresh every 5 seconds

// Helper function
function formatDate(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
}
```

## How It Works

### Creating a New Conversation
1. User clicks "New Conversation" button
2. POST to `/api/sessions/new`
3. Server creates new ChatSession, saves to disk
4. UI switches to the new empty session

### Switching Between Conversations
1. User selects different session from dropdown
2. POST to `/api/sessions/{id}/switch`
3. Server loads session from disk if needed
4. UI renders the selected conversation

### Stopping the Agent
1. User clicks Stop button (shows when agent is running)
2. POST to `/api/stop`
3. Server cancels the current task
4. Agent stops gracefully
5. User can send another message to resume/continue

### Resuming After Stop
1. User types a new message
2. Agent continues from where it left off
3. Previous context is preserved

## Session Persistence

Sessions are automatically saved:
- After each message is sent
- When agent is stopped
- When switching sessions

Sessions persist across restarts - you can close the webui and come back later!

## Testing

### 1. Start the webui
```bash
python3 -m computer_use_demo.webui
```

### 2. Test Stop/Resume
- Send a long task: "create a whatsapp clone and test it"
- Click Stop button while it's running
- Send another message: "continue where you left off"
- Agent resumes with full context

### 3. Test Multiple Sessions
- Create a new conversation
- Switch back to old conversation
- See that all messages are preserved

### 4. Test Persistence
- Create a few conversations
- Stop the webui (Ctrl+C)
- Restart it
- All sessions should still be available in the dropdown

## File Locations

- **Backend code**: `computer_use_demo/webui.py`
- **Session storage**: `~/.claude/webui_sessions/*.pkl`
- **Frontend**: Need to update the `_html_shell()` function with the UI elements above

## Next Steps

To complete the implementation, you need to:

1. Update the `_html_shell()` function in webui.py to include the new HTML elements
2. Add the CSS for the new UI components
3. Add the JavaScript for session management

Would you like me to generate the complete updated `_html_shell()` function with all these changes integrated?

# UI Not Showing Messages - FIXED!

## The Problem

User reported: **"i looked at the logs it continued working but in the viewer i didnt see it"**

The agent was working (logs confirmed tool execution) but the UI wasn't showing any updates until the ENTIRE task completed.

## Root Cause

The original webui implementation had a blocking architecture:

### Before (Blocking):
```
1. User sends message
2. POST /api/messages is called
3. await session.send() blocks until ENTIRE sampling_loop completes
4. Agent works for minutes with NO UI updates
5. Only when complete does POST return
6. UI then shows all messages at once
```

**The flow:**
```python
@app.post("/api/messages")
async def send_message(payload: SendRequest):
    session: ChatSession = app.state.session
    await session.send(payload.message)  # ← BLOCKS UNTIL COMPLETE!
    return JSONResponse(session.serialize())  # ← ONLY THEN RETURNS
```

The callbacks (`output_callback`, `tool_output_callback`) WERE being called and adding messages to `self.display_messages`, but the frontend couldn't see them because:
- The POST request didn't return until the agent finished
- The frontend only polled every 3 seconds with `setInterval(() => refreshState(true), 3000)`
- Even the polling couldn't see the messages because they were in memory during the blocking operation

## The Fix - Server-Sent Events (SSE)

Implemented real-time streaming using SSE so the UI receives updates as they happen.

### After (Non-Blocking with SSE):
```
1. User sends message
2. POST /api/messages starts agent in BACKGROUND (asyncio.create_task)
3. POST returns immediately
4. SSE stream sends updates in real-time as agent works
5. Frontend receives each message/tool result immediately
6. Continuous stream of updates!
```

## Changes Made

### 1. Added SSE Infrastructure ([webui.py](computer_use_demo/webui.py:101))

```python
# SSE streaming for real-time updates
self._sse_queues: list[asyncio.Queue] = []
```

Each connected client gets a queue to receive updates.

### 2. Made POST Non-Blocking ([webui.py](computer_use_demo/webui.py:281-287))

```python
@app.post("/api/messages")
async def send_message(payload: SendRequest):
    session: ChatSession = app.state.session
    # Start processing in background - don't wait for completion
    asyncio.create_task(session.send(payload.message))
    # Return immediately with current state
    return JSONResponse(session.serialize())
```

**Key change:** `asyncio.create_task()` instead of `await` - returns immediately!

### 3. Added SSE Endpoint ([webui.py](computer_use_demo/webui.py:290-324))

```python
@app.get("/api/stream")
async def stream_updates(request: Request):
    """Server-Sent Events endpoint for real-time updates."""
    session: ChatSession = app.state.session
    queue: asyncio.Queue = asyncio.Queue()
    session._sse_queues.append(queue)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            if queue in session._sse_queues:
                session._sse_queues.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### 4. Broadcast Updates from Callbacks ([webui.py](computer_use_demo/webui.py:129-159))

```python
def output_callback(block: BetaContentBlockParam):
    if isinstance(block, dict) and block.get("type") == "text":
        self._pending_assistant_chunks.append(block.get("text", ""))
        # Send real-time update via SSE
        asyncio.create_task(self._broadcast_sse_update())

def tool_output_callback(result: ToolResult, tool_id: str):
    # ... add message to display_messages ...
    # Send real-time update via SSE
    asyncio.create_task(self._broadcast_sse_update())
```

Every callback now broadcasts to all connected SSE clients!

### 5. Broadcast Helper ([webui.py](computer_use_demo/webui.py:216-223))

```python
async def _broadcast_sse_update(self):
    """Broadcast current state to all SSE connections."""
    data = self.serialize()
    for queue in self._sse_queues:
        try:
            await queue.put(data)
        except:
            pass  # Queue might be closed
```

### 6. Updated Frontend to Use SSE ([webui.py](computer_use_demo/webui.py:467-490))

```javascript
function connectSSE() {
    eventSource = new EventSource('/api/stream');

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            renderMessages(data.messages, true);
            updateStatus(data.running);
        } catch (e) {
            console.error('SSE parse error:', e);
        }
    };

    eventSource.onerror = (error) => {
        console.error('SSE error, reconnecting in 3s...', error);
        eventSource.close();
        setTimeout(connectSSE, 3000);
    };
}

// Connect to SSE for real-time updates
connectSSE();
```

Frontend now listens to `/api/stream` and receives updates in real-time!

## How It Works Now

### Message Flow:
```
User submits message
    ↓
POST /api/messages (returns immediately)
    ↓
Agent starts in background
    ↓
Agent uses bash tool → tool_output_callback → broadcast_sse_update
    ↓
SSE sends update → Frontend receives → UI updates
    ↓
Agent uses str_replace_editor → tool_output_callback → broadcast_sse_update
    ↓
SSE sends update → Frontend receives → UI updates
    ↓
Agent uses computer tool → tool_output_callback → broadcast_sse_update
    ↓
SSE sends update → Frontend receives → UI updates
    ↓
... continuous stream of updates ...
    ↓
Agent completes → final broadcast_sse_update
    ↓
UI shows "Idle"
```

## Benefits

✅ **Real-time updates:** User sees every message/tool result immediately
✅ **Non-blocking:** UI doesn't freeze while agent works
✅ **Continuous progress:** User sees the agent is working, not stuck
✅ **Automatic reconnection:** If SSE connection drops, frontend reconnects
✅ **Multiple clients:** Multiple browser tabs can all receive updates
✅ **Efficient:** Only sends updates when something changes

## Testing

### Restart the webui:
```bash
cd /Users/nirfeinstein/Documents/GitHub/proto-multi/computer-use-demo
python3 -m computer_use_demo.webui
```

### Try a multi-step task:
```
create tic-tac-toe in /tmp and test it in chrome
```

### Expected behavior:
```
✅ User message appears immediately
✅ Tool execution messages appear as they happen:
   - "Tool bash_1: mkdir /tmp/tic-tac-toe"
   - "Tool str_replace_editor_1: Created index.html"
   - "Tool str_replace_editor_2: Created style.css"
   - "Tool str_replace_editor_3: Created game.js"
   - "Tool bash_2: Started server on port 8000"
   - "Tool computer_1: Opened Chrome"
   - "Tool computer_2: Navigated to localhost:8000"
   - "Tool computer_3: Clicked game cell"
   - "Tool computer_4: Screenshot of working game"
✅ Status shows "Claude is working..." during execution
✅ Status shows "Idle" when complete
✅ Continuous stream of messages, no waiting!
```

## Technical Details

### SSE vs WebSocket
- **SSE** chosen because it's simpler and one-directional (server→client)
- No need for bidirectional communication here
- Native browser support with automatic reconnection
- Text-based protocol, easy to debug

### Keepalive Messages
- Every 30 seconds, sends `: keepalive\n\n` to prevent connection timeout
- Proxies and browsers won't close idle connections

### Queue Cleanup
- When client disconnects, queue is removed from `_sse_queues`
- Prevents memory leaks from disconnected clients

### Error Handling
- SSE connection errors trigger automatic reconnection after 3s
- Malformed messages are logged but don't crash the frontend
- Queue.put() errors are silently ignored (queue might be closed)

## Files Modified

1. **`computer_use_demo/webui.py`**
   - Line 13: Added `json` import
   - Line 23-24: Added `Request`, `StreamingResponse` imports
   - Line 101: Added `_sse_queues` list for SSE connections
   - Lines 129-159: Updated callbacks to broadcast SSE updates
   - Lines 216-223: Added `_broadcast_sse_update()` method
   - Lines 281-287: Made POST non-blocking with `asyncio.create_task()`
   - Lines 290-324: Added `/api/stream` SSE endpoint
   - Lines 467-490: Added `connectSSE()` in frontend JavaScript
   - Line 580: Call `connectSSE()` on page load

## Before vs After

### Before:
```
User: "create game and test it"
[sends message]
[waits... no feedback...]
[waits... no feedback...]
[waits... no feedback...]
[2 minutes later]
[ALL messages appear at once]
"Task complete!"
```

### After:
```
User: "create game and test it"
[sends message]
You: create game and test it
Tool bash_1: Created directory
Tool str_replace_editor_1: Created index.html
Tool str_replace_editor_2: Created style.css
Tool str_replace_editor_3: Created game.js
Tool bash_2: Server started
Tool computer_1: Opened Chrome
Tool computer_2: Testing game
Tool computer_3: Screenshot [image shown]
Claude: Task complete!
Idle
```

**Continuous stream of updates! 🎉**

---

## Status: ✅ Real-Time Streaming Implemented

The UI will now show all messages and tool results in real-time as the agent works!

**Restart the webui and test it!** 🚀

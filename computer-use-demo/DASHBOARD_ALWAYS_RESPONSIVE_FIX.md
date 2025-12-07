# Dashboard Always Responsive - Real Fix Needed

## Current Problem

The dashboard becomes unresponsive when the agent is thinking/executing. This is because:

1. **Python GIL (Global Interpreter Lock)** - Only one thread can execute Python bytecode at a time
2. **Blocking API calls** - When agent calls Anthropic API, it blocks the event loop
3. **Single process** - Agent and web server run in same process

## Why Current Fixes Don't Work

- ✗ `asyncio.create_task()` - Still blocked by GIL during API calls
- ✗ `await asyncio.sleep(0)` - Doesn't help with blocking I/O
- ✗ `uvloop` - Faster event loop, but still single-threaded
- ✗ Middleware yielding - Can't yield during blocking operations

## Real Solution: Separate Processes

The ONLY way to truly fix this is to run the agent in a separate process from the web server.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Main Process: Web Server (Always Responsive)              │
│  - FastAPI endpoints                                        │
│  - Dashboard API                                            │
│  - Chat interface                                           │
│  - Never blocks                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ IPC (Queue/Pipe)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Worker Process: Agent (Can Block)                          │
│  - sampling_loop()                                           │
│  - Anthropic API calls                                       │
│  - Tool execution                                            │
│  - Can take minutes without affecting web server            │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Options

#### Option 1: multiprocessing.Process (Simple)
```python
from multiprocessing import Process, Queue

def agent_worker(queue):
    while True:
        message = queue.get()
        # Run sampling_loop in separate process
        result = sampling_loop(...)
        queue.put(result)

# In main():
agent_queue = Queue()
agent_process = Process(target=agent_worker, args=(agent_queue,))
agent_process.start()
```

#### Option 2: Celery (Production-grade)
```python
from celery import Celery

app = Celery('agent', broker='redis://localhost:6379')

@app.task
def run_agent(message):
    return sampling_loop(...)

# Web server sends tasks
run_agent.delay(user_message)
```

#### Option 3: Run agent in thread with run_in_executor
```python
import concurrent.futures

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

async def send(self, user_text: str):
    # Run blocking agent work in thread pool
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, self._run_agent_sync, user_text)
```

## Recommendation

**Use Option 3** (ThreadPoolExecutor) as it's:
- ✅ Simplest to implement
- ✅ No external dependencies
- ✅ Works with existing code structure
- ✅ Properly isolates blocking operations

## Implementation Steps

1. Create ThreadPoolExecutor in startup
2. Wrap sampling_loop in sync function
3. Use run_in_executor to run it
4. Dashboard stays responsive during execution

## Status

⚠️ **CRITICAL BUG**: Dashboard is currently unusable during agent execution
📋 **PRIORITY**: Must implement separate process/thread solution

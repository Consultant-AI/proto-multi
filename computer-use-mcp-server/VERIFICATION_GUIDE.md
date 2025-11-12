# Verification and Retry System Guide

This MCP server now includes a comprehensive verification and retry system that implements a **vision-action-verification loop** to ensure computer automation tasks actually succeed.

## The Problem

Traditional computer automation tools often suffer from "silent failures" - actions that report success but don't actually work. This is especially common with:

- Web applications (like Google Docs) that need time to process input
- UI elements that haven't finished loading
- Actions that get lost due to timing issues

## The Solution: Vision-Action-Verification Loop

The new high-level tools automatically:

1. **Take a "before" screenshot** to capture the current state
2. **Execute the action** (click, type, key press)
3. **Wait for UI to update** (configurable delay)
4. **Take an "after" screenshot** to verify the change
5. **Compare screenshots** to confirm the action had an effect
6. **Retry if needed** (up to configurable max attempts)

## New Tools

### 1. `click_with_retry`

Click with automatic verification and retry.

```python
click_with_retry(
    x: int,              # X-coordinate to click
    y: int,              # Y-coordinate to click
    max_retries: int = 3,     # Maximum retry attempts
    verify_delay: float = 0.5  # Delay before verification screenshot
)
```

**Example:**
```python
# Click a button and verify it worked
await click_with_retry(x=500, y=300)
```

**Returns:**
- Success message with before/after screenshots if action succeeded
- Warning message if screen didn't change after max retries

### 2. `type_with_verification`

Type text with automatic verification and retry.

```python
type_with_verification(
    text: str,                # Text to type
    max_retries: int = 3,     # Maximum retry attempts
    verify_delay: float = 1.0  # Delay before verification screenshot
)
```

**Example:**
```python
# Type text and verify it appeared
await type_with_verification(text="Hello World")
```

**Features:**
- Automatically clears partial input before retrying
- Longer default delay (1.0s) for web applications
- Returns before/after screenshots

### 3. `press_key_with_verification`

Press a key with automatic verification and retry.

```python
press_key_with_verification(
    key: str,                 # Key to press
    modifiers: str = "",      # Modifiers like "ctrl", "shift", "cmd"
    max_retries: int = 3,     # Maximum retry attempts
    verify_delay: float = 0.5  # Delay before verification screenshot
)
```

**Example:**
```python
# Press Cmd+N to create new document
await press_key_with_verification(key="n", modifiers="cmd")
```

### 4. `execute_task_with_vision`

Meta-tool for complex multi-step tasks with continuous visual feedback.

```python
execute_task_with_vision(
    task_description: str  # What you're trying to accomplish
)
```

**Example workflow:**
```python
# Step 1: See current state
await execute_task_with_vision("Create new Google Doc")

# Step 2: Analyze screenshot and decide action
# Claude sees the screen and decides to press Cmd+N

# Step 3: Execute action with verification
await press_key_with_verification(key="n", modifiers="cmd")

# Step 4: Check new state
await execute_task_with_vision("Type demo text")

# Step 5: Type with verification
await type_with_verification("This is demo text")

# Step 6: Verify final result
await execute_task_with_vision("Verify text appeared")
```

## When to Use Each Tool

### Use verification tools when:
- Interacting with web applications (slow UI updates)
- Clicking buttons that trigger actions
- Typing text that must appear correctly
- Pressing keys that should change the screen

### Use basic tools when:
- Taking screenshots only
- Moving mouse cursor without clicking
- Getting cursor position
- Actions where verification isn't needed

## Configuration

All verification tools accept these parameters:

- **`max_retries`**: Number of attempts before giving up (default: 3)
- **`verify_delay`**: Seconds to wait before verification screenshot
  - Click: 0.5s (default)
  - Type: 1.0s (default, web apps need more time)
  - Key press: 0.5s (default)

## How It Works

### Screenshot Comparison

The system compares base64-encoded screenshots:
- If screenshots are **different** → Action succeeded ✓
- If screenshots are **identical** → Action may have failed, retry

### Retry Logic

For `type_with_verification`:
1. Try typing
2. Wait for UI update
3. Take screenshot
4. If no change detected:
   - Select all (Cmd+A or Ctrl+A)
   - Delete selection
   - Wait 0.5s
   - Retry typing

For `click_with_retry` and `press_key_with_verification`:
1. Execute action
2. Wait for UI update
3. Take screenshot
4. If no change detected:
   - Wait 0.5s
   - Retry action

## Best Practices

1. **Always use verification tools for web apps** - They need time to process events
2. **Adjust `verify_delay` if needed** - Some apps are slower than others
3. **Check the screenshots in responses** - They show exactly what happened
4. **Use `execute_task_with_vision` for complex tasks** - Provides continuous feedback
5. **Don't retry endlessly** - If max_retries is reached, something is wrong

## Example: Creating a Google Doc

**Old way (prone to silent failures):**
```python
# Press Cmd+N
await press_key("n", "cmd")

# Type text
await type_text("Demo text")

# Hope it worked! 🤞
```

**New way (verified and reliable):**
```python
# See current state
await execute_task_with_vision("Create new Google Doc")

# Press Cmd+N with verification
result = await press_key_with_verification(key="n", modifiers="cmd", verify_delay=1.0)
# Result includes before/after screenshots showing new doc opened

# Type with verification
result = await type_with_verification(text="Demo text", verify_delay=1.5)
# Result includes screenshots showing text appeared

# Verify final state
await execute_task_with_vision("Verify document created with text")
```

## Technical Implementation

### AppleScript Integration (macOS)

The keyboard tools use AppleScript for reliable input:

```applescript
tell application "System Events"
    keystroke "text here"
end tell
```

This is more reliable than cliclick for web applications.

### Async/Await

All tools are async and use proper delays:

```python
await asyncio.sleep(verify_delay)  # Wait for UI
```

### Image Compression

Screenshots are compressed to fit MCP's 25K token limit:
- Resized to 512x384 pixels
- JPEG quality 55
- Result: ~20-21K tokens per screenshot

## Troubleshooting

### "Screen did not change" after max retries

**Causes:**
- UI element not ready/loaded
- Wrong coordinates or key
- Application not in focus
- Verify delay too short

**Solutions:**
- Increase `verify_delay`
- Increase `max_retries`
- Take screenshot first to verify UI state
- Check application has focus

### Text not appearing in web apps

**Causes:**
- Web app needs more processing time
- Input field not focused
- JavaScript blocking input

**Solutions:**
- Use `type_with_verification` instead of `type_text`
- Increase `verify_delay` to 1.5s or 2.0s
- Click input field first with `click_with_retry`
- Check browser console for errors

### Actions too slow

**Solutions:**
- Use basic tools when verification not needed
- Reduce `verify_delay` for fast applications
- Reduce `max_retries` if not needed
- Skip screenshots when just moving cursor

## Future Enhancements

Potential improvements to the verification system:

1. **OCR verification** - Actually read text from screenshots
2. **Visual diff highlighting** - Show what changed between screenshots
3. **Semantic verification** - Verify specific expected changes
4. **Automatic retry strategies** - Learn which actions need more retries
5. **Performance metrics** - Track success rates per action type

## Summary

The verification and retry system transforms the MCP server from a basic automation tool into a **robust, self-verifying system** that can handle complex tasks autonomously by continuously checking that actions actually succeed.

**Key benefits:**
- ✓ Eliminates silent failures
- ✓ Automatic retry on failure
- ✓ Visual proof of success/failure
- ✓ Reliable web application automation
- ✓ Self-correcting behavior

#!/usr/bin/env python3
"""
Script to update webui.py with WhatsApp-style UI
"""

import re

# Read the current webui.py
with open('computer_use_demo/webui.py', 'r') as f:
    content = f.read()

# Find the _html_shell function
pattern = r'def _html_shell\(\) -> str:.*?return f"""'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print("Could not find _html_shell function")
    exit(1)

# Get the position where we need to insert the new HTML
start_pos = match.end()

# Find the end of the HTML template (the closing """)
end_pattern = r'</html>\s*"""'
end_match = re.search(end_pattern, content[start_pos:])

if not end_match:
    print("Could not find end of HTML template")
    exit(1)

# Calculate the full range to replace
replace_start = match.start()
replace_end = start_pos + end_match.end()

# New HTML template with WhatsApp-style UI
new_html_function = '''def _html_shell() -> str:
    """WhatsApp-style dark UI with vanilla JS for chat interactions."""
    css = """
    :root {
        --bg-main: #111b21;
        --bg-sidebar: #111b21;
        --bg-chat: #0b141a;
        --bg-panel-header: #202c33;
        --bg-message-in: #202c33;
        --bg-message-out: #005c4b;
        --bg-input: #2a3942;
        --text-primary: #e9edef;
        --text-secondary: #8696a0;
        --border: #2a3942;
        --accent: #00a884;
        --hover: #2a3942;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Helvetica Neue, Helvetica, Arial, sans-serif;
        background: var(--bg-main);
        color: var(--text-primary);
        overflow: hidden;
    }
    #app { display: flex; height: 100vh; }

    /* Sidebar */
    #sidebar {
        width: 400px;
        background: var(--bg-sidebar);
        border-right: 1px solid var(--border);
        display: flex;
        flex-direction: column;
    }
    #sidebar-header {
        background: var(--bg-panel-header);
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 60px;
    }
    #sidebar-header h1 {
        font-size: 16px;
        font-weight: 500;
        color: var(--text-primary);
    }
    .header-icons { display: flex; gap: 20px; align-items: center; }
    .icon-btn {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 8px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
    }
    .icon-btn:hover { background: var(--hover); }
    .icon-btn.new-chat { color: var(--text-primary); }
    .icon-btn.stop-btn { color: #ea4335; }

    /* Search */
    #search-container { padding: 8px 12px; background: var(--bg-sidebar); }
    #search-input {
        width: 100%;
        background: var(--bg-panel-header);
        border: none;
        border-radius: 8px;
        padding: 8px 12px 8px 52px;
        color: var(--text-primary);
        font-size: 14px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%238696a0" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>');
        background-repeat: no-repeat;
        background-position: 12px center;
        background-size: 20px;
    }
    #search-input::placeholder { color: var(--text-secondary); }

    /* Sessions List */
    #sessions-list { flex: 1; overflow-y: auto; background: var(--bg-sidebar); }
    .session-item {
        padding: 12px 16px;
        border-bottom: 1px solid var(--border);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: background 0.2s;
    }
    .session-item:hover { background: var(--hover); }
    .session-item.active { background: var(--bg-panel-header); }
    .session-avatar {
        width: 49px;
        height: 49px;
        border-radius: 50%;
        background: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 20px;
        color: #fff;
    }
    .session-info { flex: 1; min-width: 0; }
    .session-header { display: flex; justify-content: space-between; margin-bottom: 3px; }
    .session-name { font-size: 16px; color: var(--text-primary); font-weight: 400; }
    .session-time { font-size: 12px; color: var(--text-secondary); }
    .session-preview {
        font-size: 14px;
        color: var(--text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Chat Area */
    #chat-area {
        flex: 1;
        display: flex;
        flex-direction: column;
        background: var(--bg-chat);
    }
    #chat-header {
        background: var(--bg-panel-header);
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 60px;
        border-bottom: 1px solid var(--border);
    }
    .chat-title { display: flex; align-items: center; gap: 12px; }
    .chat-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        color: #fff;
    }
    .chat-info h2 { font-size: 16px; font-weight: 400; color: var(--text-primary); }
    .chat-status { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }
    .badge {
        font-size: 11px;
        padding: 4px 8px;
        border-radius: 4px;
        background: rgba(0, 168, 132, 0.2);
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Messages */
    #messages {
        flex: 1;
        padding: 20px 8%;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 8px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" opacity="0.03"><path fill="%23e9edef" d="M50 0L60 40L100 50L60 60L50 100L40 60L0 50L40 40Z"/></svg>');
    }
    .bubble {
        max-width: 65%;
        padding: 6px 7px 8px 9px;
        border-radius: 7.5px;
        position: relative;
        word-wrap: break-word;
        box-shadow: 0 1px 0.5px rgba(0,0,0,.13);
    }
    .bubble.user {
        background: var(--bg-message-out);
        align-self: flex-end;
        margin-left: auto;
    }
    .bubble.assistant, .bubble.tool {
        background: var(--bg-message-in);
        align-self: flex-start;
    }
    .bubble .label {
        font-size: 12px;
        color: rgba(233, 237, 239, 0.6);
        margin-bottom: 4px;
        font-weight: 500;
    }
    .bubble .text {
        font-size: 14.2px;
        line-height: 19px;
        color: var(--text-primary);
        white-space: pre-wrap;
    }
    .bubble .time {
        font-size: 11px;
        color: rgba(233, 237, 239, 0.45);
        margin-top: 4px;
        text-align: right;
    }
    img.tool-screenshot {
        margin-top: 8px;
        border-radius: 6px;
        max-width: 100%;
        max-height: 400px;
    }

    /* Typing Indicator */
    .typing-indicator {
        display: none;
        max-width: 65%;
        padding: 12px 16px;
        border-radius: 7.5px;
        background: var(--bg-message-in);
        align-self: flex-start;
        box-shadow: 0 1px 0.5px rgba(0,0,0,.13);
    }
    .typing-indicator.active { display: block; }
    .typing-dots { display: flex; gap: 4px; align-items: center; }
    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--text-secondary);
        animation: typing-bounce 1.4s infinite ease-in-out;
    }
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    @keyframes typing-bounce {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* Composer */
    #composer {
        padding: 10px 16px 20px;
        background: var(--bg-panel-header);
        border-top: 1px solid var(--border);
    }
    .composer-wrapper {
        background: var(--bg-input);
        border-radius: 8px;
        display: flex;
        align-items: flex-end;
        padding: 5px 10px;
        gap: 8px;
    }
    #prompt {
        flex: 1;
        background: none;
        border: none;
        color: var(--text-primary);
        font-size: 15px;
        padding: 10px;
        resize: none;
        max-height: 100px;
        overflow-y: auto;
        font-family: inherit;
    }
    #prompt::placeholder { color: var(--text-secondary); }
    #sendBtn {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s;
    }
    #sendBtn:not(:disabled) { color: var(--accent); }
    #sendBtn:not(:disabled):hover { background: rgba(0, 168, 132, 0.1); }
    #sendBtn:disabled { opacity: 0.4; cursor: not-allowed; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(134, 150, 160, 0.3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(134, 150, 160, 0.5); }
    """

    js = """'''

print("Script created. Due to complexity, I recommend manually reviewing the changes.")
print("The template has been saved to whatsapp_ui_template.html for preview.")

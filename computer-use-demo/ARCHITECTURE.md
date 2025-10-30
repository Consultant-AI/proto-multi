# Computer Use Demo - Architecture Documentation

## Overview

This project is an AI-powered computer control demonstration that allows Claude (Anthropic's AI assistant) to interact with and control a Ubuntu 24.04 LTS virtual machine through a web-based interface. The system uses computer vision and desktop automation to enable Claude to perform tasks like a human user would.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                          │
│  ┌──────────────────────┐         ┌──────────────────────────┐ │
│  │  Streamlit Chat UI   │         │   noVNC Desktop View     │ │
│  │   (Port 8501)        │         │    (Port 6080)           │ │
│  └──────────────────────┘         └──────────────────────────┘ │
│                    Combined Interface (Port 8080)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Container (Ubuntu 24.04)              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  Streamlit Application                    │ │
│  │  - Chat interface for user interaction                   │ │
│  │  - Message history management                            │ │
│  │  - HTTP request/response logging                         │ │
│  │  - Configuration settings (API keys, models, etc.)       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   Agent Loop (loop.py)                    │ │
│  │  - Manages Claude API communication                       │ │
│  │  - Implements agentic sampling loop                       │ │
│  │  - Handles prompt caching and image optimization          │ │
│  │  - Supports Anthropic API, Bedrock, and Vertex           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  Tool Collection                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐  │ │
│  │  │  Computer   │  │    Bash     │  │  Text Editor     │  │ │
│  │  │  (Vision &  │  │  (Command   │  │  (File editing   │  │ │
│  │  │   Control)  │  │  Execution) │  │   tool)          │  │ │
│  │  └─────────────┘  └─────────────┘  └──────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              X11 Desktop Environment                      │ │
│  │  ┌────────────┐  ┌──────────┐  ┌────────────────────┐    │ │
│  │  │   Xvfb     │  │  Mutter  │  │      Tint2         │    │ │
│  │  │ (Virtual   │  │ (Window  │  │  (Modern Panel     │    │ │
│  │  │  Display)  │  │ Manager) │  │   with Arc Theme)  │    │ │
│  │  └────────────┘  └──────────┘  └────────────────────┘    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   User Applications                       │ │
│  │  - Google Chrome (--no-sandbox)                          │ │
│  │  - Firefox                                               │ │
│  │  - Visual Studio Code (--no-sandbox)                     │ │
│  │  - LibreOffice Suite                                     │ │
│  │  - File Manager (PCManFM)                                │ │
│  │  - Text Editor (gedit)                                   │ │
│  │  - Calculator (galculator)                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   VNC/Display Services                    │ │
│  │  - x11vnc: VNC server (Port 5900)                        │ │
│  │  - noVNC: Web-based VNC client (Port 6080)               │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Claude API Services                      │
│  - Anthropic API (claude-sonnet-4-5-20250929)                  │
│  - AWS Bedrock                                                  │
│  - Google Cloud Vertex AI                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

#### Streamlit Web Interface (`streamlit.py`)
- **Purpose**: Provides the main chat interface for users to communicate with Claude
- **Features**:
  - Real-time chat interface with message history
  - API provider configuration (Anthropic, Bedrock, Vertex)
  - Model selection and parameter tuning
  - Screenshot management and optimization
  - HTTP exchange logging for debugging
  - Custom system prompt configuration
- **Port**: 8501
- **Technology**: Python Streamlit framework

#### noVNC Web Client
- **Purpose**: Provides web-based access to the Ubuntu desktop
- **Features**:
  - Browser-based VNC client
  - Real-time desktop visualization
  - Allows users to see what Claude is doing
- **Port**: 6080 (web interface), 5900 (VNC protocol)
- **Technology**: noVNC (JavaScript VNC client)

#### Combined Interface
- **Purpose**: Unified view of chat and desktop
- **Features**:
  - Side-by-side chat and desktop view
  - Seamless user experience
- **Port**: 8080
- **Technology**: Custom HTTP server (`http_server.py`)

### 2. Agent Layer

#### Agent Loop (`loop.py`)
- **Purpose**: Orchestrates the interaction between Claude API and local tools
- **Key Functions**:
  - `sampling_loop()`: Main async loop that sends messages to Claude API and processes responses
  - Tool execution coordination
  - Message history management
  - Image optimization (limiting recent screenshots to reduce token usage)
  - Prompt caching for improved performance
- **API Support**:
  - Anthropic Direct API
  - AWS Bedrock
  - Google Cloud Vertex AI

#### System Prompt
- Provides Claude with context about the Ubuntu 24.04 environment
- Lists available applications and how to launch them
- Includes best practices for computer use
- Warns about startup wizards and common pitfalls

### 3. Tool Layer

#### Computer Tool (`tools/computer.py`)
- **Purpose**: Computer vision and control interface
- **Capabilities**:
  - Take screenshots using `scrot`
  - Simulate mouse clicks and movements using `xdotool`
  - Simulate keyboard input
  - Cursor position tracking
  - Screen resolution scaling (optimized for XGA/1024x768)
- **Implementation**: Uses X11 utilities for desktop automation

#### Bash Tool (`tools/bash.py`)
- **Purpose**: Execute shell commands
- **Capabilities**:
  - Run arbitrary bash commands
  - Capture stdout and stderr
  - Restart functionality for long-running processes
- **Security**: Runs in isolated container environment

#### Text Editor Tool (`tools/edit.py`)
- **Purpose**: File editing capabilities
- **Capabilities**:
  - Read file contents
  - String-based find and replace
  - Create new files
  - Edit existing files
- **Version**: Uses `str_replace_based_edit_tool` (latest version)

### 4. Desktop Environment Layer

#### Display Server
- **Xvfb**: Virtual framebuffer X11 server
  - Runs X11 without physical display
  - Configurable resolution (default: 1024x768)
  - Display number: :1

#### Window Manager
- **Mutter**: Compositing window manager
  - Provides window decorations
  - Manages window placement and behavior
  - Lightweight and stable

#### Panel/Launcher
- **Tint2**: Modern taskbar and application launcher
  - **Theme**: Arc-Dark with Papirus icons
  - **Features**:
    - Application launcher with 8 quick-launch icons
    - Task manager showing open windows
    - System tray support
    - Modern, clean UI with transparency
  - **Pre-configured Apps**:
    1. Google Chrome
    2. Firefox
    3. Visual Studio Code
    4. LibreOffice
    5. Terminal (xterm)
    6. Text Editor (gedit)
    7. File Manager (PCManFM)
    8. Calculator

#### Theme Configuration
- **GTK Theme**: Arc-Dark (modern, flat design)
- **Icon Theme**: Papirus-Dark (comprehensive icon set)
- **Font**: Noto Sans (clean, readable)
- **Color Scheme**: Modern dark theme with blue accents

### 5. Application Layer

#### Web Browsers
1. **Google Chrome**
   - Latest stable version
   - Runs with `--no-sandbox` flag for container compatibility
   - Full JavaScript and modern web features
   - Best for web automation tasks

2. **Firefox**
   - Standard Firefox (not ESR in Ubuntu 24.04)
   - Mozilla PPA for updates
   - Alternative browser option

#### Development Tools
1. **Visual Studio Code**
   - Full-featured IDE
   - Runs with `--no-sandbox` flag
   - Extension support
   - Integrated terminal
   - Git integration

#### Productivity Suite
1. **LibreOffice**
   - Complete office suite (Writer, Calc, Impress, Draw)
   - GTK3 integration for native look
   - Document creation and editing
   - Spreadsheet manipulation
   - Presentation creation

#### Utilities
- **PCManFM**: Lightweight file manager
- **gedit**: Text editor with syntax highlighting
- **galculator**: Calculator application
- **xterm**: Terminal emulator
- **xpdf**: PDF viewer
- **xpaint**: Simple paint application

### 6. Infrastructure Layer

#### Docker Container
- **Base Image**: Ubuntu 24.04 LTS (Noble Numbat)
- **Architecture**: Multi-platform (amd64 primary, arm64 supported)
- **User**: Non-root user `computeruse` with sudo privileges
- **Python**: Version 3.11.6 (via pyenv)
- **Network**: Exposes ports 5900, 6080, 8080, 8501

#### Startup Sequence (`entrypoint.sh`)
1. Start X11 services (`start_all.sh`)
   - Xvfb virtual display
   - Window manager (Mutter)
   - Panel (Tint2)
   - x11vnc VNC server
2. Start noVNC web client
3. Start HTTP server (combined interface)
4. Start Streamlit application

## Data Flow

### User Request Flow
1. User types message in Streamlit chat interface
2. Message is added to conversation history
3. Agent loop sends message + history to Claude API
4. Claude analyzes the request and decides which tools to use
5. Tool results are captured and sent back to Claude
6. Claude processes results and may request more tool uses
7. Final response is displayed to user

### Tool Execution Flow
1. Claude decides to use a tool (e.g., computer, bash, edit)
2. Tool collection routes request to appropriate tool
3. Tool executes action in Ubuntu environment
4. Results (text, screenshot, error) are captured
5. Results are formatted and returned to Claude
6. Screenshots are base64-encoded and included in response

### Screenshot Optimization
1. Every computer tool use captures a screenshot
2. Recent screenshots are kept in conversation history
3. Older screenshots are removed to reduce token usage
4. Parameter `only_n_most_recent_images` controls retention
5. Prompt caching ensures efficient API usage

## Security Considerations

### Container Isolation
- All operations run inside isolated Docker container
- No direct access to host system
- Limited resource allocation

### Sandboxing
- Chrome and VSCode run with `--no-sandbox` flags
  - Required for container environment
  - Acceptable as container provides isolation
- Non-root user reduces privilege escalation risks

### API Security
- API keys stored in `~/.anthropic/` directory
- Mounted as volume for persistence
- File permissions set to 0600 (user read/write only)

### Network Security
- Container has internet access for functionality
- No production data should be accessible
- Recommended to use on isolated network or with firewall rules

## Performance Optimizations

### Prompt Caching
- Caches system prompt and recent conversation turns
- Reduces API latency and costs
- Automatic cache breakpoint management

### Image Management
- Limits number of screenshots in context
- Configurable threshold for image removal
- Prevents token bloat from excessive images

### Display Scaling
- Desktop runs at XGA resolution (1024x768)
- Optimal for Claude's vision capabilities
- Higher resolutions are downscaled to prevent resizing

### Asynchronous Operations
- Async/await pattern throughout codebase
- Non-blocking tool execution
- Efficient concurrent operations

## Configuration

### Environment Variables
- `ANTHROPIC_API_KEY`: Claude API key
- `API_PROVIDER`: anthropic|bedrock|vertex
- `WIDTH`: Display width (default: 1024)
- `HEIGHT`: Display height (default: 768)
- `DISPLAY_NUM`: X11 display number (default: 1)

### Persistent Storage
- `~/.anthropic/`: Configuration directory
  - `api_key`: Stored API key
  - `system_prompt`: Custom system prompt suffix
  - Error logs and debugging information

### Model Configuration
- Default model: claude-sonnet-4-5-20250929
- Configurable output tokens (default: 16K for Claude 4.5)
- Optional thinking budget for extended reasoning
- Tool version selection (computer_use_20250124 for latest models)

## Development Workflow

### Local Development
1. Run `./setup.sh` to configure development environment
2. Build Docker image: `docker build . -t computer-use-demo:local`
3. Run container with local code mounted
4. Streamlit auto-reloads on file changes

### Testing
- Unit tests in `tests/` directory
- Test coverage for tools, loop, and streamlit components
- Run tests with pytest

### Debugging
- HTTP exchange logs available in UI
- Streamlit logs: `/tmp/streamlit_stdout.log`
- Server logs: `/tmp/server_logs.txt`
- VNC errors: `/tmp/tint2_stderr.log`, etc.

## Deployment

### Docker Deployment
```bash
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -it ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
```

### Access Points
- **Main Interface**: http://localhost:8080
- **Chat Only**: http://localhost:8501
- **Desktop Only**: http://localhost:6080/vnc.html
- **VNC Client**: vnc://localhost:5900

## Future Enhancements

### Potential Improvements
1. Multi-user support with session isolation
2. Recording and replay of agent sessions
3. Enhanced security with more granular permissions
4. Additional productivity applications
5. Integration with more Claude API features
6. Performance metrics and analytics
7. Automated testing framework for agent behaviors

### Scalability Considerations
1. Kubernetes deployment for multiple instances
2. Load balancing for concurrent users
3. Shared storage for application data
4. Resource limits and quotas
5. Monitoring and alerting

## Troubleshooting

### Common Issues

#### Display not showing
- Check Xvfb is running: `ps aux | grep Xvfb`
- Verify DISPLAY environment variable: `echo $DISPLAY`
- Check VNC server logs: `tail -f /tmp/*.log`

#### Applications won't launch
- Ensure `--no-sandbox` flags for Chrome/VSCode
- Check file permissions on desktop entries
- Verify applications installed: `which google-chrome code`

#### API errors
- Verify API key is set correctly
- Check internet connectivity
- Review HTTP exchange logs in UI
- Ensure correct API provider selected

#### Performance issues
- Reduce screenshot retention count
- Enable prompt caching
- Lower display resolution
- Limit concurrent tool executions

## References

- [Anthropic Computer Use Documentation](https://docs.claude.com/en/docs/build-with-claude/computer-use)
- [Claude API Documentation](https://docs.claude.com/en/api)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [noVNC Project](https://github.com/novnc/noVNC)
- [Tint2 Configuration](https://gitlab.com/o9000/tint2)
- [Arc Theme](https://github.com/jnsh/arc-theme)
- [Papirus Icons](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)

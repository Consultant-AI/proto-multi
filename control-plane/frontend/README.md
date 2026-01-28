# CloudBot Platform - Frontend

React + TypeScript frontend for the CloudBot cloud platform. Provides user authentication, instance management, remote desktop viewing (noVNC), and CloudBot chat interface.

## Features

- User authentication (signup, login, API key management)
- Instance management (create, list, start, stop, delete)
- Remote desktop streaming (noVNC WebSocket client)
- CloudBot chat interface (reusing CloudBot UI components)
- Split-view layout (desktop + chat side-by-side)
- Responsive design with TailwindCSS

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Remote Desktop**: noVNC (@novnc/novnc)
- **State Management**: React Context + hooks

## Prerequisites

- Node.js 18+ or 22+
- npm or pnpm

## Development Setup

1. **Install dependencies**:
```bash
npm install
```

2. **Create environment file**:
```bash
cp .env.example .env
```

3. **Update `.env` with API endpoints**:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

4. **Start development server**:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Scripts

```bash
npm run dev          # Start development server with hot reload
npm run build        # Build for production
npm run preview      # Preview production build locally
npm run lint         # Run ESLint
```

## License

MIT

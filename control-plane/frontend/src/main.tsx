import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// StrictMode disabled temporarily to debug WebSocket connection stability
// TODO: Re-enable after fixing the connection issue
createRoot(document.getElementById('root')!).render(
  <App />,
)

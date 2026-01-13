const { app, BrowserWindow, session, screen, ipcMain } = require('electron')
const path = require('path')

function createWindow() {
  // Get full screen dimensions
  const primaryDisplay = screen.getPrimaryDisplay()
  const { width, height } = primaryDisplay.workAreaSize

  const win = new BrowserWindow({
    width,
    height,
    x: 0,
    y: 0,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      webviewTag: true,  // Enable <webview> for embedding browsers
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: true,
    },
    // Modern look for macOS
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    trafficLightPosition: { x: 15, y: 15 },
  })

  // Set a user agent that looks like regular Chrome
  session.defaultSession.webRequest.onBeforeSendHeaders((details, callback) => {
    details.requestHeaders['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    callback({ requestHeaders: details.requestHeaders })
  })

  // Development: load Vite dev server
  // Production: load built files
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged

  if (isDev) {
    // Try to load from Vite dev server
    win.loadURL('http://localhost:3000').catch(() => {
      // Fallback to file if dev server not running
      win.loadFile(path.join(__dirname, '../dist/index.html'))
    })
    // DevTools can be opened manually with Cmd+Option+I
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // Handle window close
  win.on('closed', () => {
    app.quit()
  })

  // IPC handler for toggling window maximize (macOS double-click title bar behavior)
  ipcMain.handle('toggle-maximize', () => {
    const { width: fullWidth, height: fullHeight } = screen.getPrimaryDisplay().workAreaSize
    const bounds = win.getBounds()

    // Check if currently at full size
    if (bounds.width === fullWidth && bounds.height === fullHeight && bounds.x === 0 && bounds.y === 0) {
      // Shrink to smaller centered window
      const smallWidth = 1200
      const smallHeight = 800
      const x = Math.round((fullWidth - smallWidth) / 2)
      const y = Math.round((fullHeight - smallHeight) / 2)
      win.setBounds({ x, y, width: smallWidth, height: smallHeight })
    } else {
      // Go to full size
      win.setBounds({ x: 0, y: 0, width: fullWidth, height: fullHeight })
    }
  })
}

// App ready
app.whenReady().then(() => {
  createWindow()

  // macOS: re-create window when dock icon clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

// Quit when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// Security: handle new window from webview
app.on('web-contents-created', (_, contents) => {
  if (contents.getType() === 'webview') {
    contents.setWindowOpenHandler(({ url }) => {
      // Load URL in the same webview
      contents.loadURL(url)
      return { action: 'deny' }
    })
  }
})

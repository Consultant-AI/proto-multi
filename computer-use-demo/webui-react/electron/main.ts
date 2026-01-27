import { app, BrowserWindow, session, ipcMain, screen } from 'electron'
import * as path from 'path'
import Store from 'electron-store'

// Initialize persistent store for window state
const store = new Store()

function createWindow() {
  // Get full screen dimensions
  const primaryDisplay = screen.getPrimaryDisplay()
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize

  // Load saved window bounds or use defaults
  const savedBounds = store.get('windowBounds', {
    width: screenWidth,
    height: screenHeight,
    x: 0,
    y: 0
  }) as { width: number; height: number; x: number; y: number }

  console.log('Loading window with bounds:', savedBounds)
  console.log('Screen size:', screenWidth, 'x', screenHeight)

  const win = new BrowserWindow({
    width: savedBounds.width,
    height: savedBounds.height,
    x: savedBounds.x,
    y: savedBounds.y,
    minWidth: 200,
    minHeight: 200,
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
  if (process.env.VITE_DEV_SERVER_URL) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL)
    win.webContents.openDevTools()
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  // Save window bounds when resized or moved
  const saveBounds = () => {
    if (!win.isMaximized() && !win.isMinimized() && !win.isFullScreen()) {
      const bounds = win.getBounds()
      console.log('Saving window bounds:', bounds)
      store.set('windowBounds', bounds)
      console.log('Saved to store. Verifying:', store.get('windowBounds'))
    } else {
      console.log('Not saving bounds - window is maximized/minimized/fullscreen')
    }
  }

  // Debounce save to avoid excessive writes
  let saveBoundsTimeout: NodeJS.Timeout | null = null
  const debouncedSaveBounds = () => {
    if (saveBoundsTimeout) clearTimeout(saveBoundsTimeout)
    saveBoundsTimeout = setTimeout(saveBounds, 500)
  }

  win.on('resize', debouncedSaveBounds)
  win.on('move', debouncedSaveBounds)

  // Save bounds before closing
  win.on('close', () => {
    if (saveBoundsTimeout) clearTimeout(saveBoundsTimeout)
    saveBounds()
  })

  // Handle window close
  win.on('closed', () => {
    app.quit()
  })

  // IPC handler for toggling window maximize (macOS double-click title bar behavior)
  ipcMain.handle('toggle-maximize', () => {
    if (win.isMaximized()) {
      win.unmaximize()
    } else {
      win.maximize()
    }
    return win.isMaximized()
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

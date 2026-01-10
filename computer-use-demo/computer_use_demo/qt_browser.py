"""
Qt WebEngine Browser - Real Chromium browser for the application.
This provides a true browser experience with zero bot detection.
"""

# CRITICAL: Enable Chrome DevTools Protocol BEFORE importing Qt
# This allows us to send trusted input events via CDP
import os
os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '9222'

import sys
import base64
import json
from PyQt6.QtCore import QUrl, QTimer, pyqtSignal, QObject, QBuffer, QByteArray, QIODevice, Qt, QPointF, QEvent
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtGui import QImage, QMouseEvent, QKeyEvent
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtWebSockets import QWebSocket


class CDPClient(QObject):
    """Chrome DevTools Protocol client for sending trusted input events.

    CDP allows us to send Input.dispatchMouseEvent commands that create
    truly trusted events (isTrusted: true) in the browser, bypassing
    bot detection on sites like Google.
    """

    def __init__(self):
        super().__init__()
        self.ws = QWebSocket()
        self.ws.connected.connect(self._on_connected)
        self.ws.disconnected.connect(self._on_disconnected)
        self.ws.textMessageReceived.connect(self._on_message)
        self.ws.errorOccurred.connect(self._on_error)

        self._msg_id = 0
        self._connected = False
        self._page_ws_url = None

        # HTTP manager to fetch page info
        self._http = QNetworkAccessManager(self)
        self._http.finished.connect(self._on_page_info_received)

        # Retry timer for connection
        self._retry_timer = QTimer(self)
        self._retry_timer.timeout.connect(self._fetch_page_info)
        self._retry_timer.setInterval(2000)

        # Start fetching page info after a short delay (let browser initialize)
        QTimer.singleShot(1000, self._fetch_page_info)

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _fetch_page_info(self):
        """Fetch available pages from CDP endpoint."""
        request = QNetworkRequest(QUrl("http://localhost:9222/json"))
        self._http.get(request)

    def _on_page_info_received(self, reply: QNetworkReply):
        """Handle CDP page list response."""
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                print(f"CDP: Failed to get page info: {reply.errorString()}")
                if not self._retry_timer.isActive():
                    self._retry_timer.start()
                reply.deleteLater()
                return

            data = json.loads(reply.readAll().data().decode())
            if data and len(data) > 0:
                # Get the first page's WebSocket URL
                self._page_ws_url = data[0].get('webSocketDebuggerUrl')
                if self._page_ws_url:
                    print(f"CDP: Found page, connecting to {self._page_ws_url}")
                    self._retry_timer.stop()
                    self.ws.open(QUrl(self._page_ws_url))
                else:
                    print("CDP: No webSocketDebuggerUrl in page info")
                    if not self._retry_timer.isActive():
                        self._retry_timer.start()
            else:
                print("CDP: No pages available yet")
                if not self._retry_timer.isActive():
                    self._retry_timer.start()
        except Exception as e:
            print(f"CDP: Error parsing page info: {e}")
            if not self._retry_timer.isActive():
                self._retry_timer.start()
        finally:
            reply.deleteLater()

    def _on_connected(self):
        """CDP WebSocket connected."""
        self._connected = True
        self._retry_timer.stop()
        print("✓ CDP connected - clicks will be trusted!")

    def _on_disconnected(self):
        """CDP WebSocket disconnected."""
        self._connected = False
        print("⚠ CDP disconnected, reconnecting...")
        QTimer.singleShot(2000, self._fetch_page_info)

    def _on_error(self, error):
        """CDP WebSocket error."""
        self._connected = False
        print(f"⚠ CDP error: {error}")

    def _on_message(self, message: str):
        """Handle CDP response (mostly for debugging)."""
        try:
            data = json.loads(message)
            if 'error' in data:
                print(f"CDP error: {data['error']}")
        except:
            pass

    def _send(self, method: str, params: dict = None):
        """Send a CDP command."""
        if not self._connected:
            return False

        self._msg_id += 1
        msg = {
            'id': self._msg_id,
            'method': method,
            'params': params or {}
        }
        self.ws.sendTextMessage(json.dumps(msg))
        return True

    def click(self, x: int, y: int):
        """Send a trusted click via CDP Input.dispatchMouseEvent."""
        if not self._connected:
            return False

        print(f"CDP: Sending trusted click at ({x}, {y})")

        # Send mousePressed
        self._send('Input.dispatchMouseEvent', {
            'type': 'mousePressed',
            'x': x,
            'y': y,
            'button': 'left',
            'clickCount': 1
        })

        # Send mouseReleased after a small delay
        def send_release():
            self._send('Input.dispatchMouseEvent', {
                'type': 'mouseReleased',
                'x': x,
                'y': y,
                'button': 'left',
                'clickCount': 1
            })

        QTimer.singleShot(50, send_release)
        return True

    def type_text(self, text: str):
        """Send text input via CDP Input.insertText."""
        if not self._connected:
            return False

        print(f"CDP: Typing text: {text[:20]}...")
        self._send('Input.insertText', {'text': text})
        return True

    def press_key(self, key: str):
        """Send a key press via CDP Input.dispatchKeyEvent."""
        if not self._connected:
            return False

        # Map common key names to CDP key codes
        key_map = {
            'Enter': {'key': 'Enter', 'code': 'Enter', 'keyCode': 13},
            'Tab': {'key': 'Tab', 'code': 'Tab', 'keyCode': 9},
            'Escape': {'key': 'Escape', 'code': 'Escape', 'keyCode': 27},
            'Backspace': {'key': 'Backspace', 'code': 'Backspace', 'keyCode': 8},
        }

        key_info = key_map.get(key, {'key': key, 'code': key, 'keyCode': 0})

        # keyDown
        self._send('Input.dispatchKeyEvent', {
            'type': 'keyDown',
            **key_info
        })

        # keyUp
        def send_keyup():
            self._send('Input.dispatchKeyEvent', {
                'type': 'keyUp',
                **key_info
            })

        QTimer.singleShot(50, send_keyup)
        return True


class BrowserCommunicator(QObject):
    """Handles communication with FastAPI backend using WebSocket (no polling)."""

    navigate_signal = pyqtSignal(str)
    click_signal = pyqtSignal(int, int)
    type_signal = pyqtSignal(str, bool)
    pause_signal = pyqtSignal()
    resume_signal = pyqtSignal()

    def __init__(self, backend_url="http://127.0.0.1:8000"):
        super().__init__()
        self.backend_url = backend_url
        ws_url = backend_url.replace("http://", "ws://").replace("https://", "wss://")

        # WebSocket for receiving commands (no polling!)
        self.command_socket = QWebSocket()
        self.command_socket.textMessageReceived.connect(self._handle_command)
        self.command_socket.connected.connect(self._on_connected)
        self.command_socket.disconnected.connect(self._on_disconnected)
        self.command_socket.errorOccurred.connect(self._on_error)

        # Connect to WebSocket endpoint
        self.ws_url = f"{ws_url}/ws/qt-browser/commands"
        self.command_socket.open(QUrl(self.ws_url))

        # Non-blocking HTTP for screenshots (still needed)
        self.screenshot_manager = QNetworkAccessManager(self)
        self.screenshot_manager.finished.connect(self._screenshot_finished)

        # HTTP manager for polling commands (fallback)
        self.command_manager = QNetworkAccessManager(self)
        self.command_manager.finished.connect(self._command_poll_finished)

        # Poll for commands every 500ms as fallback
        self._ws_connected = False
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self._poll_commands)
        self.poll_timer.start(500)

        # Throttling flag - don't send new screenshot until previous finished
        self._screenshot_pending = False

    def _poll_commands(self):
        """Poll for commands when WebSocket not connected."""
        if self._ws_connected:
            return
        request = QNetworkRequest(QUrl(f"{self.backend_url}/api/qt-browser/command"))
        self.command_manager.get(request)

    def _command_poll_finished(self, reply: QNetworkReply):
        """Handle polled command."""
        try:
            if reply.error() == QNetworkReply.NetworkError.NoError:
                data = json.loads(reply.readAll().data().decode())
                if data and data.get("command"):
                    self._handle_command(json.dumps(data))
        except:
            pass
        reply.deleteLater()

    def _on_connected(self):
        """WebSocket connected - no more polling needed."""
        self._ws_connected = True
        print("✓ Connected to backend via WebSocket")

    def _on_disconnected(self):
        """WebSocket disconnected - try to reconnect."""
        self._ws_connected = False
        print("⚠ WebSocket disconnected, reconnecting in 2s...")
        QTimer.singleShot(2000, lambda: self.command_socket.open(QUrl(self.ws_url)))

    def _on_error(self, error):
        """WebSocket error - try to reconnect."""
        self._ws_connected = False
        print(f"⚠ WebSocket error: {error}, reconnecting in 2s...")
        QTimer.singleShot(2000, lambda: self.command_socket.open(QUrl(self.ws_url)))

    def _handle_command(self, message: str):
        """Handle command received via WebSocket (instant, no polling)."""
        try:
            data = json.loads(message)
            command = data.get("command")

            if command == "navigate":
                url = data.get("url")
                if url:
                    self.navigate_signal.emit(url)

            elif command == "click":
                x = data.get("x")
                y = data.get("y")
                if x is not None and y is not None:
                    self.click_signal.emit(x, y)

            elif command == "type":
                text = data.get("text", "")
                enter = data.get("enter", False)
                self.type_signal.emit(text, enter)

            elif command == "pause":
                self.pause_signal.emit()

            elif command == "resume":
                self.resume_signal.emit()
        except Exception as e:
            print(f"Error handling command: {e}")

    def send_screenshot(self, screenshot_b64):
        """Send screenshot to backend (non-blocking with throttling)."""
        # Skip if previous request still pending - prevents request buildup
        if self._screenshot_pending:
            return

        self._screenshot_pending = True
        data = json.dumps({"screenshot": screenshot_b64}).encode('utf-8')
        request = QNetworkRequest(QUrl(f"{self.backend_url}/api/qt-browser/screenshot"))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        self.screenshot_manager.post(request, data)

    def _screenshot_finished(self, reply: QNetworkReply):
        """Mark screenshot request as finished."""
        self._screenshot_pending = False
        reply.deleteLater()


class QtBrowser(QMainWindow):
    """Real Chromium browser using Qt WebEngine."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proto Browser (Qt WebEngine)")
        self.setGeometry(100, 100, 1920, 1080)

        # Create web engine view
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # Set normal arrow cursor for the browser
        self.browser.setCursor(Qt.CursorShape.ArrowCursor)

        # Enable all features for full browser experience
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        # Set up communicator
        self.communicator = BrowserCommunicator()
        self.communicator.navigate_signal.connect(self.navigate)
        self.communicator.click_signal.connect(self.handle_click)
        self.communicator.type_signal.connect(self.handle_type)
        self.communicator.pause_signal.connect(self.pause_capture)
        self.communicator.resume_signal.connect(self.resume_capture)

        # CDP client for trusted input events (bypasses bot detection)
        self.cdp_client = CDPClient()

        # Screenshot timer - capture at 10 FPS (controlled by pause/resume)
        self.screenshot_timer = QTimer()
        self.screenshot_timer.timeout.connect(self.capture_screenshot)

        # No command timer needed - WebSocket receives commands instantly

        # Start paused - screenshots won't capture until resumed
        self.is_paused = True

        # Start with blank page
        self.browser.setUrl(QUrl("about:blank"))

    def navigate(self, url: str):
        """Navigate to a URL."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        print(f"Navigating to: {url}")
        self.browser.setUrl(QUrl(url))

    def handle_click(self, x: int, y: int):
        """Handle click - use CDP for trusted events, fallback to Qt events."""
        # Try CDP first (creates truly trusted events)
        if self.cdp_client.is_connected:
            self.cdp_client.click(x, y)
            return

        # Fallback to Qt mouse events (works for local files, may fail on external sites)
        print(f"Clicking at ({x}, {y}) using Qt events (CDP not connected)")
        self._qt_click(x, y)

    def _qt_click(self, x: int, y: int):
        """Send click using native Qt mouse events (fallback when CDP unavailable)."""
        # Get the actual rendering widget - focusProxy() is where events should go
        target = self.browser.focusProxy()
        if not target:
            target = self.browser

        # x,y are coordinates relative to self.browser (where screenshot is taken)
        # We need to map them to target's coordinate system
        # First convert to global coordinates using browser's coordinate system
        global_pos = self.browser.mapToGlobal(QPointF(x, y).toPoint())
        # Then convert to target's local coordinates
        local_pos = target.mapFromGlobal(global_pos)
        local_pos_f = QPointF(local_pos)
        global_pos_f = QPointF(global_pos)

        print(f"  -> Local pos in target: ({local_pos.x()}, {local_pos.y()})")

        # Send mouse press event
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            local_pos_f,
            global_pos_f,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        QApplication.sendEvent(target, press_event)

        # Small delay then release (use timer to not block)
        def send_release():
            release_event = QMouseEvent(
                QEvent.Type.MouseButtonRelease,
                local_pos_f,
                global_pos_f,
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier
            )
            QApplication.sendEvent(target, release_event)

        QTimer.singleShot(50, send_release)

    def handle_type(self, text: str, press_enter: bool):
        """Handle typing text - use CDP for trusted events, fallback to JS."""
        print(f"Typing: {text}, Enter: {press_enter}")

        # Try CDP first (creates truly trusted input)
        if self.cdp_client.is_connected:
            self.cdp_client.type_text(text)
            if press_enter:
                QTimer.singleShot(100, lambda: self.cdp_client.press_key('Enter'))
            return

        # Fallback to JavaScript injection
        print("Using JavaScript injection for typing (CDP not connected)")
        self._js_type(text, press_enter)

    def _js_type(self, text: str, press_enter: bool):
        """Type using JavaScript injection (fallback when CDP unavailable)."""
        # Escape the text for JavaScript
        escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

        # Use JavaScript to type into focused element
        js_code = f"""
        (function() {{
            var activeElement = document.activeElement;
            if (activeElement && (activeElement.tagName === 'INPUT' ||
                                  activeElement.tagName === 'TEXTAREA' ||
                                  activeElement.isContentEditable)) {{
                activeElement.value += "{escaped_text}";

                // Trigger input event
                var event = new Event('input', {{ bubbles: true }});
                activeElement.dispatchEvent(event);

                {'activeElement.form && activeElement.form.submit();' if press_enter else ''}
            }}
        }})();
        """

        try:
            self.browser.page().runJavaScript(js_code)
        except Exception as e:
            print(f"Error typing: {e}")

    def pause_capture(self):
        """Pause screenshot capture."""
        if not self.is_paused:
            print("Browser capture PAUSED (no viewers)")
            self.screenshot_timer.stop()
            self.is_paused = True

    def resume_capture(self):
        """Resume screenshot capture."""
        if self.is_paused:
            print("Browser capture RESUMED (viewer connected)")
            self.screenshot_timer.start(100)  # 10 FPS
            self.is_paused = False

    def capture_screenshot(self):
        """Capture screenshot and send to backend."""
        # Skip if paused
        if self.is_paused:
            return

        # Grab the browser widget as an image
        pixmap = self.browser.grab()
        image = pixmap.toImage()

        # Convert to base64 using QBuffer - lower quality for faster streaming
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "JPEG", quality=50)  # Lower quality = smaller payload = faster
        buffer.close()
        screenshot_b64 = base64.b64encode(byte_array.data()).decode()

        # Send to backend
        self.communicator.send_screenshot(screenshot_b64)


def main():
    """Start the Qt browser."""
    try:
        print("Starting Qt WebEngine Browser...")
        app = QApplication(sys.argv)

        # Set application name
        app.setApplicationName("Proto Browser")
        app.setOrganizationName("Proto")

        # Create and show browser
        print("Creating browser window...")
        browser = QtBrowser()
        browser.show()

        print("✓ Qt Browser window shown, entering event loop")
        sys.exit(app.exec())
    except Exception as e:
        print(f"ERROR starting Qt browser: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

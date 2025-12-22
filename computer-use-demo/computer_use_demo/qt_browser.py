"""
Qt WebEngine Browser - Real Chromium browser for the application.
This provides a true browser experience with zero bot detection.
"""

import sys
import base64
import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from PyQt6.QtCore import QUrl, QTimer, pyqtSignal, QObject, QBuffer, QByteArray, QIODevice
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtGui import QImage


class BrowserCommunicator(QObject):
    """Handles communication with FastAPI backend."""

    navigate_signal = pyqtSignal(str)
    click_signal = pyqtSignal(int, int)
    type_signal = pyqtSignal(str, bool)

    def __init__(self, backend_url="http://127.0.0.1:8000"):
        super().__init__()
        self.backend_url = backend_url

    def send_screenshot(self, screenshot_b64):
        """Send screenshot to backend."""
        try:
            data = json.dumps({"screenshot": screenshot_b64}).encode('utf-8')
            req = Request(
                f"{self.backend_url}/api/qt-browser/screenshot",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            urlopen(req, timeout=30)
        except URLError as e:
            print(f"Error sending screenshot: {e}")

    def check_commands(self):
        """Check for commands (navigate/click/type) from backend."""
        try:
            req = Request(f"{self.backend_url}/api/qt-browser/command")
            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
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

        except URLError:
            pass  # Silent fail if backend not ready


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

        # Screenshot timer - capture at 30 FPS
        self.screenshot_timer = QTimer()
        self.screenshot_timer.timeout.connect(self.capture_screenshot)
        self.screenshot_timer.start(33)  # 30 FPS

        # Command check timer - check for navigation commands
        self.command_timer = QTimer()
        self.command_timer.timeout.connect(self.communicator.check_commands)
        self.command_timer.start(100)  # Check every 100ms

        # Start with blank page
        self.browser.setUrl(QUrl("about:blank"))

    def navigate(self, url: str):
        """Navigate to a URL."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        print(f"Navigating to: {url}")
        self.browser.setUrl(QUrl(url))

    def handle_click(self, x: int, y: int):
        """Handle click at coordinates using JavaScript injection."""
        print(f"Clicking at ({x}, {y})")

        # Use JavaScript to simulate click at coordinates
        js_code = f"""
        (function() {{
            var element = document.elementFromPoint({x}, {y});
            if (element) {{
                element.click();
                element.focus();
            }}
        }})();
        """

        try:
            self.browser.page().runJavaScript(js_code)
        except Exception as e:
            print(f"Error clicking: {e}")

    def handle_type(self, text: str, press_enter: bool):
        """Handle typing text using JavaScript injection."""
        print(f"Typing: {text}, Enter: {press_enter}")

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

    def capture_screenshot(self):
        """Capture screenshot and send to backend."""
        # Grab the browser widget as an image
        pixmap = self.browser.grab()
        image = pixmap.toImage()

        # Convert to base64 using QBuffer
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "JPEG", quality=80)
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

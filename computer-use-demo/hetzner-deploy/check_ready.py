#!/usr/bin/env python3
"""
Check if instance services are ready
"""
import socket
import time
import sys

def check_port(host, port, timeout=2):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def main():
    ip = "91.98.113.134"
    max_attempts = 30  # 30 attempts x 30 seconds = 15 minutes

    print(f"Monitoring {ip} for service readiness...")
    print("This typically takes 10-15 minutes for fresh instances.")
    print("")

    for attempt in range(1, max_attempts + 1):
        elapsed = attempt * 30
        minutes = elapsed // 60
        seconds = elapsed % 60

        port_8080 = check_port(ip, 8080, timeout=2)
        port_8501 = check_port(ip, 8501, timeout=2)

        status_8080 = "✅" if port_8080 else "❌"
        status_8501 = "✅" if port_8501 else "❌"

        print(f"[{minutes:02d}:{seconds:02d}] Port 8080: {status_8080}  |  Port 8501: {status_8501}")

        if port_8080 and port_8501:
            print("")
            print("=" * 50)
            print("🎉 Services are ready!")
            print("=" * 50)
            print(f"Chat Interface: http://{ip}:8501")
            print(f"Desktop (noVNC): http://{ip}:8080")
            print("=" * 50)
            return 0

        if attempt < max_attempts:
            time.sleep(30)

    print("")
    print("⚠️ Services did not start within 15 minutes.")
    print("This may indicate a build error. Check cloud-init logs on the instance.")
    return 1

if __name__ == '__main__':
    sys.exit(main())

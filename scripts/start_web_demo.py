"""Interactive Web Simulator server for NEXUS video presentations."""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

PORT = 8088
WEB_DIR = Path(__file__).resolve().parent.parent / "src" / "nexus" / "ui" / "web"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)


def start_server():
    os.chdir(WEB_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n========================================================")
        print(f"⚡ NEXUS Interactive On-Device Web Simulator is LIVE! ⚡")
        print(f"URL: {url}")
        print(f"Open this URL in your browser to record your video presentation!")
        print(f"Press Ctrl+C to stop.")
        print(f"========================================================\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down NEXUS simulator.")


if __name__ == "__main__":
    start_server()

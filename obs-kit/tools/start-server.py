#!/usr/bin/env python3
"""Local kit server for the streaming PC."""
from __future__ import annotations

import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = ROOT / "overlays" / "shared" / "now.json"
PORT = 8765
LOAD = f"http://127.0.0.1:{PORT}/overlays/install.html?load=1"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path.split("?", 1)[0] not in ("/now", "/overlays/shared/now.json"):
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        NOW.write_bytes(body)
        payload = b'{"ok":true}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


if __name__ == "__main__":
    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print("Port 8765 already in use - opening the scene loader anyway.")
        webbrowser.open(LOAD)
        raise SystemExit(0)
    print("Kit server", LOAD)
    print("Keep this window open.")
    webbrowser.open(LOAD)
    httpd.serve_forever()

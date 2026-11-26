#!/usr/bin/env python3
"""Serve ONE local file to the TIP page for a few minutes, so a file larger than the
browser tool's upload limit can be attached from the page itself. Standard library only.

Usage:  serve_file.py <file> [--port 8765] [--minutes 3]

- Listens on 127.0.0.1 only (not reachable from other computers).
- Serves only that file, at http://127.0.0.1:<port>/file, and only to the TIP origin (CORS).
- Stops by itself after --minutes. Run it in the background and do not leave it running.

In the TIP page (Claude in Chrome, javascript tool), then run:

  const b = await fetch('http://127.0.0.1:8765/file').then(r => r.blob());
  const f = new File([b], '<original file name>', {type: b.type || 'application/pdf'});
  const dt = new DataTransfer(); dt.items.add(f);
  document.getElementById('fileupload').files = dt.files;

and click Save Draft. Check afterwards that the stored file has the same size as the original.
"""
import argparse
import mimetypes
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

ORIGIN = "https://tip.alliance.cgiar.org"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--minutes", type=float, default=3)
    a = ap.parse_args()
    path = os.path.abspath(a.file)
    if not os.path.isfile(path):
        sys.exit("File not found: %s" % path)
    ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"

    class Handler(BaseHTTPRequestHandler):
        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", ORIGIN)
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self):
            if self.path != "/file":
                self.send_response(404)
                self.end_headers()
                return
            with open(path, "rb") as fh:
                data = fh.read()
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            print("Served %d bytes" % len(data), flush=True)

        def log_message(self, *args):
            pass

    srv = HTTPServer(("127.0.0.1", a.port), Handler)
    threading.Timer(a.minutes * 60, srv.shutdown).start()
    print("Serving %s (%d bytes) at http://127.0.0.1:%d/file for %g minutes"
          % (os.path.basename(path), os.path.getsize(path), a.port, a.minutes), flush=True)
    srv.serve_forever()
    print("Stopped.", flush=True)


if __name__ == "__main__":
    main()

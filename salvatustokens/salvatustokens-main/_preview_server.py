import http.server
from functools import partial
import socketserver
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PORT = 5051


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    subprocess.run(["python", "build.py"], cwd=ROOT, check=True)
    handler = partial(QuietHandler, directory=str(ROOT / "dist"))
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        print(f"Serving http://127.0.0.1:{PORT}/ from {ROOT / 'dist'}")
        httpd.serve_forever()

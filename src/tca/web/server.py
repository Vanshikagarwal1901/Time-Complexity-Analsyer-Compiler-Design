from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from ..analyzer import analyze_program
from ..parsers import CParser
from ..semantic import analyze_semantics


HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Time Complexity Analyzer</title>
  <style>
    body { font-family: Georgia, "Times New Roman", serif; margin: 2rem; background: #f5f0e8; color: #1b1b1b; }
    textarea { width: 100%; height: 280px; font-family: "Courier New", monospace; }
    .row { display: flex; gap: 1rem; align-items: center; margin: 1rem 0; }
    .box { padding: 1rem; background: #fff7eb; border: 1px solid #d7c6b6; }
    button { background: #3a4e3a; color: #fff; border: none; padding: 0.6rem 1rem; cursor: pointer; }
  </style>
</head>
<body>
  <h1>Time Complexity Analyzer</h1>
  <div class="box">
    <div class="row">
      <label>Language:</label>
      <span>Mini-C (C/C++)</span>
      <button onclick="analyze()">Analyze</button>
    </div>
    <textarea id="code" placeholder="Paste code here..."></textarea>
    <div class="row">
      <strong>Result:</strong> <span id="result">-</span>
    </div>
  </div>
<script>
async function analyze() {
  const code = document.getElementById('code').value;
  const form = new URLSearchParams();
  form.set('code', code);
  const res = await fetch('/analyze', { method: 'POST', body: form });
  const data = await res.json();
  document.getElementById('result').textContent = data.error || data.complexity || 'O(?)';
}
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def do_POST(self) -> None:
        if self.path != "/analyze":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        data = parse_qs(body)
        code = (data.get("code") or [""])[0]
        program = CParser().parse(code)
        errors = analyze_semantics(program)
        if errors:
          payload = json.dumps({"error": errors[0]}).encode("utf-8")
        else:
          complexity = str(analyze_program(program))
          payload = json.dumps({"complexity": complexity}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def run_server() -> None:
    server = HTTPServer(("localhost", 8000), Handler)
    print("Serving on http://localhost:8000")
    server.serve_forever()

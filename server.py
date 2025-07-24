from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        secret = os.environ.get("MY-SECRET", "Secret not found")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"Simple Python Demo Project: {secret}".encode())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("", port), Handler).serve_forever()

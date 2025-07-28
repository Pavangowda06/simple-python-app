from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import requests

# Hardcoded users: username -> password
USER_CREDENTIALS = {
    "Pavan": "pavan@123",
    "alice": "secret"
}

def get_location(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}")
        data = resp.json()
        if data.get("status") == "success":
            city = data.get("city", "Unknown")
            region = data.get("regionName", "Unknown")
            country = data.get("country", "Unknown")
            return f"{city}, {region}, {country}"
        else:
            return "Location not found"
    except Exception:
        return "Error fetching location"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/login":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = """
            <html>
            <head><title>Login</title></head>
            <body>
                <h2>Login Page</h2>
                <form method="POST" action="/login">
                    Username: <input type="text" name="username"><br><br>
                    Password: <input type="password" name="password"><br><br>
                    <input type="submit" value="Login">
                </form>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            data = urllib.parse.parse_qs(post_data)

            username = data.get("username", [""])[0].strip()
            password = data.get("password", [""])[0].strip()

            # Check credentials
            if USER_CREDENTIALS.get(username) == password:
                ip = self.client_address[0]
                location = get_location(ip)

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                response_html = f"""
                <html>
                <head><title>Welcome</title></head>
                <body>
                    <h2>Welcome, {username}!</h2>
                    <p>You logged in from IP: {ip}</p>
                    <p>Location: {location}</p>
                </body>
                </html>
                """
                self.wfile.write(response_html.encode())
            else:
                self.send_response(401)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Login failed: Invalid username or password.")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}...")
    HTTPServer(("", port), Handler).serve_forever()

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import requests
import socket

# Hardcoded users: username -> password
USER_CREDENTIALS = {
    "Pavan": "pavan@123",
    "alice": "secret"
}

def is_private_ip(ip):
    # Check for common private/local IP ranges
    private_prefixes = (
        "10.",
        "172.",
        "192.168.",
        "127.",     # localhost IPv4
        "::1"       # localhost IPv6
    )
    return ip.startswith(private_prefixes)

def get_public_ip():
    try:
        ip = requests.get('https://api.ipify.org').text.strip()
        return ip
    except Exception as e:
        return None

def get_location(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}")
        resp.raise_for_status()
        data = resp.json()
        print(f"Geo API response for IP {ip}: {data}")  # Debug print
        if data.get("status") == "success":
            city = data.get("city", "Unknown")
            region = data.get("regionName", "Unknown")
            country = data.get("country", "Unknown")
            return f"{city}, {region}, {country}"
        else:
            return "Location not found"
    except Exception as e:
        return f"Error fetching location: {e}"

class Handler(BaseHTTPRequestHandler):

    def get_client_ip(self):
        x_forwarded_for = self.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            # May contain multiple IPs; take the first one
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.client_address[0]
        return ip

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
                ip = self.get_client_ip()
                print(f"Detected client IP: {ip}")  # Debug print

                # If IP is private or localhost, fallback to server's public IP (for local testing)
                if is_private_ip(ip):
                    public_ip = get_public_ip()
                    if public_ip:
                        print(f"Using server public IP instead: {public_ip}")
                        ip = public_ip
                    else:
                        print("Could not get server public IP, using detected IP.")

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

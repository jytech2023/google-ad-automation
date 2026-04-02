"""Generate a Google Ads API refresh token via Desktop OAuth flow.

Usage:
  python3.13 scripts/get-refresh-token.py

This opens a browser for Google sign-in, then prints the refresh token.
Paste it into .env.local as GOOGLE_ADS_REFRESH_TOKEN.
"""
import http.server
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
import webbrowser
import threading

# Load .env.local
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET', '')
SCOPE = 'https://www.googleapis.com/auth/adwords'
REDIRECT_URI = 'http://localhost:8089'

if not CLIENT_ID or not CLIENT_SECRET:
    print('Error: Set GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET in .env.local first')
    sys.exit(1)

auth_code = None
server_done = threading.Event()


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code = query.get('code', [None])[0]
        error = query.get('error', [None])[0]

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

        if auth_code:
            self.wfile.write(b'<html><body><h2>Authorization successful!</h2><p>You can close this tab and go back to the terminal.</p></body></html>')
        else:
            self.wfile.write(f'<html><body><h2>Authorization failed</h2><p>Error: {error}</p></body></html>'.encode())

        server_done.set()

    def log_message(self, format, *args):
        pass  # Suppress logs


def main():
    # Build auth URL
    params = urllib.parse.urlencode({
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPE,
        'access_type': 'offline',
        'prompt': 'consent',
    })
    auth_url = f'https://accounts.google.com/o/oauth2/v2/auth?{params}'

    # Start local callback server
    server = http.server.HTTPServer(('localhost', 8089), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    print('Opening browser for Google sign-in...')
    print(f'If the browser doesn\'t open, go to:\n{auth_url}\n')
    webbrowser.open(auth_url)

    # Wait for callback
    server_done.wait(timeout=120)
    server.server_close()

    if not auth_code:
        print('Error: No authorization code received')
        sys.exit(1)

    print('Authorization code received. Exchanging for tokens...\n')

    # Exchange code for tokens
    data = urllib.parse.urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
    }).encode()

    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            refresh_token = result.get('refresh_token', '')
            if refresh_token:
                print('=== SUCCESS ===')
                print(f'\nRefresh Token:\n{refresh_token}')
                print(f'\nPaste this into .env.local as:')
                print(f'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}')
            else:
                print('Error: No refresh token in response')
                print(json.dumps(result, indent=2))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        print(f'Error ({e.code}): {json.dumps(body, indent=2)}')
        sys.exit(1)


if __name__ == '__main__':
    main()

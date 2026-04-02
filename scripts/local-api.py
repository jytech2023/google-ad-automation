"""Local API server for development — runs alongside `ng serve`.

Usage:
  python3 scripts/local-api.py

Starts on port 3001. Angular dev server proxies /api/* to this.
"""
import http.server
import importlib.util
import os
import sys

PORT = 3001

# Load .env.local
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

# Import API handlers
api_dir = os.path.join(os.path.dirname(__file__), '..', 'api')

def load_handler(module_name):
    spec = importlib.util.spec_from_file_location(module_name, os.path.join(api_dir, f'{module_name}.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.handler

AdsDataHandler = load_handler('ads-data')
CampaignActionHandler = load_handler('campaign-action')
CampaignCreateHandler = load_handler('campaign-create')
BillingStatusHandler = load_handler('billing-status')
ContactHandler = load_handler('contact')
HealthHandler = load_handler('health')


class LocalHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/ads-data'):
            self.__class__ = AdsDataHandler
            self.do_GET()
        elif self.path.startswith('/api/billing-status'):
            self.__class__ = BillingStatusHandler
            self.do_GET()
        elif self.path.startswith('/api/health'):
            self.__class__ = HealthHandler
            self.do_GET()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not found"}')

    def do_POST(self):
        if self.path.startswith('/api/campaign-create'):
            self.__class__ = CampaignCreateHandler
            self.do_POST()
        elif self.path.startswith('/api/campaign-action'):
            self.__class__ = CampaignActionHandler
            self.do_POST()
        elif self.path.startswith('/api/contact'):
            self.__class__ = ContactHandler
            self.do_POST()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not found"}')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


if __name__ == '__main__':
    server = http.server.HTTPServer(('localhost', PORT), LocalHandler)
    print(f'Local API server running at http://localhost:{PORT}')
    print(f'Endpoints: /api/ads-data, /api/campaign-action, /api/contact, /api/health')
    print('Press Ctrl+C to stop\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')

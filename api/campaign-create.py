"""Create campaign API endpoint — creates a new campaign via Google Ads API."""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler


def get_oauth_token() -> str | None:
    data = urllib.parse.urlencode({
        "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID", ""),
        "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET", ""),
        "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", ""),
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("access_token")
    except Exception as e:
        print(f"[CampaignCreate] OAuth error: {e}")
        return None


def ads_mutate(access_token: str, customer_id: str, endpoint: str, body: dict, login_customer_id: str) -> tuple[dict, int]:
    url = f"https://googleads.googleapis.com/v20/customers/{customer_id}/{endpoint}"
    payload = json.dumps(body).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("developer-token", os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""))
    req.add_header("Content-Type", "application/json")
    if login_customer_id:
        req.add_header("login-customer-id", login_customer_id)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()), 200
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            return json.loads(body_text), e.code
        except json.JSONDecodeError:
            return {"error": body_text}, e.code


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        name = data.get("name", "").strip()
        daily_budget = data.get("dailyBudget", 0)  # in dollars
        status = data.get("status", "PAUSED").upper()  # PAUSED or ENABLED
        channel = data.get("channel", "SEARCH").upper()

        if not name or daily_budget <= 0:
            self._respond(400, {"error": "name and dailyBudget (> 0) are required"})
            return

        if status not in ("PAUSED", "ENABLED"):
            status = "PAUSED"

        customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "")
        login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")

        if not customer_id:
            self._respond(400, {"error": "GOOGLE_ADS_CUSTOMER_ID not configured"})
            return

        access_token = get_oauth_token()
        if not access_token:
            self._respond(401, {"error": "Failed to get OAuth token"})
            return

        # Step 1: Create budget
        budget_micros = str(int(daily_budget * 1_000_000))
        budget_body = {
            "operations": [{
                "create": {
                    "name": f"{name} Budget",
                    "amountMicros": budget_micros,
                    "deliveryMethod": "STANDARD",
                    "explicitlyShared": False,
                }
            }]
        }
        result, code = ads_mutate(access_token, customer_id, "campaignBudgets:mutate", budget_body, login_customer_id)
        if code != 200:
            self._respond(code, {"error": "Failed to create budget", "details": result})
            return

        budget_resource = result.get("results", [{}])[0].get("resourceName", "")

        # Step 2: Create campaign
        campaign_body = {
            "operations": [{
                "create": {
                    "name": name,
                    "status": status,
                    "advertisingChannelType": channel,
                    "campaignBudget": budget_resource,
                    "manualCpc": {},
                }
            }]
        }
        result, code = ads_mutate(access_token, customer_id, "campaigns:mutate", campaign_body, login_customer_id)
        if code == 200:
            campaign_resource = result.get("results", [{}])[0].get("resourceName", "")
            self._respond(200, {
                "success": True,
                "campaignName": name,
                "resourceName": campaign_resource,
                "status": status,
                "dailyBudget": daily_budget,
            })
        else:
            self._respond(code, {"error": "Failed to create campaign", "details": result})

    def _respond(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

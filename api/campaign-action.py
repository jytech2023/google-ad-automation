"""Campaign action API endpoint — pause/enable campaigns via Google Ads API."""
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
        print(f"[CampaignAction] OAuth error: {e}")
        return None


def find_campaign_resource(access_token: str, customer_id: str, campaign_name: str, login_customer_id: str) -> str | None:
    """Find campaign resource name by campaign name."""
    url = f"https://googleads.googleapis.com/v20/customers/{customer_id}/googleAds:searchStream"
    query = f"SELECT campaign.resource_name, campaign.name FROM campaign WHERE campaign.name = '{campaign_name}' LIMIT 1"
    payload = json.dumps({"query": query}).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("developer-token", os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""))
    req.add_header("Content-Type", "application/json")
    if login_customer_id:
        req.add_header("login-customer-id", login_customer_id)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            for batch in result:
                for row in batch.get("results", []):
                    return row.get("campaign", {}).get("resourceName")
    except Exception as e:
        print(f"[CampaignAction] Find campaign error: {e}")
    return None


def update_campaign_status(access_token: str, customer_id: str, resource_name: str, new_status: str, login_customer_id: str) -> dict:
    """Update campaign status (ENABLED or PAUSED)."""
    url = f"https://googleads.googleapis.com/v20/customers/{customer_id}/campaigns:mutate"
    body = {
        "operations": [{
            "update": {
                "resourceName": resource_name,
                "status": new_status,
            },
            "updateMask": "status",
        }]
    }
    payload = json.dumps(body).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("developer-token", os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""))
    req.add_header("Content-Type", "application/json")
    if login_customer_id:
        req.add_header("login-customer-id", login_customer_id)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"success": True, "result": json.loads(resp.read())}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"[CampaignAction] Update error {e.code}: {error_body}")
        try:
            return {"success": False, "error": json.loads(error_body)}
        except json.JSONDecodeError:
            return {"success": False, "error": error_body}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        campaign_name = data.get("campaignName", "").strip()
        action = data.get("action", "").strip()  # "pause" or "enable"

        if not campaign_name or action not in ("pause", "enable"):
            self._respond(400, {"error": "campaignName and action (pause|enable) are required"})
            return

        customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "")
        login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")

        if not customer_id:
            self._respond(400, {"error": "GOOGLE_ADS_CUSTOMER_ID not configured"})
            return

        access_token = get_oauth_token()
        if not access_token:
            self._respond(401, {"error": "Failed to get OAuth token"})
            return

        # Block enabling campaigns if no billing is set up
        if action == "enable":
            has_billing = self._check_billing(access_token, customer_id, login_customer_id)
            if not has_billing:
                self._respond(403, {
                    "error": "Cannot enable campaign: no billing setup found. Add a payment method in Google Ads first.",
                })
                return

        # Continue with campaign action

        resource_name = find_campaign_resource(access_token, customer_id, campaign_name, login_customer_id)
        if not resource_name:
            self._respond(404, {"error": f"Campaign '{campaign_name}' not found"})
            return

        new_status = "PAUSED" if action == "pause" else "ENABLED"
        result = update_campaign_status(access_token, customer_id, resource_name, new_status, login_customer_id)

        if result["success"]:
            self._respond(200, {"success": True, "campaignName": campaign_name, "newStatus": action})
        else:
            self._respond(500, {"error": "Failed to update campaign", "details": result.get("error")})

    def _check_billing(self, access_token: str, customer_id: str, login_customer_id: str) -> bool:
        """Check if the account has an approved billing setup."""
        url = f"https://googleads.googleapis.com/v20/customers/{customer_id}/googleAds:searchStream"
        query = "SELECT billing_setup.id, billing_setup.status FROM billing_setup WHERE billing_setup.status = 'APPROVED' LIMIT 1"
        payload = json.dumps({"query": query}).encode()

        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("developer-token", os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""))
        req.add_header("Content-Type", "application/json")
        if login_customer_id:
            req.add_header("login-customer-id", login_customer_id)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                for batch in result:
                    if batch.get("results"):
                        return True
            return False
        except Exception as e:
            print(f"[CampaignAction] Billing check error: {e}")
            return False

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

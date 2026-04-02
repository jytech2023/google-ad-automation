"""Check Google Ads billing/payment status via API."""
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
    except Exception:
        return None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "")
        login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
        developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")

        if not customer_id or not developer_token:
            self._respond(400, {"error": "Google Ads credentials not configured"})
            return

        access_token = get_oauth_token()
        if not access_token:
            self._respond(401, {"error": "OAuth failed"})
            return

        # Query billing setup status
        url = f"https://googleads.googleapis.com/v20/customers/{customer_id}/googleAds:searchStream"
        query = """
            SELECT
                billing_setup.id,
                billing_setup.status,
                billing_setup.payments_account,
                billing_setup.payments_account_info.payments_account_name,
                billing_setup.payments_account_info.payments_profile_name
            FROM billing_setup
            WHERE billing_setup.status = 'APPROVED'
            LIMIT 10
        """
        payload = json.dumps({"query": query}).encode()

        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("developer-token", developer_token)
        req.add_header("Content-Type", "application/json")
        if login_customer_id:
            req.add_header("login-customer-id", login_customer_id)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())

            setups = []
            for batch in result:
                for row in batch.get("results", []):
                    bs = row.get("billingSetup", {})
                    info = bs.get("paymentsAccountInfo", {})
                    setups.append({
                        "id": bs.get("id", ""),
                        "status": bs.get("status", ""),
                        "paymentsAccount": bs.get("paymentsAccount", ""),
                        "accountName": info.get("paymentsAccountName", ""),
                        "profileName": info.get("paymentsProfileName", ""),
                    })

            has_billing = len(setups) > 0

            self._respond(200, {
                "hasBilling": has_billing,
                "billingSetups": setups,
                "message": "Billing is active" if has_billing else "No billing setup found. Add a payment method in Google Ads to enable campaigns.",
            })

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"[BillingStatus] API error {e.code}: {error_body}")
            # If we can't query billing, assume not set up
            self._respond(200, {
                "hasBilling": False,
                "billingSetups": [],
                "message": "Unable to check billing status. Add a payment method in Google Ads to enable campaigns.",
            })

    def _respond(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

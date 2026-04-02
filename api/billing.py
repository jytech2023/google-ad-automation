"""Billing API — fetches cost/charge data from Google Ads API."""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta


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
        print(f"[Billing] OAuth error: {e}")
        return None


def query_ads(access_token: str, customer_id: str, query: str, login_customer_id: str = "") -> list | None:
    url = f"https://googleads.googleapis.com/v20/customers/{customer_id}/googleAds:searchStream"
    payload = json.dumps({"query": query}).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("developer-token", os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""))
    req.add_header("Content-Type", "application/json")
    if login_customer_id:
        req.add_header("login-customer-id", login_customer_id)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"[Billing] API error {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"[Billing] API error: {e}")
        return None


DEMO_DATA = {
    "source": "demo",
    "summary": {
        "totalCost": 6240.00,
        "totalImpressions": 48320,
        "totalClicks": 3847,
        "totalConversions": 284,
        "avgCpc": 1.62,
        "avgCostPerConversion": 21.97,
    },
    "byCampaign": [
        {"name": "Brand Awareness — US", "status": "active", "cost": 2180.00, "clicks": 1540, "conversions": 112, "cpc": 1.42, "costPerConv": 19.46},
        {"name": "Lead Gen — Europe", "status": "active", "cost": 1860.00, "clicks": 980, "conversions": 78, "cpc": 1.90, "costPerConv": 23.85},
        {"name": "Retargeting — Global", "status": "active", "cost": 1240.00, "clicks": 720, "conversions": 64, "cpc": 1.72, "costPerConv": 19.38},
        {"name": "Product Launch — APAC", "status": "paused", "cost": 680.00, "clicks": 410, "conversions": 22, "cpc": 1.66, "costPerConv": 30.91},
        {"name": "Holiday Sale Q4", "status": "ended", "cost": 280.00, "clicks": 197, "conversions": 8, "cpc": 1.42, "costPerConv": 35.00},
    ],
    "dailyCost": [
        {"date": "Mon", "cost": 890.00},
        {"date": "Tue", "cost": 920.00},
        {"date": "Wed", "cost": 980.00},
        {"date": "Thu", "cost": 840.00},
        {"date": "Fri", "cost": 1050.00},
        {"date": "Sat", "cost": 780.00},
        {"date": "Sun", "cost": 780.00},
    ],
}


def fetch_billing_data(days: int) -> dict | str:
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "")
    login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")

    if not customer_id:
        return "GOOGLE_ADS_CUSTOMER_ID not configured"

    access_token = get_oauth_token()
    if not access_token:
        return "OAuth failed"

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Campaign cost breakdown
    campaign_query = f"""
        SELECT
            campaign.name,
            campaign.status,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    campaign_result = query_ads(access_token, customer_id, campaign_query, login_customer_id)
    if not campaign_result:
        return "Failed to fetch campaign cost data"

    status_map = {"ENABLED": "active", "PAUSED": "paused", "REMOVED": "ended"}
    by_campaign = []
    total_cost = 0
    total_clicks = 0
    total_impressions = 0
    total_conversions = 0

    for batch in campaign_result:
        for row in batch.get("results", []):
            camp = row.get("campaign", {})
            m = row.get("metrics", {})
            cost_micros = int(m.get("costMicros", 0))
            clicks = int(m.get("clicks", 0))
            impressions = int(m.get("impressions", 0))
            conversions = float(m.get("conversions", 0))
            cost = cost_micros / 1_000_000

            total_cost += cost
            total_clicks += clicks
            total_impressions += impressions
            total_conversions += conversions

            by_campaign.append({
                "name": camp.get("name", "Unknown"),
                "status": status_map.get(camp.get("status", ""), "ended"),
                "cost": round(cost, 2),
                "clicks": clicks,
                "conversions": round(conversions),
                "cpc": round(cost / clicks, 2) if clicks > 0 else 0,
                "costPerConv": round(cost / conversions, 2) if conversions > 0 else 0,
            })

    # Daily cost
    daily_query = f"""
        SELECT
            segments.date,
            metrics.cost_micros
        FROM customer
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """

    daily_result = query_ads(access_token, customer_id, daily_query, login_customer_id)
    daily_cost = []
    if daily_result:
        for batch in daily_result:
            for row in batch.get("results", []):
                d = row.get("segments", {}).get("date", "")
                c = int(row.get("metrics", {}).get("costMicros", 0))
                daily_cost.append({"date": d, "cost": round(c / 1_000_000, 2)})

    return {
        "source": "google_ads_api",
        "summary": {
            "totalCost": round(total_cost, 2),
            "totalImpressions": total_impressions,
            "totalClicks": total_clicks,
            "totalConversions": round(total_conversions),
            "avgCpc": round(total_cost / total_clicks, 2) if total_clicks > 0 else 0,
            "avgCostPerConversion": round(total_cost / total_conversions, 2) if total_conversions > 0 else 0,
        },
        "byCampaign": by_campaign,
        "dailyCost": daily_cost,
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        query = parse_qs(urlparse(self.path).query)
        days = int(query.get("days", [7])[0])
        days = min(max(days, 1), 90)

        result = fetch_billing_data(days)
        if isinstance(result, str):
            # Fallback to demo
            data = DEMO_DATA
        else:
            data = result

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

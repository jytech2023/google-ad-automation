"""Google Ads data API endpoint for Vercel serverless function.

Fetches real campaign performance data from the Google Ads API.
Falls back to demo data if OAuth credentials are not configured.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta

# Demo data used when Google Ads API credentials are not configured
DEMO_KPIS = {
    "impressions": 48320, "clicks": 3847, "ctr": 7.96,
    "conversions": 284, "cost": 6240000000, "roas": 4.2,
}

DEMO_CAMPAIGNS = [
    {"name": "Brand Awareness — US", "status": "ENABLED", "channel": "SEARCH", "mutable": True, "impressions": 18420, "clicks": 1540, "ctr": 8.36, "cost": 2180000000, "conversions": 112, "roas": 5.1},
    {"name": "Lead Gen — Europe", "status": "ENABLED", "channel": "SEARCH", "mutable": True, "impressions": 12350, "clicks": 980, "ctr": 7.93, "cost": 1860000000, "conversions": 78, "roas": 4.2},
    {"name": "Retargeting — Global", "status": "ENABLED", "channel": "DISPLAY", "mutable": True, "impressions": 9800, "clicks": 720, "ctr": 7.35, "cost": 1240000000, "conversions": 64, "roas": 5.8},
    {"name": "Product Launch — APAC", "status": "PAUSED", "channel": "SHOPPING", "mutable": True, "impressions": 5200, "clicks": 410, "ctr": 7.88, "cost": 680000000, "conversions": 22, "roas": 2.9},
    {"name": "Holiday Sale Q4", "status": "REMOVED", "channel": "VIDEO", "mutable": False, "impressions": 2550, "clicks": 197, "ctr": 7.73, "cost": 280000000, "conversions": 8, "roas": 1.8},
]

DEMO_DAILY = [
    {"date": "Mon", "impressions": 6800, "clicks": 540, "conversions": 42, "cost": 890000000},
    {"date": "Tue", "impressions": 7200, "clicks": 580, "conversions": 38, "cost": 920000000},
    {"date": "Wed", "impressions": 7800, "clicks": 620, "conversions": 48, "cost": 980000000},
    {"date": "Thu", "impressions": 6500, "clicks": 510, "conversions": 36, "cost": 840000000},
    {"date": "Fri", "impressions": 8100, "clicks": 650, "conversions": 52, "cost": 1050000000},
    {"date": "Sat", "impressions": 5900, "clicks": 470, "conversions": 34, "cost": 780000000},
    {"date": "Sun", "impressions": 6020, "clicks": 477, "conversions": 34, "cost": 780000000},
]


def get_oauth_token(client_id: str, client_secret: str, refresh_token: str) -> str | None:
    """Exchange refresh token for access token."""
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
            return body.get("access_token")
    except Exception as e:
        print(f"[GoogleAds] OAuth token error: {e}")
        return None


def query_google_ads(access_token: str, developer_token: str, customer_id: str, query: str, login_customer_id: str = "") -> dict | None:
    """Execute a GAQL query against the Google Ads API."""
    url = f"https://googleads.googleapis.com/v20/customers/{customer_id}/googleAds:searchStream"
    payload = json.dumps({"query": query}).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("developer-token", developer_token)
    req.add_header("Content-Type", "application/json")
    if login_customer_id:
        req.add_header("login-customer-id", login_customer_id)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"[GoogleAds] API error {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"[GoogleAds] API request error: {e}")
        return None


def fetch_real_data(days: int) -> dict | str:
    """Fetch real data from Google Ads API. Returns error string on failure."""
    developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "")
    login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "")
    refresh_token = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", "")

    missing = []
    if not developer_token: missing.append("GOOGLE_ADS_DEVELOPER_TOKEN")
    if not customer_id: missing.append("GOOGLE_ADS_CUSTOMER_ID")
    if not client_id: missing.append("GOOGLE_ADS_CLIENT_ID")
    if not client_secret: missing.append("GOOGLE_ADS_CLIENT_SECRET")
    if not refresh_token: missing.append("GOOGLE_ADS_REFRESH_TOKEN")
    if missing:
        return f"Missing env vars: {', '.join(missing)}"

    access_token = get_oauth_token(client_id, client_secret, refresh_token)
    if not access_token:
        return "OAuth failed: could not get access token. Check CLIENT_ID, CLIENT_SECRET, and REFRESH_TOKEN."

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Fetch ALL campaigns (not filtered by date range — shows all statuses)
    campaign_query = """
        SELECT
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type
        FROM campaign
        ORDER BY campaign.status ASC, campaign.name ASC
    """

    campaign_result = query_google_ads(access_token, developer_token, customer_id, campaign_query, login_customer_id)
    if not campaign_result:
        return f"Failed to fetch campaigns for customer {customer_id}. Check CUSTOMER_ID and API permissions."

    # Fetch campaign metrics for the date range separately
    campaign_metrics_query = f"""
        SELECT
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
          AND campaign.status != 'REMOVED'
        ORDER BY metrics.impressions DESC
    """

    metrics_result = query_google_ads(access_token, developer_token, customer_id, campaign_metrics_query, login_customer_id)

    # Build metrics lookup by campaign name
    metrics_by_name: dict[str, dict] = {}
    if metrics_result:
        for batch in metrics_result:
            for row in batch.get("results", []):
                name = row.get("campaign", {}).get("name", "")
                m = row.get("metrics", {})
                metrics_by_name[name] = m

    # Parse campaign data — merge all campaigns with their metrics
    campaigns = []
    total = {"impressions": 0, "clicks": 0, "cost": 0, "conversions": 0, "conv_value": 0}
    status_map = {"ENABLED": "active", "PAUSED": "paused", "REMOVED": "ended"}

    for batch in campaign_result:
        for row in batch.get("results", []):
            camp = row.get("campaign", {})
            name = camp.get("name", "Unknown")
            m = metrics_by_name.get(name, {})

            impressions = int(m.get("impressions", 0))
            clicks = int(m.get("clicks", 0))
            cost = int(m.get("costMicros", 0))
            conversions = float(m.get("conversions", 0))
            conv_value = float(m.get("conversionsValue", 0))
            ctr = float(m.get("ctr", 0)) * 100

            total["impressions"] += impressions
            total["clicks"] += clicks
            total["cost"] += cost
            total["conversions"] += conversions
            total["conv_value"] += conv_value

            roas = round(conv_value / (cost / 1_000_000), 1) if cost > 0 else 0

            channel = camp.get("advertisingChannelType", "UNKNOWN")
            raw_status = camp.get("status", "")
            # REMOVED campaigns and VIDEO/SMART campaigns can't be mutated
            mutable = raw_status != "REMOVED" and channel in ("SEARCH", "DISPLAY", "SHOPPING")

            campaigns.append({
                "name": name,
                "status": status_map.get(raw_status, "ended"),
                "channel": channel,
                "mutable": mutable,
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr, 2),
                "cost": cost,
                "conversions": round(conversions),
                "roas": roas,
            })

    # Fetch daily metrics
    daily_query = f"""
        SELECT
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM customer
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC
    """

    daily_result = query_google_ads(access_token, developer_token, customer_id, daily_query, login_customer_id)
    daily = []
    if daily_result:
        for batch in daily_result:
            for row in batch.get("results", []):
                seg = row.get("segments", {})
                m = row.get("metrics", {})
                daily.append({
                    "date": seg.get("date", ""),
                    "impressions": int(m.get("impressions", 0)),
                    "clicks": int(m.get("clicks", 0)),
                    "conversions": round(float(m.get("conversions", 0))),
                    "cost": int(m.get("costMicros", 0)),
                })

    overall_ctr = round((total["clicks"] / total["impressions"] * 100), 2) if total["impressions"] > 0 else 0
    overall_roas = round(total["conv_value"] / (total["cost"] / 1_000_000), 1) if total["cost"] > 0 else 0

    return {
        "source": "google_ads_api",
        "kpis": {
            "impressions": total["impressions"],
            "clicks": total["clicks"],
            "ctr": overall_ctr,
            "conversions": round(total["conversions"]),
            "cost": total["cost"],
            "roas": overall_roas,
        },
        "campaigns": campaigns,
        "daily": daily,
    }


def get_demo_data(days: int) -> dict:
    """Return demo data with a multiplier based on date range."""
    m = 4.2 if days >= 30 else (2.0 if days >= 14 else 1.0)
    return {
        "source": "demo",
        "kpis": {
            "impressions": int(DEMO_KPIS["impressions"] * m),
            "clicks": int(DEMO_KPIS["clicks"] * m),
            "ctr": DEMO_KPIS["ctr"],
            "conversions": int(DEMO_KPIS["conversions"] * m),
            "cost": int(DEMO_KPIS["cost"] * m),
            "roas": DEMO_KPIS["roas"],
        },
        "campaigns": DEMO_CAMPAIGNS,
        "daily": DEMO_DAILY,
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse ?days=7 from query string
        from urllib.parse import urlparse, parse_qs
        query = parse_qs(urlparse(self.path).query)
        days = int(query.get("days", [7])[0])
        days = min(max(days, 1), 90)

        demo = query.get("demo", ["false"])[0].lower() == "true"

        if demo:
            data = get_demo_data(days)
        else:
            result = fetch_real_data(days)
            if isinstance(result, str):
                print(f"[GoogleAds] {result}")
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": result}).encode())
                return
            data = result

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

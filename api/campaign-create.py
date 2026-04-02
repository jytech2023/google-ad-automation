"""Create full campaign — budget + campaign + ad group + responsive search ad + keywords."""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler

try:
    import psycopg2
    HAS_DB = True
except ImportError:
    HAS_DB = False


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
        daily_budget = data.get("dailyBudget", 0)
        channel = data.get("channel", "SEARCH").upper()
        auth0_id = data.get("auth0Id", "").strip()

        # Ad copy from AI plan
        headlines = data.get("headlines", [])
        descriptions = data.get("descriptions", [])
        keywords = data.get("keywords", [])
        final_url = data.get("finalUrl", "").strip()

        if not name or daily_budget <= 0:
            self._respond(400, {"error": "name and dailyBudget (> 0) are required"})
            return

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

        created = {"budget": None, "campaign": None, "adGroup": None, "ad": None, "keywords": 0}
        errors = []

        # Step 1: Create budget
        budget_micros = str(int(daily_budget * 1_000_000))
        result, code = ads_mutate(access_token, customer_id, "campaignBudgets:mutate", {
            "operations": [{"create": {
                "name": f"{name} Budget",
                "amountMicros": budget_micros,
                "deliveryMethod": "STANDARD",
                "explicitlyShared": False,
            }}]
        }, login_customer_id)
        if code != 200:
            self._respond(code, {"error": "Failed to create budget", "details": result})
            return
        budget_resource = result.get("results", [{}])[0].get("resourceName", "")
        created["budget"] = budget_resource

        # Step 2: Create campaign
        result, code = ads_mutate(access_token, customer_id, "campaigns:mutate", {
            "operations": [{"create": {
                "name": name,
                "status": status,
                "advertisingChannelType": channel,
                "campaignBudget": budget_resource,
                "manualCpc": {},
                "contains_eu_political_advertising": 2,
            }}]
        }, login_customer_id)
        if code != 200:
            self._respond(code, {"error": "Failed to create campaign", "details": result})
            return
        campaign_resource = result.get("results", [{}])[0].get("resourceName", "")
        created["campaign"] = campaign_resource

        # Step 3: Create ad group
        ad_group_name = f"{name} — Ad Group"
        result, code = ads_mutate(access_token, customer_id, "adGroups:mutate", {
            "operations": [{"create": {
                "name": ad_group_name,
                "campaign": campaign_resource,
                "status": "PAUSED",
                "type": "SEARCH_STANDARD" if channel == "SEARCH" else "DISPLAY_STANDARD",
                "cpcBidMicros": str(int(daily_budget * 100_000)),  # ~10% of daily budget as default CPC
            }}]
        }, login_customer_id)
        if code == 200:
            ad_group_resource = result.get("results", [{}])[0].get("resourceName", "")
            created["adGroup"] = ad_group_resource
        else:
            errors.append({"step": "adGroup", "details": result})
            ad_group_resource = None

        # Step 4: Create responsive search ad (if we have ad copy and an ad group)
        if ad_group_resource and headlines and descriptions:
            # Google requires 3-15 headlines (max 30 chars) and 2-4 descriptions (max 90 chars)
            ad_headlines = [{"text": h[:30]} for h in headlines[:15]]
            ad_descriptions = [{"text": d[:90]} for d in descriptions[:4]]

            # Ensure minimums
            while len(ad_headlines) < 3:
                ad_headlines.append({"text": f"{name[:25]} Ads"})
            while len(ad_descriptions) < 2:
                ad_descriptions.append({"text": f"Learn more about {name[:70]}."})

            ad_url = final_url or f"https://example.com"
            result, code = ads_mutate(access_token, customer_id, "adGroupAds:mutate", {
                "operations": [{"create": {
                    "adGroup": ad_group_resource,
                    "status": "PAUSED",
                    "ad": {
                        "responsiveSearchAd": {
                            "headlines": ad_headlines,
                            "descriptions": ad_descriptions,
                        },
                        "finalUrls": [ad_url],
                    },
                }}]
            }, login_customer_id)
            if code == 200:
                created["ad"] = result.get("results", [{}])[0].get("resourceName", "")
            else:
                errors.append({"step": "ad", "details": result})

        # Step 5: Add keywords (for SEARCH campaigns)
        if ad_group_resource and keywords and channel == "SEARCH":
            kw_operations = []
            for kw in keywords[:20]:  # Max 20 keywords per batch
                kw_operations.append({"create": {
                    "adGroup": ad_group_resource,
                    "keyword": {
                        "text": kw,
                        "matchType": "BROAD",
                    },
                }})

            if kw_operations:
                result, code = ads_mutate(access_token, customer_id, "adGroupCriteria:mutate", {
                    "operations": kw_operations,
                }, login_customer_id)
                if code == 200:
                    created["keywords"] = len(kw_operations)
                else:
                    errors.append({"step": "keywords", "details": result})

        # Record in DB
        if auth0_id and HAS_DB and os.environ.get("DATABASE_URL"):
            try:
                conn = psycopg2.connect(os.environ["DATABASE_URL"])
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE auth0_id = %s", (auth0_id,))
                user_row = cur.fetchone()
                if user_row:
                    user_id = user_row[0]
                    cur.execute("""
                        SELECT aa.id, aa.org_id FROM ad_accounts aa
                        JOIN organization_members om ON om.org_id = aa.org_id
                        WHERE om.user_id = %s AND aa.platform = 'google' AND aa.account_id = %s
                        LIMIT 1
                    """, (user_id, customer_id))
                    acct = cur.fetchone()
                    ad_account_id = acct[0] if acct else None
                    org_id = acct[1] if acct else None

                    cur.execute("""
                        INSERT INTO campaigns
                            (org_id, ad_account_id, platform, platform_campaign_id,
                             campaign_name, channel, daily_budget, status, created_by)
                        VALUES (%s, %s, 'google', %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (platform, platform_campaign_id)
                        DO UPDATE SET campaign_name = EXCLUDED.campaign_name, updated_at = NOW()
                    """, (org_id, ad_account_id, campaign_resource, name, channel, daily_budget, status, user_id))
                    conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"[CampaignCreate] DB error (non-fatal): {e}")

        self._respond(200, {
            "success": True,
            "campaignName": name,
            "resourceName": campaign_resource,
            "status": status,
            "dailyBudget": daily_budget,
            "created": created,
            "errors": errors,
        })

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

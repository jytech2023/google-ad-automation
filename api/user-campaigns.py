"""User campaigns API — list campaigns for a user, filtered by org and platform."""
from __future__ import annotations

import json
import os
import psycopg2
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL", ""))


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        auth0_id = query.get("auth0Id", [None])[0]
        org_id = query.get("orgId", [None])[0]
        platform = query.get("platform", [None])[0]  # optional: 'google', 'meta', 'tiktok'

        if not auth0_id:
            self._respond(400, {"error": "auth0Id query param required"})
            return

        try:
            conn = get_db()
            cur = conn.cursor()

            cur.execute("SELECT id FROM users WHERE auth0_id = %s", (auth0_id,))
            user_row = cur.fetchone()
            if not user_row:
                cur.close(); conn.close()
                self._respond(200, {"campaigns": []})
                return

            user_id = user_row[0]

            # Build query with optional filters
            sql = """
                SELECT c.platform, c.platform_campaign_id, c.campaign_name, c.channel,
                       c.daily_budget, c.currency, c.status, c.created_at,
                       aa.account_name, o.name as org_name
                FROM campaigns c
                JOIN organization_members om ON om.org_id = c.org_id AND om.user_id = %s
                LEFT JOIN ad_accounts aa ON aa.id = c.ad_account_id
                LEFT JOIN organizations o ON o.id = c.org_id
                WHERE 1=1
            """
            params = [user_id]

            if org_id:
                sql += " AND c.org_id = %s"
                params.append(int(org_id))
            if platform:
                sql += " AND c.platform = %s"
                params.append(platform)

            sql += " ORDER BY c.created_at DESC"

            cur.execute(sql, params)
            rows = cur.fetchall()
            cur.close(); conn.close()

            campaigns = []
            for r in rows:
                campaigns.append({
                    "platform": r[0],
                    "platformCampaignId": r[1],
                    "name": r[2],
                    "channel": r[3],
                    "dailyBudget": float(r[4]) if r[4] else 0,
                    "currency": r[5],
                    "status": r[6],
                    "createdAt": r[7].isoformat() if r[7] else None,
                    "accountName": r[8],
                    "orgName": r[9],
                })

            self._respond(200, {"campaigns": campaigns})
        except Exception as e:
            self._respond(500, {"error": f"Database error: {e}"})

    def _respond(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

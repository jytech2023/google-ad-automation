"""Organization API — list user orgs, create org, manage members."""
from __future__ import annotations

import json
import os
import psycopg2
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL", ""))


def get_user_id(cur, auth0_id: str) -> int | None:
    cur.execute("SELECT id FROM users WHERE auth0_id = %s", (auth0_id,))
    row = cur.fetchone()
    return row[0] if row else None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """List orgs for a user."""
        query = parse_qs(urlparse(self.path).query)
        auth0_id = query.get("auth0Id", [None])[0]
        if not auth0_id:
            self._respond(400, {"error": "auth0Id required"})
            return

        try:
            conn = get_db()
            cur = conn.cursor()
            user_id = get_user_id(cur, auth0_id)
            if not user_id:
                cur.close(); conn.close()
                self._respond(200, {"orgs": []})
                return

            cur.execute("""
                SELECT o.id, o.name, o.domain, o.plan, om.role
                FROM organizations o
                JOIN organization_members om ON om.org_id = o.id
                WHERE om.user_id = %s
                ORDER BY o.name
            """, (user_id,))
            orgs = []
            for r in cur.fetchall():
                orgs.append({
                    "id": r[0], "name": r[1], "domain": r[2],
                    "plan": r[3], "role": r[4],
                })
            cur.close(); conn.close()
            self._respond(200, {"orgs": orgs})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_POST(self):
        """Create org or add member."""
        content_length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(content_length))

        action = data.get("action", "create")
        auth0_id = data.get("auth0Id", "").strip()
        if not auth0_id:
            self._respond(400, {"error": "auth0Id required"})
            return

        try:
            conn = get_db()
            cur = conn.cursor()
            user_id = get_user_id(cur, auth0_id)
            if not user_id:
                cur.close(); conn.close()
                self._respond(400, {"error": "User not found"})
                return

            if action == "create":
                name = data.get("name", "").strip()
                domain = data.get("domain", "").strip()
                if not name:
                    cur.close(); conn.close()
                    self._respond(400, {"error": "name required"})
                    return

                cur.execute("""
                    INSERT INTO organizations (name, domain, created_by, plan)
                    VALUES (%s, %s, %s, 'starter')
                    RETURNING id
                """, (name, domain or None, user_id))
                org_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO organization_members (org_id, user_id, role)
                    VALUES (%s, %s, 'admin')
                """, (org_id, user_id))
                conn.commit()
                cur.close(); conn.close()
                self._respond(200, {"success": True, "orgId": org_id})

            elif action == "addMember":
                org_id = data.get("orgId")
                member_email = data.get("email", "").strip()
                role = data.get("role", "member")
                if not org_id or not member_email:
                    cur.close(); conn.close()
                    self._respond(400, {"error": "orgId and email required"})
                    return

                cur.execute("SELECT role FROM organization_members WHERE org_id = %s AND user_id = %s", (org_id, user_id))
                caller_role = cur.fetchone()
                if not caller_role or caller_role[0] not in ('admin', 'owner'):
                    cur.close(); conn.close()
                    self._respond(403, {"error": "Only admins can add members"})
                    return

                cur.execute("SELECT id FROM users WHERE email = %s", (member_email,))
                member = cur.fetchone()
                if not member:
                    cur.close(); conn.close()
                    self._respond(404, {"error": f"User {member_email} not found"})
                    return

                cur.execute("""
                    INSERT INTO organization_members (org_id, user_id, role)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (org_id, user_id) DO UPDATE SET role = EXCLUDED.role
                """, (org_id, member[0], role))
                conn.commit()
                cur.close(); conn.close()
                self._respond(200, {"success": True})
            else:
                cur.close(); conn.close()
                self._respond(400, {"error": f"Unknown action: {action}"})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def _respond(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

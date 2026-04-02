"""User sync API — upserts Auth0 user info into the database."""
from __future__ import annotations

import json
import os
import psycopg2
from http.server import BaseHTTPRequestHandler


def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL", ""))


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        auth0_id = data.get("auth0Id", "").strip()
        email = data.get("email", "").strip()
        name = data.get("name", "").strip()
        picture = data.get("picture", "")

        if not auth0_id:
            self._respond(400, {"error": "auth0Id is required"})
            return

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (auth0_id, email, name, picture, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (auth0_id) DO UPDATE SET
                    email = EXCLUDED.email,
                    name = EXCLUDED.name,
                    picture = EXCLUDED.picture,
                    updated_at = NOW()
                RETURNING id, auth0_id, email, name
            """, (auth0_id, email, name, picture))
            row = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()

            self._respond(200, {
                "success": True,
                "user": {
                    "id": row[0],
                    "auth0Id": row[1],
                    "email": row[2],
                    "name": row[3],
                },
            })
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
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

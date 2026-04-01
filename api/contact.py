"""Contact form API endpoint for Vercel serverless function."""
import json
import os
import smtplib
from email.mime.text import MIMEText
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        company = data.get("company", "").strip()
        message = data.get("message", "").strip()

        if not name or not email or not message:
            self._respond(400, {"error": "Name, email, and message are required"})
            return

        # Send notification email (optional — requires SMTP env vars)
        smtp_host = os.environ.get("SMTP_HOST")
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")
        notify_email = os.environ.get("NOTIFY_EMAIL", smtp_user)

        if smtp_host and smtp_user and smtp_pass:
            try:
                msg = MIMEText(
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Company: {company}\n"
                    f"Message:\n{message}"
                )
                msg["Subject"] = f"[GlobalTrade Pro] New inquiry from {name}"
                msg["From"] = smtp_user
                msg["To"] = notify_email

                with smtplib.SMTP(smtp_host, 587) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            except Exception as e:
                print(f"Email send failed: {e}")

        # Google Ads conversion tracking (server-side, optional)
        google_ads_token = os.environ.get("GOOGLE_ADS_API_TOKEN")
        if google_ads_token:
            print(f"[GoogleAds] Lead conversion: {email}")

        self._respond(200, {"success": True, "message": "Inquiry received"})

    def _respond(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

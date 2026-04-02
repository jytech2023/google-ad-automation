"""AI Campaign Generator — uses Diffbot to extract website content, then Gemini to create campaigns."""
from __future__ import annotations

import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler

GEMINI_MODEL = "gemini-2.0-flash"

SYSTEM_PROMPT = """You are an expert Google Ads campaign planner. Given information about a business (either a description or extracted website content), generate optimal Google Ads campaign parameters.

Return ONLY valid JSON with this exact structure:
{
  "campaigns": [
    {
      "name": "Campaign name",
      "dailyBudget": 10,
      "channel": "SEARCH",
      "rationale": "Brief explanation of why this campaign setup"
    }
  ],
  "keywords": ["keyword1", "keyword2"],
  "adCopy": {
    "headlines": ["Headline 1", "Headline 2", "Headline 3"],
    "descriptions": ["Description 1", "Description 2"]
  },
  "targetAudience": "Brief audience description",
  "estimatedMonthlyBudget": 300,
  "tips": ["Tip 1", "Tip 2"]
}

Rules:
- channel must be one of: SEARCH, DISPLAY, SHOPPING, VIDEO
- dailyBudget is in USD, minimum 1
- Provide 1-3 campaigns depending on complexity
- Headlines max 30 characters each, descriptions max 90 characters each
- Keywords should be specific and high-intent
- Be practical and realistic with budget suggestions
- Always explain your rationale
- If website content is provided, use the actual business name, services, and value propositions from the site"""

URL_PATTERN = re.compile(r'https?://[^\s<>"\']+')


def crawl_with_diffbot(url: str, token: str) -> dict | None:
    """Extract website content using Diffbot Analyze API."""
    api_url = f"https://api.diffbot.com/v3/analyze?token={token}&url={urllib.parse.quote(url, safe='')}"
    req = urllib.request.Request(api_url)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            objects = data.get("objects", [])
            if not objects:
                return None

            obj = objects[0]
            return {
                "title": obj.get("title", ""),
                "text": obj.get("text", "")[:3000],  # limit to avoid token overflow
                "siteName": obj.get("siteName", ""),
                "categories": [c.get("name", "") for c in obj.get("categories", [])[:5]],
                "tags": [t.get("label", "") for t in obj.get("tags", [])[:10]],
                "url": url,
            }
    except Exception as e:
        print(f"[AI-Campaign] Diffbot error: {e}")
        return None


def call_gemini(prompt: str, api_key: str) -> dict | None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
    body = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser request: {prompt}"}]}
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        },
    }
    payload = json.dumps(body).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            return json.loads(text)
    except Exception as e:
        print(f"[AI-Campaign] Gemini error: {e}")
        return None


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        prompt = data.get("prompt", "").strip()
        if not prompt:
            self._respond(400, {"error": "prompt is required"})
            return

        api_key = os.environ.get("GOOGLE_GEMINI_API_KEY", "")
        if not api_key:
            self._respond(500, {"error": "GOOGLE_GEMINI_API_KEY not configured"})
            return

        # Detect URLs in the prompt and crawl them with Diffbot
        urls = URL_PATTERN.findall(prompt)
        site_content = None
        crawled_url = None

        if urls:
            diffbot_token = os.environ.get("DIFFBOT_API_TOKEN", "")
            if diffbot_token:
                for url in urls[:1]:  # crawl first URL only
                    site_content = crawl_with_diffbot(url, diffbot_token)
                    if site_content:
                        crawled_url = url
                        break

        # Build enriched prompt
        if site_content:
            enriched = f"""I want to create Google Ads campaigns for this website: {crawled_url}

Here is the extracted website content:
- Site Name: {site_content['siteName']}
- Title: {site_content['title']}
- Categories: {', '.join(site_content['categories']) if site_content['categories'] else 'N/A'}
- Key Topics: {', '.join(site_content['tags']) if site_content['tags'] else 'N/A'}
- Content: {site_content['text']}

Additional context from user: {prompt}

Based on this website content, create targeted Google Ads campaigns that highlight the actual services, products, and value propositions found on the site."""
        else:
            enriched = prompt

        result = call_gemini(enriched, api_key)
        if result is None:
            self._respond(500, {"error": "Failed to generate campaign plan. Please try again."})
            return

        response = {"success": True, "plan": result}
        if site_content:
            response["crawledSite"] = {
                "url": crawled_url,
                "title": site_content["title"],
                "siteName": site_content["siteName"],
            }

        self._respond(200, response)

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

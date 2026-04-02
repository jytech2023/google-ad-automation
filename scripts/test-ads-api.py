"""Test Google Ads API connection and optionally create a paused test campaign.

Usage:
  python3 scripts/test-ads-api.py              # Just test connection
  python3 scripts/test-ads-api.py --create      # Create a paused test campaign
"""
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

# Load .env.local
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key.strip(), val.strip())

load_env()

CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET', '')
REFRESH_TOKEN = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN', '')
DEVELOPER_TOKEN = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', '')
CUSTOMER_ID = os.environ.get('GOOGLE_ADS_CUSTOMER_ID', '')
LOGIN_CUSTOMER_ID = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')


def get_access_token():
    data = urllib.parse.urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': 'refresh_token',
    }).encode()
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())['access_token']


def ads_api_request(access_token, method, url, body=None, use_login_id=False):
    payload = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=payload, method=method)
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('developer-token', DEVELOPER_TOKEN)
    req.add_header('Content-Type', 'application/json')
    if use_login_id and LOGIN_CUSTOMER_ID:
        req.add_header('login-customer-id', LOGIN_CUSTOMER_ID)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return json.loads(body), e.code
        except json.JSONDecodeError:
            return {"error": body or f"HTTP {e.code}"}, e.code


def test_connection(access_token):
    """Test by listing accessible customers."""
    print('\n--- Step 1: Testing OAuth token ---')
    print(f'  Access token: {access_token[:20]}...')
    print('  OK\n')

    print('--- Step 2: Listing accessible customers ---')
    url = 'https://googleads.googleapis.com/v20/customers:listAccessibleCustomers'
    result, status = ads_api_request(access_token, 'GET', url)
    if status == 200:
        customers = result.get('resourceNames', [])
        print(f'  Found {len(customers)} accessible customer(s):')
        for c in customers:
            print(f'    - {c}')
    else:
        print(f'  Error ({status}): {json.dumps(result, indent=2)}')
        return False

    print(f'\n--- Step 3: Querying customer {CUSTOMER_ID} ---')
    query = """
        SELECT
            customer.descriptive_name,
            customer.id,
            customer.currency_code,
            customer.time_zone
        FROM customer
        LIMIT 1
    """
    url = f'https://googleads.googleapis.com/v20/customers/{CUSTOMER_ID}/googleAds:searchStream'
    result, status = ads_api_request(access_token, 'POST', url, {'query': query}, use_login_id=True)
    if status == 200:
        for batch in result:
            for row in batch.get('results', []):
                c = row.get('customer', {})
                print(f'  Account: {c.get("descriptiveName", "N/A")}')
                print(f'  ID: {c.get("id", "N/A")}')
                print(f'  Currency: {c.get("currencyCode", "N/A")}')
                print(f'  Timezone: {c.get("timeZone", "N/A")}')
    else:
        print(f'  Error ({status}): {json.dumps(result, indent=2)}')
        return False

    print('\n--- Step 4: Fetching campaign data ---')
    query = """
        SELECT
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM campaign
        WHERE segments.date DURING LAST_7_DAYS
        ORDER BY metrics.impressions DESC
        LIMIT 10
    """
    result, status = ads_api_request(access_token, 'POST', url, {'query': query}, use_login_id=True)
    if status == 200:
        count = 0
        for batch in result:
            for row in batch.get('results', []):
                camp = row.get('campaign', {})
                m = row.get('metrics', {})
                count += 1
                print(f'  [{camp.get("status", "?")}] {camp.get("name", "?")} — '
                      f'{m.get("impressions", 0)} impr, {m.get("clicks", 0)} clicks, '
                      f'${int(m.get("costMicros", 0)) / 1_000_000:.2f} cost')
        if count == 0:
            print('  No campaigns found (this is normal for new accounts)')
    else:
        print(f'  Error ({status}): {json.dumps(result, indent=2)}')

    return True


def create_test_campaign(access_token):
    """Create a paused test campaign (won't spend any money)."""
    print('\n--- Creating paused test campaign ---')

    # First, we need a budget
    budget_url = f'https://googleads.googleapis.com/v20/customers/{CUSTOMER_ID}/campaignBudgets:mutate'
    budget_body = {
        'operations': [{
            'create': {
                'name': f'AdFlowPro Test Budget',
                'amountMicros': '1000000',  # $1 (won't be spent since campaign is paused)
                'deliveryMethod': 'STANDARD',
                'explicitlyShared': False,
            }
        }]
    }
    result, status = ads_api_request(access_token, 'POST', budget_url, budget_body, use_login_id=True)
    if status != 200:
        print(f'  Budget creation failed ({status}): {json.dumps(result, indent=2)}')
        return

    budget_resource = result.get('results', [{}])[0].get('resourceName', '')
    print(f'  Budget created: {budget_resource}')

    # Create a paused search campaign
    campaign_url = f'https://googleads.googleapis.com/v20/customers/{CUSTOMER_ID}/campaigns:mutate'
    campaign_body = {
        'operations': [{
            'create': {
                'name': 'AdFlowPro Test Campaign (Paused)',
                'status': 'PAUSED',
                'advertisingChannelType': 'SEARCH',
                'campaignBudget': budget_resource,
                'manualCpc': {},
            }
        }]
    }
    result, status = ads_api_request(access_token, 'POST', campaign_url, campaign_body, use_login_id=True)
    if status == 200:
        camp_resource = result.get('results', [{}])[0].get('resourceName', '')
        print(f'  Campaign created (PAUSED): {camp_resource}')
        print('\n  This campaign is PAUSED and will NOT spend money.')
        print('  You can see it in your Google Ads dashboard.')
        print('  To remove it: Google Ads > Campaigns > select it > Remove')
    else:
        print(f'  Campaign creation failed ({status}): {json.dumps(result, indent=2)}')


def main():
    missing = []
    for var in ['CLIENT_ID', 'CLIENT_SECRET', 'REFRESH_TOKEN', 'DEVELOPER_TOKEN', 'CUSTOMER_ID']:
        if not globals()[var]:
            missing.append(f'GOOGLE_ADS_{var}')
    if missing:
        print(f'Missing env vars: {", ".join(missing)}')
        print('Set them in .env.local')
        sys.exit(1)

    print('=== Google Ads API Connection Test ===')
    try:
        access_token = get_access_token()
    except Exception as e:
        print(f'\nFailed to get access token: {e}')
        print('Check your CLIENT_ID, CLIENT_SECRET, and REFRESH_TOKEN')
        sys.exit(1)

    success = test_connection(access_token)

    if success and '--create' in sys.argv:
        create_test_campaign(access_token)

    if success:
        print('\n=== Connection successful! ===')
    else:
        print('\n=== Connection failed ===')
        sys.exit(1)


if __name__ == '__main__':
    main()

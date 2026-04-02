"""Database migration — make ad tables platform-agnostic to support Google, TikTok, Meta, etc."""
import os
import psycopg2

DATABASE_URL = None
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('DATABASE_URL=') and 'UNPOOLED' not in line and 'POSTGRES' not in line and 'NON_POOLING' not in line and 'NO_SSL' not in line and 'PRISMA' not in line:
                DATABASE_URL = line.split('=', 1)[1]
                break

DATABASE_URL = os.environ.get("DATABASE_URL", DATABASE_URL)
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found")
    exit(1)

print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Drop the old Google-specific tables (both are empty)
cur.execute("DROP TABLE IF EXISTS user_campaigns CASCADE")
cur.execute("DROP TABLE IF EXISTS user_ad_accounts CASCADE")
print("Dropped empty Google-specific tables")

# Create platform-agnostic ad_accounts table
# platform: 'google', 'meta', 'tiktok', 'linkedin', 'twitter', etc.
cur.execute("""
CREATE TABLE IF NOT EXISTS ad_accounts (
    id SERIAL PRIMARY KEY,
    org_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL,
    account_id VARCHAR(255) NOT NULL,
    account_name VARCHAR(255),
    credentials JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(org_id, platform, account_id)
);
""")

# Create platform-agnostic campaigns table
cur.execute("""
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    org_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    ad_account_id INTEGER REFERENCES ad_accounts(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL,
    platform_campaign_id VARCHAR(255) NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    channel VARCHAR(50),
    daily_budget NUMERIC(12,2),
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'PAUSED',
    metadata JSONB DEFAULT '{}',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(platform, platform_campaign_id)
);
""")

# Create platform-agnostic daily cost/metrics table
cur.execute("""
CREATE TABLE IF NOT EXISTS campaign_daily_metrics (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions NUMERIC(10,2) DEFAULT 0,
    cost NUMERIC(12,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    metadata JSONB DEFAULT '{}',
    UNIQUE(campaign_id, date)
);
""")

# Indexes
cur.execute("CREATE INDEX IF NOT EXISTS idx_ad_accounts_org ON ad_accounts(org_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_ad_accounts_platform ON ad_accounts(platform);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_org ON campaigns(org_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_platform ON campaigns(platform);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_ad_account ON campaigns(ad_account_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_campaign_metrics_campaign ON campaign_daily_metrics(campaign_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_campaign_metrics_date ON campaign_daily_metrics(date);")

conn.commit()
cur.close()
conn.close()

print("""
Migration complete! New tables:

  ad_accounts        — Links orgs to ad platform accounts (Google, Meta, TikTok, etc.)
                       platform: 'google' | 'meta' | 'tiktok' | 'linkedin' | 'twitter'
                       credentials: JSONB for platform-specific auth tokens

  campaigns          — Platform-agnostic campaign tracking
                       platform_campaign_id: the ID from the ad platform
                       metadata: JSONB for platform-specific fields

  campaign_daily_metrics — Daily cost/performance per campaign
                       metadata: JSONB for platform-specific metrics (e.g. video views for TikTok)
""")

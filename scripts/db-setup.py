"""Database setup — creates tables for user campaign ownership tracking."""
import os
import urllib.parse
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Try loading from .env.local
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('DATABASE_URL=') and 'UNPOOLED' not in line and 'POSTGRES' not in line and 'NON_POOLING' not in line and 'NO_SSL' not in line and 'PRISMA' not in line:
                    DATABASE_URL = line.split('=', 1)[1]
                    break

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found")
    exit(1)

print(f"Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Users table — stores Auth0 user info
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    auth0_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    name VARCHAR(255),
    picture TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
""")

# User Google Ads accounts — links users to their Google Ads customer IDs
cur.execute("""
CREATE TABLE IF NOT EXISTS user_ad_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    google_ads_customer_id VARCHAR(20) NOT NULL,
    account_name VARCHAR(255),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, google_ads_customer_id)
);
""")

# Campaign ownership — tracks which user created/owns which campaign
cur.execute("""
CREATE TABLE IF NOT EXISTS user_campaigns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    google_ads_customer_id VARCHAR(20) NOT NULL,
    campaign_resource_name VARCHAR(255) NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    channel VARCHAR(20),
    daily_budget NUMERIC(10,2),
    status VARCHAR(20) DEFAULT 'PAUSED',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(google_ads_customer_id, campaign_resource_name)
);
""")

# Indexes
cur.execute("CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON users(auth0_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_user_campaigns_user_id ON user_campaigns(user_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_user_ad_accounts_user_id ON user_ad_accounts(user_id);")

conn.commit()
cur.close()
conn.close()

print("Database setup complete!")
print("Tables created: users, user_ad_accounts, user_campaigns")

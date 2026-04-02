"""Database migration — adds organization tables for multi-org support."""
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

cur.execute("""
CREATE TABLE IF NOT EXISTS orgs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    google_ads_customer_id VARCHAR(20),
    credits NUMERIC(12,2) DEFAULT 0,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS org_members (
    id SERIAL PRIMARY KEY,
    org_id INTEGER REFERENCES orgs(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(org_id, user_id)
);
""")

# Add org_id to user_campaigns if not exists
cur.execute("""
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='user_campaigns' AND column_name='org_id') THEN
        ALTER TABLE user_campaigns ADD COLUMN org_id INTEGER REFERENCES orgs(id);
    END IF;
END $$;
""")

cur.execute("CREATE INDEX IF NOT EXISTS idx_org_members_user ON org_members(user_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_org_members_org ON org_members(org_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_orgs_slug ON orgs(slug);")

conn.commit()
cur.close()
conn.close()

print("Organization tables created: orgs, org_members")
print("Added org_id column to user_campaigns")

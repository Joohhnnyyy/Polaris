-- Enable the pgvector extension for semantic search (Gemini gemini-embedding-2 is 3072 dimensions)
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS briefs;
DROP TABLE IF EXISTS issues;
DROP TABLE IF EXISTS clusters;
DROP TABLE IF EXISTS officers;

-- Drop custom types if they exist
DROP TYPE IF EXISTS risk_level_enum;
DROP TYPE IF EXISTS issue_status_enum;

-- Create Enums for strict type safety
CREATE TYPE risk_level_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE issue_status_enum AS ENUM ('REPORTED', 'ANALYZING', 'VERIFIED', 'ESCALATED', 'RESOLVED');

-- 1. Create Officers Table
CREATE TABLE officers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    zone_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create Clusters Table
CREATE TABLE clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id VARCHAR(50),
    center_lat DOUBLE PRECISION NOT NULL,
    center_lng DOUBLE PRECISION NOT NULL,
    radius_m INT DEFAULT 300,
    risk_level risk_level_enum NOT NULL DEFAULT 'LOW',
    causal_hypothesis TEXT,
    confidence FLOAT DEFAULT 0.0,
    affected_residents INT DEFAULT 0,
    evidence_chain JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    explainability_factors TEXT[] DEFAULT '{}',
    assigned_officer_id UUID REFERENCES officers(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create Issues Table
CREATE TABLE issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50) NOT NULL,
    severity INT NOT NULL CHECK (severity BETWEEN 1 AND 5),
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    description TEXT,
    images TEXT[] DEFAULT '{}', -- URLs to Supabase Storage
    status issue_status_enum NOT NULL DEFAULT 'REPORTED',
    credibility_score FLOAT NOT NULL DEFAULT 1.0,
    verification_votes INT NOT NULL DEFAULT 1,
    dispute_votes INT NOT NULL DEFAULT 0,
    embedding vector(3072), -- Gemini gemini-embedding-2 vector (3072 dimensions)
    gemini_analysis JSONB DEFAULT '{}'::jsonb,
    confidence_breakdown JSONB DEFAULT '{}'::jsonb,
    is_civic_issue BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    cluster_id UUID REFERENCES clusters(id) ON DELETE SET NULL
);

-- 4. Create Briefs Table
CREATE TABLE briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cluster_id UUID REFERENCES clusters(id) ON DELETE CASCADE,
    officer_id UUID REFERENCES officers(id) ON DELETE SET NULL,
    draft_email TEXT,
    work_order JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(20) DEFAULT 'PENDING_REVIEW',
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast spatial coordinates and similarity queries
CREATE INDEX IF NOT EXISTS issues_coordinates_idx ON issues(lat, lng);
CREATE INDEX IF NOT EXISTS clusters_coordinates_idx ON clusters(center_lat, center_lng);

-- Foreign Key Indexes for fast Joins
CREATE INDEX IF NOT EXISTS issues_cluster_idx ON issues(cluster_id);
CREATE INDEX IF NOT EXISTS briefs_cluster_idx ON briefs(cluster_id);

-- IVFFlat Vector Index for fast semantic queries (using cosine ops)
CREATE INDEX IF NOT EXISTS issues_embedding_idx ON issues USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

-- Similarity search function with spatial filter and NULL protection
CREATE OR REPLACE FUNCTION find_similar_issues(
    query_embedding vector(768),
    center_lat DOUBLE PRECISION,
    center_lng DOUBLE PRECISION,
    radius_meters FLOAT,
    days_back INT
)
RETURNS TABLE (
    id UUID,
    category VARCHAR,
    severity INT,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    description TEXT,
    images TEXT[],
    status VARCHAR,
    credibility_score FLOAT,
    created_at TIMESTAMPTZ,
    cluster_id UUID,
    distance_meters FLOAT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.id,
        i.category,
        i.severity,
        i.lat,
        i.lng,
        i.description,
        i.images,
        i.status::VARCHAR,
        i.credibility_score,
        i.created_at,
        i.cluster_id,
        (111320.0 * sqrt(power(i.lat - center_lat, 2) + power(cos(radians(center_lat)) * (i.lng - center_lng), 2)))::FLOAT as distance_meters,
        (1.0 - (i.embedding <=> query_embedding))::FLOAT as similarity
    FROM issues i
    WHERE 
        i.embedding IS NOT NULL
        AND i.created_at >= NOW() - (days_back || ' days')::INTERVAL
        AND (111320.0 * sqrt(power(i.lat - center_lat, 2) + power(cos(radians(center_lat)) * (i.lng - center_lng), 2))) <= radius_meters
    ORDER BY (i.embedding <=> query_embedding) ASC;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update last_updated timestamp on clusters
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_clusters_timestamp
BEFORE UPDATE ON clusters
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

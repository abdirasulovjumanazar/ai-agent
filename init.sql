-- pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- App user (allaqachon mavjud bo'lsa xato bermaydi)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ai_readonly') THEN
        CREATE USER ai_readonly WITH PASSWORD 'readonly123';
    END IF;
END
$$;
GRANT CONNECT ON DATABASE ai_agent TO ai_readonly;
GRANT USAGE ON SCHEMA public TO ai_readonly;

-- Chunks -> embeddings jadvali
CREATE TABLE IF NOT EXISTS embeddings (
    id        TEXT PRIMARY KEY,
    text      TEXT        NOT NULL,
    metadata  JSONB       DEFAULT '{}',
    embedding vector(3072)
);

-- Savol-javob kesh jadvali
CREATE TABLE IF NOT EXISTS query_cache (
    id        TEXT PRIMARY KEY,
    question  TEXT  NOT NULL,
    answer    JSONB NOT NULL,
    embedding vector(3072)
);

-- HNSW indexlar (tez cosine qidirish uchun)
CREATE INDEX IF NOT EXISTS embeddings_hnsw_idx
    ON embeddings USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS query_cache_hnsw_idx
    ON query_cache USING hnsw (embedding vector_cosine_ops);

-- Chat tarixi jadvali
CREATE TABLE IF NOT EXISTS chat_history (
    id         BIGSERIAL PRIMARY KEY,
    session_id TEXT      NOT NULL,
    role       TEXT      NOT NULL,
    content    TEXT      NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_history_session
    ON chat_history(session_id, created_at);

-- Ruxsatlar
GRANT SELECT, INSERT, UPDATE, DELETE ON embeddings          TO ai_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON query_cache         TO ai_readonly;
GRANT SELECT, INSERT                 ON chat_history        TO ai_readonly;
GRANT USAGE, SELECT ON SEQUENCE chat_history_id_seq         TO ai_readonly;

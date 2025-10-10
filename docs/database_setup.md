# Database Setup Guide

This guide will help you set up the database for EasyRag using Supabase (PostgreSQL with pgvector).

## Prerequisites

- A Supabase account (free tier works fine)
- PostgreSQL 14+ with pgvector extension (provided by Supabase)

## Step 1: Create a Supabase Project

1. Go to [Supabase](https://supabase.com) and sign in
2. Create a new project
3. Note your project URL and anon key from the project settings

## Step 2: Enable pgvector Extension

Run this in the Supabase SQL editor:

```sql
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

## Step 3: Create the Documents Table

```sql
-- Create the main documents table
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),  -- Adjust dimensions if using different model
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on metadata for faster filtering
CREATE INDEX IF NOT EXISTS documents_metadata_idx ON documents USING gin(metadata);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS documents_created_at_idx ON documents(created_at DESC);
```

## Step 4: Create Vector Search Function

This function enables semantic search using vector similarity:

```sql
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'::jsonb,
    source_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM documents d
    WHERE 
        (source_filter IS NULL OR d.metadata->>'source' = source_filter)
        AND (filter = '{}'::jsonb OR d.metadata @> filter)
        AND d.embedding IS NOT NULL
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

## Step 5: Create Vector Index (Optional but Recommended)

For better performance on large datasets:

```sql
-- Create IVFFlat index for approximate nearest neighbor search
-- Adjust 'lists' parameter based on your dataset size:
-- - Small datasets (<10k): lists = 100
-- - Medium datasets (10k-100k): lists = 1000
-- - Large datasets (>100k): lists = 10000

CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## Step 6: Set Up Hybrid Search (Optional)

If you want to use hybrid search (combining vector and full-text search):

### 6.1: Add Full-Text Search Column

```sql
-- Add tsvector column for full-text search
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS content_tsv tsvector;

-- Create function to update tsvector
CREATE OR REPLACE FUNCTION documents_content_tsv_update() 
RETURNS trigger AS $$
BEGIN
    NEW.content_tsv := to_tsvector('english', COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update tsvector
DROP TRIGGER IF EXISTS documents_content_tsv_trigger ON documents;
CREATE TRIGGER documents_content_tsv_trigger
BEFORE INSERT OR UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION documents_content_tsv_update();

-- Update existing rows
UPDATE documents SET content_tsv = to_tsvector('english', content);
```

### 6.2: Create Full-Text Search Index

```sql
-- Create GIN index for full-text search
CREATE INDEX IF NOT EXISTS documents_content_tsv_idx 
ON documents 
USING gin(content_tsv);
```

### 6.3: Create Hybrid Search Function

```sql
CREATE OR REPLACE FUNCTION hybrid_search_documents(
    query_embedding vector(1536),
    query_text TEXT,
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'::jsonb,
    source_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT,
    match_type TEXT
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM (
        -- Vector search results
        SELECT
            d.id,
            d.content,
            d.metadata,
            1 - (d.embedding <=> query_embedding) AS similarity,
            'vector'::TEXT AS match_type
        FROM documents d
        WHERE 
            (source_filter IS NULL OR d.metadata->>'source' = source_filter)
            AND (filter = '{}'::jsonb OR d.metadata @> filter)
            AND d.embedding IS NOT NULL
        ORDER BY d.embedding <=> query_embedding
        LIMIT match_count
        
        UNION
        
        -- Full-text search results
        SELECT
            d.id,
            d.content,
            d.metadata,
            ts_rank(d.content_tsv, plainto_tsquery('english', query_text)) AS similarity,
            'fulltext'::TEXT AS match_type
        FROM documents d
        WHERE 
            d.content_tsv @@ plainto_tsquery('english', query_text)
            AND (source_filter IS NULL OR d.metadata->>'source' = source_filter)
            AND (filter = '{}'::jsonb OR d.metadata @> filter)
        ORDER BY similarity DESC
        LIMIT match_count
    ) combined
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
```

## Step 7: Create Helper Views (Optional)

Useful views for monitoring:

```sql
-- View for document statistics
CREATE OR REPLACE VIEW documents_stats AS
SELECT
    COUNT(*) as total_documents,
    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as documents_with_embeddings,
    COUNT(DISTINCT metadata->>'source') as unique_sources,
    MIN(created_at) as oldest_document,
    MAX(created_at) as newest_document
FROM documents;

-- View for documents by source
CREATE OR REPLACE VIEW documents_by_source AS
SELECT
    metadata->>'source' as source,
    COUNT(*) as count,
    MAX(created_at) as last_updated
FROM documents
GROUP BY metadata->>'source'
ORDER BY count DESC;
```

## Step 8: Test Your Setup

Run these queries to verify everything is set up correctly:

```sql
-- Check if pgvector is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check table structure
\d documents

-- Check indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'documents';

-- Check functions
SELECT routine_name, routine_type 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_name LIKE '%documents%';

-- View statistics
SELECT * FROM documents_stats;
```

## Troubleshooting

### Issue: "pgvector extension not found"

**Solution**: Make sure you're using Supabase or PostgreSQL 14+ with pgvector installed.

### Issue: "Index creation takes too long"

**Solution**: Create indexes after inserting data, or use concurrent index creation:
```sql
CREATE INDEX CONCURRENTLY documents_embedding_idx ON documents USING ivfflat (embedding vector_cosine_ops);
```

### Issue: "Poor search performance"

**Solutions**:
1. Ensure indexes are created
2. Adjust the `lists` parameter in the ivfflat index
3. Run `ANALYZE documents;` to update statistics

## Next Steps

1. Configure your `.env` file with Supabase credentials
2. Start indexing documents using the examples
3. Test search functionality

## Additional Resources

- [Supabase Vector Guide](https://supabase.com/docs/guides/ai/vector-columns)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)

-- Create video_generations table
CREATE TABLE IF NOT EXISTS video_generations (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    prompt TEXT NOT NULL,
    image_urls JSON DEFAULT '[]',
    duration INTEGER DEFAULT 30,
    style VARCHAR(100) DEFAULT 'cinematic',
    music_genre VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    video_url VARCHAR(500),
    error_message TEXT,
    external_job_id VARCHAR(200),
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create index on created_by for faster user queries
CREATE INDEX IF NOT EXISTS idx_video_generations_created_by ON video_generations(created_by);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_video_generations_status ON video_generations(status);
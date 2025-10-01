-- Comprehensive migration to add all missing columns to video_generations table

-- Add parsed_content field
ALTER TABLE video_generations
ADD COLUMN IF NOT EXISTS parsed_content JSON;

-- Add kazanim_details field
ALTER TABLE video_generations
ADD COLUMN IF NOT EXISTS kazanim_details JSON;

-- Add curriculum_details field
ALTER TABLE video_generations
ADD COLUMN IF NOT EXISTS curriculum_details JSON;

-- Verify all columns are present
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'video_generations'
ORDER BY ordinal_position;
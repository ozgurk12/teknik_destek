-- Add parsed_content field to video_generations table
ALTER TABLE video_generations
ADD COLUMN IF NOT EXISTS parsed_content JSON;
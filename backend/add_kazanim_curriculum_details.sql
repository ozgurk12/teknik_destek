-- Add kazanim_details and curriculum_details fields to video_generations table
ALTER TABLE video_generations
ADD COLUMN IF NOT EXISTS kazanim_details JSON,
ADD COLUMN IF NOT EXISTS curriculum_details JSON;
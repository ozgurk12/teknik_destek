-- Add educational content fields to video_generations table
ALTER TABLE video_generations
ADD COLUMN IF NOT EXISTS ders VARCHAR(100),
ADD COLUMN IF NOT EXISTS konu VARCHAR(200),
ADD COLUMN IF NOT EXISTS yas_grubu VARCHAR(50),
ADD COLUMN IF NOT EXISTS kazanim_ids JSON DEFAULT '[]',
ADD COLUMN IF NOT EXISTS curriculum_ids JSON DEFAULT '[]',
ADD COLUMN IF NOT EXISTS video_yapisi VARCHAR(100),
ADD COLUMN IF NOT EXISTS bolum_sonu_etkinligi TEXT,
ADD COLUMN IF NOT EXISTS vurgu_noktalari TEXT,
ADD COLUMN IF NOT EXISTS kacinilacaklar TEXT;
-- Aylık Planlar ve Video Generation modüllerini ekle

-- Aylık Planlar modülü
INSERT INTO modules (name, display_name, description, is_active, created_at)
VALUES (
    'aylik_plan',
    'Aylık Planlar',
    'Aylık plan oluşturma ve yönetim yetkisi',
    true,
    NOW()
) ON CONFLICT (name) DO NOTHING;

-- Video Generation modülü
INSERT INTO modules (name, display_name, description, is_active, created_at)
VALUES (
    'video_generation',
    'Video Oluşturma',
    'Video oluşturma ve yönetim yetkisi',
    true,
    NOW()
) ON CONFLICT (name) DO NOTHING;

-- Admin kullanıcısına otomatik olarak bu modüllerin yetkisini ver
-- (admin@edupage.com kullanıcısı için)
INSERT INTO user_modules (user_id, module_id)
SELECT u.id, m.id
FROM users u
CROSS JOIN modules m
WHERE u.email = 'admin@edupage.com'
  AND m.name IN ('aylik_plan', 'video_generation')
ON CONFLICT (user_id, module_id) DO NOTHING;

-- Tüm admin rolündeki kullanıcılara bu modülleri ekle
INSERT INTO user_modules (user_id, module_id)
SELECT u.id, m.id
FROM users u
CROSS JOIN modules m
WHERE u.role = 'admin'
  AND m.name IN ('aylik_plan', 'video_generation')
ON CONFLICT (user_id, module_id) DO NOTHING;
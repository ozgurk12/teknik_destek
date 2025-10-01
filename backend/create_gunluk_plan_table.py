#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create gunluk_planlar table
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.session import async_engine
from app.models.gunluk_plan import GunlukPlan
from app.db.base_class import Base

async def create_table():
    """Create the gunluk_planlar table"""
    async with async_engine.begin() as conn:
        # Create table using raw SQL
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS gunluk_planlar (
                id SERIAL PRIMARY KEY,
                plan_adi VARCHAR(255) NOT NULL,
                tarih DATE NOT NULL,
                yas_grubu VARCHAR(50) NOT NULL,
                sinif VARCHAR(100),
                ogretmen VARCHAR(255),
                etkinlik_idleri INTEGER[] DEFAULT '{}',
                alan_becerileri JSON DEFAULT '{}',
                kavramsal_beceriler JSON DEFAULT '{}',
                egilimler JSON DEFAULT '{}',
                sosyal_duygusal_beceriler JSON DEFAULT '{}',
                degerler JSON DEFAULT '{}',
                okuryazarlik_becerileri JSON DEFAULT '{}',
                ogrenme_ciktilari JSON DEFAULT '{}',
                kavramlar TEXT,
                sozcukler TEXT,
                materyaller TEXT,
                egitim_ortamlari TEXT,
                gune_baslama TEXT,
                ogrenme_merkezleri TEXT,
                beslenme_toplanma TEXT,
                etkinlikler TEXT,
                degerlendirme TEXT,
                zenginlestirme TEXT,
                destekleme TEXT,
                aile_katilimi TEXT,
                toplum_katilimi TEXT,
                notlar TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                created_by VARCHAR(255),
                ai_generated BOOLEAN DEFAULT FALSE,
                ai_prompt TEXT
            )
        """))
        print("✅ Günlük planlar tablosu oluşturuldu!")

if __name__ == "__main__":
    asyncio.run(create_table())
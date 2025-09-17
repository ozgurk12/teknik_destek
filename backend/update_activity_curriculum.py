#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import psycopg2
from psycopg2 import sql
import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('POSTGRES_HOST', '172.16.15.222')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_USER = os.getenv('POSTGRES_USER', 'pgadmin')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'K12P0stgr32025!!**')
DB_NAME = os.getenv('POSTGRES_DB', 'edupage_kids')

def extract_curriculum_from_kazanims(kazanim_ids: List[int], conn) -> Dict[str, Any]:
    """Extract curriculum components from kazanims"""

    cur = conn.cursor()

    # Initialize collections
    alan_becerileri = {}
    ogrenme_ciktilari = {}
    kavramsal_beceriler = []
    egilimler = []
    sosyal_duygusal = []
    degerler = []
    okuryazarlik = []

    # Fetch kazanims
    cur.execute(
        "SELECT * FROM kazanimlar WHERE id = ANY(%s)",
        (kazanim_ids,)
    )

    kazanims = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    for row in kazanims:
        kazanim = dict(zip(columns, row))

        # Extract alan becerileri
        if kazanim.get('alan_becerileri'):
            ders = kazanim.get('ders', '')
            if ders not in alan_becerileri:
                alan_becerileri[ders] = []
            if kazanim['alan_becerileri'] not in alan_becerileri[ders]:
                alan_becerileri[ders].append(kazanim['alan_becerileri'])

        # Extract öğrenme çıktıları
        if kazanim.get('ogrenme_ciktilari'):
            ders = kazanim.get('ders', '')
            if ders not in ogrenme_ciktilari:
                ogrenme_ciktilari[ders] = []

            # Add main outcome
            if kazanim['ogrenme_ciktilari'] not in ogrenme_ciktilari[ders]:
                ogrenme_ciktilari[ders].append(kazanim['ogrenme_ciktilari'])

            # Add sub-outcomes
            if kazanim.get('alt_ogrenme_ciktilari'):
                if kazanim['alt_ogrenme_ciktilari'] not in ogrenme_ciktilari[ders]:
                    ogrenme_ciktilari[ders].append(f"• {kazanim['alt_ogrenme_ciktilari']}")

        # Extract bütünleşik beceriler
        if kazanim.get('butunlesik_beceriler'):
            beceriler = kazanim['butunlesik_beceriler']

            # Split by comma if multiple
            beceri_list = [b.strip() for b in beceriler.split(',')]

            for beceri in beceri_list:
                # Categorize based on prefixes or content
                if 'KB' in beceri or 'Kavramsal' in beceri.lower():
                    if beceri not in kavramsal_beceriler:
                        kavramsal_beceriler.append(beceri)
                elif beceri.startswith('E') and '.' in beceri:
                    if beceri not in egilimler:
                        egilimler.append(beceri)
                elif 'SDB' in beceri or 'Sosyal' in beceri:
                    if beceri not in sosyal_duygusal:
                        sosyal_duygusal.append(beceri)
                elif beceri.startswith('D') and '.' in beceri:
                    if beceri not in degerler:
                        degerler.append(beceri)
                elif 'OB' in beceri or 'Okuryazarlık' in beceri.lower():
                    if beceri not in okuryazarlik:
                        okuryazarlik.append(beceri)
                # Try to detect by content
                elif any(word in beceri.lower() for word in ['dinleme', 'okuma', 'yazma', 'konuşma']):
                    if beceri not in okuryazarlik:
                        okuryazarlik.append(beceri)
                elif any(word in beceri.lower() for word in ['eleştirel', 'problem', 'karar', 'analiz']):
                    if beceri not in kavramsal_beceriler:
                        kavramsal_beceriler.append(beceri)

    cur.close()

    return {
        'alan_becerileri': alan_becerileri,
        'ogrenme_ciktilari': ogrenme_ciktilari,
        'kavramsal_beceriler': kavramsal_beceriler,
        'egilimler': egilimler,
        'sosyal_duygusal': sosyal_duygusal,
        'degerler': degerler,
        'okuryazarlik': okuryazarlik
    }

def update_activities_curriculum():
    """Update all activities with curriculum data from their kazanims"""

    conn = None
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cur = conn.cursor()

        # Fetch all activities with kazanim_idleri
        cur.execute("""
            SELECT id, etkinlik_adi, kazanim_idleri
            FROM etkinlikler
            WHERE kazanim_idleri IS NOT NULL
            ORDER BY id DESC
        """)

        activities = cur.fetchall()
        logger.info(f"Found {len(activities)} activities with kazanim IDs")

        updated_count = 0
        for activity_id, activity_name, kazanim_ids in activities:
            if not kazanim_ids:
                continue

            logger.info(f"Processing activity {activity_id}: {activity_name}")

            # Extract curriculum data
            curriculum_data = extract_curriculum_from_kazanims(kazanim_ids, conn)

            # Update activity
            cur.execute("""
                UPDATE etkinlikler
                SET
                    curriculum_data = %s,
                    alan_becerileri = %s,
                    ogrenme_ciktilari = %s,
                    kavramsal_beceriler = %s,
                    egilimler = %s,
                    sosyal_duygusal = %s,
                    degerler = %s,
                    okuryazarlik = %s
                WHERE id = %s
            """, (
                json.dumps(curriculum_data, ensure_ascii=False),
                json.dumps(curriculum_data['alan_becerileri'], ensure_ascii=False),
                json.dumps(curriculum_data['ogrenme_ciktilari'], ensure_ascii=False),
                curriculum_data['kavramsal_beceriler'],
                curriculum_data['egilimler'],
                curriculum_data['sosyal_duygusal'],
                curriculum_data['degerler'],
                curriculum_data['okuryazarlik'],
                activity_id
            ))

            updated_count += 1

            if updated_count % 5 == 0:
                conn.commit()
                logger.info(f"Updated {updated_count} activities...")

        conn.commit()
        logger.info(f"✅ Successfully updated {updated_count} activities with curriculum data!")

        # Verify update
        cur.execute("""
            SELECT id, etkinlik_adi,
                   array_length(kavramsal_beceriler, 1) as kavramsal_count,
                   array_length(egilimler, 1) as egilim_count,
                   array_length(sosyal_duygusal, 1) as sosyal_count,
                   array_length(degerler, 1) as deger_count,
                   array_length(okuryazarlik, 1) as okur_count
            FROM etkinlikler
            WHERE kazanim_idleri IS NOT NULL
            ORDER BY id DESC
            LIMIT 5
        """)

        print("\n📊 Verification - Last 5 activities:")
        for row in cur.fetchall():
            print(f"ID: {row[0]}, Activity: {row[1]}")
            print(f"  Kavramsal: {row[2] or 0} items")
            print(f"  Eğilimler: {row[3] or 0} items")
            print(f"  Sosyal: {row[4] or 0} items")
            print(f"  Değerler: {row[5] or 0} items")
            print(f"  Okuryazarlık: {row[6] or 0} items")
            print()

        cur.close()

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Updating activities with curriculum data from kazanims...")
    print(f"📍 Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME}")
    update_activities_curriculum()
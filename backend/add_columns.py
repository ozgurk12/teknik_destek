#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('POSTGRES_HOST', '172.16.15.222')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_USER = os.getenv('POSTGRES_USER', 'pgadmin')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'K12P0stgr32025!!**')
DB_NAME = os.getenv('POSTGRES_DB', 'edupage_kids')

def add_curriculum_columns():
    """Add new curriculum columns to etkinlikler table"""

    conn = None
    cur = None

    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cur = conn.cursor()

        # Add columns one by one to avoid errors if some already exist
        columns_to_add = [
            ("curriculum_data", "JSONB"),
            ("alan_becerileri", "JSONB"),
            ("ogrenme_ciktilari", "JSONB"),
            ("kavramsal_beceriler", "TEXT[]"),
            ("egilimler", "TEXT[]"),
            ("sosyal_duygusal", "TEXT[]"),
            ("degerler", "TEXT[]"),
            ("okuryazarlik", "TEXT[]")
        ]

        for column_name, column_type in columns_to_add:
            try:
                alter_query = sql.SQL("ALTER TABLE etkinlikler ADD COLUMN IF NOT EXISTS {} {}").format(
                    sql.Identifier(column_name),
                    sql.SQL(column_type)
                )
                cur.execute(alter_query)
                conn.commit()
                print(f"✓ Added column: {column_name} ({column_type})")
            except Exception as e:
                conn.rollback()
                print(f"✗ Error adding column {column_name}: {e}")

        print("\n✅ Database migration completed successfully!")

    except Exception as e:
        print(f"❌ Database connection error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Adding curriculum columns to etkinlikler table...")
    print(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
    add_curriculum_columns()
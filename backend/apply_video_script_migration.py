import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
conn_params = {
    'host': os.getenv('POSTGRE_HOST', '172.16.15.222'),
    'port': os.getenv('POSTGRE_PORT', 5432),
    'user': os.getenv('POSTGRE_USER', 'pgadmin'),
    'password': os.getenv('POSTGRE_PASSWORD', 'K12P0stgr32025!!**'),
    'database': os.getenv('POSTGRE_DATABASE', 'edupage_kids')
}

def apply_migration():
    conn = None
    cursor = None
    try:
        # Connect to database
        print(f"Connecting to database at {conn_params['host']}...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Read SQL file
        with open('add_video_script_columns.sql', 'r') as f:
            sql_script = f.read()

        # Execute migration
        print("Applying migration...")
        cursor.execute(sql_script)
        conn.commit()

        print("Migration applied successfully!")

        # Verify columns exist
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'video_generations'
            AND column_name IN ('ders', 'konu', 'yas_grubu', 'kazanim_ids', 'curriculum_ids',
                               'video_yapisi', 'bolum_sonu_etkinligi', 'vurgu_noktalari', 'kacinilacaklar')
        """)

        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Verified columns: {existing_columns}")

    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    apply_migration()
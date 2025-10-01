import csv
import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, sync_engine
from app.db.base import Base
from app.models.curriculum import (
    ButunlesikBilesenler,
    Degerler,
    Egilimler,
    KavramsalBeceriler,
    SurecBilesenleri
)


def import_butunlesik_bilesenler(db: Session, csv_path: str):
    """Import Bütünleşik Bileşenler data from CSV"""
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            record = ButunlesikBilesenler(
                butunlesik_bilesenler=row.get('Butunlesik_Bilesenler', ''),
                alt_butunlesik_bilesenler=row.get('Alt_Butunlesik_Bilesenler', ''),
                surec_bilesenleri=row.get('Surec_Bilesenleri', '')
            )
            db.add(record)
    db.commit()
    print(f"✓ Bütünleşik Bileşenler imported successfully")


def import_degerler(db: Session, csv_path: str):
    """Import Değerler data from CSV"""
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            record = Degerler(
                ana_deger_kodu=row.get('Ana_Deger_Kodu', ''),
                ana_deger_adi=row.get('Ana_Deger_Adi', ''),
                ana_deger_aciklamasi=row.get('Ana_Deger_Aciklamasi', ''),
                alt_deger_kodu=row.get('Alt_Deger_Kodu', ''),
                alt_deger_adi=row.get('Alt_Deger_Adi', ''),
                davranis_gostergesi_kodu=row.get('Davranis_Gostergesi_Kodu', ''),
                davranis_gostergesi_aciklamasi=row.get('Davranis_Gostergesi_Aciklamasi', ''),
                ogretim_yontemleri=row.get('Ogretim_Yontemleri', '')
            )
            db.add(record)
    db.commit()
    print(f"✓ Değerler imported successfully")


def import_egilimler(db: Session, csv_path: str):
    """Import Eğilimler data from CSV"""
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            record = Egilimler(
                ana_egilim=row.get('Ana_Egilim', ''),
                alt_egilim=row.get('Alt_Egilim', '')
            )
            db.add(record)
    db.commit()
    print(f"✓ Eğilimler imported successfully")


def import_kavramsal_beceriler(db: Session, csv_path: str):
    """Import Kavramsal Beceriler data from CSV"""
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            record = KavramsalBeceriler(
                ana_beceri_kategorisi=row.get('Ana_Beceri_Kategorisi', ''),
                ana_beceri_kodu=row.get('Ana_Beceri_Kodu', ''),
                ana_beceri_adi=row.get('Ana_Beceri_Adi', ''),
                alt_beceri_kodu=row.get('Alt_Beceri_Kodu', ''),
                alt_beceri_adi=row.get('Alt_Beceri_Adi', ''),
                surec_bileseni_kodu=row.get('Surec_Bileseni_Kodu', ''),
                aciklama=row.get('Aciklama', '')
            )
            db.add(record)
    db.commit()
    print(f"✓ Kavramsal Beceriler imported successfully")


def import_surec_bilesenleri(db: Session, csv_path: str):
    """Import Süreç Bileşenleri data from CSV"""
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            record = SurecBilesenleri(
                surec_bileseni_kodu=row.get('Surec_Bileseni_Kodu', ''),
                surec_bileseni_adi=row.get('Surec_Bileseni_Adi', ''),
                gosterge_kodu=row.get('Gosterge_Kodu', ''),
                gosterge_aciklamasi=row.get('Gosterge_Aciklamasi', '')
            )
            db.add(record)
    db.commit()
    print(f"✓ Süreç Bileşenleri imported successfully")


def clear_existing_data(db: Session):
    """Clear existing data from curriculum tables"""
    db.query(ButunlesikBilesenler).delete()
    db.query(Degerler).delete()
    db.query(Egilimler).delete()
    db.query(KavramsalBeceriler).delete()
    db.query(SurecBilesenleri).delete()
    db.commit()
    print("✓ Existing data cleared")


def main():
    """Main function to import all CSV data"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=sync_engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get the base directory
        base_dir = Path(__file__).parent.parent.parent.parent
        csv_dir = base_dir / "csv"
        
        # Clear existing data
        clear_existing_data(db)
        
        # Import each CSV file
        csv_files = {
            "butunlesikbilesenler.csv": import_butunlesik_bilesenler,
            "degerler.csv": import_degerler,
            "egilimler.csv": import_egilimler,
            "kavramsal_beceriler.csv": import_kavramsal_beceriler,
            "surec_bilesenleri.csv": import_surec_bilesenleri
        }
        
        for csv_file, import_func in csv_files.items():
            csv_path = csv_dir / csv_file
            if csv_path.exists():
                try:
                    import_func(db, str(csv_path))
                except Exception as e:
                    print(f"⚠ Error importing {csv_file}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"⚠ Warning: {csv_file} not found")
        
        print("\n✅ All CSV data imported successfully!")
        
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
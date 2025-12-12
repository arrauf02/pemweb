import argparse
import sys

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.exc import OperationalError
from sqlalchemy import engine_from_config

from .. import models
from ..models.meta import Base

def setup_models(dbsession):
    """
    Menambahkan data awal ke database.
    """
    # Kita tambahkan satu review contoh agar tidak error
    model = models.Review(
        product_name='System Check', 
        review_text='Database initialization successful!',
        sentiment='POSITIVE',
        confidence=1.0,
        key_points='["System Ready"]'
    )
    dbsession.add(model)

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config_uri',
        help='Configuration file, e.g., development.ini',
    )
    return parser.parse_args(argv[1:])

def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)

    try:
        # --- TAMBAHAN PENTING: Force Create Tables ---
        # Ini memastikan tabel 'reviews' dibuat tanpa perlu ribet pakai Alembic
        settings = env['registry'].settings
        engine = engine_from_config(settings, 'sqlalchemy.')
        Base.metadata.create_all(engine)
        # ---------------------------------------------

        with env['request'].tm:
            dbsession = env['request'].dbsession
            setup_models(dbsession)
            
        print("✅ Database berhasil diinisialisasi!")

    except OperationalError as e:
        print(f"❌ Terjadi Error Database: {e}")
        print('''
Pastikan:
1. Server PostgreSQL sudah jalan.
2. Database 'review_db' sudah dibuat.
3. Password & Username di development.ini sudah benar.
        ''')
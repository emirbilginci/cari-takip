from pathlib import Path
import sqlite3


# Proje kök dizini
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# SQLite veritabanının yolu
DATABASE_PATH = PROJECT_ROOT / "data" / "cari.db"


def get_connection():
    """SQLite veritabanına bağlantı oluşturur."""

    connection = sqlite3.connect(DATABASE_PATH)

    # Sonuçlara kolon isimleriyle erişebilmek için
    connection.row_factory = sqlite3.Row

    # Foreign key constraints etkinleştir
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.commit()

    return connection
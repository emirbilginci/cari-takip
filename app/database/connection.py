from pathlib import Path
import sqlite3
import sys
import shutil


def get_app_directory() -> Path:
    """
    Uygulamanın gerçek çalışma klasörünü döndürür.

    Normal Python:
        Proje kökü

    PyInstaller EXE:
        CariTakip.exe'nin bulunduğu klasör
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


# Uygulamanın bulunduğu klasör
APP_DIRECTORY = get_app_directory()

# Veritabanı klasörü
DATA_DIRECTORY = APP_DIRECTORY / "data"

# Veritabanı dosyası
DATABASE_PATH = DATA_DIRECTORY / "cari.db"


def ensure_database():
    """
    Veritabanı klasörünün ve dosyasının mevcut olduğundan emin olur.
    """

    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

    if DATABASE_PATH.exists():
        return

    # Geliştirme ortamında mevcut proje veritabanını kullan.
    source_database = Path(__file__).resolve().parents[2] / "data" / "cari.db"

    if source_database.exists():
        shutil.copy2(source_database, DATABASE_PATH)


def get_connection():
    """SQLite veritabanına bağlantı oluşturur."""

    ensure_database()

    connection = sqlite3.connect(str(DATABASE_PATH))

    # Sonuçlara kolon isimleriyle erişebilmek için
    connection.row_factory = sqlite3.Row

    # Foreign key constraints etkinleştir
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.commit()

    return connection
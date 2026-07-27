import os
import psycopg2
from dotenv import load_dotenv

# Membaca variabel lingkungan dari file .env jika ada
load_dotenv()

def get_db_connection():
    """
    Membuka dan mengembalikan objek koneksi PostgreSQL.
    """
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "ecommerce_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    return conn
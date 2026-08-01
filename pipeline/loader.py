import psycopg2
from config.database import get_db_connection
from .logger import logger


class PostgresLoader:
    
    def __init__(self):
        pass

    def upsert_products(self, products: list[dict]) -> int:
        """
        Memasukkan atau memperbarui daftar produk ke tabel dim_products.
        Mengembalikan jumlah baris yang berhasil diproses.
        """
        if not products:
            logger.info("Tidak ada data untuk dimuat.")
            return 0

        # Query UPSERT PostgreSQL
        upsert_query = """
            INSERT INTO dim_products (sku, title, price, stock_status, rating, last_updated)
            VALUES (%(sku)s, %(title)s, %(price)s, %(stock_status)s, %(rating)s, %(last_updated)s)
            ON CONFLICT (sku) 
            DO UPDATE SET
                title = EXCLUDED.title,
                price = EXCLUDED.price,
                stock_status = EXCLUDED.stock_status,
                rating = EXCLUDED.rating,
                last_updated = EXCLUDED.last_updated;
        """
        
        conn = None
        rows_affected = 0
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Eksekusi batch transaction
            for product in products:
                cursor.execute(upsert_query, product)
                rows_affected += cursor.rowcount
            
            # Commit transaksi jika seluruh batch berhasil
            conn.commit()
            cursor.close()
            logger.info(f"Berhasil memproses {len(products)} record (UPSERT) ke database. Total baris diubah: {rows_affected}")
            
        except psycopg2.DatabaseError as db_err:
            if conn:
                conn.rollback()  # Batalkan transaksi jika terjadi error database
            logger.error(f"Transaksi PostgreSQL gagal & di-rollback: {db_err}", exc_info=True)
            raise db_err

        except Exception as e:
            if conn:
                conn.rollback()
            logger.critical(f"Error tidak terduga pada layer Loader: {e}", exc_info=True)
            raise e
        
        finally:
            if conn:
                conn.close()
                logger.debug("Koneksi database PostgreSQL berhasil ditutup.")
                
        return rows_affected
    def save_execution_log(self, status: str, total_extracted: int, total_upserted: int, data_loss_rate: float, duration_seconds: float):
        """
        Menyimpan ringkasan eksekusi ETL ke dalam tabel etl_execution_logs.
        """
        insert_query = """
            INSERT INTO etl_execution_logs (status, total_extracted, total_upserted, data_loss_rate, duration_seconds)
            VALUES (%(status)s, %(total_extracted)s, %(total_upserted)s, %(data_loss_rate)s, %(duration_seconds)s);
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(insert_query, {
                "status": status,
                "total_extracted": total_extracted,
                "total_upserted": total_upserted,
                "data_loss_rate": data_loss_rate,
                "duration_seconds": duration_seconds
            })
            
            conn.commit()
            cursor.close()
            logger.info("Audit log eksekusi berhasil disimpan ke tabel etl_execution_logs.")
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Gagal menyimpan audit log eksekusi: {e}", exc_info=True)
            
        finally:
            if conn:
                conn.close()
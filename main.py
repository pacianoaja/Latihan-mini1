import os
from dotenv import load_dotenv
from pipeline.extractor import PlaywrightExtractor
from pipeline.transformer import DataTransformer
from pipeline.loader import PostgresLoader
from config.database import get_db_connection
from pipeline.logger import logger
from pipeline.validator import DataValidator, DataValidationError
import time

def run_validation_query():
    """
    Menjalankan query validasi integritas data sesuai spesifikasi tugas.
    """
    validation_query = """
        SELECT 
            COUNT(*) AS total_records,
            ROUND(AVG(price), 2) AS avg_price,
            COUNT(*) FILTER (WHERE stock_status = TRUE) AS in_stock_count
        FROM dim_products;
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(validation_query)
        result = cursor.fetchone()
        
        print("\n" + "="*40)
        print("     HASIL QUERY VALIDASI DATABASE     ")
        print("="*40)
        print(f"Total Records   : {result[0]}")
        print(f"Average Price   : {result[1]}")
        print(f"In-Stock Count  : {result[2]}")
        print("="*40 + "\n")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Gagal menjalankan query validasi: {e}")

def running():
    logger.info("==================================================")
    logger.info("Memulai Pipeline E-Commerce Competitive Intelligence...")
    logger.info("==================================================")
    start_time = time.perf_counter()
    loader = PostgresLoader()
    loader.create_tables_if_not_exists()

    # Inisialisasi variabel & loader di awal

    status = "FAILED"
    total_extracted = 0
    total_cleaned = 0
    total_upserted = 0
    data_loss = 0
    data_loss_rate = 0.0
    
    try :
        # Target URL latihan
        TARGET_URL = os.getenv("TARGET_URL")
        
        # 1. Extraction Layer
        extractor = PlaywrightExtractor(base_url=TARGET_URL)
        raw_products = extractor.extract_products(limit=20)
        logger.info(f"[EXTRACT] Terambil {len(raw_products)} raw record.")
        total_extracted = len(raw_products)
        
        # 2. Transformation Layer
        transformed_products = []
        for raw in raw_products:
            clean_data = DataTransformer.transform_product(raw)
            transformed_products.append(clean_data)
        logger.info(f"[TRANSFORM] Berhasil membersihkan {len(transformed_products)} record.")
        total_cleaned = len(transformed_products)

        # additional buat memeriksa apkah datanya bersih
        DataValidator.validate_batch(transformed_products)
        
        # 3. Loading Layer (PostgreSQL UPSERT)
        loader = PostgresLoader()
        loader.upsert_products(transformed_products)
        logger.info(f"[LOAD] Berhasil UPSERT {len(transformed_products)} record ke database.")
        total_upserted = loader.upsert_products(transformed_products)
        
        # 4. Validation Layer
        run_validation_query()
        data_loss = total_extracted - total_upserted
        data_loss_rate = (data_loss / total_extracted) * 100 if total_extracted > 0 else 0.0
        
        logger.info("Pipeline selesai dieksekusi tanpa error.")


    except DataValidationError as e:
        # Menangkap error khusus validasi data kotor
        logger.error(f"[PIPELINE ABORTED] Kegagalan Kualitas Data: {e}")
        # Re-raise error agar scheduler/wrapper tahu pipeline gagal (penting untuk Alerting nanti)
        raise e

    except Exception as e:
        # Menangkap error fatal yang dilempar (raise) dari layer mana pun
        logger.critical(f"Pipeline berhenti secara paksa karena terjadi kesalahan fatal: {e}", exc_info=True)

    end_time = time.perf_counter()

    # buat nyari waktu eksekusi 

    duration_seconds = end_time - start_time

    loader.save_execution_log(
        status="SUCCESS",
        total_extracted=total_extracted,
        total_upserted=total_upserted,
        data_loss_rate=data_loss_rate,
        duration_seconds=duration_seconds
    )
    summary_log = f"""
==================================================
             PIPELINE EXECUTION SUMMARY           
==================================================
Status           : SUCCESS
Total Extracted  : {total_extracted} records
Total Cleaned    : {total_cleaned} records
Total UPSERT     : {total_upserted} records
Data Loss        : {data_loss} records ({data_loss_rate:.2f}%)
Total Duration   : {duration_seconds:.2f} seconds
=================================================="""
    logger.info(summary_log)

if __name__ == "__main__":
    running()
from pipeline.extractor import PlaywrightExtractor
from pipeline.transformer import DataTransformer
from pipeline.loader import PostgresLoader
from config.database import get_db_connection
from pipeline.logger import logger

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

    
    try :
        # Target URL latihan
        TARGET_URL = "http://books.toscrape.com/"
        
        # 1. Extraction Layer
        extractor = PlaywrightExtractor(base_url=TARGET_URL)
        raw_products = extractor.extract_products(limit=20)
        logger.info(f"[EXTRACT] Terambil {len(raw_products)} raw record.")
        
        # 2. Transformation Layer
        transformed_products = []
        for raw in raw_products:
            clean_data = DataTransformer.transform_product(raw)
            transformed_products.append(clean_data)
        logger.info(f"[TRANSFORM] Berhasil membersihkan {len(transformed_products)} record.")
        
        # 3. Loading Layer (PostgreSQL UPSERT)
        loader = PostgresLoader()
        loader.upsert_products(transformed_products)
        logger.info(f"[LOAD] Berhasil UPSERT {len(transformed_products)} record ke database.")
        
        # 4. Validation Layer
        run_validation_query()
        
        logger.info("Pipeline selesai dieksekusi tanpa error.")

    except Exception as e:
        # Menangkap error fatal yang dilempar (raise) dari layer mana pun
        logger.critical(f"Pipeline berhenti secara paksa karena terjadi kesalahan fatal: {e}", exc_info=True)

if __name__ == "__main__":
    running()
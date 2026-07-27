from pipeline.extractor import PlaywrightExtractor
from pipeline.transformer import DataTransformer
from pipeline.loader import PostgresLoader
from config.database import get_db_connection

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

def main():
    print("[START] Memulai Pipeline E-Commerce Competitive Intelligence...")
    
    # Target URL latihan
    TARGET_URL = "http://books.toscrape.com/"
    
    # 1. Extraction Layer
    extractor = PlaywrightExtractor(base_url=TARGET_URL)
    raw_products = extractor.extract_products(limit=20)
    print(f"[EXTRACT] Terambil {len(raw_products)} raw record.")
    
    # 2. Transformation Layer
    transformed_products = []
    for raw in raw_products:
        clean_data = DataTransformer.transform_product(raw)
        transformed_products.append(clean_data)
    print(f"[TRANSFORM] Berhasil membersihkan {len(transformed_products)} record.")
    
    # 3. Loading Layer (PostgreSQL UPSERT)
    loader = PostgresLoader()
    loader.upsert_products(transformed_products)
    
    # 4. Validation Layer
    run_validation_query()
    
    print("[END] Pipeline selesai dieksekusi tanpa error.")

if __name__ == "__main__":
    main()
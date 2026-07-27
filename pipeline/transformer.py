import re
from datetime import datetime, timezone

class DataTransformer:
    
    @staticmethod
    def clean_price(raw_price: str) -> float:
        """
        Mengonversi string harga (misal: '£51.77' atau 'Rp 150.000,-') menjadi float.
        """
        if not raw_price:
            return 0.0
        # Menghapus semua karakter selain angka dan titik desimal
        cleaned = re.sub(r"[^\d.]", "", raw_price.replace(",", "."))
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def parse_stock(raw_stock: str) -> bool:
        """
        Mengonversi status stok string ('In stock', 'Tersedia') menjadi Boolean.
        """
        if not raw_stock:
            return False
        
        positive_indicators = ["in stock", "available", "tersedia", "ready"]
        return any(indicator in raw_stock.lower() for indicator in positive_indicators)

    @staticmethod
    def parse_rating(raw_rating: str) -> float:
        """
        Mengonversi teks rating ('Four', '4.5') menjadi float desimal.
        """
        word_to_num = {
            "one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0
        }
        if not raw_rating:
            return 0.0
        
        cleaned = raw_rating.strip().lower()
        if cleaned in word_to_num:
            return word_to_num[cleaned]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @classmethod
    def transform_product(cls, raw_data: dict) -> dict:
        """
        Menggabungkan seluruh proses pembersihan ke satu dictionary siap simpan ke DB.
        """
        return {
            "sku": str(raw_data.get("sku", "")).strip(),
            "title": str(raw_data.get("title", "")).strip(),
            "price": cls.clean_price(raw_data.get("price", "")),
            "stock_status": cls.parse_stock(raw_data.get("stock_status", "")),
            "rating": cls.parse_rating(raw_data.get("rating", "")),
            "last_updated": datetime.now(timezone.utc)
        }
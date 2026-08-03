from .logger import logger

class DataValidationError(Exception):
    """Custom Exception untuk menandai kegagalan validasi data."""
    pass


class DataValidator:

    @classmethod
    def validate_batch(cls, products: list[dict]) -> bool:
        """
        Memvalidasi list of dict hasil transformasi sebelum dikirim ke loader.
        Jika menemukan anomali, sengaja melempar DataValidationError.
        """
        logger.info("[VALIDATOR] Memulai validasi kualitas data...")

        # 1. Cek Apakah Batch Kosong
        if not products:
            raise DataValidationError("Validasi Gagal: Batch data kosong (0 items)!")

        # 2. Cek Kelengkapan Field Wajib dan Aturan Nilai pada Tiap Item
        for idx, item in enumerate(products, start=1):
            sku = item.get("sku")
            title = item.get("title")
            price = item.get("price")

            # Field Wajib Tidak Boleh Kosong
            if not sku or not title:
                raise DataValidationError(
                    f" Validasi Gagal pada item ke-{idx}: SKU atau Title kosong! Data: {item}"
                )

            # Validasi Aturan Harga (Price Constraints)
            if price is None or price <= 0:
                raise DataValidationError(
                    f" Validasi Gagal pada item ke-{idx} (SKU: {sku}): Harga tidak valid ({price})! Harga harus > 0."
                )

        logger.info(f" [VALIDATOR] Validasi Sukses! Total {len(products)} record dinyatakan bersih dan layak di-UPSERT.")
        return True
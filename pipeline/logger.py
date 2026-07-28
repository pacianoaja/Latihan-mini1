# logger.py
import logging
import sys

def setup_logger(name: str = "etl_pipeline", log_file: str = "pipeline.log") -> logging.Logger:
    """
    Menyediakan logger tersentralisasi dengan dua output:
    1. Terminal (StreamHandler) -> Hanya menampilkan log penting (INFO ke atas)
    2. File Disk (FileHandler)    -> Menyimpan seluruh detail jejak eksekusi (DEBUG ke atas)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Menangkap semua level dari DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Mencegah duplikasi log jika fungsi dipanggil ulang
    if logger.hasHandlers():
        logger.handlers.clear()

    # Format Tampilan Log: Waktu | Level | Nama File:Baris Kode | Pesan Error/Informasi
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Output ke Terminal (Console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Output ke File pipeline.log
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Instance logger yang siap di-import oleh file lain
logger = setup_logger()


# Uji coba langsung modul
if __name__ == "__main__":
    logger.info("Pengujian modul logger: Status NORMAL.")
    logger.warning("Pengujian modul logger: Ada potensi MASALAH.")
    logger.error("Pengujian modul logger: Terjadi ERROR.")
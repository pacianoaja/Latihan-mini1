import os
from dotenv import load_dotenv
import time
import sys
import schedule
from pipeline.logger import logger
from main import running
from pipeline.notifier import TelegramNotifier

# LIHAT ENV
load_dotenv()
# ==========================================
# KONFIGURASI PENJADWALAN (PARAMETERISASI)
# ==========================================
# Untuk keperluan pengujian/testing, gunakan interval menit/detik.
# Di lingkungan produksi, nilai ini bisa diubah sesuai kebutuhan bisnis.
INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", 3)) 
notifier = TelegramNotifier()
execution_counter = 0

def execute_job_wrapper():
    """
    Wrapper pembungkus fungsi ETL dari main.py.
    Bertugas mencatat pembuka dan penutup sesi eksekusi berkala ke dalam log.
    """
    global execution_counter
    execution_counter += 1

    logger.info(" Scheduler memicu eksekusi ETL otomatis...")
    notifier.send_notification(f"🔄 <b>[ETL RUN #{execution_counter}]</b> Memproses data...")
    try:
        running()
    except Exception as e:
        logger.error(f"Terjadi kegagalan saat mengeksekusi job terjadwal: {e}", exc_info=True)
        notifier.send_notification(f"🚨 <b>[FAILED RUN #{execution_counter}]</b> Error: <code>{str(e)}</code>")
    


def start_scheduler():
    """
    Inisialisasi utama untuk menjalankan daemon scheduler secara kontinu.
    """
    logger.info("==================================================")
    logger.info(f" Layanan Scheduler ETL Berhasil Diaktifkan!")
    logger.info(f" Jadwal Eksekusi : Setiap {INTERVAL_MINUTES} menit")
    logger.info(f" Tekan Ctrl+C di terminal untuk menghentikan scheduler.")
    logger.info("==================================================")

    # 1. Immediate Run (Jalankan sekali di awal saat scheduler pertama kali dinyalakan)
    execute_job_wrapper()

    # 2. Registrasi Task ke Library 'schedule'
    schedule.every(INTERVAL_MINUTES).minutes.do(execute_job_wrapper)

    # 3. Continuous Event Loop dengan Graceful Shutdown Handling
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Optimasi CPU: Mencegah thread mengambil 100% CPU Clock

    except KeyboardInterrupt:
        # HANDLING GRACEFUL SHUTDOWN
        logger.warning("\n[INTERRUPT] Sinyal penghentian (Ctrl+C) diterima oleh sistem!")
        logger.info("Sedang membersihkan alokasi memori dan menghentikan Daemon Scheduler...")
        logger.info("Layanan Scheduler ETL berhasil dihentikan secara aman (Graceful Exit).")
        sys.exit(0)


if __name__ == "__main__":
    start_scheduler()
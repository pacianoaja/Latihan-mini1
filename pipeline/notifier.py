import os
from .logger import logger
import requests
from dotenv import load_dotenv
load_dotenv()


class TelegramNotifier:
    def __init__(self, token: str = None, chat_id: str = None):
        """
        Inisialisasi Notifier. Jika token/chat_id tidak diisi, 
        akan otomatis mengambil dari .env
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage" if self.token else None

    def send_notification(self, message: str) -> bool:
        """Mengirim pesan ke Telegram."""
        if not self.token or not self.chat_id:
            logger.warning("[NOTIFIER] Telegram Token atau Chat ID belum diset di .env.")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("[NOTIFIER] Notifikasi Telegram berhasil dikirim.")
                return True
            else:
                logger.error(f"[NOTIFIER] Gagal kirim. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"[NOTIFIER] Error HTTP Request: {str(e)}")
            return False
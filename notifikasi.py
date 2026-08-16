import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def kirim_notifikasi(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Gagal kirim notifikasi: {e}")
        return False

if __name__ == "__main__":
    # Test kirim pesan
    berhasil = kirim_notifikasi("🔔 Tes notifikasi dari Sistem Stok!")
    print("Berhasil!" if berhasil else "Gagal.")
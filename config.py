import os
from dotenv import load_dotenv

# .env faylini yuklash (lokal muhit uchun)
load_dotenv()

# Railway va .env o'zgaruvchilarini o'qib olish
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ADMIN_IDS ni ro'yxat shakliga keltirish (masalan: "12345678,87654321" -> [12345678, 87654321])
raw_admin_ids = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in raw_admin_ids.split(",") if x.strip().isdigit()]
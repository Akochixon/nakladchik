FROM python:3.11-slim

# Ishchi katalogini belgilash
WORKDIR /app

# Tizim uchun zaruriy paketlarni o'rnatish
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Zaruriy kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini konteynerga ko'chirish
COPY . .

# Botni ishga tushirish
CMD ["python", "bot.py"]
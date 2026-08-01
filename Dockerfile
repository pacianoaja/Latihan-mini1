# 1. Gunakan Python 3.10 slim
FROM python:3.10-slim

# 2. Install dependensi sistem + Font + Grafis Playwright
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    fonts-liberation \
    fonts-noto-color-emoji \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2t64 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Copy requirements
COPY requirements.txt .

# 5. Install dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Install browser chromium
RUN python -m playwright install chromium

# 7. Copy seluruh file proyek
COPY . .

# 8. Jalankan main.py
CMD ["python", "main.py"]
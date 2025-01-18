FROM python:3.9-slim

# Встановлюємо необхідні пакунки для роботи з Python та іншими залежностями
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочий каталог
WORKDIR /backend

# Встановлюємо Python-залежності
RUN pip install gunicorn flask flask_cors python-dotenv requests configparser

# Вказуємо команду для запуску програми
CMD ["gunicorn", "-b", "0.0.0.0:8081", "main:app"]
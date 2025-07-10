FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установим зависимости системы: GDAL + PostGIS + другие
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    gdal-bin \
    libgdal-dev \
    && pip install --upgrade pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Обязательно установить переменную окружения для GDAL
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

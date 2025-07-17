# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Установка системных зависимостей для mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Обновление pip и установка пакетов
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --root-user-action=ignore

COPY . .

# Собираем статические файлы (если нужно)
# RUN python manage.py collectstatic --noinput

# Миграции и создание суперпользователя при запуске
CMD ["/bin/bash", "-c", "python manage.py migrate && python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL || true && python manage.py runserver 0.0.0.0:8000"] 
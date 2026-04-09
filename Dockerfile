# ЭТАП 1: Сборка (Build stage)
# Используем образ с инструментами компиляции
FROM python:3.11-slim AS builder

WORKDIR /app

# Устанавливаем системные зависимости, нужные для сборки некоторых библиотек (например, psycopg2)
RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt .
# Устанавливаем библиотеки не в систему, а в отдельную папку
RUN pip install --user --no-cache-dir -r requirements.txt


# ЭТАП 2: Финальный образ (Run stage)
# Берем чистый легкий образ
FROM python:3.11-slim

WORKDIR /app

# Ставим только runtime-библиотеку для работы с Postgres (она маленькая)
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

# Копируем только установленные пакеты из первого этапа (из папки .local)
COPY --from=builder /root/.local /root/.local
# Копируем твой код
COPY . .

# Прокидываем путь к установленным библиотекам
ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
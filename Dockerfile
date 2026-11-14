FROM python:3.11-slim

# Отключаем буферизацию вывода, чтобы логи бота сразу появлялись в консоли Docker
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Сначала копируем и ставим зависимости (для кэширования слоев Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код проекта
COPY . .

# Запускаем бота как модуль (важно для корректной работы импортов вида "from bot.config_reader...")
CMD ["python", "-m", "bot"]
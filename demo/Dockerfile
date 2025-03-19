# Используем официальный образ TensorFlow с поддержкой GPU
FROM tensorflow/tensorflow:latest-gpu

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Команда для запуска
CMD ["python", "main.py"]
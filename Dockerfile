# Usamos una imagen oficial y ligera de Python 3.13
FROM python:3.13-slim

# Evita que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python guarde en buffer la salida de consola (para ver los logs en tiempo real)
ENV PYTHONUNBUFFERED=1

# Creamos una carpeta dentro de la cápsula llamada /app y nos movemos a ella
WORKDIR /app

# Instalamos las librerías del sistema que WeasyPrint necesita para crear los PDFs
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libpangoft2-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero la lista de requisitos (para que Docker lo guarde en caché y vaya más rápido)
COPY requirements.txt /app/

# Instalamos las dependencias necesarias en la cápsula
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Instalamos gunicorn (un servidor web profesional para Django, superior a runserver)
RUN pip install gunicorn

# Ahora copiamos todo el resto de tu código a la cápsula
COPY . /app/

# Exponemos el puerto 8000 para poder conectarnos desde el navegador
EXPOSE 8000
